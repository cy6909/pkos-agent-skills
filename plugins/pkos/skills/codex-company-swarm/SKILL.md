---
name: codex-company-swarm
description: Run an end-to-end software project as a centrally managed GPT-5.6 Sol Max engineering organization with the current session as Technical Director, persistent Notion coordination, Review Board gates, paired developers and testers, MFSQ security/performance coverage, CI/Jenkins enforcement, single-owner integration, durable checkpoints, takeover recovery, end-to-end traceability, and PKOS canonical writeback. Use only for explicit maximum-quality, high-concurrency, token-insensitive project delivery.
metadata:
  short-description: Sol Max company swarm with durable Notion coordination
---

# Codex Company Swarm v0.5

Operate one software outcome as a managed engineering company, not a loose set of chats. Every active role requests `gpt-5.6-sol` with `model_reasoning_effort="max"`; high reasoning never relaxes ownership, evidence, context freshness, or external-action boundaries.

This Skill extends PKOS and `codex-sol-luna-workflow`. It adds a **Notion Durable Coordination Plane** for cross-session state, append-only event history, evidence pointers, Feature projection, context brokerage, checkpoints, recovery, and retrospective. It does not create a second project-knowledge or memory system.

## Command contract

- The current Skill-loading session is logical Technical Director `TD-01`; never spawn another Director.
- Only TD-01 controls staffing, route, generation, shared contracts, candidate freeze, and final user reporting. All children use `may_delegate=false`.
- Provision persistent `PK-01` before RB-01 or delivery lanes. PK-01 is the single Notion coordination writer for the whole run, not a final-only scribe.
- Codex messages are low-latency transport; `.pkos` is the write-ahead/outbox/checkpoint store; Git/CI/Figma are executable or visual evidence; Notion is the durable coordination projection; PKOS canonical nodes own durable project truth and memory.
- Every material Session/Lane/Feature/Pack/Context/Defect/CI/Candidate/Gate/Takeover transition emits a structured event and receives a verified Notion receipt before its dependent barrier releases.
- Every product developer is reciprocally paired with one independent tester. Developers write product code only; testers own test scope, test code, CI interpretation, defects, and lane test verdict.
- Only `INT-01` creates the cumulative candidate. Lanes do not merge directly into the integration branch.
- Every active result carries `run_id`, `generation`, `director_epoch`, `pack_revision`, candidate/base identity, Source Manifest or snapshot hash, and evidence references. Preserve but reject stale results.
- A report is not evidence. Exact commits, paths, tests, CI runs/reports, checksums, review verdicts, and Notion receipts decide acceptance.
- Never claim model identity, child sessions, Jenkins, deployment, Notion writes, CI, or PKOS writeback without observed evidence.

Read [organization and command chain](references/organization-and-command-chain.md) and [Notion Durable Coordination Plane](references/notion-durable-coordination-plane.md) before provisioning.

## Organization

```text
User / Product Sponsor
└── TD-01 Technical Director (current logical root; sole staffing authority)
    ├── PK-01 Coordination & Governance Scribe (persistent single Notion writer)
    ├── RB-01 Review Board Chair (persistent read-only gate owner)
    │   └── AR-01 Requirements & Architecture Analyst (optional)
    ├── D-FE Frontend Developer       ↔ T-FE Frontend Quality Engineer
    ├── D-BE Backend Developer        ↔ T-BE Backend Quality Engineer
    ├── D-AND Android Developer       ↔ T-AND Android Quality Engineer
    ├── D-IOS iOS Developer           ↔ T-IOS iOS Quality Engineer
    ├── D-AI AI/Data Developer        ↔ T-AI AI/Data Quality Engineer
    ├── D-PLAT Platform Developer     ↔ T-PLAT Platform Quality Engineer
    ├── TM-01 Test Manager
    ├── CI-01 CI/CD & Jenkins Engineer
    ├── SQ-01 Security & Performance Quality Engineer
    └── INT-01 Integration Owner
```

Create only justified roles. Explicit invocation authorizes a default ceiling of 24 child sessions, subject to the runtime's lower hard limit.

## Phase 0 — establish durable coordination

Before ordinary staffing, TD-01 must:

