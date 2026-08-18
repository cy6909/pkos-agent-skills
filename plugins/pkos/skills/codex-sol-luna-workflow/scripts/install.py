#!/usr/bin/env python3
"""Install the Codex Sol-Luna Skill and/or named agent definitions safely."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "codex-sol-luna-workflow"
AGENT_FILES = {
    "adaptive": [
        "codex_luna_worker.toml",
        "codex_sol_planner.toml",
        "codex_sol_reviewer.toml",
    ],
    "max-pair": [
        "codex_luna_max_worker.toml",
        "codex_sol_max_planner.toml",
        "codex_sol_max_reviewer.toml",
    ],
}
EXCLUDED_NAMES = {"__pycache__", ".DS_Store"}


def default_codex_home() -> Path:
    raw = os.environ.get("CODEX_HOME")
    return Path(raw).expanduser() if raw else Path.home() / ".codex"


def ignore_names(_directory: str, names: list[str]) -> set[str]:
    return {
        name
        for name in names
        if name in EXCLUDED_NAMES or name.endswith(".zip") or name.endswith(".pyc")
    }


def atomic_copytree(source: Path, destination: Path, force: bool, dry_run: bool) -> None:
    if source.resolve() == destination.resolve():
        print(f"Skill already at {destination}")
        return
    if destination.exists() and not force:
        raise FileExistsError(f"refusing to overwrite {destination}; use --force")
    if dry_run:
        print(f"DRY-RUN copy tree {source} -> {destination}")
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent) as temp_dir:
        staged = Path(temp_dir) / destination.name
        shutil.copytree(source, staged, ignore=ignore_names)
        if destination.exists():
            shutil.rmtree(destination)
        staged.replace(destination)


def copy_file(source: Path, destination: Path, force: bool, dry_run: bool) -> None:
    if destination.exists() and not force:
        raise FileExistsError(f"refusing to overwrite {destination}; use --force")
    if dry_run:
        print(f"DRY-RUN copy {source} -> {destination}")
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def selected_agent_names(profile: str) -> list[str]:
    names: list[str] = []
    if profile in {"adaptive", "all"}:
        names.extend(AGENT_FILES["adaptive"])
    if profile in {"max-pair", "all"}:
        names.extend(AGENT_FILES["max-pair"])
    return names


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--standalone",
        action="store_true",
        help="install the Skill under CODEX_HOME/skills and named agents under CODEX_HOME/agents",
    )
    mode.add_argument(
        "--agents-only",
        action="store_true",
        help="install only named agent definitions; use this for PKOS/plugin mode",
    )
    mode.add_argument(
        "--skill-only",
        action="store_true",
        help="install only the Skill under CODEX_HOME/skills or --project-root/.agents/skills",
    )
    parser.add_argument(
        "--codex-home",
        type=Path,
        default=default_codex_home(),
        help="Codex home (default: CODEX_HOME or ~/.codex)",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        help="with --skill-only, install to <project>/.agents/skills",
    )
    parser.add_argument(
        "--profile",
        choices=("adaptive", "max-pair", "all"),
        default="all",
        help="agent definitions to install",
    )
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if args.project_root and not args.skill_only:
        parser.error("--project-root can be used only with --skill-only")

    codex_home = args.codex_home.expanduser().resolve()
    skill_destination = (
        args.project_root.expanduser().resolve() / ".agents" / "skills" / SKILL_NAME
        if args.project_root
        else codex_home / "skills" / SKILL_NAME
    )

    install_skill = args.standalone or args.skill_only
    install_agents = args.standalone or args.agents_only

    try:
        if install_skill:
            atomic_copytree(ROOT, skill_destination, args.force, args.dry_run)
        if install_agents:
            for name in selected_agent_names(args.profile):
                copy_file(
                    ROOT / "assets" / "agent-configs" / name,
                    codex_home / "agents" / name,
                    args.force,
                    args.dry_run,
                )
    except (FileExistsError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if install_skill:
        print(f"Skill target: {skill_destination}")
    if install_agents:
        print(f"Agent target: {codex_home / 'agents'}")
    print(
        "The installer does not edit config.toml. Merge the multi-agent snippet if "
        "needed, restart Codex/open a new task, and run the smoke test in "
        "references/runtime-setup.md."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
