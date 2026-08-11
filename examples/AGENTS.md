# PKOS project knowledge

This repository uses the installed PKOS plugin for durable project knowledge.

Project ID: <PROJECT_ID>
Project Root Map: <NOTION_PROJECT_ROOT_URL>
PKOS Protocol: use the installed `pkos` plugin references.

Before project-specific work:

1. Use `$pkos-project-session` / PKOS project workflow when available.
2. Route through Project Root; do not recursively load all project documentation.
3. Dereference only task-relevant nodes and evidence.
4. Search existing Node IDs, Feature Registry, names, and aliases before creating project documentation.

After meaningful durable changes:

1. Update the single canonical owner in Notion when writable tools are available.
2. Refresh parent pointer summaries for state/interface changes.
3. Refresh Root snapshot/system map for cross-cutting scope, architecture, phase, or P0/P1 changes.
4. Apply C0-C5 audit/ADR/incident rules.
5. Never claim a Notion write succeeded unless the tool confirmed it.

Repository build/test/lint commands:

- <COMMAND>