1. Inspect applicable `AGENTS.md`, requirements, Git state, relevant code/tests/design, and execution environments without recursively reading the repository.
2. Resolve the PKOS Project Root, Memory Root, one Feature Registry, current canonical nodes, and external-action authority.
3. Classify Notion as `DIRECT_WRITABLE | DIRECT_READ_ONLY | BROKERED | UNAVAILABLE`.
4. Provision PK-01 and discover the minimal coordination schema:
   - Swarm Run & Lane Registry;
   - Event & Decision Ledger;
   - Evidence Registry;
   - coordination fields on the existing Feature Registry.
5. Search Before Create. Bind existing databases first; create missing schema only with authorized Notion writes. Otherwise produce a proposed schema and enter degraded mode.
6. Create the Run record, `RUN_CREATED` event, idempotent outbox item, verified receipt, contiguous sync watermark, bounded Shared Collaboration Pack, Source Manifest, and initial checkpoint/resume token.
7. Validate the initial coordination bundle before RB-01 or delivery lanes start.

Full `COMPANY_SWARM_ACCEPTED` requires a writable, `READY`, `IN_SYNC` Notion coordination plane. Read-only/unavailable operation may continue safe repository work to a checkpoint but cannot claim certified durable coordination.

## Durable artifacts

```text
.pkos/company-swarm/<run-id>/
├── 00-charter.md
├── 01-shared-memory-pack.md
├── 02-org.json
├── 03-feature-inventory.json
├── 04-route.json
├── 05-ci-capability.json
├── coordination/
│   ├── coordination-state.json
│   ├── event-ledger.json
│   ├── notion-schema.json
│   ├── notion-sync.json
│   ├── traceability.json
│   ├── checkpoint.json
│   ├── resume-plan.json
│   ├── outbox/ receipts/ dead-letter/
│   ├── pack-deltas/ context-requests/ checkpoints/
├── lanes/<lane-id>/ task-packet, results, tests, defects, evidence
├── integration/ manifest, candidate, pipeline evidence
├── reviews/ G0, G1, G4, return orders
├── retrospective.md
├── dashboard.md
└── pkos-writeback.json
```

Chat history is transport, never the run ledger.

## Event/outbox discipline

TD-01 authorizes event sequence and state transition. PK-01 writes the local outbox first, performs an idempotent Notion write, reads back/verifies the affected row, stores a receipt, advances the highest contiguous confirmed watermark, and updates current projections.

Sync classes:

- `S0 EPHEMERAL`: no Notion write;
- `S1 PROGRESS`: coalesce into the next checkpoint;
- `S2 CONTROL`: sync before dependent handoff/barrier;
- `S3 GATE`: sync before Gate settles;
- `S4 GOVERNANCE`: sync before acceptance when durable truth changed.

Required event families cover Run, Session, Lane, Task, Context, Pack, Feature, Handoff, Test, Defect, CI, Evidence, Candidate, Gate, Checkpoint, Takeover, PKOS writeback, retrospective, acceptance, and block. `IN_SYNC` requires watermark = latest sequence and zero pending/dead-letter S2–S4 entries.

```bash
python scripts/validate_event_ledger.py coordination/event-ledger.json
python scripts/validate_notion_sync.py coordination/notion-sync.json
```

Read [event sync and outbox](references/event-sync-and-outbox.md).

## Context and Pack freshness

Each child receives a bounded task packet with run/generation/Director epoch/Pack revision, role/lane, worktree and write scope, pair, acceptance IDs, blockers, artifact destinations, and one of:

- `DIRECT_VERIFIED`: directly verify named Notion canonical sources;
- `BROKERED_SNAPSHOT`: consume a PK-01/TD-01 bounded hash-addressed snapshot;
- `BLOCKED_CONTEXT_FRESHNESS`: stop because required current facts cannot be established.

Missing facts emit `CONTEXT_REQUESTED`; PK-01 returns only the relevant nodes/evidence and emits `CONTEXT_SUPPLIED`. Shared C2+ contract, interface, schema, security, environment, CI, design, or authority changes create a Pack Delta with `from/to`, source revisions, change class, affected lanes/sessions, invalidated artifacts, mandatory acknowledgements, and generation/compatibility decision. No affected handoff or Gate advances until all required acknowledgements settle.

```bash
python scripts/validate_pack_delta.py coordination/pack-deltas/<revision>.json
```

Read [context pack versioning](references/context-pack-versioning.md).

## G0 — requirements, gap, path, and Feature review

