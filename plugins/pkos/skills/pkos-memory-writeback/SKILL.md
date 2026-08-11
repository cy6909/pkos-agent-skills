---
name: pkos-memory-writeback
description: Extract, deduplicate, update, supersede, consolidate, or delete durable long-term user/agent memories in the PKOS Notion Memory Registry. Use when the user explicitly asks to remember/forget something or when a stable preference, persistent goal/constraint, important feedback, or reusable collaboration rule should persist across sessions. Do not store transient chat details or unverified sensitive inferences.
---

# PKOS Memory Writeback

Use `../../references/pkos-memory-spec.md`.

1. Extract the smallest independent durable memory candidate; do not paste whole chats.
2. Score salience: core/high/normal/low. Ignore low-value one-off details.
3. Classify sensitivity. Raise the write threshold for personal/sensitive facts.
4. Search active memories by Subject/alias/Scope/Type before adding.
5. Resolve to ADD / UPDATE / SUPERSEDE / DELETE / IGNORE.
6. If several near-duplicate active memories express one stable concept, consolidate them into one canonical memory and supersede the old current entries.
7. Maintain `Valid From/Until`, confidence, provenance/source episode, and Decay Policy.
8. Inference may be stored only as `hypothesis`; never compile it into Core Profile until confirmed.
9. Refresh Core/Memory Root only for broadly useful high-salience current memory.
10. Record the minimal memory audit event.
11. Verify every Notion write actually succeeded.

For a forget/delete request, remove the fact from active current memory and compiled pointers/views; audit must not preserve the sensitive fact body.
