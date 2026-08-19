# Shared memory, execution environments, and session reuse

Read this reference before dispatching any worker, tester, integrator, or reviewer.

## Current session is the planner

The session that loaded this Skill owns planning, routing, coordination, settlement, and acceptance for the root task. Do not spawn a second planner or transfer planner ownership to a child. Record `planner.session=current` and `planner.spawn_planner=false` in the route.

If the current model cannot safely perform the required planning judgment, stop with `NEEDS_STRONGER_EXECUTOR`; creating another planner behind the user's back is not a valid fallback.

## Confirm the session budget

Before creating any work session, ask the user to confirm one bounded budget covering the whole root task:

- maximum total non-planner sessions;
- maximum worker sessions, including implementation, repair, and integration;
- maximum tester/verifier sessions;
- maximum reviewer sessions.

Offer a compact default such as `total=4, workers=2, testers=1, reviewers=1`, but wait for confirmation unless an active, current shared-memory rule already records the user's limit. A concurrency limit is a ceiling, not a target. Never represent an omitted limit as unlimited.

Persist confirmed limits in the route and session-pool ledger. If all eligible sessions are busy or a role limit is exhausted, queue the lane instead of spawning another Luna/Luna Max session.

## Reuse idle sessions by affinity

Maintain a durable session-pool ledger with session ID, role class, model/effort, state, worktree, affinity tags, loaded Memory Pack revision, last lane, and last activity.

When a lane becomes ready:

1. Find an idle session with the correct role class, model, permissions, and compatible worktree.
2. Prefer exact component/domain affinity, then adjacent technology or verification affinity, then the least-recently-used compatible session.
3. Send a self-contained follow-up packet to that existing session through the host's resume/message adapter.
4. Spawn only when no compatible idle session exists and both the role limit and total limit have capacity.
5. Otherwise keep the lane queued and wait for a compatible session to become idle.

Do not reuse a session when it has unresolved writes, a stale generation, incompatible permissions, contradictory shared memory, or an ambiguous terminal state. Fence or settle it first. Reuse preserves useful caches and working context, but the new packet remains authoritative and must replace stale task assumptions.

Run `scripts/schedule_sessions.py` to produce deterministic `reuse | spawn | queue` recommendations. The script does not create or message sessions; the planner applies the recommendation through the available runtime adapter and records the actual action.

## Shared Memory Pack

The planner and every child session load one versioned shared collaboration pack before task-specific context. Build it from PKOS Memory in Notion using `pkos-memory-context-router`, selecting only active, currently valid, low-sensitivity procedural constraints relevant to the task.

The pack contains:

- Memory Pack revision and source Notion page/Memory IDs;
- confirmed session budget and reuse policy;
- local-versus-remote execution boundary;
- design-system/Figma gates;
- repository, project, security, deployment, and collaboration rules shared by all lanes;
- conflicts, unresolved items, and validity timestamp.

Store the compiled snapshot under the run directory and include its path plus canonical Notion source refs in every Task Packet. Under the current collaboration policy, every child must verify the referenced current memories through its own direct Notion access before work starts. The planner-compiled snapshot is a bounded handoff and recovery aid, not a substitute for that direct read. If direct Notion access is unavailable, keep the lane blocked and report `BLOCKED_EXTERNAL_BOUNDARY`; do not dispatch it under stale or second-hand memory. A child acknowledges the exact pack revision and direct source refs in its result artifact. A result with missing direct access or a mismatched required Memory Pack cannot settle.

Task-specific source files are not shared memory. Keep them in `context_refs` and avoid copying the parent transcript.

## Execution environment boundary

Resolve the current environment policy from shared memory. For the user's current policy, the local machine is development-only. Source inspection and code editing may happen locally; resource-consuming work runs in the canonical remote environment alias `remote-12` after the relevant pushed revision is pulled there.

Treat these as remote-required unless the user explicitly changes the active memory:

- tests and test fixtures that execute code;
- builds, packaging, migrations, and benchmarks;
- Docker/container lifecycle;
- deployment, recovery, and runtime verification;
- other resource-intensive validation.

Every verification item declares `kind` and `environment`. Before remote work, verify a clean authorized remote checkout, perform a fast-forward pull of the intended revision, and record remote revision plus evidence. Do not silently fall back to local execution when the remote environment is unavailable; return `BLOCKED_EXTERNAL_BOUNDARY` with the unrun checks.

Keep credentials, tokens, private host details, and volatile runtime state out of the route and Memory Pack. Use stable environment aliases and canonical private runbooks.

## Figma gate for UI changes

If a lane changes user-visible UI, interaction, layout, component variants, or visual states:

1. load the connected Figma plugin and its mandatory prerequisite skills;
2. locate the canonical Figma file/components;
3. update or approve the design before implementation;
4. freeze node IDs, states, responsive behavior, tokens, and acceptance evidence;
5. include the Figma evidence ref and required Figma skills in the worker packet.

Do not dispatch UI implementation before this gate passes. If Figma is unavailable or the canonical design cannot be identified, return `BLOCKED_EXTERNAL_BOUNDARY` instead of inventing the design in code.

## Task packet context manifest

Every dispatched packet explicitly lists:

- `memory_pack_ref` and canonical Notion source refs;
- `required_skills` the child must load;
- `standards_refs` and repository instructions;
- execution environment and remote pull rule;
- Figma evidence when UI is in scope;
- session affinity and whether the session was reused;
- exact ownership, exclusions, acceptance, verification, and completion artifact.

The planner is responsible for selecting the relevant standards and skills. Telling a worker only what to build, without telling it which governing constraints to load, is an incomplete dispatch.
