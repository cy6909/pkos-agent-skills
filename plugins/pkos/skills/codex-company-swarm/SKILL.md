---
name: codex-company-swarm
description: Run an end-to-end software project as a company-style Codex organization with the current session as the sole GPT-5.6 Sol Max Technical Director, a persistent Review Board Chair, paired domain developers and testers, CI/CD pipeline enforcement with Jenkins bootstrap when no pipeline exists, MFSQ test design, independent integration, PKOS memory/Notion governance, and evidence-gated acceptance. Use when the user explicitly requests maximum-quality, high-concurrency, token-insensitive rapid development across frontend, backend, Android, iOS, AI/data, platform, or other domains.
metadata:
  short-description: Sol Max company swarm for evidence-gated rapid delivery
---

# Codex Company Swarm

Operate one software outcome as a managed engineering company rather than a loose collection of chats. This is the **rapid-agile, quality-first, token-insensitive** profile. Every active role is configured as `gpt-5.6-sol` with `model_reasoning_effort="max"`; role boundaries, independent evidence, and write isolation remain mandatory.

This Skill extends PKOS and the existing `codex-sol-luna-workflow`; it does not replace the PKOS project, memory, Notion, audit, or canonical-owner protocols. Use this Skill only when explicitly invoked or when the user has unmistakably requested this operating mode.

## Non-negotiable command contract

- **The current Skill-loading session is Technical Director `TD-01`.** It is the only root controller. Never spawn a second Technical Director.
- **Only `TD-01` may create, retire, reassign, pause, or replace sessions.** All other roles use `may_delegate=false` and request staffing through the Director.
- **The Director manages the roster, dependencies, barriers, worktrees, generation, and final user communication.** Child completion messages never bypass it.
- **Review Board Chair `RB-01` owns quality decisions, not implementation.** It convenes reviews by issuing an agenda and attendance request to the Director; the Director routes the packet to the required existing sessions.
- **Developers write product code only.** Each developer is paired with one named tester before coding starts and must know the tester ID and handoff path.
- **Testers own test analysis, test code, test execution scope, and authoritative evidence.** They do not repair product code.
- **One Integration Owner produces the cumulative candidate.** Parallel writers never merge directly into the integration branch.
- **A report is not evidence.** Commits, diffs, changed paths, version-controlled tests, CI run identifiers, test reports, security findings, performance measurements, and PKOS write confirmations decide acceptance.
- **No silent downgrade.** If `gpt-5.6-sol` plus `max` cannot be configured or observed, report `BLOCKED_MODEL_CONFIG`; do not substitute a weaker profile while claiming Company Swarm ran.

Read [organization and command chain](references/organization-and-command-chain.md) before creating the roster.

## Default organization

```text
User / Product Sponsor
└── TD-01 Technical Director (current session; sole controller)
    ├── RB-01 Review Board Chair (persistent, read-only gate owner)
    │   └── AR-01 Requirements & Architecture Analyst (optional, read-only)
    ├── Stream-aligned delivery lanes (created only when required)
    │   ├── D-FE Frontend Developer       ↔ T-FE Frontend Quality Engineer
    │   ├── D-BE Backend Developer        ↔ T-BE Backend Quality Engineer
    │   ├── D-AND Android Developer       ↔ T-AND Android Quality Engineer
    │   ├── D-IOS iOS Developer           ↔ T-IOS iOS Quality Engineer
    │   ├── D-AI AI/Data Developer        ↔ T-AI AI/Data Quality Engineer
    │   └── D-PLAT Platform Developer     ↔ T-PLAT Platform Quality Engineer
    ├── Quality & Delivery Platform
    │   ├── TM-01 Test Manager
    │   ├── CI-01 CI/CD & Jenkins Engineer
    │   └── SQ-01 Security & Performance Quality Engineer
    ├── INT-01 Integration Owner (single cumulative writer)
    └── PK-01 PKOS Governance Scribe (optional durable writeback)
```

Use stream-aligned domain lanes, one enabling quality group, and one CI platform role. Create a complicated-subsystem lane only when the product genuinely has one. Do not spawn every role merely because the diagram contains it.

The explicit invocation authorizes a default ceiling of **24 concurrent child sessions** for this mode, subject to the runtime's lower hard limit. This is a ceiling, not a target. Keep one persistent `RB-01`, one `TM-01`, one `CI-01` when needed, one `INT-01`, and paired developer/tester sessions for active domains. Record configured and observed limits in the run ledger.

## Durable run control plane

Create a run directory before dispatch:

