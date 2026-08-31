---
name: codex-company-swarm
description: Orchestrate maximum-quality parallel delivery with this session as TD-01, Director-routed visible Codex tasks, bounded concurrency, persistent PK-01 Notion coordination, paired development/testing, exact-candidate review, recovery, traceability, and PKOS writeback. Use only for Company Swarm delivery.
metadata:
  short-description: Visible, routed, budgeted delivery with durable coordination
---

# Codex Company Swarm

Treat this file as an executable control program. Do not preload its references.

## Registers

```text
RUN   = {project_id, run_id, generation, director_epoch, pack_revision, staffing_budget, concurrency_state, task_registry}
STATE = BOOT -> G0 -> G1 -> EXEC -> G2 -> G3 -> G4 -> G5
ROOT  = .pkos/company-swarm/<run_id>/
ROUTE = TD-01 selects model + reasoning_effort + rationale + risk per packet
```

Storage roles:

```text
Codex messages = low-latency transport
ROOT            = events, receipts, checkpoints, manifests
Git/CI/Figma    = executable or visual evidence
Notion          = durable coordination projections and event/evidence indexes
PKOS nodes      = canonical project truth and long-term memory
```

## Invariants

1. Current session is logical `TD-01`; never spawn a second Director.
2. Only TD-01 changes staffing, shared contracts, generation, candidate freeze, takeover, or final status. Children set `may_delegate=false`.
3. Provision `PK-01` first. It is the sole Notion writer; other roles only read or emit event candidates.
   Notion human text uses `NOTION_WRITE_LANGUAGE=zh-CN`.
4. Pair every product developer with one independent tester. Developer owns product code; tester owns test scope/code, CI interpretation, defects, and lane verdict.
5. Only `INT-01` creates the cumulative candidate.
6. Every mutable result carries current `{run_id, generation, director_epoch, pack_revision}` plus base/candidate identity and evidence refs. Reject stale values.
7. Settlement requires commits, tests, exact-candidate CI/reports, verdicts, and verified Notion receipts.
8. Never invent model identity, sessions, external writes, Jenkins, deployment, CI, or Notion/PKOS success.
9. Every execution role is a sidebar-visible Codex task. Hidden subagents are not Company Swarm roles; child packets set `may_delegate=false`.
10. TD-01 alone schedules within hard caps, reuses affinity tasks, and preserves ownership/single-writer barriers.

## Reference loading

Load only the row needed for the next transition; stop reading once that transition is executable. Load a second reference only when the first exposes a blocker.

| Condition | Load |
|---|---|
| Staff, authority, ownership, session lifecycle | `references/organization-and-command-chain.md` |
| Model routing, visible tasks, budgets, scheduling | `references/visible-task-staffing-and-concurrency.md` |
| Bind/create Notion coordination schema | `references/notion-durable-coordination-plane.md` |
| Outbox, receipts, watermark, replay | `references/event-sync-and-outbox.md` |
| Context Request, Source Manifest, Pack Delta | `references/context-pack-versioning.md` |
| Gate semantics and repair generations | `references/review-gates-and-delivery-lifecycle.md` |
| Developer/tester handoff or defect routing | `references/developer-tester-handoff.md` |
| MFSQ case design | `references/mfsq-quality-model.md` |
| CI discovery or Jenkins bootstrap | `references/jenkins-pipeline-contract.md` |
| Resume or Director takeover | `references/checkpoint-resume-and-takeover.md` |
| G4/G5 completeness and retrospective | `references/traceability-and-retrospective.md` |
| Canonical Feature/Current Truth/Memory writeback | `references/pkos-memory-and-notion-integration.md` plus shared PKOS refs only as needed |
| Install or smoke test | `references/runtime-installation.md` |

Never load `references/research-sources.md` during execution.

## BOOT — establish control plane

```text
INPUT  = user goal + repo + available tools
OUTPUT = RUN, org, schema binding, Pack, initial checkpoint
```

1. Inspect applicable rules, requirements, Git/code/test/design state, environments, and external authority; resolve canonical PKOS roots/owners.
2. Provision PK-01; classify Notion, Search Before Create, bind/propose coordination stores, and persist `RUN_CREATED` through outbox, verified receipt, and watermark.
3. Compile bounded Shared Pack/Source Manifest and a checksummed checkpoint/resume token.
4. Register this visible task as TD-01; set/reconcile staffing (defaults: lanes 3, target 6, minimum 4, active hard cap 8, registered hard cap 12).
5. Validate organization and coordination bundle before RB-01 or delivery lanes.

`COMPANY_SWARM_ACCEPTED` requires writable, schema-ready, in-sync Notion. Other modes may produce a recoverable checkpoint only.

## G0 — decide what to build

RB-01 returns requirements/Features, platform units/dependencies, atomic acceptances, assumptions/exclusions, gaps/selected freezes, migration/rollback, owners, approved visual+text Test Design, MFSQ/CI/integration/staffing/model plans, evidence, and `GO | GO_WITH_ACTIONS | REPLAN`.

PK-01 projects Features and persists the G0 verdict/checkpoint before implementation.

## G1 — prove readiness

