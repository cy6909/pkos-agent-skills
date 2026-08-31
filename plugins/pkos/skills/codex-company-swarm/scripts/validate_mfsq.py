#!/usr/bin/env python3
"""Validate a PKOS MFSQ v2 test design and executable case plan."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set

EXPECTED_SCHEMA = "pkos-mfsq/v2"
AXES = {"M", "F", "S", "Q"}
VALID_STATUSES = {"planned", "implemented", "passed", "failed", "blocked", "skipped"}
VALID_LAYERS = {"frontend", "backend", "android", "ios", "ai_data", "ops", "shared"}
VALID_SIDES = VALID_LAYERS | {"cross_end"}
VALID_CASE_TYPES = {
    "unit", "component", "contract", "integration", "e2e", "security",
    "performance", "migration", "static", "manual_acceptance",
}
DEPENDENCY_CASE_TYPES = {"contract", "integration", "e2e"}
USER_ACCEPTANCE_CASE_TYPES = {"e2e", "manual_acceptance"}
SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


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


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_list(value: Any, label: str, errors: List[str], require: bool = True) -> List[str]:
    if not isinstance(value, list) or any(not nonempty(item) for item in value):
        errors.append("%s must be an array of non-empty strings" % label)
        return []
    if require and not value:
        errors.append("%s must not be empty" % label)
    if len(value) != len(set(value)):
        errors.append("%s contains duplicates" % label)
    return value


def approved_exclusion(exclusion: Dict[str, Any]) -> bool:
    return (
        nonempty(exclusion.get("reason"))
        and isinstance(exclusion.get("approved_by"), str)
        and exclusion["approved_by"].startswith("RB-")
        and nonempty(exclusion.get("approval_artifact"))
    )


def validate_test_design(data: Any, errors: List[str]) -> None:
    if not isinstance(data, dict):
        errors.append("test_design must be an object")
        return
    for field in ("design_id", "visual_ref", "text_ref"):
        if not nonempty(data.get(field)):
            errors.append("test_design.%s must be a non-empty string" % field)
    if not isinstance(data.get("version"), int) or data.get("version", 0) < 1:
        errors.append("test_design.version must be an integer >= 1")
    if not isinstance(data.get("checksum"), str) or not SHA256_RE.match(data.get("checksum", "")):
        errors.append("test_design.checksum must be sha256:<64 lowercase hex>")
    if data.get("review_status") != "APPROVED":
        errors.append("test_design.review_status must be APPROVED before G1 can pass")
    reviewers = string_list(data.get("reviewers"), "test_design.reviewers", errors)
    if reviewers and not any(item.startswith(("TM-", "RB-")) for item in reviewers):
        errors.append("test_design.reviewers must include TM-* or RB-*")


def validate_material_gate(data: Any, errors: List[str]) -> None:
    if not isinstance(data, dict):
        errors.append("material_gate must be an object")
        return
    if not nonempty(data.get("gate_id")):
        errors.append("material_gate.gate_id must be a non-empty string")
    if data.get("status") not in VALID_STATUSES:
        errors.append("material_gate.status is invalid")
    checks = data.get("checks")
    if not isinstance(checks, list) or not checks:
        errors.append("material_gate.checks must be a non-empty array")
        return
    seen: Set[str] = set()
    for index, check in enumerate(checks):
        label = "material_gate.checks[%d]" % index
        if not isinstance(check, dict):
            errors.append("%s must be an object" % label)
            continue
        for field in ("check_id", "title", "procedure", "expected", "automation_path", "pipeline_stage"):
            if not nonempty(check.get(field)):
                errors.append("%s.%s must be a non-empty string" % (label, field))
        check_id = check.get("check_id")
        if nonempty(check_id):
            if check_id in seen:
                errors.append("duplicate material check_id: %s" % check_id)
            seen.add(check_id)
        if check.get("status") not in VALID_STATUSES:
            errors.append("%s.status is invalid" % label)
        if str(check.get("automation_path", "")).strip().lower() in {"manual", "n/a", "none"}:
            errors.append("%s must map to a version-controlled automation_path" % label)
        if str(check.get("pipeline_stage", "")).strip().lower() in {"local", "manual", "n/a", "none"}:
            errors.append("%s must map to an authoritative pipeline_stage" % label)


def validate(data: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if data.get("schema") != EXPECTED_SCHEMA:
        errors.append("schema must be %s; v1 is historical evidence only" % EXPECTED_SCHEMA)
    for field in ("run_id", "lane_id", "developer_session_id", "tester_session_id", "canonical_environment", "pipeline_provider"):
        if not nonempty(data.get(field)):
            errors.append("%s must be a non-empty string" % field)
    if not isinstance(data.get("generation"), int) or data.get("generation", 0) < 1:
        errors.append("generation must be an integer >= 1")
    if not isinstance(data.get("behavior_changing"), bool):
        errors.append("behavior_changing must be boolean")

    requirement_ids = set(string_list(data.get("requirement_ids"), "requirement_ids", errors))
    feature_ids = set(string_list(data.get("feature_ids"), "feature_ids", errors))
    acceptance_ids = set(string_list(data.get("acceptance_ids"), "acceptance_ids", errors))
    validate_test_design(data.get("test_design"), errors)
    validate_material_gate(data.get("material_gate"), errors)

    units = data.get("implementation_units")
    if not isinstance(units, list) or not units:
        errors.append("implementation_units must be a non-empty array")
        units = []
    unit_map: Dict[str, Dict[str, Any]] = {}
    for index, unit in enumerate(units):
        label = "implementation_units[%d]" % index
        if not isinstance(unit, dict):
            errors.append("%s must be an object" % label)
            continue
        unit_id = unit.get("unit_id")
        if not nonempty(unit_id):
            errors.append("%s.unit_id must be a non-empty string" % label)
            continue
        if unit_id in unit_map:
            errors.append("duplicate implementation unit_id: %s" % unit_id)
        unit_map[unit_id] = unit
        if unit.get("layer") not in VALID_LAYERS:
            errors.append("%s.layer is invalid" % label)
        if not nonempty(unit.get("title")):
            errors.append("%s.title must be a non-empty string" % label)
        for field, allowed in (("requirement_ids", requirement_ids), ("feature_ids", feature_ids), ("acceptance_ids", acceptance_ids)):
            refs = string_list(unit.get(field), "%s.%s" % (label, field), errors)
            for ref in refs:
                if ref not in allowed:
                    errors.append("%s.%s references unknown ID %s" % (label, field, ref))
        for field in ("user_facing", "state_changing"):
            if not isinstance(unit.get(field), bool):
                errors.append("%s.%s must be boolean" % (label, field))

    dependencies = data.get("dependencies", [])
    if not isinstance(dependencies, list):
        errors.append("dependencies must be an array")
        dependencies = []
    dependency_map: Dict[str, Dict[str, Any]] = {}
    for index, dependency in enumerate(dependencies):
        label = "dependencies[%d]" % index
        if not isinstance(dependency, dict):
            errors.append("%s must be an object" % label)
            continue
        dep_id = dependency.get("dependency_id")
        if not nonempty(dep_id):
            errors.append("%s.dependency_id must be a non-empty string" % label)
            continue
        if dep_id in dependency_map:
            errors.append("duplicate dependency_id: %s" % dep_id)
        dependency_map[dep_id] = dependency
        consumer = dependency.get("consumer_unit_id")
        provider = dependency.get("provider_unit_id")
        if consumer not in unit_map:
            errors.append("%s.consumer_unit_id references unknown unit" % label)
        if provider not in unit_map:
            errors.append("%s.provider_unit_id references unknown unit" % label)
        if nonempty(consumer) and consumer == provider:
            errors.append("%s cannot depend on itself" % label)
        if not nonempty(dependency.get("contract_ref")):
            errors.append("%s.contract_ref must be a non-empty string" % label)
        if not isinstance(dependency.get("required"), bool):
            errors.append("%s.required must be boolean" % label)

    exclusions = data.get("exclusions", [])
    if not isinstance(exclusions, list):
        errors.append("exclusions must be an array")
        exclusions = []
    excluded_axes: Set[str] = set()
    excluded_targets: Set[tuple[str, str]] = set()
    security_excluded = False
    performance_excluded = False
    for index, exclusion in enumerate(exclusions):
        label = "exclusions[%d]" % index
        if not isinstance(exclusion, dict):
            errors.append("%s must be an object" % label)
            continue
        if not approved_exclusion(exclusion):
            errors.append("%s requires reason, RB-* approved_by, and approval_artifact" % label)
            continue
        scope = exclusion.get("scope")
        if scope == "axis":
            axis = exclusion.get("axis")
            if axis not in AXES:
                errors.append("%s.axis must be one of M, F, S, Q" % label)
                continue
            excluded_axes.add(axis)
            security_excluded = security_excluded or axis == "S"
            performance_excluded = performance_excluded or (axis == "Q" and str(exclusion.get("quality_attribute", "")).lower() == "performance")
        elif scope in {"acceptance", "implementation_unit", "dependency", "user_acceptance"}:
            target_id = exclusion.get("target_id")
            if not nonempty(target_id):
                errors.append("%s.target_id must be a non-empty string" % label)
            else:
                excluded_targets.add((scope, target_id))
        else:
            errors.append("%s.scope is invalid" % label)

    cases = data.get("cases")
    if not isinstance(cases, list):
        return errors + ["cases must be an array"]
    case_ids: Set[str] = set()
    covered_axes: Set[str] = set()
    covered_acceptances: Set[str] = set()
    covered_units: Set[str] = set()
    dependency_case_units: List[Set[str]] = []
    user_acceptance_units: Set[str] = set()
    security_present = False
    performance_present = False

    for index, case in enumerate(cases):
        label = "cases[%d]" % index
        if not isinstance(case, dict):
            errors.append("%s must be an object" % label)
            continue
        for field in ("case_id", "title", "risk", "rationale", "automation_path", "pipeline_stage", "owner_session_id"):
            if not nonempty(case.get(field)):
                errors.append("%s.%s must be a non-empty string" % (label, field))
        case_id = case.get("case_id")
        if nonempty(case_id):
            if case_id in case_ids:
                errors.append("duplicate case_id: %s" % case_id)
            case_ids.add(case_id)
        axis = case.get("axis")
        if axis not in AXES:
            errors.append("%s.axis must be one of M, F, S, Q" % label)
        else:
            covered_axes.add(axis)
            security_present = security_present or axis == "S"
            performance_present = performance_present or (axis == "Q" and str(case.get("quality_attribute", "")).lower() == "performance")
        secondary_axes = string_list(case.get("secondary_axes", []), "%s.secondary_axes" % label, errors, require=False)
        if any(item not in AXES for item in secondary_axes):
            errors.append("%s.secondary_axes may contain only M, F, S, Q" % label)
        case_type = case.get("case_type")
        if case_type not in VALID_CASE_TYPES:
            errors.append("%s.case_type is invalid" % label)
        if case.get("side") not in VALID_SIDES:
            errors.append("%s.side is invalid" % label)
        for field, allowed in (
            ("requirement_ids", requirement_ids), ("feature_ids", feature_ids),
            ("acceptance_ids", acceptance_ids), ("implementation_unit_ids", set(unit_map)),
        ):
            refs = string_list(case.get(field), "%s.%s" % (label, field), errors)
            for ref in refs:
                if ref not in allowed:
                    errors.append("%s.%s references unknown ID %s" % (label, field, ref))
            if field == "acceptance_ids":
                covered_acceptances.update(refs)
            if field == "implementation_unit_ids":
                covered_units.update(refs)
                if case_type in DEPENDENCY_CASE_TYPES:
                    dependency_case_units.append(set(refs))
                if case_type in USER_ACCEPTANCE_CASE_TYPES:
                    user_acceptance_units.update(refs)
        preconditions = case.get("preconditions")
        if not isinstance(preconditions, list) or any(not nonempty(item) for item in preconditions):
            errors.append("%s.preconditions must be an array of non-empty strings" % label)
        steps = case.get("steps")
        if not isinstance(steps, list) or not steps:
            errors.append("%s.steps must be a non-empty array" % label)
        else:
            step_ids: Set[str] = set()
            for step_index, step in enumerate(steps):
                step_label = "%s.steps[%d]" % (label, step_index)
                if not isinstance(step, dict):
                    errors.append("%s must be an object" % step_label)
                    continue
                for field in ("step_id", "action", "expected"):
                    if not nonempty(step.get(field)):
                        errors.append("%s.%s must be a non-empty string" % (step_label, field))
                step_id = step.get("step_id")
                if nonempty(step_id):
                    if step_id in step_ids:
                        errors.append("%s has duplicate step_id %s" % (label, step_id))
                    step_ids.add(step_id)
        code_refs = case.get("code_refs", [])
        if not isinstance(code_refs, list):
            errors.append("%s.code_refs must be an array" % label)
            code_refs = []
        for ref_index, code_ref in enumerate(code_refs):
            ref_label = "%s.code_refs[%d]" % (label, ref_index)
            if not isinstance(code_ref, dict):
                errors.append("%s must be an object" % ref_label)
                continue
            for field in ("path", "symbol", "purpose"):
                if not nonempty(code_ref.get(field)):
                    errors.append("%s.%s must be a non-empty string" % (ref_label, field))
        if case_type == "unit":
            if not nonempty(case.get("test_symbol")):
                errors.append("%s unit case requires test_symbol" % label)
            if not code_refs:
                errors.append("%s unit case requires code_refs describing tested code and purpose" % label)
        if case.get("status") not in VALID_STATUSES:
            errors.append("%s.status is invalid" % label)
        if str(case.get("automation_path", "")).strip().lower() in {"manual", "n/a", "none"}:
            errors.append("%s must map to a version-controlled automation_path" % label)
        if str(case.get("pipeline_stage", "")).strip().lower() in {"local", "manual", "n/a", "none"}:
            errors.append("%s must map to an authoritative pipeline_stage" % label)

    missing_axes = AXES - covered_axes - excluded_axes
    if missing_axes:
        errors.append("missing MFSQ disposition for axes: %s" % ", ".join(sorted(missing_axes)))
    if data.get("behavior_changing") is True:
        if not security_present and not security_excluded:
            errors.append("behavior-changing work requires an S case or RB-approved S exclusion")
        if not performance_present and not performance_excluded:
            errors.append("behavior-changing work requires a Q/performance case or RB-approved performance exclusion")
    for acceptance_id in acceptance_ids - covered_acceptances:
        if ("acceptance", acceptance_id) not in excluded_targets:
            errors.append("acceptance %s has no executable test case or approved exclusion" % acceptance_id)
    for unit_id in set(unit_map) - covered_units:
        if ("implementation_unit", unit_id) not in excluded_targets:
            errors.append("implementation unit %s has no executable test case or approved exclusion" % unit_id)
    for dep_id, dependency in dependency_map.items():
        pair = {dependency.get("consumer_unit_id"), dependency.get("provider_unit_id")}
        if not any(pair.issubset(case_units) for case_units in dependency_case_units):
            if ("dependency", dep_id) not in excluded_targets:
                errors.append("dependency %s lacks a contract, integration, or E2E case covering both units" % dep_id)
    for unit_id, unit in unit_map.items():
        if unit.get("user_facing") is True and unit_id not in user_acceptance_units:
            if ("user_acceptance", unit_id) not in excluded_targets:
                errors.append("user-facing implementation unit %s lacks E2E/manual acceptance coverage" % unit_id)
    if data.get("review_status") != "APPROVED":
        errors.append("review_status must be APPROVED before G1 can pass")
    reviewers = string_list(data.get("reviewers"), "reviewers", errors)
    if reviewers and not any(item.startswith(("TM-", "RB-")) for item in reviewers):
        errors.append("reviewers must include TM-* or RB-*")
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
    print("MFSQ v2 validation OK: %d cases, %d implementation units, %d dependencies." % (len(data.get("cases", [])), len(data.get("implementation_units", [])), len(data.get("dependencies", []))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
