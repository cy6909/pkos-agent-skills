# Codex Company Swarm v0.6

`codex-company-swarm` is PKOS's explicit maximum-quality parallel delivery mode: one logical Technical Director, persistent PK-01 Notion coordination, Review Board gates, paired developers/testers, MFSQ and exact-candidate CI, one Integration Owner, recovery, traceability, and canonical writeback.

## v0.6: progressive-disclosure runtime

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
```

`COMPANY_SWARM_ACCEPTED` still requires writable, ready, in-sync Notion coordination, exact-candidate CI, complete traceability, G4 acceptance, confirmed PKOS writeback, final checkpoint, dashboard, and retrospective.
