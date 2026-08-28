#!/usr/bin/env python3
"""Validate a durable Company Swarm checkpoint and optional takeover record."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set

EXPECTED_SCHEMA = "pkos-company-swarm/checkpoint-v1"
GATES = {"G0", "G1", "G2", "G3", "G4", "G5"}
SHA256 = re.compile(r"^sha256:[0-9a-fA-F]{64}$")


def load_json(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError("file not found: %s" % path) from exc
    except json.JSONDecodeError as exc:
        raise ValueError("invalid JSON at line %s column %s: %s" % (exc.lineno, exc.colno, exc.msg)) from exc
    if not isinstance(data, dict):
        raise ValueError("checkpoint must be an object")
    return data


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate(data: Dict[str, Any], ledger: Dict[str, Any] | None = None) -> List[str]:
    errors: List[str] = []
    if data.get("schema") != EXPECTED_SCHEMA:
        errors.append("schema must be %s" % EXPECTED_SCHEMA)
    for field in ("project_id", "run_id", "checkpoint_id", "created_at", "director_runtime_id", "shared_pack_revision", "resume_token"):
        if not nonempty(data.get(field)):
            errors.append("%s must be non-empty" % field)
    for field in ("generation", "event_seq", "state_version", "director_epoch", "notion_sync_watermark"):
        value = data.get(field)
        if not isinstance(value, int) or value < 1:
            errors.append("%s must be an integer >= 1" % field)
    if data.get("state_version") != data.get("event_seq"):
        errors.append("state_version must equal event_seq")
    if data.get("notion_sync_watermark", 0) > data.get("event_seq", 0):
        errors.append("notion_sync_watermark cannot exceed event_seq")
    if data.get("current_gate") not in GATES:
        errors.append("current_gate is invalid")
    if data.get("previous_checkpoint_id") is not None and not nonempty(data.get("previous_checkpoint_id")):
        errors.append("previous_checkpoint_id must be null or non-empty")
    if not nonempty(data.get("notion_run_record_id")):
        errors.append("notion_run_record_id must be non-empty")

    artifacts = data.get("artifact_manifest")
    if not isinstance(artifacts, list) or not artifacts:
        errors.append("artifact_manifest must be a non-empty array")
        artifacts = []
    paths: Set[str] = set()
    required_count = 0
    for index, artifact in enumerate(artifacts):
        label = "artifact_manifest[%d]" % index
        if not isinstance(artifact, dict):
            errors.append("%s must be an object" % label)
            continue
        path = artifact.get("path")
        if not nonempty(path):
            errors.append("%s.path must be non-empty" % label)
        elif path in paths:
            errors.append("duplicate checkpoint artifact path %s" % path)
        else:
            paths.add(path)
        checksum = artifact.get("checksum")
        if not isinstance(checksum, str) or not SHA256.match(checksum):
            errors.append("%s.checksum must be sha256:<64 hex>" % label)
        if artifact.get("required_for_resume") is True:
            required_count += 1
    if required_count < 3:
        errors.append("checkpoint must retain at least three required resume artifacts")

    sessions = data.get("sessions")
    if not isinstance(sessions, list) or not sessions:
        errors.append("sessions must be a non-empty array")
        sessions = []
    session_ids: Set[str] = set()
    for index, session in enumerate(sessions):
        label = "sessions[%d]" % index
        if not isinstance(session, dict):
            errors.append("%s must be an object" % label)
            continue
        sid = session.get("session_id")
        if not nonempty(sid):
            errors.append("%s.session_id must be non-empty" % label)
            continue
        if sid in session_ids:
            errors.append("duplicate checkpoint session %s" % sid)
        session_ids.add(sid)
        if session.get("director_epoch") != data.get("director_epoch"):
            errors.append("checkpoint session %s has stale director_epoch" % sid)
        if session.get("pack_revision") != data.get("shared_pack_revision"):
            errors.append("checkpoint session %s has stale pack_revision" % sid)
        if not nonempty(session.get("state")):
            errors.append("checkpoint session %s state must be non-empty" % sid)
        if not nonempty(session.get("task_packet")):
            errors.append("checkpoint session %s task_packet must be non-empty" % sid)

    lanes = data.get("lanes")
    if not isinstance(lanes, list):
        errors.append("lanes must be an array")
        lanes = []
    lane_ids: Set[str] = set()
    for index, lane in enumerate(lanes):
        label = "lanes[%d]" % index
        if not isinstance(lane, dict):
            errors.append("%s must be an object" % label)
            continue
        lane_id = lane.get("lane_id")
        if not nonempty(lane_id):
            errors.append("%s.lane_id must be non-empty" % label)
        elif lane_id in lane_ids:
            errors.append("duplicate checkpoint lane %s" % lane_id)
        else:
            lane_ids.add(lane_id)
        if not nonempty(lane.get("state")):
            errors.append("%s.state must be non-empty" % label)
        if not isinstance(lane.get("feature_ids"), list) or not lane.get("feature_ids"):
            errors.append("%s.feature_ids must be non-empty" % label)

    pending = data.get("pending_outbox_event_ids")
    if not isinstance(pending, list) or any(not nonempty(item) for item in pending):
        errors.append("pending_outbox_event_ids must be an array of non-empty strings")
    elif len(pending) != len(set(pending)):
        errors.append("pending_outbox_event_ids contains duplicates")

    takeover = data.get("takeover")
    if takeover is not None:
        if not isinstance(takeover, dict):
            errors.append("takeover must be null or an object")
        else:
            old = takeover.get("previous_epoch")
            new = takeover.get("new_epoch")
            if not isinstance(old, int) or not isinstance(new, int) or new != old + 1:
                errors.append("takeover requires consecutive previous/new epoch")
            if new != data.get("director_epoch"):
                errors.append("takeover.new_epoch must match checkpoint director_epoch")
            for field in ("event_id", "requested_by", "authorized_by", "reason"):
                if not nonempty(takeover.get(field)):
                    errors.append("takeover.%s must be non-empty" % field)
            if not isinstance(takeover.get("stale_sessions_invalidated"), list):
                errors.append("takeover.stale_sessions_invalidated must be an array")

    if ledger is not None:
        if ledger.get("run_id") != data.get("run_id"):
            errors.append("checkpoint and ledger run_id mismatch")
        if data.get("event_seq", 0) > ledger.get("last_event_seq", 0):
            errors.append("checkpoint event_seq exceeds ledger")
        events = ledger.get("events")
        if isinstance(events, list) and 0 < data.get("event_seq", 0) <= len(events):
            event = events[data["event_seq"] - 1]
            if event.get("event_type") not in {"CHECKPOINT_CREATED", "RUN_ACCEPTED", "TAKEOVER"}:
                errors.append("checkpoint event_seq must land on a checkpoint/acceptance/takeover event")
            if event.get("director_epoch") != data.get("director_epoch"):
                errors.append("checkpoint director_epoch disagrees with ledger event")
        if ledger.get("current_generation") != data.get("generation"):
            errors.append("checkpoint generation disagrees with ledger")
    return errors


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("--ledger", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        checkpoint = load_json(args.checkpoint)
        ledger = load_json(args.ledger) if args.ledger else None
    except ValueError as exc:
        print("Checkpoint validation failed:", file=sys.stderr)
        print("- %s" % exc, file=sys.stderr)
        return 1
    errors = validate(checkpoint, ledger)
    if errors:
        print("Checkpoint validation failed:", file=sys.stderr)
        for error in errors:
            print("- %s" % error, file=sys.stderr)
        return 1
    print("Checkpoint validation OK: %s at event %s, epoch %s." % (checkpoint.get("checkpoint_id"), checkpoint.get("event_seq"), checkpoint.get("director_epoch")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
