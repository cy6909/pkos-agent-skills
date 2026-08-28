# MFSQ quality model

## Status of the term

This Skill does not assume that “MFSQ” has one universally recognized software-testing expansion. It defines a project-operational model so every run is deterministic. If a repository already owns a canonical MFSQ definition, the G0 review may use it only after recording the source and a complete mapping to the four obligations below.

## M — Mission & Model coverage

Purpose: prove that the intended mission and system model are represented by tests.

Typical coverage:

- every requirement and acceptance criterion;
- component boundaries and dependency direction;
- API/event/schema contracts;
- data model, state model, lifecycle, permissions, and tenancy;
- platform variants: web, backend, Android, iOS, AI/data, infrastructure;
- migrations, backward compatibility, rollout, rollback, and feature flags;
- AI/data-specific datasets, evaluation slices, nondeterminism controls, and failure modes.

Examples:

- requirement traceability test;
- contract/schema compatibility test;
- migration forward/backward test;
- platform parity matrix;
- model/evaluation slice coverage.

## F — Functional & Flow coverage

Purpose: prove behavior across complete user/system flows, not only happy-path functions.

Typical coverage:

- happy path and alternate paths;
- invalid input and authorization failures;
- boundaries, empty/extreme values, time/date/localization;
- state transitions and forbidden transitions;
- retry, timeout, cancellation, idempotency, duplicate delivery;
- concurrency, ordering, race, offline/online transitions;
- partial failure, rollback, recovery, and compensation;
- UI interaction, accessibility interaction, device lifecycle, and backgrounding where applicable.

## S — Security & Safety coverage

Purpose: prove the change does not introduce unacceptable security or unsafe failure behavior.

Typical coverage:

- authentication, session lifecycle, authorization, object-level access;
- input validation, injection, deserialization, file handling, SSRF and path control;
- secrets, credentials, logs, error messages, and privacy-sensitive data;
- encryption and transport expectations;
- tenant/user isolation and privilege boundaries;
- dependency, supply-chain, SBOM, signature, container and IaC checks;
- abuse/rate limiting, fraud/misuse paths, replay, automation resistance;
- mobile storage, IPC, deep links, WebView/network controls;
- safe degradation, fail-closed/fail-safe decisions, and destructive-operation protection.

Use project risk and applicable standards, including NIST SSDF and OWASP ASVS/MASVS/WSTG, rather than blindly executing a generic checklist.

## Q — Quality-attribute coverage

Purpose: prove non-functional behavior. **Performance is mandatory for behavior-changing work unless RB-01 approves N/A with evidence.**

Typical attributes:

- latency, throughput, startup, frame time, memory, CPU/GPU, disk, network, battery, cost, capacity;
- reliability, availability, durability, and fault tolerance;
- observability: logs, metrics, traces, audit, alertability;
- recoverability, backup/restore, rollback, disaster behavior;
- compatibility, upgrade, downgrade, browser/device/OS matrix;
- accessibility and internationalization;
- maintainability/testability and deterministic build behavior;
- resource leaks, long-run stability, load shedding and graceful degradation.

Performance cases require a baseline, environment, workload, warmup, repetitions, candidate result, statistic, threshold, and regression decision. “Feels fast” is not evidence.

## Required plan fields

Each executable test case contains:

```json
{
  "case_id": "TC-Q-004",
  "axis": "Q",
  "title": "p95 recommendation latency under target load",
  "acceptance_ids": ["AC-8"],
  "risk": "high",
  "quality_attribute": "performance",
  "preconditions": ["test dataset revision ds-17"],
  "procedure": "Run k6 scenario perf/recommendations.js",
  "expected": "p95 <= 450 ms and error rate < 0.5%",
  "automation_path": "tests/performance/recommendations.js",
  "pipeline_stage": "performance",
  "owner_session_id": "T-BE-01",
  "status": "planned",
  "evidence": []
}
```

Plan-level fields:

- `schema = pkos-mfsq/v1`;
- run, generation, lane, feature ID, behavior-changing flag;
- developer/tester pairing;
- canonical environment and pipeline provider;
- cases;
- exclusions with axis, reason, approved-by, approval artifact;
- review status and reviewers.

## Coverage rules

1. Every feature/change has visible M, F, S, and Q disposition.
2. An axis may be `N/A` only with a concrete reason and `RB-01` approval.
3. Behavior-changing work requires a security case or S exception and a performance case or Q/performance exception.
4. Every executable case has an automation path and pipeline stage. Truly manual acceptance requires a machine-retained evidence artifact and Chair approval; it does not replace automatable coverage.
5. Every acceptance criterion maps to one or more cases or an approved explicit gap.
6. Security/performance findings retain severity/threshold and exact evidence.
7. Test implementation is owned by testers/specialists, not developers.

## Review checklist

`TM-01` checks completeness, duplication, risk prioritization, cross-lane coverage, environment realism, data/fixture control, and pipeline mapping.

`SQ-01` checks threat/risk coverage, security tooling limits, performance methodology, baseline comparability, and false-confidence risks.

`RB-01` judges exceptions, unresolved gaps, and whether evidence is sufficient for acceptance.
