#!/usr/bin/env python3
"""Recommend bounded Sol-Luna session reuse, spawning, or queuing.

The script is deterministic control-plane assistance. It never creates sessions
or sends messages; the current planner applies the recommendations through the
runtime adapter and records what actually happened.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ACTIVE_STATES = {"starting", "running", "busy", "ambiguous"}
IDLE_STATE = "idle"
ROLE_CLASS = {
    "implementation": "worker",
    "repair": "worker",
    "integration": "worker",
    "verification": "tester",
    "investigation": "tester",
    "reviewer": "reviewer",
}


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path}: root must be an object")
    return data


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def affinity_score(lane: dict[str, Any], session: dict[str, Any]) -> int:
    lane_tags = {str(tag) for tag in as_list(lane.get("session_affinity"))}
    session_tags = {str(tag) for tag in as_list(session.get("affinity"))}
    exact = len(lane_tags & session_tags)
    adjacent = sum(
        1
        for left in lane_tags
        for right in session_tags
        if left != right and (left.startswith(right + "/") or right.startswith(left + "/"))
    )
    return exact * 100 + adjacent * 10


def compatible(route: dict[str, Any], lane: dict[str, Any], session: dict[str, Any]) -> bool:
    return all(
        (
            session.get("state") == IDLE_STATE,
            session.get("role_class") == ROLE_CLASS.get(lane.get("role")),
            session.get("model") == lane.get("model"),
            session.get("effort") == lane.get("effort"),
            session.get("generation") in {None, route.get("generation")},
            session.get("memory_pack_ref") in {None, route.get("shared_memory", {}).get("memory_pack_ref")},
            session.get("unresolved_writes") is not True,
        )
    )


def recommend(route: dict[str, Any], pool: dict[str, Any]) -> dict[str, Any]:
    policy = route.get("session_policy", {})
    role_limits = policy.get("role_limits", {})
    total_limit = policy.get("max_total_sessions", 0)
    sessions = [item.copy() for item in as_list(pool.get("sessions")) if isinstance(item, dict)]
    recommendations: list[dict[str, Any]] = []

    settled_lanes = {str(item) for item in as_list(pool.get("settled_lanes"))}
    ready_lanes = [
        lane
        for lane in as_list(route.get("lanes"))
        if (
            isinstance(lane, dict)
            and lane.get("dispatch_state", "ready") == "ready"
            and set(str(item) for item in as_list(lane.get("depends_on"))).issubset(settled_lanes)
        )
    ]
    for lane in ready_lanes:
        role_class = ROLE_CLASS.get(lane.get("role"))
        candidates = [session for session in sessions if compatible(route, lane, session)]
        candidates.sort(
            key=lambda session: (
                -affinity_score(lane, session),
                str(session.get("last_active_at", "")),
                str(session.get("id", "")),
            )
        )
        if candidates:
            chosen = candidates[0]
            chosen["state"] = "reserved"
            recommendations.append(
                {
                    "lane_id": lane.get("id"),
                    "action": "reuse",
                    "session_id": chosen.get("id"),
                    "role_class": role_class,
                    "affinity_score": affinity_score(lane, chosen),
                    "reason": "compatible idle session preferred for cache and context continuity",
                }
            )
            continue

        live_sessions = [s for s in sessions if s.get("state") in ACTIVE_STATES | {IDLE_STATE, "reserved"}]
        role_sessions = [s for s in live_sessions if s.get("role_class") == role_class]
        role_limit = role_limits.get(role_class, 0)
        if (
            isinstance(total_limit, int)
            and isinstance(role_limit, int)
            and len(live_sessions) < total_limit
            and len(role_sessions) < role_limit
        ):
            placeholder = {
                "id": f"new:{lane.get('id')}",
                "state": "starting",
                "role_class": role_class,
                "model": lane.get("model"),
                "effort": lane.get("effort"),
            }
            sessions.append(placeholder)
            recommendations.append(
                {
                    "lane_id": lane.get("id"),
                    "action": "spawn",
                    "session_id": None,
                    "role_class": role_class,
                    "affinity_score": 0,
                    "reason": "no compatible idle session and confirmed capacity remains",
                }
            )
        else:
            recommendations.append(
                {
                    "lane_id": lane.get("id"),
                    "action": "queue",
                    "session_id": None,
                    "role_class": role_class,
                    "affinity_score": 0,
                    "reason": "no compatible idle session or confirmed session cap reached",
                }
            )

    return {
        "version": "codex-sol-luna-session-plan-v1",
        "run_id": route.get("run_id"),
        "generation": route.get("generation"),
        "recommendations": recommendations,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("route", type=Path)
    parser.add_argument("pool", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        route = load_json(args.route)
        pool = load_json(args.pool)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    output = recommend(route, pool)
    rendered = json.dumps(output, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"WROTE: {args.output}")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
