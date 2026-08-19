#!/usr/bin/env python3
"""Validate a Codex Sol-Luna route before dispatch.

The validator checks deterministic invariants: current-session planning,
user-confirmed session caps, shared-memory loading, execution environments,
design gates, model/role boundaries, ownership isolation, parallel worktrees,
integration barriers, strict fresh review, and bounded retry budgets.
"""

from __future__ import annotations

import argparse
import json
import posixpath
import sys
from pathlib import Path
from typing import Any

VERSION = "codex-sol-luna-route-v3"
SOL_MODEL = "gpt-5.6-sol"
LUNA_MODEL = "gpt-5.6-luna"
ALLOWED_EFFORTS = {"none", "low", "medium", "high", "xhigh", "max"}
ALLOWED_PROFILES = {"adaptive", "max-pair"}
ALLOWED_ASSURANCE = {"standard", "strict"}
ALLOWED_BOUNDARY_MODES = {"practical", "supervision-only"}
ALLOWED_WORKTREE_MODES = {"sequential", "isolated"}
ALLOWED_ROLES = {
    "implementation",
    "repair",
    "integration",
    "verification",
    "reviewer",
    "investigation",
}
WRITING_ROLES = {"implementation", "repair", "integration"}
LUNA_WRITING_ROLES = {"implementation", "repair", "integration"}
ROLE_CLASS = {
    "implementation": "worker",
    "repair": "worker",
    "integration": "worker",
    "verification": "tester",
    "investigation": "tester",
    "reviewer": "reviewer",
}
REMOTE_REQUIRED_KINDS = {"test", "build", "benchmark", "container", "migration", "deploy", "runtime"}


class RouteValidationError(Exception):
    """Raised for malformed route input."""


