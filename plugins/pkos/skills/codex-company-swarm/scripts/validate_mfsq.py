#!/usr/bin/env python3
"""Validate a PKOS MFSQ test plan."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set

EXPECTED_SCHEMA = "pkos-mfsq/v1"
AXES = {"M", "F", "S", "Q"}
VALID_STATUSES = {"planned", "implemented", "passed", "failed", "blocked", "skipped"}


def load_json(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError("file not found: %s" % path) from exc
    except json.JSONDecodeError as exc:
        raise ValueError("invalid JSON at line %s column %s: %s" % (exc.lineno, exc.colno, exc.msg)) from exc
    if not isinstance(data, dict):
        raise ValueError("MFSQ plan must be a JSON object")
    return data


def approved_exclusion(exclusion: Dict[str, Any]) -> bool:
    approver = exclusion.get("approved_by")
    reason = exclusion.get("reason")
    return isinstance(approver, str) and approver.startswith("RB-") and isinstance(reason, str) and bool(reason.strip())


def validate(data: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if data.get("schema") != EXPECTED_SCHEMA:
        errors.append("schema must be %s" % EXPECTED_SCHEMA)
    for field in ("run_id", "lane_id", "feature_id", "developer_session_id", "tester_session_id", "canonical_environment", "pipeline_provider"):
        if not isinstance(data.get(field), str) or not data.get(field):
            errors.append("%s must be a non-empty string" % field)
    if not isinstance(data.get("generation"), int) or data.get("generation", 0) < 1:
        errors.append("generation must be an integer >= 1")
    if not isinstance(data.get("behavior_changing"), bool):
        errors.append("behavior_changing must be boolean")

    cases = data.get("cases")
    if not isinstance(cases, list):
        return errors + ["cases must be an array"]
    exclusions = data.get("exclusions", [])
    if not isinstance(exclusions, list):
        errors.append("exclusions must be an array")
        exclusions = []

    case_ids: Set[str] = set()
    covered_axes: Set[str] = set()
    security_present = False
    performance_present = False

    required_case_fields = (
        "case_id",
        "axis",
        "title",
        "acceptance_ids",
        "risk",
        "procedure",
        "expected",
        "automation_path",
        "pipeline_stage",
        "owner_session_id",
        "status",
    )

    for index, case in enumerate(cases):
        label = "cases[%d]" % index
        if not isinstance(case, dict):
            errors.append("%s must be an object" % label)
            continue
        for field in required_case_fields:
            value = case.get(field)
            if field == "acceptance_ids":
                if not isinstance(value, list) or not value or any(not isinstance(item, str) or not item for item in value):
                    errors.append("%s.acceptance_ids must be a non-empty string array" % label)
            elif not isinstance(value, str) or not value.strip():
                errors.append("%s.%s must be a non-empty string" % (label, field))
        case_id = case.get("case_id")
        if isinstance(case_id, str):
            if case_id in case_ids:
                errors.append("duplicate case_id: %s" % case_id)
            case_ids.add(case_id)
        axis = case.get("axis")
        if axis not in AXES:
            errors.append("%s.axis must be one of M, F, S, Q" % label)
        else:
            covered_axes.add(axis)
            if axis == "S":
                security_present = True
            if axis == "Q" and str(case.get("quality_attribute", "")).lower() == "performance":
                performance_present = True
        if case.get("status") not in VALID_STATUSES:
            errors.append("%s.status is invalid" % label)
        if isinstance(case.get("automation_path"), str) and case.get("automation_path", "").strip().lower() in {"manual", "n/a", "none"}:
            errors.append("%s must map to a version-controlled automation_path" % label)
        if isinstance(case.get("pipeline_stage"), str) and case.get("pipeline_stage", "").strip().lower() in {"local", "manual", "n/a", "none"}:
            errors.append("%s must map to an authoritative pipeline_stage" % label)

    excluded_axes: Set[str] = set()
    security_excluded = False
    performance_excluded = False
    for index, exclusion in enumerate(exclusions):
        label = "exclusions[%d]" % index
        if not isinstance(exclusion, dict):
            errors.append("%s must be an object" % label)
            continue
        axis = exclusion.get("axis")
        if axis not in AXES:
            errors.append("%s.axis must be one of M, F, S, Q" % label)
            continue
        if not approved_exclusion(exclusion):
            errors.append("%s requires a reason and RB-* approved_by" % label)
            continue
        excluded_axes.add(axis)
        if axis == "S":
            security_excluded = True
        if axis == "Q" and str(exclusion.get("quality_attribute", "")).lower() == "performance":
            performance_excluded = True

    missing_axes = AXES - covered_axes - excluded_axes
    if missing_axes:
        errors.append("missing MFSQ disposition for axes: %s" % ", ".join(sorted(missing_axes)))

    if data.get("behavior_changing") is True:
        if not security_present and not security_excluded:
            errors.append("behavior-changing work requires an S case or RB-approved S exclusion")
        if not performance_present and not performance_excluded:
            errors.append("behavior-changing work requires a Q/performance case or RB-approved performance exclusion")

    if data.get("review_status") == "APPROVED":
        reviewers = data.get("reviewers")
        if not isinstance(reviewers, list) or not reviewers:
            errors.append("approved plans require at least one reviewer")

    return errors


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        data = load_json(args.plan)
    except ValueError as exc:
        print("MFSQ validation failed:", file=sys.stderr)
        print("- %s" % exc, file=sys.stderr)
        return 1

    errors = validate(data)
    if errors:
        print("MFSQ validation failed:", file=sys.stderr)
        for error in errors:
            print("- %s" % error, file=sys.stderr)
        return 1

    print("MFSQ validation OK: %d cases for feature %s." % (len(data.get("cases", [])), data.get("feature_id")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
