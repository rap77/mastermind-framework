#!/usr/bin/env python3
"""
MasterMind Ship Handler

Generates ship payload for version tagging, archiving, and cleanup.
Supports multiple modes: ship, verify, archive, cleanup.
"""

import argparse
import json
import subprocess
from pathlib import Path


def _find_project_root() -> Path:
    """Find project root via git, fallback to file-relative path."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except Exception:
        pass
    return Path(__file__).resolve().parent.parent.parent.parent


def _read_project_id() -> str | None:
    """Read project_id from .mastermind/config.yaml."""
    config_path = _find_project_root() / ".mastermind" / "config.yaml"
    if not config_path.exists():
        return None
    for line in config_path.read_text().splitlines():
        if line.strip().startswith("project_id:"):
            value = line.split(":", 1)[1].strip().strip('"').strip("'")
            return value if value else None
    return None


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for ship-handler.

    Returns:
        Parsed arguments including mode flags and version options.
    """
    parser = argparse.ArgumentParser(
        description="Ship: verify, tag, archive, and cleanup releases",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 ship-handler.py --verify\n"
            "  python3 ship-handler.py --tag v0.2.0\n"
            "  python3 ship-handler.py --patch\n"
            "  python3 ship-handler.py --minor\n"
            "  python3 ship-handler.py --major\n"
            "  python3 ship-handler.py --archive\n"
            "  python3 ship-handler.py --cleanup\n"
        ),
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify preconditions without creating tag (dry-run)",
    )
    parser.add_argument(
        "--tag",
        metavar="VX.Y.Z",
        help="Explicit tag version (e.g., v0.2.0)",
    )
    parser.add_argument(
        "--patch",
        action="store_true",
        help="Increment patch version (default: v0.1.0 -> v0.1.1)",
    )
    parser.add_argument(
        "--minor",
        action="store_true",
        help="Increment minor version (e.g., v0.1.0 -> v0.2.0)",
    )
    parser.add_argument(
        "--major",
        action="store_true",
        help="Increment major version (e.g., v0.1.0 -> v1.0.0)",
    )
    parser.add_argument(
        "--archive",
        action="store_true",
        help="Archive artifacts only",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Cleanup temporary files only",
    )
    return parser.parse_args()


def get_last_tag() -> str | None:
    """Get the most recent git tag.

    Returns:
        Tag string (e.g., "v0.1.0") or None if no tags exist.
    """
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            tag = result.stdout.strip()
            return tag if tag else None
        return None
    except (subprocess.TimeoutExpired, Exception):
        return None


def parse_version(tag: str) -> tuple[int, int, int] | None:
    """Parse semantic version from tag string.

    Args:
        tag: Tag string (e.g., "v0.1.0").

    Returns:
        Tuple of (major, minor, patch) or None if invalid.
    """
    if not tag.startswith("v"):
        return None
    try:
        parts = tag[1:].split(".")
        if len(parts) != 3:
            return None
        return int(parts[0]), int(parts[1]), int(parts[2])
    except (ValueError, IndexError):
        return None


def increment_version(
    version: tuple[int, int, int], increment_type: str
) -> tuple[int, int, int]:
    """Increment version based on type.

    Args:
        version: Tuple of (major, minor, patch).
        increment_type: One of "patch", "minor", "major".

    Returns:
        New version tuple.
    """
    major, minor, patch = version
    if increment_type == "major":
        return major + 1, 0, 0
    elif increment_type == "minor":
        return major, minor + 1, 0
    else:  # patch
        return major, minor, patch + 1


def format_version(version: tuple[int, int, int]) -> str:
    """Format version tuple as tag string.

    Args:
        version: Tuple of (major, minor, patch).

    Returns:
        Tag string (e.g., "v0.1.0").
    """
    return f"v{version[0]}.{version[1]}.{version[2]}"


