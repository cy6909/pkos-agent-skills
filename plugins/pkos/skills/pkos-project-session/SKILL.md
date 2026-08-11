---
name: pkos-project-session
description: Apply PKOS during normal software-project work: route the smallest project context before implementation and write durable project truth back afterward when Notion tools are available. Use for repository-specific feature work, architecture changes, debugging, refactoring, deployment changes, or project analysis where persistent project knowledge may matter. Do not use for generic coding questions unrelated to a concrete project.
---

# PKOS Project Session

Use this as the normal PKOS project-work orchestration workflow.

1. Detect whether a Notion-capable tool/app is available. Do not assume exact tool names; use `../../references/notion-tool-contract.md` when needed.
2. Resolve the project Root Map from the repo's `AGENTS.md`, current instructions, project name, or a targeted Notion search.
3. If a Root exists, route the minimum context using the principles in `pkos-context-router`; do not recursively load the project.
4. Perform the user's project task using code/runtime/design evidence as needed.
5. Before finishing, decide whether the work changed durable project truth.
6. If yes, classify the change C0-C5 and apply the `pkos-project-writeback` workflow. Load `../../references/audit-governance.md` for C2+ or structural/incident work.
7. If the task depends on persistent user goals/preferences/collaboration rules, use the bounded memory workflow rather than loading broad user history.
8. If Notion is unavailable/read-only, complete the primary task when possible and return a precise pending writeback; never claim persistence succeeded.

Keep project-context reads proportional to the task, never to total project size.
