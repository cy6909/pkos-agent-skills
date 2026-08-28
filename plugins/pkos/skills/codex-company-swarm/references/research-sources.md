# Design sources and rationale

The Skill combines established engineering, event-sourcing, transactional-outbox, secure-delivery and PKOS ideas. Sources inform design; explicit Skill contracts govern a run.

## OpenAI Codex

- Codex subagents: https://developers.openai.com/codex/subagents/
- Configuration reference: https://developers.openai.com/codex/config-reference/
- Agent Skills: https://developers.openai.com/codex/skills/
- AGENTS.md: https://developers.openai.com/codex/guides/agents-md/

Applied: focused child context, custom roles/model effort, inspectable sessions, cautious parallel writes, Skill packaging and instruction discovery.

## Organization and delivery

- Team Topologies: https://teamtopologies.com/key-concepts
- Scrum Guide / Definition of Done: https://scrumguides.org/scrum-guide.html

Applied: stream-aligned lanes, enabling quality roles, CI platform capability, explicit evidence-based done. The requested Technical Director hierarchy is stronger than Scrum autonomy.

## CI/Jenkins

- Jenkins Pipeline: https://www.jenkins.io/doc/book/pipeline/
- Jenkinsfile: https://www.jenkins.io/doc/book/pipeline/jenkinsfile/
- Multibranch: https://www.jenkins.io/doc/book/pipeline/multibranch/

Applied: source-controlled Pipeline as Code, multibranch discovery, reproducible agents, retained reports/artifacts and safe promotion.

## Secure development

- NIST SSDF SP 800-218: https://csrc.nist.gov/pubs/sp/800/218/final
- OWASP ASVS: https://owasp.org/www-project-application-security-verification-standard/
- OWASP MASVS: https://mas.owasp.org/MASVS/
- OWASP WSTG: https://owasp.org/www-project-web-security-testing-guide/

Applied: lifecycle security, risk-based verification, mobile/web coverage, retained evidence and triage rather than scanner-only confidence.

## Durable coordination

- Martin Fowler, Event Sourcing: https://martinfowler.com/eaaDev/EventSourcing.html
- Microsoft transactional outbox guidance: https://learn.microsoft.com/azure/architecture/patterns/transactional-outbox
- AWS Prescriptive Guidance, transactional outbox: https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html

Applied: append-only semantic events, current projections, local write-ahead outbox, idempotency, receipts, watermarks, replay and checkpoints. The Skill does not claim cross-system ACID or a distributed lock.

## PKOS

The repository's canonical Project, Memory, Notion tool, Audit and Sol–Luna protocols remain primary internal sources. Company Swarm v0.5 adds a durable execution coordination plane while preserving one Feature Registry, one Current Truth and bounded memory.
