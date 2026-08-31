---
name: pkos-memory-lint
description: Audit and garbage-collect PKOS long-term memory for duplicate active facts, stale temporal state, oversized core context, low-utility noise, unsupported inference, sensitive-memory provenance gaps, and forgotten-data residue. Use when memory quality drifts, retrieval becomes noisy, Core Profile grows, or as periodic maintenance.
---

# PKOS Memory Lint / GC

Use `../../references/pkos-memory-spec.md`.

`NOTION_WRITE_LANGUAGE=zh-CN` applies to every repaired value, audit note, and pending Notion writeback; follow `../../references/notion-tool-contract.md`.

Check:

- multiple active memories for the same Subject/Scope/Meaning;
- active facts outside their validity window;
- `hypothesis` compiled into Core;
- oversized Core / Always-On set;
- dynamic memories long overdue for verification;
- ephemeral memories with low utility and no recent useful access;
- missing provenance/source episode;
- unsupported sensitive inference;
- orphan / over-specific memory entries;
- contradictory active memories;
- forgotten/deleted information still exposed by active pointers or profile summaries.

Repair current truth first. Consolidate duplicates, supersede obsolete entries, downgrade stale dynamic entries to needs-review, and remove low-value ephemeral entries from default retrieval.

GC optimizes retrieval precision, not Notion storage usage.

After repair, simulate a bounded Context Compiler pass and verify that the working set remains within configured budget without losing the highest-value current facts.
