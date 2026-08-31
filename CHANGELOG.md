# Changelog

## 0.9.0 - 2026-08-31

- Replace the historical MFSQ v1 manifest with `pkos-mfsq/v2` and enforce Requirement → Feature → platform implementation unit/dependency → atomic Acceptance → approved visual/text Test Design → executable test/CI traceability.
- Keep M as Mission & Model and add a separate fail-closed Material/provenance pre-gate for exact source, lockfiles, generated files, toolchains, models/data, SBOM and artifact integrity.
- Require every test step to carry its expected result; require unit tests to identify test/code symbols, purpose and rationale; require dependency and user-facing acceptance coverage.
- Define normalized Notion Requirement, implementation-unit, dependency, atomic-acceptance, Test Design and MFSQ Test Case projections while preserving the single canonical Product Feature Registry.
- Add validator and negative-test coverage for legacy manifests, orphan acceptances, missing code mappings, missing dependency/E2E coverage and incomplete Material gates.

## 0.8.0 - 2026-08-31

- Require all ten PKOS Skill entrypoints to apply `NOTION_WRITE_LANGUAGE=zh-CN` to human-readable Notion writes and pending writeback payloads.
- Define one shared Chinese-writing contract covering natural wording, semantic accuracy, factual status, technical-term preservation, existing-schema compatibility, and read-back verification.
- Extend Company Swarm's PK-01 role and coordination/writeback references so its sole Notion writer emits understandable Chinese without translating machine contracts.
- Add repository validation that rejects a PKOS Skill missing the language marker or a shared Notion contract missing its accuracy and verification rules.

## 0.7.1 - 2026-08-28

- Make `codex-company-swarm` discoverable in fresh Codex skill catalogs so explicit `$codex-company-swarm` activation works outside the source repository.
- Shorten the Company Swarm plugin starter prompt to Codex's 128-character manifest limit and enforce the three-prompt/128-character contract in repository validation.

## 0.7.0 - 2026-08-28

- Preserve the BOOT→G5 state machine, sole TD-01/PK-01/INT-01 authorities, developer/tester pairing, exact-candidate review, evidence chain, Notion receipts, and checkpoint/takeover semantics.
- Replace the all-Sol-Max role lock with Director-controlled model routing recorded per visible task and Task Packet; default high-risk/product/integration work to Sol Max, bounded test/CI/mechanical work to Luna Max, and reuse/escalate the same task on anomalous Luna output.
- Require every formal child role to be a sidebar-visible `create_thread` task with stored thread/host/worktree/title/lane/generation/epoch/model/effort/risk/rationale/cursor metadata; prohibit hidden formal subagents and child delegation.
- Add explicit staffing registers: three default product lanes (four only with disjoint ownership evidence), target six active children, minimum productive concurrency four, active hard cap eight, registered hard cap twelve, and a 90-second underfill alert.
- Add the TD-only reconciliation loop, bounded cursor-based waits, affinity follow-up reuse, slot release, verifiable underfill reasons, and `CONCURRENCY_UNDERFILLED` events while retaining single-writer barriers.
- Add `org-v3` and Task Packet v2 schemas, three executable staffing examples, and negative validation for hidden/duplicate/stale/unrouted/over-cap/underfilled organizations.
- Prefer project-approved CI and use Jenkins-as-code only as the governance fallback when no approved provider exists.
- Remove fixed model keys from role packet templates, lower the runtime concurrency example to eight, and keep the plugin UI prompt list within Codex's three-prompt limit.

## 0.6.0 - 2026-08-28

- Refactor `codex-company-swarm` into an executable-style progressive-disclosure entrypoint: registers, invariants, conditional reference map, BOOT→G5 state machine, guards, validators, and statuses.
- Remove unconditional startup reference reads and move duplicated organization, Notion, event, MFSQ, CI, recovery, traceability, and field-level detail behind condition-specific references.
- Shorten discovery metadata, the UI starter prompt, and all ten Sol Max role contracts while preserving authority, freshness, evidence, testing, integration, and writeback boundaries.
- Add `audit_prompt_budget.py` with CI-enforced limits for SKILL, metadata, root core load, role TOMLs, reference size, duplicate runtime paragraphs, and reference-preload regressions.
- Add prompt-budget negative tests and make installation validation report estimated activation context.
- Preserve v0.5 Notion coordination, outbox receipts/watermark, Pack Delta, checkpoints/takeover, traceability, MFSQ, exact-candidate CI, and G0–G5 acceptance semantics.

