#!/usr/bin/env python3
"""Validate a PKOS Company Swarm v0.5 organization manifest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set, Tuple

EXPECTED_SCHEMA = "pkos-company-swarm/org-v2"
EXPECTED_MODE = "rapid-agile-sol-max"
EXPECTED_MODEL = "gpt-5.6-sol"
REQUIRED_GATES = ["G0", "G1", "G2", "G3", "G4", "G5"]
ACTIVE = {"planned", "provisioned", "acknowledged", "active", "waiting_on_dependency", "handed_off", "settled", "idle", "blocked"}
REPO_WRITERS = {"domain-developer", "quality-engineer", "ci-engineer", "security-performance-engineer", "integration-owner"}
NOTION_MODES = {"DIRECT_WRITABLE", "BROKERED_WRITABLE", "READ_ONLY", "UNAVAILABLE"}


def load_json(path: Path) -> Dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError("file not found: %s" % path) from exc
    except json.JSONDecodeError as exc:
        raise ValueError("invalid JSON at line %s column %s: %s" % (exc.lineno, exc.colno, exc.msg)) from exc
    if not isinstance(value, dict):
        raise ValueError("organization manifest must be an object")
    return value


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def path_prefix(pattern: str) -> str:
    text = pattern.strip().replace("\\", "/")
    if not text or text.startswith("<"):
        return ""
    cut = min([pos for token in ("*", "?", "[") if (pos := text.find(token)) >= 0] or [len(text)])
    return text[:cut].rstrip("/")


def overlaps(left: str, right: str) -> bool:
    a, b = path_prefix(left), path_prefix(right)
    return bool(a and b and (a == b or a.startswith(b + "/") or b.startswith(a + "/")))


def validate(data: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if data.get("schema") != EXPECTED_SCHEMA:
        errors.append("schema must be %s" % EXPECTED_SCHEMA)
    if data.get("mode") != EXPECTED_MODE:
        errors.append("mode must be %s" % EXPECTED_MODE)
    if not nonempty(data.get("run_id")):
        errors.append("run_id must be non-empty")
    generation = data.get("generation")
    epoch = data.get("director_epoch")
    pack = data.get("shared_pack_revision")
    if not isinstance(generation, int) or generation < 1:
        errors.append("generation must be an integer >= 1")
    if not isinstance(epoch, int) or epoch < 1:
        errors.append("director_epoch must be an integer >= 1")
    if not nonempty(pack):
        errors.append("shared_pack_revision must be non-empty")
    if data.get("root_session_id") != "TD-01":
        errors.append("root_session_id must be TD-01")
    if data.get("spawn_authority") != ["TD-01"]:
        errors.append("spawn_authority must contain only TD-01")
    if not isinstance(data.get("configured_concurrency_ceiling"), int) or data.get("configured_concurrency_ceiling", 0) < 1:
        errors.append("configured_concurrency_ceiling must be >= 1")

    coordination = data.get("notion_coordination")
    if not isinstance(coordination, dict):
        errors.append("notion_coordination must be an object")
        coordination = {}
    if coordination.get("writer_session_id") != "PK-01":
        errors.append("notion_coordination.writer_session_id must be PK-01")
    if coordination.get("mode") not in NOTION_MODES:
        errors.append("notion_coordination.mode is invalid")
    if coordination.get("schema_state") not in {"READY", "PARTIAL", "MISSING", "UNVERIFIED"}:
        errors.append("notion_coordination.schema_state is invalid")
    for flag in ("event_ledger_required", "state_projection_required", "outbox_required", "checkpoint_required", "traceability_required"):
        if coordination.get(flag) is not True:
            errors.append("notion_coordination.%s must be true" % flag)
    if coordination.get("mode") in {"DIRECT_WRITABLE", "BROKERED_WRITABLE"}:
        if coordination.get("schema_state") != "READY":
            errors.append("writable coordination requires schema_state READY")
        if not nonempty(coordination.get("control_plane_node_id")):
            errors.append("writable coordination requires control_plane_node_id")

    sessions = data.get("sessions")
    if not isinstance(sessions, list) or not sessions:
        return errors + ["sessions must be a non-empty array"]
    by_id: Dict[str, Dict[str, Any]] = {}
    role_counts: Dict[str, int] = {}
    notion_writers: List[str] = []
    for index, session in enumerate(sessions):
        label = "sessions[%d]" % index
        if not isinstance(session, dict):
            errors.append("%s must be an object" % label)
            continue
        sid = session.get("session_id")
        if not nonempty(sid):
            errors.append("%s.session_id must be non-empty" % label)
            continue
        if sid in by_id:
            errors.append("duplicate session_id: %s" % sid)
            continue
        by_id[sid] = session
        role = session.get("role")
        role_counts[role] = role_counts.get(role, 0) + 1
        if session.get("model") != EXPECTED_MODEL:
            errors.append("%s model must be %s" % (sid, EXPECTED_MODEL))
        if session.get("reasoning_effort") != "max":
            errors.append("%s reasoning_effort must be max" % sid)
        if session.get("state") in ACTIVE:
            if session.get("director_epoch") != epoch:
                errors.append("%s must use the current director_epoch" % sid)
            if session.get("pack_revision") != pack:
                errors.append("%s must use the current shared_pack_revision" % sid)
        if session.get("notion_write") is True:
            notion_writers.append(sid)
        if sid == "TD-01":
            if role != "technical-director":
                errors.append("TD-01 must have role technical-director")
            if session.get("parent_session_id") is not None or session.get("managed_by") is not None:
                errors.append("TD-01 must have no parent or manager")
            if session.get("may_delegate") is not True:
                errors.append("TD-01 must be the only delegating session")
            if session.get("notion_write") is not False:
                errors.append("TD-01 must not write Notion directly")
        else:
            if session.get("parent_session_id") != "TD-01" or session.get("managed_by") != "TD-01":
                errors.append("%s must be parented and managed by TD-01" % sid)
            if session.get("may_delegate") is not False:
                errors.append("%s must set may_delegate=false" % sid)
        if sid == "PK-01":
            if role != "coordination-governance-scribe":
                errors.append("PK-01 must have role coordination-governance-scribe")
            if session.get("persistent") is not True:
                errors.append("PK-01 must be persistent")
            if session.get("notion_write") is not True:
                errors.append("PK-01 must be the sole Notion coordination writer")
        scope = session.get("write_scope", [])
        if not isinstance(scope, list) or any(not isinstance(item, str) for item in scope):
            errors.append("%s write_scope must be an array of strings" % sid)
        if role in REPO_WRITERS and role != "integration-owner" and not scope:
            errors.append("repository writer %s must have a non-empty write_scope" % sid)
        if role == "domain-developer" and session.get("test_acceptance") is not False:
            errors.append("developer %s must set test_acceptance=false" % sid)
        if role == "quality-engineer" and session.get("test_acceptance") is not True:
            errors.append("quality engineer %s must set test_acceptance=true" % sid)

    if role_counts.get("technical-director") != 1:
        errors.append("exactly one technical-director is required")
    if role_counts.get("coordination-governance-scribe") != 1:
        errors.append("exactly one coordination-governance-scribe is required")
    if role_counts.get("review-chair") != 1:
        errors.append("exactly one review-chair is required")
    if role_counts.get("integration-owner") != 1:
        errors.append("exactly one integration-owner is required")
    if notion_writers != ["PK-01"]:
        errors.append("PK-01 must be the only session with notion_write=true")

    for sid, session in by_id.items():
        role = session.get("role")
        if role not in {"domain-developer", "quality-engineer"}:
            continue
        pair_id = session.get("paired_session_id")
        pair = by_id.get(pair_id)
        expected = "quality-engineer" if role == "domain-developer" else "domain-developer"
        if pair is None:
            errors.append("%s must reference an existing paired_session_id" % sid)
        else:
            if pair.get("role") != expected:
                errors.append("%s must pair with role %s" % (sid, expected))
            if pair.get("paired_session_id") != sid:
                errors.append("pairing must be reciprocal: %s <-> %s" % (sid, pair_id))
            if pair.get("domain") != session.get("domain"):
                errors.append("paired sessions %s and %s must share a domain" % (sid, pair_id))

    lanes = data.get("lanes")
    if not isinstance(lanes, list):
        errors.append("lanes must be an array")
        lanes = []
    lane_ids: Set[str] = set()
    lane_devs: Set[str] = set()
    lane_tests: Set[str] = set()
    for index, lane in enumerate(lanes):
        if not isinstance(lane, dict):
            errors.append("lanes[%d] must be an object" % index)
            continue
        lane_id = lane.get("lane_id")
        if not nonempty(lane_id):
            errors.append("lanes[%d].lane_id must be non-empty" % index)
            continue
        if lane_id in lane_ids:
            errors.append("duplicate lane_id: %s" % lane_id)
        lane_ids.add(lane_id)
        if lane.get("director_epoch") != epoch or lane.get("pack_revision") != pack:
            errors.append("lane %s must use current director_epoch and shared_pack_revision" % lane_id)
        dev_id, test_id = lane.get("developer_session_id"), lane.get("tester_session_id")
        dev, tester = by_id.get(dev_id), by_id.get(test_id)
        if not dev or dev.get("role") != "domain-developer":
            errors.append("lane %s developer_session_id is invalid" % lane_id)
        if not tester or tester.get("role") != "quality-engineer":
            errors.append("lane %s tester_session_id is invalid" % lane_id)
        if dev and tester and (dev.get("paired_session_id") != test_id or tester.get("paired_session_id") != dev_id):
            errors.append("lane %s pair does not match session records" % lane_id)
        lane_devs.add(dev_id)
        lane_tests.add(test_id)
    if lane_devs != {sid for sid, item in by_id.items() if item.get("role") == "domain-developer"}:
        errors.append("every domain developer must appear in exactly one lane")
    if lane_tests != {sid for sid, item in by_id.items() if item.get("role") == "quality-engineer"}:
        errors.append("every quality engineer must appear in exactly one lane")

    writable: List[Tuple[str, str]] = []
    for sid, session in by_id.items():
        if session.get("role") not in REPO_WRITERS or session.get("role") == "integration-owner":
            continue
        for scope in session.get("write_scope", []):
            if path_prefix(scope):
                writable.append((sid, scope))
    for index, (sid_a, scope_a) in enumerate(writable):
        for sid_b, scope_b in writable[index + 1:]:
            if sid_a != sid_b and overlaps(scope_a, scope_b):
                errors.append("overlapping write scopes: %s:%s and %s:%s" % (sid_a, scope_a, sid_b, scope_b))

    if data.get("gates") != REQUIRED_GATES:
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
    print("Company Swarm organization validation OK: %d sessions, %d lanes, persistent PK-01 coordination." % (len(data["sessions"]), len(data.get("lanes", []))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
