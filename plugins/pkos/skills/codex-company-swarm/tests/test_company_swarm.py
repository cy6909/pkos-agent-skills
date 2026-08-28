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

    def test_rejects_model_downgrade(self) -> None:
        self.data["sessions"][2]["model"] = "gpt-5.6-luna"
        errors = ORG.validate(self.data)
        self.assertTrue(any("model must be gpt-5.6-sol" in item for item in errors))


class MFSQValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = json.loads((ROOT / "assets" / "examples" / "mfsq-test-plan.example.json").read_text(encoding="utf-8"))

    def test_valid_example(self) -> None:
        self.assertEqual([], MFSQ.validate(self.data))

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
            "axis": "Q",
            "quality_attribute": "performance",
            "reason": "Documentation-only code path has no runtime behavior",
            "approved_by": "RB-01"
        }]
        self.assertEqual([], MFSQ.validate(self.data))

    def test_rejects_local_only_case(self) -> None:
        self.data["cases"][0]["pipeline_stage"] = "local"
        errors = MFSQ.validate(self.data)
        self.assertTrue(any("authoritative pipeline_stage" in item for item in errors))


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
