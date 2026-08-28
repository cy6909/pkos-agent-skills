# PKOS project, memory, and Notion integration v0.5

## One knowledge system

Company Swarm adds execution coordination, not a second project or memory architecture. Existing PKOS remains authoritative:

- Project Root Map and progressive disclosure;
- one Project Feature Registry;
- one Canonical Owner per durable fact;
- Current Truth separated from Audit/ADR/Incident/Evidence;
- bounded Memory Context Compiler;
- Search Before Create;
- verified external writes or exact pending writeback.

Run/Lane projections are operational views. They never become duplicate product truth.

## Phase 0 reads

TD-01/PK-01 resolve only the smallest needed:

1. Project Root and current snapshot;
2. target Capability/Feature/Architecture nodes;
3. Feature Registry schema/rows;
4. active procedural Memory and environment/design/deployment rules;
5. evidence required to resolve conflicts.

Do not recursively fetch Notion or copy broad history into children.

## Shared Pack and Source Manifest

Compile one versioned Shared Collaboration Pack from active canonical sources. Every child receives the same common constraints plus task-scoped context and acknowledges either direct verified sources or a brokered snapshot hash. Pack Delta/versioning rules are mandatory when shared facts change.

Long-term memory still uses `none | core | scoped | deep`. Token-insensitive mode does not justify stale/noisy history.

## Continuous coordination versus canonical writeback

PK-01 continuously writes compact Run/Lane/Session/Task/Feature projections, event decisions and evidence pointers. These are C1 operational coordination unless they also change durable product truth.

Canonical writeback occurs when durable truth changes:

- Feature behavior/status/acceptance -> Feature Registry and FEAT owner;
- API/schema/permission/contract -> canonical owner + Audit, ADR when needed;
- architecture/security/deployment model -> canonical owner + Audit + ADR;
- incident/data/security failure -> Incident plus stable prevention updates;
- reusable collaboration rule -> procedural Memory after write gate.

Do not defer operational coordination to G5, but do defer unverified canonical truth until evidence/review supports it.

## Feature projection

G0 maps every run Feature to an existing stable Feature ID or proposes one after Search Before Create. The existing Feature Registry projects current run/lane/development/test/CI/review/candidate/defect/evidence state at material transitions. History remains in the Event Ledger.

At G5, accepted durable fields, validation evidence, release and Last Verified are finalized in canonical owners. Full run logs are not pasted into them.

## Change and memory gates

Use C0–C5. Only stable reusable process lessons become procedural Memory. Do not store transient Session IDs, raw logs, temporary branches, one-off failures, volatile candidate IDs, or unsupported inference as durable memory.

A retrospective may remain episodic evidence. Compile stable prevention and reusable collaboration changes into current project nodes or procedural Memory with provenance/confidence/scope.

## Notion capability behavior

### Writable

Search/bind, write through outbox, verify receipts, update current projection, then perform approved canonical writeback. Report exact rows/nodes and receipts.

### Read-only/unavailable

Continue safe repository work when possible, preserve outbox and pending `pkos-writeback.json`, expose the block in the dashboard/checkpoint, and never claim Notion synchronization. Full accepted durable coordination is unavailable.

## Conflict resolution

When Notion conflicts with code/config/runtime/design/CI:

1. record the conflict event/evidence;
2. stop affected material transitions;
3. inspect authoritative evidence;
4. let TD-01/RB-01 establish current truth;
5. repair projection and canonical owner;
6. record Audit/ADR/Incident as applicable;
7. issue Pack Delta if shared context changed.
