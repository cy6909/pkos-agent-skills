# PKOS Memory Protocol Reference

## Principle

**Memory storage is unbounded; memory context is bounded. Never load memory proportional to total stored memory.**

Notion can hold a growing Memory Registry and evidence history. Every task receives a bounded, compiled working set.

## Address space

```text
Memory Protocol
  ↓
Memory Root Map
  ├── Core Profile
  ├── Preferences
  ├── Goals & Constraints
  ├── Work & Projects
  ├── Learning
  ├── Procedural Collaboration
  ├── Relationships / People
  └── Episodic / Evidence
       ↓
Memory Registry
       ↓
MEM-* Canonical Memory / Episodes
```

## Memory types

- `profile-semantic`: stable facts/preferences/context.
- `goal-state`: active goals or state with temporal validity.
- `procedural`: reusable collaboration/workflow rules.
- `episodic`: important event/decision/result evidence; generally not always-on.

## Memory fields

Recommended registry semantics:

`Memory ID | Type | Subject | Scope | Summary | Status | Confidence | Salience | Always On | Valid From | Valid Until | Last Verified | Sensitivity | Source Episode | Canonical Node | Supersedes | Last Accessed | Access Count | Last Useful | Utility | Decay Policy`

Statuses: `active | needs-review | hypothesis | superseded | deleted`.

Decay: `stable | dynamic | ephemeral`.

## Context compiler

```text
Task
 ↓
Need-Memory Gate: none | core | scoped | deep
 ↓
Scope Filter
 ↓
Status + Temporal + Sensitivity Filter
 ↓
Subject / Type / alias
 ↓
Semantic / Keyword / Relation Retrieval
 ↓
Relevance + Scope Match + Temporal Validity + Confidence + Salience + Utility
 ↓
Dedup / Conflict Resolution
 ↓
Token Budget Packing
 ↓
Memory Pack
```

Default budget guidance:

- M1 Core: 500–1000, hard cap ~1200 tokens.
- M2 Domain/Pointer: 300–800.
- M3 Retrieved memory: 800–2000.
- M4 Evidence: 0 by default.
- Ordinary total long-term-memory context: ~1500–2500.

Budget is task-dependent but never storage-size-dependent.

## Write gate

Persist only when at least one applies:

- user explicitly asks to remember;
- stable/repeated preference with future reuse value;
- persistent goal, constraint, environment, or collaboration rule;
- important event/decision likely needed for future context.

Do not persist casual chat, one-off details, low-value logs, or unverified inference as confirmed user truth.

## Write pipeline

`candidate -> salience -> sensitivity -> search/dedupe -> contradiction -> ADD/UPDATE/SUPERSEDE/DELETE/IGNORE -> temporal validity -> provenance -> Core refresh if warranted -> audit`

## Compaction

Near-duplicate current memories may consolidate into one higher-level canonical memory. Old active entries become superseded. Preserve source episodes/evidence for provenance.

## GC / lint

Check duplicate, superseded, expired, stale, low-utility, orphan, over-specific, contradictory, unsupported-sensitive, and forgotten-data residue.

GC optimizes retrieval precision, not storage size.
