# PKOS memory and Notion integration

## Existing PKOS remains authoritative

Company Swarm introduces execution artifacts, not a second project-knowledge or memory system. Continue to use:

- Project Root Map and progressive disclosure;
- one Project Feature Registry;
- one canonical owner for every durable fact;
- Current Truth plus Audit/ADR/Incident separation;
- bounded Memory Context Compiler;
- Search Before Create;
- verified Notion writes or explicit pending writeback.

Read the shared PKOS references under `plugins/pkos/references/` rather than copying them into run artifacts.

## Shared Collaboration Pack

Before staffing, `TD-01` compiles one versioned pack containing only constraints every role must share:

- canonical Project/Memory Node IDs and source references;
- run ID, base revision, generation, and pack revision;
- user goal, explicit constraints, exclusions, authority boundaries;
- project architecture/feature pointers needed across lanes;
- environment aliases and CI provider;
- design/Figma prerequisites;
- organization command rules and Sol Max requirement;
- Notion write policy, memory sensitivity, security/deployment rules;
- unresolved conflicts and validity timestamp.

Each child receives:

```text
Shared Collaboration Pack
+ lane/role task packet
+ smallest task-scoped code/design/Notion context
```

Do not fork the complete Director transcript or recursively load Notion. Every result acknowledges the exact pack revision and cites canonical sources used.

## Long-term-memory loading

Use the existing gate:

```text
none | core | scoped | deep
```

Even in token-insensitive execution, long-term memory remains bounded because excess memory reduces precision and creates stale conflicts. “Ignore token cost” authorizes high reasoning and parallel staffing, not indiscriminate history ingestion.

## Feature Registry integration

G0 builds a run feature inventory, but it does not become a second durable feature ledger. Map every run feature to:

- existing `Feature ID`, or
- proposed new stable ID after Search Before Create.

During G5:

- update the canonical Project Feature Registry status, acceptance, platforms, implementation/test evidence, release, and verification date;
- create a `FEAT-*` detail node only when complexity requires it;
- update Capability/Domain pointer summaries when material;
- do not paste full run logs into Current Truth.

## Change classification and writeback

Classify final changes:

- C0 editorial;
- C1 state/progress;
- C2 contract/API/schema/behavior;
- C3 architecture/boundary/topology/security model;
- C4 canonical-structure change;
- C5 incident/security/data-loss/rollback.

Follow existing PKOS Audit/ADR gates. Company-wide organization artifacts may be episodic evidence, but only stable, reusable process changes become procedural memory.

## Memory write gate

Persist a collaboration memory only when it is likely to matter beyond this run, for example:

- stable project environment alias or CI provider;
- durable Figma/design prerequisite;
- recurring branch/worktree/deployment rule;
- approved MFSQ override;
- stable security/performance threshold;
- persistent user preference for Company Swarm defaults.

Do not store one-off session IDs, transient failures, raw logs, temporary branches, or speculative conclusions as durable memory.

## Notion capability behavior

When Notion is writable:

1. discover/search the correct nodes;
2. read the smallest relevant ranges;
3. update the smallest canonical owners;
4. verify each write response;
5. report exact nodes/rows changed;
6. record Audit/ADR/Incident evidence when required.

When read-only or unavailable:

- continue repository work when safe;
- write `.pkos/company-swarm/<run-id>/pkos-writeback.json` containing target nodes, intended changes, classification, evidence, and dependencies;
- mark `writeback_status=READ_ONLY|UNAVAILABLE|FAILED`;
- never claim Notion was updated.

## Conflict resolution

Code/config/runtime/design evidence may reveal that Notion is stale. Record the conflict, inspect authoritative evidence, let `RB-01` and `TD-01` establish current truth, then repair the canonical Notion owner. Never silently choose whichever source is most convenient.
