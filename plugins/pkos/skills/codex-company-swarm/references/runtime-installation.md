# Runtime installation and v0.10 smoke test

**READ WHEN:** installing roles, selecting an adapter, or certifying a runtime. Do not load during normal delivery.

## Adapter

Require a Codex surface that can create/message/inspect sidebar-visible tasks, preserve role identity, isolate writers, and settle artifacts. Formal Company Swarm roles use visible App tasks/threads with model, reasoning, repo, and worktree controls. Hidden custom subagents, hidden agents, and unregistered `codex exec` processes are not formal roles. Manual visible sessions may be used only when they preserve the same IDs, packets, ledgers, and inspectability.

If the adapter cannot inspect or settle children, return `BLOCKED_RUNTIME`; do not claim centralized execution.

## Model

TD-01 routes every task. Sol/max is preferred for Director, Chair, requirements/architecture, product development, integration, strict review, security/performance, migration and high-risk repair. Luna/max is preferred for independent testing, CI/verifier, and frozen low-risk mechanical work. Each manifest entry and packet records model, effort, rationale, risk, and routing source. User routing wins; TD-01 may override defaults with a reason. Escalate anomalous or repeatedly failing Luna work by following up the same task with Sol/max; do not create an automatic reviewer. Record identity as `observed | configured | unverified`. Explicit mismatch is `BLOCKED_MODEL_CONFIG`.

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

1. Root records itself as TD-01; create or wake product tasks first. PK-01 remains queued until an authorized gate batch and is the sole Notion writer.
2. Bind the existing Feature Registry; verify local events, gate-batch outbox/receipt/watermark, Pack, and checkpoint.
3. Create RB-01 plus one isolated developer/tester pair as sidebar-visible tasks; verify IDs, titles, worktrees, `may_delegate=false`, scope and freshness rejection.
4. Exercise direct/snapshot/blocked context and one Pack Delta acknowledgement.
5. Exercise progressive MFSQ, exact-candidate CI, CI Stop Rule, TD-01 candidate freeze, and conditional G4 review.
6. Exercise failed Notion write/replay, checkpoint/resume, authorized takeover, stale-epoch rejection, traceability, dashboard, retrospective, and canonical writeback.

Packaging validation is not runtime certification. Report actual model, session, Notion, CI, and external-action evidence honestly.
