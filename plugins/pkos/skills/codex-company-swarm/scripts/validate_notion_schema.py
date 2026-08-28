#!/usr/bin/env python3
"""Validate the minimal Notion Durable Coordination Plane schema contract."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set

EXPECTED_SCHEMA = "pkos-company-swarm/notion-schema-v1"
REQUIRED_DATABASES = {
    "swarm_registry": {"Record ID", "Record Type", "Project ID", "Run ID", "Generation", "Director Epoch", "State Version", "Parent Record", "Feature IDs", "Current Gate", "Current State", "Owner Session", "Paired Session", "Pack Revision", "Base Commit", "Head Commit", "Candidate Revision", "Blocked By", "Last Event", "Evidence", "Last Verified", "Resume Token", "Sync Status"},
    "event_decision_ledger": {"Event ID", "Sequence", "Idempotency Key", "Project ID", "Run ID", "Generation", "Director Epoch", "State Version", "Actor Session", "Event Type", "Gate", "Subject ID", "Previous State", "New State", "Summary", "Evidence", "Occurred At", "Verification", "Supersedes"},
    "evidence_registry": {"Evidence ID", "Type", "Project ID", "Run ID", "Generation", "Feature IDs", "Lane ID", "Candidate Commit", "Produced By", "Verified By", "URI", "Checksum", "Summary", "Created At", "Retention", "Status", "Supersedes"},
}
REQUIRED_FEATURE_EXTENSION = {"Current Run", "Current Lane", "Development Status", "Test Status", "CI Status", "Review Status", "Accepted Candidate", "Open Defects", "Evidence", "Last Event", "Last Verified"}
VALID_STATUS = {"BOUND", "PROPOSED", "BLOCKED"}


def load_json(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError("file not found: %s" % path) from exc
    except json.JSONDecodeError as exc:
        raise ValueError("invalid JSON at line %s column %s: %s" % (exc.lineno, exc.colno, exc.msg)) from exc
    if not isinstance(data, dict):
        raise ValueError("Notion schema contract must be an object")
    return data


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate(data: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if data.get("schema") != EXPECTED_SCHEMA:
        errors.append("schema must be %s" % EXPECTED_SCHEMA)
    for field in ("project_id", "control_plane_node_id", "contract_version"):
        if not nonempty(data.get(field)):
            errors.append("%s must be non-empty" % field)
    if data.get("schema_state") not in {"READY", "PROPOSED", "BLOCKED"}:
        errors.append("schema_state is invalid")
    databases = data.get("databases")
    if not isinstance(databases, list):
        return errors + ["databases must be an array"]
    by_name: Dict[str, Dict[str, Any]] = {}
    for index, database in enumerate(databases):
        label = "databases[%d]" % index
        if not isinstance(database, dict):
            errors.append("%s must be an object" % label)
            continue
        name = database.get("logical_name")
        if not nonempty(name):
            errors.append("%s.logical_name must be non-empty" % label)
            continue
        if name in by_name:
            errors.append("duplicate logical database %s" % name)
        by_name[name] = database
        if database.get("status") not in VALID_STATUS:
            errors.append("%s.status is invalid" % label)
        if database.get("status") == "BOUND" and (not nonempty(database.get("stable_id")) or not nonempty(database.get("database_id"))):
            errors.append("%s bound database requires stable_id and database_id" % label)
        if not isinstance(database.get("properties"), dict):
            errors.append("%s.properties must be an object" % label)
    missing = set(REQUIRED_DATABASES) - set(by_name)
    if missing:
        errors.append("missing required coordination databases: %s" % ", ".join(sorted(missing)))
    for name, required_props in REQUIRED_DATABASES.items():
        database = by_name.get(name)
        if not database:
            continue
        props = database.get("properties") if isinstance(database.get("properties"), dict) else {}
        missing_props = required_props - set(props)
        if missing_props:
            errors.append("%s missing properties: %s" % (name, ", ".join(sorted(missing_props))))

    extension = data.get("feature_registry_extension")
    if not isinstance(extension, dict):
        errors.append("feature_registry_extension must be an object")
        extension = {}
    if not nonempty(extension.get("database_pointer")):
        errors.append("feature_registry_extension.database_pointer must be non-empty")
    props = extension.get("properties")
    if not isinstance(props, dict):
        errors.append("feature_registry_extension.properties must be an object")
        props = {}
    missing_feature = REQUIRED_FEATURE_EXTENSION - set(props)
    if missing_feature:
        errors.append("feature registry extension missing properties: %s" % ", ".join(sorted(missing_feature)))

    if data.get("schema_state") == "READY":
        for name in REQUIRED_DATABASES:
            if by_name.get(name, {}).get("status") != "BOUND":
                errors.append("READY schema requires %s to be BOUND" % name)
        if extension.get("status") != "BOUND":
            errors.append("READY schema requires feature registry extension BOUND")
    return errors


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("schema_contract", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        data = load_json(args.schema_contract)
    except ValueError as exc:
        print("Notion-schema validation failed:", file=sys.stderr)
        print("- %s" % exc, file=sys.stderr)
        return 1
    errors = validate(data)
    if errors:
        print("Notion-schema validation failed:", file=sys.stderr)
        for error in errors:
            print("- %s" % error, file=sys.stderr)
        return 1
    print("Notion-schema validation OK: durable coordination plane is %s." % data.get("schema_state"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
