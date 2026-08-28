# Design sources

**READ WHEN:** maintaining the Skill design. Never load during a delivery run.

## OpenAI Codex

- Build skills / progressive disclosure: https://developers.openai.com/codex/build-skills
- Customization overview: https://developers.openai.com/codex/customization/overview
- Subagents: https://developers.openai.com/codex/subagents/
- Configuration: https://developers.openai.com/codex/config-reference/
- AGENTS.md: https://developers.openai.com/codex/guides/agents-md/

Applied: concise `SKILL.md`, conditional references, scripts for deterministic checks, focused child context, custom roles, inspectable sessions, and isolated writes.

## Organization and delivery

- Team Topologies: https://teamtopologies.com/key-concepts
- Scrum Guide: https://scrumguides.org/scrum-guide.html
- Jenkins Pipeline/Jenkinsfile/Multibranch: https://www.jenkins.io/doc/book/pipeline/

Applied: stream-aligned lanes, enabling quality roles, CI platform capability, evidence-based done, and source-controlled delivery.

## Security and durability

- NIST SSDF SP 800-218: https://csrc.nist.gov/pubs/sp/800/218/final
- OWASP ASVS/MASVS/WSTG: https://owasp.org/
- Event Sourcing: https://martinfowler.com/eaaDev/EventSourcing.html
- Transactional outbox: https://learn.microsoft.com/azure/architecture/patterns/transactional-outbox

Applied: lifecycle security, risk-based verification, append-only semantic events, local write-ahead outbox, idempotency, receipts, watermarks, replay, and checkpoints. The Skill does not claim cross-system ACID or a distributed lock.

## PKOS

Shared Project, Memory, Notion, Audit, and Sol–Luna protocols remain authoritative. Company Swarm v0.6 changes prompt layout, not canonical ownership or completion semantics.
