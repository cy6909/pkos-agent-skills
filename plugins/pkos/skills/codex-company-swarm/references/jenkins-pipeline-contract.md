# CI/CD and Jenkins pipeline contract

## Mandatory bounded preflight and Stop Rule

Before CI, finish within 10 minutes and record controller, executor, credentials, job-creation permission, and artifact capacity. `RUNNING` is invalid unless all five pass. If any prerequisite fails twice or blocks over 15 minutes, set `STOPPED`, report exact blocker/reason/authority/recovery, release capacity to product development, and stop unbounded diagnosis. Reuse approved CI; Jenkins-as-code is only a governed fallback, and GitHub Actions is forbidden.

## Discover before bootstrap

`CI-01` inspects the repository and configured test environment for:

- existing Jenkinsfile or pipeline library;
- GitHub Actions, GitLab CI, Buildkite, Azure Pipelines, or another canonical CI;
- branch/multibranch configuration and required checks;
- test environment provisioning and deployment scripts;
- report/artifact retention;
- credentials references and agent capabilities;
- recent run evidence when access exists.

Classify:

- `EXISTS_VALID`: canonical pipeline can execute all required tests and preserve evidence.
- `EXISTS_GAPPED`: pipeline exists but lacks stages, environments, reports, or controls required by this change.
- `MISSING`: no usable CI/CD pipeline.
- `BLOCKED`: capability cannot be verified or created due to missing access, infrastructure, credentials, policy, or network.

## Provider decision

- Prefer the project-approved canonical CI when it is valid; explicit project policy (including a prohibition on a provider) wins.
- Repair gaps in the existing provider rather than adding a second competing source of truth.
- When no approved pipeline exists, apply project governance; the default fallback is Jenkins-as-code.
- If the user/project explicitly names another provider, record that decision and apply the same quality contract. Never add a competing or prohibited provider merely because it is the fallback.

## Jenkins bootstrap lane

A `CI-BOOTSTRAP` lane should produce, as applicable:

```text
Jenkinsfile
ci/jenkins/
  README.md or runbook
  controller/agent provisioning as code
  shared-library references or pinned library code
  credentials manifest with references only
  test-environment provisioning
  report publication and artifact retention
  backup/upgrade/rollback notes
```

Prefer:

- Pipeline as Code in the repository;
- multibranch pipeline or organization-folder discovery;
- reproducible ephemeral agents/containers;
- least-privilege credential IDs, never embedded secrets;
- pinned toolchains and dependency caching with integrity controls;
- deterministic workspace cleanup;
- timestamps, timeouts, retries only where safe, and concurrency controls;
- JUnit/coverage/security/performance report publication;
- immutable build artifacts and provenance/SBOM when relevant;
- explicit test-environment deployment and teardown;
- approval gates for destructive, production, or release actions.

A skill cannot manufacture a live Jenkins controller without authority and infrastructure. When those are unavailable, generate complete source-controlled bootstrap artifacts and return `BLOCKED_EXTERNAL_BOUNDARY`; never report Jenkins as running.

## Material and provenance pre-gate

Every run starts with a fail-closed Material gate. Material is not M; M means Mission & Model. The gate proves candidate/input reproducibility.

Required checks, as applicable:

- exact commit, tree, clean checkout, submodules and generated-file drift;
- lockfiles, dependency resolution and pinned tool/container images;
- source/schema/migration/fixture/model/data/design checksums;
- SBOM, provenance, attestations, artifact hashes and environment identity.

`pkos-mfsq/v2` maps each `material_gate` check to a pipeline stage. Missing/failed checks block acceptance and are not MFSQ exclusions.

## Pipeline stage contract

The exact stages are risk- and stack-dependent, but every run begins with Material/provenance checks and ends with evidence publication.

```text
material / provenance
  -> ownership / route / generated-file validation
  -> build / lint / format / typecheck / compile
  -> M: mission and model contracts
  -> F: unit / contract / integration / platform E2E
  -> S: security and safety
  -> Q: performance / reliability / accessibility / compatibility
  -> package / SBOM / artifact
  -> deploy to canonical test environment
  -> acceptance and report publication
```

Parallelize only independent stages; failed prerequisites remain failed.

## All tests on pipeline

Authoritative acceptance requires:

- a passing Material gate and approved `pkos-mfsq/v2` test design;
- version-controlled test implementation;
- source-controlled pipeline mapping;
- exact candidate revision;
- run ID/URL or retained local connector reference;
- stage/job status and concrete exit state;
- machine-readable test/security/performance reports;
- skipped/disabled/quarantined tests listed explicitly;
- environment and toolchain identity;
- artifacts retained long enough for G4 review.

Each case keeps ordered steps with an expected result per step. Developer feedback does not replace tester-owned CI evidence.

## Security stages

Select applicable controls:

- secret scanning;
- SAST;
- dependency/SCA and license policy;
- SBOM generation and vulnerability scan;
- container and IaC scanning;
- API/web/mobile dynamic tests in the test environment;
- authorization and abuse tests from MFSQ S;
- artifact signing/provenance when required.

Tool output is not automatically a blocker. `SQ-01` triages reachability, exploitability, severity, suppressions, and accepted risk with evidence.

## Performance stages

A performance stage records:

- baseline and candidate commits;
- identical or normalized environment;
- workload/data/tool versions;
- warmup and repetitions;
- percentile/throughput/resource metrics;
- absolute threshold and regression budget;
- raw report artifact;
- pass/fail/unstable decision.

Do not compare incomparable machines or datasets without normalization and disclosure.

## Pipeline evidence schema

```json
{
  "schema": "pkos-company-swarm/pipeline-evidence-v1",
  "provider": "jenkins",
  "pipeline": "stylemuse/main",
  "run_id": "411",
  "candidate_commit": "...",
  "environment": "test-01",
  "status": "PASS",
  "started_at": "...",
  "completed_at": "...",
  "duration_seconds": 812,
  "stages": [],
  "reports": [],
  "artifacts": [],
  "skipped_tests": [],
  "unverified_claims": []
}
```
