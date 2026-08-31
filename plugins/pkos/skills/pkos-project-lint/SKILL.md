---
name: pkos-project-lint
description: Audit and repair a PKOS software project's knowledge structure for duplicate canonical owners, orphan pages, stale pointer summaries, oversized maps, Feature Registry duplication, missing routing metadata, missing audit/ADR records, and unresolved source conflicts. Use after migrations, major refactors, documentation drift, or when agents load too much context or find conflicting pages.
---

# PKOS Project Lint

Use `../../references/pkos-project-spec.md` and `../../references/audit-governance.md`.

`NOTION_WRITE_LANGUAGE=zh-CN` applies to every repaired value, finding, audit note, and pending Notion writeback; follow `../../references/notion-tool-contract.md`.

Check:

1. Address integrity: unique Root, stable Node IDs, valid parent pointers, no important orphans.
2. Ownership integrity: one canonical owner per durable fact; no duplicate Feature/Incident/Roadmap/Architecture indexes.
3. Feature integrity: one project Feature Registry; capability pages use views/pointers rather than copied lists.
4. Context efficiency: Root/maps remain within budget; summaries and READ WHEN rules are sufficient for routing.
5. Cache consistency: pointer summaries and Root snapshot match canonical current truth.
6. Evidence freshness: Last Verified/source evidence exists where material; code/runtime conflicts are explicit.
7. Governance: C2+ changes have audit, C3 decisions have ADR, incidents have INC.
8. Current Truth hygiene: obsolete copies are not still presented as active current state.

Repair policy:

- report suspected duplicate groups before destructive cleanup;
- choose a canonical candidate with evidence;
- downgrade old entries to superseded/migration pointers before archive/delete decisions;
- when splitting oversized pages, move detail down and leave a pointer, not two active owners;
- after repair, simulate navigation from Root and verify important current facts are reachable in 2-3 hops.

Return health Green/Yellow/Red plus prioritized P0-P2 findings.
