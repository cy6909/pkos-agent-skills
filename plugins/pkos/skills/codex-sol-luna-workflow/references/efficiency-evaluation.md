# Efficiency and non-inferiority evaluation

Use this reference to determine whether Sol/Luna routing or parallelism actually improved the user's workflow.

## Experiment rule

Compare the same task under comparable conditions:

- same repository base and initial dirty state;
- same specification and acceptance criteria;
- same tool/sandbox/test environment;
- same task boundaries;
- same model/effort except the variable being evaluated;
- no hidden manual help in only one arm.

A single anecdotal run is a smoke test, not a general conclusion.

## Baselines

At minimum record:

1. **Serial baseline:** one implementation lane at a time with the same quality gate.
2. **Parallel candidate:** disjoint lanes, isolated worktrees, integration barrier, same cumulative acceptance.
3. Optionally compare adaptive and max-pair routes separately.

## Time metrics

```text
T_serial = serial end-to-end wall time
T_parallel = parallel end-to-end wall time including setup, barrier, integration,
             repair, and final verification
Speedup = T_serial / T_parallel
Parallel efficiency = Speedup / writer_count
Time saved % = (T_serial - T_parallel) / T_serial * 100
Coordination share = coordination_seconds / T_parallel
```

Do not sum child durations and call that wall-clock. The user experiences end-to-end elapsed time.

## Resource metrics

Record when observable:

- input/output/reasoning/cached/total tokens;
- parent, worker, verifier, and reviewer tokens separately;
- subscription allowance consumption;
- API money using current prices, separately from token volume;
- context bytes or files transferred;
- child turns, retry calls, reviewer calls;
- repeated file reads and full-plan regenerations;
- p50 and p95 latency over repeated runs.

## Quality gate

Quality is non-inferior only when all hard invariants pass and the predeclared margins hold.

Hard failures:

- unresolved P0/P1 finding;
- acceptance or hidden-test failure;
- ownership violation;
- unrelated user change lost;
- stale generation integrated;
- role boundary failure;
- recovery/data-integrity/public-contract failure;
- unreviewed high-risk candidate.

Suggested soft comparisons:

- acceptance pass rate within 0 percentage points for deterministic tasks;
- hidden-test pass rate within a predeclared small margin for repeated corpora;
- repair rounds and human interventions no worse than the allowed margin;
- false-positive/reviewer noise within the allowed margin.

## Decision labels

- `EFFICIENT_NON_INFERIOR`: quality gate passes and speedup meets threshold.
- `QUALITY_OK_NOT_FASTER`: quality passes but speedup does not.
- `FASTER_BUT_QUALITY_FAILED`: never adopt.
- `TOKEN_SAVING_NON_INFERIOR`: quality passes and the user's chosen consumption meter improves.
- `INCONCLUSIVE`: missing baseline, small sample, unstable runtime, or unobserved metrics.

## Metrics JSON

```json
{
  "version": "codex-sol-luna-metrics-v1",
  "serial_baseline": {
    "wall_seconds": 850,
    "total_tokens": 100000,
    "quality": {
      "acceptance_pass_rate": 1.0,
      "hidden_test_pass_rate": 1.0,
      "p0_p1_findings": 0,
      "ownership_violations": 0,
      "unresolved_blockers": 0,
      "human_interventions": 0
    }
  },
  "parallel_run": {
    "wall_seconds": 550,
    "writer_count": 2,
    "coordination_seconds": 45,
    "integration_seconds": 80,
    "repair_seconds": 0,
    "total_tokens": 115000,
    "quality": {
      "acceptance_pass_rate": 1.0,
      "hidden_test_pass_rate": 1.0,
      "p0_p1_findings": 0,
      "ownership_violations": 0,
      "unresolved_blockers": 0,
      "human_interventions": 0
    }
  },
  "thresholds": {
    "min_speedup": 1.2,
    "max_token_ratio": 1.3,
    "quality_margin": 0.0,
    "max_extra_human_interventions": 0
  }
}
```

Run:

```bash
python scripts/score_efficiency.py metrics.json
```

## Repeated evaluation

For decisions beyond one repository task:

- use real feature slices and reversed real bug-fix commits;
- include clean diffs for false positives;
- blind review outputs when practical;
- repeat key cells multiple times, preferably at least five;
- report medians and tails;
- separate detection from assertion for reviewers;
- preserve raw run artifacts and exact model/effort/date/version metadata.
