# Task contracts and durable artifacts

Use these templates to keep Sol decisions and Luna execution bounded. Store them under `.codex/sol-luna/<run-id>/` or another repository-approved ignored workspace.

## Goal Contract

```text
RUN_ID:
GENERATION:
REPOSITORY / BRANCH / BASE:
INITIAL_DIRTY_PATHS:
OUTCOME:
WHY IT MATTERS:
AUTHORITIES:
INVARIANTS:
EXCLUDED SCOPE:
ACCEPTANCE CRITERIA:
ROLLBACK / RECOVERY BOUNDARY:
EXTERNAL ACTION AUTHORITY:
PROFILE / ASSURANCE:
SOL BOUNDARY MODE:
MAX PARALLEL WRITERS:
```

## Route ledger

```text
| Lane | Generation | Role | Model/Effort | Worktree | Write scope | Depends on | Result artifact | Status |
| --- | ---: | --- | --- | --- | --- | --- | --- | --- |
```

Statuses:

```text
planned -> dispatched -> running -> completed-claim
        -> settled | blocked | failed | stale | superseded
settled dependencies -> barrier-ready -> integrated -> verified -> accepted
```

Update the ledger; do not regenerate a full plan after every event.

## Luna Task Packet

```text
ROLE
Act as the bounded implementation worker. You are not alone in the repository.
Do not create children. Preserve unrelated edits and own only the scope below.

RUN ID / GENERATION / LANE
<stable values>

PROFILE / ASSURANCE
<adaptive|max-pair> / <standard|strict>

OBJECTIVE
<one observable result>

BASE / WORKTREE
<revision, branch, worktree path, initial dirty paths>

OWNERSHIP
- Own: <exact files/directories or responsibility>
- Do not touch: <shared/excluded/generated/user-owned paths>

FROZEN CONTRACTS
- <interfaces, schemas, behavior, compatibility>

CONTEXT REFS
- <minimum paths/artifacts; do not read the whole repository>

CONSTRAINTS
- <repository rules, dependencies, safety, limits>
- Return blocked before changing a frozen decision or leaving ownership.
- Do not push, merge, deploy, publish, or mutate production.

ACCEPTANCE
- <criterion with observable result>

VERIFICATION
- Run: <exact command>
  Success: <expected exit/result>

COMPLETION ARTIFACT
Write structured JSON to: <path>

RETURN
STATUS: complete | partial | blocked | failed
CHANGES: actual file-by-file summary
VERIFIED: commands and concrete results
DECISIONS: local implementation choices that did not change contracts
GAPS: unrun checks, blockers, uncertainty, or none
EVIDENCE_REFS: artifact paths
```

## Child result JSON

```json
{
  "version": "codex-sol-luna-result-v1",
  "run_id": "run-2026-08-18-example",
  "generation": 1,
  "lane_id": "lane-a",
  "status": "complete",
  "base_revision": "<sha>",
  "requested_model": "gpt-5.6-luna",
  "requested_effort": "high",
  "observed_model": "gpt-5.6-luna",
  "observed_effort": "high",
  "identity_confidence": "observed",
  "started_at": "2026-08-18T16:00:00Z",
  "completed_at": "2026-08-18T16:10:00Z",
  "changed_paths": ["src/a.rs", "tests/a_test.rs"],
  "acceptance": [
    {"criterion": "A works", "result": "pass", "evidence_ref": "artifacts/a-test.txt"}
  ],
  "verification": [
    {"command": "cargo test a", "exit_code": 0, "evidence_ref": "artifacts/a-test.txt"}
  ],
  "decisions": [],
  "gaps": [],
  "evidence_refs": ["artifacts/a-test.txt"]
}
```

## Fresh reviewer packet

```text
ROLE
Act as a fresh read-only reviewer. Do not edit, fix, commit, push, or orchestrate.

RUN / GENERATION:
BASE / FROZEN CANDIDATE:
GOAL CONTRACT:
COMPLETE CUMULATIVE DIFF:
ACCEPTANCE AND EVIDENCE:
RISK SURFACES:

Review the whole declared scope in one pass. A blocker must establish:
1. violated criterion/invariant/contract;
2. concrete reachable path or material evidence gap;
3. impact;
4. precise file/contract reference;
5. why current evidence does not close it.

RETURN
VERDICT: SHIP | FIX_FIRST | RETHINK | UNUSABLE_RUNTIME
AUDIT_COMPLETENESS: complete | scope-too-broad
FINDINGS: ordered blocking findings
RESIDUAL_RISK: non-blocking risks
EVIDENCE_CHECK: missing, contradictory, or sufficient evidence
```

## Integration packet

```text
RUN / GENERATION:
SETTLED LANES:
INTEGRATION BASE:
ORDER:
- <lane/commit/patch sequence>
FROZEN SHARED INTERFACES:
CONFLICT POLICY:
CUMULATIVE ACCEPTANCE:
CUMULATIVE VERIFICATION:
OUTPUT CANDIDATE:
```

Only one integration owner writes the integration checkout.
