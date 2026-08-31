from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load %s" % path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ORG = load_module("test_validate_org", ROOT / "scripts" / "validate_org.py")
MFSQ = load_module("test_validate_mfsq", ROOT / "scripts" / "validate_mfsq.py")
DASHBOARD = load_module("test_render_dashboard", ROOT / "scripts" / "render_dashboard.py")


class OrganizationValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = json.loads((ROOT / "assets" / "examples" / "organization.example.json").read_text(encoding="utf-8"))

    def test_valid_example(self) -> None:
        self.assertEqual([], ORG.validate(self.data))

    def test_rejects_second_director(self) -> None:
        duplicate = copy.deepcopy(self.data["sessions"][0])
        duplicate["session_id"] = "TD-02"
        duplicate["parent_session_id"] = "TD-01"
        duplicate["managed_by"] = "TD-01"
        duplicate["may_delegate"] = False
        self.data["sessions"].append(duplicate)
        errors = ORG.validate(self.data)
        self.assertTrue(any("exactly one technical-director" in item for item in errors))

    def test_rejects_non_director_delegation(self) -> None:
        self.data["sessions"][1]["may_delegate"] = True
        errors = ORG.validate(self.data)
        self.assertTrue(any("must set may_delegate=false" in item for item in errors))

    def test_rejects_non_reciprocal_pair(self) -> None:
        tester = next(item for item in self.data["sessions"] if item["session_id"] == "T-FE-01")
        tester["paired_session_id"] = "D-BE-01"
        errors = ORG.validate(self.data)
        self.assertTrue(any("pairing must be reciprocal" in item or "pair does not match" in item for item in errors))

    def test_rejects_developer_test_acceptance(self) -> None:
        developer = next(item for item in self.data["sessions"] if item["session_id"] == "D-BE-01")
        developer["test_acceptance"] = True
        errors = ORG.validate(self.data)
        self.assertTrue(any("test_acceptance=false" in item for item in errors))

    def test_rejects_overlapping_write_scope(self) -> None:
        tester = next(item for item in self.data["sessions"] if item["session_id"] == "T-BE-01")
        tester["write_scope"] = ["server/tests/**"]
        errors = ORG.validate(self.data)
        self.assertTrue(any("overlapping write scopes" in item for item in errors))

    def test_accepts_small_two_lane_budget(self) -> None:
        data = ORG.load_json(ROOT / "assets" / "examples" / "staffing-small-two-lane.example.json")
        self.assertEqual([], ORG.validate(data))

    def test_accepts_same_thread_luna_escalation(self) -> None:
        data = ORG.load_json(ROOT / "assets" / "examples" / "staffing-luna-escalation-reuse.example.json")
        self.assertEqual([], ORG.validate(data))

    def test_rejects_unexplained_default_route_change(self) -> None:
        self.data["sessions"][3]["model"] = "gpt-5.6-luna"
        self.data["sessions"][3]["task_packet"]["model"] = "gpt-5.6-luna"
        errors = ORG.validate(self.data)
        self.assertTrue(any("default route must use gpt-5.6-sol" in item for item in errors))

    def test_rejects_hidden_role(self) -> None:
        self.data["sessions"][3]["visible_task"] = False
        self.assertTrue(any("hidden roles" in item for item in ORG.validate(self.data)))

    def test_rejects_missing_thread_id(self) -> None:
        self.data["sessions"][3]["threadId"] = ""
        self.assertTrue(any("threadId must be non-empty" in item for item in ORG.validate(self.data)))

    def test_rejects_missing_packet_model_effort(self) -> None:
        self.data["sessions"][4]["task_packet"].pop("reasoning_effort")
        self.assertTrue(any("task_packet.reasoning_effort" in item for item in ORG.validate(self.data)))

    def test_rejects_stale_generation(self) -> None:
        self.data["sessions"][3]["generation"] = 0
        self.data["sessions"][3]["task_packet"]["generation"] = 0
        self.assertTrue(any("stale generation" in item for item in ORG.validate(self.data)))

    def test_rejects_duplicate_reviewer(self) -> None:
        duplicate = copy.deepcopy(next(item for item in self.data["sessions"] if item["session_id"] == "RB-01"))
        duplicate["session_id"] = "RB-02"
        duplicate["threadId"] = "thread-rb-2"
        duplicate["title"] = "run-standard-six RB-02 review"
        self.data["sessions"].append(duplicate)
        self.data["concurrency_state"]["registered_count"] += 1
        self.data["concurrency_state"]["settled_count"] += 1
        self.assertTrue(any("exactly one review-chair" in item for item in ORG.validate(self.data)))

    def test_rejects_active_hard_cap_breach(self) -> None:
        for sid in ("RB-01", "INT-01"):
            task = next(item for item in self.data["sessions"] if item["session_id"] == sid)
            task["state"] = "active"
            task["productive"] = True
            task["waiting_on_dependency"] = False
        self.data["concurrency_state"].update({"active_count": 9, "productive_active_count": 9, "settled_count": 0})
        self.assertTrue(any("hard cap" in item for item in ORG.validate(self.data)))

    def test_rejects_registered_hard_cap_breach(self) -> None:
        template = next(item for item in self.data["sessions"] if item["session_id"] == "RB-01")
        for number in range(2, 5):
            task = copy.deepcopy(template)
            task.update({"session_id": "V-%02d" % number, "role": "verifier", "threadId": "thread-v-%d" % number, "title": "run-standard-six V-%02d review" % number})
            self.data["sessions"].append(task)
        self.data["concurrency_state"].update({"registered_count": 13, "settled_count": 4})
        self.assertTrue(any("registered visible task count exceeds" in item for item in ORG.validate(self.data)))

    def test_rejects_unexplained_low_concurrency(self) -> None:
        for sid in ("D-FE-01", "T-FE-01", "D-BE-01", "T-BE-01"):
            task = next(item for item in self.data["sessions"] if item["session_id"] == sid)
            task.update({"state": "queued", "productive": False, "ready_for_dispatch": True})
        self.data["concurrency_state"].update({"active_count": 3, "productive_active_count": 3, "ready_count": 4, "underfill_age_seconds": 90, "underfill_reason": "", "dispatch_action": "", "events": []})
        self.assertTrue(any("CONCURRENCY_UNDERFILLED" in item for item in ORG.validate(self.data)))


class MFSQValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = json.loads((ROOT / "assets" / "examples" / "mfsq-test-plan.example.json").read_text(encoding="utf-8"))

    def test_valid_example(self) -> None:
        self.assertEqual([], MFSQ.validate(self.data))

    def test_rejects_v1_schema_for_new_runs(self) -> None:
        self.data["schema"] = "pkos-mfsq/v1"
        errors = MFSQ.validate(self.data)
        self.assertTrue(any("historical evidence only" in item for item in errors))

    def test_rejects_missing_security(self) -> None:
        self.data["cases"] = [item for item in self.data["cases"] if item["axis"] != "S"]
        errors = MFSQ.validate(self.data)
        self.assertTrue(any("requires an S case" in item for item in errors))

    def test_rejects_missing_performance(self) -> None:
        self.data["cases"] = [item for item in self.data["cases"] if item.get("quality_attribute") != "performance"]
        errors = MFSQ.validate(self.data)
        self.assertTrue(any("performance case" in item for item in errors))

    def test_accepts_approved_performance_exclusion(self) -> None:
        self.data["cases"] = [item for item in self.data["cases"] if item.get("quality_attribute") != "performance"]
        self.data["exclusions"] = [{
            "scope": "axis",
            "axis": "Q",
            "quality_attribute": "performance",
            "reason": "Documentation-only code path has no runtime behavior",
            "approved_by": "RB-01",
            "approval_artifact": "notion://RV-Q-N-A-001"
        }]
        self.assertEqual([], MFSQ.validate(self.data))

    def test_rejects_local_only_case(self) -> None:
        self.data["cases"][0]["pipeline_stage"] = "local"
        errors = MFSQ.validate(self.data)
        self.assertTrue(any("authoritative pipeline_stage" in item for item in errors))

    def test_rejects_step_without_expected_result(self) -> None:
        del self.data["cases"][0]["steps"][0]["expected"]
        errors = MFSQ.validate(self.data)
        self.assertTrue(any("steps[0].expected" in item for item in errors))

    def test_rejects_unit_case_without_code_mapping(self) -> None:
        unit_case = next(item for item in self.data["cases"] if item["case_type"] == "unit")
        unit_case["code_refs"] = []
        errors = MFSQ.validate(self.data)
        self.assertTrue(any("unit case requires code_refs" in item for item in errors))

    def test_rejects_uncovered_acceptance(self) -> None:
        self.data["acceptance_ids"].append("AC-ORDER-UNTESTED")
        errors = MFSQ.validate(self.data)
        self.assertTrue(any("AC-ORDER-UNTESTED has no executable test case" in item for item in errors))

    def test_rejects_dependency_without_cross_unit_contract_case(self) -> None:
        contract_case = next(item for item in self.data["cases"] if item["case_type"] == "contract")
        contract_case["implementation_unit_ids"] = ["BE-API-ORDER-RETRY"]
        e2e_case = next(item for item in self.data["cases"] if item["case_type"] == "e2e")
        e2e_case["case_type"] = "component"
        errors = MFSQ.validate(self.data)
        self.assertTrue(any("DEP-ORDER-RETRY-001 lacks a contract" in item for item in errors))

    def test_rejects_user_facing_unit_without_acceptance_case(self) -> None:
        e2e_case = next(item for item in self.data["cases"] if item["case_type"] == "e2e")
        e2e_case["case_type"] = "component"
        errors = MFSQ.validate(self.data)
        self.assertTrue(any("FE-WEB-ORDER-RETRY lacks E2E" in item for item in errors))

    def test_rejects_missing_material_provenance_checks(self) -> None:
        self.data["material_gate"]["checks"] = []
        errors = MFSQ.validate(self.data)
        self.assertTrue(any("material_gate.checks must be a non-empty array" in item for item in errors))


class DashboardTests(unittest.TestCase):
    def test_dashboard_contains_key_evidence(self) -> None:
        data = json.loads((ROOT / "assets" / "examples" / "run-state.example.json").read_text(encoding="utf-8"))
        rendered = DASHBOARD.render(data)
        self.assertIn("# Company Swarm Dashboard", rendered)
        self.assertIn("```mermaid", rendered)
        self.assertIn("## MFSQ evidence", rendered)
        self.assertIn("stylemuse/main", rendered)
        self.assertIn("## PKOS writeback", rendered)

    def test_cli_writes_dashboard(self) -> None:
        source = ROOT / "assets" / "examples" / "run-state.example.json"
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "dashboard.md"
            code = DASHBOARD.main([str(source), "--output", str(output)])
            self.assertEqual(0, code)
            self.assertTrue(output.exists())
            self.assertGreater(output.stat().st_size, 500)


if __name__ == "__main__":
    unittest.main()
