# Contributing to PKOS Agent Skills

Thank you for helping improve PKOS.

## Design invariants

Every contribution must preserve these invariants:

1. Route before read.
2. Search before create.
3. One canonical owner per durable fact.
4. Current Truth is clean; history is auditable elsewhere.
5. Project Feature Registry is the project-wide canonical feature ledger.
6. Memory storage may grow, but context working sets are always bounded.
7. Notion writes must be verified; never claim persistence without tool success.
8. Sensitive memory must never be inferred into a confirmed profile.

## Skill design

Keep each skill focused on a recognizable workflow. Put detailed schemas and policy in `references/` and keep `SKILL.md` concise enough for progressive disclosure.

A new or changed skill should specify:

- trigger conditions;
- when it must *not* trigger;
- expected inputs;
- deterministic workflow steps;
- write / read boundaries;
- failure behavior;
- output contract;
- referenced protocol files.

## Pull requests

Run:

```bash
python scripts/validate.py
```

Then include:

- problem being solved;
- protocol / skill files changed;
- compatibility implications;
- at least one positive trigger example;
- at least one negative / non-trigger example.

Protocol-breaking changes should also update `CHANGELOG.md`.