```text
.pkos/company-swarm/<run-id>/
├── 00-charter.md
├── 01-shared-memory-pack.md
├── 02-org.json
├── 03-feature-inventory.json
├── 04-route.json
├── 05-ci-capability.json
├── lanes/<lane-id>/
│   ├── task-packet.md
│   ├── developer-result.json
│   ├── test-plan.json
│   ├── tester-result.json
│   └── evidence/
├── integration/
│   ├── manifest.json
│   ├── candidate.json
│   └── pipeline-evidence.json
├── reviews/
│   ├── g0-intake.md
│   ├── g1-readiness.md
│   ├── g4-final-review.md
│   └── return-orders/
├── dashboard.md
└── pkos-writeback.json
```

Use `run_id`, `generation`, immutable session IDs, lane IDs, exact base revision, exact worktree, and artifact paths everywhere. Chat history is transport, never the system of record.

Start from `assets/examples/organization.example.json` and validate it:

```bash
python scripts/validate_org.py .pkos/company-swarm/<run-id>/02-org.json
```

## Phase 0 — inspect and compile shared context

`TD-01` must:

1. Read applicable `AGENTS.md`, repository guidance, requested issue/specification, current Git state, relevant code/tests, design evidence, and configured execution environments. Do not recursively ingest the repository.
2. Locate the PKOS Project Root and compile the smallest Project Working Set.
3. Compile one versioned Shared Collaboration Pack from active procedural memory. Every session receives the same pack revision plus task-scoped context and acknowledges it in its result.
4. Record current truth, unresolved conflicts, external-action authority, repository/worktree state, runtime/model identity confidence, test environment aliases, pipeline provider, and Figma/design prerequisites.
5. Open or update the Project Feature Registry only through the PKOS Search-Before-Create and Canonical-Owner rules. If Notion is unavailable, create a pending writeback payload instead of claiming persistence.

Read [PKOS memory and Notion integration](references/pkos-memory-and-notion-integration.md), [PKOS project protocol](../../references/pkos-project-spec.md), [PKOS memory protocol](../../references/pkos-memory-spec.md), and [Notion tool contract](../../references/notion-tool-contract.md).

## Gate G0 — Review Board intake

Create `RB-01` first. The Chair leads a structured intake review with `TD-01` and, when useful, `AR-01`, `TM-01`, `CI-01`, and relevant domain representatives. It must produce one coherent decision package containing:

- normalized requirements, assumptions, exclusions, and acceptance criteria;
- current-state inventory and gap analysis against the requested outcome;
- implementation-path options, selected path, trade-offs, migrations, and rollback boundary;
- architecture/interface/data/security/deployment decisions that must be frozen before parallel work;
- a complete feature inventory classified as `implement | modify | optimize | performance | security | migration | operations | documentation`;
- affected platforms and domains: frontend, backend, Android, iOS, AI/data, platform, or others;
- domain development lanes and one paired tester for every development lane;
- test strategy, canonical test environment, CI/CD capability state, and MFSQ coverage intent;
- dependency graph, write ownership, integration order, and review risks;
- `GO`, `GO_WITH_ACTIONS`, or `REPLAN`.

The Chair does not spawn participants. It writes the agenda and requested attendee IDs; `TD-01` routes synchronized packets and records attendance/evidence.

No implementation begins before `G0=GO|GO_WITH_ACTIONS` and all blocking actions have owners.

## Gate G1 — organizational and delivery readiness

Before any developer writes product code, `TD-01` and `RB-01` verify:

- all behavior and shared interfaces needed for parallel work are frozen or explicitly versioned;
- every lane has disjoint product-code ownership, an isolated worktree, base revision, generation, and rollback boundary;
- every developer has exactly one paired tester ID; every tester points back to the same developer;
- developer and tester task packets contain the same acceptance IDs and Shared Collaboration Pack revision;
- test ownership and product-code ownership are separate;
- `TM-01` has approved the MFSQ strategy;
- `CI-01` has classified the pipeline as `EXISTS_VALID | EXISTS_GAPPED | MISSING | BLOCKED`;
- missing CI/CD has created a blocking `CI-BOOTSTRAP` lane using Jenkins pipeline-as-code;
- design/Figma evidence exists before UI implementation when the project contract requires it;
- external writes, credentials, deployment, and production actions have explicit authority.

A missing pipeline blocks authoritative testing, but need not block product implementation when the CI bootstrap lane can proceed safely in parallel. It always blocks G3/G4 acceptance.

Read [review gates and lifecycle](references/review-gates-and-delivery-lifecycle.md) and [Jenkins pipeline contract](references/jenkins-pipeline-contract.md).

## Parallel development and test preparation

After G1, start independent work simultaneously:

