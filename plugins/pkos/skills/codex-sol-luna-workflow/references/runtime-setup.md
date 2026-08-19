# Runtime setup and installation

This Skill does not require CodeHive. It uses whichever Codex adapter can prove the requested model, keep worker context bounded, and preserve repository isolation.

## Adapter priority

1. Visible Codex App task/thread with explicit `model`, `thinking`, project, and worktree controls.
2. Native named agent roles with `fork_turns="none"`.
3. Isolated `codex exec` processes with explicit model/effort and sandbox.
4. No delegation when model identity, write isolation, or result artifacts cannot be established.

Do not pretend a route ran when the host cannot create or inspect the required children.

## Parent session

Prefer `gpt-5.6-sol` for the root task before invoking this workflow when planning risk warrants it. Regardless of the supported current model, the session that loads the Skill remains the planner/controller and its observed identity is recorded honestly. Do not spawn `codex_sol_planner` or `codex_sol_max_planner` after invocation; those profiles are only useful when selecting the root session before the Skill loads. If the current session cannot safely resolve the planning judgment, return `NEEDS_STRONGER_EXECUTOR` rather than secretly creating another planner.

Record:

- observed parent model/effort when the host exposes it;
- otherwise configured or unverified identity;
- Sol boundary mode: Practical or Supervision-only.
- `planner.session=current` and `planner.spawn_planner=false`.
- the user-confirmed total and per-role session limits.

## Named-agent setup

Merge the supplied snippet into `~/.codex/config.toml` when your Codex build requires multi-agent v2 role invocation:

```toml
[features.multi_agent_v2]
hide_spawn_agent_metadata = false
tool_namespace = "agents"
```

Copy the desired files from `assets/agent-configs/` to `~/.codex/agents/`:

```text
codex_luna_worker.toml
codex_luna_max_worker.toml
codex_sol_planner.toml
codex_sol_max_planner.toml
codex_sol_reviewer.toml
codex_sol_max_reviewer.toml
```

Example named role invocation:

```text
agents.spawn_agent(
  agent_type="codex_luna_worker",
  fork_turns="none",
  message="Load the required skills and PKOS shared memory named in <packet>, execute only that lane in its declared environment, and write the result JSON to <path>."
)
```

If direct `model="gpt-5.6-luna"` overrides are rejected in your environment, prefer the named role path rather than silently substituting another model.

## Visible App task/thread adapter

When the App accepts explicit model and thinking:

1. locate the exact project/repository;
2. inspect the durable session-pool ledger and reuse a compatible idle task/thread when possible;
3. create one health-probe child only when no reusable compatible session exists and confirmed capacity remains;
4. immediately read it back and verify task ID, cwd/worktree, state, requested model, and effort;
5. stop the batch if the child did not materialize;
6. create only bounded project-local tasks and never exceed user-confirmed role/total limits;
7. message an idle compatible task with the next affinity-matched packet instead of creating a replacement;
8. read terminal results and inspect actual files/artifacts;
9. do not archive unresolved or unaccepted children.

## Isolated process fallback

Example Luna worker:

```bash
codex exec \
  -m gpt-5.6-luna \
  -c 'model_reasoning_effort="high"' \
  --sandbox workspace-write \
  < .codex/sol-luna/<run-id>/lane-a-packet.md
```

Example hard-isolated Sol reviewer:

```bash
codex exec \
  -m gpt-5.6-sol \
  -c 'model_reasoning_effort="high"' \
  --sandbox read-only \
  < .codex/sol-luna/<run-id>/review-packet.md
```

Use isolated worktrees for parallel writers. Do not launch two workspace-write processes against the same checkout.

## PKOS plugin installation

Recommended path inside the existing PKOS plugin:

```text
plugins/pkos/skills/codex-sol-luna-workflow/
```

Because the PKOS plugin manifest exposes `./skills/`, the Skill becomes part of the installed plugin after the marketplace/plugin snapshot is refreshed. Git push alone does not update an already installed snapshot.

After integrating:

```bash
python plugins/pkos/skills/codex-sol-luna-workflow/scripts/validate_install.py
python scripts/validate.py
```

Then refresh the marketplace/plugin, restart Codex or open a new task, and verify the Skill appears.

Named agent TOMLs are runtime files, not ordinary Skill metadata. Install them separately without duplicating the Skill:

```bash
python plugins/pkos/skills/codex-sol-luna-workflow/scripts/install.py \
  --agents-only --profile all
```

## Standalone installation

From the unpacked Skill:

```bash
python scripts/install.py --standalone --profile all
```

This installs:

```text
$CODEX_HOME/skills/codex-sol-luna-workflow/
$CODEX_HOME/agents/codex_*.toml
```

The installer does not modify `config.toml` automatically.

## Project-local installation

To expose the Skill only inside one repository:

```bash
python scripts/install.py --project-root /path/to/repo --skill-only
```

This installs to:

```text
<repo>/.agents/skills/codex-sol-luna-workflow/
```

Agent role files still belong under the user's Codex home unless the host provides another role registry.

## Smoke test

After any install or role change:

1. restart Codex or start a fresh process;
2. select a Sol parent;
3. invoke the Skill explicitly;
4. confirm a small session budget, then dispatch `codex_luna_worker` with `fork_turns="none"` on a read-only sentinel;
5. inspect child runtime identity and result schema;
6. run a temporary isolated write task with a deterministic check;
7. verify no out-of-scope paths changed and no child was spawned;
8. run a fresh read-only Sol reviewer;
9. test two isolated worktrees and `settle_results.py` before relying on parallel mode.
10. mark the sentinel worker idle, run `schedule_sessions.py`, and verify a related second packet is routed back to that worker while an over-cap lane queues.
11. verify each child directly loads the shared Notion memory sources and acknowledges the Memory Pack revision.
12. verify test/build/container/deploy commands cannot settle when reported as local, and a UI route cannot validate without Figma evidence.

Classify the route as observed/configured/unverified. Do not call an unverified route certified.
