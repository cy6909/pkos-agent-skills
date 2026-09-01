# Codex Company Swarm v0.10.0

`codex-company-swarm` optimizes acceptable product delivery per Token. The current main task is the sole planner, scheduler, and cumulative integrator. Every formal child is a sidebar-visible Codex task; hidden subagents and child delegation are forbidden.

## Defaults

- TD-01 plus at most three mutually exclusive product developers and one shared independent tester.
- Reviewer is demand-driven; PK-01 writes Notion only in gate batches.
- Active-child hard cap is 6; registered hard cap is 8.
- Product code must be at least 70% of productive child concurrency. Waiting, reporting, repeated context, and environment-blocked work are not productive.

Task Packets contain exactly seven allowed fields and at most 1200 Chinese characters. Follow-ups are delta-only; settlements are at most 600 Chinese characters. Coordination/reporting/Notion above 30% of estimated Token use, or 120 minutes without a candidate/accepted feature, enters `CONSOLIDATION_MODE` and stops new tasks/features.

Each generation has one cumulative candidate. TD-01 integrates a lane immediately after developer self-test instead of waiting for every lane. Reviewer starts only after candidate freeze and a recorded trigger. Two strict-review returns also force consolidation.

Developer handoff requires an exact pushed SHA, remote-12 clean checkout, targeted tests, type/build checks, and—when Web changes—public-production evidence from real `cy6909` Chrome. Windows local is limited to editing, static Git, and scheduling; services, tests, Docker, private origin, and GitHub Actions are forbidden.

CI performs a bounded 10-minute controller/executor/credential/job/artifact preflight. Two prerequisite failures or more than 15 minutes blocked stops the CI lane, reports the exact boundary and recovery action, and releases capacity.

Notion human-readable content is accurate Chinese and is batched only at requirement freeze, lane handoff, candidate freeze, final strict review, and final deployment/acceptance. It updates the original Product Feature Registry rather than creating a duplicate summary database.

## Validate and migrate

```bash
python plugins/pkos/skills/codex-company-swarm/scripts/audit_prompt_budget.py
python plugins/pkos/skills/codex-company-swarm/scripts/validate_install.py
python -m unittest discover -s plugins/pkos/skills/codex-company-swarm/tests -v
python plugins/pkos/skills/codex-company-swarm/scripts/validate_org.py plugins/pkos/skills/codex-company-swarm/assets/examples/organization.example.json
python plugins/pkos/skills/codex-company-swarm/scripts/migrate_org_v3.py OLD_ORG.json --output migration.json
```

For org-v3, checkpoint first and preserve evidence, receipts, generation, epoch, task identity, and settled results. TD-01 becomes integrator; reuse at most three developers and one tester, archive INT-01/extra testers, and reissue pending work as Task Packet v3. Never invent missing legacy fields.
