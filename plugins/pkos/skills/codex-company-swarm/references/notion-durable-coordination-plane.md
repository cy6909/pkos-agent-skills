# Notion Durable Coordination Plane

## Purpose

Notion is the durable, human-readable control plane across sessions, not the message bus and not a replacement for Git, CI, Figma or PKOS canonical truth.

```text
Codex messages                immediate transport
.pkos artifacts              WAL/outbox/receipts/checkpoints
Git/CI/Figma                 executable/visual evidence
Notion                       run projection, history, evidence pointers
PKOS nodes                   canonical project truth and memory
```

Store compact semantic state and stable pointers, never raw logs, transcripts, large diffs, binaries, secrets or volatile output. Human text follows `NOTION_WRITE_LANGUAGE=zh-CN`; preserve machine IDs/enums/paths/hashes.

## Minimal schema

Search Before Create; reuse compatible databases and persist bindings in `notion-schema.json`.

### Swarm Run & Lane Registry

Current projections with `Record Type = Run | Lane | Session | Task`:

```text
Record/Project/Run IDs | Generation | Director Epoch | State Version
Parent | Feature IDs | Gate/State | Owner/Pair | Pack Revision
Base/Head/Candidate | Blocked By | Last Event/Evidence/Verified
Resume Token | Sync Status
```

### Event & Decision Ledger

Append-only history:

```text
Event ID/Sequence/Idempotency Key | Project/Run/Generation/Epoch/Version
Actor | Type/Gate/Subject | Previous/New State | Summary/Evidence
Occurred At | Verification | Supersedes
```

Correct invalid history with a superseding event; do not rewrite it.

### Evidence Registry

```text
Evidence ID/Type | Project/Run/Generation | Feature/Lane/Candidate
Produced/Verified By | URI/Checksum/Summary | Created/Retention/Status/Supersedes
```

Bodies remain in Git, CI, artifact storage, design tools or canonical pages.

### Canonical Feature and normalized views

Never create a second Feature ledger or turn the Feature Registry into a test monolith. Extend its current projection with Run/Lane, development/test/CI/review status, accepted candidate, defects, evidence, last event and verification.

Bind compatible project registries/views for:

```text
Requirement
Frontend / Backend / Mobile / Data Implementation Unit
Dependency
Atomic Acceptance
Test Design
MFSQ Test Case
```

They relate to the canonical Feature owner. A Feature may have several platform units; a unit may depend on several providers; an Acceptance may have several cases.

Git `pkos-mfsq/v2` is the machine contract. Notion stores Chinese summaries, relations and evidence pointers. Each case page includes axis/type/side, requirement/feature/unit/acceptance relations, pipeline stage/evidence, and `步骤序号 / 操作 / 预期结果`. Unit cases add test/code symbols, purpose and rationale. Test Design links versioned visual and textual references, checksum and approval.

## Capability and authority

- `DIRECT_WRITABLE`: PK-01 can read/write and verify.
- `DIRECT_READ_ONLY`: reads only; outbox stays pending.
- `BROKERED`: an explicit adapter performs verified writes for PK-01.
- `UNAVAILABLE`: no access.

Full acceptance requires writable coordination, schema `READY`, `IN_SYNC` and verified canonical writeback. Otherwise checkpoint with an honest blocked status.

PK-01 is the sole logical writer. Roles emit structured candidates through TD-01. TD-01 authorizes order/state; RB-01 decides Gates; evidence owners own their claims. PK-01 records only authorized evidence.

## Lifecycle and refinement

```text
PLANNED -> ANALYZED -> READY -> IN_DEVELOPMENT -> DEV_HANDOFF
-> IN_TEST -> TEST_PASSED | DEFECT_RETURN | BLOCKED
-> INTEGRATING -> IN_REVIEW -> ACCEPTED | DEFERRED
```

Transitions carry Feature/lane, sequence, generation, epoch, Pack, evidence, verifier and Last Verified. Keep four layers separate:

1. small current projection;
2. Event/Audit/ADR/Incident reasoning;
3. exact evidence pointers;
4. canonical product/memory truth.

## Bootstrap

PK-01:

1. finds Project Root, Feature Registry and candidates by stable identity/semantics;
2. reads minimal schemas/rows and validates bindings;
3. creates only missing authorized compatible structures;
4. writes `RUN_CREATED` through outbox;
5. reads back records and stores receipts;
6. records schema/mode/watermark and checkpoints.

Never call a proposal `READY` or an unverified write `CONFIRMED`.

## Conflict

When Notion and code/config/runtime/design/CI disagree: record conflict; freeze material transitions; inspect authoritative evidence; let TD-01/RB-01 establish truth; repair the correct owner/projection; retain the trail. Never silently choose convenience.
