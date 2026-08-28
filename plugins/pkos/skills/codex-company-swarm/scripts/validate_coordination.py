#!/usr/bin/env python3
"""Validate a Company Swarm durable coordination-state projection."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set

EXPECTED_SCHEMA = "pkos-company-swarm/coordination-state-v1"
GATES = {"G0", "G1", "G2", "G3", "G4", "G5"}
RUN_STATES = {"INITIALIZING", "PLANNING", "READY", "DEVELOPING", "TESTING", "INTEGRATING", "IN_REVIEW", "RETURNED_TO_LANES", "BLOCKED", "CHECKPOINT", "ACCEPTED"}
NOTION_MODES = {"DIRECT_WRITABLE", "DIRECT_READ_ONLY", "BROKERED", "UNAVAILABLE"}
SYNC_STATES = {"IN_SYNC", "PENDING", "DEGRADED", "FAILED"}
SCHEMA_STATES = {"READY", "PROPOSED", "BLOCKED"}
SESSION_STATES = {"PLANNED", "PROVISIONED", "ACKNOWLEDGED", "ACTIVE", "WAITING_ON_DEPENDENCY", "HANDED_OFF", "SETTLED", "COMPLETE", "BLOCKED", "SUPERSEDED", "RETIRED"}
ACTIVE_SESSION_STATES = {"PROVISIONED", "ACKNOWLEDGED", "ACTIVE", "WAITING_ON_DEPENDENCY", "HANDED_OFF", "SETTLED", "COMPLETE"}
LANE_STATES = {"PLANNED", "READY", "DEV_ACTIVE", "DEV_HANDOFF", "TEST_ACTIVE", "DEFECT_RETURN", "TEST_PASSED", "INTEGRATING", "IN_REVIEW", "ACCEPTED", "BLOCKED", "DEFERRED"}
FEATURE_STATES = {"PLANNED", "ANALYZED", "READY", "IN_DEVELOPMENT", "DEV_HANDOFF", "IN_TEST", "DEFECT_RETURN", "TEST_PASSED", "INTEGRATING", "IN_REVIEW", "ACCEPTED", "BLOCKED", "DEFERRED"}
ACK_MODES = {"DIRECT_VERIFIED", "BROKERED_SNAPSHOT"}


def load_json(path: Path) -> Dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError("file not found: %s" % path) from exc
    except json.JSONDecodeError as exc:
        raise ValueError("invalid JSON at line %s column %s: %s" % (exc.lineno, exc.colno, exc.msg)) from exc
    if not isinstance(value, dict):
        raise ValueError("coordination state must be a JSON object")
    return value


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def unique_strings(values: Any, label: str, errors: List[str]) -> Set[str]:
    if not isinstance(values, list):
        errors.append("%s must be an array" % label)
        return set()
    result: Set[str] = set()
    for index, value in enumerate(values):
        if not nonempty_string(value):
            errors.append("%s[%d] must be a non-empty string" % (label, index))
            continue
        if value in result:
            errors.append("%s contains duplicate value %s" % (label, value))
        result.add(value)
    return result


def validate(data: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if data.get("schema") != EXPECTED_SCHEMA:
        errors.append("schema must be %s" % EXPECTED_SCHEMA)
    for field in ("project_id", "run_id"):
        if not nonempty_string(data.get(field)):
            errors.append("%s must be a non-empty string" % field)
    for field in ("generation", "state_version", "last_event_seq"):
        value = data.get(field)
        if not isinstance(value, int) or value < 1:
            errors.append("%s must be an integer >= 1" % field)
    if data.get("state_version") != data.get("last_event_seq"):
        errors.append("state_version must equal last_event_seq for deterministic projection")
    if data.get("current_gate") not in GATES:
        errors.append("current_gate must be one of G0-G5")
    if data.get("run_state") not in RUN_STATES:
        errors.append("run_state is invalid")

    director = data.get("director")
    if not isinstance(director, dict):
        errors.append("director must be an object")
        director = {}
    if director.get("role_id") != "TD-01":
        errors.append("director.role_id must be TD-01")
    if not nonempty_string(director.get("runtime_session_id")):
        errors.append("director.runtime_session_id must be non-empty")
    epoch = director.get("epoch")
    if not isinstance(epoch, int) or epoch < 1:
        errors.append("director.epoch must be an integer >= 1")
        epoch = -1
    if director.get("identity_confidence") not in {"observed", "configured", "unverified"}:
        errors.append("director.identity_confidence is invalid")

    pack = data.get("shared_pack")
    if not isinstance(pack, dict):
        errors.append("shared_pack must be an object")
        pack = {}
    revision = pack.get("revision")
    if not nonempty_string(revision):
        errors.append("shared_pack.revision must be non-empty")
    if not nonempty_string(pack.get("source_manifest_hash")):
        errors.append("shared_pack.source_manifest_hash must be non-empty")
    mandatory = unique_strings(pack.get("mandatory_ack_sessions", []), "shared_pack.mandatory_ack_sessions", errors)
    acknowledgements = pack.get("acknowledgements", [])
    ack_by_session: Dict[str, Dict[str, Any]] = {}
    if not isinstance(acknowledgements, list):
        errors.append("shared_pack.acknowledgements must be an array")
        acknowledgements = []
    for index, ack in enumerate(acknowledgements):
        label = "shared_pack.acknowledgements[%d]" % index
        if not isinstance(ack, dict):
            errors.append("%s must be an object" % label)
            continue
        sid = ack.get("session_id")
        if not nonempty_string(sid):
            errors.append("%s.session_id must be non-empty" % label)
            continue
        if sid in ack_by_session:
            errors.append("duplicate pack acknowledgement for %s" % sid)
        ack_by_session[sid] = ack
        if ack.get("revision") != revision:
            errors.append("%s must acknowledge current pack revision" % label)
        if ack.get("status") != "ACKNOWLEDGED":
            errors.append("%s.status must be ACKNOWLEDGED" % label)
        mode = ack.get("mode")
        if mode not in ACK_MODES:
            errors.append("%s.mode is invalid" % label)
        if mode == "DIRECT_VERIFIED" and (not isinstance(ack.get("verified_source_refs"), list) or not ack.get("verified_source_refs")):
            errors.append("%s requires verified_source_refs" % label)
        if mode == "BROKERED_SNAPSHOT" and not nonempty_string(ack.get("snapshot_hash")):
            errors.append("%s requires snapshot_hash" % label)
    missing_acks = mandatory - set(ack_by_session)
    if missing_acks:
        errors.append("missing mandatory pack acknowledgements: %s" % ", ".join(sorted(missing_acks)))

    notion = data.get("notion")
    if not isinstance(notion, dict):
        errors.append("notion must be an object")
        notion = {}
    if notion.get("mode") not in NOTION_MODES:
        errors.append("notion.mode is invalid")
    if notion.get("sync_status") not in SYNC_STATES:
        errors.append("notion.sync_status is invalid")
    if notion.get("schema_state") not in SCHEMA_STATES:
        errors.append("notion.schema_state is invalid")
    synced_seq = notion.get("last_synced_event_seq")
    if not isinstance(synced_seq, int) or synced_seq < 0:
        errors.append("notion.last_synced_event_seq must be an integer >= 0")
        synced_seq = -1
    if isinstance(data.get("last_event_seq"), int) and synced_seq > data["last_event_seq"]:
        errors.append("notion.last_synced_event_seq cannot exceed last_event_seq")
    if notion.get("sync_status") == "IN_SYNC":
        if synced_seq != data.get("last_event_seq"):
            errors.append("IN_SYNC requires last_synced_event_seq == last_event_seq")
        if data.get("pending_outbox_count") != 0:
            errors.append("IN_SYNC requires pending_outbox_count == 0")
        if not nonempty_string(notion.get("last_write_receipt_id")):
            errors.append("IN_SYNC requires last_write_receipt_id")
    if notion.get("mode") == "DIRECT_WRITABLE" and notion.get("schema_state") == "READY" and not nonempty_string(notion.get("run_record_id")):
        errors.append("ready writable Notion mode requires run_record_id")

    checkpoint = data.get("checkpoint")
    if not isinstance(checkpoint, dict):
        errors.append("checkpoint must be an object")
        checkpoint = {}
    if not nonempty_string(checkpoint.get("checkpoint_id")):
        errors.append("checkpoint.checkpoint_id must be non-empty")
    for field in ("event_seq", "state_version"):
        value = checkpoint.get(field)
        if not isinstance(value, int) or value < 1:
            errors.append("checkpoint.%s must be an integer >= 1" % field)
    if checkpoint.get("event_seq", 0) > data.get("last_event_seq", 0):
        errors.append("checkpoint.event_seq cannot exceed last_event_seq")
    if checkpoint.get("state_version", 0) > data.get("state_version", 0):
        errors.append("checkpoint.state_version cannot exceed state_version")
    if checkpoint.get("director_epoch") != epoch:
        errors.append("checkpoint.director_epoch must match current director epoch")
    if checkpoint.get("shared_pack_revision") != revision:
        errors.append("checkpoint.shared_pack_revision must match current pack")
    if not nonempty_string(checkpoint.get("artifact_path")):
        errors.append("checkpoint.artifact_path must be non-empty")
    if not nonempty_string(checkpoint.get("checksum")):
        errors.append("checkpoint.checksum must be non-empty")

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
        if not nonempty_string(sid):
            errors.append("%s.session_id must be non-empty" % label)
            continue
        if sid in session_ids:
            errors.append("duplicate session_id: %s" % sid)
        session_ids.add(sid)
        if session.get("state") not in SESSION_STATES:
            errors.append("%s.state is invalid" % label)
        if session.get("generation") != data.get("generation") and session.get("state") not in {"SUPERSEDED", "RETIRED"}:
            errors.append("%s must use current generation or be superseded/retired" % label)
        if session.get("state") in ACTIVE_SESSION_STATES:
            if session.get("director_epoch") != epoch:
                errors.append("active session %s has stale director_epoch" % sid)
            if session.get("pack_revision") != revision:
                errors.append("active session %s has stale pack_revision" % sid)
        last_seq = session.get("last_event_seq")
        if not isinstance(last_seq, int) or last_seq < 0 or last_seq > data.get("last_event_seq", 0):
            errors.append("%s.last_event_seq is invalid" % label)
    if "TD-01" not in session_ids:
        errors.append("sessions must include logical TD-01")
    unknown_mandatory = mandatory - session_ids
    if unknown_mandatory:
        errors.append("mandatory acknowledgements reference unknown sessions: %s" % ", ".join(sorted(unknown_mandatory)))

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
        if not nonempty_string(lane_id):
            errors.append("%s.lane_id must be non-empty" % label)
            continue
        if lane_id in lane_ids:
            errors.append("duplicate lane_id: %s" % lane_id)
        lane_ids.add(lane_id)
        if lane.get("state") not in LANE_STATES:
            errors.append("%s.state is invalid" % label)
        for field in ("developer_session_id", "tester_session_id"):
            sid = lane.get(field)
            if not nonempty_string(sid) or sid not in session_ids:
                errors.append("%s.%s must reference an existing session" % (label, field))
        if not isinstance(lane.get("feature_ids"), list) or not lane.get("feature_ids"):
            errors.append("%s.feature_ids must be a non-empty array" % label)
        if lane.get("pack_revision") != revision:
            errors.append("%s.pack_revision must match current pack" % label)
        if lane.get("director_epoch") != epoch:
            errors.append("%s.director_epoch must match current epoch" % label)

    projections = data.get("feature_projection")
    if not isinstance(projections, list):
        errors.append("feature_projection must be an array")
        projections = []
    feature_ids_seen: Set[str] = set()
    for index, feature in enumerate(projections):
        label = "feature_projection[%d]" % index
        if not isinstance(feature, dict):
            errors.append("%s must be an object" % label)
            continue
        feature_id = feature.get("feature_id")
        if not nonempty_string(feature_id):
            errors.append("%s.feature_id must be non-empty" % label)
            continue
        if feature_id in feature_ids_seen:
            errors.append("duplicate projected feature_id: %s" % feature_id)
        feature_ids_seen.add(feature_id)
        if feature.get("lifecycle") not in FEATURE_STATES:
            errors.append("%s.lifecycle is invalid" % label)
        if feature.get("current_lane") not in lane_ids:
            errors.append("%s.current_lane must reference a lane" % label)
        if not isinstance(feature.get("evidence_ids"), list):
            errors.append("%s.evidence_ids must be an array" % label)
        last_seq = feature.get("last_event_seq")
        if not isinstance(last_seq, int) or last_seq < 1 or last_seq > data.get("last_event_seq", 0):
            errors.append("%s.last_event_seq is invalid" % label)

    if not isinstance(data.get("open_context_requests"), list):
        errors.append("open_context_requests must be an array")
    for field in ("pending_outbox_count", "dead_letter_count"):
        value = data.get(field)
        if not isinstance(value, int) or value < 0:
            errors.append("%s must be an integer >= 0" % field)
    if data.get("traceability_status") not in {"PASS", "FAIL", "PENDING"}:
        errors.append("traceability_status is invalid")

    if data.get("run_state") == "ACCEPTED":
        if data.get("current_gate") != "G5":
            errors.append("ACCEPTED requires current_gate G5")
        candidate = data.get("active_candidate")
        if not isinstance(candidate, dict) or candidate.get("status") != "ACCEPTED":
            errors.append("ACCEPTED requires an accepted active_candidate")
        if data.get("traceability_status") != "PASS":
            errors.append("ACCEPTED requires traceability_status PASS")
        if notion.get("mode") != "DIRECT_WRITABLE" or notion.get("sync_status") != "IN_SYNC":
            errors.append("ACCEPTED requires writable, in-sync Notion coordination")
        if data.get("pending_outbox_count") != 0 or data.get("dead_letter_count") != 0:
            errors.append("ACCEPTED requires no pending outbox or dead letters")
        if data.get("open_context_requests"):
            errors.append("ACCEPTED requires no open context requests")
        if checkpoint.get("event_seq") != data.get("last_event_seq"):
            errors.append("ACCEPTED requires checkpoint at the latest event")
    return errors


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        data = load_json(args.state)
    except ValueError as exc:
        print("Coordination-state validation failed:", file=sys.stderr)
        print("- %s" % exc, file=sys.stderr)
        return 1
    errors = validate(data)
    if errors:
        print("Coordination-state validation failed:", file=sys.stderr)
        for error in errors:
            print("- %s" % error, file=sys.stderr)
        return 1
    print("Coordination-state validation OK: run %s, version %s, epoch %s." % (data.get("run_id"), data.get("state_version"), data.get("director", {}).get("epoch")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