Guard tasks/worktrees/ownership; RUN/Pack; frozen contracts; approved `pkos-mfsq/v2` design/cases; Material gate; CI; staffing; security/migration/rollback; and Notion sync/traceability. Run `validate_mfsq.py` before implementation.

Prefer the project-approved CI. When no approved pipeline exists, use the project-governance fallback (Jenkins Pipeline-as-Code by default). It may run beside implementation but blocks G2-G4 settlement. Persist G1 and checkpoint.

## EXEC + G2 — parallel implementation and lane settlement

Run developers, paired testers, CI-01, SQ-01, and PK-01 concurrently within their scopes.

Reconcile `task_registry` at BOOT, Gates, task events, generation changes and recovery. Wait on at most eight tasks and persist cursors. Below target, reuse an affinity task, create within budget, or record `underfill_reason`. Emit `CONCURRENCY_UNDERFILLED` after 90 seconds below minimum with ready work.

```text
Developer -> product commit + mapped self-tests/case IDs + compact DEV_HANDOFF
Tester    -> independent v2 MFSQ tests + exact-candidate canonical CI + defects + lane verdict
CI-01     -> reuse valid CI, repair gaps, or bootstrap Jenkins
PK-01     -> material events, projections, evidence pointers, receipts
```

Developer handoff must include exact base/head, paths, acceptance mapping, runtime/migration effects, risks/exclusions, pair, RUN freshness, and evidence. Testers never repair product code; developer claims never close defects.

Apply S0-S4 event barriers from the event reference; `IN_SYNC` requires a current watermark and no pending/dead-letter S2-S4 item. Context is `DIRECT_VERIFIED | BROKERED_SNAPSHOT | BLOCKED_CONTEXT_FRESHNESS`; shared C2+ changes require acknowledged Pack Delta, and contract breaks normally start a generation.

## G3 — build one candidate

INT-01 applies only settled current RUN lane/test commits in dependency order, resolves mechanical conflicts, runs the full canonical pipeline, and freezes one immutable candidate. Require agreement among contracts, migrations, event watermark, traceability, security/performance evidence, and checkpoint. Persist candidate and `INTEGRATING` projections.

## G4 — review one frozen candidate

RB-01 reviews the exact candidate once against G0/G1 contracts, implementation, MFSQ, unchanged-code interactions, security/performance, migration/rollback/operations, CI, freshness, event health, artifact retention, and PKOS obligations.

```text
VERDICT = ACCEPT | RETURN_TO_LANE | REPLAN_ORG | BLOCKED_EXTERNAL_BOUNDARY
```

A return creates a new generation for affected lanes, preserves independent accepted work, invalidates affected artifacts, updates Pack/projections, and requires retest. Maximum three same-architecture repair generations.

## G5 — certify or checkpoint

Traceability must be complete:

```text
Requirement -> Feature -> Implementation Unit/Dependency -> Atomic Acceptance
-> approved Test Design -> Lane/Packet -> Product Commit
-> MFSQ Test/expected steps/Test Commit -> exact-candidate CI/reports
-> Security/Performance -> G4 -> Notion canonical owner + verified receipt
```

TD-01 returns `COMPANY_SWARM_ACCEPTED` only when all are true:

```text
coordination bundle PASS
Notion DIRECT_WRITABLE + schema READY + IN_SYNC
pending/dead-letter S2-S4 = 0
current Pack/epoch acknowledged
Material gate + exact-candidate CI PASS; open P0/P1 = 0
traceability PASS; G4 ACCEPT
canonical PKOS writeback receipts confirmed
stable evidence retained
final checkpoint + dashboard + retrospective produced
```

Only stable reusable lessons enter procedural Memory; transient sessions and raw logs do not.

## Recovery

Checkpoint at G0, G1, handoff batches, candidate freeze, every G4 result, takeover, and G5. A replacement runtime may assume TD-01 only with observable authority: validate checkpoint/ledger, replay outbox, append `TAKEOVER`, increment `director_epoch` exactly one, verify the Notion Run projection, and reissue affected packets. Old-epoch results remain evidence but cannot mutate current state.

## Validators

Run from this Skill directory or adapt paths explicitly:

```bash
python scripts/validate_org.py assets/examples/organization.example.json
python scripts/validate_org.py assets/examples/staffing-small-two-lane.example.json
python scripts/validate_org.py assets/examples/staffing-luna-escalation-reuse.example.json
python scripts/validate_mfsq.py assets/examples/mfsq-test-plan.example.json
python scripts/validate_coordination_bundle.py assets/examples/coordination-bundle
python scripts/audit_prompt_budget.py
python scripts/validate_install.py
```

## Final statuses

```text
COMPANY_SWARM_ACCEPTED | COMPANY_SWARM_CHECKPOINT
RETURNED_TO_LANES | REPLAN_ORGANIZATION
BLOCKED_MODEL_CONFIG | BLOCKED_RUNTIME | BLOCKED_CONTEXT_FRESHNESS
BLOCKED_NOTION_COORDINATION | BLOCKED_CI | BLOCKED_EXTERNAL_BOUNDARY
```

Final report separates observed/proposed work and covers RUN freshness, organization, Notion sync, candidate/CI, review, traceability, writeback, checkpoint, unrun evidence, and risk.
