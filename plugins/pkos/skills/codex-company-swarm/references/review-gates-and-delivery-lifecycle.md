# Review gates and delivery lifecycle v0.5

```text
Phase 0 durable coordination
-> G0 requirements/gap/path/Feature review
-> G1 organization/context/ownership/CI readiness
-> parallel development + test design + pipeline + coordination
-> G2 paired lane settlement
-> G3 single-owner integration + exact-candidate CI
-> G4 Review Board decision
-> G5 Director acceptance, canonical writeback, dashboard, retrospective
```

A Gate is an evidence-backed durable decision. It is not settled until the verdict event and dependent projections have verified receipts and a checkpoint.

## G0

Required artifacts:

- goal contract, normalized requirements, assumptions/exclusions, acceptance IDs;
- repository/current-state and requested-gap matrices;
- selected path and rejected alternatives/trade-offs;
- architecture/interface/data/security/deployment freeze list;
- Feature inventory with stable IDs, types, platforms, dependencies, risks, lane/pair, test strategy and PKOS owners;
- MFSQ and CI intent;
- staffing, ownership, dependency, integration and rollback plan;
- coordination readiness and verdict.

PK-01 projects Features `PLANNED -> ANALYZED`, registers evidence and confirms the verdict/checkpoint. No product implementation begins before durable `GO | GO_WITH_ACTIONS` and blocking actions have owners.

## G1

Blocking checks:

- independent lanes and frozen/versioned shared contracts;
- isolated worktrees/disjoint ownership;
- reciprocal developer/tester pairs;
- current generation/Director epoch/Pack and mandatory acknowledgements;
- settled Context Requests;
- Notion schema/mode/sync watermark and initial checkpoint;
- canonical environment/pipeline state and Jenkins bootstrap when needed;
- MFSQ ownership, Figma/design, security/data/migration/rollback;
- secrets/external actions/production authority;
- traceability plan.

PK-01 registers Session/Lane/Task records, projects Features to `READY`, and confirms G1/checkpoint. `GO_WITH_ACTIONS` is not ready until blocking actions close.

## G2 lane state

```text
PLANNED -> DEV_ACTIVE + TEST_DESIGN_ACTIVE -> DEV_HANDOFF_READY
-> TEST_PLAN_APPROVED -> TESTS_IMPLEMENTED -> PIPELINE_RUNNING
-> PASS | DEFECT_RETURN | BLOCKED_ENVIRONMENT | REPLAN_REQUIRED
```

Lane evidence includes developer/test commits, ownership, MFSQ, exact-candidate CI/reports, defects, risk, Pack/epoch and receipts. Green local commands are not pipeline acceptance. PK-01 confirms handoff, material defects, CI and verdict before settlement.

## G3

INT-01 receives only settled current run/generation/epoch/Pack artifacts. Integration order follows dependencies, not completion time. Verify cumulative paths/contracts/schema/data/migration, unchanged interactions, full pipeline, security/performance, deploy/rollback evidence, traceability, watermark and candidate checkpoint. Freeze one immutable candidate for G4.

## G4

RB-01 reviews one frozen candidate in one pass. Blocking findings state violated contract, reachable scenario/missing evidence, impact/severity, paths/commits/tests/stages, owner, retest and whether architecture stays frozen.

Verdicts:

- `ACCEPT`;
- `RETURN_TO_LANE`;
- `REPLAN_ORG`;
- `BLOCKED_EXTERNAL_BOUNDARY`.

PK-01 confirms verdict/findings/checkpoint. A return creates a new generation for affected lanes, invalidates named artifacts/Pack context and preserves independent accepted work. Three same-architecture repairs maximum.

## G5

TD-01 verifies:

- G4 ACCEPT for exact final candidate;
- exact-candidate canonical CI and no silently skipped tests;
- Security/performance thresholds or authorized residual risk;
- complete traceability and no open P0/P1/orphan evidence;
- Notion mode writable, schema ready, watermark current, no pending/dead-letter S2–S4 events;
- current Pack/epoch acknowledgements;
- Feature/current-truth/Audit/ADR/Incident/Memory writeback receipts;
- retained stable evidence/checksums;
- final checkpoint/resume token, dashboard and retrospective.

Code-complete but externally/coordination blocked work is a checkpoint, not accepted delivery.
