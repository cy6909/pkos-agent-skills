# Product-first organization and v3 migration

## Authority

TD-01 is the current main task and combines planner, scheduler, integration owner, and final acceptor. No planner child and no INT-01 exist in org-v4. Product developers own disjoint code scopes. T-SHARED-01 independently tests eligible handoffs. RB-01 is optional and read-only. PK-01 is the gate-only sole Notion writer. Children never delegate.

## Default organization

```text
TD-01 current main task
D-01..03 up to three persistent affinity-matched product developers
T-SHARED-01 one shared independent tester
PK-01 gate-only, queued/settled outside five write points
RB-01 or CI-01 only when triggered and within caps
```

All formal children are sidebar-visible `create_thread` tasks with stored threadId, hostId, lane, worktree, route, cursor, state, affinity, and evidence links. A related feature or repair uses follow-up on the same developer task.

## Ownership

Every writer packet names exact owned files/modules. TD-01 resolves overlapping routers, schemas, migrations, generated files, lockfiles, localization/navigation registries, and shared test fixtures before dispatch. Active overlaps fail G1; “resolve later during cherry-pick” is forbidden.

## org-v3 migration

Run `scripts/migrate_org_v3.py` against a checkpointed v3 manifest. Preserve evidence, receipts, checkpoints, generation, epoch, thread IDs, and settled results. Make TD-01 integration owner; retain at most three developer tasks; select one tester task for shared reuse; archive extra testers, INT-01, and idle Reviewer from the active registry; convert PK-01 to gate-only.

Old packets remain historical evidence. Any registered/queued/active/attention v3 packet is `REPACK_REQUIRED` and cannot dispatch until TD-01 supplies a truthful seven-field task-packet-v3 within 1200 characters. Never invent missing Feature ID, frozen requirement, owned scope, base SHA, or acceptance criteria.
