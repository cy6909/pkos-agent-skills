# Product capacity, task reuse, and Token control

## Registers

```text
max_product_lanes=3
hard_cap_active_child_tasks=6
max_registered_visible_tasks_per_run=8
min_product_code_share_percent=70
task_packet_max_chars=1200
settlement_max_chars=600
coordination_ratio_limit=0.30
stagnation_limit_minutes=120
```

`productive_count` includes only active independent work producing product code or current-candidate test evidence. Waiting dependencies, status reports, repeated reads/Memory Pack transmission, and environment-blocked tasks are not productive. `product_code_share = active productive domain-developers / productive_count`. In NORMAL mode it is at least 70%; consolidation may temporarily contain only integration/repair/test/deployment.

Reconcile at BOOT, handoff, candidate update/freeze, attention/settlement, strict-review return, Gate, and recovery. Release waiting slots. If four or more children are active but fewer than three are productive, reclaim waits immediately. Create no task merely to summarize state.

## Affinity reuse

Store `affinity_key`, threadId, hostId, worktree, last feature, generation, state, and cursor. For same/near module work, send only a compact delta to the existing task. Spawn only when no compatible registered task exists and both caps permit it. Never rebuild the Memory Pack in follow-ups.

## Token loop

Estimate total and coordination/reporting/Notion tokens after every settlement and Gate. Track accepted Features, candidate formation minutes, Token per accepted Feature, coordination ratio, strict-review returns, and real-browser pass rate. If coordination exceeds 30%, either candidate or accepted-Feature progress stalls for 120 minutes, or strict review returns twice, enter `CONSOLIDATION_MODE`, set new-task creation false, and allow only integration, repair, test, deployment, and required gate writeback.

Every 60 minutes emit only the six incremental fields named in SKILL.md. Large logs live under ROOT or stable evidence storage.