## 0.5.0 - 2026-08-28

- Upgrade `codex-company-swarm` from PKOS-backed final writeback to a continuous **Notion Durable Coordination Plane**.
- Make `PK-01` a persistent single Notion coordination writer from Phase 0 through G5 rather than an optional final scribe.
- Add a minimal three-database coordination schema: Swarm Run & Lane Registry, append-only Event & Decision Ledger, and Evidence Registry; extend the existing single Project Feature Registry instead of creating a duplicate feature list.
- Add event-driven Run/Lane/Session/Task/Pack/Feature/Defect/CI/Candidate/Gate/Checkpoint/Takeover projection with idempotency keys, `.pkos` write-ahead outbox, verified Notion write receipts, contiguous sync watermark, bounded retry, and dead-letter discipline.
- Add Direct Verified, Brokered Snapshot, and blocked-freshness context modes; structured Context Requests; versioned Pack Delta, mandatory reload acknowledgements, stale Pack rejection, and C2+ generation invalidation.
- Add durable checkpoints, resume tokens, artifact checksums, optimistic Director epoch, authorized takeover, stale-epoch rejection, and deterministic resume-plan generation.
- Add end-to-end Requirement → Feature → Acceptance → Product/Test commits → CI/security/performance evidence → Review → Notion owner/write-receipt traceability and a complete bundle validator.
- Add event-driven Feature lifecycle projection during G0–G5, while preserving the one canonical Feature Registry and Current Truth/Audit/ADR/Incident separation.
- Add G5 retrospective and disciplined procedural-memory compilation so reusable lessons persist without storing raw chats, logs, temporary sessions, or speculative conclusions.
- Extend the Dashboard with Gate, state version, Director epoch, Pack, Notion mode/schema/watermark/outbox/dead letters, checkpoint/resume token, Context Requests, stale-result rejection, traceability, and write receipts.
- Add seven coordination examples plus a cross-file bundle, nine coordination/recovery validators/helpers, and 36 new positive/negative tests; preserve all previous organization/MFSQ/dashboard tests.

## 0.4.0 - 2026-08-28

- Add `codex-company-swarm`, an explicit token-insensitive rapid-agile mode with the current session as sole GPT-5.6 Sol Max Technical Director.
- Add a persistent Review Board Chair, stream-aligned domain development lanes, reciprocal developer/tester pairing, Test Manager, CI/Jenkins, security/performance, single integration, and PKOS governance roles.
- Add G0–G5 evidence gates covering requirement and gap analysis, implementation-path review, organizational readiness, developer-to-tester settlement, cumulative integration, Review Board acceptance, and Director reporting/writeback.
- Define MFSQ operationally as Mission & Model, Functional & Flow, Security & Safety, and Quality Attributes; require security and performance disposition for behavior-changing work.
- Discover an existing canonical CI/CD pipeline first and bootstrap Jenkins Pipeline as Code only when no usable pipeline exists; require all authoritative tests and new test cases to execute in CI.
- Add deterministic organization/MFSQ validators, dashboard rendering, installation helpers, examples, and positive/negative unit tests.
- Preserve PKOS canonical-owner, bounded-memory, Notion Search-Before-Create, Current Truth, Audit/ADR/Incident, and verified-writeback rules.

## 0.3.0 - 2026-08-19

- Keep the Skill-loading session as the sole Sol planner instead of spawning another planner.
- Require user-confirmed total and per-role session caps; reuse idle affinity-matched sessions and queue at capacity.
- Add deterministic `schedule_sessions.py` recommendations and a durable session-pool example.
- Require every lane to load the same PKOS Shared Collaboration Pack, canonical Notion sources, required skills, and governing standards.
- Enforce development-only local execution, remote environment evidence for tests/builds/containers/deployment, and a Figma-first gate for UI changes.
- Upgrade route/result contracts to `codex-sol-luna-route-v3` and `codex-sol-luna-result-v2` with negative validation coverage.

## 0.1.0 - 2026-08-11

Initial public repository scaffold.

- PKOS project knowledge address-space protocol.
- Capability Map and single Project Feature Registry model.
- C0-C5 audit / ADR / incident governance.
- PKOS long-term memory with temporal validity and provenance.
- Bounded Memory Context Compiler, paging, compaction, and GC.
- Eight Agent Skills.
- OpenAI repo marketplace packaging.
- English and Simplified Chinese documentation.
