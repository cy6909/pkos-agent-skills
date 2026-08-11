---
name: pkos-project-bootstrap
description: Initialize or migrate a software project's durable knowledge into the PKOS Notion architecture. Use when creating a new project knowledge base, normalizing inconsistent project documentation, building a Project Root Map, creating the canonical Feature Registry, or migrating duplicate legacy pages. Do not use for ordinary implementation when a healthy PKOS Root already exists.
---

# PKOS Project Bootstrap

Read `../../references/pkos-project-spec.md` and `../../references/templates.md` as needed.

## Workflow

1. Discover existing project sources before creating anything: Notion pages/databases, repositories, architecture, features, incidents, operations, plans, and design sources.
2. Classify discovered material as canonical candidate, map, registry, evidence, log, archive, or duplicate candidate.
3. Define one canonical owner for each durable fact class.
4. Create/normalize the Project Root Map first; keep it within the L1 context budget.
5. Establish Product, Capabilities, Architecture, Engineering, Operations, Planning, Governance/Audit, Evidence addresses. Do not create empty pages.
6. Create or bind exactly one Project Feature Registry. Capability pages use filtered views of this ledger.
7. Create or bind an Audit Ledger and Decision/Incident indexes where relevant.
8. Register existing pages before creating replacement pages. Add Node headers only when useful.
9. Create missing canonical nodes only where responsibility is genuinely missing.
10. Register every new node in one primary parent map and add important backlinks.
11. Run PKOS lint and report unresolved ownership conflicts or duplicate candidates.

## Constraints

- Search Before Create.
- Never delete uncertain historical material during bootstrap; first downgrade it to evidence/superseded candidate.
- Never copy all repository-level implementation detail into Notion.
- Never claim a complete Notion scan unless the tool actually enumerated the complete scope.

## Done definition

An agent reading only the protocol + Root Map can explain what the project is, its current phase, high-level system, active priorities, and where to dereference task-specific facts in 2-3 hops.
