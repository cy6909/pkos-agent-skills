# MFSQ quality and test-design contract

## Progressive execution order

Execute by risk and candidate maturity, not matrix completeness. Layer 1 is P0 user smoke plus critical writes; Layer 2 is exceptions, idempotency, permissions, and recovery; Layer 3 is performance, long-run stability, and cross-device/platform. A missing or failing Layer 1 blocks major Layer 3 investment. T-SHARED-01 must not expand a large low-priority suite before a cumulative candidate exists.

## Meaning

- **M — Mission & Model:** requirements, acceptances, contracts, state/data models, platform allocation, migration and compatibility.
- **F — Functional & Flow:** happy/alternate/invalid/boundary paths, retry, cancellation, concurrency, offline, recovery and E2E.
- **S — Security & Safety:** identity, authorization, isolation, validation, privacy, abuse, supply chain and safe degradation.
- **Q — Quality Attributes:** performance, reliability, accessibility, compatibility, observability, recoverability, maintainability and cost.

Material is not M. Exact source, clean tree, lockfiles, tool/image digests, SBOM, provenance and hashes form a separate fail-closed **Material & Provenance pre-gate**. Historical `pkos-mfsq/v1` is evidence only; new runs require `pkos-mfsq/v2`.

## Required chain

```text
Requirement -> canonical Product Feature
-> platform implementation unit(s) + typed dependency edges
-> atomic Acceptance -> approved visual + textual Test Design
-> MFSQ Case -> ordered action/expected steps
-> test path/symbol + tested code path/symbol
-> exact-candidate pipeline result/evidence
```

Platform units (`frontend | backend | android | ios | ai_data | ops | shared`) do not duplicate the Product Feature. Dependencies name consumer, provider and contract; each requires a contract, integration or E2E case spanning both units.

## Test Design

Before implementation, the plan references an approved, versioned design with stable ID, checksum, visual coverage map, and written scope/risk/environment/data cases. Written cases are executable truth. G1 fails on stale design, implementation map, or dependencies.

## Coverage focus

**M:** requirement/acceptance completeness; unit allocation; API/event/schema/generated-client contracts; state/data/permission/tenancy lifecycles; migration/rollback/flags/compatibility; AI data/evaluation/failure models.

**F:** alternate and invalid values; state transitions; timeout/retry/idempotency/duplicates; ordering/races; offline/background; partial failure/compensation; navigation/refresh/persistence and cross-unit user flows.

**S:** auth/session/object access; tenant isolation; upload/deserialization/injection/SSRF/path control; secrets/logs/privacy/transport; abuse/rate/replay; reachable dependency/container/IaC findings; mobile storage/deep links/WebView; destructive-operation safety.

**Q:** latency/throughput/startup/frame/memory/CPU/GPU/network/battery/cost; reliability/durability; logs/metrics/traces/audit; backup/restore; browser/device/OS/accessibility/i18n; deterministic build, leaks, load shedding and graceful degradation.

Behavior changes require S and Q/performance unless RB-01 approves a scoped exception. Performance records comparable baseline/environment/workload, repetitions, statistic, threshold, budget, and decision.

## Material pre-gate

`material_gate` contains version-controlled, pipeline-mapped checks for:

- exact authorized commit/tree, clean checkout and submodules;
- lockfile, dependency and generated-file consistency;
- pinned toolchain/agent/container images and source provenance;
- schema/migration/fixture/model/data/design checksums;
- SBOM, signatures/attestations, artifact and evidence hashes.

Every required check has automation path, pipeline stage, expected result, status and evidence. Failure blocks acceptance and cannot be excluded as MFSQ.

## Plan and case fields

Plan fields: run/generation/lane; behavior-changing flag; requirement/feature/atomic-acceptance IDs; developer/tester pair; canonical environment/pipeline; approved Test Design; units/dependencies; Material gate; cases; exclusions; review status/reviewers.

Each implementation unit records `unit_id, layer, title, requirement_ids, feature_ids, acceptance_ids, user_facing, state_changing`. Each dependency records `dependency_id, consumer_unit_id, provider_unit_id, contract_ref, required`.

Each case records:

```text
case_id; axis + secondary_axes; case_type; side; title
requirement_ids; feature_ids; implementation_unit_ids; acceptance_ids
risk; rationale; quality_attribute; preconditions
steps[{step_id, action, expected, evidence_hook}]
automation_path; pipeline_stage; owner_session_id; status; evidence
```

Case types: `unit | component | contract | integration | e2e | security | performance | migration | static | manual_acceptance`.

Every step has its own expected result. Unit cases require stable `test_symbol`, `code_refs[{path,symbol,purpose}]`, fixtures, and regression rationale.

Exclusions name `scope`, target/axis, concrete reason, `RB-*` approver and approval artifact.

## Admission rules

1. Every requirement reaches a Feature and atomic Acceptance; every Feature reaches a unit.
2. Every unit, dependency and Acceptance has executable coverage or approved exclusion.
3. Every case has axis, side, type, rationale, ordered action/expected steps, automation path, pipeline stage and owner.
4. Unit cases include test/code symbols, purpose and rationale.
5. User-facing units include E2E or approved manual acceptance. Project-required developer browser self-test remains separate admission evidence.
6. Behavior changes have S and Q/performance coverage or scoped RB exceptions.
7. Testers/specialists own independent test implementation; developer self-tests cite case IDs but do not replace it.
8. v1 plans are never silently upgraded and cannot pass new G1.

## Notion projection and review

Keep one canonical Feature Registry. Relate it to Requirement, platform Implementation Unit, Dependency, atomic Acceptance, Test Design and MFSQ Test Case registries/views. A case page renders ordered steps/results and points to the Git v2 artifact; store evidence pointers, not raw logs.

- RA-01: requirements, Feature ownership, unit allocation, dependencies.
- TM-01: design coverage, risk, precise steps, fixtures and pipeline mapping.
- SQ-01: threat coverage, tool limits, performance method and false confidence.
- RB-01: exclusions and G1/G4 sufficiency.
