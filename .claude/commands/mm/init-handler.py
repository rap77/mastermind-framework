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

# Import db_client for PostgreSQL integration
# Graceful degradation: works even if asyncpg not installed
try:
    from db_client import MasterMindDB

    DB_CLIENT_AVAILABLE = True
except ImportError:
    DB_CLIENT_AVAILABLE = False
    MasterMindDB = None  # type: ignore

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
    "review",
    "ship",
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


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for init-handler.

    Returns:
        Parsed arguments including target path, check mode, and force flag.
    """
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
    """Detect the technology stack of a project.

    Args:
        target: Path to the project directory to scan.

    Returns:
        List of detected stack identifiers (e.g., ["nextjs", "python", "claude-code"]).
        Returns ["unknown"] if no recognized technologies are found.
    """
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
        except (json.JSONDecodeError, OSError) as e:
            print(f"WARNING: Failed to parse package.json: {e}")
            stack.append("nodejs")
    if (target / "pyproject.toml").exists() or (target / "requirements.txt").exists():
        stack.append("python")
    if (target / "Cargo.toml").exists():
        stack.append("rust")
    if (target / "go.mod").exists():
        stack.append("go")
    if (target / "CLAUDE.md").exists():
        stack.append("claude-code")
    return stack or ["unknown"]


def copy_commands(src_root: Path, dest: Path) -> None:
    """Copy MasterMind command files to target project.

    Args:
        src_root: Path to the MasterMind framework root directory.
        dest: Path to the target project directory.
    """
    src_commands = src_root / ".claude" / "commands" / "mm"
    dest_commands = dest / ".claude" / "commands" / "mm"
    dest_commands.mkdir(parents=True, exist_ok=True)

    for item in src_commands.iterdir():
        if item.is_file() and (
            item.name in COMMANDS_WHITELIST
            or item.name.endswith("-handler.py")
            or item.name == "db_client.py"
        ):
            shutil.copy2(item, dest_commands / item.name)


def _replace_directory_atomic(src: Path, dest: Path) -> None:
    """Atomically replace destination directory with source.

    Copies src to dest.tmp, then removes old dest and moves tmp into place.
    If copy fails, tmp is cleaned up and original dest is preserved.
    """
    tmp_dest = dest.parent / f"{dest.name}.tmp"
    try:
        shutil.rmtree(tmp_dest, ignore_errors=True)
        shutil.copytree(src, tmp_dest)
        if dest.exists():
            shutil.rmtree(dest)
        shutil.move(tmp_dest, dest)
    except Exception:
        # Clean up .tmp on failure
        shutil.rmtree(tmp_dest, ignore_errors=True)
        raise


def copy_skills(src_root: Path, dest: Path) -> None:
    """Copy MasterMind skill files to target project.

    Args:
        src_root: Path to the MasterMind framework root directory.
        dest: Path to the target project directory.
    """
    src_skills = src_root / ".claude" / "skills" / "mm"
    dest_skills = dest / ".claude" / "skills" / "mm"

    for skill_name in SKILLS_WHITELIST:
        src_skill = src_skills / skill_name
        if src_skill.exists():
            dest_skill = dest_skills / skill_name
            if dest_skill.exists():
                _replace_directory_atomic(src_skill, dest_skill)
            else:
                shutil.copytree(src_skill, dest_skill)


def copy_agents(src_root: Path, dest: Path) -> None:
    """Copy MasterMind agent files to target project.

    Args:
        src_root: Path to the MasterMind framework root directory.
        dest: Path to the target project directory.
    """
    src_agents = src_root / ".claude" / "agents" / "mm"
    dest_agents = dest / ".claude" / "agents" / "mm"

    for agent_name in AGENTS_WHITELIST:
        src_agent = src_agents / agent_name
        if src_agent.exists():
            dest_agent = dest_agents / agent_name
            if dest_agent.exists():
                _replace_directory_atomic(src_agent, dest_agent)
            else:
                shutil.copytree(src_agent, dest_agent)


def _sanitize_yaml_string(value: str) -> str:
    """Sanitize string for safe YAML embedding.

    Prevents YAML injection by escaping special characters.
    """
    return (
        value.replace('"', "'").replace(":", "-").replace("\n", " ").replace("\r", " ")
    )


def create_config(target: Path, stack: list[str]) -> None:
    """Create MasterMind configuration file in target project.

    Args:
        target: Path to the target project directory.
        stack: List of detected technology stack identifiers.
    """
    mastermind_dir = target / ".mastermind"
    mastermind_dir.mkdir(exist_ok=True)

    # Format stack as valid YAML list
    stack_lines = ["stack:"] + [f"  - {s}" for s in stack]

    config_lines = [
        "project:",
        f'  name: "{_sanitize_yaml_string(target.name)}"',
        "",
        "framework:",
        "  version: 3.0.0",
        "",
        *stack_lines,
        "",
        "brains:",
        "  active: [1, 2, 3, 4, 5, 6, 7]",
    ]
    (mastermind_dir / "config.yaml").write_text("\n".join(config_lines) + "\n")


def main() -> None:
    """Install MasterMind Framework in a target project.

    This function:
    1. Parses command-line arguments (target, check, force)
    2. Warns if installing into framework source itself
    3. In --check mode, reports installation status without changes
    4. Validates preconditions (not a file, not already installed without --force)
    5. Detects technology stack
    6. Copies commands, skills, and agents (whitelist only)
    7. Creates .mastermind/config.yaml with detected stack

    Exits with code 1 on error, 0 on success.
    """
    args = parse_args()
    target = Path(args.target).resolve() if args.target else Path.cwd()

    # Initialize DB client if available
    db = MasterMindDB() if DB_CLIENT_AVAILABLE else None

    # B1.12 — Warn if target == mastermind source
    try:
        if target.samefile(FRAMEWORK_ROOT):
            print(
                "WARNING: target is the MasterMind source directory itself — self-install detected"
            )
            print("WARNING: continuing anyway, but this may overwrite framework files")
    except FileNotFoundError:
        # One or both paths don't exist yet, fall back to string comparison
        if target == FRAMEWORK_ROOT.resolve():
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

    # Validate target is a directory, not a file
    if target.exists() and not target.is_dir():
        print("ERROR: target is not a directory")
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

    # B1.11 — Register project in database (if DB available)
    db_status = "unavailable"
    if db and db.available:
        try:
            project_id = db.register_project(
                name=target.name, path=str(target), stack=stack
            )
            if project_id:
                db_status = "connected"
                print(f"INFO: Project registered in database (ID: {project_id})")
            else:
                db_status = "unavailable"
                print("WARNING: Database connection failed - project not registered")
        except Exception as e:
            db_status = "error"
            print(f"WARNING: Failed to register project: {e}")
    else:
        print("INFO: PostgreSQL not available - project not registered")

    # B1.10 — Output
    print("STATUS: installed")
    print(f"DB: {db_status}")


if __name__ == "__main__":
    main()
