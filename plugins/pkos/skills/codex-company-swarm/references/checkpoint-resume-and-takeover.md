# Checkpoint, resume, and Technical Director takeover

## Checkpoint purpose

A checkpoint is a checksummed recovery boundary, not a progress paragraph. It allows a new runtime to reconstruct the run without relying on the former chat transcript.

Create checkpoints:

- after Phase 0 coordination bootstrap;
- after G0 and G1;
- after meaningful handoff batches;
- at candidate freeze;
- after every G4 verdict/return/replan/block;
- before and after Director takeover;
- at G5 completion or durable block.

## Required checkpoint state

```text
Project/Run/Checkpoint/previous checkpoint
created at | generation | event seq | state version
Director logical role/runtime/epoch
current Gate | Pack revision
Notion run record | sync watermark | pending outbox IDs
active candidate revision/commit/status
Session and Lane projections
artifact manifest with sha256 and required-for-resume flag
resume token | takeover record | verifiers
```

A checkpoint is valid only when required artifacts exist, checksums are valid, Pack/epoch are current, and event/state/watermark relationships are coherent.

## Resume without takeover

Use when the same logical and observable Director runtime continues:

1. load the latest valid checkpoint;
2. verify manifest checksums;
3. verify the Notion Run record, epoch, Pack and watermark;
4. replay outbox above the watermark idempotently;
5. rebuild current projections and traceability;
6. inspect child runtime/worktree state;
7. reuse only compatible clean sessions;
8. reissue stale/incomplete packets;
9. validate the bundle and write a new checkpoint.

## Authorized takeover

A replacement runtime may assume logical TD-01 only with observable authority from the user/runtime policy or an explicit durable takeover protocol. Do not infer takeover authority because an old chat appears inactive.

Takeover procedure:

1. load and verify the last checkpoint and Notion Run record;
2. determine the active epoch and former runtime identity;
3. append `TAKEOVER` with previous/new consecutive epoch, reason, authority, and stale runtime refs;
4. PK-01 writes/verifies the event and updates the Run projection;
5. increment `director_epoch` exactly one;
6. mark former runtime/session assignments stale or superseded;
7. reissue every active child packet with the new epoch, current generation and Pack;
8. reject late old-epoch results from current state while preserving them as history;
9. replay pending outbox, rebuild projections/traceability, validate, and checkpoint.

This protocol reduces split-brain risk but is not a claim of a transactional distributed lock. When the runtime cannot prove exclusive takeover, stop with `BLOCKED_RUNTIME` or `BLOCKED_EXTERNAL_BOUNDARY`.

## Resume plan

`build_resume_plan.py` returns:

- source checkpoint and resume token;
- current/target Director epoch;
- takeover required;
- reusable sessions;
- sessions requiring packet reissue;
- pending outbox replay;
- artifact verification and validation commands;
- next permitted barrier.

Under takeover, no existing child packet is current until reissued with the new epoch.

## Retention

Keep the latest checkpoint, Gate checkpoints, takeover checkpoints, accepted/final blocked checkpoint, and the manifest/checksum records necessary to resolve evidence. Superseded high-frequency checkpoints may be compacted after a later checkpoint is verified, while append-only events and required evidence pointers remain.
