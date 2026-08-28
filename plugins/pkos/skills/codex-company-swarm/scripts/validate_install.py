#!/usr/bin/env python3
"""Validate Company Swarm packaging, Sol Max roles, durable Notion coordination, examples, and dashboard."""

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
    "assets/examples/coordination-state.example.json",
    "assets/examples/event-ledger.example.json",
    "assets/examples/notion-schema.example.json",
    "assets/examples/notion-sync.example.json",
    "assets/examples/pack-delta.example.json",
    "assets/examples/traceability.example.json",
    "assets/examples/checkpoint.example.json",
    "assets/examples/resume-plan.example.json",
    "assets/examples/dashboard-v05.example.md",
    "references/organization-and-command-chain.md",
    "references/review-gates-and-delivery-lifecycle.md",
    "references/developer-tester-handoff.md",
    "references/mfsq-quality-model.md",
    "references/jenkins-pipeline-contract.md",
    "references/pkos-memory-and-notion-integration.md",
    "references/notion-durable-coordination-plane.md",
    "references/event-sync-and-outbox.md",
    "references/context-pack-versioning.md",
    "references/checkpoint-resume-and-takeover.md",
    "references/traceability-and-retrospective.md",
    "references/runtime-installation.md",
    "references/research-sources.md",
    "scripts/install.py",
    "scripts/validate_org.py",
    "scripts/validate_mfsq.py",
    "scripts/render_dashboard.py",
    "scripts/validate_coordination.py",
    "scripts/validate_event_ledger.py",
    "scripts/validate_notion_schema.py",
    "scripts/validate_notion_sync.py",
    "scripts/validate_pack_delta.py",
    "scripts/validate_traceability.py",
    "scripts/validate_checkpoint.py",
    "scripts/validate_coordination_bundle.py",
    "scripts/build_resume_plan.py",
    "tests/test_company_swarm.py",
    "tests/test_notion_coordination.py",
]

