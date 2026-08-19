#!/usr/bin/env python3
"""Validate the Codex Sol-Luna Skill package and deterministic examples."""

from __future__ import annotations

import importlib.util
import json
import py_compile
import re
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 on the canonical remote-12 environment.
    tomllib = None

ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "codex-sol-luna-workflow"
REQUIRED = [
    "SKILL.md",
    "agents/openai.yaml",
    "references/role-boundaries.md",
    "references/routing-policy.md",
    "references/task-contracts.md",
    "references/parallel-coordination.md",
    "references/assurance-gates.md",
    "references/efficiency-evaluation.md",
    "references/runtime-setup.md",
    "references/shared-memory-environment-and-session-pool.md",
    "references/research-sources.md",
    "scripts/validate_route.py",
    "scripts/settle_results.py",
    "scripts/score_efficiency.py",
    "scripts/install.py",
    "scripts/schedule_sessions.py",
    "assets/agent-configs/codex_luna_worker.toml",
    "assets/agent-configs/codex_luna_max_worker.toml",
    "assets/agent-configs/codex_sol_planner.toml",
    "assets/agent-configs/codex_sol_max_planner.toml",
    "assets/agent-configs/codex_sol_reviewer.toml",
    "assets/agent-configs/codex_sol_max_reviewer.toml",
    "assets/config-snippets/multi-agent-v2.toml",
    "assets/routes/adaptive-standard.json",
    "assets/routes/max-pair-strict.json",
    "assets/routes/parallel-two-lane.json",
    "assets/results/example-provider-a.json",
    "assets/results/example-provider-b.json",
    "assets/metrics/example-run.json",
    "assets/session-pools/example-pool.json",
]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_agent_toml(text: str) -> dict[str, object]:
    """Load top-level agent TOML without adding a Python 3.10 dependency.

    Python 3.11+ uses the complete standard-library parser. The fallback is
    deliberately strict and supports only this package's flat strings,
    string arrays, and multiline basic strings; unsupported TOML fails closed.
    """
    if tomllib is not None:
        return tomllib.loads(text)

    data: dict[str, object] = {}
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        line_number = index + 1
        stripped = lines[index].strip()
        index += 1
        if not stripped or stripped.startswith("#"):
            continue
        match = re.fullmatch(r"([A-Za-z0-9_-]+)\s*=\s*(.*)", stripped)
        if not match:
            raise ValueError(f"line {line_number}: unsupported TOML syntax")
        key, raw = match.groups()
        if key in data:
            raise ValueError(f"line {line_number}: duplicate key {key!r}")
        if raw.startswith('"""'):
            remainder = raw[3:]
            chunks: list[str] = []
            if remainder.endswith('"""'):
                data[key] = remainder[:-3]
                continue
            if remainder:
                chunks.append(remainder)
            while index < len(lines):
                current = lines[index]
                index += 1
                if current.endswith('"""'):
                    chunks.append(current[:-3])
                    data[key] = "\n".join(chunks)
                    break
                chunks.append(current)
            else:
                raise ValueError(f"line {line_number}: unterminated multiline string")
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"line {line_number}: unsupported TOML value: {exc}") from exc
        if not isinstance(value, (str, list, bool, int, float)):
            raise ValueError(f"line {line_number}: unsupported TOML value type")
        if isinstance(value, list) and not all(isinstance(item, str) for item in value):
            raise ValueError(f"line {line_number}: only string arrays are supported")
        data[key] = value
    return data


def validate_frontmatter(errors: list[str]) -> None:
    path = ROOT / "SKILL.md"
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        errors.append("SKILL.md has invalid YAML frontmatter boundaries")
        return
    frontmatter = match.group(1)
    name = re.search(r"^name:\s*(.+?)\s*$", frontmatter, re.M)
    description = re.search(r"^description:\s*(.+?)\s*$", frontmatter, re.M)
    if not name or name.group(1).strip() != SKILL_NAME:
        errors.append("SKILL.md name does not match directory")
    if not description or len(description.group(1).strip()) < 80:
        errors.append("SKILL.md description is missing or not discriminating")
    if "TODO" in text or "TBD" in text or "[TODO:" in text:
        errors.append("SKILL.md contains unfinished placeholders")
    if "does not require CodeHive" not in text:
        errors.append("SKILL.md must state that CodeHive is not required")


