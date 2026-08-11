# PKOS Specification

## 1. Project knowledge

PKOS models project knowledge as an address space. Root/Domain/Capability maps are routing structures; canonical nodes own facts; evidence verifies them.

Core invariants:

1. Route Before Read.
2. Search Before Create.
3. One Canonical Owner per durable fact.
4. Progressive Disclosure and Stop Rule.
5. Current Truth stays clean; history is kept in audit/decision/incident/evidence.
6. Pointer summaries are caches, not second sources of truth.
7. Every new canonical node is registered in one primary map.

### Layers

- L0 protocol;
- L1 Project Root (800–1500 tokens target);
- L2 Domain/Capability maps (500–1200 each);
- L3 canonical nodes;
- L4 raw evidence.

### Skeleton

`00 Control Plane / 10 Product / 15 Capabilities / 20 Architecture / 30 Engineering / 40 Operations / 50 Planning / 60 Governance & Audit / 80 Evidence / 90 Archive`.

### Capability and feature

Architecture answers *what exists and how it connects*. Capability answers *what each part provides*. Engineering answers *how code implements it*.

One project uses one Feature Registry. Capability pages use filtered views.

## 2. Current Truth, audit, ADR

Changes are classified C0-C5. C2+ requires audit, C3 requires ADR, C5 requires Incident. Current canonical pages should not keep obsolete full content beside the new state.

Audit events carry compact before/after summaries, cause, actor, evidence, verification, and related ADR/Incident.

## 3. Long-term memory

Notion Memory Registry is the durable address space; Core Profile is a compiled cache; Episodes are provenance.

Memory types: profile-semantic, goal-state, procedural, episodic.

Dynamic facts have temporal validity. Conflicting active facts are not allowed for the same meaning.

### Bounded context

Storage size must never determine prompt size. Every task passes through Need-Memory Gate, scope/status/time/sensitivity filters, retrieval/ranking, dedup/conflict resolution, and token-budget packing.

Recommended ordinary memory pack: about 1500–2500 tokens.

### Compaction / GC

Consolidate near-duplicate current memories into one canonical memory and preserve episodes. GC checks duplicates, expiry, staleness, low utility, orphan entries, unsupported sensitive inference, contradictions, and forget/delete residue.

## 4. Notion integration

PKOS is tool-name agnostic. It uses the capabilities exposed by the connected Notion MCP/app and never claims a write succeeded without a successful tool response.
