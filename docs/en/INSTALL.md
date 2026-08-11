# Installation

## Marketplace install

```bash
codex plugin marketplace add cy6909/pkos-agent-skills
codex plugin marketplace list
```

Restart the supported desktop surface, open Plugins, choose the PKOS Agent Skills marketplace source, and install `pkos`.

To refresh:

```bash
codex plugin marketplace upgrade pkos-agent-skills
```

## Notion

Notion is optional at installation time but required for actual durable persistence. Connect a Notion MCP/app with the read/write capabilities described in `NOTION-MCP.md`.

## Per-project bootloader

Copy `examples/AGENTS.md` into a project repository and set Project ID + Notion Root URL when you want deterministic project routing.
