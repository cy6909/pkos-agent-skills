#!/usr/bin/env python3
"""Validate Company Swarm packaging, role definitions, examples, and dashboard rendering."""

from __future__ import annotations

import importlib.util
import re
import sys
import tempfile
from pathlib import Path
from types import ModuleType
from typing import List

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "SKILL.md",
    "agents/openai.yaml",
    "assets/config.toml.fragment",
    "assets/examples/organization.example.json",
    "assets/examples/mfsq-test-plan.example.json",
    "assets/examples/run-state.example.json",
    "references/organization-and-command-chain.md",
    "references/review-gates-and-delivery-lifecycle.md",
    "references/developer-tester-handoff.md",
    "references/mfsq-quality-model.md",
    "references/jenkins-pipeline-contract.md",
    "references/pkos-memory-and-notion-integration.md",
    "references/runtime-installation.md",
    "references/research-sources.md",
    "scripts/install.py",
    "scripts/validate_org.py",
    "scripts/validate_mfsq.py",
    "scripts/render_dashboard.py",
    "tests/test_company_swarm.py",
]

EXPECTED_AGENTS = {
    "pkos_company_technical_director.toml",
    "pkos_company_review_chair.toml",
    "pkos_company_requirements_architect.toml",
    "pkos_company_domain_developer.toml",
    "pkos_company_quality_engineer.toml",
    "pkos_company_test_manager.toml",
    "pkos_company_ci_jenkins_engineer.toml",
    "pkos_company_security_performance_engineer.toml",
    "pkos_company_integration_owner.toml",
    "pkos_company_governance_scribe.toml",
}


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load %s" % path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    errors: List[str] = []
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            errors.append("missing required file: %s" % rel)

    skill_path = ROOT / "SKILL.md"
    if skill_path.is_file():
        skill = skill_path.read_text(encoding="utf-8")
        if not skill.startswith("---\n"):
            errors.append("SKILL.md missing YAML frontmatter")
        match = re.search(r"^name:\s*(\S+)\s*$", skill, re.MULTILINE)
        if not match or match.group(1) != "codex-company-swarm":
            errors.append("SKILL.md name must be codex-company-swarm")
        for marker in ("TD-01", "RB-01", "MFSQ", "Jenkins", "G0", "G5", "PKOS"):
            if marker not in skill:
                errors.append("SKILL.md missing required marker: %s" % marker)

    openai_path = ROOT / "agents" / "openai.yaml"
    if openai_path.is_file():
        openai_text = openai_path.read_text(encoding="utf-8")
        if "allow_implicit_invocation: false" not in openai_text:
            errors.append("expensive Company Swarm must disable implicit invocation")

    actual_agents = {path.name for path in (ROOT / "assets" / "agent-configs").glob("*.toml")}
    if actual_agents != EXPECTED_AGENTS:
        errors.append("agent config set mismatch: expected %s, found %s" % (sorted(EXPECTED_AGENTS), sorted(actual_agents)))
    for path in sorted((ROOT / "assets" / "agent-configs").glob("*.toml")):
        text = path.read_text(encoding="utf-8")
        if 'model = "gpt-5.6-sol"' not in text:
            errors.append("%s must request gpt-5.6-sol" % path.name)
        if 'model_reasoning_effort = "max"' not in text:
            errors.append("%s must request max reasoning" % path.name)
        if "developer_instructions" not in text:
            errors.append("%s missing developer_instructions" % path.name)

    if not errors:
        try:
            org = load_module("company_validate_org", ROOT / "scripts" / "validate_org.py")
            org_data = org.load_json(ROOT / "assets" / "examples" / "organization.example.json")
            errors.extend("organization example: %s" % item for item in org.validate(org_data))

            mfsq = load_module("company_validate_mfsq", ROOT / "scripts" / "validate_mfsq.py")
            mfsq_data = mfsq.load_json(ROOT / "assets" / "examples" / "mfsq-test-plan.example.json")
            errors.extend("MFSQ example: %s" % item for item in mfsq.validate(mfsq_data))

            dashboard = load_module("company_render_dashboard", ROOT / "scripts" / "render_dashboard.py")
            state = dashboard.load_json(ROOT / "assets" / "examples" / "run-state.example.json")
            rendered = dashboard.render(state)
            for heading in ("# Company Swarm Dashboard", "## Organization", "## MFSQ evidence", "## CI/CD", "## PKOS writeback"):
                if heading not in rendered:
                    errors.append("dashboard missing heading: %s" % heading)
            with tempfile.TemporaryDirectory() as temp_dir:
                out = Path(temp_dir) / "dashboard.md"
                out.write_text(rendered, encoding="utf-8")
                if out.stat().st_size < 500:
                    errors.append("rendered dashboard is unexpectedly small")
        except Exception as exc:
            errors.append("example validation raised: %s" % exc)

    if errors:
        print("Company Swarm install validation failed:")
        for error in errors:
            print("- %s" % error)
        return 1

    print("Company Swarm install validation OK: %d role configs, examples and dashboard valid." % len(actual_agents))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
