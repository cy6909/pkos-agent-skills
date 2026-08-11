# PKOS Audit, ADR, and Current Truth

## Separation of concerns

- **Current Truth**: the canonical page's current valid state.
- **Audit Ledger**: compact semantic change events: who/agent, when, trigger, action, reason, before/after summary, evidence, verification.
- **ADR / DEC-***: durable explanation of significant design choices and trade-offs.
- **INC-***: incident timeline, impact, root cause, fix, verification, prevention.

Do not keep obsolete full bodies in Current Truth merely for history.

## Change classification

- C0 Editorial: spelling/format/link/non-semantic reorganization. Audit not required.
- C1 State: status/progress/owner/verification/implementation completion. Audit when materially tracked.
- C2 Contract: feature scope/API/schema/permission/behavior/data-flow/runtime contract. Audit required. ADR when trade-offs/compatibility matter.
- C3 Architecture: boundaries/tech stack/topology/core dependency/security model/cross-project relationship. Audit + ADR required.
- C4 Structural: canonical owner migration/page merge/split/Node ID retirement/registry restructuring. Audit required.
- C5 Incident/Security: production incident/data loss/security issue/rollback. Audit + Incident required. ADR if it creates an architecture decision.

## ADR gate

Create or update a DEC/ADR if any answer is yes:

1. Were two or more reasonable options traded off?
2. Did the change alter system boundaries, dependency direction, technology stack, data model, deployment model, or security model?
3. Will a future maintainer reasonably ask “why this and not the alternative?”
4. Is there material migration cost, compatibility cost, long-lived constraint, or trade-off?
5. Does it affect multiple Features, repos, platforms, or projects?
6. Does it supersede a prior formal decision?

## Completion gate for C2+

Before marking complete, verify:

- only one Current Truth remains;
- Root/Domain pointers still target the correct owner;
- Feature Registry / Architecture Map are synchronized where relevant;
- ADR / Incident requirements are satisfied;
- an Audit Event exists;
- code/test/runtime/design evidence supports the new current truth.
