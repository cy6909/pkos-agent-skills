# PKOS Agent Skills

[简体中文](README.zh-CN.md) · English

**PKOS (Project Knowledge Operating System)** is a skill-only plugin for ChatGPT and Codex that turns Notion into an AI-addressable control plane for software-project knowledge and long-term memory.

It is designed for teams and individuals who use multiple AI agents, IDEs, devices, and repositories but want one durable, inspectable source of truth for:

- project maps and current state;
- product capabilities and feature tracking;
- architecture and ADRs;
- engineering / operations knowledge;
- audit trails and current-truth governance;
- long-term user/agent memory;
- bounded, token-efficient context retrieval.

PKOS does **not** ship a Notion credential, MCP server, or vendor-specific integration. If the agent already has a Notion MCP/app with suitable read/write tools, the skills use it. If Notion is unavailable or read-only, PKOS continues safely and reports the exact pending writeback instead of pretending persistence succeeded.

> Core rule: **Storage can grow; context must stay bounded. Route before read, search before create, and keep one canonical owner per durable fact.**

## Why PKOS?

AI-assisted projects often fail at documentation for predictable reasons:

1. Every agent invents a different project-document structure.
2. Agents re-read huge pages to understand a project, wasting context tokens.
3. Feature lists, incident lists, roadmaps, and architecture summaries are duplicated.
4. Nobody knows which page owns the current truth.
5. Old and new states accumulate in the same page until documentation becomes ambiguous.
6. Long-term memory grows without a retrieval budget and eventually pollutes context.

PKOS treats knowledge as an **address space** instead of a pile of documents:

```text
Protocol            ≈ instruction set / ABI
Project Root Map     ≈ root page table
Domain / Capability  ≈ second-level page table
Pointer Entry        ≈ pointer + short routing descriptor
Canonical Node       ≈ object at the canonical address
Evidence             ≈ source material / ground truth
Agent                ≈ process dereferencing pointers on demand
```

The same model is used for long-term memory:

```text
LLM context          ≈ bounded physical RAM
Core Profile         ≈ L1/L2 cache
Memory Root Map      ≈ page table
Memory Registry      ≈ virtual address space
MEM-*                ≈ memory pages
Episode / Evidence   ≈ disk / ground truth
Context Compiler     ≈ memory manager
Memory GC            ≈ garbage collector
```

## What is included?

The `pkos` plugin currently contains eight focused skills:

| Skill | Purpose |
|---|---|
| `pkos-project-session` | Orchestrate normal project work: minimal context before work, durable writeback after work. |
| `pkos-project-bootstrap` | Initialize or migrate a software project into the PKOS skeleton. |
| `pkos-context-router` | Load the smallest project working set instead of recursively reading documentation. |
| `pkos-project-writeback` | Write durable changes to the correct canonical Notion node and propagate summaries. |
| `pkos-project-lint` | Detect duplicate owners, stale pointers, oversized maps, missing audit, and structural drift. |
| `pkos-memory-context-router` | Compile a bounded, task-relevant long-term-memory working set. |
| `pkos-memory-writeback` | Extract, deduplicate, supersede, consolidate, and audit durable memories. |
| `pkos-memory-lint` | Audit / GC long-term memory for duplicates, stale facts, low utility, and context bloat. |

## Repository layout

```text
pkos-agent-skills/
├── .agents/plugins/marketplace.json     # repo marketplace catalog
├── plugins/pkos/
│   ├── .codex-plugin/plugin.json        # plugin manifest
│   ├── skills/                          # installable Agent Skills
│   └── references/                      # detailed protocol used on demand
├── docs/
│   ├── en/                              # English docs
│   └── zh-CN/                           # Chinese docs
├── examples/AGENTS.md                   # optional repository entry point
├── scripts/validate.py                  # local/CI structural validation
└── .github/workflows/validate.yml
```

## Install from the GitHub marketplace source

### 1. Add this repository as a marketplace

```bash
codex plugin marketplace add cy6909/pkos-agent-skills
```

Optionally pin a branch/ref:

```bash
codex plugin marketplace add cy6909/pkos-agent-skills --ref main
```

Confirm the marketplace is registered:

```bash
codex plugin marketplace list
```

### 2. Install the `pkos` plugin

Restart the ChatGPT desktop app / supported Codex surface, open **Plugins**, select the **PKOS Agent Skills** marketplace source, and install **PKOS – Project & Memory OS**.

The repository follows the current OpenAI plugin layout:

```text
.agents/plugins/marketplace.json
plugins/pkos/.codex-plugin/plugin.json
plugins/pkos/skills/<skill>/SKILL.md
```

### 3. Connect Notion (recommended, not bundled)

PKOS intentionally does not embed a Notion MCP endpoint or credentials. Connect any Notion MCP/app that gives the agent the capabilities it needs, ideally:

- search pages/databases;
- fetch/read page content and database schemas;
- create pages/databases when explicitly needed;
- update page content/properties;
- query database rows/views.

When these capabilities exist, PKOS uses Notion as the durable project/memory control plane. When they do not exist, the skills degrade safely to a read-only or pending-writeback workflow.

See [Notion MCP integration](docs/en/NOTION-MCP.md).

