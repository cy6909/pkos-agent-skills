#!/usr/bin/env python3
"""Validate a PKOS Company Swarm organization manifest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

EXPECTED_SCHEMA = "pkos-company-swarm/org-v1"
EXPECTED_MODE = "rapid-agile-sol-max"
EXPECTED_MODEL = "gpt-5.6-sol"
EXPECTED_EFFORT = "max"
REQUIRED_GATES = ["G0", "G1", "G2", "G3", "G4", "G5"]
WRITER_ROLES = {
    "domain-developer",
    "quality-engineer",
    "ci-engineer",
    "security-performance-engineer",
    "integration-owner",
    "governance-scribe",
}


def load_json(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError("file not found: %s" % path) from exc
    except json.JSONDecodeError as exc:
        raise ValueError("invalid JSON at line %s column %s: %s" % (exc.lineno, exc.colno, exc.msg)) from exc
    if not isinstance(data, dict):
        raise ValueError("organization manifest must be a JSON object")
    return data


def path_prefix(pattern: str) -> str:
    text = pattern.strip().replace("\\", "/")
    if not text or text.startswith("<"):
        return ""
    cut = len(text)
    for token in ("*", "?", "["):
        pos = text.find(token)
        if pos >= 0:
            cut = min(cut, pos)
    return text[:cut].rstrip("/")


def scopes_overlap(left: str, right: str) -> bool:
    a = path_prefix(left)
    b = path_prefix(right)
    if not a or not b:
        return False
    return a == b or a.startswith(b + "/") or b.startswith(a + "/")


def validate(data: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    if data.get("schema") != EXPECTED_SCHEMA:
        errors.append("schema must be %s" % EXPECTED_SCHEMA)
    if data.get("mode") != EXPECTED_MODE:
        errors.append("mode must be %s" % EXPECTED_MODE)
    if not isinstance(data.get("run_id"), str) or not data.get("run_id"):
        errors.append("run_id must be a non-empty string")
    if not isinstance(data.get("generation"), int) or data.get("generation", 0) < 1:
        errors.append("generation must be an integer >= 1")

    root_id = data.get("root_session_id")
    if root_id != "TD-01":
        errors.append("root_session_id must be TD-01")
    if data.get("spawn_authority") != ["TD-01"]:
        errors.append("spawn_authority must contain only TD-01")

    configured_ceiling = data.get("configured_concurrency_ceiling")
    observed_ceiling = data.get("observed_runtime_ceiling")
    if not isinstance(configured_ceiling, int) or configured_ceiling < 1:
        errors.append("configured_concurrency_ceiling must be an integer >= 1")
    if observed_ceiling is not None and (not isinstance(observed_ceiling, int) or observed_ceiling < 1):
        errors.append("observed_runtime_ceiling must be null or an integer >= 1")

    sessions = data.get("sessions")
    if not isinstance(sessions, list) or not sessions:
        return errors + ["sessions must be a non-empty array"]

    by_id: Dict[str, Dict[str, Any]] = {}
    role_counts: Dict[str, int] = {}
    for index, raw in enumerate(sessions):
        if not isinstance(raw, dict):
            errors.append("sessions[%d] must be an object" % index)
            continue
        sid = raw.get("session_id")
        if not isinstance(sid, str) or not sid:
            errors.append("sessions[%d].session_id must be non-empty" % index)
            continue
        if sid in by_id:
            errors.append("duplicate session_id: %s" % sid)
            continue
        by_id[sid] = raw
        role = raw.get("role")
        if not isinstance(role, str) or not role:
            errors.append("%s role must be non-empty" % sid)
        else:
            role_counts[role] = role_counts.get(role, 0) + 1

        if raw.get("model") != EXPECTED_MODEL:
            errors.append("%s model must be %s" % (sid, EXPECTED_MODEL))
        if raw.get("reasoning_effort") != EXPECTED_EFFORT:
            errors.append("%s reasoning_effort must be max" % sid)

        if sid == root_id:
            if raw.get("role") != "technical-director":
                errors.append("TD-01 must have role technical-director")
            if raw.get("parent_session_id") is not None or raw.get("managed_by") is not None:
                errors.append("TD-01 must have no parent or manager")
            if raw.get("may_delegate") is not True:
                errors.append("TD-01 must be the only delegating session")
        else:
            if raw.get("parent_session_id") != root_id or raw.get("managed_by") != root_id:
                errors.append("%s must be parented and managed by TD-01" % sid)
            if raw.get("may_delegate") is not False:
                errors.append("%s must set may_delegate=false" % sid)

        scope = raw.get("write_scope", [])
        if not isinstance(scope, list) or any(not isinstance(item, str) for item in scope):
            errors.append("%s write_scope must be an array of strings" % sid)
        if raw.get("role") in WRITER_ROLES and raw.get("role") != "integration-owner":
            if not scope:
                errors.append("writer %s must have a non-empty write_scope" % sid)
        if raw.get("role") == "domain-developer" and raw.get("test_acceptance") is not False:
            errors.append("developer %s must set test_acceptance=false" % sid)
        if raw.get("role") == "quality-engineer" and raw.get("test_acceptance") is not True:
            errors.append("quality engineer %s must set test_acceptance=true" % sid)

    if role_counts.get("technical-director") != 1:
        errors.append("exactly one technical-director is required")
    if role_counts.get("review-chair") != 1:
        errors.append("exactly one review-chair is required")
    if role_counts.get("integration-owner") != 1:
        errors.append("exactly one integration-owner is required")

    for sid, session in by_id.items():
        role = session.get("role")
        if role not in {"domain-developer", "quality-engineer"}:
            continue
        pair_id = session.get("paired_session_id")
        if not isinstance(pair_id, str) or pair_id not in by_id:
            errors.append("%s must reference an existing paired_session_id" % sid)
            continue
        pair = by_id[pair_id]
        expected_role = "quality-engineer" if role == "domain-developer" else "domain-developer"
        if pair.get("role") != expected_role:
            errors.append("%s must pair with role %s" % (sid, expected_role))
        if pair.get("paired_session_id") != sid:
            errors.append("pairing must be reciprocal: %s <-> %s" % (sid, pair_id))
        if pair.get("domain") != session.get("domain"):
            errors.append("paired sessions %s and %s must share a domain" % (sid, pair_id))

    lanes = data.get("lanes")
    if not isinstance(lanes, list):
        errors.append("lanes must be an array")
        lanes = []
    lane_ids = set()
    paired_developers = set()
    paired_testers = set()
    for index, lane in enumerate(lanes):
        if not isinstance(lane, dict):
            errors.append("lanes[%d] must be an object" % index)
            continue
        lane_id = lane.get("lane_id")
        if not isinstance(lane_id, str) or not lane_id:
            errors.append("lanes[%d].lane_id must be non-empty" % index)
            continue
        if lane_id in lane_ids:
            errors.append("duplicate lane_id: %s" % lane_id)
        lane_ids.add(lane_id)
        dev_id = lane.get("developer_session_id")
        test_id = lane.get("tester_session_id")
        dev = by_id.get(dev_id)
        tester = by_id.get(test_id)
        if not dev or dev.get("role") != "domain-developer":
            errors.append("lane %s developer_session_id is invalid" % lane_id)
        if not tester or tester.get("role") != "quality-engineer":
            errors.append("lane %s tester_session_id is invalid" % lane_id)
        if dev and tester:
            if dev.get("paired_session_id") != test_id or tester.get("paired_session_id") != dev_id:
                errors.append("lane %s pair does not match session records" % lane_id)
            if dev.get("domain") != lane_id or tester.get("domain") != lane_id:
                errors.append("lane %s must match developer/tester domain" % lane_id)
        paired_developers.add(dev_id)
        paired_testers.add(test_id)

    all_developers = {sid for sid, item in by_id.items() if item.get("role") == "domain-developer"}
    all_testers = {sid for sid, item in by_id.items() if item.get("role") == "quality-engineer"}
    if paired_developers != all_developers:
        errors.append("every domain developer must appear in exactly one lane")
    if paired_testers != all_testers:
        errors.append("every quality engineer must appear in exactly one lane")

    writable: List[Tuple[str, str]] = []
    for sid, session in by_id.items():
        if session.get("role") not in WRITER_ROLES or session.get("role") == "integration-owner":
            continue
        for scope in session.get("write_scope", []):
            if path_prefix(scope):
                writable.append((sid, scope))
    for index, (sid_a, scope_a) in enumerate(writable):
        for sid_b, scope_b in writable[index + 1 :]:
            if sid_a != sid_b and scopes_overlap(scope_a, scope_b):
                errors.append("overlapping write scopes: %s:%s and %s:%s" % (sid_a, scope_a, sid_b, scope_b))

    gates = data.get("gates")
    if gates != REQUIRED_GATES:
        errors.append("gates must be exactly %s" % REQUIRED_GATES)

    pipeline = data.get("pipeline")
    if not isinstance(pipeline, dict):
        errors.append("pipeline must be an object")
    else:
        state = pipeline.get("capability_state")
        if state not in {"EXISTS_VALID", "EXISTS_GAPPED", "MISSING", "BLOCKED"}:
            errors.append("pipeline.capability_state is invalid")
        if pipeline.get("authoritative_testing") is not True:
            errors.append("pipeline.authoritative_testing must be true")
        if state in {"EXISTS_GAPPED", "MISSING", "BLOCKED"} and role_counts.get("ci-engineer", 0) < 1:
            errors.append("a ci-engineer is required when the pipeline is not EXISTS_VALID")

    return errors


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        data = load_json(args.manifest)
    except ValueError as exc:
        print("Company Swarm organization validation failed:", file=sys.stderr)
        print("- %s" % exc, file=sys.stderr)
        return 1

    errors = validate(data)
    if errors:
        print("Company Swarm organization validation failed:", file=sys.stderr)
        for error in errors:
            print("- %s" % error, file=sys.stderr)
        return 1

    print("Company Swarm organization validation OK: %d sessions, %d lanes." % (len(data["sessions"]), len(data.get("lanes", []))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
