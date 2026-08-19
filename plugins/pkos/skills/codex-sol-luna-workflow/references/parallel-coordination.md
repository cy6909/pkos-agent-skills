# Parallel coordination and concurrent completion settlement

Use this reference when two or more lanes run concurrently or when multiple child sessions finish close together.

## Principle

Completion messages are notifications, not state transitions. Persist typed results first, then settle them deterministically by `run_id`, `generation`, dependencies, ownership, and barrier rules.

## Required topology

```text
Integration checkout / task branch
  ├─ Lane A isolated worktree / branch
  └─ Lane B isolated worktree / branch
```

Each lane has:

- unique lane ID;
- same run ID and active generation;
- exact base revision;
- isolated worktree/branch;
- disjoint write scope;
- result artifact path;
- dependency list;
- focused acceptance and checks.
- shared Memory Pack revision, required skills, standards, and environment policy;
- session affinity and assigned/reused session ID.

The integration owner has the only write authority over the integration checkout.

## Dispatch rules

- Freeze shared interfaces before workers start.
- Do not run parallel writers against the same checkout.
- Do not allocate a shared registry, lockfile, manifest, migration sequence, generated file, or public interface to multiple lanes.
- Read-only investigation lanes may run concurrently without worktrees when they cannot mutate the repository.
- Record start time only after the child actually materializes and begins work.
- Confirm total and per-role session limits before the first dispatch.
- Reuse an idle compatible session with the strongest lane affinity before spawning.
- At capacity, queue ready work. Do not create extra Luna Max sessions to reduce waiting time.
- Send the full new Task Packet when reusing a session; old lane assumptions never override the active generation.

Use `scripts/schedule_sessions.py route.json session-pool.json` to obtain deterministic recommendations. A `reuse` recommendation is applied by messaging/resuming that exact session; `spawn` is permitted only within the confirmed caps; `queue` remains pending until capacity changes.

## Result arrival

When several children finish:

1. write every result to its declared artifact;
2. append a compact ledger event;
3. do not merge or accept from the chat message;
4. run deterministic settlement over all currently available results;
5. read long evidence only for invalid, contradictory, failed, or integration-critical lanes.

## Settlement rules

A result is `settled` only when:

- run ID and generation match the active route;
- lane ID exists exactly once;
- status is `complete`;
- base revision matches the lane contract;
- requested/observed model identity does not contradict the route;
- changed paths remain inside ownership and outside exclusions;
- every required acceptance result is `pass`;
- every required verification command has a successful exit state;
- no blocking gap remains.
- the exact shared Memory Pack and canonical Notion sources were loaded;
- required skills were loaded and the actual session ID/reuse state were recorded;
- remote-required checks report the canonical environment, pulled revision, and evidence;
- UI lanes include the frozen Figma evidence.

A result can be:

- `settled`: valid and complete;
- `blocked`: worker found a boundary or external prerequisite;
- `failed`: implementation or verification failed;
- `invalid`: malformed, mismatched, scope-violating, or contradictory;
- `stale`: older generation;
- `pending`: required result not present;
- `superseded`: preserved history replaced by a later explicit generation/lane.

## Generation behavior

- Replanning increments `generation`.
- A late result from generation N never enters generation N+1 automatically.
- Preserve stale evidence for diagnosis, but do not apply its patch or release its barrier.
- A new generation may explicitly adopt a prior settled artifact only after Sol revalidates it against the new contract.

## Barrier release

A barrier becomes `ready` only when all declared dependencies are settled. Arrival order is irrelevant.

```text
A settled ─┐
           ├─ barrier ready -> integration
B settled ─┘
```

If A settles and B fails:

```text
A remains settled
B -> repair or replan
barrier remains blocked
```

Do not rerun A merely because B failed. Recheck A only if B's repair changes a frozen shared interface or the active generation.

## Duplicate and ambiguous results

- Two result artifacts for the same `(run_id, generation, lane_id)` are a conflict unless byte-identical and explicitly deduplicated.
- An interrupted child with unknown completion state remains ambiguous; do not create a replacement that can write the same scope until the first lane is cancelled or fenced.
- Use unique worktrees/branches and lane IDs to prevent double writers.

## Integration order

Sol chooses integration order from dependencies and compatibility, not message timing. A single integration owner:

1. verifies each lane's base and candidate;
2. applies/cherry-picks/merges in declared order;
3. resolves conflicts against the frozen shared contract;
4. runs cumulative checks;
5. records the final candidate and integration evidence.

A child lane saying “tests pass” cannot prove that the combined candidate passes.

## Event-driven waiting

- While Sol has useful inspection, task-packet, or integration work, do not wait.
- When idle, use one long/event-driven wait supported by the host rather than repeated short polls.
- After wake, reconcile actual children and result artifacts; a completion message without an artifact remains incomplete.
- Mark a settled child idle in the session-pool ledger, then assign the nearest ready affinity-matched lane before considering a spawn.

## Compact controller view

```text
| Lane | Generation | Child | Status | Scope | Checks | Result artifact | Barrier impact |
| --- | ---: | --- | --- | --- | --- | --- | --- |
```

Sol first reads this view. It opens full diffs/logs only where judgment is needed, reducing context pressure when multiple children complete together.