def load_route(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise RouteValidationError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RouteValidationError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise RouteValidationError("route root must be a JSON object")
    return data


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def clean_scope(path: str) -> str:
    value = path.replace("\\", "/").strip()
    while value.endswith("/**"):
        value = value[:-3]
    value = value.rstrip("/")
    normalized = posixpath.normpath(value)
    return "" if normalized == "." else normalized


def path_contains(scope: str, path: str) -> bool:
    s = clean_scope(scope)
    p = clean_scope(path)
    if not s or not p:
        return False
    return p == s or p.startswith(s + "/")


def scopes_overlap(left: str, right: str) -> bool:
    a = clean_scope(left)
    b = clean_scope(right)
    if not a or not b:
        return False
    return a == b or a.startswith(b + "/") or b.startswith(a + "/")


def validate_external_actions(route: dict[str, Any], errors: list[str]) -> None:
    actions = route.get("external_actions", [])
    require(isinstance(actions, list), "external_actions must be a list", errors)
    if not isinstance(actions, list):
        return
    for index, action in enumerate(actions):
        if isinstance(action, str):
            errors.append(
                f"external_actions[{index}] must be an object with authorized=true"
            )
            continue
        if not isinstance(action, dict):
            errors.append(f"external_actions[{index}] must be an object")
            continue
        require(bool(action.get("action")), f"external_actions[{index}] missing action", errors)
        require(
            action.get("authorized") is True,
            f"external_actions[{index}] is not explicitly authorized",
            errors,
        )


def validate_session_policy(route: dict[str, Any], errors: list[str]) -> None:
    policy = route.get("session_policy")
    require(isinstance(policy, dict), "session_policy object is required", errors)
    if not isinstance(policy, dict):
        return
    require(policy.get("confirmed_by_user") is True, "session_policy must be confirmed by the user", errors)
    require(policy.get("reuse_idle_sessions") is True, "session_policy.reuse_idle_sessions must be true", errors)
    require(policy.get("prefer_affinity_reuse") is True, "session_policy.prefer_affinity_reuse must be true", errors)
    total = policy.get("max_total_sessions")
    require(isinstance(total, int) and not isinstance(total, bool) and total >= 1, "session_policy.max_total_sessions must be an integer >= 1", errors)
    limits = policy.get("role_limits")
    require(isinstance(limits, dict), "session_policy.role_limits object is required", errors)
    if not isinstance(limits, dict):
        return
    for role_class in ("worker", "tester", "reviewer"):
        value = limits.get(role_class)
        require(isinstance(value, int) and not isinstance(value, bool) and value >= 0, f"session_policy.role_limits.{role_class} must be an integer >= 0", errors)
    if isinstance(total, int) and all(isinstance(limits.get(key), int) for key in ("worker", "tester", "reviewer")):
        require(sum(limits[key] for key in ("worker", "tester", "reviewer")) >= total, "role limits must provide capacity for max_total_sessions", errors)


def validate_shared_memory(route: dict[str, Any], errors: list[str]) -> None:
    memory = route.get("shared_memory")
    require(isinstance(memory, dict), "shared_memory object is required", errors)
    if not isinstance(memory, dict):
        return
    require(memory.get("required") is True, "shared_memory.required must be true", errors)
    require(memory.get("planner_loaded") is True, "planner must load shared memory before dispatch", errors)
    require(memory.get("worker_ack_required") is True, "shared_memory.worker_ack_required must be true", errors)
    require(memory.get("worker_direct_notion_required") is True, "shared_memory.worker_direct_notion_required must be true", errors)
    require(bool(memory.get("memory_pack_ref")), "shared_memory.memory_pack_ref is required", errors)
    sources = memory.get("notion_source_refs")
    require(isinstance(sources, list) and bool(sources), "shared_memory.notion_source_refs must be a non-empty list", errors)
    if isinstance(sources, list):
        require(all(isinstance(item, str) and item.strip() for item in sources), "shared_memory.notion_source_refs must contain non-empty strings", errors)


def validate_execution_policy(route: dict[str, Any], errors: list[str]) -> None:
    policy = route.get("execution_policy")
    require(isinstance(policy, dict), "execution_policy object is required", errors)
    if not isinstance(policy, dict):
        return
    require(policy.get("local_mode") == "development-only", "execution_policy.local_mode must be development-only", errors)
    require(bool(policy.get("resource_environment")), "execution_policy.resource_environment is required", errors)
    require(policy.get("remote_pull_required") is True, "execution_policy.remote_pull_required must be true", errors)
    forbidden = as_list(policy.get("local_forbidden"))
    require(REMOTE_REQUIRED_KINDS.issubset(set(forbidden)), "execution_policy.local_forbidden must cover every resource-intensive kind", errors)


def validate_design_policy(route: dict[str, Any], lanes: list[dict[str, Any]], errors: list[str]) -> None:
    ui_lanes = [lane for lane in lanes if lane.get("ui_change") is True]
    if not ui_lanes:
        return
    design = route.get("design_policy")
    require(isinstance(design, dict), "UI routes require design_policy", errors)
    if not isinstance(design, dict):
        return
    require(design.get("figma_required_before_implementation") is True, "UI routes require the Figma pre-implementation gate", errors)
    require(design.get("figma_plugin_loaded") is True, "UI routes require the Figma plugin to be loaded", errors)
    require(design.get("figma_design_updated") is True, "UI routes require the canonical Figma design to be updated first", errors)
    require(bool(design.get("figma_evidence_ref")), "UI routes require figma_evidence_ref", errors)


def validate_lane(
    lane: dict[str, Any],
    route: dict[str, Any],
    lane_ids: set[str],
    errors: list[str],
    warnings: list[str],
) -> None:
    lane_id = lane.get("id")
    role = lane.get("role")
    model = lane.get("model")
    effort = lane.get("effort")
    prefix = f"lane {lane_id or '<missing>'}"

    require(isinstance(lane_id, str) and bool(lane_id.strip()), f"{prefix}: missing id", errors)
    if isinstance(lane_id, str):
        require(lane_id not in lane_ids, f"duplicate lane id: {lane_id}", errors)
        lane_ids.add(lane_id)

    require(role in ALLOWED_ROLES, f"{prefix}: unsupported role {role!r}", errors)
    require(effort in ALLOWED_EFFORTS, f"{prefix}: invalid effort {effort!r}", errors)
    require(lane.get("bounded") is True, f"{prefix}: bounded must be true", errors)
    require(lane.get("may_delegate") is False, f"{prefix}: may_delegate must be false", errors)
    require(bool(lane.get("objective")), f"{prefix}: objective is required", errors)
    require(bool(lane.get("completion_artifact")), f"{prefix}: completion_artifact is required", errors)
    require(isinstance(lane.get("depends_on", []), list), f"{prefix}: depends_on must be a list", errors)

    write_paths = as_list(lane.get("write_paths"))
    excluded_paths = as_list(lane.get("excluded_paths"))
    acceptance = as_list(lane.get("acceptance"))
    verification = as_list(lane.get("verification"))
    context_refs = as_list(lane.get("context_refs"))
    required_skills = as_list(lane.get("required_skills"))
    standards_refs = as_list(lane.get("standards_refs"))
    session_affinity = as_list(lane.get("session_affinity"))

    require(all(isinstance(p, str) and clean_scope(p) for p in write_paths), f"{prefix}: write_paths must contain non-empty paths", errors)
    require(all(isinstance(p, str) and clean_scope(p) for p in excluded_paths), f"{prefix}: excluded_paths must contain non-empty paths", errors)
    require(all(isinstance(p, str) and p.strip() for p in context_refs), f"{prefix}: context_refs must contain strings", errors)
    require(bool(required_skills) and all(isinstance(p, str) and p.strip() for p in required_skills), f"{prefix}: required_skills must contain at least one skill", errors)
    require(bool(standards_refs) and all(isinstance(p, str) and p.strip() for p in standards_refs), f"{prefix}: standards_refs must contain at least one governing reference", errors)
    require(bool(session_affinity) and all(isinstance(p, str) and p.strip() for p in session_affinity), f"{prefix}: session_affinity must contain at least one tag", errors)
    require(lane.get("memory_pack_ref") == route.get("shared_memory", {}).get("memory_pack_ref"), f"{prefix}: memory_pack_ref must match the route shared Memory Pack", errors)
    require(lane.get("role_class") == ROLE_CLASS.get(role), f"{prefix}: role_class does not match role", errors)
    require(isinstance(lane.get("ui_change"), bool), f"{prefix}: ui_change must be boolean", errors)

    execution_policy = route.get("execution_policy", {})
    resource_environment = execution_policy.get("resource_environment")
    for index, item in enumerate(verification):
        if not isinstance(item, dict):
            errors.append(f"{prefix}: verification[{index}] must be an object")
            continue
        kind = item.get("kind")
        environment = item.get("environment")
        require(isinstance(kind, str) and bool(kind), f"{prefix}: verification[{index}] kind is required", errors)
        require(isinstance(environment, str) and bool(environment), f"{prefix}: verification[{index}] environment is required", errors)
        if kind in REMOTE_REQUIRED_KINDS:
            require(environment == resource_environment, f"{prefix}: verification[{index}] kind {kind} must run in {resource_environment}", errors)

    if role in WRITING_ROLES:
        require(model == LUNA_MODEL, f"{prefix}: writing roles must use {LUNA_MODEL}", errors)
        require(lane.get("read_only") is False, f"{prefix}: writing role cannot be read_only", errors)
        require(bool(write_paths), f"{prefix}: writing role requires write_paths", errors)
        require(lane.get("judgment_open") is False, f"{prefix}: judgment_open must be false", errors)
        require(lane.get("interface_frozen") is True, f"{prefix}: interface_frozen must be true", errors)
        require(bool(acceptance), f"{prefix}: acceptance is required", errors)
        require(bool(verification), f"{prefix}: verification is required", errors)
        require(bool(lane.get("worktree")), f"{prefix}: worktree is required", errors)
        for owned in write_paths:
            for excluded in excluded_paths:
                require(
                    not scopes_overlap(owned, excluded),
                    f"{prefix}: owned scope {owned!r} overlaps excluded scope {excluded!r}",
                    errors,
                )
    elif role == "reviewer":
        require(model == SOL_MODEL, f"{prefix}: reviewer must use {SOL_MODEL}", errors)
        require(lane.get("read_only") is True, f"{prefix}: reviewer must be read_only", errors)
        require(lane.get("independent") is True, f"{prefix}: reviewer must be independent", errors)
        require(lane.get("fresh_session") is True, f"{prefix}: independent reviewer must use a fresh session", errors)
        require(not write_paths, f"{prefix}: reviewer cannot have write_paths", errors)
        require(bool(acceptance), f"{prefix}: reviewer acceptance contract is required", errors)
        require(bool(verification), f"{prefix}: reviewer verdict contract is required", errors)
    else:
        require(lane.get("read_only") is True, f"{prefix}: non-writing role should be read_only", errors)
        require(not write_paths, f"{prefix}: non-writing role cannot have write_paths", errors)
        if model is not None:
            require(model in {SOL_MODEL, LUNA_MODEL}, f"{prefix}: unsupported model {model!r}", errors)

    if effort == "max":
        require(bool(lane.get("max_reason")), f"{prefix}: max effort requires max_reason", errors)

    profile = route.get("profile")
    if profile == "max-pair" and role in LUNA_WRITING_ROLES:
        require(effort == "max", f"{prefix}: max-pair Luna writer must use max", errors)
    if profile == "max-pair" and role == "reviewer":
        require(effort == "max", f"{prefix}: max-pair reviewer must use max", errors)

    if len(context_refs) > 25:
        warnings.append(f"{prefix}: {len(context_refs)} context refs may be excessive")


def validate_dependencies(lanes: list[dict[str, Any]], errors: list[str]) -> None:
    ids = {lane.get("id") for lane in lanes if isinstance(lane.get("id"), str)}
    graph: dict[str, list[str]] = {}
    for lane in lanes:
        lane_id = lane.get("id")
        if not isinstance(lane_id, str):
            continue
        deps = as_list(lane.get("depends_on"))
        graph[lane_id] = []
        for dep in deps:
            require(isinstance(dep, str), f"lane {lane_id}: dependency must be a string", errors)
            if isinstance(dep, str):
                require(dep in ids, f"lane {lane_id}: unknown dependency {dep}", errors)
                require(dep != lane_id, f"lane {lane_id}: cannot depend on itself", errors)
                graph[lane_id].append(dep)

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visited:
            return
        if node in visiting:
            errors.append(f"dependency cycle detected at {node}")
            return
        visiting.add(node)
        for dep in graph.get(node, []):
            visit(dep)
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node)


