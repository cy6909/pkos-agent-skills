# Codex Company Swarm

`codex-company-swarm` is PKOS's maximum-quality, high-concurrency delivery mode. It treats one Codex root session as a Technical Director that centrally manages a persistent Review Board, domain development lanes, paired independent testers, CI/CD platform work, security/performance specialists, one Integration Owner, and PKOS writeback.

## Install

Refresh/install the `pkos` plugin from this repository, then install the custom role TOMLs:

```bash
python plugins/pkos/skills/codex-company-swarm/scripts/install.py --agents-only
```

For project-local installation:

```bash
python plugins/pkos/skills/codex-company-swarm/scripts/install.py \
  --project-root /path/to/project
```

Merge supported keys from `assets/config.toml.fragment`, restart Codex or open a fresh task, and invoke explicitly:

```text
$codex-company-swarm
```

The Skill disables implicit invocation because it can create many Sol Max sessions.

## Operating model

- The current session is the sole `TD-01`; never spawn a second Director.
- `RB-01` leads requirements/current-state gap/implementation-path/feature-inventory review and the final implementation review.
- Every product-code developer has one reciprocal paired tester; developers do not own test scope or acceptance.
- Testers design and implement MFSQ tests, including security and performance, and all authoritative tests run in the canonical pipeline.
- Existing CI/CD is reused when valid. When no usable pipeline exists, the CI role bootstraps Jenkins as source-controlled Pipeline as Code.
- One Integration Owner builds the cumulative candidate; the Review Board accepts or returns it; the Director reports with an evidence dashboard and verified PKOS writeback.

Read the Skill's `SKILL.md` and `references/` for the full G0–G5 contracts.

## Validate

```bash
python plugins/pkos/skills/codex-company-swarm/scripts/validate_install.py
python -m unittest discover \
  -s plugins/pkos/skills/codex-company-swarm/tests -v
```
