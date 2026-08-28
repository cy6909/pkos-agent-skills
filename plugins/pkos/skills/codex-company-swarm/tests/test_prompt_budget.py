from __future__ import annotations

import importlib.util
import shutil
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


BUDGET = load_module("test_prompt_budget_module", ROOT / "scripts" / "audit_prompt_budget.py")


class PromptBudgetTests(unittest.TestCase):
    def copy_skill(self, temp_dir: str) -> Path:
        target = Path(temp_dir) / "skill"
        shutil.copytree(ROOT, target)
        return target

    def test_current_skill_passes(self) -> None:
        errors, metrics = BUDGET.audit(ROOT)
        self.assertEqual([], errors)
        self.assertLessEqual(metrics["skill_bytes"], BUDGET.MAX_SKILL_BYTES)
        self.assertLessEqual(metrics["root_core_load_bytes"], BUDGET.MAX_CORE_LOAD_BYTES)

    def test_rejects_oversized_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = self.copy_skill(temp_dir)
            path = root / "SKILL.md"
            path.write_text(path.read_text(encoding="utf-8") + ("\nnoise" * 3000), encoding="utf-8")
            errors, _ = BUDGET.audit(root)
            self.assertTrue(any("SKILL.md exceeds" in item for item in errors))

    def test_rejects_long_description(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = self.copy_skill(temp_dir)
            path = root / "SKILL.md"
            text = path.read_text(encoding="utf-8")
            text = text.replace("description: ", "description: " + ("x" * 500), 1)
            path.write_text(text, encoding="utf-8")
            errors, _ = BUDGET.audit(root)
            self.assertTrue(any("frontmatter description exceeds" in item for item in errors))

    def test_rejects_reference_preloading(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = self.copy_skill(temp_dir)
            path = root / "SKILL.md"
            text = path.read_text(encoding="utf-8")
            text += "\nRead [all](references/research-sources.md) before provisioning sessions.\n"
            path.write_text(text, encoding="utf-8")
            errors, _ = BUDGET.audit(root)
            self.assertTrue(any("unconditional startup reference read" in item for item in errors))

    def test_rejects_oversized_role(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = self.copy_skill(temp_dir)
            path = root / "assets" / "agent-configs" / "pkos_company_domain_developer.toml"
            path.write_text(path.read_text(encoding="utf-8") + ("x" * 2000), encoding="utf-8")
            errors, _ = BUDGET.audit(root)
            self.assertTrue(any("pkos_company_domain_developer.toml exceeds" in item for item in errors))


if __name__ == "__main__":
    unittest.main()
