# Event sync, outbox, receipts, and replay

## Event envelope

Every material transition is first written locally as a structured event:

```json
{
  "seq": 42,
  "state_version": 42,
  "event_id": "EV-042",
  "idempotency_key": "run-123:EV-042",
  "run_id": "run-123",
  "generation": 2,
  "director_epoch": 3,
  "event_type": "DEV_HANDOFF",
  "actor_session_id": "D-BE-01",
  "occurred_at": "...",
  "gate": "G2",
  "subject_id": "LANE:backend",
  "previous_state": "IN_DEVELOPMENT",
  "new_state": "DEV_HANDOFF",
  "summary": "Committed candidate handed to paired tester.",
  "evidence_ids": ["E-COMMIT-17"],
  "source_artifact_path": "...",
  "source_artifact_hash": "sha256:...",
  "payload": {}
}
```

Sequence and state version are monotonic. Event IDs and idempotency keys are unique. Epoch may change only through a valid `TAKEOVER` event. Generation never decreases.

## Sync classes

- `S0 EPHEMERAL`: thoughts, ordinary command output, micro-edits; do not sync.
- `S1 PROGRESS`: non-critical progress; coalesce into a checkpoint/status projection.
- `S2 CONTROL`: Session/Lane/Task/Pack/context/handoff/defect/CI/candidate transitions; sync before dependent work.
- `S3 GATE`: G0/G1/G4/G5 verdicts and return/replan/block; sync before Gate settles.
- `S4 GOVERNANCE`: Feature/current-truth/ADR/Audit/Incident/Memory writeback; sync before accepted completion.

A failed S2–S4 event blocks its dependent barrier. Do not continue merely because the chat message was delivered.

## Transactional outbox discipline

1. TD-01 authorizes the event and expected projection change.
2. PK-01 writes the event and outbox record under `.pkos/.../coordination/` before the external mutation.
3. PK-01 uses the stable idempotency key for the Notion write.
4. PK-01 reads back or otherwise verifies the exact row/page and revision.
5. PK-01 stores a receipt with observed ID/revision/time.
6. Event sync status becomes `CONFIRMED`.
7. Watermark advances only through the highest contiguous confirmed sequence.
8. Current projections update from confirmed events.
9. A checkpoint captures event/state version, watermark, Pack, epoch, and checksums.

This is an application-level protocol, not a claim that Notion provides a distributed transaction.

## Outbox record

```json
{
  "event_id": "EV-042",
  "idempotency_key": "run-123:EV-042",
  "event_seq": 42,
  "target": "FEATURE_REGISTRY",
  "operation": "UPDATE",
  "status": "PENDING | CONFIRMED | DEAD_LETTER",
  "attempts": 1,
  "payload_hash": "sha256:...",
  "receipt_id": null
}
```

Targets include `SWARM_REGISTRY`, `EVENT_LEDGER`, `EVIDENCE_REGISTRY`, `FEATURE_REGISTRY`, and approved canonical PKOS nodes. Operations include `APPEND`, `CREATE`, `UPDATE`, and `SUPERSEDE`.

## Receipt

A confirmed receipt records:

```text
Receipt ID | Event ID | Idempotency Key | Target | Operation
Observed Record ID | Observed Revision | Verified | Verified At
```

A tool call returning without an error is not enough when the connector exposes read-back verification. Never fabricate a revision or URL.

## Retry and dead-letter

Retry only idempotently. Preserve the original event and payload hash. Classify failures:

- transient transport/rate/concurrency failure — bounded retry;
- schema mismatch — stop, repair/rebind schema, then replay;
- permission/read-only — keep pending and block required Gate;
- stale expected state — record conflict and replan; do not overwrite;
- permanent invalid payload — dead-letter with reason and owner.

Do not delete failed events. A superseding event can correct semantics while preserving history.

## Replay

On resume:

1. load the latest valid checkpoint;
2. verify checksums and event/state sequence;
3. list outbox events above the confirmed watermark;
4. inspect existing receipts/Notion rows by idempotency key;
5. mark already-applied entries confirmed rather than duplicating them;
6. replay only truly unapplied valid entries in sequence;
7. rebuild projections and validate the bundle;
8. issue a new checkpoint.

## Required material events

At minimum record:

```text
RUN_CREATED / RUN_BLOCKED / RUN_ACCEPTED
SESSION_PROVISIONED / ACKNOWLEDGED / BLOCKED / REPLACED / RETIRED
LANE_STARTED / HANDED_OFF / RETURNED / SETTLED
CONTEXT_REQUESTED / SUPPLIED / BLOCKED
PACK_SUPERSEDED / ACKNOWLEDGED
FEATURE_STATE_CHANGED
DEV_HANDOFF / TEST_PLAN_APPROVED
DEFECT_OPENED / CLOSED
CI_STARTED / COMPLETED
EVIDENCE_REGISTERED
CANDIDATE_FROZEN
GATE_VERDICT
CHECKPOINT_CREATED
TAKEOVER
PKOS_WRITEBACK_CONFIRMED
RETROSPECTIVE_RECORDED
```

Missing evidence is recorded as missing, never reconstructed from conversational memory.
