# Organization and command chain v0.5

## Authority model

Company Swarm is a hierarchical control plane around parallel isolated execution. Only logical TD-01 has staffing/route authority. PK-01 is the persistent single Notion coordination writer. RB-01 owns Gate verdicts. Domain/test/CI/integration roles own evidence within bounded scopes.

| Role | Staff | Decide contracts | Product code | Test code/scope | Notion coordination | Integrate | Accept |
|---|---:|---:|---:|---:|---:|---:|---:|
| TD-01 | yes | yes with review/evidence | no | no | authorize only | no | final after RB-01 |
| PK-01 | no | no | no | no | single writer | no | no |
| RB-01 | no | gate/recommend | no | review only | no | no | G0/G1/G4 verdict |
| AR-01 | no | analyze | no | no | no | no | no |
| Domain Developer | no | packet-local only | allowlist | no | no | no | no |
| Paired QE | no | no | no | allowlist/yes | no | no | lane verdict |
| TM-01 | no | no | no | strategy/review | no | no | plan approval |
| CI-01 | no | delivery platform only | no | pipeline/config | no | no | pipeline readiness |
| SQ-01 | no | no | no | security/performance | no | no | findings |
| INT-01 | no | no | mechanical conflicts only | no | no | yes | no |

Other roles request staffing through a structured `staffing_request`; they never create children.

## Organization manifest

Use `pkos-company-swarm/org-v2`. It records:

- run/generation/Director epoch/current Pack;
- sole spawn authority;
- configured/observed concurrency;
- Notion coordination writer/mode/schema/control requirements;
- Session role/parent/manager/model/effort/state/persistence/Notion-write flag;
- worktree/write scope/pair/epoch/Pack;
- Lane pair/scope/dependencies/epoch/Pack;
- Gates and canonical pipeline.

Exactly one technical director, one persistent coordination-governance scribe (`PK-01`), one review chair and one integration owner are required. PK-01 must be the only Session with `notion_write=true`.

## Lifecycle

```text
planned -> provisioned -> acknowledged -> active
-> waiting_on_dependency -> handed_off -> settled -> idle -> retired
-> blocked | superseded
```

Every material transition emits an event candidate. PK-01 confirms it in Notion before a dependent S2/S3 barrier. The current projection is derived from confirmed events, not chat messages.

## Staffing order

1. TD-01 establishes Run identity and authority.
2. Provision persistent PK-01.
3. Bind/propose Notion schema, Run/event/outbox/receipt/Pack/checkpoint.
4. Provision persistent RB-01.
5. G0 determines domains, pairs, TM/CI/SQ/INT/AR needs.
6. Provision each developer and paired tester together.
7. Provision INT-01 before first handoff but keep it waiting until G3.
8. Do not create prestige roles without packet, artifact destination and settlement condition.

## Ownership

- one worktree per writer;
- one active writer per path prefix;
- product/test/pipeline/security/performance/integration ownership separated;
- shared generated files, schemas, lockfiles, navigation/localization/build manifests get one named owner or deterministic integration rule;
- no lane pushes directly to the integration branch;
- unrelated user changes are preserved/listed;
- stale generation/epoch/Pack results remain history but cannot update current state.

Overlapping write ownership is a G1 failure.

## Review meetings

A meeting is a synchronized evidence review. RB-01 writes meeting ID, Gate, frozen plan/candidate revision, agenda/questions, required attendees/evidence, barrier condition, decision rule and verdict path. TD-01 routes the same packet; PK-01 records the meeting/verdict/evidence pointers. Missing evidence is explicitly missing, never reconstructed from memory.

## Escalation

```text
implementation ambiguity -> TD-01
missing/stale context -> CONTEXT_REQUESTED -> PK-01/TD-01
product defect -> paired developer
systemic testability/architecture -> TM-01 + RB-01 + TD-01
CI infrastructure/authority -> TD-01 with external-boundary evidence
semantic integration conflict -> owning lanes + RB-01 + TD-01
Notion write/schema conflict -> PK-01 dead-letter/conflict event + TD-01
three repair generations -> REPLAN_ORG
director loss -> verified checkpoint + authorized TAKEOVER
```

## Split-brain protection

Every packet/result/event contains Director epoch. A takeover increments it exactly one and reissues active packets. Old-epoch results cannot mutate the current projection. The protocol does not claim a transactional lock; when exclusive authority cannot be established, block honestly.
