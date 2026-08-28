# Design sources and rationale

This Skill combines established engineering-organization and delivery ideas with Codex/PKOS constraints. Sources are guidance, not copied policy; the Skill's explicit contracts are authoritative for a run.

## OpenAI Codex

- Codex subagents and parallel work: https://developers.openai.com/codex/subagents/
- Codex configuration reference: https://developers.openai.com/codex/config-reference/
- Agent Skills: https://developers.openai.com/codex/skills/
- AGENTS.md instruction discovery: https://developers.openai.com/codex/guides/agents-md/

Applied ideas:

- focused child context and inspectable subagent threads;
- custom agent roles with model/reasoning/developer instructions;
- cautious parallel write behavior;
- Skill packaging with `SKILL.md`, references, scripts, assets, and UI metadata;
- project/user instruction precedence.

## Engineering organization

- Team Topologies key concepts: https://teamtopologies.com/key-concepts
- Scrum Guide and Definition of Done: https://scrumguides.org/scrum-guide.html

Applied ideas:

- stream-aligned domain lanes;
- enabling quality specialists;
- CI/CD as a platform capability;
- complicated-subsystem lanes only when justified;
- a concrete shared Definition of Done represented here by G0–G5 gates and evidence.

The Company Swarm intentionally keeps a stronger hierarchy than a Scrum Team because the user requested one Technical Director session to centrally manage every other session.

## CI/CD and Jenkins

- Jenkins Pipeline: https://www.jenkins.io/doc/book/pipeline/
- Using a Jenkinsfile: https://www.jenkins.io/doc/book/pipeline/jenkinsfile/
- Multibranch Pipeline: https://www.jenkins.io/doc/book/pipeline/multibranch/

Applied ideas:

- source-controlled Pipeline as Code;
- multibranch discovery;
- parallel stages where dependencies permit;
- archived machine-readable test reports and artifacts;
- reproducible, reviewable delivery configuration.

## Secure software and application verification

- NIST Secure Software Development Framework (SP 800-218): https://csrc.nist.gov/pubs/sp/800/218/final
- OWASP Application Security Verification Standard: https://owasp.org/www-project-application-security-verification-standard/
- OWASP Mobile Application Security Verification Standard: https://mas.owasp.org/MASVS/
- OWASP Web Security Testing Guide: https://owasp.org/www-project-web-security-testing-guide/

Applied ideas:

- security across the development lifecycle rather than a final scanner-only step;
- risk-based application/mobile verification;
- version-controlled security tests and retained evidence;
- explicit triage and no blind trust in tool output.

## PKOS integration

The repository's canonical PKOS project, memory, Notion tool, audit, and existing Sol–Luna references remain the primary internal sources. Company Swarm adds an execution organization and does not duplicate those protocols.
