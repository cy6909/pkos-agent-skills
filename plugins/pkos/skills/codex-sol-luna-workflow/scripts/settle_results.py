#!/usr/bin/env python3
"""Settle Codex Sol-Luna child results deterministically.

Results are matched by run/generation/lane, validated against ownership and
acceptance contracts, and summarized without relying on completion-message order.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESULT_VERSION = "codex-sol-luna-result-v2"
ALLOWED_STATUSES = {"complete", "partial", "blocked", "failed"}
ALLOWED_IDENTITY = {"observed", "configured", "unverified"}


def load_validator():
    path = ROOT / "scripts" / "validate_route.py"
    spec = importlib.util.spec_from_file_location("validate_route", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load validate_route.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_validator()


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path}: root must be an object")
    return data


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def expected_command_map(lane: dict[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in as_list(lane.get("verification")):
        if isinstance(item, dict) and isinstance(item.get("command"), str):
            result[item["command"]] = str(item.get("expected", ""))
    return result


def settle_one(
    route: dict[str, Any],
    lane: dict[str, Any],
    result: dict[str, Any],
    source: str,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    lane_id = lane.get("id")

    if result.get("version") != RESULT_VERSION:
        errors.append(f"version must be {RESULT_VERSION}")
    if result.get("run_id") != route.get("run_id"):
        errors.append("run_id mismatch")
    if result.get("generation") != route.get("generation"):
        classification = "stale" if isinstance(result.get("generation"), int) and result.get("generation", 0) < route.get("generation", 0) else "invalid"
        return {
            "lane_id": lane_id,
            "source": source,
            "classification": classification,
            "errors": ["generation mismatch"],
            "warnings": [],
            "status": result.get("status"),
        }
    if result.get("lane_id") != lane_id:
        errors.append("lane_id mismatch")
    if result.get("base_revision") != route.get("base_revision"):
        errors.append("base_revision mismatch")
    if result.get("status") not in ALLOWED_STATUSES:
        errors.append(f"unsupported status {result.get('status')!r}")

    if not isinstance(result.get("session_id"), str) or not result.get("session_id", "").strip():
        errors.append("session_id is required")
    if not isinstance(result.get("session_reused"), bool):
        errors.append("session_reused must be boolean")
    if result.get("role_class") != lane.get("role_class"):
        errors.append("role_class contradicts route")
    if result.get("memory_loaded") is not True:
        errors.append("shared Memory Pack was not loaded")
    if result.get("memory_access") != "direct-notion":
        errors.append("worker must load shared memory through direct Notion access")
    if result.get("memory_pack_ref") != lane.get("memory_pack_ref"):
        errors.append("memory_pack_ref contradicts route")
    expected_skills = {str(item) for item in as_list(lane.get("required_skills"))}
    loaded_skills = {str(item) for item in as_list(result.get("skills_loaded"))}
    if not expected_skills.issubset(loaded_skills):
        errors.append("required skills were not all loaded")
    expected_memory_sources = {
        str(item)
        for item in as_list(route.get("shared_memory", {}).get("notion_source_refs"))
    }
    actual_memory_sources = {str(item) for item in as_list(result.get("memory_source_refs"))}
    if not expected_memory_sources.issubset(actual_memory_sources):
        errors.append("required Notion memory sources were not acknowledged")

    expected_model = lane.get("model")
    expected_effort = lane.get("effort")
    requested_model = result.get("requested_model")
    requested_effort = result.get("requested_effort")
    observed_model = result.get("observed_model")
    observed_effort = result.get("observed_effort")
    identity = result.get("identity_confidence")

    if requested_model is not None and requested_model != expected_model:
        errors.append("requested_model contradicts route")
    if requested_effort is not None and requested_effort != expected_effort:
        errors.append("requested_effort contradicts route")
    if observed_model is not None and observed_model != expected_model:
        errors.append("observed_model contradicts route")
    if observed_effort is not None and observed_effort != expected_effort:
        errors.append("observed_effort contradicts route")
    if identity not in ALLOWED_IDENTITY:
        errors.append("identity_confidence must be observed, configured, or unverified")
    if route.get("assurance") == "strict" and identity == "unverified":
        errors.append("strict assurance cannot settle an unverified routed model")

    write_paths = [str(p) for p in as_list(lane.get("write_paths"))]
    excluded_paths = [str(p) for p in as_list(lane.get("excluded_paths"))]
    changed_paths = result.get("changed_paths", [])
    if not isinstance(changed_paths, list):
        errors.append("changed_paths must be a list")
        changed_paths = []
    for changed in changed_paths:
        if not isinstance(changed, str):
            errors.append("changed_paths must contain strings")
            continue
        if lane.get("role") == "reviewer":
            errors.append(f"read-only reviewer changed {changed}")
            continue
        if not any(VALIDATOR.path_contains(scope, changed) for scope in write_paths):
            errors.append(f"out-of-scope changed path: {changed}")
        if any(VALIDATOR.path_contains(scope, changed) for scope in excluded_paths):
            errors.append(f"changed excluded path: {changed}")

    acceptance_results = result.get("acceptance", [])
    if not isinstance(acceptance_results, list):
        errors.append("acceptance must be a list")
        acceptance_results = []
    expected_criteria = [str(x) for x in as_list(lane.get("acceptance"))]
    actual_by_criterion: dict[str, dict[str, Any]] = {}
    for item in acceptance_results:
        if not isinstance(item, dict) or not isinstance(item.get("criterion"), str):
            errors.append("acceptance entries require criterion")
            continue
        criterion = item["criterion"]
        if criterion in actual_by_criterion:
            errors.append(f"duplicate acceptance result: {criterion}")
        actual_by_criterion[criterion] = item
    for criterion in expected_criteria:
        item = actual_by_criterion.get(criterion)
        if item is None:
            errors.append(f"missing acceptance result: {criterion}")
            continue
        if item.get("result") != "pass":
            errors.append(f"acceptance did not pass: {criterion} ({item.get('result')})")
        if not item.get("evidence_ref"):
            errors.append(f"acceptance lacks evidence_ref: {criterion}")
    for criterion in actual_by_criterion:
        if criterion not in expected_criteria:
            warnings.append(f"extra acceptance result not in route: {criterion}")

    verification_results = result.get("verification", [])
    if not isinstance(verification_results, list):
        errors.append("verification must be a list")
        verification_results = []
    actual_commands: dict[str, dict[str, Any]] = {}
    for item in verification_results:
        if not isinstance(item, dict) or not isinstance(item.get("command"), str):
            errors.append("verification entries require command")
            continue
        command = item["command"]
        if command in actual_commands:
            errors.append(f"duplicate verification result: {command}")
        actual_commands[command] = item
    for command in expected_command_map(lane):
        item = actual_commands.get(command)
        if item is None:
            errors.append(f"missing verification result: {command}")
            continue
        if command.startswith("read-only review packet validation"):
            if item.get("verdict") not in {"SHIP", "FIX_FIRST", "RETHINK", "UNUSABLE_RUNTIME"}:
                errors.append("review verification requires a valid verdict")
        elif item.get("exit_code") != 0:
            errors.append(f"verification failed: {command} exit={item.get('exit_code')}")
        expected_item = next(
            (
                entry
                for entry in as_list(lane.get("verification"))
                if isinstance(entry, dict) and entry.get("command") == command
            ),
            {},
        )
        if item.get("environment") != expected_item.get("environment"):
            errors.append(f"verification environment mismatch: {command}")
        if item.get("kind") != expected_item.get("kind"):
            errors.append(f"verification kind mismatch: {command}")
        if expected_item.get("kind") in VALIDATOR.REMOTE_REQUIRED_KINDS:
            if result.get("remote_pull_confirmed") is not True:
                errors.append("remote-required verification lacks pull confirmation")
            if not result.get("remote_revision"):
                errors.append("remote-required verification lacks remote_revision")
        if not item.get("evidence_ref"):
            errors.append(f"verification lacks evidence_ref: {command}")

    if lane.get("ui_change") is True and not result.get("figma_evidence_ref"):
        errors.append("UI lane lacks Figma evidence")

    gaps = result.get("gaps", [])
    if not isinstance(gaps, list):
        errors.append("gaps must be a list")
        gaps = []
    blocking_gaps = [gap for gap in gaps if isinstance(gap, dict) and gap.get("blocking") is True]
    if blocking_gaps:
        errors.append(f"{len(blocking_gaps)} blocking gap(s) remain")

    if result.get("status") != "complete":
        classification = result.get("status") or "invalid"
    elif errors:
        classification = "invalid"
    else:
        classification = "settled"

    return {
        "lane_id": lane_id,
        "source": source,
        "classification": classification,
        "status": result.get("status"),
        "identity_confidence": identity,
        "session_id": result.get("session_id"),
        "session_reused": result.get("session_reused"),
        "memory_pack_ref": result.get("memory_pack_ref"),
        "memory_access": result.get("memory_access"),
        "remote_revision": result.get("remote_revision"),
        "changed_paths": changed_paths,
        "errors": errors,
        "warnings": warnings,
        "evidence_refs": as_list(result.get("evidence_refs")),
        "started_at": result.get("started_at"),
        "completed_at": result.get("completed_at"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("route", type=Path)
    parser.add_argument("results", nargs="*", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    try:
        route = load_json(args.route)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    route_errors, route_warnings = VALIDATOR.validate_route(route)
    if route_errors:
        for error in route_errors:
            print(f"ROUTE ERROR: {error}", file=sys.stderr)
        return 2

    lanes = {lane["id"]: lane for lane in route.get("lanes", []) if isinstance(lane, dict) and isinstance(lane.get("id"), str)}
    result_by_lane: dict[str, tuple[dict[str, Any], str]] = {}
    conflicts: list[str] = []
    unknown_results: list[str] = []

    for path in args.results:
        try:
            result = load_json(path)
        except ValueError as exc:
            conflicts.append(str(exc))
            continue
        lane_id = result.get("lane_id")
        if lane_id not in lanes:
            unknown_results.append(f"{path}: unknown lane_id {lane_id!r}")
            continue
        if lane_id in result_by_lane:
            prior, prior_source = result_by_lane[lane_id]
            if prior != result:
                conflicts.append(f"conflicting duplicate results for lane {lane_id}: {prior_source} and {path}")
            continue
        result_by_lane[lane_id] = (result, str(path))

    settled: list[dict[str, Any]] = []
    for lane_id, lane in lanes.items():
        if lane_id not in result_by_lane:
            settled.append(
                {
                    "lane_id": lane_id,
                    "source": None,
                    "classification": "pending",
                    "status": None,
                    "errors": [],
                    "warnings": [],
                }
            )
            continue
        result, source = result_by_lane[lane_id]
        settled.append(settle_one(route, lane, result, source))

    classification_by_lane = {item["lane_id"]: item["classification"] for item in settled}
    barrier = route.get("integration_barrier")
    barrier_status: dict[str, Any] | None = None
    if isinstance(barrier, dict):
        deps = barrier.get("depends_on", [])
        ready = all(classification_by_lane.get(dep) == "settled" for dep in deps)
        barrier_status = {
            "id": barrier.get("id"),
            "depends_on": deps,
            "integration_lane": barrier.get("integration_lane"),
            "ready": ready,
            "blocking": {
                dep: classification_by_lane.get(dep, "missing")
                for dep in deps
                if classification_by_lane.get(dep) != "settled"
            },
        }

    reviewer_lanes = [lane for lane in route.get("lanes", []) if lane.get("role") == "reviewer"]
    integration_lanes = [lane for lane in route.get("lanes", []) if lane.get("role") == "integration"]
    required_final_ids = [lane["id"] for lane in (reviewer_lanes or integration_lanes)]
    if not required_final_ids:
        required_final_ids = [lane["id"] for lane in route.get("lanes", []) if lane.get("role") in {"implementation", "repair"}]

    all_required_settled = all(classification_by_lane.get(lane_id) == "settled" for lane_id in required_final_ids)
    any_invalid = any(item["classification"] in {"invalid", "failed"} for item in settled)
    any_blocked = any(item["classification"] in {"blocked", "partial"} for item in settled)
    any_pending = any(item["classification"] == "pending" for item in settled)

    if conflicts or unknown_results or any_invalid:
        overall = "INVALID_OR_FAILED"
    elif any_blocked:
        overall = "BLOCKED_OR_PARTIAL"
    elif all_required_settled:
        overall = "READY_FOR_ACCEPTANCE"
    elif barrier_status and barrier_status["ready"]:
        overall = "INTEGRATION_READY"
    elif any_pending:
        overall = "WAITING"
    else:
        overall = "WAITING"

    output = {
        "version": "codex-sol-luna-settlement-v1",
        "run_id": route.get("run_id"),
        "generation": route.get("generation"),
        "overall": overall,
        "route_warnings": route_warnings,
        "conflicts": conflicts,
        "unknown_results": unknown_results,
        "lanes": settled,
        "barrier": barrier_status,
    }

    rendered = json.dumps(output, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"WROTE: {args.output}")
    print(rendered)

    return 0 if overall in {"WAITING", "INTEGRATION_READY", "READY_FOR_ACCEPTANCE"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
