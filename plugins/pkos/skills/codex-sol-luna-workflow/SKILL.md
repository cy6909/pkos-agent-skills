---
name: codex-sol-luna-workflow
description: Orchestrate Codex software-development work with GPT-5.6 Sol as a non-writing planner, coordinator, integrator, and evidence judge, and GPT-5.6 Luna as a bounded implementation worker. Use when the user wants better coding quality, parallel speed, or token efficiency through explicit Sol/Luna routing, isolated ownership, deterministic verification, optional fresh review, and measurable completion gates. This skill is CodeHive-inspired but does not require CodeHive.
metadata:
  short-description: Sol decides, Luna implements, evidence decides
---

# Codex Sol–Luna Workflow

Coordinate one software outcome through Codex without requiring CodeHive. Borrow only the useful control-plane ideas: typed task packets, single-writer ownership, generations, barriers, durable evidence, bounded repair, and acceptance from actual artifacts.

## Core contract

- **Sol decides:** inspect the minimum authoritative context, resolve ambiguity, freeze interfaces, decompose bounded slices, coordinate dependencies, inspect cumulative diffs, adjudicate evidence, and accept or replan.
- **Luna implements:** edit only its assigned scope, run the requested focused checks, report concrete artifacts, and stop before crossing a boundary or making a new design decision.
- **Evidence decides:** a child saying “done” is never acceptance. Diff, changed paths, commands, exit states, acceptance mapping, review findings, and integration results are the authority.
- **The runtime enforces what it can:** worktrees, sandbox/tool restrictions, named roles, file ownership, route validation, and result settlement. Prompt-only constraints must be reported as declarative, not proven isolation.

This skill must not pretend CodeHive is available, must not call CodeHive tools, and must not require a CodeHive project. It may be used in any Git repository supported by Codex.

## Preflight

1. Read applicable `AGENTS.md`, repository guidance, the requested specification or issue, the relevant source/tests, and the current Git state. Do not recursively ingest the repository.
2. Record repository, branch/worktree, exact base revision, staged/unstaged/untracked paths, and unrelated user changes.
3. State the observable outcome, invariants, excluded scope, acceptance criteria, rollback boundary, and external-action authority.
4. Confirm the current parent is Sol when the requested route requires it. Classify model identity as `observed`, `configured`, or `unverified`; do not infer it from a role name.
5. Choose a routing profile and assurance mode. Read [routing policy](references/routing-policy.md) only when the route is not obvious.
6. Create a durable run directory such as `.codex/sol-luna/<run-id>/` for route, task packets, child results, settlement, metrics, and review artifacts. Do not rely on conversation memory.

For a localized change where delegation adds no real benefit, Sol may recommend direct execution outside this skill. Invoking the skill is not a reason to create children.

## Choose profile and assurance

### `adaptive` — default

Use the least expensive effort likely to finish correctly in one bounded turn.

- Sol `medium` for ordinary planning and integration.
- Sol `high` or `xhigh` for cross-component ambiguity, architecture, difficult diagnosis, or high-risk judgment.
- Sol `max` only when explicitly requested, a lower effort failed once, or failure cost clearly justifies it.
- Luna `medium` for mechanical one-file work.
- Luna `high` for normal bounded implementation.
- Luna `xhigh` for difficult but fully specified implementation.
- Luna `max` only when the Luna-safety gate passes and a concrete reason is recorded.

### `max-pair` — explicit quality-first route

Use Sol `max` for planning/integration and Luna `max` for bounded implementation. This is not the universal default and does not relax any scope, evidence, or review gate.

### `standard` assurance — default

Luna implements; deterministic checks run; Sol inspects the real cumulative diff and evidence. No fresh independent reviewer is required.

### `strict` assurance

Use for auth, secrets, money, data integrity, migrations, destructive behavior, concurrency, public APIs, production-critical paths, or broad architectural changes. Add one fresh read-only Sol reviewer after deterministic verification. Allow at most one Luna repair and one fresh re-review.

## Sol non-writer boundary

Sol may inspect, plan, route, monitor, settle results, integrate decisions, review, and accept. Sol must not author or repair product code under this workflow.

- Keep all code writes assigned to Luna or an explicitly named non-Sol executor.
- Sol may invoke read-only Git inspection and deterministic validation orchestration. When the user requires strict supervision-only behavior, assign command execution to a verifier/worker and require zero Sol shell execution.
- Record parent write events when the host exposes tool events. Any Sol-authored product-code change invalidates the claimed Sol/Luna route even if the final code works.
- A read-only sandbox or tool-restricted Sol planner/reviewer is stronger evidence than prose. When unavailable, label the boundary `declared`, not `enforced`.

Read [role boundaries](references/role-boundaries.md) for the exact audit contract.

## Luna-safety gate

A Luna writer may start only when all are true:

- one coherent, independently testable outcome;
- architecture, public behavior, and interfaces are settled;
- exact write ownership and explicit exclusions;
- relevant file/artifact references rather than inherited parent history;
- concrete acceptance criteria and exact verification commands;
- no unresolved security, migration, data-integrity, concurrency, public-contract, or production decision;
- no unauthorized external side effect;
- a blocker contract requiring return before leaving scope;
- `may_delegate: false`.

