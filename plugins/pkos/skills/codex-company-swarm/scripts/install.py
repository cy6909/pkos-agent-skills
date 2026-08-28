#!/usr/bin/env python3
"""Install the Codex Company Swarm Skill and/or Sol Max role definitions safely."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Iterable, Set

ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "codex-company-swarm"
EXCLUDED_NAMES = {"__pycache__", ".DS_Store"}


def default_codex_home() -> Path:
    raw = os.environ.get("CODEX_HOME")
    return Path(raw).expanduser() if raw else Path.home() / ".codex"


def default_skills_home() -> Path:
    return Path.home() / ".agents" / "skills"


def ignore_names(_directory: str, names: list[str]) -> Set[str]:
    return {name for name in names if name in EXCLUDED_NAMES or name.endswith((".pyc", ".zip"))}


def atomic_copytree(source: Path, destination: Path, force: bool, dry_run: bool) -> None:
    if source.resolve() == destination.resolve():
        print("Skill already at %s" % destination)
        return
    if destination.exists() and not force:
        raise FileExistsError("refusing to overwrite %s; use --force" % destination)
    if dry_run:
        print("DRY-RUN copy tree %s -> %s" % (source, destination))
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=str(destination.parent)) as temp_dir:
        staged = Path(temp_dir) / destination.name
        shutil.copytree(source, staged, ignore=ignore_names)
        if destination.exists():
            shutil.rmtree(destination)
        staged.replace(destination)


def copy_file(source: Path, destination: Path, force: bool, dry_run: bool) -> None:
    if destination.exists() and not force:
        raise FileExistsError("refusing to overwrite %s; use --force" % destination)
    if dry_run:
        print("DRY-RUN copy %s -> %s" % (source, destination))
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agents-only", action="store_true", help="install role TOMLs only")
    parser.add_argument("--standalone", action="store_true", help="install Skill to ~/.agents/skills and roles to CODEX_HOME/agents")
    parser.add_argument("--project-root", type=Path, help="install Skill to <project>/.agents/skills and roles to <project>/.codex/agents")
    parser.add_argument("--codex-home", type=Path, default=default_codex_home())
    parser.add_argument("--skills-home", type=Path, default=default_skills_home())
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)

    selected = int(args.agents_only) + int(args.standalone) + int(args.project_root is not None)
    if selected != 1:
        parser.error("choose exactly one of --agents-only, --standalone, or --project-root")

    codex_home = args.codex_home.expanduser().resolve()
    install_skill = args.standalone or args.project_root is not None
    if args.project_root:
        project_root = args.project_root.expanduser().resolve()
        skill_destination = project_root / ".agents" / "skills" / SKILL_NAME
        agent_destination = project_root / ".codex" / "agents"
        config_destination = project_root / ".codex" / "company-swarm.config.toml.example"
    else:
        skill_destination = args.skills_home.expanduser().resolve() / SKILL_NAME
        agent_destination = codex_home / "agents"
        config_destination = codex_home / "company-swarm.config.toml.example"

    try:
        if install_skill:
            atomic_copytree(ROOT, skill_destination, args.force, args.dry_run)
        for source in sorted((ROOT / "assets" / "agent-configs").glob("*.toml")):
            copy_file(source, agent_destination / source.name, args.force, args.dry_run)
        copy_file(ROOT / "assets" / "config.toml.fragment", config_destination, args.force, args.dry_run)
    except (FileExistsError, OSError) as exc:
        print("ERROR: %s" % exc, file=sys.stderr)
        return 1

    if install_skill:
        print("Skill target: %s" % skill_destination)
    print("Agent target: %s" % agent_destination)
    print("Config example: %s" % config_destination)
    print("The installer never edits the active Codex config automatically. Restart Codex or open a fresh task after installation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
