#!/usr/bin/env python3
"""Activate the next recommended objective from the roadmap."""

from __future__ import annotations

import json
import subprocess
from argparse import ArgumentParser, Namespace
from pathlib import Path


def project_root() -> Path:
    """Find the git project root, falling back to file-relative detection."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except Exception:
        pass
    return Path(__file__).resolve().parent.parent.parent.parent


ROOT = project_root()
PLANNING_DIR = ROOT / ".mm-flow" / "planning"
ROADMAP_JSON = PLANNING_DIR / "roadmap" / "objectives.json"
CHANGES_DIR = PLANNING_DIR / "changes"
ARCHIVE_DIR = PLANNING_DIR / "archive"
COMMANDS_DIR = Path(__file__).resolve().parent
DISCOVER_HANDLER = COMMANDS_DIR / "discover-handler.py"


def parse_args() -> Namespace:
    """Parse CLI args."""
    parser = ArgumentParser(description="Activate the next recommended objective.")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Generate a lighter/faster package for the recommended objective.",
    )
    return parser.parse_args()


def load_roadmap() -> list[dict[str, object]]:
    """Load roadmap objective records."""
    if not ROADMAP_JSON.exists():
        raise FileNotFoundError(
            "Roadmap not found. Run /mm:discover --roadmap --existing first."
        )
    return json.loads(ROADMAP_JSON.read_text(encoding="utf-8"))


def get_recommended_next(
    objectives: list[dict[str, object]],
) -> dict[str, object] | None:
    """Return the recommended-next roadmap entry, if any."""
    for objective in objectives:
        if objective.get("recommended_next") is True:
            return objective
    return None


def active_objective_dirs() -> list[Path]:
    """Return active objective package directories."""
    if not CHANGES_DIR.exists():
        return []
    return [path for path in CHANGES_DIR.iterdir() if path.is_dir()]


def run_discover_for_objective(
    slug: str, name: str, quick: bool
) -> subprocess.CompletedProcess[str]:
    """Materialize the objective package via discover-handler."""
    cmd = [
        "python3",
        str(DISCOVER_HANDLER),
        "--existing",
        "--objective",
        slug,
        name,
    ]
    if quick:
        cmd.insert(5, "--quick")
    return subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def main() -> int:
    """Activate the next recommended roadmap objective."""
    args = parse_args()

    active_dirs = active_objective_dirs()
    if active_dirs:
        print("STATUS: FAILED")
        print(
            f"- Active objective package already exists: {active_dirs[0].relative_to(ROOT)}"
        )
        print(
            "- Archive or complete the current active objective before activating the next one."
        )
        return 1

    try:
        objectives = load_roadmap()
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print("STATUS: FAILED")
        print(f"- {exc}")
        return 1

    recommended = get_recommended_next(objectives)
    if recommended is None:
        print("STATUS: FAILED")
        print(
            "- No recommended_next objective found in .mm-flow/planning/roadmap/objectives.json"
        )
        return 1

    slug = str(recommended["slug"])
    name = str(recommended.get("name") or slug.replace("-", " ").title())

    result = run_discover_for_objective(slug, name, args.quick)
    if result.returncode != 0:
        print("STATUS: FAILED")
        print(f"- discover-handler failed for `{slug}`")
        if result.stdout.strip():
            print(result.stdout.strip())
        if result.stderr.strip():
            print(result.stderr.strip())
        return result.returncode

    print("STATUS: PASSED")
    print(f"- Activated recommended objective: `{slug}`")
    print(f"- Package created under: {CHANGES_DIR / slug}")
    print("- Next steps:")
    print(f"  1. /mm:discover-contract-check --objective {slug}")
    print("  2. /mm:complete-task <FIRST_TASK_ID> --brief")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
