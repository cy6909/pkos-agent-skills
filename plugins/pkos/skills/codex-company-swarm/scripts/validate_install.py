#!/usr/bin/env python3
"""Validate Company Swarm packaging, prompt budget, roles, examples, and coordination contracts."""

from __future__ import annotations

import importlib.util
import re
import sys
import tempfile
from pathlib import Path
from types import ModuleType
from typing import Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
VERSION = "v0.9"

REQUIRED_FILES = [
    "SKILL.md",
    "agents/openai.yaml",
    "assets/config.toml.fragment",
    "assets/examples/organization.example.json",
    "assets/examples/staffing-standard-six.example.json",
    "assets/examples/staffing-small-two-lane.example.json",
    "assets/examples/staffing-luna-escalation-reuse.example.json",
    "assets/schemas/organization-v3.schema.json",
    "assets/schemas/task-packet-v2.schema.json",
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
    "references/organization-and-command-chain.md",
    "references/visible-task-staffing-and-concurrency.md",
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
    "scripts/audit_prompt_budget.py",
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
    "tests/test_prompt_budget.py",
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


def validate_static(errors: List[str]) -> None:
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
            "Treat this file as an executable control program",
            "## Registers",
            "## Reference loading",
            "TD-01",
            "PK-01",
            "MFSQ",
            "G0",
            "G5",
            "TAKEOVER",
            "visible Codex task",
            "CONCURRENCY_UNDERFILLED",
            "NOTION_WRITE_LANGUAGE=zh-CN",
            "BLOCKED_NOTION_COORDINATION",
        ):
            if marker not in skill:
                errors.append("SKILL.md missing marker: %s" % marker)

    openai_path = ROOT / "agents" / "openai.yaml"
    if openai_path.is_file():
        value = openai_path.read_text(encoding="utf-8")
        if "allow_implicit_invocation: true" not in value:
            errors.append("Company Swarm must be discoverable in the Codex skills catalog")
        if "TD-01" not in value or "PK-01" not in value:
            errors.append("openai.yaml must route TD-01 and PK-01")

    actual = {path.name for path in (ROOT / "assets" / "agent-configs").glob("*.toml")}
    if actual != EXPECTED_AGENTS:
        errors.append("agent config set mismatch: %s" % sorted(actual))
    for path in sorted((ROOT / "assets" / "agent-configs").glob("*.toml")):
        value = path.read_text(encoding="utf-8")
        for marker in ("ROLE=", "MAY_DELEGATE="):
            if marker not in value:
                errors.append("%s missing marker: %s" % (path.name, marker))
        if re.search(r'^model\s*=|^model_reasoning_effort\s*=', value, re.MULTILINE):
            errors.append("%s must not hard-code model routing" % path.name)
    scribe_path = ROOT / "assets" / "agent-configs" / "pkos_company_governance_scribe.toml"
    if scribe_path.is_file():
        scribe = scribe_path.read_text(encoding="utf-8").lower()
        for marker in ("single", "notion", "outbox", "receipt", "watermark", "context request", "takeover", "notion_write_language=zh-cn"):
            if marker not in scribe:
                errors.append("PK-01 config missing marker: %s" % marker)

    budget = load_module("company_prompt_budget", ROOT / "scripts" / "audit_prompt_budget.py")
    budget_errors, metrics = budget.audit(ROOT)
    errors.extend("prompt budget: %s" % item for item in budget_errors)
    print(
        "Prompt budget: SKILL=%s bytes (~%s tokens); root core=%s bytes (~%s tokens)."
        % (
            metrics.get("skill_bytes", 0),
            metrics.get("skill_tokens_estimate", 0),
            metrics.get("root_core_load_bytes", 0),
            metrics.get("root_core_tokens_estimate", 0),
        )
    )


def validate_examples(errors: List[str]) -> None:
    examples = ROOT / "assets" / "examples"
    scripts = ROOT / "scripts"

    pairs: List[Tuple[str, str, str]] = [
        ("organization", "validate_org.py", "organization.example.json"),
        ("MFSQ", "validate_mfsq.py", "mfsq-test-plan.example.json"),
        ("coordination", "validate_coordination.py", "coordination-state.example.json"),
        ("events", "validate_event_ledger.py", "event-ledger.example.json"),
        ("Notion schema", "validate_notion_schema.py", "notion-schema.example.json"),
        ("Notion sync", "validate_notion_sync.py", "notion-sync.example.json"),
        ("Pack Delta", "validate_pack_delta.py", "pack-delta.example.json"),
        ("traceability", "validate_traceability.py", "traceability.example.json"),
    ]
    modules = {}
    for label, script_name, example_name in pairs:
        module = load_module("company_%s" % label.lower().replace(" ", "_"), scripts / script_name)
        modules[script_name] = module
        value = module.load_json(examples / example_name)
        errors.extend("%s example: %s" % (label, item) for item in module.validate(value))

    org_module = modules["validate_org.py"]
    for example_name in ("staffing-small-two-lane.example.json", "staffing-luna-escalation-reuse.example.json"):
        value = org_module.load_json(examples / example_name)
        errors.extend("%s: %s" % (example_name, item) for item in org_module.validate(value))

    ledger = modules["validate_event_ledger.py"].load_json(examples / "event-ledger.example.json")
    checkpoint_module = load_module("company_checkpoint", scripts / "validate_checkpoint.py")
    checkpoint = checkpoint_module.load_json(examples / "checkpoint.example.json")
    errors.extend("checkpoint example: %s" % item for item in checkpoint_module.validate(checkpoint, ledger))

    bundle = load_module("company_bundle", scripts / "validate_coordination_bundle.py")
    errors.extend(
        "coordination bundle: %s" % item
        for item in bundle.validate_bundle(examples / "coordination-bundle")
    )

    resume = load_module("company_resume", scripts / "build_resume_plan.py")
    plan = resume.build(checkpoint, takeover=True)
    if plan.get("target_director_epoch") != checkpoint.get("director_epoch") + 1:
        errors.append("takeover plan must increment Director epoch")
    if not plan.get("sessions_requiring_reissue"):
        errors.append("takeover plan must reissue stale packets")

    dashboard = load_module("company_dashboard", scripts / "render_dashboard.py")
    state = dashboard.load_json(examples / "run-state.example.json")
    rendered = dashboard.render(state)
    for marker in (
        "# Company Swarm Dashboard",
        "## Durable coordination",
        "## Organization",
        "## MFSQ evidence",
        "## CI/CD",
        "## PKOS writeback",
        "Event watermark",
        "Traceability",
        "Resume token",
    ):
        if marker not in rendered:
            errors.append("dashboard missing marker: %s" % marker)
    with tempfile.TemporaryDirectory() as temp_dir:
        output = Path(temp_dir) / "dashboard.md"
        output.write_text(rendered, encoding="utf-8")
        if output.stat().st_size < 1000:
            errors.append("rendered dashboard is unexpectedly small")


def main(argv: Iterable[str] | None = None) -> int:
    del argv
    errors: List[str] = []
    try:
        validate_static(errors)
        if not errors:
            validate_examples(errors)
    except Exception as exc:
        errors.append("validation raised: %s" % exc)

    if errors:
        print("Company Swarm install validation failed:", file=sys.stderr)
        for error in errors:
            print("- %s" % error, file=sys.stderr)
        return 1

    print("Company Swarm %s validation OK: visible routing, budgets, concurrency, coordination, examples, and dashboard." % VERSION)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
