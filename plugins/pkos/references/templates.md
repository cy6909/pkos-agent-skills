# PKOS Templates

## Pointer

```text
[NODE-ID] Name -> <page>
Purpose: one sentence.
Summary: current routing summary only.
READ WHEN: concrete task triggers.
SKIP WHEN: cases where detail is unnecessary.
Status: active | deprecated | superseded | archived
Last Verified: YYYY-MM-DD
```

## Project Root Map

```text
Node ID: ROOT-<PROJECT>
Type: Project Root Map
Canonical For: project entry, current snapshot, L1 address space
Summary: <3-8 lines>
READ WHEN: first project entry, cross-domain work, fact routing
SKIP WHEN: never
Status: active
Last Verified: YYYY-MM-DD
```

Root body:

- Project Manifest: mission/scope/lifecycle/repos/design/runtime/source precedence.
- Current Snapshot: phase, 5-8 core capabilities, <=5 P0/P1, <=5 risks, 3-5 recent material changes.
- System Map: high-level system/container/data flow.
- Active Working Set: 3-8 pointers.
- Pointer Table: Product/Capabilities/Architecture/Engineering/Operations/Planning/Governance/Evidence.
- Update Contract.

## DEC / ADR

```text
Title: DEC-XXX | Decision
Status: proposed | accepted | superseded | rejected
Context:
Decision:
Options:
Rationale:
Trade-offs:
Consequences:
Revisit When:
Related Nodes:
```

## Incident

```text
Impact / Scope
Current Status
Symptoms
Timeline / Evidence
Hypotheses & Eliminated Causes
Confirmed Root Cause / Confidence
Fix
Verification
Prevention
Related Runbook / Architecture / Decision
```

## Audit event

`Event ID | Time | Actor/Agent | Change Class | Trigger | Canonical Node | Action | Reason | Before Summary | After Summary | Evidence | Related ADR/INC | Verification | Reversible`