def validate_parallel(route: dict[str, Any], lanes: list[dict[str, Any]], errors: list[str]) -> None:
    implementation_lanes = [
        lane for lane in lanes if lane.get("role") in {"implementation", "repair"}
    ]
    max_parallel = route.get("max_parallel_writers")
    require(isinstance(max_parallel, int) and 1 <= max_parallel <= 2, "max_parallel_writers must be an integer from 1 to 2", errors)

    if len(implementation_lanes) <= 1:
        return

    require(route.get("worktree_mode") == "isolated", "parallel writers require worktree_mode=isolated", errors)
    require(max_parallel >= len(implementation_lanes), "max_parallel_writers is lower than implementation lane count", errors)

    worktrees: set[str] = set()
    for lane in implementation_lanes:
        worktree = lane.get("worktree")
        require(isinstance(worktree, str) and bool(worktree), f"lane {lane.get('id')}: isolated worktree required", errors)
        if isinstance(worktree, str):
            require(worktree not in worktrees, f"parallel lanes reuse worktree {worktree}", errors)
            worktrees.add(worktree)

    for index, left in enumerate(implementation_lanes):
        for right in implementation_lanes[index + 1 :]:
            for a in as_list(left.get("write_paths")):
                for b in as_list(right.get("write_paths")):
                    require(
                        not scopes_overlap(a, b),
                        f"parallel ownership overlap: {left.get('id')}:{a} vs {right.get('id')}:{b}",
                        errors,
                    )

    barrier = route.get("integration_barrier")
    require(isinstance(barrier, dict), "parallel route requires integration_barrier", errors)
    if not isinstance(barrier, dict):
        return
    deps = as_list(barrier.get("depends_on"))
    expected = {lane.get("id") for lane in implementation_lanes}
    require(set(deps) == expected, "integration_barrier.depends_on must equal all implementation lane ids", errors)
    integration_lane_id = barrier.get("integration_lane")
    integration = next((lane for lane in lanes if lane.get("id") == integration_lane_id), None)
    require(integration is not None, "integration_barrier references unknown integration lane", errors)
    if integration is not None:
        require(integration.get("role") == "integration", "barrier integration lane must have role=integration", errors)
        require(set(as_list(integration.get("depends_on"))) == expected, "integration lane must depend on all implementation lanes", errors)
        require(integration.get("worktree") not in worktrees, "integration lane must use a separate worktree", errors)


