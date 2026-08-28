#!/usr/bin/env python3
"""Enforce progressive-disclosure and prompt-size budgets for Company Swarm."""

from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[1]

MAX_SKILL_BYTES = 10_500
MAX_DESCRIPTION_CHARS = 360
MAX_OPENAI_YAML_BYTES = 560
MAX_DEFAULT_PROMPT_CHARS = 330
MAX_AGENT_BYTES = 1_250
MAX_CONTROL_AGENT_BYTES = 1_500
MAX_CORE_LOAD_BYTES = 12_000
MAX_REFERENCE_BYTES = 6_500
CONTROL_AGENTS = {
    "pkos_company_technical_director.toml",
    "pkos_company_governance_scribe.toml",
}


def utf8_size(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").encode("utf-8"))


def estimate_tokens(characters: int) -> int:
    return int(math.ceil(characters / 4.0))


def frontmatter(text: str) -> Dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return {}
    values: Dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line or line.startswith((" ", "\t")):
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def default_prompt(text: str) -> str:
    match = re.search(r'^\s*default_prompt:\s*["\'](.*)["\']\s*$', text, re.MULTILINE)
    return match.group(1) if match else ""


def normalized_paragraphs(text: str) -> List[str]:
    values: List[str] = []
    for raw in re.split(r"\n\s*\n", text):
        value = re.sub(r"\s+", " ", raw.strip())
        if len(value) >= 180 and not value.startswith(("```", "|")):
            values.append(value.lower())
    return values


def audit(root: Path = ROOT) -> Tuple[List[str], Dict[str, object]]:
    errors: List[str] = []
    metrics: Dict[str, object] = {}

    skill_path = root / "SKILL.md"
    openai_path = root / "agents" / "openai.yaml"
    agent_root = root / "assets" / "agent-configs"
    reference_root = root / "references"

    if not skill_path.is_file():
        return ["missing SKILL.md"], metrics

    skill = skill_path.read_text(encoding="utf-8")
    skill_bytes = len(skill.encode("utf-8"))
    metadata = frontmatter(skill)
    description = metadata.get("description", "")
    metrics["skill_bytes"] = skill_bytes
    metrics["skill_tokens_estimate"] = estimate_tokens(len(skill))
    metrics["description_chars"] = len(description)

    if skill_bytes > MAX_SKILL_BYTES:
        errors.append("SKILL.md exceeds %d bytes: %d" % (MAX_SKILL_BYTES, skill_bytes))
    if len(description) > MAX_DESCRIPTION_CHARS:
        errors.append("frontmatter description exceeds %d chars: %d" % (MAX_DESCRIPTION_CHARS, len(description)))
    if "Treat this file as an executable control program. Do not preload its references." not in skill:
        errors.append("SKILL.md must explicitly forbid reference preloading")
    if "## Reference loading" not in skill:
        errors.append("SKILL.md requires a conditional reference-loading map")
    if re.search(r"(?is)read\s+\[[^\]]+\].{0,80}before\s+(provision|start|staff)", skill):
        errors.append("SKILL.md contains an unconditional startup reference read")

    openai_bytes = 0
    prompt_chars = 0
    if not openai_path.is_file():
        errors.append("missing agents/openai.yaml")
    else:
        openai = openai_path.read_text(encoding="utf-8")
        openai_bytes = len(openai.encode("utf-8"))
        prompt_chars = len(default_prompt(openai))
        if openai_bytes > MAX_OPENAI_YAML_BYTES:
            errors.append("agents/openai.yaml exceeds %d bytes: %d" % (MAX_OPENAI_YAML_BYTES, openai_bytes))
        if prompt_chars > MAX_DEFAULT_PROMPT_CHARS:
            errors.append("openai.yaml default_prompt exceeds %d chars: %d" % (MAX_DEFAULT_PROMPT_CHARS, prompt_chars))
    metrics["openai_yaml_bytes"] = openai_bytes
    metrics["default_prompt_chars"] = prompt_chars

    agent_sizes: Dict[str, int] = {}
    if not agent_root.is_dir():
        errors.append("missing assets/agent-configs")
    else:
        for path in sorted(agent_root.glob("*.toml")):
            size = utf8_size(path)
            agent_sizes[path.name] = size
            limit = MAX_CONTROL_AGENT_BYTES if path.name in CONTROL_AGENTS else MAX_AGENT_BYTES
            if size > limit:
                errors.append("%s exceeds %d bytes: %d" % (path.name, limit, size))
    metrics["agent_bytes"] = agent_sizes

    td_size = agent_sizes.get("pkos_company_technical_director.toml", 0)
    core_load = skill_bytes + td_size
    metrics["root_core_load_bytes"] = core_load
    metrics["root_core_tokens_estimate"] = estimate_tokens(len(skill) + td_size)
    if core_load > MAX_CORE_LOAD_BYTES:
        errors.append("root Skill + TD role exceeds %d bytes: %d" % (MAX_CORE_LOAD_BYTES, core_load))

    reference_sizes: Dict[str, int] = {}
    if reference_root.is_dir():
        for path in sorted(reference_root.glob("*.md")):
            size = utf8_size(path)
            reference_sizes[path.name] = size
            if size > MAX_REFERENCE_BYTES:
                errors.append("reference %s exceeds %d bytes: %d" % (path.name, MAX_REFERENCE_BYTES, size))
    metrics["reference_bytes"] = reference_sizes

    paragraph_owner: Dict[str, str] = {}
    duplicate_paragraphs: List[str] = []
    runtime_files = [skill_path]
    runtime_files.extend(sorted(agent_root.glob("*.toml")) if agent_root.is_dir() else [])
    for path in runtime_files:
        for paragraph in normalized_paragraphs(path.read_text(encoding="utf-8")):
            owner = paragraph_owner.get(paragraph)
            if owner and owner != path.name:
                duplicate_paragraphs.append("%s == %s" % (owner, path.name))
            else:
                paragraph_owner[paragraph] = path.name
    if duplicate_paragraphs:
        errors.append("duplicate long runtime paragraphs: %s" % ", ".join(sorted(set(duplicate_paragraphs))))
    metrics["duplicate_long_paragraphs"] = len(set(duplicate_paragraphs))

    return errors, metrics


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(list(argv) if argv is not None else None)

    errors, metrics = audit(args.root)
    print(
        "Prompt budget: SKILL=%s bytes (~%s tokens), root core=%s bytes (~%s tokens), description=%s chars, openai prompt=%s chars."
        % (
            metrics.get("skill_bytes", 0),
            metrics.get("skill_tokens_estimate", 0),
            metrics.get("root_core_load_bytes", 0),
            metrics.get("root_core_tokens_estimate", 0),
            metrics.get("description_chars", 0),
            metrics.get("default_prompt_chars", 0),
        )
    )
    if errors:
        print("Company Swarm prompt-budget audit failed:", file=sys.stderr)
        for error in errors:
            print("- %s" % error, file=sys.stderr)
        return 1
    print("Company Swarm prompt-budget audit OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
