#!/usr/bin/env python3
"""Build a deterministic Company Swarm resume/takeover plan from a validated checkpoint."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List


def load_json(path: Path) -> Dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError("file not found: %s" % path) from exc
    except json.JSONDecodeError as exc:
        raise ValueError("invalid JSON at line %s column %s: %s" % (exc.lineno, exc.colno, exc.msg)) from exc
    if not isinstance(value, dict):
        raise ValueError("checkpoint must be an object")
    return value


def build(checkpoint: Dict[str, Any], takeover: bool = False) -> Dict[str, Any]:
    current_epoch = int(checkpoint.get("director_epoch", 0))
    target_epoch = current_epoch + 1 if takeover else current_epoch
    reusable: List[Dict[str, Any]] = []
    must_reissue: List[Dict[str, Any]] = []
    for session in checkpoint.get("sessions", []):
        if not isinstance(session, dict):
            continue
        record = {
            "session_id": session.get("session_id"),
            "state": session.get("state"),
            "task_packet": session.get("task_packet"),
            "required_pack_revision": checkpoint.get("shared_pack_revision"),
            "required_director_epoch": target_epoch,
        }
        if takeover or session.get("director_epoch") != target_epoch or session.get("pack_revision") != checkpoint.get("shared_pack_revision"):
            record["reason"] = "reissue packet under current director epoch and pack revision"
            must_reissue.append(record)
        elif session.get("state") in {"ACTIVE", "WAITING_ON_DEPENDENCY", "HANDED_OFF", "SETTLED"}:
            reusable.append(record)
        else:
            record["reason"] = "session state requires explicit Director decision"
            must_reissue.append(record)
    return {
        "schema": "pkos-company-swarm/resume-plan-v1",
        "run_id": checkpoint.get("run_id"),
        "project_id": checkpoint.get("project_id"),
        "checkpoint_id": checkpoint.get("checkpoint_id"),
        "resume_token": checkpoint.get("resume_token"),
        "current_gate": checkpoint.get("current_gate"),
        "generation": checkpoint.get("generation"),
        "previous_director_epoch": current_epoch,
        "target_director_epoch": target_epoch,
        "takeover_required": takeover,
        "shared_pack_revision": checkpoint.get("shared_pack_revision"),
        "notion_run_record_id": checkpoint.get("notion_run_record_id"),
        "sync_watermark": checkpoint.get("notion_sync_watermark"),
        "pending_outbox_event_ids": checkpoint.get("pending_outbox_event_ids", []),
        "active_candidate": checkpoint.get("active_candidate"),
        "reusable_sessions": reusable,
        "sessions_requiring_reissue": must_reissue,
        "lanes": checkpoint.get("lanes", []),
        "required_resume_artifacts": [
            item.get("path")
            for item in checkpoint.get("artifact_manifest", [])
            if isinstance(item, dict) and item.get("required_for_resume") is True
        ],
        "mandatory_actions": [
            "verify Notion run record and Event Ledger watermark",
            "verify every required artifact checksum",
            "flush or adjudicate pending outbox entries",
            "reject results carrying a stale director epoch or pack revision",
            "revalidate the frozen candidate and current gate before dispatch",
        ] + (["append a TAKEOVER event and verify the incremented director epoch before messaging children"] if takeover else []),
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("--takeover", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        plan = build(load_json(args.checkpoint), args.takeover)
    except (ValueError, TypeError) as exc:
        print("Resume-plan generation failed: %s" % exc, file=sys.stderr)
        return 1
    rendered = json.dumps(plan, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print("Wrote resume plan: %s" % args.output)
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
