# Runtime installation and smoke test

## Runtime requirements

This mode needs a Codex surface that can create or manage inspectable child sessions, preserve role identity, and isolate parallel writers. Preferred adapters:

1. native Codex subagents/custom agents with project or user agent TOMLs;
2. visible Codex App tasks/threads with explicit model, reasoning, project, and worktree controls;
3. isolated `codex exec` processes managed by the current Director session;
4. manually opened visible sessions using the same durable roster and packets when the host cannot spawn directly.

Do not claim centralized management occurred when the host cannot create, message, inspect, or settle the child sessions. Use `BLOCKED_RUNTIME` or disclose the manual adapter.

## Model requirement

Every role requests:

```toml
model = "gpt-5.6-sol"
model_reasoning_effort = "max"
```

Record identity confidence as `observed`, `configured`, or `unverified`. An explicit mismatch is `BLOCKED_MODEL_CONFIG`. Do not silently downgrade.

## Role files

Role definitions live under:

```text
assets/agent-configs/
```

The Technical Director file is used only when selecting the root role before this Skill loads. After invocation, the current session is `TD-01`; never spawn another Director.

Install role TOMLs globally:

```bash
python scripts/install.py --agents-only
```

Install the standalone Skill plus roles:

```bash
python scripts/install.py --standalone
```

Install project-local Skill and role definitions:

```bash
python scripts/install.py --project-root /path/to/project
```

The installer does not overwrite existing files unless `--force` is given and never modifies the user's main Codex configuration automatically.

## Concurrency configuration

A sample is provided at `assets/config.toml.fragment`:

```toml
[agents]
max_concurrent_threads_per_session = 24

[features.multi_agent_v2]
hide_spawn_agent_metadata = false
tool_namespace = "agents"
```

Merge only keys supported by the installed Codex version. Runtime limits lower than 24 take precedence and are recorded in `02-org.json`.

## Worktree layout

Suggested layout:

```text
.worktrees/company-swarm/<run-id>/
  D-FE-01/
  T-FE-01/
  D-BE-01/
  T-BE-01/
  CI-01/
  INT-01/
```

Do not run two workspace-write sessions in one checkout. Review/analysis roles should use read-only access when the adapter can enforce it.

## Native role invocation pattern

Illustrative adapter call:

```text
agents.spawn_agent(
  agent_type="pkos_company_domain_developer",
  fork_turns="none",
  message="Load <shared-pack> and <task-packet>; acknowledge the revisions; work only in <worktree>; write the structured result to <artifact>; do not delegate."
)
```

The exact tool namespace may differ. The Director maps runtime calls to the organization contract and records observed child IDs.

## Isolated process fallback

Illustrative developer:

```bash
codex exec \
  -m gpt-5.6-sol \
  -c 'model_reasoning_effort="max"' \
  --sandbox workspace-write \
  < .pkos/company-swarm/<run-id>/lanes/backend/task-packet.md
```

Illustrative Review Chair:

```bash
codex exec \
  -m gpt-5.6-sol \
  -c 'model_reasoning_effort="max"' \
  --sandbox read-only \
  < .pkos/company-swarm/<run-id>/reviews/g4-packet.md
```

The parent process/session remains the Director and settles result artifacts.

## Smoke test

Before production-critical use:

1. validate installation and examples;
2. start a Sol Max root and explicitly invoke `$codex-company-swarm`;
3. verify the current root records itself as `TD-01` and does not spawn another Director;
4. spawn/read back `RB-01` and verify it cannot write product code or delegate;
5. spawn one developer/tester pair in separate temporary worktrees;
6. verify reciprocal pairing and disjoint product/test ownership using `validate_org.py`;
7. make the developer write a harmless sentinel product file and the tester write a separate sentinel test;
8. verify each refuses the other's path and produces structured results;
9. validate an MFSQ example, then verify missing S/performance coverage fails validation;
10. classify an intentionally missing pipeline and verify a CI bootstrap task is created without claiming a live Jenkins server;
11. have `INT-01` combine only the sentinel commits after the barrier;
12. have `RB-01` review the frozen candidate and produce a verdict;
13. render the dashboard and inspect all counts/evidence;
14. verify PKOS/Notion writes are either confirmed or explicitly pending;
15. remove temporary worktrees and artifacts.

## Validation commands

```bash
python scripts/validate_install.py
python -m unittest discover -s tests -v
python scripts/validate_org.py assets/examples/organization.example.json
python scripts/validate_mfsq.py assets/examples/mfsq-test-plan.example.json
python scripts/render_dashboard.py assets/examples/run-state.example.json
```
