# Assurance and acceptance gates

Use this reference before accepting Luna work, at a strict review boundary, or after a repair.

## Gate 1 — identity

Record separately:

- requested model/effort;
- configured named-role model/effort;
- observed runtime model/effort;
- confidence: `observed`, `configured`, or `unverified`.

A role name or model self-report is not runtime proof. A contradiction is a route failure. Strict assurance requires at least configured identity and should prefer observed identity.

## Gate 2 — scope and preservation

Inspect the actual candidate, including staged, unstaged, and in-scope untracked files.

Pass only when:

- changed paths belong to the lane or integration owner;
- excluded/shared/user-dirty files were not overwritten;
- public contracts were not changed without Sol approval;
- no unauthorized external action occurred;
- no worker delegated to another child;
- every change can be attributed to an actor/lane.

Tests passing do not excuse a scope violation.

## Gate 3 — acceptance mapping

Build:

```text
criterion -> implementation path/symbol -> evidence ref -> result
```

Classify each criterion:

- `pass` — direct evidence establishes it;
- `fail` — behavior/evidence contradicts it;
- `not_run` — applicable evidence missing; blocks acceptance;
- `not_applicable` — concrete contract reason required.

Do not accept vague entries such as “tests added” or “works as expected.”

## Gate 4 — verification depth

Distinguish:

- static/format/lint;
- focused unit tests;
- integration tests;
- runtime/acceptance checks;
- packaging/delivery checks;
- production evidence.

One level does not prove another. Run focused checks first, then broader checks proportionate to risk. Record command, exit code, relevant observation, and artifact path.

## Gate 5 — Sol adversarial integration pass

Sol inspects the cumulative candidate, not only lane summaries:

- negative/error paths;
- changed-to-unchanged interactions;
- compatibility and migration behavior;
- concurrency/recovery/idempotency when relevant;
- tests that would fail without the change;
- fix-induced regressions;
- contradictions between acceptance and implementation.

This is parent judgment, not independent review.

## Gate 6 — strict fresh review

Strict assurance requires one fresh read-only Sol reviewer after the candidate is frozen and deterministic checks pass.

Reviewer verdicts:

- `SHIP` — no blocker;
- `FIX_FIRST` — actionable blocking findings;
- `RETHINK` — architecture/acceptance/scope is incoherent or too broad;
- `UNUSABLE_RUNTIME` — reviewer identity/tool boundary/evidence is not trustworthy.

Review budget:

- target one call;
- maximum two calls: initial review plus one fresh re-review after one repair;
- every started reviewer consumes a call;
- do not split or rename the same scope to reset budget.

## Gate 7 — repair closure

For `FIX_FIRST`:

1. Sol classifies each finding against the contract.
2. One Luna repair packet owns exact fix paths and criteria.
3. Rerun focused and broader checks.
4. Refreeze the cumulative candidate.
5. Use one fresh reviewer for re-review.

A second failed repair/re-review returns `REPLAN_REQUIRED`; do not loop.

## Gate 8 — integration

For parallel work, pass only when:

- every required lane is settled;
- the integration barrier released legitimately;
- one integration candidate contains all accepted lane changes;
- cumulative checks pass;
- frozen shared interfaces still match;
- no lane fix invalidated another lane's evidence.

## Final status rules

`SHIP_STANDARD` requires Gates 1–5 and applicable integration.

`SHIP_STRICT` requires Gates 1–8.

Use `CHECKPOINT_READY` for partial parent-verified progress that is not the final boundary.

Use `REPLAN_REQUIRED` when the packet, interface, route, or repair budget is insufficient.

Use `NEEDS_STRONGER_EXECUTOR` when implementation remains judgment-heavy after Sol attempts to settle it.

Use `BLOCKED_RUNTIME` for missing model/tool/worktree/runtime capability.

Use `BLOCKED_EXTERNAL_BOUNDARY` for unauthorized merge, push, deploy, production, payment, destructive, or other external action.
