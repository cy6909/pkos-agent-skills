#!/usr/bin/env python3
"""Score serial vs parallel Codex Sol-Luna efficiency with a quality gate."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

VERSION = "codex-sol-luna-metrics-v1"


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("metrics root must be an object")
    return data


def number(value: Any, label: str, errors: list[str], *, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        errors.append(f"{label} must be a finite number")
        return 0.0
    result = float(value)
    if positive and result <= 0:
        errors.append(f"{label} must be > 0")
    return result


def integer(value: Any, label: str, errors: list[str], *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        errors.append(f"{label} must be an integer")
        return 0
    if value < minimum:
        errors.append(f"{label} must be >= {minimum}")
    return value


def quality_check(
    baseline: dict[str, Any],
    candidate: dict[str, Any],
    thresholds: dict[str, Any],
) -> tuple[bool, list[str], list[str]]:
    failures: list[str] = []
    notes: list[str] = []
    margin = float(thresholds.get("quality_margin", 0.0))
    max_extra_interventions = int(thresholds.get("max_extra_human_interventions", 0))

    hard_zero_fields = [
        "p0_p1_findings",
        "ownership_violations",
        "unresolved_blockers",
    ]
    for field in hard_zero_fields:
        value = candidate.get(field)
        if value is None:
            failures.append(f"parallel quality missing {field}")
        elif value != 0:
            failures.append(f"parallel {field} must be 0, got {value}")

    rate_fields = ["acceptance_pass_rate", "hidden_test_pass_rate"]
    for field in rate_fields:
        base = baseline.get(field)
        cand = candidate.get(field)
        if base is None or cand is None:
            failures.append(f"quality comparison missing {field}")
            continue
        if not isinstance(base, (int, float)) or not isinstance(cand, (int, float)):
            failures.append(f"quality field {field} must be numeric")
            continue
        if float(cand) + margin < float(base):
            failures.append(
                f"{field} regressed: baseline={base}, parallel={cand}, margin={margin}"
            )

    base_interventions = baseline.get("human_interventions", 0)
    cand_interventions = candidate.get("human_interventions", 0)
    if isinstance(base_interventions, int) and isinstance(cand_interventions, int):
        if cand_interventions - base_interventions > max_extra_interventions:
            failures.append(
                "human interventions exceeded margin: "
                f"baseline={base_interventions}, parallel={cand_interventions}, "
                f"allowed_extra={max_extra_interventions}"
            )
    else:
        notes.append("human intervention comparison unavailable")

    return not failures, failures, notes


def score(data: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    if data.get("version") != VERSION:
        errors.append(f"version must be {VERSION}")

    serial = data.get("serial_baseline")
    parallel = data.get("parallel_run")
    thresholds = data.get("thresholds", {})
    if not isinstance(serial, dict):
        errors.append("serial_baseline must be an object")
        serial = {}
    if not isinstance(parallel, dict):
        errors.append("parallel_run must be an object")
        parallel = {}
    if not isinstance(thresholds, dict):
        errors.append("thresholds must be an object")
        thresholds = {}

    serial_wall = number(serial.get("wall_seconds"), "serial_baseline.wall_seconds", errors, positive=True)
    parallel_wall = number(parallel.get("wall_seconds"), "parallel_run.wall_seconds", errors, positive=True)
    writers = integer(parallel.get("writer_count"), "parallel_run.writer_count", errors, minimum=1)
    coordination = number(parallel.get("coordination_seconds", 0), "parallel_run.coordination_seconds", errors)
    integration = number(parallel.get("integration_seconds", 0), "parallel_run.integration_seconds", errors)
    repair = number(parallel.get("repair_seconds", 0), "parallel_run.repair_seconds", errors)

    serial_tokens_raw = serial.get("total_tokens")
    parallel_tokens_raw = parallel.get("total_tokens")
    serial_tokens = None
    parallel_tokens = None
    if serial_tokens_raw is not None:
        serial_tokens = number(serial_tokens_raw, "serial_baseline.total_tokens", errors, positive=True)
    if parallel_tokens_raw is not None:
        parallel_tokens = number(parallel_tokens_raw, "parallel_run.total_tokens", errors, positive=True)

    min_speedup = number(thresholds.get("min_speedup", 1.0), "thresholds.min_speedup", errors, positive=True)
    max_token_ratio = number(thresholds.get("max_token_ratio", 999.0), "thresholds.max_token_ratio", errors, positive=True)

    speedup = serial_wall / parallel_wall if serial_wall > 0 and parallel_wall > 0 else 0.0
    parallel_efficiency = speedup / writers if writers > 0 else 0.0
    time_saved_pct = ((serial_wall - parallel_wall) / serial_wall * 100.0) if serial_wall > 0 else 0.0
    coordination_share = (coordination / parallel_wall) if parallel_wall > 0 else 0.0
    integration_share = (integration / parallel_wall) if parallel_wall > 0 else 0.0
    repair_share = (repair / parallel_wall) if parallel_wall > 0 else 0.0
    token_ratio = None
    if serial_tokens and parallel_tokens:
        token_ratio = parallel_tokens / serial_tokens

    serial_quality = serial.get("quality", {})
    parallel_quality = parallel.get("quality", {})
    if not isinstance(serial_quality, dict):
        errors.append("serial_baseline.quality must be an object")
        serial_quality = {}
    if not isinstance(parallel_quality, dict):
        errors.append("parallel_run.quality must be an object")
        parallel_quality = {}

    quality_ok, quality_failures, quality_notes = quality_check(
        serial_quality, parallel_quality, thresholds
    )

    speed_ok = speedup >= min_speedup
    token_ok = token_ratio is None or token_ratio <= max_token_ratio

    if not quality_ok and speedup > 1.0:
        decision = "FASTER_BUT_QUALITY_FAILED"
    elif quality_ok and speed_ok and token_ok:
        decision = "EFFICIENT_NON_INFERIOR"
    elif quality_ok and speed_ok and not token_ok:
        decision = "FASTER_QUALITY_OK_TOKEN_THRESHOLD_FAILED"
    elif quality_ok:
        decision = "QUALITY_OK_NOT_FASTER"
    else:
        decision = "QUALITY_FAILED"

    result = {
        "version": "codex-sol-luna-efficiency-score-v1",
        "decision": decision,
        "quality_non_inferior": quality_ok,
        "quality_failures": quality_failures,
        "quality_notes": quality_notes,
        "speedup": round(speedup, 4),
        "parallel_efficiency": round(parallel_efficiency, 4),
        "time_saved_percent": round(time_saved_pct, 2),
        "coordination_share": round(coordination_share, 4),
        "integration_share": round(integration_share, 4),
        "repair_share": round(repair_share, 4),
        "token_ratio": round(token_ratio, 4) if token_ratio is not None else None,
        "thresholds": {
            "min_speedup": min_speedup,
            "max_token_ratio": max_token_ratio,
        },
        "threshold_results": {
            "speed": speed_ok,
            "tokens": token_ok,
        },
    }
    return result, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("metrics", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    try:
        data = load_json(args.metrics)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    result, errors = score(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2

    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"WROTE: {args.output}")
    print(rendered)

    return 0 if result["quality_non_inferior"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
