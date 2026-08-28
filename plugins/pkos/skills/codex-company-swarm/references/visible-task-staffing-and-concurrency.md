# Visible-task staffing, routing, and concurrency v0.7

## Director-controlled routing

TD-01 chooses `model`, `reasoning_effort`, `model_rationale`, `risk_level`, and `routing_source` for every Task Packet. User instructions override defaults. Prefer Sol/max for direction, requirements/architecture, product development, integration, strict review, security/performance, migrations, and high-risk repairs. Prefer Luna/max for independent tests, CI/verifiers, and simple mechanical implementation after contracts and ownership are frozen. A Luna task that drifts, produces anomalous output, or fails repeatedly is followed up in the same task with Sol/max and an escalation record. Do not create a reviewer per packet.

## Visible task contract

The current task is TD-01. Every formal child role must be created with `create_thread`, appear in the sidebar, and remain openable/readable by the user and validator. Repository work uses a project worktree. The title contains `run_id`, role, and lane. Store `threadId`, `hostId`, worktree, role, lane, model/effort/rationale/risk, generation, Director epoch, state, and last `afterCursor` in `task_registry`.

Child prompts state:

```text
may_delegate=false; do not create child tasks.
Do not push, deploy, or write Notion unless this packet grants the unique authority.
Use only the named worktree/write scope and current generation/epoch/Pack.
Return commits, paths, tests/evidence, blockers, and a structured settlement.
```

Use `send_message_to_thread` for related small features, repairs, and later generations on the affinity-matched task. Create only when the required role has no reusable registered task. A resumed run binds stored IDs and cursors before creating anything.

## Budget registers

```text
default_max_product_lanes              = 3
max_product_lanes                      = 3 (may be 4 only with disjoint ownership evidence)
default_target_active_child_tasks      = 6
target_active_child_tasks              = 6
min_productive_concurrency             = 4
max_active_child_tasks                 = 8
hard_cap_active_child_tasks            = 8
max_registered_visible_tasks_per_run   = 12
underfill_alert_seconds                = 90
```

The active and registered hard caps are not silently adjustable. Any target/lane adjustment is recorded at G0/G1 with reason and evidence. A normal run uses three developer lanes plus three independent tester lanes; PK/CI/specialists fill spare capacity only when they have ready packets. There is one registered/active-at-a-time TD, PK, RB, and INT.

## State and counts

- `registered`: known visible task, not yet dispatchable;
- `queued`: packet exists but is awaiting dispatch or a dependency;
- `active`: executing an independent ready packet and occupying a child slot;
- `attention`: stopped/failed/input-needed, releases its active slot;
- `settled`: completed packet, retained for follow-up reuse;
- `archived`: terminal retained record.

`active_count` counts active children, excluding root TD-01. `productive_active_count` counts only active tasks doing ready work. Dependency waits are queued, never productive. `ready_count` is the ready queue not already active. Counts are derived from the registry and must match `concurrency_state`.

## Reconcile loop

TD-01 reconciles at BOOT, every Gate, completion/attention, generation change, and recovery:

1. validate current generation/epoch/Pack and derive counts;
2. release slots for attention/settled tasks;
3. inspect visible tasks with list/read and a bounded `wait_threads` call for at most eight active targets, using stored `afterCursor`;
4. when active is below target and ready work exists, first follow up a matching registered task, then create a missing role within both caps;
5. otherwise record a verifiable `underfill_reason` such as dependency, write conflict, environment capacity, external authorization, or unfrozen contract;
6. if ready >= minimum while productive active < minimum for 90 seconds, append `CONCURRENCY_UNDERFILLED` and correct or explain it.

Parallelism never overrides ownership. Shared migrations, routers, OpenAPI/schema, generated registries, cumulative integration, and any overlapping scope retain a named single-writer barrier.
