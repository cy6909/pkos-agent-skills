#!/usr/bin/env python3
"""Validate a complete Company Swarm Notion coordination bundle and cross-file invariants."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Dict, Iterable, List

SCRIPT_ROOT = Path(__file__).resolve().parent
REQUIRED = {
    "coordination-state.json": "validate_coordination.py",
    "event-ledger.json": "validate_event_ledger.py",
    "notion-schema.json": "validate_notion_schema.py",
    "notion-sync.json": "validate_notion_sync.py",
    "pack-delta.json": "validate_pack_delta.py",
    "traceability.json": "validate_traceability.py",
    "checkpoint.json": "validate_checkpoint.py",
}


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load %s" % path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_bundle(directory: Path) -> List[str]:
    errors: List[str] = []
    documents: Dict[str, dict] = {}
    modules: Dict[str, ModuleType] = {}
    for filename, validator_name in REQUIRED.items():
        path = directory / filename
        if not path.is_file():
            errors.append("missing bundle file: %s" % filename)
            continue
        module = load_module("bundle_%s" % validator_name.replace(".py", ""), SCRIPT_ROOT / validator_name)
        modules[filename] = module
        try:
            data = module.load_json(path)
            documents[filename] = data
            if filename != "checkpoint.json":
                errors.extend("%s: %s" % (filename, item) for item in module.validate(data))
        except Exception as exc:
            errors.append("%s raised: %s" % (filename, exc))

    if "checkpoint.json" in documents:
        ledger = documents.get("event-ledger.json")
        errors.extend("checkpoint.json: %s" % item for item in modules["checkpoint.json"].validate(documents["checkpoint.json"], ledger))
    if errors:
        return errors

    state = documents["coordination-state.json"]
    ledger = documents["event-ledger.json"]
    sync = documents["notion-sync.json"]
    delta = documents["pack-delta.json"]
    trace = documents["traceability.json"]
    checkpoint = documents["checkpoint.json"]
    notion_schema = documents["notion-schema.json"]

    run_ids = {state.get("run_id"), ledger.get("run_id"), sync.get("run_id"), delta.get("run_id"), trace.get("run_id"), checkpoint.get("run_id")}
    if len(run_ids) != 1:
        errors.append("bundle run_id mismatch: %s" % sorted(str(value) for value in run_ids))
    if len({state.get("project_id"), notion_schema.get("project_id"), checkpoint.get("project_id")}) != 1:
        errors.append("bundle project_id mismatch")
    if state.get("last_event_seq") != ledger.get("last_event_seq"):
        errors.append("coordination state and event ledger last_event_seq mismatch")
    if state.get("state_version") != ledger.get("state_version"):
        errors.append("coordination state and event ledger state_version mismatch")
    if state.get("director", {}).get("epoch") != ledger.get("current_director_epoch"):
        errors.append("coordination state and event ledger director epoch mismatch")
    if state.get("generation") != ledger.get("current_generation") or state.get("generation") != trace.get("generation"):
        errors.append("bundle generation mismatch")
    if state.get("shared_pack", {}).get("revision") != delta.get("to_revision"):
        errors.append("coordination state does not use the latest pack delta revision")
    if checkpoint.get("shared_pack_revision") != state.get("shared_pack", {}).get("revision"):
        errors.append("checkpoint pack revision mismatch")
    if checkpoint.get("director_epoch") != state.get("director", {}).get("epoch"):
        errors.append("checkpoint director epoch mismatch")
    if checkpoint.get("event_seq") != state.get("last_event_seq"):
        errors.append("checkpoint is not at the latest projected event")
    if sync.get("watermark_event_seq") != state.get("notion", {}).get("last_synced_event_seq"):
        errors.append("Notion sync watermark mismatch")
    if state.get("notion", {}).get("schema_state") != notion_schema.get("schema_state"):
        errors.append("Notion schema state mismatch")
    candidate = state.get("active_candidate") if isinstance(state.get("active_candidate"), dict) else {}
    if candidate.get("commit") != trace.get("candidate_commit"):
        errors.append("coordination candidate and traceability candidate mismatch")
    if checkpoint.get("active_candidate", {}).get("commit") != trace.get("candidate_commit"):
        errors.append("checkpoint candidate and traceability candidate mismatch")
    if state.get("run_state") == "ACCEPTED":
        if trace.get("completion_target") != "ACCEPTED":
            errors.append("accepted state requires ACCEPTED traceability target")
        if sync.get("sync_status") != "IN_SYNC":
            errors.append("accepted state requires in-sync Notion bundle")
        if notion_schema.get("schema_state") != "READY":
            errors.append("accepted state requires ready Notion schema")
        if checkpoint.get("pending_outbox_event_ids"):
            errors.append("accepted state cannot retain pending checkpoint outbox entries")
    return errors


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        errors = validate_bundle(args.directory)
    except Exception as exc:
        print("Coordination-bundle validation failed:", file=sys.stderr)
        print("- %s" % exc, file=sys.stderr)
        return 1
    if errors:
        print("Coordination-bundle validation failed:", file=sys.stderr)
        for error in errors:
            print("- %s" % error, file=sys.stderr)
        return 1
    print("Coordination-bundle validation OK: %s" % args.directory)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
