---
name: pkos-memory-context-router
description: Retrieve and compile the smallest relevant long-term user/agent context from PKOS Memory in Notion. Use when a task depends on persistent preferences, goals, constraints, prior feedback, or collaboration rules across sessions. Do not use when current conversation context is sufficient or the task does not benefit from personal long-term memory.
---

# PKOS Memory Context Router

Read `../../references/pkos-memory-spec.md` when detailed memory rules are needed.

`NOTION_WRITE_LANGUAGE=zh-CN` applies if this Skill produces any human-readable Notion update or pending writeback; follow `../../references/notion-tool-contract.md`.

1. Start with `memory_required = none | core | scoped | deep`; default to `none`.
2. If memory is required, read the Memory Root/Core first, not the whole registry.
3. Select relevant scopes only.
4. Filter to current valid memory: status, temporal validity, and sensitivity before semantic retrieval.
5. Retrieve by Subject/Type/alias plus semantic/keyword matching; expand relations/evidence only when necessary.
6. Rank by relevance, scope match, temporal validity, confidence, salience, and utility. Access frequency is only a secondary signal.
7. Deduplicate and resolve contradictions before packing.
8. Compile a bounded Memory Pack. Ordinary total memory context should usually remain about 1500-2500 tokens.
9. For multi-session work, compile one versioned Shared Collaboration Pack from active procedural memory before dispatch. Include canonical Notion refs, session caps/reuse policy, environment boundaries, Figma/design gates, and required collaboration rules; do not include broad history or secrets.
10. Require every worker/tester/reviewer session to load and acknowledge the same pack revision. Under a direct-Notion collaboration policy, each session must verify the canonical sources itself; if it cannot, block the lane instead of treating the planner snapshot as sufficient.
11. Use episodes/evidence only for deep verification or historical reconstruction.
12. Stop when the current working set is sufficient.

Never load memory proportional to total Memory Registry size.
Never treat `hypothesis`, `superseded`, or `deleted` as current user facts.
