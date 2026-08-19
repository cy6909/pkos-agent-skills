# Routing policy

Use this reference when choosing whether to delegate, how much reasoning effort to use, or whether parallelism is justified.

## First decide whether to delegate

Delegate only when at least one concrete benefit exceeds coordination cost:

- a bounded implementation can run while Sol performs independent inspection or integration preparation;
- two disjoint lanes can reduce the critical path;
- context isolation materially reduces error risk;
- a fresh reviewer materially reduces self-confirmation risk;
- Luna is a better cost/throughput fit for an already settled slice.

Do not delegate merely because:

- the Skill was invoked;
- the task is described as “large”;
- several files are mentioned;
- a child slot is available.

Localized, low-risk, strongly sequential changes may be faster outside this workflow.

## Planner and session-budget gate

The current session that loaded the Skill is the planner. Do not route planning to a new Sol session. Before any child dispatch, obtain one user-confirmed budget for total non-planner sessions and worker/tester/reviewer role limits. If the user has not confirmed a number, propose a small bounded default and wait; omission never means unlimited.

When a lane becomes ready, prefer a compatible idle session using role, model, worktree safety, Memory Pack revision, and component/domain affinity. Spawn only if no compatible idle session exists and confirmed capacity remains. At capacity, queue the lane. Reuse is forbidden for ambiguous, stale, unresolved-write, permission-incompatible, or independence-sensitive sessions.

## Profile selection

| Profile | Sol | Luna | Use when |
| --- | --- | --- | --- |
| `adaptive` | medium by default; high/xhigh for judgment | medium/high; xhigh for difficult settled work | Normal work |
| `max-pair` | max | max | Explicit quality-first request or costly difficult failure |

Effort escalation rules:

1. Start at the lowest tier likely to finish in one bounded turn.
2. Escalate Sol for unresolved decisions, conflicting evidence, difficult diagnosis, or high-risk review.
3. Escalate Luna only after task boundaries are complete; more reasoning does not compensate for an ambiguous packet.
4. After one ineffective Luna attempt, Sol diagnoses before another implementation attempt.
5. `max` requires a written reason. Never use `ultra` automatically.

## Task classification

### Mechanical

Known operation, exact files, exact expected result, little judgment.

Route: Sol low/medium planning → Luna medium.

### Standard implementation

Real coding and tests, but contracts and boundaries are clear.

Route: Sol medium/high → Luna high → deterministic checks → Sol acceptance.

### Difficult bounded implementation

Subtle invariants or multi-file work, but architecture/interfaces are frozen.

Route: Sol high/xhigh → Luna xhigh or max with reason → strict review if risk warrants.

### Open-ended architecture or incident diagnosis

The safe implementation path is not settled.

Route: Sol high/xhigh/max diagnosis first. Do not dispatch Luna until the safety gate passes.

## Parallel eligibility

All must be true:

- at least two implementation lanes have no dependency edge between them;
- write-path prefixes are disjoint;
- each lane has an isolated worktree/checkout;
- shared interfaces and data shapes are frozen before dispatch;
- no lane must edit a common registry, manifest, lockfile, generated artifact, or migration sequence;
- one integration owner and one barrier are declared;
- serial baseline or an estimated serial equivalent can be measured;
- the expected time saved exceeds setup/integration cost.

Ordinary limit: two concurrent writers and never more than the user-confirmed worker limit. More requires a new explicit user-confirmed cap, a benchmark reason, and a wider integration plan.

## Memory, environment, and design gates

- Every lane loads the same versioned PKOS shared Memory Pack and its relevant canonical Notion sources before task-specific context.
- Every packet names the required skills and governing standards; the planner does not assume workers inherited its context.
- Resource-consuming verification follows the current shared environment policy. Under the active policy, local is development-only and tests/builds/containers/migrations/deployment/runtime checks run on `remote-12` after pulling the intended revision.
- A user-visible UI lane is ineligible until the connected Figma plugin and prerequisite skills are loaded, the canonical design is updated/approved, and a Figma evidence ref is frozen in the route.

## Assurance selection

Use `strict` for:

- authn/authz, secrets, tenant isolation;
- money, billing, quotas, irreversible actions;
- data integrity, migrations, deletion;
- concurrency, recovery, idempotency;
- public API/schema/compatibility changes;
- production-critical or wide architectural changes;
- an explicit user request for independent review.

Otherwise use `standard`.

## Economic routing rule

Quality is the gate; cost is the optimizer.

1. Reject unsafe or non-inferior-failing routes regardless of savings.
2. Among quality-eligible routes, compare the user's actual meter: subscription allowance, API money, wall-clock, or a weighted combination.
3. Report token volume separately from monetary cost and subscription consumption.
4. Count coordination turns, retries, review calls, and context transfer; cheap per-token models can lose if they require many extra turns.
