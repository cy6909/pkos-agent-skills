# End-to-end traceability, retention, and retrospective

## Traceability graph

Every accepted requirement must remain connected through implementation, verification, review and canonical writeback:

```text
Requirement -> Feature -> Acceptance -> Lane/Task Packet
-> Product Commit -> MFSQ Test Case/Test Commit
-> exact-candidate CI Run/Reports
-> Security/Performance Evidence -> G4 Verdict
-> Notion Canonical Owner/verified write receipt
```

Required invariants:

- every Requirement maps to one or more stable Features;
- every Feature has Acceptance IDs, owner lane and PKOS owner pointer;
- every Acceptance maps to product commits and tests;
- every executable test has M/F/S/Q axis, automation path, test commit, pipeline stage and CI run;
- behavior changes have Security and Q/performance coverage or RB-approved explicit exceptions;
- CI evidence targets the exact frozen candidate;
- all blocking findings are closed or the run is blocked;
- G4 verdict targets the same candidate;
- every durable accepted change has confirmed canonical Notion writeback;
- no required evidence is orphaned or silently skipped.

A Feature marked `NO_DURABLE_WRITEBACK` must provide a justified non-durable classification; accepted C2+ changes cannot use it.

## Evidence retention

Notion stores compact pointers, summaries, checksum, producer/verifier, candidate and retention class. Evidence bodies stay in stable systems.

Recommended classes:

- `RUN`: retain through active run and immediate review;
- `RELEASE`: retain while the release/feature is supported;
- `AUDIT`: retain according to governance/security policy;
- `EPHEMERAL`: discard after a verified checkpoint/compaction when not required for traceability.

Before deleting a worktree or temporary artifact, verify that commits, reports, receipts, manifest and stable evidence pointers exist. A deleted local path must not be the only evidence URI.

## Retrospective

At G5 or a terminal block, produce a compact evidence-backed retrospective:

```text
planned vs actual scope and architecture
Feature/lane first-pass and repair outcomes
defect discovery stage and escape prevention
coordination/barrier/outbox/context delay
CI/environment failures
security/performance baseline and candidate change
which assumptions or evidence were weak
which Pack/organization decisions changed
parallelism benefit and integration cost
specific prevention/actions, owners and due conditions
```

Do not turn the retrospective into a full transcript.

## Compilation to durable knowledge

Separate:

- Current Truth — current valid product/project state;
- Event/Audit — what changed and evidence;
- ADR — why a durable trade-off was selected;
- Incident — impact, timeline, root cause, recovery, prevention;
- Episode/Retrospective — run-specific learning;
- Procedural Memory — only stable reusable collaboration rules.

A lesson becomes procedural Memory only when it has future reuse value, appropriate scope, evidence/confidence, and no duplicate/conflicting active memory. Transient Session IDs, raw logs, temporary branches and speculative inference do not become long-term memory.

## Gate

`validate_traceability.py` and `validate_coordination_bundle.py` must pass before `COMPANY_SWARM_ACCEPTED`. The dashboard reports broken links, orphan evidence, unrun tests, writeback status and residual risks rather than hiding them.
