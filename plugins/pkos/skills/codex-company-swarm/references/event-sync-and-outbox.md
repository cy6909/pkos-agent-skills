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

## Local event classes and gate projection

- `S0 EPHEMERAL`: thoughts, ordinary command output, micro-edits; do not sync.
- `S1 PROGRESS`: non-critical progress; coalesce into a local checkpoint.
- `S2 CONTROL`: Session/Lane/Task/Pack/context/handoff/defect/CI/candidate transitions; retain locally and include in the next applicable gate batch.
- `S3 GATE`: requirement freeze, lane handoff, candidate freeze, strict-review terminal, and deployment/acceptance terminal; project the coalesced delta before the Gate settles.
- `S4 GOVERNANCE`: Feature/current-truth/ADR/Audit/Incident/Memory writeback; include in the same authorized gate batch before accepted completion.

A failed local event write blocks its dependent work. A failed S3/S4 Notion gate batch blocks Gate settlement. Do not create a Notion write for every S1/S2 event.

## Transactional outbox discipline

1. TD-01 appends material local events and coalesces the pending semantic delta.
2. At one of the five write points, PK-01 creates one idempotent outbox batch under `.pkos/.../coordination/`.
3. PK-01 updates the original Product Feature Registry and approved canonical nodes in accurate Chinese.
4. PK-01 reads back the exact row/page and revision and stores the receipt.
5. The gate-batch watermark advances only through the highest contiguous confirmed batch.
6. A checkpoint captures local event/state version, batch watermark, Pack, epoch, and checksums.

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
