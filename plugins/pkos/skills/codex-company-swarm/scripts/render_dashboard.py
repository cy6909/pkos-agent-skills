#!/usr/bin/env python3
"""Render an evidence-oriented Markdown dashboard from Company Swarm run state."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List


def load_json(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError("file not found: %s" % path) from exc
    except json.JSONDecodeError as exc:
        raise ValueError("invalid JSON at line %s column %s: %s" % (exc.lineno, exc.colno, exc.msg)) from exc
    if not isinstance(data, dict):
        raise ValueError("run state must be a JSON object")
    return data


def text(value: Any) -> str:
    if value is None:
        return "—"
    return str(value).replace("|", "\\|").replace("\n", " ")


def percent(numerator: int, denominator: int) -> str:
    return "—" if denominator <= 0 else "%.1f%%" % (100.0 * numerator / denominator)


def node_id(value: str) -> str:
    return "N_" + "".join(ch if ch.isalnum() else "_" for ch in value)


def render(data: Dict[str, Any]) -> str:
    sessions = data.get("sessions") if isinstance(data.get("sessions"), list) else []
    features = data.get("features") if isinstance(data.get("features"), list) else []
    mfsq = data.get("mfsq") if isinstance(data.get("mfsq"), dict) else {}
    pipeline = data.get("pipeline") if isinstance(data.get("pipeline"), dict) else {}
    security = data.get("security") if isinstance(data.get("security"), dict) else {}
    performance = data.get("performance") if isinstance(data.get("performance"), list) else []
    reviews = data.get("reviews") if isinstance(data.get("reviews"), list) else []
    risks = data.get("risks") if isinstance(data.get("risks"), list) else []
    writeback = data.get("pkos_writeback") if isinstance(data.get("pkos_writeback"), dict) else {}
    model = data.get("model") if isinstance(data.get("model"), dict) else {}

    session_states = Counter(str(item.get("state", "unknown")) for item in sessions if isinstance(item, dict))
    feature_states = Counter(str(item.get("status", "unknown")) for item in features if isinstance(item, dict))
    accepted = feature_states.get("accepted", 0) + feature_states.get("complete", 0)

    out: List[str] = [
        "# Company Swarm Dashboard — %s" % text(data.get("run_id")),
        "",
        "| Field | Value |",
        "|---|---|",
        "| Status | `%s` |" % text(data.get("status")),
        "| Generation | %s |" % text(data.get("generation")),
        "| Requested model | `%s` |" % text(model.get("requested")),
        "| Reasoning effort | `%s` |" % text(model.get("reasoning_effort")),
        "| Identity confidence | `%s` |" % text(model.get("identity_confidence")),
        "| Sessions | %d total; %s |" % (len(sessions), ", ".join("%s=%d" % item for item in sorted(session_states.items())) or "none"),
        "| Features | %d/%d accepted or complete (%s) |" % (accepted, len(features), percent(accepted, len(features))),
        "",
        "## Organization",
        "",
        "```mermaid",
        "graph TD",
    ]

    for item in sessions:
        if not isinstance(item, dict):
            continue
        sid = str(item.get("session_id", "unknown"))
        label = "%s\\n%s / %s\\n%s" % (sid, item.get("role", "unknown"), item.get("domain", "—"), item.get("state", "unknown"))
        out.append('  %s["%s"]' % (node_id(sid), label.replace('"', "'")))
        if sid != "TD-01":
            out.append("  %s --> %s" % (node_id("TD-01"), node_id(sid)))
    seen_pairs = set()
    for item in sessions:
        if not isinstance(item, dict):
            continue
        sid = item.get("session_id")
        pair = item.get("paired_session_id")
        if isinstance(sid, str) and isinstance(pair, str):
            key = tuple(sorted((sid, pair)))
            if key not in seen_pairs:
                seen_pairs.add(key)
                out.append("  %s -. paired .- %s" % (node_id(sid), node_id(pair)))
    out.extend(["```", "", "| Session | Role | Domain | State | Pair |", "|---|---|---|---|---|"])
    for item in sessions:
        if isinstance(item, dict):
            out.append("| %s | %s | %s | %s | %s |" % tuple(text(item.get(key)) for key in ("session_id", "role", "domain", "state", "paired_session_id")))
    if not sessions:
        out.append("| — | — | — | — | — |")

    out.extend(["", "## Feature delivery", "", "| Feature | Type | Lane | Status |", "|---|---|---|---|"])
    for item in features:
        if isinstance(item, dict):
            out.append("| %s — %s | %s | %s | %s |" % (text(item.get("feature_id")), text(item.get("title")), text(item.get("type")), text(item.get("lane")), text(item.get("status"))))
    if not features:
        out.append("| — | — | — | — |")

    out.extend(["", "## MFSQ evidence", "", "| Axis | Passed | Failed | Blocked | N/A | Pass rate |", "|---|---:|---:|---:|---:|---:|"])
    for axis in ("M", "F", "S", "Q"):
        values = mfsq.get(axis) if isinstance(mfsq.get(axis), dict) else {}
        passed = int(values.get("passed", 0) or 0)
        failed = int(values.get("failed", 0) or 0)
        blocked = int(values.get("blocked", 0) or 0)
        na = int(values.get("na", 0) or 0)
        out.append("| %s | %d | %d | %d | %d | %s |" % (axis, passed, failed, blocked, na, percent(passed, passed + failed + blocked)))

    passed_jobs = int(pipeline.get("passed_jobs", 0) or 0)
    total_jobs = int(pipeline.get("total_jobs", 0) or 0)
    out.extend([
        "", "## CI/CD", "", "| Field | Value |", "|---|---|",
        "| Provider | %s |" % text(pipeline.get("provider")),
        "| Pipeline | %s |" % text(pipeline.get("pipeline")),
        "| Run ID | %s |" % text(pipeline.get("run_id")),
        "| Candidate | %s |" % text(pipeline.get("candidate_commit")),
        "| Status | %s |" % text(pipeline.get("status")),
        "| Duration (s) | %s |" % text(pipeline.get("duration_seconds")),
        "| Job pass rate | %d/%d (%s) |" % (passed_jobs, total_jobs, percent(passed_jobs, total_jobs)),
        "| Artifacts | %s |" % (", ".join(text(item) for item in pipeline.get("artifacts", [])) if isinstance(pipeline.get("artifacts"), list) and pipeline.get("artifacts") else "—"),
        "", "## Security", "", "| Critical | High | Medium | Low | Unresolved |", "|---:|---:|---:|---:|---:|",
        "| %s | %s | %s | %s | %s |" % tuple(text(security.get(key, 0)) for key in ("critical", "high", "medium", "low", "unresolved")),
        "", "## Performance", "", "| Metric | Baseline | Candidate | Threshold | Result |", "|---|---:|---:|---|---|",
    ])
    for item in performance:
        if isinstance(item, dict):
            unit = text(item.get("unit"))
            out.append("| %s | %s %s | %s %s | %s | %s |" % (text(item.get("metric")), text(item.get("baseline")), unit, text(item.get("candidate")), unit, text(item.get("threshold")), text(item.get("result"))))
    if not performance:
        out.append("| — | — | — | — | — |")

    out.extend(["", "## Review history", "", "| Gate | Generation | Verdict |", "|---|---:|---|"])
    for item in reviews:
        if isinstance(item, dict):
            out.append("| %s | %s | %s |" % (text(item.get("gate")), text(item.get("generation")), text(item.get("verdict"))))
    if not reviews:
        out.append("| — | — | — |")
    out.extend(["", "Ownership violations: **%s**" % text(data.get("ownership_violations", 0)), "", "## Residual risks", ""])
    if risks:
        for item in risks:
            if isinstance(item, dict):
                out.append("- **%s / %s:** %s" % (text(item.get("severity")), text(item.get("status")), text(item.get("description"))))
    else:
        out.append("- None recorded.")

    changed = writeback.get("changed_nodes") if isinstance(writeback.get("changed_nodes"), list) else []
    out.extend([
        "", "## PKOS writeback", "",
        "- Status: `%s`" % text(writeback.get("status")),
        "- Changed nodes/rows: %s" % (", ".join("`%s`" % text(item) for item in changed) if changed else "none confirmed"),
        "", "_Generated from the durable run-state artifact; verify referenced commits, CI reports, and Notion write responses before relying on this dashboard._", ""
    ])
    return "\n".join(out)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_state", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        dashboard = render(load_json(args.run_state))
    except (ValueError, TypeError, KeyError) as exc:
        print("Dashboard rendering failed: %s" % exc, file=sys.stderr)
        return 1
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(dashboard, encoding="utf-8")
        print("Wrote dashboard: %s" % args.output)
    else:
        print(dashboard)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
