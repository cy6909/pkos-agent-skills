#!/usr/bin/env python3
"""Validate a PKOS Company Swarm v0.7 visible-task organization manifest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set, Tuple

EXPECTED_SCHEMA = "pkos-company-swarm/org-v3"
EXPECTED_MODE = "director-routed-visible-tasks"
REQUIRED_GATES = ["G0", "G1", "G2", "G3", "G4", "G5"]
TASK_STATES = {"registered", "queued", "active", "attention", "settled", "archived"}
CURRENT_STATES = {"queued", "active", "attention"}
REPO_WRITERS = {"domain-developer", "quality-engineer", "ci-engineer", "security-performance-engineer", "integration-owner"}
SINGLETON_ROLES = {"technical-director": "TD-01", "coordination-governance-scribe": "PK-01", "review-chair": "RB-01", "integration-owner": "INT-01"}
SOL_DEFAULT_ROLES = {"technical-director", "review-chair", "requirements-architect", "domain-developer", "integration-owner", "security-performance-engineer"}
LUNA_DEFAULT_ROLES = {"quality-engineer", "ci-engineer", "verifier"}


def deep_merge(target: Dict[str, Any], patch: Dict[str, Any]) -> None:
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            deep_merge(target[key], value)
        else:
            target[key] = value


def load_json(path: Path) -> Dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("cannot load %s: %s" % (path, exc)) from exc
    if not isinstance(value, dict):
        raise ValueError("organization manifest must be an object")
    if nonempty(value.get("$extends")):
        base = load_json(path.parent / value["$extends"])
        remove_sessions = set(value.get("remove_sessions", []))
        remove_lanes = set(value.get("remove_lanes", []))
        base["sessions"] = [item for item in base.get("sessions", []) if item.get("session_id") not in remove_sessions]
        base["lanes"] = [item for item in base.get("lanes", []) if item.get("lane_id") not in remove_lanes]
        deep_merge(base, value.get("patch", {}))
        for session_id, session_patch in value.get("session_patches", {}).items():
            task = next((item for item in base.get("sessions", []) if item.get("session_id") == session_id), None)
            if task is None:
                raise ValueError("session patch target not found: %s" % session_id)
            deep_merge(task, session_patch)
        value = base
    return value


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def path_prefix(pattern: str) -> str:
    text = pattern.strip().replace("\\", "/")
    if not text or text.startswith("<"):
        return ""
    positions = [text.find(token) for token in ("*", "?", "[") if text.find(token) >= 0]
    return text[:min(positions or [len(text)])].rstrip("/")


def overlaps(left: str, right: str) -> bool:
    a, b = path_prefix(left), path_prefix(right)
    return bool(a and b and (a == b or a.startswith(b + "/") or b.startswith(a + "/")))


def validate_budget(data: Dict[str, Any], errors: List[str]) -> Dict[str, Any]:
    budget = data.get("staffing_budget")
    if not isinstance(budget, dict):
        errors.append("staffing_budget must be an object")
        return {}
    fields = ("default_max_product_lanes", "max_product_lanes", "default_target_active_child_tasks", "target_active_child_tasks", "min_productive_concurrency", "max_active_child_tasks", "hard_cap_active_child_tasks", "max_registered_visible_tasks_per_run", "underfill_alert_seconds")
    for field in fields:
        if not isinstance(budget.get(field), int) or budget.get(field, 0) < 1:
            errors.append("staffing_budget.%s must be an integer >= 1" % field)
    if budget.get("default_max_product_lanes") != 3:
        errors.append("default_max_product_lanes must be 3")
    if budget.get("default_target_active_child_tasks") != 6:
        errors.append("default_target_active_child_tasks must be 6")
    if budget.get("hard_cap_active_child_tasks") != 8 or budget.get("max_active_child_tasks", 99) > 8:
        errors.append("active child hard cap is 8")
    if budget.get("target_active_child_tasks", 99) > budget.get("max_active_child_tasks", 0):
        errors.append("target_active_child_tasks exceeds active maximum")
    if budget.get("min_productive_concurrency", 99) > budget.get("target_active_child_tasks", 0):
        errors.append("min_productive_concurrency exceeds target")
    if budget.get("max_registered_visible_tasks_per_run") != 12:
        errors.append("registered visible task hard cap is 12")
    if not 60 <= budget.get("underfill_alert_seconds", 0) <= 120:
        errors.append("underfill_alert_seconds must be between 60 and 120")
    if budget.get("max_product_lanes", 0) > 4:
        errors.append("max_product_lanes cannot exceed 4")
    adjusted = budget.get("max_product_lanes") != 3 or budget.get("target_active_child_tasks") != 6
    if adjusted and (not nonempty(budget.get("adjustment_reason")) or not budget.get("adjustment_evidence")):
        errors.append("adjusted staffing budget requires reason and evidence")
    if budget.get("max_product_lanes") == 4 and budget.get("ownership_mutually_exclusive") is not True:
        errors.append("four product lanes require mutually exclusive ownership evidence")
    return budget


def validate(data: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if data.get("schema") != EXPECTED_SCHEMA:
        errors.append("schema must be %s" % EXPECTED_SCHEMA)
    if data.get("mode") != EXPECTED_MODE:
        errors.append("mode must be %s" % EXPECTED_MODE)
    run_id, generation, epoch, pack = data.get("run_id"), data.get("generation"), data.get("director_epoch"), data.get("shared_pack_revision")
    if not nonempty(run_id) or not isinstance(generation, int) or generation < 1 or not isinstance(epoch, int) or epoch < 1 or not nonempty(pack):
        errors.append("run_id, generation>=1, director_epoch>=1, and shared_pack_revision are required")
    if data.get("root_session_id") != "TD-01" or data.get("spawn_authority") != ["TD-01"]:
        errors.append("TD-01 must be root and sole spawn authority")
    budget = validate_budget(data, errors)
    coordination = data.get("notion_coordination", {})
    if not isinstance(coordination, dict) or coordination.get("writer_session_id") != "PK-01":
        errors.append("PK-01 must be the Notion coordination writer")
    if coordination.get("mode") in {"DIRECT_WRITABLE", "BROKERED_WRITABLE"} and coordination.get("schema_state") != "READY":
        errors.append("writable coordination requires schema_state READY")
    for flag in ("event_ledger_required", "state_projection_required", "outbox_required", "checkpoint_required", "traceability_required"):
        if coordination.get(flag) is not True:
            errors.append("notion_coordination.%s must be true" % flag)

    sessions = data.get("sessions")
    if not isinstance(sessions, list) or not sessions:
        return errors + ["sessions must be a non-empty array"]
    if len(sessions) > budget.get("max_registered_visible_tasks_per_run", 0):
        errors.append("registered visible task count exceeds hard cap")
    by_id: Dict[str, Dict[str, Any]] = {}
    role_counts: Dict[str, int] = {}
    notion_writers: List[str] = []
    for index, task in enumerate(sessions):
        if not isinstance(task, dict) or not nonempty(task.get("session_id")):
            errors.append("sessions[%d] must have a session_id" % index)
            continue
        sid, role = task["session_id"], task.get("role")
        if sid in by_id:
            errors.append("duplicate session_id: %s" % sid)
            continue
        by_id[sid] = task
        role_counts[role] = role_counts.get(role, 0) + 1
        if task.get("visible_task") is not True or task.get("transport") != "visible_codex_task":
            errors.append("%s must be sidebar-visible; hidden roles are forbidden" % sid)
        for field in ("threadId", "hostId", "title", "model", "reasoning_effort", "model_rationale"):
            if not nonempty(task.get(field)):
                errors.append("%s.%s must be non-empty" % (sid, field))
        title = task.get("title", "")
        if nonempty(run_id) and (str(run_id) not in title or sid not in title or str(task.get("lane", "")) not in title):
            errors.append("%s title must contain run_id, role ID, and lane" % sid)
        if task.get("risk_level") not in {"low", "medium", "high", "critical"} or task.get("routing_source") not in {"default", "director_override", "user_override", "escalation"}:
            errors.append("%s requires valid risk_level and routing_source" % sid)
        if task.get("routing_source") == "default" and role in SOL_DEFAULT_ROLES and task.get("model") != "gpt-5.6-sol":
            errors.append("%s default route must use gpt-5.6-sol" % sid)
        if task.get("routing_source") == "default" and role in LUNA_DEFAULT_ROLES and task.get("model") != "gpt-5.6-luna":
            errors.append("%s default route must use gpt-5.6-luna" % sid)
        if task.get("routing_source") == "escalation":
            history = task.get("model_history", [])
            if task.get("reuse_threadId") != task.get("threadId") or not any(item.get("model") == "gpt-5.6-luna" for item in history if isinstance(item, dict)):
                errors.append("%s escalation must reuse the same thread and retain Luna history" % sid)
        state = task.get("state")
        if state not in TASK_STATES:
            errors.append("%s state is invalid" % sid)
        if state in CURRENT_STATES and (task.get("generation") != generation or task.get("director_epoch") != epoch or task.get("pack_revision") != pack):
            errors.append("%s has stale generation, director_epoch, or shared_pack_revision" % sid)
        if state != "active" and task.get("productive") is True:
            errors.append("%s cannot be productive unless active" % sid)
        if state == "queued" and task.get("waiting_on_dependency") is True and task.get("ready_for_dispatch") is True:
            errors.append("%s dependency wait cannot be ready work" % sid)
        if task.get("notion_write") is True:
            notion_writers.append(sid)
        packet = task.get("task_packet")
        if not isinstance(packet, dict):
            errors.append("%s task_packet must be an object" % sid)
        else:
            for field in ("generation", "director_epoch", "pack_revision", "model", "reasoning_effort", "model_rationale", "risk_level", "may_delegate"):
                if packet.get(field) != task.get(field):
                    errors.append("%s task_packet.%s must match manifest" % (sid, field))
        if sid == "TD-01":
            if role != "technical-director" or task.get("root_task") is not True or task.get("created_via") != "current_task" or task.get("may_delegate") is not True:
                errors.append("TD-01 must be current root Director and sole delegator")
        elif task.get("root_task") is not False or task.get("created_via") != "create_thread" or task.get("may_delegate") is not False:
            errors.append("%s must be created with create_thread and must set may_delegate=false" % sid)
        if sid != "TD-01" and (task.get("parent_session_id") != "TD-01" or task.get("managed_by") != "TD-01"):
            errors.append("%s must be parented and managed by TD-01" % sid)
        if role in REPO_WRITERS and not nonempty(task.get("worktree")):
            errors.append("repository writer %s requires an isolated worktree" % sid)
        if role == "domain-developer" and task.get("test_acceptance") is not False:
            errors.append("developer %s must set test_acceptance=false" % sid)
        if role == "quality-engineer" and task.get("test_acceptance") is not True:
            errors.append("quality engineer %s must set test_acceptance=true" % sid)
    for role, sid in SINGLETON_ROLES.items():
        if role_counts.get(role) != 1 or by_id.get(sid, {}).get("role") != role:
            errors.append("exactly one %s (%s) is required" % (role, sid))
    if notion_writers != ["PK-01"]:
        errors.append("PK-01 must be the only session/task with notion_write=true")

    lanes = data.get("lanes", [])
    if not isinstance(lanes, list) or len(lanes) > budget.get("max_product_lanes", 0):
        errors.append("product lanes must be an array within budget")
        lanes = []
    lane_ids: Set[str] = set()
    lane_devs: Set[str] = set()
    lane_tests: Set[str] = set()
    for lane in lanes:
        lane_id = lane.get("lane_id") if isinstance(lane, dict) else None
        if not nonempty(lane_id) or lane_id in lane_ids:
            errors.append("lane IDs must be unique and non-empty")
            continue
        lane_ids.add(lane_id)
        dev_id, test_id = lane.get("developer_session_id"), lane.get("tester_session_id")
        dev, tester = by_id.get(dev_id), by_id.get(test_id)
        if not dev or dev.get("role") != "domain-developer" or not tester or tester.get("role") != "quality-engineer":
            errors.append("lane %s requires developer/tester pair" % lane_id)
        elif dev.get("paired_session_id") != test_id or tester.get("paired_session_id") != dev_id:
            errors.append("lane %s pairing must be reciprocal" % lane_id)
        lane_devs.add(dev_id)
        lane_tests.add(test_id)
    if lane_devs != {sid for sid, item in by_id.items() if item.get("role") == "domain-developer"} or lane_tests != {sid for sid, item in by_id.items() if item.get("role") == "quality-engineer"}:
        errors.append("every developer/tester must appear in exactly one lane")

    writable: List[Tuple[str, str]] = []
    for sid, task in by_id.items():
        if task.get("role") in REPO_WRITERS and task.get("role") != "integration-owner" and task.get("state") == "active":
            writable.extend((sid, scope) for scope in task.get("write_scope", []) if isinstance(scope, str) and path_prefix(scope))
    for index, (sid_a, scope_a) in enumerate(writable):
        for sid_b, scope_b in writable[index + 1:]:
            if sid_a != sid_b and overlaps(scope_a, scope_b):
                errors.append("overlapping write scopes among active tasks: %s:%s and %s:%s" % (sid_a, scope_a, sid_b, scope_b))

    children = [task for task in sessions if isinstance(task, dict) and task.get("session_id") != "TD-01"]
    derived = {
        "registered_count": len(sessions),
        "active_count": sum(task.get("state") == "active" for task in children),
        "productive_active_count": sum(task.get("state") == "active" and task.get("productive") is True for task in children),
        "ready_count": sum(task.get("state") == "queued" and task.get("ready_for_dispatch") is True for task in children),
        "attention_count": sum(task.get("state") == "attention" for task in children),
        "settled_count": sum(task.get("state") == "settled" for task in children),
        "archived_count": sum(task.get("state") == "archived" for task in children),
    }
    concurrency = data.get("concurrency_state", {})
    if not isinstance(concurrency, dict):
        errors.append("concurrency_state must be an object")
        concurrency = {}
    for field, expected in derived.items():
        if concurrency.get(field) != expected:
            errors.append("concurrency_state.%s must equal %s" % (field, expected))
    if not nonempty(concurrency.get("last_reconciled_at")):
        errors.append("last_reconciled_at is required")
    if concurrency.get("target") != budget.get("target_active_child_tasks") or concurrency.get("min") != budget.get("min_productive_concurrency") or concurrency.get("hard_max") != 8:
        errors.append("concurrency target/min/hard_max must match budget")
    if derived["active_count"] > budget.get("max_active_child_tasks", 0):
        errors.append("active child task count exceeds hard cap")
    if derived["active_count"] < budget.get("target_active_child_tasks", 0) and derived["ready_count"] > 0 and not nonempty(concurrency.get("dispatch_action")) and not nonempty(concurrency.get("underfill_reason")):
        errors.append("active below target with ready work requires action or reason")
    underfilled = derived["ready_count"] >= budget.get("min_productive_concurrency", 0) and derived["productive_active_count"] < budget.get("min_productive_concurrency", 0)
    if underfilled and concurrency.get("underfill_age_seconds", 0) >= budget.get("underfill_alert_seconds", 90):
        if not nonempty(concurrency.get("underfill_reason")) or "CONCURRENCY_UNDERFILLED" not in concurrency.get("events", []):
            errors.append("low concurrency requires reason and CONCURRENCY_UNDERFILLED event")
    if data.get("gates") != REQUIRED_GATES:
        errors.append("gates must be exactly %s" % REQUIRED_GATES)
    pipeline = data.get("pipeline", {})
    if pipeline.get("capability_state") not in {"EXISTS_VALID", "EXISTS_GAPPED", "MISSING", "BLOCKED"} or not nonempty(pipeline.get("provider_policy")):
        errors.append("pipeline must record capability_state and provider_policy")
    return errors


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        data = load_json(args.manifest)
    except ValueError as exc:
        print("Company Swarm organization validation failed:\n- %s" % exc, file=sys.stderr)
        return 1
    errors = validate(data)
    if errors:
        print("Company Swarm organization validation failed:", file=sys.stderr)
        for error in errors:
            print("- %s" % error, file=sys.stderr)
        return 1
    print("Company Swarm organization validation OK: %d visible tasks, %d lanes." % (len(data["sessions"]), len(data.get("lanes", []))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