def validate_openai_yaml(errors: list[str]) -> None:
    text = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
    for token in (
        "display_name:",
        "short_description:",
        "default_prompt:",
        "$codex-sol-luna-workflow",
    ):
        if token not in text:
            errors.append(f"agents/openai.yaml missing {token}")


def validate_links(errors: list[str]) -> None:
    markdown_files = [ROOT / "SKILL.md", *(ROOT / "references").glob("*.md")]
    for path in markdown_files:
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(r"\]\((?!https?://|#)([^)#]+)", text):
            raw = match.group(1)
            target = (path.parent / raw).resolve()
            try:
                target.relative_to(ROOT)
            except ValueError:
                errors.append(f"{path.relative_to(ROOT)} links outside package: {raw}")
                continue
            if not target.exists():
                errors.append(f"{path.relative_to(ROOT)} has missing link: {raw}")


def validate_toml(errors: list[str]) -> None:
    for path in (ROOT / "assets" / "agent-configs").glob("*.toml"):
        try:
            data = load_agent_toml(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            errors.append(f"{path.relative_to(ROOT)} invalid TOML: {exc}")
            continue
        for field in (
            "name",
            "description",
            "model",
            "model_reasoning_effort",
            "developer_instructions",
        ):
            if not data.get(field):
                errors.append(f"{path.relative_to(ROOT)} missing {field}")
        if data.get("model") not in {"gpt-5.6-sol", "gpt-5.6-luna"}:
            errors.append(f"{path.relative_to(ROOT)} uses unsupported model")
        if data.get("model_reasoning_effort") == "ultra":
            errors.append(f"{path.relative_to(ROOT)} uses forbidden ultra effort")
        if data.get("name") != path.stem:
            errors.append(f"{path.relative_to(ROOT)} name must match file stem")


def validate_scripts(errors: list[str]) -> None:
    for path in (ROOT / "scripts").glob("*.py"):
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"{path.relative_to(ROOT)} does not compile: {exc.msg}")


def validate_routes(errors: list[str]) -> None:
    validator = load_module("validate_route", ROOT / "scripts" / "validate_route.py")
    for path in sorted((ROOT / "assets" / "routes").glob("*.json")):
        route = validator.load_route(path)
        route_errors, _warnings = validator.validate_route(route)
        errors.extend(f"{path.relative_to(ROOT)}: {message}" for message in route_errors)

    parallel_path = ROOT / "assets" / "routes" / "parallel-two-lane.json"
    bad = json.loads(parallel_path.read_text(encoding="utf-8"))
    bad["lanes"][1]["write_paths"] = ["src/providers/a/shared.rs"]
    bad_errors, _ = validator.validate_route(bad)
    if not any("parallel ownership overlap" in message for message in bad_errors):
        errors.append("negative overlap test did not fail as expected")

    negative_cases = [
        (
            "spawned planner",
            lambda route: route["planner"].update({"spawn_planner": True}),
            "planner.spawn_planner must be false",
        ),
        (
            "unconfirmed session cap",
            lambda route: route["session_policy"].update({"confirmed_by_user": False}),
            "session_policy must be confirmed by the user",
        ),
        (
            "missing shared memory",
            lambda route: route["lanes"][0].update({"memory_pack_ref": "wrong-pack.md"}),
            "memory_pack_ref must match",
        ),
        (
            "local test",
            lambda route: route["lanes"][0]["verification"][0].update({"environment": "local-development"}),
            "must run in remote-12",
        ),
        (
            "UI without Figma gate",
            lambda route: route["lanes"][0].update({"ui_change": True}),
            "UI routes require design_policy",
        ),
    ]
    source = json.loads((ROOT / "assets" / "routes" / "adaptive-standard.json").read_text(encoding="utf-8"))
    for label, mutate, expected in negative_cases:
        bad_route = json.loads(json.dumps(source))
        mutate(bad_route)
        bad_errors, _ = validator.validate_route(bad_route)
        if not any(expected in message for message in bad_errors):
            errors.append(f"negative route test {label!r} did not fail with {expected!r}")


