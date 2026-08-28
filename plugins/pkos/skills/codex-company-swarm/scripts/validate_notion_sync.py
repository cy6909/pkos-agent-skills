#!/usr/bin/env python3
"""Validate the Company Swarm Notion outbox, receipts, and sync watermark."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set

EXPECTED_SCHEMA = "pkos-company-swarm/notion-sync-v1"
MODES = {"DIRECT_WRITABLE", "DIRECT_READ_ONLY", "BROKERED", "UNAVAILABLE"}
TARGETS = {"SWARM_REGISTRY", "EVENT_LEDGER", "EVIDENCE_REGISTRY", "FEATURE_REGISTRY", "CURRENT_TRUTH", "AUDIT", "ADR", "INCIDENT", "MEMORY"}
OPERATIONS = {"CREATE", "UPDATE", "APPEND", "SUPERSEDE"}
OUTBOX_STATES = {"PENDING", "CONFIRMED", "FAILED", "DEAD_LETTER"}


def load_json(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError("file not found: %s" % path) from exc
    except json.JSONDecodeError as exc:
        raise ValueError("invalid JSON at line %s column %s: %s" % (exc.lineno, exc.colno, exc.msg)) from exc
    if not isinstance(data, dict):
        raise ValueError("Notion sync file must be an object")
    return data


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate(data: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if data.get("schema") != EXPECTED_SCHEMA:
        errors.append("schema must be %s" % EXPECTED_SCHEMA)
    if not nonempty(data.get("run_id")):
        errors.append("run_id must be non-empty")
    if data.get("mode") not in MODES:
        errors.append("mode is invalid")
    if data.get("schema_state") not in {"READY", "PROPOSED", "BLOCKED"}:
        errors.append("schema_state is invalid")

    bindings = data.get("bindings")
    if not isinstance(bindings, dict):
        errors.append("bindings must be an object")
        bindings = {}
    required_bindings = {"swarm_registry", "event_decision_ledger", "evidence_registry", "feature_registry"}
    if data.get("mode") == "DIRECT_WRITABLE" and data.get("schema_state") == "READY":
        for key in sorted(required_bindings):
            if not nonempty(bindings.get(key)):
                errors.append("writable ready mode requires binding %s" % key)

    outbox = data.get("outbox")
    if not isinstance(outbox, list):
        return errors + ["outbox must be an array"]
    receipts = data.get("receipts")
    if not isinstance(receipts, list):
        errors.append("receipts must be an array")
        receipts = []

    receipt_by_id: Dict[str, Dict[str, Any]] = {}
    receipt_by_event: Dict[str, Dict[str, Any]] = {}
    for index, receipt in enumerate(receipts):
        label = "receipts[%d]" % index
        if not isinstance(receipt, dict):
            errors.append("%s must be an object" % label)
            continue
        rid = receipt.get("receipt_id")
        event_id = receipt.get("event_id")
        if not nonempty(rid) or not nonempty(event_id):
            errors.append("%s requires receipt_id and event_id" % label)
            continue
        if rid in receipt_by_id:
            errors.append("duplicate receipt_id: %s" % rid)
        if event_id in receipt_by_event:
            errors.append("duplicate receipt for event: %s" % event_id)
        receipt_by_id[rid] = receipt
        receipt_by_event[event_id] = receipt
        if receipt.get("verified") is not True:
            errors.append("%s must set verified=true" % label)
        for field in ("idempotency_key", "target", "operation", "observed_id", "observed_revision", "verified_at"):
            if not nonempty(receipt.get(field)):
                errors.append("%s.%s must be non-empty" % (label, field))

    event_ids: Set[str] = set()
    keys: Set[str] = set()
    confirmed_seqs: Set[int] = set()
    dead_letter_ids: Set[str] = set()
    for index, item in enumerate(outbox):
        label = "outbox[%d]" % index
        if not isinstance(item, dict):
            errors.append("%s must be an object" % label)
            continue
        event_id = item.get("event_id")
        key = item.get("idempotency_key")
        seq = item.get("event_seq")
        if not nonempty(event_id):
            errors.append("%s.event_id must be non-empty" % label)
        elif event_id in event_ids:
            errors.append("duplicate outbox event_id: %s" % event_id)
        else:
            event_ids.add(event_id)
        if not nonempty(key):
            errors.append("%s.idempotency_key must be non-empty" % label)
        elif key in keys:
            errors.append("duplicate outbox idempotency_key: %s" % key)
        else:
            keys.add(key)
        if not isinstance(seq, int) or seq < 1:
            errors.append("%s.event_seq must be an integer >= 1" % label)
        if item.get("target") not in TARGETS:
            errors.append("%s.target is invalid" % label)
        if item.get("operation") not in OPERATIONS:
            errors.append("%s.operation is invalid" % label)
        if item.get("status") not in OUTBOX_STATES:
            errors.append("%s.status is invalid" % label)
        if not nonempty(item.get("payload_hash")):
            errors.append("%s.payload_hash must be non-empty" % label)
        attempts = item.get("attempts")
        if not isinstance(attempts, int) or attempts < 0:
            errors.append("%s.attempts must be an integer >= 0" % label)
        status = item.get("status")
        rid = item.get("receipt_id")
        receipt = receipt_by_event.get(event_id)
        if status == "CONFIRMED":
            if not nonempty(rid) or receipt is None:
                errors.append("%s confirmed item requires a receipt" % label)
            else:
                if receipt.get("receipt_id") != rid:
                    errors.append("%s receipt_id does not match receipt" % label)
                if receipt.get("idempotency_key") != key:
                    errors.append("%s receipt idempotency_key mismatch" % label)
                if receipt.get("target") != item.get("target") or receipt.get("operation") != item.get("operation"):
                    errors.append("%s receipt target/operation mismatch" % label)
            if isinstance(seq, int):
                confirmed_seqs.add(seq)
        else:
            if rid is not None:
                errors.append("%s non-confirmed item must not claim receipt_id" % label)
            if receipt is not None:
                errors.append("%s non-confirmed item unexpectedly has a receipt" % label)
        if status == "DEAD_LETTER" and nonempty(event_id):
            dead_letter_ids.add(event_id)

    orphan_receipts = set(receipt_by_event) - event_ids
    if orphan_receipts:
        errors.append("orphan receipts for events: %s" % ", ".join(sorted(orphan_receipts)))
    watermark = data.get("watermark_event_seq")
    if not isinstance(watermark, int) or watermark < 0:
        errors.append("watermark_event_seq must be an integer >= 0")
        watermark = -1
    highest_contiguous = 0
    while highest_contiguous + 1 in confirmed_seqs:
        highest_contiguous += 1
    if watermark != highest_contiguous:
        errors.append("watermark_event_seq must equal highest contiguous confirmed event sequence")
    actual_pending = sum(1 for item in outbox if isinstance(item, dict) and item.get("status") in {"PENDING", "FAILED"})
    if data.get("pending_count") != actual_pending:
        errors.append("pending_count does not match outbox")
    if data.get("dead_letter_count") != len(dead_letter_ids):
        errors.append("dead_letter_count does not match outbox")
    if data.get("mode") == "DIRECT_WRITABLE" and data.get("sync_status") == "IN_SYNC":
        if actual_pending or dead_letter_ids:
            errors.append("IN_SYNC cannot have pending or dead-letter items")
        if watermark != max([0] + [item.get("event_seq", 0) for item in outbox if isinstance(item, dict)]):
            errors.append("IN_SYNC watermark must cover the entire outbox")
    return errors


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sync_file", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        data = load_json(args.sync_file)
    except ValueError as exc:
        print("Notion-sync validation failed:", file=sys.stderr)
        print("- %s" % exc, file=sys.stderr)
        return 1
    errors = validate(data)
    if errors:
        print("Notion-sync validation failed:", file=sys.stderr)
        for error in errors:
            print("- %s" % error, file=sys.stderr)
        return 1
    print("Notion-sync validation OK: watermark %s, %d receipts." % (data.get("watermark_event_seq"), len(data.get("receipts", []))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
