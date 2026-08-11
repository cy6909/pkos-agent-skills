---
name: pkos-context-router
description: Load the smallest task-relevant context from a PKOS-managed software project. Use when an agent needs to understand a project, trace architecture, prepare implementation, analyze performance, or investigate a project-specific bug without reading the entire Notion knowledge base. Do not use when the required project context is already present in the current conversation.
---

# PKOS Context Router

Use progressive disclosure from `../../references/pkos-project-spec.md`.

1. Read the Project Root Map only.
2. Extract task entities: feature/capability, component, platform, symptom, environment, action, constraints.
3. Match Root pointers and READ WHEN / SKIP WHEN rules; expand at most 1-3 domain/capability maps first.
4. Read pointer summaries and build the smallest working set.
5. Dereference L3 only if a concrete fact needed for the next action is missing, the node will be modified, interface/constraint/validation detail is required, or information conflicts.
6. Read L4 evidence only for implementation, validation, debugging, comparison, or historical reconstruction.
7. After every expansion ask: is the current context sufficient for the next action? If yes, stop.

Prefer an initial project context around 3k-6k tokens for ordinary tasks. Exceed it only when the task itself requires deeper evidence.

If multiple pages appear to own the same fact, treat that as an ownership conflict instead of arbitrarily selecting one or creating a new summary.