RB-01 produces one evidence-backed package containing normalized requirements/assumptions/exclusions/acceptance, current-state and requested-gap matrices, implementation options and selected path, architecture/interface/data/security/deployment freezes, migration/rollback, complete Feature inventory (`implement | modify | optimize | performance | security | migration | operations | documentation`), domain/platform impact, developer/tester pairs, MFSQ/CI intent, dependency/ownership/integration plan, PKOS owner mapping, and `GO | GO_WITH_ACTIONS | REPLAN`.

PK-01 registers Run/Feature/requirement/evidence projections and confirms the G0 verdict/checkpoint before implementation begins.

## G1 — organization and delivery readiness

Verify isolated worktrees and disjoint ownership, reciprocal pairs, current epoch/Pack and settled Context Requests, frozen/versioned contracts, MFSQ strategy, canonical test environment, CI state (`EXISTS_VALID | EXISTS_GAPPED | MISSING | BLOCKED`), Jenkins bootstrap lane when missing, Figma/design prerequisites, security/data/migration/rollback, external authority, Notion schema/mode/watermark, and traceability plan.

PK-01 projects Features `ANALYZED -> READY`, registers Session/Lane/Task records, and confirms G1/checkpoint. Missing CI may allow implementation in parallel with bootstrap but blocks G2–G4. Missing writable Notion blocks certified acceptance.

## Parallel implementation and test preparation

Developers implement product scope in isolated worktrees while paired testers design/review MFSQ tests; CI-01 repairs/bootstraps source-controlled delivery; SQ-01 prepares security/performance coverage; PK-01 continuously settles material events and evidence pointers. Ordinary thought logs, compile output, and micro-edits stay S0/S1 and do not pollute Notion.

Feature projections move through `PLANNED -> ANALYZED -> READY -> IN_DEVELOPMENT -> DEV_HANDOFF -> IN_TEST -> TEST_PASSED | DEFECT_RETURN | BLOCKED -> INTEGRATING -> IN_REVIEW -> ACCEPTED`.

## MFSQ

- **M — Mission & Model:** requirement, component, interface, data/state/migration/platform coverage.
- **F — Functional & Flow:** happy, alternate, negative, boundary, concurrency, retry, idempotency, rollback, recovery.
- **S — Security & Safety:** identity, authorization, validation, data/secrets/supply-chain/abuse/isolation/privacy/failure safety.
- **Q — Quality Attributes:** performance is mandatory for behavior changes; also reliability, compatibility, accessibility, observability, maintainability, resource use, recoverability.

Every change has M/F/S/Q disposition or RB-01-approved N/A. Every executable case maps to version-controlled test code and a canonical pipeline stage.

## G2 — developer/tester settlement

Developer handoff includes exact base/head, paths, acceptance mapping, migrations/runtime effects, risks/exclusions, feedback outcomes, pair, current epoch/Pack, and committed candidate. The paired tester independently decides final scope, implements tests, runs exact-candidate canonical CI, opens/closes structured defects, and issues lane verdict. Testers never repair product code; developer claims never close defects.

Before settlement, PK-01 confirms `DEV_HANDOFF`, test-plan review, P0/P1 defect transitions, CI/evidence, lane verdict, and Feature projection.

## CI/CD and Jenkins

CI-01 reuses a valid canonical provider, repairs gapped source-controlled CI, or bootstraps Jenkins Pipeline as Code only when no usable provider exists. Prefer `Jenkinsfile`, multibranch discovery, reproducible agents, credentials by reference, retained JUnit/security/performance reports, artifacts/SBOM, test-environment deployment, and safe release gates. Local-only results cannot settle G2–G4. Evidence Registry pointers retain candidate commit, producer/verifier, URI, checksum, retention, and status.

## G3 — cumulative integration

Only INT-01 applies settled current-generation/current-epoch/current-Pack lane/test commits in dependency order, resolves mechanical conflicts, runs the full canonical pipeline, and freezes one immutable candidate. Event ledger, coordination projection, watermark, traceability, contracts, migrations, security/performance, and checkpoint must agree. PK-01 projects Features into `INTEGRATING` and confirms candidate/evidence/checkpoint records.

## G4 — Review Board

RB-01 reviews one frozen candidate in one pass against G0/G1 contracts, implementation completeness, MFSQ traceability, unchanged-code interactions, security/performance, migration/rollback/operations, exact-candidate CI, Pack/epoch freshness, pending/dead-letter events, artifact retention, and PKOS obligations.

