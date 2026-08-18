# Research sources and design lineage

The Skill is independent of CodeHive. It borrows general workflow ideas from CodeHive planning—bounded services, ownership, generations, barriers, evidence, repair, and recovery—but implements them with Codex tasks, worktrees, durable files, and deterministic scripts.

These sources are examples and design evidence, not proof that one route is universally optimal.

## Sol/Luna and Codex orchestration examples

- Solweaver: https://github.com/jay7793/solweaver
- Codex Model Routing Team: https://github.com/zjp1997720/codex-model-routing-team
- GPT-5.6 Orbit: https://github.com/yashau/gpt-5-6-orbit
- OpenAI Codex: https://github.com/openai/codex

They support explicit model routing, named roles or visible tasks, bounded ownership, fresh review, health probes, and runtime identity checks. Credible implementations do not make Luna Max the universal default; they keep open-ended judgment with stronger planning/review roles.

## Workflow, evidence, and evaluation sources

- Superpowers: https://github.com/obra/superpowers
- Compound Engineering Plugin: https://github.com/EveryInc/compound-engineering-plugin
- Academic Research Skills: https://github.com/Imbad0202/academic-research-skills
- Google Skills: https://github.com/google/skills

Useful patterns adopted here:

- fresh bounded child context;
- durable ledgers and artifact-path handoffs;
- task-level verification plus cumulative review;
- no worker-spawned reviewers;
- explicit model and effort on every route;
- non-inferiority evaluation on the exact role;
- repeated trials, medians, and tail latency;
- blind or fresh review to reduce anchoring;
- token volume separated from monetary/subscription cost.

## Additional source set supplied for the research task

- https://github.com/msitarzewski/agency-agents
- https://github.com/multica-ai/andrej-karpathy-skills
- https://github.com/arturseo-geo/llm-knowledge-base
- https://github.com/anthropics/knowledge-work-plugins
- https://github.com/mukul975/Anthropic-Cybersecurity-Skills
- https://github.com/xixu-me/awesome-persona-distill-skills
- https://github.com/safishamsi/graphify
- https://github.com/nashsu/llm_wiki

These broaden the reference set for persona specialization, progressive knowledge loading, structured skills, security review, graph-based context, and repository understanding. This package does not claim every repository was an empirical benchmark of Sol/Luna coding quality.

## Supported conclusion

A Sol planner/integrator plus Luna bounded-worker workflow is implementable in Codex. Quality depends on correct task routing, frozen interfaces, ownership isolation, deterministic evidence, integration checks, and fresh review for risk. The correct route must be measured on the user's tasks; model names alone do not guarantee quality, speed, or token savings.
