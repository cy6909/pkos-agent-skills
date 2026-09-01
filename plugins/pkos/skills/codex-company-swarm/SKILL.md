---
name: codex-company-swarm
description: Deliver acceptable product features per Token through one planning/integration session, up to three reusable visible developer tasks, one shared independent tester, one cumulative candidate, bounded on-demand review/Notion/CI, remote-only verification, and evidence-gated acceptance. Use only for Company Swarm delivery.
metadata:
  short-description: Product delivery per Token with one cumulative candidate
---

# Codex Company Swarm

Treat this file as an executable control program. Do not preload its references.

## Registers

Optimize acceptable product delivery per Token, not organization completeness or active-task count:

```text
STATE   = BOOT -> G0 -> G1 -> EXEC/G2 -> G3 -> G4 -> G5
RUN     = {run_id, generation, director_epoch, task_registry, token_control}
CAND    = exactly one cumulative candidate, maintained by TD-01
METRICS = accepted features; candidate time; tokens/accepted feature;
          coordination/total tokens; strict-review returns; real-browser pass rate
ROOT    = .pkos/company-swarm/<run_id>/
```

## Invariants

1. This current visible task is `TD-01`, the sole planner, scheduler, and cumulative integrator. Never create another planner or `INT-01`.
2. Default registered organization is TD-01, at most three mutually exclusive product developers, one shared independent tester, and gate-only PK-01. Reviewer/CI are created or reused only when triggered.
3. Each child is a visible Codex task created with `create_thread` and `may_delegate=false`; hidden subagents and summary-only tasks are forbidden.
4. Active child hard cap is 6; registered visible-task hard cap is 8. Reuse the affinity-matched developer for related work and later generations.
5. At least 70% of productive child concurrency implements product code. Waiting, reporting, repeated context, and blocked-environment work is never productive.
6. Maintain one candidate per generation. Integrate each self-tested lane immediately into it; do not wait for every lane or maintain parallel candidates.
7. Every writer has one frozen owned scope. TD-01 adjudicates shared files before dispatch.
8. `NOTION_WRITE_LANGUAGE=zh-CN`; PK-01 is the only Notion writer and works only in gate batches.
9. Claims never settle work. Require exact pushed SHA, remote-12 clean checkout, tests/build, browser evidence when applicable, candidate identity, and receipts.
10. Never invent sessions, model identity, CI, deployment, browser, Notion, or external authority.
11. `TAKEOVER` increments `director_epoch`, checkpoints first, and reissues only stale packets to reusable visible tasks.

## Reference loading

| Need | Load |
|---|---|
| Staffing, reuse, Token/concurrency calculation | `references/visible-task-staffing-and-concurrency.md` |
| Authority, ownership, org-v3 migration | `references/organization-and-command-chain.md` |
| Developer self-test/shared tester handoff | `references/developer-tester-handoff.md` |
| Candidate integration/reviewer/consolidation | `references/review-gates-and-delivery-lifecycle.md` |
| Progressive P0→P2 testing | `references/mfsq-quality-model.md` |
| CI preflight and Stop Rule | `references/jenkins-pipeline-contract.md` |
| Gate-batched Chinese Notion writes | `references/notion-durable-coordination-plane.md` |
| Pack deltas only | `references/context-pack-versioning.md` |
| Checkpoint/takeover | `references/checkpoint-resume-and-takeover.md` |
| Final traceability/metrics | `references/traceability-and-retrospective.md` |
| Install/smoke test | `references/runtime-installation.md` |

Never load `references/research-sources.md` during execution.

## Task and settlement budgets

Each child Task Packet is at most 1200 Chinese characters and contains only:

```text
feature_id | frozen_requirements | owned_files_modules | base_sha
acceptance_criteria | prohibitions | notion_links
```

Do not copy chat history. Later messages send deltas only and never repeat the Memory Pack. Settlement is at most 600 Chinese characters; detailed logs live in files/evidence pages and the response carries links plus a compact result.

Estimate total and coordination tokens after every settlement and Gate. If coordination/reporting/Notion exceeds 30%, enter `CONSOLIDATION_MODE`: stop new tasks; allow only integration, repair, test, deployment, and required gate writeback.

## BOOT — minimum viable control

1. Read applicable `AGENTS.md`, exact requirements, Git/design state, existing PKOS owners, and external authority.
2. Register this task as TD-01 and one live cumulative candidate based on the exact base SHA.
3. Compile one bounded shared Pack; child packets link only necessary Notion sources.
4. Set org-v4 budgets: developers 3, shared tester 1, active children 6, registered 8, product share 70%.
5. Enforce environment policy: Windows local is editing/static Git/scheduling only; build/test/deploy/diagnose/Docker/services run on `remote-12`; Web acceptance uses only the public production domain and real `cy6909` Chrome; GitHub Actions, local private origin, local service/test/Docker are forbidden.
6. For org-v3, checkpoint first and run `scripts/migrate_org_v3.py`; old evidence remains valid, but pending old packets must be reissued as v3 packets before dispatch.

