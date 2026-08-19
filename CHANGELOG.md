# Changelog

## 0.3.0 - 2026-08-19

- Keep the Skill-loading session as the sole Sol planner instead of spawning another planner.
- Require user-confirmed total and per-role session caps; reuse idle affinity-matched sessions and queue at capacity.
- Add deterministic `schedule_sessions.py` recommendations and a durable session-pool example.
- Require every lane to load the same PKOS Shared Collaboration Pack, canonical Notion sources, required skills, and governing standards.
- Enforce development-only local execution, remote environment evidence for tests/builds/containers/deployment, and a Figma-first gate for UI changes.
- Upgrade route/result contracts to `codex-sol-luna-route-v3` and `codex-sol-luna-result-v2` with negative validation coverage.

## 0.1.0 - 2026-08-11

Initial public repository scaffold.

- PKOS project knowledge address-space protocol.
- Capability Map and single Project Feature Registry model.
- C0-C5 audit / ADR / incident governance.
- PKOS long-term memory with temporal validity and provenance.
- Bounded Memory Context Compiler, paging, compaction, and GC.
- Eight Agent Skills.
- OpenAI repo marketplace packaging.
- English and Simplified Chinese documentation.