def validate_scheduler(errors: list[str]) -> None:
    scheduler = load_module("schedule_sessions", ROOT / "scripts" / "schedule_sessions.py")
    route = json.loads((ROOT / "assets" / "routes" / "parallel-two-lane.json").read_text(encoding="utf-8"))
    pool = json.loads((ROOT / "assets" / "session-pools" / "example-pool.json").read_text(encoding="utf-8"))
    result = scheduler.recommend(route, pool)
    actions = {item.get("lane_id"): item.get("action") for item in result.get("recommendations", [])}
    if actions.get("implement-provider-a") != "reuse":
        errors.append("scheduler did not reuse the affinity-matched idle worker")
    if actions.get("implement-provider-b") != "queue":
        errors.append("scheduler exceeded the confirmed worker cap instead of queuing")


def validate_settlement(errors: list[str]) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        output = Path(temp_dir) / "settlement.json"
        command = [
            sys.executable,
            str(ROOT / "scripts" / "settle_results.py"),
            str(ROOT / "assets" / "routes" / "parallel-two-lane.json"),
            str(ROOT / "assets" / "results" / "example-provider-a.json"),
            str(ROOT / "assets" / "results" / "example-provider-b.json"),
            "--output",
            str(output),
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            errors.append(f"settlement example failed: {result.stderr or result.stdout}")
            return
        data = json.loads(output.read_text(encoding="utf-8"))
        if data.get("overall") != "INTEGRATION_READY":
            errors.append(f"settlement example expected INTEGRATION_READY, got {data.get('overall')}")
        if not data.get("barrier", {}).get("ready"):
            errors.append("settlement example barrier did not become ready")


def validate_efficiency(errors: list[str]) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        output = Path(temp_dir) / "score.json"
        command = [
            sys.executable,
            str(ROOT / "scripts" / "score_efficiency.py"),
            str(ROOT / "assets" / "metrics" / "example-run.json"),
            "--output",
            str(output),
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            errors.append(f"efficiency example failed: {result.stderr or result.stdout}")
            return
        data = json.loads(output.read_text(encoding="utf-8"))
        if data.get("decision") != "EFFICIENT_NON_INFERIOR":
            errors.append(
                "efficiency example expected EFFICIENT_NON_INFERIOR, "
                f"got {data.get('decision')}"
            )
        if data.get("speedup", 0) <= 1:
            errors.append("efficiency example did not calculate a speedup")


def validate_installer(errors: list[str]) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        command = [
            sys.executable,
            str(ROOT / "scripts" / "install.py"),
            "--agents-only",
            "--codex-home",
            temp_dir,
            "--dry-run",
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            errors.append(f"installer dry-run failed: {result.stderr or result.stdout}")


def main() -> int:
    errors: list[str] = []
    for relative in REQUIRED:
        if not (ROOT / relative).exists():
            errors.append(f"missing required file: {relative}")

    if not errors:
        validate_frontmatter(errors)
        validate_openai_yaml(errors)
        validate_links(errors)
        validate_toml(errors)
        validate_scripts(errors)
        validate_routes(errors)
        validate_scheduler(errors)
        validate_settlement(errors)
        validate_efficiency(errors)
        validate_installer(errors)

    if errors:
        print("Codex Sol-Luna Skill validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    file_count = sum(1 for path in ROOT.rglob("*") if path.is_file())
    print(f"VALID: {SKILL_NAME} ({file_count} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
