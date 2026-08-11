# PKOS Project Protocol Reference

Load this reference when a task needs the detailed project-knowledge rules rather than only a skill workflow.

## Address-space model

- Protocol: stable cross-project rules.
- Root Map: the project's unique entry point and L1 routing cache.
- Domain/Capability Map: second-level routing pages.
- Pointer: stable Node ID + destination + short purpose/summary + READ WHEN + SKIP WHEN + freshness.
- Canonical Node: unique owner of a durable fact.
- Evidence: raw sources used for verification.

A pointer is not a second copy of the body. Maps route; nodes own facts.

## Progressive disclosure

- L0 Protocol.
- L1 Root Map, target 800–1500 tokens.
- L2 Domain/Capability maps, target 500–1200 tokens each.
- L3 canonical details, task-selected only.
- L4 evidence/raw logs/code, only for implementation, validation, debugging, comparison, or historical reconstruction.

Stop reading when the current layer is sufficient for the next action.

## Project skeleton

```text
<Project> Root Map
├── 00 Control Plane
│   ├── AI Entry / Protocol pointer
│   ├── Project Manifest
│   └── Current Snapshot
├── 10 Product
├── 15 Capabilities
│   ├── Capability Index
│   ├── Project Feature Registry
│   └── Capability Maps
├── 20 Architecture
│   ├── Context / Containers / Components as needed
│   ├── Data / API / Security / Deployment
│   └── DEC / ADR Index
├── 30 Engineering
├── 40 Operations
├── 50 Planning
├── 60 Governance & Audit
├── 80 Evidence
└── 90 Archive
```

Do not create empty pages just because the skeleton names a section.

## Canonical Node header

```text
Node ID:
Type:
Canonical For:
Summary:
READ WHEN:
SKIP WHEN:
Depends On:
Referenced By:
Status:
Last Verified:
Source of Truth:
```

Recommended body order:

```text
00 Summary / Current Truth
10 Scope & Boundaries
20 Model / Architecture / Flow
30 Current State / Interfaces
40 Details / Implementation
60 Validation / Test / Operations
80 Risks / Conflicts / Unknowns
90 References / Evidence / Related Nodes
99 Change Notes
```

## Feature Registry

One project = one feature ledger. Capability pages use filtered views.

Minimum stable semantics:

- Feature ID;
- Feature;
- Capability;
- Summary;
- Lifecycle;
- Priority;
- Type;
- Platforms;
- Acceptance;
- Owner Node;
- Architecture;
- Dependencies;
- Requirement/Source;
- Release;
- Last Verified;
- Audit Required.

Create a `FEAT-*` detail node only when the feature needs non-trivial behavior, interaction/state, API/data/security rules, cross-platform differences, or sustained evolution.

## Writeback propagation

- local implementation detail -> smallest owner only, or no durable writeback if truly transient;
- node state/interface -> canonical owner + parent pointer summary;
- cross-cutting scope/architecture/project phase/P0-P1 -> canonical owner + Domain Map + Root snapshot/system map;
- new/retired node -> parent map + backlinks + registry;
- significant trade-off -> DEC/ADR;
- incident -> INC; stable prevention/runbook/architecture lessons are compiled back into current nodes.
