---
name: pkos-project-writeback
description: Write durable software-project changes back to the correct PKOS canonical Notion node and keep maps, Feature Registry, audit, and decision history consistent. Use after meaningful product, feature, API, architecture, engineering, operations, incident, milestone, or risk changes. Do not persist transient scratch work with no long-term project value.
---

# PKOS Project Writeback

Load `../../references/audit-governance.md` for change classification and `../../references/pkos-project-spec.md` for propagation rules.

1. Classify the durable change: product/feature/architecture/decision/engineering/operations/incident/planning/risk/evidence/log.
2. Resolve the existing canonical owner from Root/Domain/Capability maps and registries. Search aliases before creating anything.
3. Assign C0-C5 change class.
4. Separate durable truth from process history:
   - durable current truth -> canonical node/registry;
   - debugging or meeting process -> log/evidence;
   - significant trade-off -> DEC/ADR;
   - production incident -> INC.
5. Update the smallest canonical owner and remove obsolete current statements that would create ambiguity.
6. Propagate only as required:
   - local detail -> smallest owner only;
   - node state/interface -> parent pointer summary;
   - feature state -> Feature Registry + Capability cache when material;
   - cross-cutting scope/architecture/project phase/P0-P1 -> Root snapshot/system map/active set.
7. For C2+, satisfy audit requirements. For C3, ADR is required. For C5, Incident is required.
8. Verify the new truth against code/tests/runtime/design/user decision as appropriate and update freshness metadata.
9. Verify each external write actually succeeded.

Never create a new “latest summary” to avoid updating an existing canonical owner.