When the gate fails, Sol must resolve the decision, split the slice, or return `NEEDS_STRONGER_EXECUTOR`. Do not force Luna merely to save tokens.

## Build the route

Create a compact Goal Contract and one or more Task Packets using [task contracts](references/task-contracts.md). Validate the route before dispatch:

```bash
python scripts/validate_route.py path/to/route.json
```

Standard graph:

```text
Sol plan/freeze
  -> Luna bounded implementation
  -> deterministic focused verification
  -> broader checks proportional to risk
  -> Sol cumulative diff + evidence acceptance
```

Strict graph:

```text
Sol plan/freeze
  -> Luna bounded implementation
  -> deterministic verification
  -> fresh read-only Sol review
      -> SHIP
      -> one Luna repair -> reverify -> one fresh re-review
      -> REPLAN
```

Parallel graph:

```text
Sol freezes interfaces and ownership
  -> Luna lane A in isolated worktree
  -> Luna lane B in isolated worktree
  -> deterministic result settlement by run/generation/lane
  -> integration barrier
  -> one integration owner applies/merges in dependency order
  -> cumulative verification and Sol acceptance
```

Parallelize only when write scopes are disjoint, dependencies are absent, interfaces are frozen, each lane has its own worktree, and the integration barrier is explicit. Default to one writer and cap ordinary routes at two concurrent writers.

## Handle concurrent completions

Child completion order is not integration order.

1. Each child writes a structured result artifact containing `run_id`, `generation`, `lane_id`, base, changed paths, checks, acceptance mapping, gaps, and evidence refs.
2. Persist results before reading long reports. Do not merge directly from chat messages.
3. Settle results by route generation and dependency order:

```bash
python scripts/settle_results.py route.json result-a.json result-b.json \
  --output settlement.json
```

4. Ignore stale-generation results for the active candidate while preserving them as history.
5. Preserve successful lanes when another lane fails; keep the barrier blocked and repair or replan only the failed lane.
6. Release integration only when all required dependencies are settled. One integration owner produces the cumulative candidate.

Read [parallel coordination](references/parallel-coordination.md) for recovery, duplicate, late, and partial-result rules.

## Evaluate Luna success

Luna succeeds only when all applicable layers pass:

1. **Runtime identity:** requested/configured/observed model and effort are recorded without overclaiming.
2. **Scope compliance:** every changed path belongs to the lane; excluded and unrelated user files remain untouched; no child delegation occurred.
3. **Functional evidence:** each acceptance criterion maps to implementation and deterministic evidence; required commands have concrete exit states.
4. **Code quality:** Sol inspects the cumulative diff; strict mode adds a fresh read-only reviewer with actionable, evidence-backed findings.
5. **Integration:** all lanes coexist, cumulative tests pass, shared interfaces match the frozen contract, and fix-induced regressions are checked.

A worker report is only a claim. Use [assurance gates](references/assurance-gates.md).

## Measure whether parallelism helped

Do not claim efficiency from the number of children. Compare a serial baseline with the parallel route under the same base, requirements, acceptance, environment, and model configuration.

Record metrics and score them:

```bash
python scripts/score_efficiency.py metrics.json
```

At minimum report:

- serial and parallel wall-clock time;
- speedup and parallel efficiency;
- coordination, barrier, integration, and repair time;
- total tokens and per-role tokens when observable;
- acceptance/hidden-test results, P0/P1 findings, ownership violations, repair rounds, and human interventions.

Quality must be non-inferior before time or token savings count. Read [efficiency evaluation](references/efficiency-evaluation.md).

## Context and token controls

- Load this entrypoint once per root task and only the references needed for the chosen mode.
- Use `fork_turns="none"` and self-contained packets; never copy the entire parent transcript.
- Pass paths, revisions, small context manifests, diffs, and evidence refs instead of pasting full files or logs.
- Keep large outputs in run artifacts; return compact summaries.
- Do not regenerate full plans after checkpoints; update the route ledger.
- Use event-driven/long waits rather than rapid polling, and continue parent-owned inspection or integration preparation while workers run.
- Batch small same-shape edits when one worker and one review surface are cheaper than several children.
- Reserve budget for verification and one repair; concurrency is a ceiling, not a target.
- Track token volume, API money, subscription allowance, latency, and human effort as separate axes.

## Runtime and installation

Read [runtime setup](references/runtime-setup.md). The package supports:

- PKOS/plugin mode: the Skill lives under `plugins/pkos/skills/codex-sol-luna-workflow/`, while named agent TOMLs are installed separately;
- standalone user mode under `$CODEX_HOME/skills/`;
- project-local mode under `.agents/skills/`;
- named-agent, visible App thread/task, or isolated `codex exec` adapters.

Validate after changing or installing:

```bash
python scripts/validate_install.py
```

## Final statuses

Return one of:

- `SHIP_STANDARD`
- `SHIP_STRICT`
- `CHECKPOINT_READY`
- `REPLAN_REQUIRED`
- `NEEDS_STRONGER_EXECUTOR`
- `BLOCKED_RUNTIME`
- `BLOCKED_EXTERNAL_BOUNDARY`

Final reporting must include the actual route, identity confidence, base/candidate, changed scope, checks, review result, repairs, parallel metrics when applicable, unrun evidence, and remaining risk. Never describe a proposed route as one that actually ran.
