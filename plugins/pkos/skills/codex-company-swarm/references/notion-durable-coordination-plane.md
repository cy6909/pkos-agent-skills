# Notion Durable Coordination Plane

## Purpose

Company Swarm uses Notion as a durable, human-inspectable coordination control plane across Codex sessions. It is not the high-frequency message bus and it does not replace Git, CI, Figma, or PKOS canonical product truth.

```text
Codex messages                  immediate commands and replies
.pkos coordination artifacts   write-ahead log, outbox, receipts, checkpoints
Git / CI / reports / Figma      executable and visual evidence
Notion coordination plane      current run projection, event history, evidence pointers
PKOS canonical nodes           durable project truth and long-term memory
```

Notion contains compact semantic state and stable evidence pointers. Never paste raw logs, complete transcripts, large diffs, binaries, secrets, or volatile runtime output into it.

## Minimal schema

Reuse existing databases when their semantic contract is compatible. Search Before Create and record stable IDs/bindings in `notion-schema.json`.

### Swarm Run & Lane Registry

One database stores typed current projections using `Record Type = Run | Lane | Session | Task`.

Required semantics:

```text
Record ID | Record Type | Project ID | Run ID | Generation
Director Epoch | State Version | Parent Record | Feature IDs
Current Gate | Current State | Owner Session | Paired Session
Pack Revision | Base Commit | Head Commit | Candidate Revision
Blocked By | Last Event | Evidence | Last Verified
Resume Token | Sync Status
```

This is a current-state projection, not an append-only history.

### Event & Decision Ledger

Append-only semantic history:

```text
Event ID | Sequence | Idempotency Key | Project ID | Run ID
Generation | Director Epoch | State Version | Actor Session
Event Type | Gate | Subject ID | Previous State | New State
Summary | Evidence | Occurred At | Verification | Supersedes
```

Do not rewrite prior events except to correct an explicitly identified invalid record through a superseding event.

### Evidence Registry

Stable pointers and integrity metadata:

```text
Evidence ID | Type | Project ID | Run ID | Generation
Feature IDs | Lane ID | Candidate Commit | Produced By | Verified By
URI | Checksum | Summary | Created At | Retention | Status | Supersedes
```

Evidence bodies remain in Git, CI, artifact storage, design tools, or canonical Notion pages.

### Existing Project Feature Registry extension

Do not create another Feature ledger. Extend the existing single Project Feature Registry with:

```text
Current Run | Current Lane | Development Status | Test Status
CI Status | Review Status | Accepted Candidate | Open Defects
Evidence | Last Event | Last Verified
```

History belongs in the Event Ledger. Product behavior and durable acceptance remain in the Feature canonical owner.

## Capability modes

- `DIRECT_WRITABLE`: PK-01 can search/read/create/update/query and verify writes.
- `DIRECT_READ_ONLY`: PK-01 can read but cannot mutate; outbox remains pending.
- `BROKERED`: another explicitly available Notion-capable adapter performs verified writes for PK-01.
- `UNAVAILABLE`: no current Notion access.

A mode is observed/configured evidence, not inferred from a role name.

Full `COMPANY_SWARM_ACCEPTED` requires writable coordination, schema `READY`, sync `IN_SYNC`, and verified canonical writeback. Read-only/unavailable runs may reach a durable repository checkpoint but return `BLOCKED_NOTION_COORDINATION` or another honest blocked/checkpoint status.

## Single writer

PK-01 is the only logical writer to coordination projections and ledgers. Other roles produce structured event/evidence candidates through TD-01. This prevents duplicate rows, conflicting lifecycle transitions, and uncontrolled schema creation.

TD-01 authorizes state changes and event order. PK-01 does not invent decisions. RB-01 decides Gate verdicts. Domain/test/CI roles own their evidence claims. PK-01 records only authorized, evidence-backed transitions.

## Feature lifecycle projection

Recommended current projection:

```text
PLANNED -> ANALYZED -> READY -> IN_DEVELOPMENT -> DEV_HANDOFF
-> IN_TEST -> TEST_PASSED | DEFECT_RETURN | BLOCKED
-> INTEGRATING -> IN_REVIEW -> ACCEPTED | DEFERRED
```

Every transition includes Feature ID, lane, event sequence, generation, epoch, Pack, evidence, verifier, and Last Verified. Coalesce insignificant progress; never hide material handoffs, defects, CI outcomes, candidate freezes, or Gate decisions.

## Information refinement

Keep four layers separate:

1. **Current projection** — small, immediately useful status.
2. **Event/Audit/ADR/Incident** — why and how state changed.
3. **Evidence pointers** — exact artifacts and integrity metadata.
4. **Canonical product/memory truth** — stable facts and reusable knowledge.

Maps and projections route; canonical nodes own facts; evidence proves them. This preserves brevity without losing traceability.

## Bootstrap and binding

PK-01 must:

1. Find Project Root, Feature Registry, and existing candidate databases by stable IDs, aliases, or semantics.
2. Read only schemas and minimal representative rows.
3. Validate required semantics and record bindings.
4. Create only missing compatible structures when authorized.
5. Write a Run record and `RUN_CREATED` event through the outbox.
6. Read back the affected records and store receipts.
7. Record schema version/state and coordination mode.
8. Checkpoint the binding state.

Never call a merely proposed schema `READY`, and never call a write `CONFIRMED` without a verified response.

## Source-of-truth conflict

Notion is the durable control plane; code/config/runtime/design/CI are verification evidence. When they disagree:

1. record a conflict event;
2. freeze the affected transition when material;
3. inspect authoritative evidence;
4. let TD-01/RB-01 establish the current truth;
5. repair the correct canonical owner/projection;
6. retain the decision/evidence trail.

Do not silently choose the convenient source.
