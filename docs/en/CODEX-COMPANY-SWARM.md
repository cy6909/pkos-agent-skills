# Codex Company Swarm v0.5

`codex-company-swarm` is PKOS's maximum-quality, high-concurrency delivery mode. One Codex root session acts as logical Technical Director and centrally manages a persistent Notion coordination scribe, Review Board, domain developer/tester pairs, CI/CD, security/performance, one Integration Owner, traceability, checkpoints, and canonical PKOS writeback.

## What changed in v0.5

Notion is no longer only read at startup and updated at the end. It becomes a durable coordination control plane for material project events and recovery:

```text
Codex messages -> .pkos outbox/checkpoints -> PK-01 -> Notion projections/events/evidence
                                               ↓
                                  PKOS Feature/Current Truth/ADR/Audit/Memory
```

The design deliberately does **not** store full chats or raw logs in Notion.

### Persistent PK-01

`PK-01` is provisioned before the Review Board and remains active through G5. It is the single writer for:

- Run/Lane/Session/Task/Pack/Checkpoint current state;
- append-only semantic Event & Decision history;
- evidence pointers and checksums;
- material Feature lifecycle projections;
- Context Requests and brokered snapshots;
- Pack Delta acknowledgements;
- outbox receipts/watermark/dead letters;
- takeover/recovery records;
- final authorized PKOS canonical writeback and retrospective.

### Minimal Notion schema

Reuse the existing Project Feature Registry and add:

1. Swarm Run & Lane Registry;
2. Event & Decision Ledger;
3. Evidence Registry.

Schema discovery follows Search Before Create and validates stable IDs/properties before creating anything.

### Recovery and completeness

Every current packet/result carries generation, Director epoch, Pack revision, and source identity. v0.5 adds checksummed checkpoints, resume tokens, authorized takeover with epoch increment, stale-result rejection, and Requirement-to-Notion traceability validators.

## Install/update

```bash
codex plugin marketplace upgrade pkos-agent-skills
python plugins/pkos/skills/codex-company-swarm/scripts/install.py --agents-only --force
```

Restart Codex or open a fresh task, then invoke explicitly:

```text
$codex-company-swarm
```

This expensive mode keeps implicit invocation disabled.

## Validate

```bash
python plugins/pkos/skills/codex-company-swarm/scripts/validate_install.py
python -m unittest discover \
  -s plugins/pkos/skills/codex-company-swarm/tests -v
```

A full accepted route requires writable, ready, in-sync Notion coordination. Read-only/unavailable Notion can produce a durable checkpoint, but not `COMPANY_SWARM_ACCEPTED`.
