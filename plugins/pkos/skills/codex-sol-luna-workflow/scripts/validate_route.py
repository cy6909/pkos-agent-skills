#!/usr/bin/env python3
"""Validate a Codex Sol-Luna route before dispatch.

The validator checks deterministic invariants: model/role boundaries, bounded
Luna packets, ownership isolation, parallel worktrees, integration barriers,
strict fresh review, and bounded retry budgets. It does not choose the route.
"""

from __future__ import annotations

import argparse
import json
import posixpath
import sys
from pathlib import Path
from typing import Any

VERSION = "codex-sol-luna-route-v2"
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
    require(lane.get("fresh_session") is True, f"{prefix}: fresh_session must be true", errors)
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

    require(all(isinstance(p, str) and clean_scope(p) for p in write_paths), f"{prefix}: write_paths must contain non-empty paths", errors)
    require(all(isinstance(p, str) and clean_scope(p) for p in excluded_paths), f"{prefix}: excluded_paths must contain non-empty paths", errors)
    require(all(isinstance(p, str) and p.strip() for p in context_refs), f"{prefix}: context_refs must contain strings", errors)

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
        require(planner.get("model") == SOL_MODEL, f"planner must use {SOL_MODEL}", errors)
        require(planner.get("effort") in ALLOWED_EFFORTS, "planner effort is invalid", errors)
        require(planner.get("non_writer") is True, "planner.non_writer must be true", errors)
        if planner.get("effort") == "max":
            require(bool(planner.get("max_reason")), "planner max effort requires max_reason", errors)
        if route.get("profile") == "max-pair":
            require(planner.get("effort") == "max", "max-pair planner must use max", errors)

    validate_external_actions(route, errors)

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