## G0 — freeze product work

Freeze stable Feature IDs, P0 acceptance, dependencies, owned files/modules, exact base, risk, deployment/browser method, and candidate integration order. Use at most three disjoint product lanes. Resolve shared router/schema/migration/generated files to TD-01 or one lane now—not at cherry-pick time.

PK-01 may batch-write requirement freeze to the original Product Feature Registry, then returns queued/settled. Do not create a duplicate summary database.

## G1 — prove executable readiness

Validate org-v4, seven-field packet size, visible task IDs/worktrees, ownership, model route, shared Pack revision, remote-12 authority, Figma evidence for UI, developer self-test method, progressive test plan, CI preflight plan, Token baseline, and one candidate. Ordinary clear work starts without Reviewer.

## EXEC/G2 — implement, self-test, integrate continuously

Developers implement only owned product scope. Before independent-test handoff each developer provides:

```text
exact pushed SHA
remote-12 clean checkout
directed tests
typecheck/build
Web: public production + real cy6909 Chrome self-test
```

No complete developer self-test means no tester handoff. The shared tester does not replace developer self-test and prioritizes MFSQ layer 1: P0 smoke and critical writes. Layer 2 covers exceptions/idempotency/permissions; layer 3 covers performance/long-run/cross-device only after layer 1 passes.

When a lane self-test passes, TD-01 immediately integrates that SHA into the same candidate, resolves only pre-adjudicated mechanical effects, updates candidate SHA, and sends the delta to the shared tester. Do not wait for all lanes.

Every reconciliation reuses related visible tasks first. If many tasks are active but fewer than three are productive, reclaim waiting slots immediately. If no new cumulative candidate and no accepted Feature appear for 120 minutes, enter `CONSOLIDATION_MODE` and stop creating tasks.

## CI Stop Rule

Before CI work, complete within 10 minutes: controller, executor, credentials, job creation, and artifact space. If any prerequisite fails twice or blocks over 15 minutes, stop CI immediately, report exact blocker/reason/authority/recovery, release capacity to product development, and forbid unbounded diagnosis or scope expansion. Reuse project-approved CI; if none exists, follow governance fallback without GitHub Actions.

## G3 — freeze the single candidate

Freeze the current cumulative candidate only after required integrated Features, self-test evidence, shared independent test, deployment path, traceability, and P0/P1 disposition agree. There is no separate integration task and no second candidate.

## G4 — conditional strict review

Start/reuse one Reviewer only after candidate freeze and only for high-risk security/ledger/migration/permission work, explicit strict acceptance, or behavior TD-01 finds clearly abnormal. Ordinary clear tasks do not receive early Reviewers.

Two consecutive strict-review returns stop new Features and force root-cause consolidation. Repairs update the same candidate through a new generation; preserve independent accepted evidence.

## G5 — deploy and accept

Accept only the exact candidate with required remote-12 checks, public-production real-browser acceptance for Web, open P0/P1=0, traceability, authorized residual risk, and verified gate writebacks. Report only 60-minute increments:

```text
accepted-feature delta | candidate SHA | passed real gates | P0/P1 blockers
productive code output per lane | estimated Token direction
```

PK-01 batch-writes only at requirement freeze, lane handoff, candidate freeze, strict-review terminal, and deployment/real-acceptance terminal. Each Feature row records developer, tester, review/integration session, round result, Accepted Candidate, acceptance method, evidence/gaps, and next action.

## Validators

```bash
python scripts/validate_org.py assets/examples/organization.example.json
python scripts/validate_org.py assets/examples/ci-stop-rule.example.json
python scripts/validate_org.py assets/examples/consolidation-after-stall.example.json
python scripts/validate_org.py assets/examples/affinity-session-reuse.example.json
python scripts/validate_org.py assets/examples/reviewer-after-freeze.example.json
python scripts/validate_org.py assets/examples/notion-gate-batch.example.json
python scripts/migrate_org_v3.py assets/examples/organization-v3-legacy.example.json --output migration.json
python scripts/validate_install.py
```

## Final statuses

```text
COMPANY_SWARM_ACCEPTED | COMPANY_SWARM_CHECKPOINT | CONSOLIDATION_MODE
RETURNED_TO_LANES | BLOCKED_CI_STOP_RULE | BLOCKED_EXTERNAL_BOUNDARY
BLOCKED_RUNTIME | BLOCKED_CONTEXT_FRESHNESS | BLOCKED_NOTION_COORDINATION
```

Final report includes default session counts, productive-concurrency calculation, Token controls, Stop Rule, single-candidate convergence, accepted features/browser rate, and legacy migration state.
