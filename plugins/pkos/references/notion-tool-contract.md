# Notion Tool Contract

PKOS is provider-agnostic. Do not assume exact MCP tool names.

## Simplified Chinese write contract

`NOTION_WRITE_LANGUAGE=zh-CN` is mandatory for every PKOS Skill unless the user explicitly requests another language or an existing canonical node has a documented locale requirement.

All human-facing Notion content must use accurate, natural, easy-to-understand Simplified Chinese. This includes page and database titles, headings, summaries, descriptions, decisions and rationales, status explanations, risks, action items, acceptance notes, audit/ADR/incident narratives, memory bodies, and pending writeback payloads. Translate meaning rather than words: preserve the distinction between observed fact, user decision, proposal, assumption, uncertainty, and unverified claim; never improve fluency by inventing facts.

Keep machine contracts and precision-sensitive values verbatim: schema/property keys, Node/Feature/Memory/Run IDs, enum values, code symbols, API names, paths, commands, URLs, hashes, commit SHAs, error output, and product/proper names whose translation would reduce accuracy. When an existing Notion schema uses English property names, retain those property keys and write their human-readable values in Chinese. Do not invent a locale property that the schema does not support.

When updating an existing non-Chinese canonical node, preserve stable identifiers, aliases, links, and historical evidence. Convert or append only the human-readable current content needed by the task; do not silently rename canonical IDs or rewrite quoted source evidence. Mixed Chinese and preserved technical terms is correct when it is clearer and more exact than forced translation.

Read back every affected title, property value, and page section. A write is verified only when the response confirms persistence and the Chinese is semantically accurate, understandable in context, and free of unsupported claims. Awkward, ambiguous, misleading, or wrongly translated content must be corrected before reporting success.

## Capability discovery

Before a Notion-backed workflow, inspect available tools and map them to capabilities:

- search: find pages/databases by project name, Node ID, alias, feature, error, memory subject;
- fetch/read: read page content, database schema, and relevant rows;
- create: create page/database only after Search Before Create passes;
- update: modify the smallest canonical page or database row;
- query: filter/sort registry data and detect duplicates/current active state.

## Required behavior when Notion is available

1. Find the correct PKOS Root / Memory Root before reading details.
2. Use minimal reads; never recursively fetch all descendants just because the API allows it.
3. Search before creating pages or rows.
4. Perform writes only when the user's request and tool permissions allow it.
5. Apply `NOTION_WRITE_LANGUAGE=zh-CN` to every human-facing value and body.
6. Verify both the write response and the written Chinese through read-back.
7. Report the exact nodes/rows changed.

## If Notion is unavailable

- Continue the coding/analysis task when it can be completed from repository/current context.
- Produce a concise pending PKOS writeback plan for durable facts.
- Never state or imply that Notion was updated.

## If Notion is read-only

- Use it as project/memory context if needed.
- Do not work around permissions.
- Report the writeback payload that a writable agent or human should apply.

## Conflict handling

Notion is the durable control plane, but code/config/runtime/design are verification evidence. When they disagree, mark the conflict, inspect the relevant evidence, determine the current truth, then repair Notion so future agents receive one coherent state.
