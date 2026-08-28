# Context brokerage and Shared Pack versioning

## Goal

Every role must receive enough current context to perform its bounded responsibility without copying the Director transcript or recursively reading Notion. Context is versioned evidence, not informal memory.

## Shared Collaboration Pack

The Pack contains only constraints every relevant session must share:

- canonical Project/Memory source IDs and revisions;
- user goal, exclusions, acceptance and authority boundaries;
- architecture, interfaces, schema and security rules;
- Feature/PKOS owner pointers;
- environment, CI, Figma/design, migration and deployment constraints;
- organization/ownership/evidence rules;
- current run, generation, Director epoch, Pack revision and validity time;
- unresolved conflicts.

It excludes full history, secrets, raw logs, large source files, and unrelated personal memory.

## Context modes

### DIRECT_VERIFIED

The session directly reads the named canonical sources and returns source IDs/revisions/Last Verified. Use when direct Notion capability is available and required.

### BROKERED_SNAPSHOT

PK-01 or TD-01 compiles the smallest task-specific snapshot plus Source Manifest and hash. The child acknowledges the snapshot but must not claim direct Notion verification.

### BLOCKED_CONTEXT_FRESHNESS

Use when the task depends on a current contract/security/data/authority fact and neither direct verification nor a sufficiently fresh signed snapshot is available. The lane stops rather than guessing from old chat.

## Context Request

A role emits:

```text
request_id | run/generation/epoch/Pack | requester
missing fact/question | reason | urgency/barrier
suggested source IDs | sensitivity | response artifact
```

PK-01 searches canonical sources, supplies only the relevant ranges/evidence, records mode/revisions/hash, and emits `CONTEXT_SUPPLIED` or `CONTEXT_BLOCKED`.

## Pack Delta

When shared facts change, create an immutable delta:

```text
from_revision | to_revision | reason | created_by/at
source changes: node, old/new revision, C0-C5, summary
affected sessions/lanes | invalidated artifacts
mandatory_reload | requires_new_generation | compatibility_preserved
acknowledgement barrier | supersedes
```

C2–C5 changes ordinarily require a new generation unless compatibility is explicitly preserved with evidence. C0–C1 changes may avoid invalidation when behavior/contracts are unaffected.

Examples requiring a Delta:

- requirement/acceptance change;
- API/event/schema/data contract change;
- architecture/security boundary change;
- environment/CI/Figma/deployment/rollback change;
- MFSQ interpretation or threshold change;
- user authority or external-action boundary change.

## Reload barrier

1. Freeze affected handoffs/Gates.
2. Publish the delta and source manifest.
3. Invalidate named task/test/review/candidate artifacts.
4. Reissue packets with current generation/epoch/Pack.
5. Require acknowledgements from all affected sessions.
6. Reject results produced from invalidated revisions.
7. Release the barrier only after validation and confirmed Pack events.

Acknowledgement records mode, verified refs or snapshot hash, status, and timestamp. Silence is not acknowledgement.

## Context precision

Use progressive disclosure:

```text
Root/Pack pointer -> 1–3 relevant Domain/Capability maps
-> exact canonical details -> raw evidence only when needed
```

Stop when the current working set is sufficient for the next action. Token-insensitive execution permits more reasoning and parallelism, not indiscriminate stale context.
