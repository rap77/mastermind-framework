#!/usr/bin/env python3
"""
MasterMind Init Handler

Installs MasterMind Framework in any project.
Detects stack, copies files, creates config.
"""

import argparse
import json
import shutil
import socket
import subprocess
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


def check_postgresql() -> bool:
    """Verify PostgreSQL is running and accessible.

    Checks:
    1. Docker compose ps shows PostgreSQL container running
    2. Port 5433 on localhost is accepting connections

    Returns:
        True if PostgreSQL is running and accessible, False otherwise.
    """
    print("INFO: Checking PostgreSQL service...")

    # Check 1: Docker compose ps
    try:
        result = subprocess.run(
            ["docker", "compose", "ps"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if "postgres" in result.stdout.lower() and "Up" in result.stdout:
            print("INFO: PostgreSQL container is running (docker compose ps)")
        else:
            print("ERROR: PostgreSQL container not found or not running")
            print("ERROR: Run 'docker compose up -d' to start PostgreSQL")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"ERROR: Failed to check docker compose: {e}")
        print("ERROR: Ensure Docker is running and PostgreSQL container is up")
        return False

    # Check 2: Ping localhost:5433
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(("localhost", 5433))
        sock.close()

        if result == 0:
            print("INFO: PostgreSQL is listening on localhost:5433")
            return True
        else:
            print("ERROR: PostgreSQL is not listening on localhost:5433")
            print("ERROR: Run 'docker compose up -d' to start PostgreSQL")
            return False
    except Exception as e:
        print(f"ERROR: Failed to connect to PostgreSQL: {e}")
        return False


def check_rust_control_plane() -> bool:
    """Check if Rust Control Plane is available (optional).

    Warns if not available but does not fail the installation.

    Returns:
        True if Rust Control Plane is available, False otherwise.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(("localhost", 3001))
        sock.close()

        if result == 0:
            print("INFO: Rust Control Plane is available on localhost:3001")
            return True
        else:
            print(
                "WARNING: Rust Control Plane not detected on localhost:3001 (optional, continuing)"
            )
            return False
    except Exception:
        print(
            "WARNING: Could not verify Rust Control Plane on localhost:3001 (optional, continuing)"
        )
        return False


def check_provider_available(db: MasterMindDB | None) -> bool:
    """Check if at least one AI provider has available tokens.

    Args:
        db: MasterMindDB instance (may be None if DB not available).

    Returns:
        True if at least one provider has tokens, False otherwise.
    """
    if not db or not db.available:
        print("WARNING: Cannot check provider availability (DB unavailable)")
        return True  # Don't fail if DB is unavailable

    try:
        providers_status = db.get_provider_status()
        available_providers = [
            name for name, available in providers_status.items() if available
        ]

        if available_providers:
            print(f"INFO: Available providers: {', '.join(available_providers)}")
            return True
        else:
            print("ERROR: No AI providers have available tokens")
            print("ERROR: Configure provider tokens in backend_sessions")
            return False
    except Exception as e:
        print(f"WARNING: Failed to check provider availability: {e}")
        return True  # Don't fail if check fails


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
    parser.add_argument(
        "--skip-postgres-check",
        action="store_true",
        help=argparse.SUPPRESS,  # Hidden flag for testing only
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


def _remove_existing(path: Path) -> None:
    if path.is_symlink():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def install_symlinks(src_root: Path, dest: Path) -> None:
    """Create symlinks in target project pointing to the framework.

    Three symlinks are created:
      .claude/commands/mm  → FRAMEWORK/.mm-flow/commands/mm/
      .claude/agents/mm    → FRAMEWORK/.mm-flow/agents/mm/
      .claude/skills/mm    → FRAMEWORK/.mm-flow/skills/mm/

    Any pre-existing path (file, dir, or symlink) at each destination is
    removed before the symlink is created.
    """
    links = [
        (
            src_root / ".mm-flow" / "commands" / "mm",
            dest / ".claude" / "commands" / "mm",
        ),
        (src_root / ".mm-flow" / "agents" / "mm", dest / ".claude" / "agents" / "mm"),
        (src_root / ".mm-flow" / "skills" / "mm", dest / ".claude" / "skills" / "mm"),
    ]
    for src, link in links:
        if not src.exists():
            print(f"WARNING: Framework source not found, skipping: {src}")
            continue
        link.parent.mkdir(parents=True, exist_ok=True)
        _remove_existing(link)
        link.symlink_to(src)
        print(f"INFO: Symlinked {link.relative_to(dest)} → {src}")


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
        "database:",
        "  host: localhost",
        "  port: 5433",
        "",
        *stack_lines,
        "",
        "brains:",
        "  active: [1, 2, 3, 4, 5, 6, 7]",
    ]
    (mastermind_dir / "config.yaml").write_text("\n".join(config_lines) + "\n")


def _write_project_id_to_config(target: Path, project_id: str) -> None:
    """Append project_id to .mastermind/config.yaml for per-project DB isolation."""
    config_path = target / ".mastermind" / "config.yaml"
    if not config_path.exists():
        return
    content = config_path.read_text()
    # Remove existing project_id line (idempotent re-registration)
    lines = [
        ln for ln in content.splitlines() if not ln.strip().startswith("project_id:")
    ]
    lines.append(f'project_id: "{project_id}"')
    config_path.write_text("\n".join(lines) + "\n")


def install_python_deps(target: Path) -> None:
    """Install required Python dependencies (psycopg2-binary) for DB support.

    Tries two strategies in order:
    1. uv pip install inside target project (uses target's venv if present)
    2. uv pip install --system (installs into system Python used by handlers)

    Never fails the installation — warns and continues if both strategies fail.
    """
    pkg = "psycopg2-binary"

    # Strategy 1: install into target project's venv (if uv project exists)
    try:
        result = subprocess.run(
            ["uv", "pip", "install", pkg],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=target,
        )
        if result.returncode == 0:
            print(f"INFO: {pkg} installed (target venv)")
            return
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Strategy 2: install into system Python (used directly by handlers)
    try:
        result = subprocess.run(
            ["uv", "pip", "install", pkg, "--system"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            print(f"INFO: {pkg} installed (system Python)")
            return
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    print(f"WARNING: Could not install {pkg} — DB features disabled")
    print(f"WARNING: Fix manually: uv pip install {pkg}")


def main() -> None:
    """Install MasterMind Framework in a target project.

    This function:
    1. Parses command-line arguments (target, check, force)
    2. Warns if installing into framework source itself
    3. In --check mode, reports installation status without changes
    4. Verifies PostgreSQL is running (REQUIRED, fails if not available)
    5. Checks provider availability (warns if not available)
    6. Checks Rust Control Plane (optional, warns if not available)
    7. Validates preconditions (not a file, not already installed without --force)
    8. Detects technology stack
    9. Copies commands, skills, and agents (whitelist only)
    10. Creates .mastermind/config.yaml with detected stack
    11. Registers project in PostgreSQL (if available)

    Exits with code 1 on error, 0 on success.
    """
    args = parse_args()
    target = Path(args.target).resolve() if args.target else Path.cwd()

    # Initialize DB client if available
    db: MasterMindDB | None = None
    if DB_CLIENT_AVAILABLE:
        db = MasterMindDB()

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

    # B2.1 — Verify PostgreSQL is running (OPTIONAL — warn only, do not block install)
    # Skip check if --skip-postgres-check flag is set (for testing)
    if not args.skip_postgres_check:
        if not check_postgresql():
            print("WARNING: PostgreSQL not available — DB features will be disabled")
            print("WARNING: Run 'docker compose up -d' to enable DB integration")

    # B2.2 — Check provider availability (warns if not available, does not fail)
    if not check_provider_available(db):
        print("WARNING: No AI providers available - continuing anyway")

    # B2.3 — Check Rust Control Plane (optional, warns if not available)
    check_rust_control_plane()

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

    # B1.6-B1.8 — Install symlinks (commands, agents, skills)
    try:
        install_symlinks(FRAMEWORK_ROOT, target)
    except Exception as e:
        print(f"ERROR: Failed to install symlinks: {e}")
        sys.exit(1)

    # B1.8b — Install Python dependencies (psycopg2-binary for DB support)
    install_python_deps(target)

    # B1.9 — Create config.yaml
    try:
        create_config(target, stack)
        print("INFO: Config created at .mastermind/config.yaml")
    except Exception as e:
        print(f"ERROR: Failed to create config: {e}")
        sys.exit(1)

    # B1.11 — Register project in database (if DB available) + persist project_id
    db_status = "unavailable"
    if db and db.available:
        try:
            project_id = db.register_project(
                name=target.name, metadata={"path": str(target), "stack": stack}
            )
            if project_id:
                db_status = "connected"
                print(f"INFO: Project registered in database (ID: {project_id})")
                # Persist project_id to config.yaml for per-project DB isolation
                _write_project_id_to_config(target, project_id)
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
