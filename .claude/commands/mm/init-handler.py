#!/usr/bin/env python3
"""
MasterMind Init Handler

Installs MasterMind Framework in any project.
Detects stack, copies files, creates config.
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

FRAMEWORK_ROOT = Path(__file__).parent.parent.parent.parent

COMMANDS_WHITELIST = {
    "init.md",
    "discover.md",
    "complete-task.md",
    "review.md",
    "ship.md",
}
SKILLS_WHITELIST = {
    "brain-context",
    "brain-persistence",
    "discover",
    "safe-commit",
}
AGENTS_WHITELIST = {
    "brain-01-product",
    "brain-02-ux",
    "brain-03-ui",
    "brain-04-frontend",
    "brain-05-backend",
    "brain-06-qa",
    "brain-07-growth",
    "discover-planner",
    "rediscovery-auditor",
    "task-executor",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Install MasterMind Framework in a project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 init-handler.py --target /path/to/project\n"
            "  python3 init-handler.py --check --target /path/to/project\n"
            "  python3 init-handler.py --force --target /path/to/project\n"
        ),
    )
    parser.add_argument(
        "--target",
        default=None,
        metavar="PATH",
        help="Target directory (default: current working directory)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if MasterMind is installed in target (no changes)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force overwrite if .mastermind/ already exists",
    )
    return parser.parse_args()


def detect_stack(target: Path) -> list[str]:
    stack = []
    if (target / "package.json").exists():
        try:
            pkg = json.loads((target / "package.json").read_text())
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            if "next" in deps:
                stack.append("nextjs")
            elif "react" in deps:
                stack.append("react")
            else:
                stack.append("nodejs")
        except Exception:
            stack.append("nodejs")
    if (target / "pyproject.toml").exists() or (target / "requirements.txt").exists():
        stack.append("python")
    if (target / "Cargo.toml").exists():
        stack.append("rust")
    if (target / "go.mod").exists():
        stack.append("go")
    return stack or ["unknown"]


def copy_commands(src_root: Path, dest: Path) -> None:
    src_commands = src_root / ".claude" / "commands" / "mm"
    dest_commands = dest / ".claude" / "commands" / "mm"
    dest_commands.mkdir(parents=True, exist_ok=True)

    for item in src_commands.iterdir():
        if item.is_file():
            if item.name in COMMANDS_WHITELIST:
                shutil.copy2(item, dest_commands / item.name)
            elif item.name.endswith("-handler.py") or item.name == "db_client.py":
                shutil.copy2(item, dest_commands / item.name)


def copy_skills(src_root: Path, dest: Path) -> None:
    src_skills = src_root / ".claude" / "skills" / "mm"
    dest_skills = dest / ".claude" / "skills" / "mm"

    for skill_name in SKILLS_WHITELIST:
        src_skill = src_skills / skill_name
        if src_skill.exists():
            dest_skill = dest_skills / skill_name
            if dest_skill.exists():
                shutil.rmtree(dest_skill)
            shutil.copytree(src_skill, dest_skill)


def copy_agents(src_root: Path, dest: Path) -> None:
    src_agents = src_root / ".claude" / "agents" / "mm"
    dest_agents = dest / ".claude" / "agents" / "mm"

    for agent_name in AGENTS_WHITELIST:
        src_agent = src_agents / agent_name
        if src_agent.exists():
            dest_agent = dest_agents / agent_name
            if dest_agent.exists():
                shutil.rmtree(dest_agent)
            shutil.copytree(src_agent, dest_agent)


def create_config(target: Path, stack: list[str]) -> None:
    mastermind_dir = target / ".mastermind"
    mastermind_dir.mkdir(exist_ok=True)

    config_lines = [
        "project:",
        f'  name: "{target.name}"',
        f'  path: "{target}"',
        "",
        "framework:",
        "  version: 3.0.0",
        f'  source: "{FRAMEWORK_ROOT}"',
        "",
        f"stack: {stack}",
        "",
        "db:",
        "  host: localhost",
        "  port: 5433",
        "  name: mastermind_bd",
        "",
        "brains:",
        "  active: [1, 2, 3, 4, 5, 6, 7]",
    ]
    (mastermind_dir / "config.yaml").write_text("\n".join(config_lines) + "\n")


def main():
    args = parse_args()
    target = Path(args.target).resolve() if args.target else Path.cwd()

    # B1.12 — Warn if target == mastermind source
    if target.resolve() == FRAMEWORK_ROOT.resolve():
        print(
            "WARNING: target is the MasterMind source directory itself — self-install detected"
        )
        print("WARNING: continuing anyway, but this may overwrite framework files")

    # B1.3 — --check mode
    if args.check:
        config_path = target / ".mastermind" / "config.yaml"
        if config_path.exists():
            print("STATUS: installed")
        else:
            print("STATUS: not-installed")
        return

    # B1.11 — Protection: no overwrite without --force
    mastermind_dir = target / ".mastermind"
    if mastermind_dir.exists() and not args.force:
        print(
            "ERROR: MasterMind already installed in target. Use --force to overwrite."
        )
        sys.exit(1)

    # Ensure target exists
    if not target.exists():
        target.mkdir(parents=True)

    # B1.5 — Detect stack
    stack = detect_stack(target)
    print(f"INFO: Detected stack: {stack}")

    # B1.6 — Copy commands
    try:
        copy_commands(FRAMEWORK_ROOT, target)
        print("INFO: Commands copied")
    except Exception as e:
        print(f"ERROR: Failed to copy commands: {e}")
        sys.exit(1)

    # B1.7 — Copy skills
    try:
        copy_skills(FRAMEWORK_ROOT, target)
        print("INFO: Skills copied")
    except Exception as e:
        print(f"ERROR: Failed to copy skills: {e}")
        sys.exit(1)

    # B1.8 — Copy agents
    try:
        copy_agents(FRAMEWORK_ROOT, target)
        print("INFO: Agents copied")
    except Exception as e:
        print(f"ERROR: Failed to copy agents: {e}")
        sys.exit(1)

    # B1.9 — Create config.yaml
    try:
        create_config(target, stack)
        print("INFO: Config created at .mastermind/config.yaml")
    except Exception as e:
        print(f"ERROR: Failed to create config: {e}")
        sys.exit(1)

    # B1.10 — Output
    print("STATUS: installed")


if __name__ == "__main__":
    main()
