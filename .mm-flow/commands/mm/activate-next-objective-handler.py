#!/usr/bin/env python3
"""Activate the next recommended objective from the roadmap."""

from __future__ import annotations

import importlib.util
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


def load_gate_status_helpers():
    """Load shared gate-status helpers from the sibling module file."""
    module_path = COMMANDS_DIR / "objective-gate-status.py"
    spec = importlib.util.spec_from_file_location(
        "mm_objective_gate_status", module_path
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load gate-status helpers from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_GATE_STATUS_HELPERS = load_gate_status_helpers()
infer_objective_gate_status = _GATE_STATUS_HELPERS.infer_objective_gate_status


def load_active_objective_helpers():
    """Load shared active-objective helpers from the sibling module file."""
    module_path = COMMANDS_DIR / "active-objective-state.py"
    spec = importlib.util.spec_from_file_location(
        "mm_active_objective_state", module_path
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load active-objective helpers from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_ACTIVE_OBJECTIVE_HELPERS = load_active_objective_helpers()
active_objective_dirs = _ACTIVE_OBJECTIVE_HELPERS.active_objective_dirs
find_active_objective_exception = (
    _ACTIVE_OBJECTIVE_HELPERS.find_active_objective_exception
)


def parse_args() -> Namespace:
    """Parse CLI args."""
    parser = ArgumentParser(description="Activate the next recommended objective.")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Generate a lighter/faster package for the recommended objective.",
    )
    return parser.parse_args()


def load_roadmap() -> object:
    """Load roadmap data as-is from objectives.json."""
    if not ROADMAP_JSON.exists():
        raise FileNotFoundError(
            "Roadmap not found. Run /mm:discover --roadmap --existing first."
        )
    return json.loads(ROADMAP_JSON.read_text(encoding="utf-8"))


def get_recommended_next(
    roadmap: object,
) -> dict[str, object] | None:
    """Return the recommended-next roadmap entry, if any.

    Supports both:
    - current list format: [{slug, recommended_next, ...}, ...]
    - future dict format: {recommended_next, objectives: [...]}
    """
    if isinstance(roadmap, list):
        for objective in roadmap:
            if isinstance(objective, dict) and objective.get("recommended_next"):
                return objective
        return None

    if isinstance(roadmap, dict):
        recommended_slug = roadmap.get("recommended_next")
        objectives = roadmap.get("objectives", [])
        if not recommended_slug or not isinstance(objectives, list):
            return None
        for objective in objectives:
            if not isinstance(objective, dict):
                continue
            if (
                objective.get("id") == recommended_slug
                or objective.get("slug") == recommended_slug
            ):
                return objective
    return None


def run_discover_for_objective(
    slug: str, name: str, quick: bool
) -> subprocess.CompletedProcess[str]:
    """Materialize the objective package via discover-handler."""
    cmd = [
        "python3",
        str(DISCOVER_HANDLER),
        "--existing",
        "--delegated-from",
        "activate-next-objective",
        "--objective",
        slug,
        name,
    ]
    if quick:
        cmd.insert(7, "--quick")
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

    try:
        roadmap = load_roadmap()
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print("STATUS: FAILED")
        print(f"- {exc}")
        return 1

    recommended = get_recommended_next(roadmap)
    if recommended is None:
        print("STATUS: FAILED")
        print(
            "- No recommended_next objective found in .mm-flow/planning/roadmap/objectives.json"
        )
        return 1

    slug = str(recommended.get("slug") or recommended.get("id"))
    name = str(
        recommended.get("title")
        or recommended.get("name")
        or slug.replace("-", " ").title()
    )
    active_dirs = active_objective_dirs(ROOT)
    if active_dirs:
        active_slugs = {path.name for path in active_dirs}
        matched_exception = find_active_objective_exception(
            ROOT,
            active_slugs,
            slug,
            "activate-next-objective",
        )
        if matched_exception is None:
            print("STATUS: FAILED")
            print(
                f"- Active objective package already exists: {active_dirs[0].relative_to(ROOT)}"
            )
            print(
                "- Archive or complete the current active objective before activating the next one."
            )
            return 1
        delegated_exception = find_active_objective_exception(
            ROOT,
            active_slugs,
            slug,
            "discover --existing --objective",
            "activate-next-objective",
        )
        if delegated_exception is None:
            print("STATUS: FAILED")
            print(
                "- Matched active-objective exception does not authorize the delegated discover materialization path via bundle metadata."
            )
            print(
                "- Add valid bundle metadata for `activate-next-objective` -> `discover --existing --objective`, or run discover directly with explicit discover scope."
            )
            return 1
        allowed_slugs = ", ".join(
            str(item) for item in matched_exception.get("objective_slugs", [])
        )
        print(f"ACTIVE_OBJECTIVE_EXCEPTION: {matched_exception.get('id', '')}")
        print(f"ALLOWED_OBJECTIVES: {allowed_slugs}")
        print(f"- {matched_exception.get('reason', '')}")
        print(f"- Expires when: {matched_exception.get('expires_when', '')}")

    gate_status, gate_guidance, gate_artifact = infer_objective_gate_status(ROOT, slug)
    if gate_status != "NO_CANONICAL" and gate_status != "PASSED":
        print("STATUS: BLOCKED")
        print(f"- Recommended objective `{slug}` is not activation-ready.")
        print(f"GATE_STATUS: {gate_status}")
        if gate_artifact:
            print(f"GATE_ARTIFACT: {gate_artifact}")
        print(f"- {gate_guidance}")
        return 2

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
