# Runtime installation and v0.6 smoke test

**READ WHEN:** installing roles, selecting an adapter, or certifying a runtime. Do not load during normal delivery.

## Adapter

Require a Codex surface that can create/message/inspect children, preserve role identity, isolate writers, and settle artifacts. Preference:

1. native custom subagents;
2. visible App tasks/threads with model, reasoning, repo, and worktree controls;
3. isolated `codex exec` processes managed by TD-01;
4. manual visible sessions using the same packets and ledgers.

If the adapter cannot inspect or settle children, return `BLOCKED_RUNTIME`; do not claim centralized execution.

## Model

Every role requests:

```toml
model = "gpt-5.6-sol"
model_reasoning_effort = "max"
```

Record identity as `observed | configured | unverified`. Explicit mismatch is `BLOCKED_MODEL_CONFIG`.

## Install

```bash
# Plugin mode: install/replace custom role TOMLs
python plugins/pkos/skills/codex-company-swarm/scripts/install.py --agents-only --force

# Standalone
python scripts/install.py --standalone --force

# Project-local
python scripts/install.py --project-root /path/to/project --force
```

The installer never edits active Codex configuration. Merge only supported keys from `assets/config.toml.fragment`; runtime lower limits win.

Use one worktree per writer and read-only sandboxes for planners/reviewers when enforceable.

## Static certification

```bash
python scripts/audit_prompt_budget.py
python scripts/validate_install.py
python -m unittest discover -s tests -v
python scripts/validate_coordination_bundle.py assets/examples/coordination-bundle
```

## Runtime smoke test

Execute one bounded sentinel route:

1. Root records itself as TD-01; PK-01 starts first and is sole Notion writer.
2. Bind/propose coordination schema; verify Run event, outbox, receipt, watermark, Pack, and checkpoint.
3. Spawn RB-01 plus one isolated developer/tester pair; verify scope and freshness rejection.
4. Exercise direct/snapshot/blocked context and one Pack Delta acknowledgement.
5. Exercise MFSQ, exact-candidate CI, Jenkins-missing classification, INT-01 freeze, and G4 verdict.
6. Exercise failed Notion write/replay, checkpoint/resume, authorized takeover, stale-epoch rejection, traceability, dashboard, retrospective, and canonical writeback.

Packaging validation is not runtime certification. Report actual model, session, Notion, CI, and external-action evidence honestly.