BUNDLE_FILES = [
    "coordination-state.json",
    "event-ledger.json",
    "notion-schema.json",
    "notion-sync.json",
    "pack-delta.json",
    "traceability.json",
    "checkpoint.json",
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
    for rel in BUNDLE_FILES:
        if not (ROOT / "assets" / "examples" / "coordination-bundle" / rel).is_file():
            errors.append("missing coordination bundle example: %s" % rel)

    skill_path = ROOT / "SKILL.md"
    if skill_path.is_file():
        skill = skill_path.read_text(encoding="utf-8")
        if not skill.startswith("---\n"):
            errors.append("SKILL.md missing YAML frontmatter")
        match = re.search(r"^name:\s*(\S+)\s*$", skill, re.MULTILINE)
        if not match or match.group(1) != "codex-company-swarm":
            errors.append("SKILL.md name must be codex-company-swarm")
        for marker in (
            "TD-01",
            "PK-01",
            "RB-01",
            "Notion Durable Coordination Plane",
            "MFSQ",
            "Jenkins",
            "G0",
            "G5",
            "TAKEOVER",
            "traceability",
            "BLOCKED_NOTION_COORDINATION",
        ):
            if marker not in skill:
                errors.append("SKILL.md missing required marker: %s" % marker)

    openai_path = ROOT / "agents" / "openai.yaml"
    if openai_path.is_file():
        openai_text = openai_path.read_text(encoding="utf-8")
        if "allow_implicit_invocation: false" not in openai_text:
            errors.append("expensive Company Swarm must disable implicit invocation")
        if "persistent PK-01" not in openai_text or "Notion Durable Coordination Plane" not in openai_text:
            errors.append("openai.yaml default prompt must require persistent PK-01 and durable coordination")

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
        if path.name != "pkos_company_requirements_architect.toml" and "director_epoch" not in text.lower() and "Director epoch" not in text:
            errors.append("%s must enforce Director epoch freshness" % path.name)
        if "Pack" not in text:
            errors.append("%s must enforce Shared Pack freshness" % path.name)
    scribe_path = ROOT / "assets" / "agent-configs" / "pkos_company_governance_scribe.toml"
    if scribe_path.is_file():
        scribe = scribe_path.read_text(encoding="utf-8")
        for marker in ("single Notion coordination writer", "outbox", "receipts", "watermark", "Context Request", "takeover"):
            if marker.lower() not in scribe.lower():
                errors.append("governance scribe missing continuous coordination marker: %s" % marker)

    if not errors:
        try:
            org = load_module("company_validate_org", ROOT / "scripts" / "validate_org.py")
            org_data = org.load_json(ROOT / "assets" / "examples" / "organization.example.json")
            errors.extend("organization example: %s" % item for item in org.validate(org_data))

            mfsq = load_module("company_validate_mfsq", ROOT / "scripts" / "validate_mfsq.py")
            mfsq_data = mfsq.load_json(ROOT / "assets" / "examples" / "mfsq-test-plan.example.json")
            errors.extend("MFSQ example: %s" % item for item in mfsq.validate(mfsq_data))

            validators = [
                ("coordination", "validate_coordination.py", "coordination-state.example.json"),
                ("events", "validate_event_ledger.py", "event-ledger.example.json"),
                ("notion schema", "validate_notion_schema.py", "notion-schema.example.json"),
                ("notion sync", "validate_notion_sync.py", "notion-sync.example.json"),
                ("pack delta", "validate_pack_delta.py", "pack-delta.example.json"),
                ("traceability", "validate_traceability.py", "traceability.example.json"),
            ]
            for label, script_name, example_name in validators:
                module = load_module("company_%s" % label.replace(" ", "_"), ROOT / "scripts" / script_name)
                value = module.load_json(ROOT / "assets" / "examples" / example_name)
                errors.extend("%s example: %s" % (label, item) for item in module.validate(value))

            event_module = load_module("company_events_checkpoint", ROOT / "scripts" / "validate_event_ledger.py")
            checkpoint_module = load_module("company_checkpoint", ROOT / "scripts" / "validate_checkpoint.py")
            ledger = event_module.load_json(ROOT / "assets" / "examples" / "event-ledger.example.json")
            checkpoint = checkpoint_module.load_json(ROOT / "assets" / "examples" / "checkpoint.example.json")
            errors.extend("checkpoint example: %s" % item for item in checkpoint_module.validate(checkpoint, ledger))

            bundle = load_module("company_coordination_bundle", ROOT / "scripts" / "validate_coordination_bundle.py")
            errors.extend(
                "coordination bundle: %s" % item
                for item in bundle.validate_bundle(ROOT / "assets" / "examples" / "coordination-bundle")
            )

            resume = load_module("company_resume", ROOT / "scripts" / "build_resume_plan.py")
            plan = resume.build(checkpoint, takeover=True)
            if plan.get("target_director_epoch") != checkpoint.get("director_epoch") + 1:
                errors.append("resume plan must increment Director epoch on takeover")
            if not plan.get("sessions_requiring_reissue"):
                errors.append("takeover resume plan must reissue stale session packets")

            dashboard = load_module("company_render_dashboard", ROOT / "scripts" / "render_dashboard.py")
            state = dashboard.load_json(ROOT / "assets" / "examples" / "run-state.example.json")
            rendered = dashboard.render(state)
            for heading in (
                "# Company Swarm Dashboard",
                "## Durable coordination",
                "## Organization",
                "## MFSQ evidence",
                "## CI/CD",
                "## PKOS writeback",
            ):
                if heading not in rendered:
                    errors.append("dashboard missing heading: %s" % heading)
            for marker in ("Notion mode", "Event watermark", "Traceability", "Resume token"):
                if marker not in rendered:
                    errors.append("dashboard missing coordination marker: %s" % marker)
            with tempfile.TemporaryDirectory() as temp_dir:
                out = Path(temp_dir) / "dashboard.md"
                out.write_text(rendered, encoding="utf-8")
                if out.stat().st_size < 1000:
                    errors.append("rendered dashboard is unexpectedly small")
        except Exception as exc:
            errors.append("example validation raised: %s" % exc)

    if errors:
        print("Company Swarm install validation failed:")
        for error in errors:
            print("- %s" % error)
        return 1

    print(
        "Company Swarm v0.5 install validation OK: %d Sol Max roles, durable Notion coordination bundle, examples, and dashboard valid."
        % len(actual_agents)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
