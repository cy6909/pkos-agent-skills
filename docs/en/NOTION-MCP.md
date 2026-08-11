# Notion MCP Integration

PKOS does not hard-code a Notion MCP implementation. The agent should discover the tool surface and map it to these capabilities:

- search pages/databases;
- fetch/read page content and schemas;
- query registry rows/views;
- create pages/databases after Search Before Create;
- update page content/properties and registry rows;
- verify write responses.

## Policy

When Notion tools are writable, PKOS persists durable project and memory truth there.

When tools are read-only, PKOS may use Notion for context but must return pending writeback instead of bypassing permissions.

When Notion is unavailable, the primary coding/analysis task may still proceed from repository/current context, but no persistence claim is allowed.

## Source-of-truth nuance

Notion is the durable control plane, not an excuse to ignore evidence. Code, config, runtime, tests, logs, and design sources may reveal that Notion is stale. Resolve the conflict with evidence, then update Notion so future agents see one current truth.
