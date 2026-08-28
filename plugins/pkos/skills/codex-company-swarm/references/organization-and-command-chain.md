# Organization and command chain

## Purpose

The Company Swarm is a hierarchical control plane around parallel, isolated execution. It borrows the useful parts of a modern engineering organization—stream-aligned teams, an enabling quality group, a delivery platform, independent review, and one accountable technical leader—without pretending chat sessions are people or a real legal organization.

## Authority matrix

| Role | May spawn/retire sessions | May change architecture | May write product code | May write tests | May decide test scope | May integrate | May accept |
|---|---:|---:|---:|---:|---:|---:|---:|
| Technical Director | yes | yes, with Review Board record | no | no | no | no | final after Chair accepts |
| Review Board Chair | no | recommends / gates | no | no | reviews | no | implementation verdict |
| Requirements & Architecture Analyst | no | analyzes only | no | no | no | no | no |
| Domain Developer | no | only packet-local implementation choices | yes, allowlist only | no | no | no | no |
| Paired Quality Engineer | no | no | no | yes, allowlist only | yes | no | lane test verdict |
| Test Manager | no | no | no | may coordinate shared test assets | final test strategy | no | test-plan approval |
| CI/CD & Jenkins Engineer | no | delivery-platform decisions only | no | pipeline/config only | no | no | pipeline readiness |
| Security & Performance QE | no | no | no | security/performance tests only | specialist scope | no | specialist findings |
| Integration Owner | no | no | mechanical integration only | no | no | yes | no |
| PKOS Governance Scribe | no | no | no | no | no | no | no; writes approved durable truth |

Only the Director holds staffing authority. Other roles may request help by writing a `staffing_request` artifact with purpose, required role, scope, urgency, and blocking dependency.

## Session identity

Every session record contains:

```json
{
  "session_id": "D-BE-01",
  "role": "domain-developer",
  "domain": "backend",
  "parent_session_id": "TD-01",
  "managed_by": "TD-01",
  "model": "gpt-5.6-sol",
  "reasoning_effort": "max",
  "may_delegate": false,
  "generation": 1,
  "state": "planned",
  "worktree": ".worktrees/company-swarm/run-123/D-BE-01",
  "write_scope": ["server/**"],
  "paired_session_id": "T-BE-01",
  "task_packet": ".pkos/company-swarm/run-123/lanes/backend/task-packet.md"
}
```

The runtime identity is classified as `observed`, `configured`, or `unverified`. A role name is not proof of a model. This mode requires all active role records to request Sol Max; unverified identity must be disclosed, and an explicit mismatch blocks the route.

## Role lifecycle

```text
planned -> provisioned -> acknowledged -> active
       -> waiting_on_dependency -> active
       -> handed_off -> settled -> idle -> retired
       -> blocked
       -> superseded (new generation only)
```

The Director records every transition. A session may not be reused across an incompatible domain, generation, write scope, or memory-pack revision without an explicit reassignment packet and clean worktree state.

## Staffing rules

1. Create `RB-01` before implementation planning is accepted.
2. Create one developer only for a coherent stream-aligned domain with disjoint ownership.
3. Create the paired tester at the same time as the developer, not after implementation.
4. Create `TM-01` for any multi-lane, security-sensitive, performance-sensitive, mobile, AI/data, or production-critical change.
5. Create `CI-01` whenever pipeline capability is unknown, gapped, missing, or must be changed.
6. Create `SQ-01` when security or performance is material; for behavior-changing work, it is normally material.
7. Create `INT-01` before the first lane handoff, but do not let it write until the integration barrier opens.
8. Create `PK-01` only when durable Notion/PKOS writeback is non-trivial; the Director may perform simple governance orchestration itself.
9. Do not create empty prestige roles. A role must have a packet, artifact destination, and settlement condition.

## Work ownership

Parallel development requires:

- one worktree per writer;
- one active writer per path prefix;
- explicit test-path versus product-path ownership;
- frozen interface owners;
- no direct push to the integration branch by lanes;
- unrelated user changes preserved and listed;
- late or stale results retained as history but excluded from the active generation.

Overlapping path ownership is a G1 failure. Shared generated files, lockfiles, schemas, localization catalogs, navigation registries, or build manifests get one named owner or are deferred to `INT-01` with a deterministic update rule.

## Review Board meetings

A “meeting” is a synchronized evidence review, not free-form discussion. `RB-01` writes:

- meeting ID and gate;
- frozen candidate or plan revision;
- agenda and questions;
- required attendee session IDs;
- evidence each attendee must provide;
- response deadline expressed as a barrier condition, never a wall-clock promise;
- decision rule and verdict artifact path.

`TD-01` sends the same meeting packet to attendees, waits for required results, and returns the settled evidence set to the Chair. Missing evidence is recorded as missing; it is not reconstructed from memory.

## Escalation

- Developer implementation ambiguity -> Director; do not invent a new contract.
- Tester finds a product defect -> paired developer through a structured defect packet.
- Tester finds architectural/testability failure -> Test Manager + Review Chair + Director.
- CI authority/infrastructure missing -> Director with `BLOCKED_EXTERNAL_BOUNDARY` evidence.
- Integration semantic conflict -> Review Chair and Director; Integration Owner does not choose behavior.
- Repeated repair (three generations) -> `REPLAN_ORG`.
- Notion/code/runtime conflict -> verify evidence, establish current truth, then write back under PKOS governance.
