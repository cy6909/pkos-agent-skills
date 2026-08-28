#!/usr/bin/env python3
"""Validate the append-only Company Swarm coordination event ledger."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set

EXPECTED_SCHEMA = "pkos-company-swarm/event-ledger-v1"
EVENT_TYPES = {"RUN_CREATED", "COORDINATION_SCHEMA_BOUND", "SESSION_PROVISIONED", "SESSION_ACKNOWLEDGED", "SESSION_BLOCKED", "SESSION_REPLACED", "LANE_STARTED", "LANE_STATE_CHANGED", "TASK_ASSIGNED", "CONTEXT_REQUESTED", "CONTEXT_SUPPLIED", "PACK_SUPERSEDED", "PACK_ACKNOWLEDGED", "FEATURE_PROJECTED", "DEV_HANDOFF", "TEST_PLAN_APPROVED", "DEFECT_OPENED", "DEFECT_CLOSED", "CI_STARTED", "CI_COMPLETED", "EVIDENCE_REGISTERED", "CANDIDATE_FROZEN", "GATE_VERDICT", "LANE_RETURNED", "CHECKPOINT_CREATED", "TAKEOVER", "PKOS_WRITEBACK_CONFIRMED", "RETROSPECTIVE_RECORDED", "RUN_ACCEPTED", "RUN_BLOCKED"}
SYNC_STATES = {"PENDING", "CONFIRMED", "FAILED", "READ_ONLY", "UNAVAILABLE"}
GATES = {"G0", "G1", "G2", "G3", "G4", "G5"}
EVIDENCE_REQUIRED = {"DEV_HANDOFF", "CI_COMPLETED", "CANDIDATE_FROZEN", "GATE_VERDICT", "CHECKPOINT_CREATED", "PKOS_WRITEBACK_CONFIRMED", "RUN_ACCEPTED"}
GENERATION_CHANGE_EVENTS = {"LANE_RETURNED", "GATE_VERDICT", "TAKEOVER"}


def load_json(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError("file not found: %s" % path) from exc
    except json.JSONDecodeError as exc:
        raise ValueError("invalid JSON at line %s column %s: %s" % (exc.lineno, exc.colno, exc.msg)) from exc
    if not isinstance(data, dict):
        raise ValueError("event ledger must be a JSON object")
    return data


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate(data: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if data.get("schema") != EXPECTED_SCHEMA:
        errors.append("schema must be %s" % EXPECTED_SCHEMA)
    run_id = data.get("run_id")
    if not nonempty(run_id):
        errors.append("run_id must be a non-empty string")
    events = data.get("events")
    if not isinstance(events, list) or not events:
        return errors + ["events must be a non-empty array"]

    ids: Set[str] = set()
    idempotency_keys: Set[str] = set()
    previous_epoch: int | None = None
    previous_generation: int | None = None
    parent_ids: Set[str] = set()

    for index, event in enumerate(events):
        label = "events[%d]" % index
        expected_seq = index + 1
        if not isinstance(event, dict):
            errors.append("%s must be an object" % label)
            continue
        seq = event.get("seq")
        if seq != expected_seq:
            errors.append("%s.seq must be contiguous and equal %d" % (label, expected_seq))
        if event.get("state_version") != seq:
            errors.append("%s.state_version must equal seq" % label)
        if event.get("run_id") != run_id:
            errors.append("%s.run_id must match ledger run_id" % label)
        event_id = event.get("event_id")
        if not nonempty(event_id):
            errors.append("%s.event_id must be non-empty" % label)
        elif event_id in ids:
            errors.append("duplicate event_id: %s" % event_id)
        else:
            ids.add(event_id)
        key = event.get("idempotency_key")
        if not nonempty(key):
            errors.append("%s.idempotency_key must be non-empty" % label)
        elif key in idempotency_keys:
            errors.append("duplicate idempotency_key: %s" % key)
        else:
            idempotency_keys.add(key)

        event_type = event.get("event_type")
        if event_type not in EVENT_TYPES:
            errors.append("%s.event_type is invalid" % label)
        for field in ("actor_session_id", "occurred_at", "subject_id", "summary"):
            if not nonempty(event.get(field)):
                errors.append("%s.%s must be non-empty" % (label, field))
        if isinstance(event.get("summary"), str) and len(event["summary"]) > 500:
            errors.append("%s.summary must not exceed 500 characters" % label)
        if event.get("gate") is not None and event.get("gate") not in GATES:
            errors.append("%s.gate is invalid" % label)

        generation = event.get("generation")
        if not isinstance(generation, int) or generation < 1:
            errors.append("%s.generation must be an integer >= 1" % label)
        elif previous_generation is not None:
            if generation < previous_generation:
                errors.append("%s.generation cannot decrease" % label)
            if generation > previous_generation:
                if generation != previous_generation + 1:
                    errors.append("%s.generation may increase only by one" % label)
                if event_type not in GENERATION_CHANGE_EVENTS:
                    errors.append("%s changes generation using an invalid event type" % label)
        if isinstance(generation, int):
            previous_generation = generation

        epoch = event.get("director_epoch")
        if not isinstance(epoch, int) or epoch < 1:
            errors.append("%s.director_epoch must be an integer >= 1" % label)
        elif previous_epoch is not None:
            if epoch < previous_epoch:
                errors.append("%s.director_epoch cannot decrease" % label)
            if epoch > previous_epoch:
                if epoch != previous_epoch + 1:
                    errors.append("%s.director_epoch may increase only by one" % label)
                if event_type != "TAKEOVER":
                    errors.append("%s changes director_epoch without TAKEOVER" % label)
        if isinstance(epoch, int):
            previous_epoch = epoch

        evidence = event.get("evidence_ids")
        if not isinstance(evidence, list) or any(not nonempty(item) for item in evidence):
            errors.append("%s.evidence_ids must be an array of non-empty strings" % label)
            evidence = []
        if event_type in EVIDENCE_REQUIRED and not evidence:
            errors.append("%s requires at least one evidence_id" % label)
        source_path = event.get("source_artifact_path")
        if source_path is not None and not nonempty(source_path):
            errors.append("%s.source_artifact_path must be null or non-empty" % label)
        if source_path is not None and not nonempty(event.get("source_artifact_hash")):
            errors.append("%s requires source_artifact_hash when source_artifact_path is set" % label)

        sync = event.get("notion_sync")
        if not isinstance(sync, dict):
            errors.append("%s.notion_sync must be an object" % label)
            sync = {}
        status = sync.get("status")
        if status not in SYNC_STATES:
            errors.append("%s.notion_sync.status is invalid" % label)
        if status == "CONFIRMED":
            if not nonempty(sync.get("receipt_id")) or not nonempty(sync.get("synced_at")):
                errors.append("%s confirmed sync requires receipt_id and synced_at" % label)
        elif sync.get("receipt_id") is not None:
            errors.append("%s non-confirmed sync must not claim receipt_id" % label)

        parent = event.get("parent_event_id")
        if parent is not None:
            if not nonempty(parent):
                errors.append("%s.parent_event_id must be null or non-empty" % label)
            elif parent not in parent_ids:
                errors.append("%s.parent_event_id must reference an earlier event" % label)
        supersedes = event.get("supersedes_event_id")
        if supersedes is not None and (not nonempty(supersedes) or supersedes not in parent_ids):
            errors.append("%s.supersedes_event_id must reference an earlier event" % label)
        if nonempty(event_id):
            parent_ids.add(event_id)

        payload = event.get("payload")
        if not isinstance(payload, dict):
            errors.append("%s.payload must be an object" % label)
            payload = {}
        if event_type == "PACK_SUPERSEDED":
            for field in ("from_revision", "to_revision"):
                if not nonempty(payload.get(field)):
                    errors.append("%s PACK_SUPERSEDED requires payload.%s" % (label, field))
            if payload.get("from_revision") == payload.get("to_revision"):
                errors.append("%s PACK_SUPERSEDED revisions must differ" % label)
            if not isinstance(payload.get("affected_sessions"), list) or not payload.get("affected_sessions"):
                errors.append("%s PACK_SUPERSEDED requires affected_sessions" % label)
            if payload.get("mandatory_reload") is not True:
                errors.append("%s PACK_SUPERSEDED must set mandatory_reload=true" % label)
        if event_type == "TAKEOVER":
            old = payload.get("previous_epoch")
            new = payload.get("new_epoch")
            if not isinstance(old, int) or not isinstance(new, int) or new != old + 1:
                errors.append("%s TAKEOVER requires consecutive previous/new epoch" % label)
            if new != epoch:
                errors.append("%s TAKEOVER new_epoch must equal event director_epoch" % label)
            if not nonempty(payload.get("authorized_by")):
                errors.append("%s TAKEOVER requires authorized_by" % label)
            if not isinstance(payload.get("stale_sessions_invalidated"), list):
                errors.append("%s TAKEOVER requires stale_sessions_invalidated array" % label)
        if event_type == "GATE_VERDICT":
            if payload.get("gate") not in GATES:
                errors.append("%s GATE_VERDICT requires valid payload.gate" % label)
            if payload.get("verdict") not in {"GO", "GO_WITH_ACTIONS", "REPLAN", "PASS", "ACCEPT", "RETURN_TO_LANE", "REPLAN_ORG", "BLOCKED_EXTERNAL_BOUNDARY"}:
                errors.append("%s GATE_VERDICT payload.verdict is invalid" % label)
        if event_type == "RUN_ACCEPTED" and status != "CONFIRMED":
            errors.append("RUN_ACCEPTED must be confirmed in Notion")

    if data.get("last_event_seq") != len(events):
        errors.append("last_event_seq must equal the number of events")
    if data.get("state_version") != len(events):
        errors.append("ledger state_version must equal the number of events")
    if data.get("current_director_epoch") != previous_epoch:
        errors.append("current_director_epoch must match the last event")
    if data.get("current_generation") != previous_generation:
        errors.append("current_generation must match the last event")
    return errors


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        data = load_json(args.ledger)
    except ValueError as exc:
        print("Event-ledger validation failed:", file=sys.stderr)
        print("- %s" % exc, file=sys.stderr)
        return 1
    errors = validate(data)
    if errors:
        print("Event-ledger validation failed:", file=sys.stderr)
        for error in errors:
            print("- %s" % error, file=sys.stderr)
        return 1
    print("Event-ledger validation OK: %d events, epoch %s." % (len(data["events"]), data.get("current_director_epoch")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