def validate_route(route: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    require(route.get("version") == VERSION, f"version must be {VERSION}", errors)
    require(isinstance(route.get("run_id"), str) and bool(route.get("run_id", "").strip()), "run_id is required", errors)
    require(isinstance(route.get("generation"), int) and route.get("generation", 0) >= 1, "generation must be an integer >= 1", errors)
    require(route.get("profile") in ALLOWED_PROFILES, "invalid profile", errors)
    require(route.get("assurance") in ALLOWED_ASSURANCE, "invalid assurance", errors)
    require(isinstance(route.get("base_revision"), str) and bool(route.get("base_revision", "").strip()), "base_revision is required", errors)
    require(route.get("sol_boundary_mode") in ALLOWED_BOUNDARY_MODES, "invalid sol_boundary_mode", errors)
    require(route.get("worktree_mode") in ALLOWED_WORKTREE_MODES, "invalid worktree_mode", errors)
    require(route.get("repair_budget") in {0, 1}, "repair_budget must be 0 or 1", errors)

    planner = route.get("planner")
    require(isinstance(planner, dict), "planner object is required", errors)
    if isinstance(planner, dict):
        require(planner.get("model") in {SOL_MODEL, LUNA_MODEL}, "planner model must match the observed current supported session", errors)
        require(planner.get("effort") in ALLOWED_EFFORTS, "planner effort is invalid", errors)
        require(planner.get("non_writer") is True, "planner.non_writer must be true", errors)
        require(planner.get("session") == "current", "the current Skill-loading session must be the planner", errors)
        require(planner.get("spawn_planner") is False, "planner.spawn_planner must be false", errors)
        if planner.get("effort") == "max":
            require(bool(planner.get("max_reason")), "planner max effort requires max_reason", errors)
        if route.get("profile") == "max-pair":
            require(planner.get("effort") == "max", "max-pair planner must use max", errors)

    validate_external_actions(route, errors)
    validate_session_policy(route, errors)
    validate_shared_memory(route, errors)
    validate_execution_policy(route, errors)

    lanes_raw = route.get("lanes")
    require(isinstance(lanes_raw, list) and bool(lanes_raw), "lanes must be a non-empty list", errors)
    lanes = [lane for lane in lanes_raw if isinstance(lane, dict)] if isinstance(lanes_raw, list) else []
    if isinstance(lanes_raw, list):
        for index, lane in enumerate(lanes_raw):
            require(isinstance(lane, dict), f"lanes[{index}] must be an object", errors)

    lane_ids: set[str] = set()
    for lane in lanes:
        validate_lane(lane, route, lane_ids, errors, warnings)

    validate_dependencies(lanes, errors)
    validate_parallel(route, lanes, errors)
    validate_design_policy(route, lanes, errors)

    role_limits = route.get("session_policy", {}).get("role_limits", {})
    max_parallel = route.get("max_parallel_writers")
    if isinstance(role_limits, dict) and isinstance(role_limits.get("worker"), int) and isinstance(max_parallel, int):
        require(max_parallel <= role_limits["worker"], "max_parallel_writers exceeds the confirmed worker session limit", errors)
        declared_role_classes = {ROLE_CLASS.get(lane.get("role")) for lane in lanes}
        for role_class in declared_role_classes - {None}:
            require(role_limits.get(role_class, 0) >= 1, f"declared {role_class} lanes require a confirmed {role_class} session limit >= 1", errors)

    assurance = route.get("assurance")
    reviewers = [lane for lane in lanes if lane.get("role") == "reviewer"]
    review_budget = route.get("review_budget")
    if assurance == "strict":
        require(review_budget == 2, "strict assurance requires review_budget=2", errors)
        require(len(reviewers) == 1, "strict assurance requires exactly one declared reviewer lane", errors)
    else:
        require(review_budget == 0, "standard assurance requires review_budget=0", errors)
        require(not reviewers, "standard assurance must not predeclare a reviewer lane", errors)

    if route.get("sol_boundary_mode") == "supervision-only":
        warnings.append("supervision-only requires runtime evidence; route JSON alone is declarative")

    return errors, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("route", type=Path)
    parser.add_argument("--json", action="store_true", help="emit machine-readable result")
    args = parser.parse_args(argv)

    try:
        route = load_route(args.route)
    except RouteValidationError as exc:
        if args.json:
            print(json.dumps({"valid": False, "errors": [str(exc)], "warnings": []}, indent=2))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    errors, warnings = validate_route(route)
    if args.json:
        print(json.dumps({"valid": not errors, "errors": errors, "warnings": warnings}, indent=2))
    else:
        for warning in warnings:
            print(f"WARNING: {warning}")
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
        else:
            print(
                f"VALID: {route.get('run_id')} generation {route.get('generation')} "
                f"({route.get('profile')}/{route.get('assurance')}, {len(route.get('lanes', []))} lanes)"
            )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
