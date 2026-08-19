# Role boundaries and audit contract

Use this reference when the user asks why Sol will not take over implementation, when strict role separation matters, or when runtime evidence is available.

## Responsibilities

### Sol planner/controller

The current session that loaded the Skill is the only Sol planner/controller for the root task. A separately spawned planner is a route violation.

Allowed:

- inspect repository guidance, code, tests, diffs, and evidence;
- resolve product, architecture, compatibility, safety, and interface decisions;
- create the Goal Contract, route, ownership map, dependencies, and barriers;
- dispatch bounded workers;
- ask the user to confirm total and per-role session limits before dispatch;
- compile the shared PKOS Memory Pack and attach required skills/standards to every packet;
- reuse compatible idle sessions by affinity and queue work at capacity;
- monitor state, settle results, and decide repair versus replan;
- inspect the cumulative candidate and accept/reject it;
- perform separately authorized merge/release decisions after gates pass.

Not allowed under this workflow:

- author, patch, or repair product code;
- silently expand a worker's scope;
- replace a failed Luna lane without recording a route change;
- claim verification from a worker's prose without checking artifacts;
- act as the fresh independent reviewer for its own final judgment;
- cross external boundaries without separate authorization.
- spawn or hand off to another planner after this Skill is loaded;
- exceed a confirmed session cap or treat a missing cap as unlimited;

Deterministic commands are a configurable boundary:

- **Practical mode:** Sol may trigger read-only inspection and deterministic validation commands as orchestration, but may not edit code.
- **Supervision-only mode:** all command execution is assigned to a worker/verifier; Sol only reads evidence.

Record which mode was used. Do not present Practical mode as zero-execution supervision.

### Luna implementation worker

Allowed:

- edit only declared write paths;
- run exact focused commands and risk-proportionate broader commands named in the packet;
- make local implementation choices that do not alter frozen contracts;
- return a blocker before leaving ownership or changing a settled decision.
- load the exact shared Memory Pack, canonical Notion sources, required skills, and standards named by the packet;
- perform resource work only in the declared remote environment after the intended revision is pulled;

Not allowed:

- redesign public behavior or interfaces;
- edit excluded/shared paths;
- delegate to another agent;
- deploy, publish, merge, push, or perform production mutations unless separately assigned and authorized;
- claim success without concrete command output and changed-file evidence.
- run tests, builds, containers, migrations, deployment, or resource-intensive verification locally when the shared environment policy marks local as development-only;
- implement a UI change before the Figma gate and evidence are complete.

### Fresh Sol reviewer

Allowed:

- inspect the frozen cumulative candidate, acceptance contract, tests, and evidence;
- return `SHIP`, `FIX_FIRST`, `RETHINK`, or `UNUSABLE_RUNTIME`;
- identify blockers with a concrete violated contract, reachable path, impact, file reference, and evidence gap.

Not allowed:

- edit or fix code;
- orchestrate workers;
- stop after the first issue when the review contract asks for a complete pass;
- convert optional hardening or style preferences into blockers.

## Enforcement levels

Classify each run honestly:

- `declared`: role behavior exists only in prompts/instructions.
- `configured`: named roles and sandbox/tool settings are configured, but actual events are not observed.
- `observed`: runtime events show the actor, model/effort, tools, and file changes.
- `enforced`: the runtime prevents forbidden tools or paths and events confirm the boundary.

A Skill alone normally provides `declared`; named-role configuration may provide `configured`; worktrees, sandbox restrictions, ownership checks, and event logs can raise confidence.

## Minimal audit fields

```text
RUN_ID:
GENERATION:
SOL_BOUNDARY_MODE: practical | supervision-only
SOL_BOUNDARY_CONFIDENCE: declared | configured | observed | enforced
PARENT_PRODUCT_WRITE_EVENTS:
PARENT_REPAIR_EVENTS:
PARENT_TEST_EXECUTION_EVENTS:
REVIEWER_WRITE_EVENTS:
WORKER_CHILD_SPAWN_EVENTS:
SPAWNED_PLANNER_EVENTS:
SESSION_CAP_VIOLATIONS:
MEMORY_PACK_MISMATCHES:
LOCAL_RESOURCE_EXECUTION_EVENTS:
UI_WITHOUT_FIGMA_EVENTS:
OUT_OF_SCOPE_WRITE_EVENTS:
UNATTRIBUTED_CHANGED_PATHS:
```

Route validity requires:

```text
PARENT_PRODUCT_WRITE_EVENTS = 0
PARENT_REPAIR_EVENTS = 0
REVIEWER_WRITE_EVENTS = 0
WORKER_CHILD_SPAWN_EVENTS = 0
SPAWNED_PLANNER_EVENTS = 0
SESSION_CAP_VIOLATIONS = 0
MEMORY_PACK_MISMATCHES = 0
LOCAL_RESOURCE_EXECUTION_EVENTS = 0
UI_WITHOUT_FIGMA_EVENTS = 0
OUT_OF_SCOPE_WRITE_EVENTS = 0
UNATTRIBUTED_CHANGED_PATHS = 0
```

`PARENT_TEST_EXECUTION_EVENTS` may be nonzero only in Practical mode and must be reported.

## Failure handling

- A Sol-authored implementation invalidates the claimed Sol/Luna experiment. Preserve the code, but classify the route as `ROLE_BOUNDARY_FAILED`.
- A Luna scope violation blocks acceptance even when tests pass.
- A reviewer write invalidates independence; rerun with a fresh read-only reviewer only if review budget remains.
- Missing actor/model metadata is `unverified`, not automatic proof of the expected route.