```text
For each domain lane:
  Developer implements product scope in developer worktree
  Paired tester designs MFSQ cases in tester worktree
  CI engineer closes pipeline gaps / bootstraps Jenkins when needed
  Security-performance specialist prepares cross-cutting cases
```

Each developer packet must include:

- developer session ID and paired tester ID;
- exact product-code write allowlist and test-code denylist;
- frozen requirements/interfaces and acceptance IDs;
- base revision/worktree/generation;
- handoff artifact path and expected commit format;
- non-authoritative feedback commands allowed locally;
- blocker and return rules;
- `may_delegate=false`.

Each tester packet must include:

- tester session ID and paired developer ID;
- test-code/config/report write allowlist and product-code denylist;
- authority to expand test scope based on risk;
- MFSQ obligations, security/performance thresholds, and N/A approval rules;
- canonical CI environment and pipeline stage mapping;
- developer handoff path, candidate commit intake process, defect reporting path;
- `may_delegate=false`.

Developers may run compile, typecheck, formatting, or static feedback commands when allowed by the packet, but these are not test acceptance. They do not author test cases, change test expectations to make code pass, or declare quality complete.

Testers begin test analysis before code is complete. They implement and review version-controlled tests after the test plan is approved, then run them against the developer candidate through the canonical pipeline.

Read [developer-tester handoff](references/developer-tester-handoff.md).

## MFSQ test design

This Skill defines MFSQ operationally because the acronym has no single assumed universal meaning. A project with an existing canonical MFSQ definition may override it only by recording the source and mapping every required axis.

- **M — Mission & Model coverage:** requirement-to-test traceability, component/interface/data/state/migration/platform model coverage.
- **F — Functional & Flow coverage:** happy, alternate, negative, boundary, state-transition, concurrency, retry, idempotency, rollback, and recovery flows.
- **S — Security & Safety coverage:** identity, authorization, validation, data protection, secrets, supply chain, abuse, tenant isolation, privacy, and failure safety.
- **Q — Quality-attribute coverage:** performance is mandatory; also reliability, compatibility, accessibility, observability, maintainability, resource use, and recoverability as applicable.

For every feature or change, the test plan must contain M/F/S/Q rows or an explicit `N/A` with reason and `RB-01` approval. Any behavior-changing feature requires at least one security assessment and one performance case or approved N/A. Every executable case maps to a version-controlled test and CI stage.

Validate plans:

```bash
python scripts/validate_mfsq.py .pkos/company-swarm/<run-id>/lanes/<lane-id>/test-plan.json
```

Read [MFSQ quality model](references/mfsq-quality-model.md).

## Gate G2 — developer-to-tester handoff

A developer may hand off only a committed, self-contained candidate with:

- exact base and head commit;
- changed paths and product ownership proof;
- acceptance mapping and implementation summary;
- migrations/configuration/runtime impacts;
- known risks and unimplemented exclusions;
- feedback commands and their concrete outcomes;
- paired tester ID and target test-plan artifact.

The paired tester independently determines the final test scope. It may return `TEST_PLAN_GAP`, `CANDIDATE_NOT_TESTABLE`, or defects before pipeline execution. Product-code defects go back to the developer as structured defect packets; the tester never repairs product code.

A lane reaches `G2_PASS` only when the candidate and approved test suite both exist, all owned paths are compliant, and pipeline execution has produced authoritative evidence.

## CI/CD and Jenkins rule

`CI-01` first discovers the canonical pipeline rather than blindly replacing it:

- `EXISTS_VALID`: use it and add all new tests/stages.
- `EXISTS_GAPPED`: repair the source-controlled pipeline before acceptance.
- `MISSING`: immediately create and execute a `CI-BOOTSTRAP` lane using Jenkins unless the project contract names another provider.
- `BLOCKED`: create complete pipeline-as-code/bootstrap artifacts, record missing authority or infrastructure, and stop before claiming a live pipeline.

Jenkins bootstrap must prefer a source-controlled `Jenkinsfile`, multibranch or organization-folder discovery, credentials by reference rather than in source, reproducible agents, archived test/security/performance reports, and clear promotion/deployment gates. All authoritative tests run in CI; local-only evidence cannot settle G2–G4.

The pipeline should select applicable stages from:

```text
policy / ownership validation
lint / format / typecheck
unit
contract / schema
integration
UI or API end-to-end
Android / iOS device or simulator tests
AI/data evaluation and regression
security: SAST, SCA, secrets, container/IaC, DAST as applicable
performance: benchmark, load, latency, throughput, resource, regression thresholds
package / artifact / SBOM
test-environment deploy
acceptance / evidence publication
```

