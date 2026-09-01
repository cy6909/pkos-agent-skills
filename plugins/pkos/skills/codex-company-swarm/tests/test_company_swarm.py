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

    def test_six_executable_examples(self) -> None:
        for name in ("ci-stop-rule.example.json", "consolidation-after-stall.example.json", "affinity-session-reuse.example.json", "reviewer-after-freeze.example.json", "notion-gate-batch.example.json"):
            self.assertEqual([], ORG.validate(ORG.load_json(ROOT / "assets" / "examples" / name)), name)

    def task(self, sid: str):
        return next(item for item in self.data["sessions"] if item["session_id"] == sid)

    def test_rejects_hidden_or_delegating_child(self) -> None:
        self.task("D-FE-01")["visible_task"] = False
        self.task("D-FE-01")["may_delegate"] = True
        errors = ORG.validate(self.data)
        self.assertTrue(any("hidden subagents" in item for item in errors))
        self.assertTrue(any("may_delegate=false" in item for item in errors))

    def test_rejects_missing_visible_identity_or_model_route(self) -> None:
        task = self.task("D-FE-01")
        task["threadId"] = ""
        task["model"] = ""
        del task["reasoning_effort"]
        del task["risk_level"]
        errors = ORG.validate(self.data)
        for field in ("threadId", "model", "reasoning_effort", "risk_level"):
            self.assertTrue(any(field in item for item in errors), field)

    def test_rejects_active_and_registered_hard_caps(self) -> None:
        template = self.task("D-FE-01")
        for index in range(3):
            task = copy.deepcopy(template)
            task.update({
                "session_id": f"V-{index}",
                "role": "verifier",
                "lane": f"verify-{index}",
                "threadId": f"thread-v-{index}",
                "title": f"run-product-first V-{index} verify",
                "state": "active",
                "productive": False,
                "activity_kind": "waiting",
            })
            task["task_packet"]["feature_id"] = f"VERIFY-{index}"
            self.data["sessions"].append(task)
        errors = ORG.validate(self.data)
        self.assertTrue(any("registered visible task hard cap" in item for item in errors))
        self.assertTrue(any("active child hard cap" in item for item in errors))

    def test_rejects_missing_feature_or_scope(self) -> None:
        packet = self.task("D-BE-01")["task_packet"]
        packet["feature_id"] = ""
        packet["owned_files_modules"] = []
        errors = ORG.validate(self.data)
        self.assertTrue(any("feature_id" in item for item in errors))
        self.assertTrue(any("owned scope" in item for item in errors))

    def test_rejects_repeated_context_and_large_packet(self) -> None:
        packet = self.task("D-BE-01")["task_packet"]
        packet["memory_pack"] = "x" * 1300
        errors = ORG.validate(self.data)
        self.assertTrue(any("seven allowed fields" in item for item in errors))
        self.assertTrue(any("1200" in item for item in errors))

    def test_rejects_handoff_without_developer_self_test(self) -> None:
        self.data["lanes"][0]["handoff_state"] = "READY_FOR_TEST"
        errors = ORG.validate(self.data)
        self.assertTrue(any("self-test incomplete" in item for item in errors))
        self.assertTrue(any("cy6909 Chrome" in item for item in errors))

    def test_rejects_reviewer_before_freeze(self) -> None:
        reviewed = ORG.load_json(ROOT / "assets" / "examples" / "reviewer-after-freeze.example.json")
        reviewed["cumulative_candidate"]["state"] = "LIVE"
        self.assertTrue(any("reviewer may start" in item for item in ORG.validate(reviewed)))

    def test_rejects_ci_without_preflight(self) -> None:
        self.data["ci_control"]["lane_state"] = "RUNNING"
        self.assertTrue(any("CI cannot run" in item for item in ORG.validate(self.data)))

    def test_rejects_non_product_capacity_dominance(self) -> None:
        self.task("D-FE-01")["productive"] = False
        self.data["concurrency_state"].update({"productive_count": 3, "product_code_count": 2, "product_code_share_percent": 66.67})
        errors = ORG.validate(self.data)
        self.assertTrue(any("70%" in item for item in errors))

    def test_rejects_multiple_or_missing_candidate(self) -> None:
        self.data["cumulative_candidate"]["parallel_candidate_count"] = 1
        self.assertTrue(any("exactly one cumulative candidate" in item for item in ORG.validate(self.data)))

    def test_requires_consolidation_on_token_overrun(self) -> None:
        self.data["token_control"]["estimated_coordination_tokens"] = 20000
        self.assertTrue(any("CONSOLIDATION_MODE" in item for item in ORG.validate(self.data)))

    def test_requires_consolidation_when_either_progress_clock_stalls(self) -> None:
        self.data["token_control"]["minutes_since_candidate"] = 120
        self.assertTrue(any("CONSOLIDATION_MODE" in item for item in ORG.validate(self.data)))

    def test_rejects_non_delta_progress_report(self) -> None:
        self.data["progress_report"]["interval_minutes"] = 15
        self.data["progress_report"]["fields"].append("full_status_recap")
        self.assertTrue(any("60-minute delta" in item for item in ORG.validate(self.data)))

    def test_rejects_local_execution_policy_drift(self) -> None:
        self.data["environment_policy"]["resource_environment"] = "local"
        self.assertTrue(any("environment policy" in item for item in ORG.validate(self.data)))


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