Return exactly `ACCEPT | RETURN_TO_LANE | REPLAN_ORG | BLOCKED_EXTERNAL_BOUNDARY`. PK-01 confirms verdict/findings/checkpoint. A return increments generation for affected lanes, preserves accepted independent work, updates Feature projections, and invalidates affected route/Pack/test/review artifacts. Three same-architecture repairs maximum.

## Traceability

Maintain and validate:

```text
Requirement -> Feature -> Acceptance -> Lane/Packet -> Product Commit
-> MFSQ Test/Test Commit -> exact-candidate CI and reports
-> Security/Performance Evidence -> G4 Verdict
-> Notion Canonical Owner and verified write receipt
```

Accepted delivery requires complete links, no open P0/P1, no orphan evidence, exact-candidate CI PASS, and confirmed Notion writeback for durable changes.

```bash
python scripts/validate_traceability.py coordination/traceability.json
python scripts/validate_coordination_bundle.py coordination/
```

## Checkpoint, resume, and TAKEOVER

Create checkpoints at G0, G1, handoff batches, candidate freeze, every G4 verdict/return, before/after takeover, and G5 completion/block. Record event/state version, generation, Director runtime/epoch, Pack revision, Notion watermark/run record, candidate, sessions/lanes, artifact checksums, pending outbox, resume token, and verifiers.

A replacement runtime may assume logical TD-01 only with observable authority. Append `TAKEOVER`, increment `director_epoch` exactly one, update and verify the Notion Run record, invalidate stale runtime refs, and reissue affected packets. Old-epoch results cannot mutate current state.

```bash
python scripts/validate_checkpoint.py coordination/checkpoint.json --ledger coordination/event-ledger.json
python scripts/build_resume_plan.py coordination/checkpoint.json --takeover --output coordination/resume-plan.json
```

Read [checkpoint, resume, and takeover](references/checkpoint-resume-and-takeover.md).

## G5 — acceptance, canonical writeback, dashboard, retrospective

TD-01 may accept only after RB-01 `ACCEPT` for the exact candidate and all of these pass:

1. Coordination bundle validation.
2. Notion `DIRECT_WRITABLE`, schema `READY`, watermark at latest event, zero pending/dead-letter S2–S4 events.
3. Complete traceability, exact-candidate CI PASS, no open P0/P1.
4. Current Pack/epoch acknowledged by all relevant sessions.
5. Feature Registry projection and Current Truth/Audit/ADR/Incident/Memory obligations confirmed with receipts.
6. Required Git/CI/design/run artifacts retained with stable pointers/checksums.
7. Final checkpoint/resume token and evidence dashboard.
8. Retrospective covering plan-vs-actual, repairs, defects, coordination/barrier delays, security/performance change, weak evidence, and prevention lessons.
9. Only stable reusable lessons become procedural Memory; transient sessions/logs remain episodic or are discarded.

The dashboard reports Gate/state version/epoch/Pack/checkpoint, organization and pairs, Feature projection, Notion mode/schema/watermark/outbox/dead letters/receipts, Context Requests, traceability, CI, MFSQ, security/performance, reviews, writeback, and residual risk.

## Final statuses

- `COMPANY_SWARM_ACCEPTED`
- `COMPANY_SWARM_CHECKPOINT`
- `RETURNED_TO_LANES`
- `REPLAN_ORGANIZATION`
- `BLOCKED_MODEL_CONFIG`
- `BLOCKED_RUNTIME`
- `BLOCKED_CONTEXT_FRESHNESS`
- `BLOCKED_NOTION_COORDINATION`
- `BLOCKED_CI`
- `BLOCKED_EXTERNAL_BOUNDARY`

The final report distinguishes observed from proposed work and includes organization, model confidence, generation/epoch/Pack, Notion mode/schema/watermark/receipts, changed scope, candidate/CI, Review verdict, repairs, traceability, PKOS writeback, checkpoint, unrun evidence, and residual risk.

## Validation

```bash
python plugins/pkos/skills/codex-company-swarm/scripts/validate_install.py
python -m unittest discover -s plugins/pkos/skills/codex-company-swarm/tests -v
python scripts/validate.py
```

Runtime smoke-test schema binding, outbox receipts, context modes, Pack Delta reload, one developer/tester pair, CI evidence, integration, checkpoint/resume, authorized takeover, traceability, and canonical writeback before production-critical use.
