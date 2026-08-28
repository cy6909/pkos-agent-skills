# Review gates and delivery lifecycle

## Lifecycle overview

```text
G0 Intake and gap review
  -> G1 Organization / interface / CI readiness
    -> parallel product implementation + test design + pipeline work
      -> G2 paired developer-to-tester settlement per lane
        -> G3 single-owner cumulative integration + full pipeline
          -> G4 Review Board acceptance or return
            -> G5 Technical Director decision, dashboard, PKOS writeback
```

A gate is a durable decision with evidence, not an informal progress update.

## G0 — Intake and gap review

Required artifacts:

- goal contract;
- requirement normalization and assumption register;
- repository/current-state map;
- requested-versus-current gap matrix;
- selected implementation path and rejected alternatives;
- architecture/interface/security/deployment freeze list;
- feature inventory;
- domain and platform impact matrix;
- initial MFSQ strategy;
- staffing and dependency proposal;
- verdict.

The feature inventory must distinguish at least:

| Type | Meaning |
|---|---|
| implement | new user/system behavior |
| modify | change existing behavior or contract |
| optimize | improve maintainability, UX, or internal efficiency without intended contract change |
| performance | latency, throughput, startup, memory, storage, battery, cost, or capacity target |
| security | explicit security control, remediation, threat mitigation, or compliance work |
| migration | schema/data/API/config/runtime transition |
| operations | deployment, monitoring, incident readiness, rollback, runbooks |
| documentation | durable operator/developer/product knowledge |

Each feature has stable ID, acceptance IDs, owner lane, platforms, dependencies, risk, test strategy, and PKOS owner pointer.

## G1 — Readiness

Blocking checks:

- all lanes are independently implementable;
- shared contracts are frozen or versioned;
- every writer has an isolated worktree and disjoint write allowlist;
- every development lane has a reciprocal paired tester;
- memory-pack revision and task packets are acknowledged;
- canonical environment and pipeline status are known;
- missing CI has a blocking bootstrap lane;
- MFSQ plan ownership is assigned;
- secrets/external actions/production writes are authorized;
- design evidence is available where required;
- rollback and migration sequencing are defined.

`GO_WITH_ACTIONS` from G0 is not G1 pass until every blocking action is closed.

## G2 — Lane settlement

Per-lane state:

```text
PLANNED
  -> DEV_ACTIVE + TEST_DESIGN_ACTIVE
  -> DEV_HANDOFF_READY
  -> TEST_PLAN_APPROVED
  -> TESTS_IMPLEMENTED
  -> PIPELINE_RUNNING
  -> PASS | DEFECT_RETURN | BLOCKED_ENVIRONMENT | REPLAN_REQUIRED
```

Lane evidence includes developer commit, test commit, ownership validation, MFSQ matrix, CI run, results, defects, and risk. A green local command is not a pipeline pass.

## G3 — Integration

The Integration Owner receives only settled lane artifacts. Integration order follows the frozen dependency graph, not completion time.

Required checks:

- active generation only;
- exact lane commits and test commits;
- cumulative diff and path ownership;
- API/schema/data/migration compatibility;
- cross-lane tests and unchanged-code interactions;
- full canonical pipeline;
- security and performance aggregate evidence;
- deploy/rollback/test-environment evidence when applicable;
- artifact provenance.

The integration candidate becomes immutable for G4. Any change after freeze creates a new candidate revision and invalidates stale review evidence.

## G4 — Review Board

The Chair performs one complete review. Findings are grouped by severity:

- `P0`: exploitable security/data-loss/unsafe production behavior or objective failure of a critical requirement;
- `P1`: material functional, integration, migration, reliability, or performance failure;
- `P2`: non-blocking robustness/maintainability/observability problem with evidence;
- `P3`: optional hardening or preference.

Only evidence-backed findings may block. Each blocking finding states:

- violated acceptance/contract/standard;
- concrete reachable scenario or missing evidence;
- impact and severity;
- affected paths/commits/tests/pipeline stages;
- owner lane;
- required retest scope;
- whether architecture remains frozen.

The Chair returns all current findings in one pass rather than drip-feeding avoidable rounds.

## Repair generations

`RETURN_TO_LANE` creates a new run generation for affected lanes while preserving accepted independent work. Results from previous generations remain evidence but do not settle the new candidate.

Maximum same-architecture repairs: three. The next failure triggers `REPLAN_ORG` because repeated repair usually signals an incorrect requirement, boundary, ownership, architecture, or test strategy.

## G5 — Completion

The Director checks that:

- Chair verdict is `ACCEPT` for the exact final candidate;
- pipeline result belongs to the exact final commit;
- no required test is unrun or silently skipped;
- security/performance thresholds are satisfied or explicitly accepted as residual risk by authorized user policy;
- no production/deployment/Notion action is overstated;
- PKOS Feature Registry, Current Truth, Audit, ADR, Incident, and Memory obligations are settled or listed as pending;
- user dashboard is generated from evidence.

A code-complete but externally blocked result is a checkpoint, not accepted delivery.
