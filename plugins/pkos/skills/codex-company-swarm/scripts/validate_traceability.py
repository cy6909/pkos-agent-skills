#!/usr/bin/env python3
"""Validate end-to-end requirement-to-Notion traceability for Company Swarm."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set

EXPECTED_SCHEMA = "pkos-company-swarm/traceability-v1"
AXES = {"M", "F", "S", "Q"}
EVIDENCE_TYPES = {"REQUIREMENT", "DESIGN", "COMMIT", "DIFF", "TEST_PLAN", "TEST_REPORT", "CI_RUN", "SECURITY_REPORT", "PERFORMANCE_REPORT", "REVIEW_VERDICT", "NOTION_WRITE_RECEIPT", "ADR", "AUDIT", "INCIDENT", "DASHBOARD"}


def load_json(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError("file not found: %s" % path) from exc
    except json.JSONDecodeError as exc:
        raise ValueError("invalid JSON at line %s column %s: %s" % (exc.lineno, exc.colno, exc.msg)) from exc
    if not isinstance(data, dict):
        raise ValueError("traceability document must be an object")
    return data


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def object_map(items: Any, key: str, label: str, errors: List[str]) -> Dict[str, Dict[str, Any]]:
    if not isinstance(items, list):
        errors.append("%s must be an array" % label)
        return {}
    result: Dict[str, Dict[str, Any]] = {}
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append("%s[%d] must be an object" % (label, index))
            continue
        identifier = item.get(key)
        if not nonempty(identifier):
            errors.append("%s[%d].%s must be non-empty" % (label, index, key))
            continue
        if identifier in result:
            errors.append("duplicate %s %s" % (key, identifier))
        result[identifier] = item
    return result


def string_refs(item: Dict[str, Any], field: str, label: str, errors: List[str], require: bool = True) -> List[str]:
    values = item.get(field)
    if not isinstance(values, list) or any(not nonempty(value) for value in values):
        errors.append("%s.%s must be an array of non-empty strings" % (label, field))
        return []
    if require and not values:
        errors.append("%s.%s must not be empty" % (label, field))
    if len(values) != len(set(values)):
        errors.append("%s.%s contains duplicates" % (label, field))
    return values


def validate(data: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if data.get("schema") != EXPECTED_SCHEMA:
        errors.append("schema must be %s" % EXPECTED_SCHEMA)
    for field in ("run_id", "candidate_commit"):
        if not nonempty(data.get(field)):
            errors.append("%s must be non-empty" % field)
    if not isinstance(data.get("generation"), int) or data.get("generation", 0) < 1:
        errors.append("generation must be an integer >= 1")
    if data.get("completion_target") not in {"CHECKPOINT", "ACCEPTED"}:
        errors.append("completion_target is invalid")

    requirements = object_map(data.get("requirements"), "requirement_id", "requirements", errors)
    features = object_map(data.get("features"), "feature_id", "features", errors)
    acceptances = object_map(data.get("acceptances"), "acceptance_id", "acceptances", errors)
    test_cases = object_map(data.get("test_cases"), "case_id", "test_cases", errors)
    ci_runs = object_map(data.get("ci_runs"), "ci_run_id", "ci_runs", errors)
    verdicts = object_map(data.get("review_verdicts"), "verdict_id", "review_verdicts", errors)
    evidence = object_map(data.get("evidence"), "evidence_id", "evidence", errors)

    for evidence_id, item in evidence.items():
        if item.get("type") not in EVIDENCE_TYPES:
            errors.append("evidence %s has invalid type" % evidence_id)
        for field in ("uri", "checksum", "produced_by", "verified_by"):
            if not nonempty(item.get(field)):
                errors.append("evidence %s.%s must be non-empty" % (evidence_id, field))

    all_feature_refs: Set[str] = set()
    all_evidence_refs: Set[str] = set()
    for req_id, req in requirements.items():
        refs = string_refs(req, "feature_ids", "requirement %s" % req_id, errors)
        source_refs = string_refs(req, "source_refs", "requirement %s" % req_id, errors)
        for ref in source_refs:
            all_evidence_refs.add(ref)
            if ref not in evidence:
                errors.append("requirement %s references unknown evidence %s" % (req_id, ref))
        for ref in refs:
            all_feature_refs.add(ref)
            if ref not in features:
                errors.append("requirement %s references unknown feature %s" % (req_id, ref))

    all_acceptance_refs: Set[str] = set()
    all_test_refs: Set[str] = set()
    behavior_features: Set[str] = set()
    for feature_id, feature in features.items():
        if feature_id not in all_feature_refs:
            errors.append("feature %s is not mapped from any requirement" % feature_id)
        if feature.get("status") not in {"PLANNED", "IMPLEMENTED", "TESTED", "ACCEPTED", "DEFERRED", "BLOCKED"}:
            errors.append("feature %s has invalid status" % feature_id)
        if not nonempty(feature.get("lane_id")):
            errors.append("feature %s.lane_id must be non-empty" % feature_id)
        acceptance_ids = string_refs(feature, "acceptance_ids", "feature %s" % feature_id, errors)
        commits = string_refs(feature, "product_commits", "feature %s" % feature_id, errors)
        tests = string_refs(feature, "test_case_ids", "feature %s" % feature_id, errors)
        evidence_ids = string_refs(feature, "evidence_ids", "feature %s" % feature_id, errors)
        for ref in acceptance_ids:
            all_acceptance_refs.add(ref)
            if ref not in acceptances:
                errors.append("feature %s references unknown acceptance %s" % (feature_id, ref))
        for ref in tests:
            all_test_refs.add(ref)
            if ref not in test_cases:
                errors.append("feature %s references unknown test case %s" % (feature_id, ref))
        for ref in evidence_ids:
            all_evidence_refs.add(ref)
            if ref not in evidence:
                errors.append("feature %s references unknown evidence %s" % (feature_id, ref))
        if not commits:
            errors.append("feature %s requires a product commit" % feature_id)
        if feature.get("behavior_changing") is True:
            behavior_features.add(feature_id)
        durable = feature.get("durable_writeback")
        if durable not in {"REQUIRED", "NO_DURABLE_WRITEBACK"}:
            errors.append("feature %s durable_writeback is invalid" % feature_id)
        if durable == "REQUIRED" and not nonempty(feature.get("notion_owner_id")):
            errors.append("feature %s requires notion_owner_id" % feature_id)
        if durable == "NO_DURABLE_WRITEBACK" and not nonempty(feature.get("no_writeback_reason")):
            errors.append("feature %s requires no_writeback_reason" % feature_id)

    for acceptance_id, acceptance in acceptances.items():
        if acceptance_id not in all_acceptance_refs:
            errors.append("acceptance %s is not referenced by any feature" % acceptance_id)
        commits = string_refs(acceptance, "product_commits", "acceptance %s" % acceptance_id, errors)
        tests = string_refs(acceptance, "test_case_ids", "acceptance %s" % acceptance_id, errors)
        runs = string_refs(acceptance, "ci_run_ids", "acceptance %s" % acceptance_id, errors)
        reviews = string_refs(acceptance, "review_verdict_ids", "acceptance %s" % acceptance_id, errors)
        if not commits:
            errors.append("acceptance %s requires product_commits" % acceptance_id)
        for ref in tests:
            if ref not in test_cases:
                errors.append("acceptance %s references unknown test case %s" % (acceptance_id, ref))
        for ref in runs:
            if ref not in ci_runs:
                errors.append("acceptance %s references unknown CI run %s" % (acceptance_id, ref))
        for ref in reviews:
            if ref not in verdicts:
                errors.append("acceptance %s references unknown review verdict %s" % (acceptance_id, ref))

    feature_axes: Dict[str, Set[str]] = {feature_id: set() for feature_id in features}
    performance_features: Set[str] = set()
    for case_id, case in test_cases.items():
        if case_id not in all_test_refs:
            errors.append("test case %s is not referenced by any feature" % case_id)
        axis = case.get("axis")
        if axis not in AXES:
            errors.append("test case %s has invalid MFSQ axis" % case_id)
        feature_ids = string_refs(case, "feature_ids", "test case %s" % case_id, errors)
        for feature_id in feature_ids:
            if feature_id not in features:
                errors.append("test case %s references unknown feature %s" % (case_id, feature_id))
            elif axis in AXES and case_id in all_test_refs:
                feature_axes.setdefault(feature_id, set()).add(axis)
                if axis == "Q" and str(case.get("quality_attribute", "")).lower() == "performance":
                    performance_features.add(feature_id)
        for field in ("test_commit", "automation_path", "pipeline_stage"):
            if not nonempty(case.get(field)):
                errors.append("test case %s.%s must be non-empty" % (case_id, field))
        if str(case.get("pipeline_stage", "")).lower() in {"local", "manual", "none", "n/a"}:
            errors.append("test case %s must run in an authoritative pipeline stage" % case_id)
        runs = string_refs(case, "ci_run_ids", "test case %s" % case_id, errors)
        for run_id in runs:
            if run_id not in ci_runs:
                errors.append("test case %s references unknown CI run %s" % (case_id, run_id))
        status = case.get("status")
        if status not in {"PASSED", "FAILED", "BLOCKED", "N_A"}:
            errors.append("test case %s status is invalid" % case_id)
        if status == "N_A" and not nonempty(case.get("approved_by")):
            errors.append("test case %s N_A requires approved_by" % case_id)

    for feature_id in behavior_features:
        axes = feature_axes.get(feature_id, set())
        if "S" not in axes:
            errors.append("behavior-changing feature %s lacks Security/Safety traceability" % feature_id)
        if feature_id not in performance_features:
            errors.append("behavior-changing feature %s lacks performance traceability" % feature_id)

    candidate = data.get("candidate_commit")
    for run_id, run in ci_runs.items():
        if run.get("candidate_commit") != candidate:
            errors.append("CI run %s does not test the declared candidate" % run_id)
        if run.get("status") != "PASS":
            errors.append("CI run %s must PASS for traceability completion" % run_id)
        for evidence_id in string_refs(run, "report_evidence_ids", "CI run %s" % run_id, errors):
            if evidence_id not in evidence:
                errors.append("CI run %s references unknown evidence %s" % (run_id, evidence_id))

    accepted_verdict = False
    for verdict_id, verdict in verdicts.items():
        if verdict.get("candidate_commit") != candidate:
            errors.append("review verdict %s does not reference declared candidate" % verdict_id)
        if verdict.get("gate") == "G4" and verdict.get("verdict") == "ACCEPT":
            accepted_verdict = True
        for evidence_id in string_refs(verdict, "evidence_ids", "review verdict %s" % verdict_id, errors):
            if evidence_id not in evidence:
                errors.append("review verdict %s references unknown evidence %s" % (verdict_id, evidence_id))
    if data.get("completion_target") == "ACCEPTED" and not accepted_verdict:
        errors.append("ACCEPTED target requires a G4 ACCEPT verdict")

    findings = data.get("open_findings")
    if not isinstance(findings, list):
        errors.append("open_findings must be an array")
        findings = []
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            errors.append("open_findings[%d] must be an object" % index)
        elif finding.get("severity") in {"P0", "P1"} and finding.get("status") == "OPEN":
            errors.append("P0/P1 finding %s remains open" % finding.get("finding_id", index))

    writebacks = data.get("notion_writeback")
    if not isinstance(writebacks, list):
        errors.append("notion_writeback must be an array")
        writebacks = []
    writeback_by_feature: Dict[str, Dict[str, Any]] = {}
    for index, writeback in enumerate(writebacks):
        if not isinstance(writeback, dict):
            errors.append("notion_writeback[%d] must be an object" % index)
            continue
        feature_id = writeback.get("feature_id")
        if not nonempty(feature_id):
            errors.append("notion_writeback[%d].feature_id must be non-empty" % index)
            continue
        if feature_id in writeback_by_feature:
            errors.append("duplicate notion writeback for %s" % feature_id)
        writeback_by_feature[feature_id] = writeback
        status = writeback.get("status")
        if status not in {"CONFIRMED", "PENDING", "NO_DURABLE_WRITEBACK"}:
            errors.append("notion writeback %s status is invalid" % feature_id)
        if status == "CONFIRMED" and (not nonempty(writeback.get("owner_node_id")) or not nonempty(writeback.get("receipt_id"))):
            errors.append("confirmed notion writeback %s requires owner_node_id and receipt_id" % feature_id)
        wb_evidence = string_refs(writeback, "evidence_ids", "notion writeback %s" % feature_id, errors, require=(status == "CONFIRMED"))
        for evidence_id in wb_evidence:
            all_evidence_refs.add(evidence_id)
            if evidence_id not in evidence:
                errors.append("notion writeback %s references unknown evidence %s" % (feature_id, evidence_id))
        if status == "NO_DURABLE_WRITEBACK" and not nonempty(writeback.get("reason")):
            errors.append("no-writeback feature %s requires reason" % feature_id)
    for feature_id, feature in features.items():
        writeback = writeback_by_feature.get(feature_id)
        if writeback is None:
            errors.append("feature %s lacks notion_writeback disposition" % feature_id)
            continue
        if feature.get("durable_writeback") == "REQUIRED" and writeback.get("status") != "CONFIRMED" and data.get("completion_target") == "ACCEPTED":
            errors.append("accepted feature %s requires confirmed Notion writeback" % feature_id)
        if feature.get("durable_writeback") == "NO_DURABLE_WRITEBACK" and writeback.get("status") != "NO_DURABLE_WRITEBACK":
            errors.append("feature %s writeback disposition conflicts with feature contract" % feature_id)

    referenced_evidence = all_evidence_refs.copy()
    for run in ci_runs.values():
        referenced_evidence.update(run.get("report_evidence_ids", []))
    for verdict in verdicts.values():
        referenced_evidence.update(verdict.get("evidence_ids", []))
    unreferenced = set(evidence) - referenced_evidence
    if unreferenced:
        errors.append("unreferenced evidence records: %s" % ", ".join(sorted(unreferenced)))
    return errors


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("traceability", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        data = load_json(args.traceability)
    except ValueError as exc:
        print("Traceability validation failed:", file=sys.stderr)
        print("- %s" % exc, file=sys.stderr)
        return 1
    errors = validate(data)
    if errors:
        print("Traceability validation failed:", file=sys.stderr)
        for error in errors:
            print("- %s" % error, file=sys.stderr)
        return 1
    print("Traceability validation OK: %d requirements, %d features, candidate %s." % (len(data.get("requirements", [])), len(data.get("features", [])), data.get("candidate_commit")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