A new feature is incomplete until its approved tests are version controlled, wired to the pipeline, executed, and retained as evidence.

## Gate G3 — integration barrier

Only `INT-01` may create the cumulative integration candidate. It applies lane commits and test commits in the frozen dependency order, resolves only mechanical integration conflicts, and returns design/behavior conflicts to `TD-01` and `RB-01`.

Before releasing the barrier:

- all required lane results belong to the active run/generation;
- no stale or duplicate result is treated as current;
- product/test write ownership has no violations;
- shared interfaces match G0/G1 contracts;
- migrations and deployment order are coherent;
- the complete candidate runs through the canonical pipeline;
- cumulative security and performance evidence exists;
- failed lanes can be repaired without discarding accepted independent lanes.

`INT-01` cannot accept functionality or waive tests. It produces the candidate and evidence manifest only.

## Gate G4 — Review Board final decision

`RB-01` convenes the implementation review with the Director, affected developers, paired testers, `TM-01`, `CI-01`, `SQ-01`, and `INT-01` as needed. Review one frozen cumulative candidate in a single complete pass against:

- G0 requirements, gap analysis, selected implementation path, and feature inventory;
- implementation completeness and scope discipline;
- platform/domain consistency and unchanged-code interactions;
- MFSQ coverage and requirement-to-evidence traceability;
- security findings, performance thresholds, migrations, rollback, observability, and operations;
- pipeline definition, run results, retained artifacts, and unrun tests;
- PKOS Current Truth, ADR/Audit/Feature Registry writeback obligations.

Return exactly one verdict:

- `ACCEPT`: all blocking obligations are satisfied.
- `RETURN_TO_LANE`: issue precise return orders with owner, violated contract, evidence, severity, and retest scope.
- `REPLAN_ORG`: architecture, requirement, ownership, or test strategy is invalid; Director creates a new generation.
- `BLOCKED_EXTERNAL_BOUNDARY`: implementation may be ready but required environment/authority/evidence is unavailable.

Allow up to three repair generations for the same frozen architecture. A fourth return requires explicit `REPLAN_ORG` so the organization does not loop endlessly.

## Gate G5 — Director decision, dashboard, and writeback

`TD-01` accepts only after `RB-01=ACCEPT`. It then:

1. verifies the final base/head, diff scope, pipeline run, artifacts, open defects, residual risks, and external actions;
2. produces `dashboard.md` with a Mermaid organization/flow view and compact tables for lanes, feature status, MFSQ, CI, security, performance, repairs, and risks;
3. classifies durable changes C0–C5, executes or prepares PKOS project/memory writeback, updates the single Feature Registry and Current Truth, and creates ADR/Audit/Incident records when required;
4. reports exactly what ran and what did not run; never describes a proposed Jenkins server, deployment, Notion write, or child session as completed;
5. returns a final status.

Generate a deterministic dashboard from the run state when available:

```bash
python scripts/render_dashboard.py \
  .pkos/company-swarm/<run-id>/run-state.json \
  --output .pkos/company-swarm/<run-id>/dashboard.md
```

Minimum user-facing measures:

- organization size, active/complete/blocked sessions, and lane pairing;
- feature inventory: planned, implemented, tested, accepted, deferred;
- M/F/S/Q case totals and pass/fail/blocked/N/A counts;
- pipeline provider, run ID, pass rate, duration, artifact links/paths;
- security findings by severity and unresolved count;
- performance baseline, candidate, delta, and threshold result;
- review verdicts, repair generations, ownership violations, and remaining risks.

## Required final statuses

Return one of:

- `COMPANY_SWARM_ACCEPTED`
- `COMPANY_SWARM_CHECKPOINT`
- `RETURNED_TO_LANES`
- `REPLAN_ORGANIZATION`
- `BLOCKED_MODEL_CONFIG`
- `BLOCKED_RUNTIME`
- `BLOCKED_CI`
- `BLOCKED_EXTERNAL_BOUNDARY`

The final report must include the actual organization, configured/observed model identity, active generation, changed scope, pipeline evidence, Review Board verdict, repair history, PKOS writeback result, unrun evidence, and residual risk.

## Installation and validation

Plugin installation exposes the Skill, but custom role TOMLs must also be installed into the Codex agent registry. Read [runtime installation](references/runtime-installation.md).

Repository validation:

```bash
python plugins/pkos/skills/codex-company-swarm/scripts/validate_install.py
python -m unittest discover \
  -s plugins/pkos/skills/codex-company-swarm/tests -v
python scripts/validate.py
```

Runtime smoke-test the Director, Review Chair, one developer/tester pair, CI role, and Integration Owner before using this mode on production-critical work.