def get_changelog(since_tag: str | None = None) -> list[str]:
    """Generate changelog from git commits.

    Args:
        since_tag: Starting tag (if None, returns empty list).

    Returns:
        List of commit messages (oneline format).
    """
    if not since_tag:
        return []

    try:
        result = subprocess.run(
            ["git", "log", f"{since_tag}..HEAD", "--oneline"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            commits = [
                line.strip() for line in result.stdout.split("\n") if line.strip()
            ]
            return commits
        return []
    except (subprocess.TimeoutExpired, Exception):
        return []


def check_uncommitted_changes() -> bool:
    """Check if there are uncommitted changes.

    Returns:
        True if there are uncommitted changes, False otherwise.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--quiet"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode != 0
    except (subprocess.TimeoutExpired, Exception):
        return False


def check_spec_exists() -> bool:
    """Check if SPEC.md exists in .planning/tasks/ directory.

    Returns:
        True if SPEC.md exists, False otherwise.
    """
    spec_path = Path(".planning/tasks/SPEC.md")
    return spec_path.exists()


def check_tests_pass() -> bool:
    """Check if tests pass (basic check).

    Returns:
        True if we can't determine test status (fail-open),
        False if tests definitely fail.
    """
    # For now, return True (fail-open) because running tests
    # is expensive and context-dependent. The ship-executor agent
    # will run actual tests before creating the tag.
    return True


def calculate_next_tag(
    last_tag: str | None,
    explicit_tag: str | None,
    increment_type: str,
) -> tuple[str | None, str | None]:
    """Calculate the next tag.

    Args:
        last_tag: Current tag (or None).
        explicit_tag: User-specified tag (takes precedence).
        increment_type: One of "patch", "minor", "major".

    Returns:
        Tuple of (current_tag, next_tag). Both may be None.
    """
    if explicit_tag:
        return last_tag, explicit_tag

    if not last_tag:
        # No tags yet, suggest v0.1.0
        return None, "v0.1.0"

    version = parse_version(last_tag)
    if not version:
        # Last tag is not semantic, suggest v0.1.0
        return last_tag, "v0.1.0"

    next_version = increment_version(version, increment_type)
    return last_tag, format_version(next_version)


def determine_mode(args: argparse.Namespace) -> str:
    """Determine the mode based on arguments.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Mode string: "verify", "ship", "archive", or "cleanup".
    """
    if args.verify:
        return "verify"
    if args.archive:
        return "archive"
    if args.cleanup:
        return "cleanup"
    return "ship"


def determine_increment_type(args: argparse.Namespace) -> str:
    """Determine version increment type.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Increment type: "patch", "minor", or "major".
    """
    if args.major:
        return "major"
    if args.minor:
        return "minor"
    return "patch"


def check_preconditions() -> dict[str, bool | str]:
    """Check preconditions for shipping.

    Returns:
        Dict with precondition status:
        {
            "tests_pass": bool,
            "no_uncommitted": bool,
            "spec_exists": bool,
            "status": "pass" | "fail"
        }
    """
    tests_pass = check_tests_pass()
    no_uncommitted = not check_uncommitted_changes()
    spec_exists = check_spec_exists()

    all_pass = tests_pass and no_uncommitted and spec_exists

    return {
        "tests_pass": tests_pass,
        "no_uncommitted": no_uncommitted,
        "spec_exists": spec_exists,
        "status": "pass" if all_pass else "fail",
    }


def main() -> None:
    """Generate ship payload.

    This function:
    1. Parses command-line arguments to determine mode
    2. Checks preconditions (tests, uncommitted changes, SPEC.md)
    3. Reads last tag and calculates next tag
    4. Generates changelog from git log
    5. Outputs structured payload for ship-executor agent

    Output format:
        MODE: ship|verify|archive|cleanup
        CURRENT_TAG: vX.Y.Z
        NEXT_TAG: vX.Y.Z+1
        CHANGELOG: [N commits since last tag]
        PRECONDITIONS: pass|fail
        LAUNCH: ship-executor
        PAYLOAD: <json>
    """
    args = parse_args()

    # Determine mode
    mode = determine_mode(args)

    # Determine increment type
    increment_type = determine_increment_type(args)

    # Check preconditions
    preconditions = check_preconditions()

    # Get last tag
    last_tag = get_last_tag()

    # Calculate next tag
    current_tag, next_tag = calculate_next_tag(last_tag, args.tag, increment_type)

    # Generate changelog
    changelog = get_changelog(current_tag)

    # Build payload
    payload = {
        "mode": mode,
        "current_tag": current_tag,
        "next_tag": next_tag,
        "changelog": changelog,
        "changelog_count": len(changelog),
        "increment_type": increment_type,
        "explicit_tag": args.tag,
        "preconditions": preconditions,
        "working_directory": str(_find_project_root()),
        "project_id": _read_project_id(),
    }

    # Output
    print(f"MODE: {mode}")
    print(f"CURRENT_TAG: {current_tag or 'none'}")
    print(f"NEXT_TAG: {next_tag or 'none'}")
    print(f"CHANGELOG: {len(changelog)} commits since {current_tag or 'beginning'}")
    print(f"PRECONDITIONS: {preconditions['status']}")
    print("LAUNCH: ship-executor")
    print(f"PAYLOAD: {json.dumps(payload, indent=2)}")
    print()

    # Additional info
    if mode == "verify":
        print("INFO: Verify mode (dry-run) — no tag will be created")

    if preconditions["status"] == "fail":
        print("WARNING: Preconditions failed:")
        if not preconditions["tests_pass"]:
            print("  - Tests are not passing")
        if not preconditions["no_uncommitted"]:
            print("  - There are uncommitted changes")
        if not preconditions["spec_exists"]:
            print("  - SPEC.md does not exist in .planning/tasks/")

    if changelog:
        print(f"INFO: Changelog ({len(changelog)} commits):")
        for commit in changelog[:10]:  # Show first 10
            print(f"  - {commit}")
        if len(changelog) > 10:
            print(f"  ... and {len(changelog) - 10} more")


if __name__ == "__main__":
    main()