### 4. Optional: add a repo-level `AGENTS.md`

For a repository that should always route project knowledge through a known PKOS Root Map, copy [examples/AGENTS.md](examples/AGENTS.md) to the repository root and fill in the Notion URLs / project ID.

This keeps `AGENTS.md` short. It is a bootloader and router, not a knowledge dump.

## Update

Refresh Git-backed marketplace sources with:

```bash
codex plugin marketplace upgrade pkos-agent-skills
```

Or refresh all configured marketplace sources:

```bash
codex plugin marketplace upgrade
```

After refreshing, restart the relevant desktop surface if needed so the installed plugin is reloaded.

## How PKOS behaves with Notion

PKOS uses four hard rules:

**Route Before Read** — start at the Root Map and dereference only task-relevant nodes.

**Search Before Create** — search IDs, names, aliases, registries, and existing owners before creating a page or memory.

**Canonical Owner** — one durable fact has one current owner. Other pages may cache a short summary and pointer, but may not become a second source of truth.

**Current Truth + Audit** — canonical pages contain the current state. History belongs in Audit / ADR / Incident / Git / Evidence, not as multiple obsolete copies inside the current page.

## Project skeleton

Every PKOS project uses the same conceptual skeleton:

```text
<Project> Root Map
├── 00 Control Plane
├── 10 Product
├── 15 Capabilities
│   ├── Capability Index
│   ├── Project Feature Registry   # one feature ledger per project
│   └── Capability Maps / filtered views
├── 20 Architecture
├── 30 Engineering
├── 40 Operations
├── 50 Planning
├── 60 Governance & Audit
├── 80 Evidence
└── 90 Archive
```

Empty template sections do not require empty pages. PKOS creates nodes only when real information needs an owner.

See [Full specification](docs/en/SPEC.md).

## Feature Registry

A project has **one Project Feature Registry**. Capability pages expose filtered views of that same ledger instead of maintaining separate handwritten feature lists.

Core fields include:

- stable Feature ID;
- Feature / Summary;
- Capability;
- Type;
- Lifecycle;
- Priority;
- Platforms;
- Acceptance;
- Owner Node;
- Architecture pointer;
- Dependencies;
- Requirement / source;
- Release;
- Last Verified;
- Audit Required.

Simple features can live only as registry rows. Complex features get a `FEAT-*` canonical page.

## Audit and ADR policy

Before a durable write, PKOS classifies the change:

| Class | Meaning | Audit | ADR / Incident |
|---|---|---|---|
| C0 Editorial | formatting / typo / non-semantic cleanup | no | no |
| C1 State | status, progress, owner, verification | when materially tracked | usually no |
| C2 Contract | feature scope, API, schema, permissions, behavior | required | ADR when trade-offs/compatibility matter |
| C3 Architecture | boundaries, tech stack, topology, core dependencies | required | ADR required |
| C4 Structural | merge/split/owner migration/node retirement | required | ADR when design rationale matters |
| C5 Incident/Security | production incident, data/security issue, rollback | required | Incident required; ADR if architecture changes |

Canonical pages are cleaned to the new current truth; Audit stores compact before/after summaries and evidence, not full obsolete page copies.

## Long-term memory without context explosion

PKOS separates unbounded storage from bounded working context:

```text
Task
 ↓
Need-Memory Gate: none | core | scoped | deep
 ↓
Scope / status / temporal / sensitivity filters
 ↓
semantic + keyword + relation retrieval
 ↓
relevance + salience + confidence + utility ranking
 ↓
deduplicate / contradiction resolution
 ↓
Token Budget Packing
 ↓
Memory Pack
```

Recommended defaults:

- M1 Core Profile: 500–1000 tokens, hard cap around 1200;
- M2 Domain/Pointer summaries: 300–800;
- M3 retrieved memories: 800–2000;
- M4 Episode/Evidence: 0 by default; only for verification/history;
- ordinary total long-term-memory context: roughly 1500–2500 tokens.

Memory storage may contain ten or ten thousand entries; the working-set budget remains bounded.

## Safety and data behavior

PKOS is instruction-only. It does not itself grant access to Notion or any other external system. The connected app/MCP and the user's source-system permissions still determine what the agent can read or modify.

The skills also require the agent to:

- never claim a Notion write succeeded unless a write tool actually succeeded;
- raise the threshold for sensitive personal memory;
- keep inference as `hypothesis`, never silently promote it to user fact;
- honor forget/delete requests by removing the fact from active current memory and compiled views;
- preserve only the minimum audit trail needed for governance;
- verify conflicts between Notion and code/runtime/design evidence instead of silently choosing one.

## Public Plugin Directory

This GitHub marketplace is useful for development, community distribution, and direct installation. Publishing into the universal public Plugins Directory is a separate OpenAI review flow. A skills-only submission is supported; the submission needs final skills, listing metadata, starter prompts, test cases, and policy review.

See [Publishing guide](docs/en/PUBLISHING.md).

## Contributing

Contributions are welcome. Start with [CONTRIBUTING.md](CONTRIBUTING.md). The most important rule is that a skill must preserve PKOS invariants rather than create a second competing documentation model.

## License

MIT. See [LICENSE](LICENSE).
