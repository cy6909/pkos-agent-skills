# Runtime installation and v0.5 smoke test

## Adapter requirements

Company Swarm needs a Codex surface that can create/message/inspect child sessions, preserve custom role identity, isolate writers, and settle result artifacts. Preferred adapters:

1. native custom subagents with project/user TOMLs;
2. visible Codex App tasks/threads with explicit model/reasoning/project/worktree;
3. isolated `codex exec` processes managed by TD-01;
4. manually opened visible sessions using the same durable organization/packets when spawning is unavailable.

Do not claim centralized management if the adapter cannot inspect or settle children.

## Models

Every role requests:

```toml
model = "gpt-5.6-sol"
model_reasoning_effort = "max"
```

Record identity as `observed | configured | unverified`. Explicit mismatch is `BLOCKED_MODEL_CONFIG`; do not silently downgrade.

## Install

Plugin installation exposes the Skill. Install custom role TOMLs separately:

```bash
python plugins/pkos/skills/codex-company-swarm/scripts/install.py --agents-only
```

Standalone:

```bash
python scripts/install.py --standalone
```

Project-local:

```bash
python scripts/install.py --project-root /path/to/project
```

The installer never edits active Codex configuration automatically.

Sample supported configuration:

```toml
[agents]
max_concurrent_threads_per_session = 24

[features.multi_agent_v2]
hide_spawn_agent_metadata = false
tool_namespace = "agents"
```

Merge only keys supported by the installed Codex version. Runtime lower limits win.

## Worktrees

Use one worktree per repository writer. Read-only planners/reviewers should use read-only sandboxes when enforceable. Do not run two write sessions in one checkout.

## Invocation

The current root is TD-01. Provision PK-01 first, then establish/validate coordination before other staffing. Illustrative child packet:

```text
Load <Pack/Source Manifest>, acknowledge run/generation/Director epoch/Pack,
work only in <worktree/write scope>, emit events/results to <paths>,
do not delegate or write Notion directly.
```

## Smoke test

1. Validate installation, organization v2, examples and unit tests.
2. Start a Sol Max root and invoke `$codex-company-swarm` explicitly.
3. Verify it records itself as logical TD-01 and does not spawn another Director.
4. Provision PK-01 first; verify it is persistent and the sole Notion writer.
5. Discover/bind or safely propose the three coordination databases and Feature extension.
6. Create/verify Run event, outbox, receipt, watermark, Pack, Source Manifest and initial checkpoint.
7. Spawn RB-01 and one developer/tester pair in separate worktrees; verify reciprocal pairing and path separation.
8. Verify children reject each other's scopes, stale Pack and stale Director epoch.
9. Exercise `DIRECT_VERIFIED`, `BROKERED_SNAPSHOT`, `CONTEXT_REQUESTED` and blocked-freshness paths.
10. Publish a C2+ Pack Delta and verify mandatory reload/invalidation/generation rules.
11. Validate MFSQ including negative Security/performance cases.
12. Classify missing CI and create a Jenkins bootstrap task without claiming a live server.
13. Run exact-candidate CI/evidence, integrate with INT-01 and freeze the candidate.
14. Exercise a failed Notion write, retry/idempotency, receipt, dead-letter and replay.
15. Create/check checkpoints and generate a normal resume plan.
16. Perform an explicitly authorized takeover; verify epoch increment/reissued packets/old-result rejection.
17. Validate complete traceability and one intentionally broken link.
18. Have RB-01 review the frozen candidate; verify durable verdict/checkpoint.
19. Render the v0.5 dashboard and verify coordination fields.
20. Confirm canonical PKOS writeback or exact pending payload; run retrospective/memory gate.

## Validation

```bash
python plugins/pkos/skills/codex-company-swarm/scripts/validate_install.py
python -m unittest discover -s plugins/pkos/skills/codex-company-swarm/tests -v
python plugins/pkos/skills/codex-company-swarm/scripts/validate_coordination_bundle.py \
  plugins/pkos/skills/codex-company-swarm/assets/examples/coordination-bundle
```

Classify actual runtime/model/Notion/CI behavior honestly; packaging validation is not runtime certification.
