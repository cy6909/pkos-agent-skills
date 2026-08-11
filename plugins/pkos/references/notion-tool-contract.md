# Notion Tool Contract

PKOS is provider-agnostic. Do not assume exact MCP tool names.

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
5. Verify the write response.
6. Report the exact nodes/rows changed.

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
