# Codex Company Swarm v0.8.0

`codex-company-swarm` is PKOS's explicit maximum-quality parallel delivery mode: one logical Technical Director, Director-routed sidebar-visible tasks, bounded reusable staffing, persistent PK-01 Notion coordination, Review Board gates, paired developers/testers, exact-candidate CI, one Integration Owner, recovery, traceability, and canonical writeback.

## v0.7: visible routing and bounded concurrency

- TD-01 records model, effort, rationale, risk, and routing source for each visible Task Packet. Sol Max remains the high-risk/product default; Luna Max is preferred for bounded independent tests, CI/verifiers, and frozen mechanical work.
- Formal children use `create_thread`, repository writers use worktrees, titles include run/role/lane, and registry records retain thread/host/cursor identity for follow-up reuse and recovery. Hidden subagents are not formal Company Swarm roles.
- Defaults are three product lanes, target six active children, minimum productive concurrency four, active hard cap eight, registered hard cap twelve, and a 90-second underfill alert.
- TD-01 reconciles on lifecycle boundaries, waits on at most eight visible targets with cursors, reuses an affinity task before creating one, and records an action or evidence-backed underfill reason.
- The project-approved CI wins. Jenkins-as-code is only the governance fallback when no approved provider exists.

The BOOT→G5 gates, PK-01/INT-01 single writers, paired lanes, exact-candidate review, receipts, traceability, recovery, and acceptance contract are unchanged.

## v0.6 foundation: progressive-disclosure runtime

The delivery contract is unchanged; its prompt layout is not.

```text
startup metadata
  -> compact SKILL.md state machine
    -> one reference only when the next transition needs it
      -> scripts/schemas/examples for deterministic detail
```

The entrypoint now contains only registers, invariants, conditional reference routing, BOOT→G5 transitions, acceptance guards, and final statuses. Detailed schemas, field lists, MFSQ guidance, Jenkins rules, event/outbox logic, Pack Delta, recovery, and traceability remain in focused references and scripts.

A CI-enforced prompt budget prevents regression:

```text
SKILL.md <= 10.5 KB
frontmatter description <= 360 chars
openai.yaml <= 560 bytes
root SKILL + TD role <= 12 KB
ordinary role TOML <= 1.25 KB
reference <= 6.5 KB
no unconditional startup reference reads
```

This reduces activation context without removing Notion coordination, evidence, or quality gates.

## Runtime architecture

```text
Codex messages -> .pkos outbox/checkpoints -> PK-01 -> Notion projections/events/evidence
                                               ↓
                                  PKOS Feature/Current Truth/ADR/Audit/Memory
```

Notion stores compact semantic state and stable evidence pointers, not full chats or raw logs.

## Install/update

```bash
codex plugin marketplace upgrade pkos-agent-skills
python plugins/pkos/skills/codex-company-swarm/scripts/install.py --agents-only --force
```

Restart Codex and invoke explicitly:

```text
$codex-company-swarm
```

## Validate

```bash
python plugins/pkos/skills/codex-company-swarm/scripts/audit_prompt_budget.py
python plugins/pkos/skills/codex-company-swarm/scripts/validate_install.py
python -m unittest discover -s plugins/pkos/skills/codex-company-swarm/tests -v
python plugins/pkos/skills/codex-company-swarm/scripts/validate_org.py plugins/pkos/skills/codex-company-swarm/assets/examples/staffing-small-two-lane.example.json
python plugins/pkos/skills/codex-company-swarm/scripts/validate_org.py plugins/pkos/skills/codex-company-swarm/assets/examples/staffing-luna-escalation-reuse.example.json
```

Migration from v0.6: replace `org-v2` with `org-v3`; register the current task as visible TD-01; bind existing child IDs rather than recreating them; add `staffing_budget`, `concurrency_state`, visible identity/cursor fields, and per-task routing fields; map dependency waits to `queued`. Validate before claiming the cache is active, then restart/open a fresh Codex task and confirm the skill appears.

`COMPANY_SWARM_ACCEPTED` still requires writable, ready, in-sync Notion coordination, exact-candidate CI, complete traceability, G4 acceptance, confirmed PKOS writeback, final checkpoint, dashboard, and retrospective.
