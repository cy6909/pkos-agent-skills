# Developer–tester pairing and handoff

## Pair contract

Every product-code developer has exactly one primary paired tester for the active lane. The pair is reciprocal in `02-org.json`:

```text
D-BE-01.paired_session_id = T-BE-01
T-BE-01.paired_session_id = D-BE-01
```

A specialist may support several testers, but does not replace the primary tester.

## Separation of duties

### Developer owns

- implementation within product-code allowlist;
- implementation notes and acceptance mapping;
- build/config/migration impact description;
- product-code commit;
- response to structured defects;
- local compile/typecheck/lint feedback only when allowed.

### Developer does not own

- test scope;
- test-plan approval;
- test code or snapshots/fixtures intended as acceptance evidence;
- weakening expected behavior to fit implementation;
- authoritative test execution;
- quality verdict.

### Tester owns

- risk-based test scope;
- MFSQ plan and traceability;
- test-case review;
- automated test implementation in test allowlist;
- pipeline wiring for tests, in collaboration with CI role;
- authoritative pipeline execution and result analysis;
- defect packets and lane test verdict.

### Tester does not own

- repairing product code;
- changing requirements;
- choosing architecture;
- merging the cumulative candidate;
- waiving security/performance without Chair approval.

## Developer result schema

```json
{
  "schema": "pkos-company-swarm/developer-result-v1",
  "run_id": "run-123",
  "generation": 1,
  "lane_id": "backend",
  "developer_session_id": "D-BE-01",
  "paired_tester_id": "T-BE-01",
  "base_commit": "...",
  "head_commit": "...",
  "changed_paths": ["server/api.py"],
  "acceptance_mapping": [{"acceptance_id": "AC-1", "paths": ["server/api.py"]}],
  "migrations": [],
  "runtime_changes": [],
  "feedback_commands": [{"command": "python -m compileall server", "exit_code": 0}],
  "known_risks": [],
  "excluded_scope": [],
  "test_handoff_path": ".pkos/company-swarm/run-123/lanes/backend/test-plan.json",
  "status": "HANDOFF_READY"
}
```

The developer reports exact outcomes; it does not label commands as test acceptance.

## Test plan workflow

1. Tester reads G0/G1 contracts before developer completion.
2. Tester drafts MFSQ matrix and identifies testability gaps.
3. `TM-01` reviews cross-lane consistency and `SQ-01` reviews security/performance portions when applicable.
4. `RB-01` approves any M/F/S/Q N/A exception.
5. Tester implements version-controlled tests and pipeline mapping.
6. Tester ingests the exact developer commit and confirms testability.
7. Canonical pipeline executes.
8. Tester publishes result and defects.

## Defect packet

```json
{
  "schema": "pkos-company-swarm/defect-v1",
  "defect_id": "DEF-BE-004",
  "run_id": "run-123",
  "generation": 1,
  "lane_id": "backend",
  "reported_by": "T-BE-01",
  "assigned_to": "D-BE-01",
  "severity": "P1",
  "violated_contract": "AC-4",
  "scenario": "Retry after timeout creates duplicate order",
  "evidence": ["jenkins/run-411/test-report#order-retry"],
  "affected_commit": "...",
  "required_change": "Preserve idempotency key across retry",
  "required_retest": ["TC-F-021", "TC-S-009", "TC-Q-004"],
  "architecture_frozen": true,
  "status": "OPEN"
}
```

The developer returns a new commit; the tester decides regression scope. A developer saying “fixed” never closes the defect.

## Shared files and generated artifacts

If a test requires a shared file also touched by product code, assign one owner during G1. Common cases:

- package lockfiles;
- generated API clients;
- snapshots/golden files;
- database fixtures;
- route/navigation registries;
- mobile resources;
- CI configuration.

Never allow two active writers to “coordinate by being careful” in the same checkout. Use distinct commits/worktrees and one integration rule.
