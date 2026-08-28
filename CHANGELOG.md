# Changelog

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
