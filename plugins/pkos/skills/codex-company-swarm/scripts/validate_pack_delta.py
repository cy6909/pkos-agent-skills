#!/usr/bin/env python3
"""Validate Shared Collaboration Pack delta, invalidation, and acknowledgements."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set

EXPECTED_SCHEMA = "pkos-company-swarm/context-pack-delta-v1"
CHANGE_CLASSES = {"C0", "C1", "C2", "C3", "C4", "C5"}
ACK_MODES = {"DIRECT_VERIFIED", "BROKERED_SNAPSHOT"}
STATUS = {"OPEN", "SETTLED", "BLOCKED"}


def load_json(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError("file not found: %s" % path) from exc
    except json.JSONDecodeError as exc:
        raise ValueError("invalid JSON at line %s column %s: %s" % (exc.lineno, exc.colno, exc.msg)) from exc
    if not isinstance(data, dict):
        raise ValueError("pack delta must be an object")
    return data


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate(data: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if data.get("schema") != EXPECTED_SCHEMA:
        errors.append("schema must be %s" % EXPECTED_SCHEMA)
    for field in ("run_id", "from_revision", "to_revision", "created_by", "created_at", "reason", "source_manifest_hash"):
        if not nonempty(data.get(field)):
            errors.append("%s must be non-empty" % field)
    if data.get("from_revision") == data.get("to_revision"):
        errors.append("from_revision and to_revision must differ")
    if data.get("status") not in STATUS:
        errors.append("status is invalid")
    if data.get("mandatory_reload") is not True:
        errors.append("mandatory_reload must be true for a durable pack delta")
    if not isinstance(data.get("requires_new_generation"), bool):
        errors.append("requires_new_generation must be boolean")

    changes = data.get("source_changes")
    high_impact = False
    if not isinstance(changes, list) or not changes:
        errors.append("source_changes must be a non-empty array")
        changes = []
    node_ids: Set[str] = set()
    for index, change in enumerate(changes):
        label = "source_changes[%d]" % index
        if not isinstance(change, dict):
            errors.append("%s must be an object" % label)
            continue
        for field in ("node_id", "previous_revision", "new_revision", "summary"):
            if not nonempty(change.get(field)):
                errors.append("%s.%s must be non-empty" % (label, field))
        if change.get("previous_revision") == change.get("new_revision"):
            errors.append("%s previous/new revision must differ" % label)
        node_id = change.get("node_id")
        if nonempty(node_id):
            if node_id in node_ids:
                errors.append("duplicate changed node %s" % node_id)
            node_ids.add(node_id)
        change_class = change.get("change_class")
        if change_class not in CHANGE_CLASSES:
            errors.append("%s.change_class is invalid" % label)
        if change_class in {"C2", "C3", "C4", "C5"}:
            high_impact = True
    if high_impact and data.get("requires_new_generation") is not True and data.get("compatibility_preserved") is not True:
        errors.append("C2+ pack changes require a new generation or compatibility_preserved=true")

    def unique_list(field: str) -> Set[str]:
        raw = data.get(field)
        if not isinstance(raw, list):
            errors.append("%s must be an array" % field)
            return set()
        result: Set[str] = set()
        for index, item in enumerate(raw):
            if not nonempty(item):
                errors.append("%s[%d] must be non-empty" % (field, index))
            elif item in result:
                errors.append("%s contains duplicate %s" % (field, item))
            else:
                result.add(item)
        return result

    affected_sessions = unique_list("affected_sessions")
    unique_list("affected_lanes")
    invalidated = unique_list("invalidated_artifacts")
    if not affected_sessions:
        errors.append("affected_sessions must not be empty")
    if high_impact and not invalidated:
        errors.append("C2+ pack changes require invalidated_artifacts")

    acknowledgements = data.get("acknowledgements")
    if not isinstance(acknowledgements, list):
        errors.append("acknowledgements must be an array")
        acknowledgements = []
    acked: Set[str] = set()
    for index, ack in enumerate(acknowledgements):
        label = "acknowledgements[%d]" % index
        if not isinstance(ack, dict):
            errors.append("%s must be an object" % label)
            continue
        sid = ack.get("session_id")
        if not nonempty(sid):
            errors.append("%s.session_id must be non-empty" % label)
            continue
        if sid in acked:
            errors.append("duplicate acknowledgement for %s" % sid)
        acked.add(sid)
        if sid not in affected_sessions:
            errors.append("%s acknowledges a session not affected by the delta" % label)
        if ack.get("revision") != data.get("to_revision"):
            errors.append("%s must acknowledge to_revision" % label)
        if ack.get("status") != "ACKNOWLEDGED":
            errors.append("%s.status must be ACKNOWLEDGED" % label)
        mode = ack.get("mode")
        if mode not in ACK_MODES:
            errors.append("%s.mode is invalid" % label)
        if mode == "DIRECT_VERIFIED" and not ack.get("verified_source_refs"):
            errors.append("%s direct verification requires verified_source_refs" % label)
        if mode == "BROKERED_SNAPSHOT" and not nonempty(ack.get("snapshot_hash")):
            errors.append("%s brokered snapshot requires snapshot_hash" % label)
    if data.get("status") == "SETTLED":
        missing = affected_sessions - acked
        if missing:
            errors.append("SETTLED delta missing acknowledgements: %s" % ", ".join(sorted(missing)))
    return errors


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("delta", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        data = load_json(args.delta)
    except ValueError as exc:
        print("Pack-delta validation failed:", file=sys.stderr)
        print("- %s" % exc, file=sys.stderr)
        return 1
    errors = validate(data)
    if errors:
        print("Pack-delta validation failed:", file=sys.stderr)
        for error in errors:
            print("- %s" % error, file=sys.stderr)
        return 1
    print("Pack-delta validation OK: %s -> %s, %s." % (data.get("from_revision"), data.get("to_revision"), data.get("status")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
