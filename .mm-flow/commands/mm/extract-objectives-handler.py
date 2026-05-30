#!/usr/bin/env python3
"""
MasterMind Extract Objectives Handler

Extracts objectives from existing roadmap or planning documents
and creates individual objective packages.
"""

from __future__ import annotations

import argparse
import json
import subprocess
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


def parse_args() -> argparse.Namespace:
    """Parse extract-objectives command arguments."""
    parser = argparse.ArgumentParser(
        description="Extract objectives from roadmap into individual packages"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Extract all objectives from roadmap",
    )
    parser.add_argument(
        "--slug",
        help="Extract a specific objective by slug",
    )
    parser.add_argument(
        "--output-dir",
        default=str(PLANNING_DIR / "changes"),
        help="Output directory for objective packages",
    )
    return parser.parse_args()


def load_roadmap() -> list[dict]:
    """Load roadmap objectives."""
    if not ROADMAP_JSON.exists():
        raise FileNotFoundError(f"Roadmap not found: {ROADMAP_JSON}")
    return json.loads(ROADMAP_JSON.read_text(encoding="utf-8"))


def extract_objective(objective: dict, output_dir: Path) -> int:
    """Extract a single objective into a package."""
    slug = objective.get("slug")
    if not slug:
        print("ERROR: Objective missing 'slug' field")
        return 1

    package_dir = output_dir / slug
    package_dir.mkdir(parents=True, exist_ok=True)

    # Create basic package files
    # requirements.md
    req_content = f"""# Requirements — {slug}

## Problem / Purpose
{objective.get('description', 'No description available')}

## Objective-level Acceptance Criteria
- [ ] The objective has an execution-ready package with requirements, design, tasks, and handoff.
- [ ] The implementation slice advances the target objective without breaking adjacent flows.
- [ ] Validation commands are documented and usable by another model or human operator.
"""
    (package_dir / "requirements.md").write_text(req_content)

    # design.md
    design_content = f"""# Design — {slug}

## Arquitectura
Ver archivo de diseño del proyecto.

## Dependencies
- No explicit upstream dependency declared

## Validation Strategy
- Run targeted Python tests or validation commands for touched areas.
- Run relevant web lint/typecheck commands when frontend files change.
- Refresh handoff state after completing or partially completing the objective.
"""
    (package_dir / "design.md").write_text(design_content)

    # tasks.md
    tasks_content = f"""# Tasks — {slug}

## Execution Rules
- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Each task must declare purpose, dependencies, likely file touchpoints, validation commands, and acceptance criteria.

## T1: Implement {slug}

### Purpose
{objective.get('description', 'Implement the objective')}

### Depends On
None

### Parallelizable
no

### Files / Areas Likely Touched
- implementation-specific files

### Validation Commands
- Run targeted validation commands for the touched area.

### Acceptance Criteria
- [ ] The main user-visible or system-visible behavior exists.
- [ ] Tests or validation commands demonstrate the behavior.
"""
    (package_dir / "tasks.md").write_text(tasks_content)

    # todo.md
    todo_content = f"""# Todo — {slug}

## Status
- **Total:** 1 task(s)
- **Pending:** 1
- **In Progress:** 0
- **Completed:** 0

## Tasks

| ID | Description | Status |
|----|-------------|--------|
| T1 | Implement {slug} | pending |

## Dependencies
- None
"""
    (package_dir / "todo.md").write_text(todo_content)

    print("STATUS: extracted")
    print(f"- Package: {package_dir.relative_to(ROOT)}")
    return 0


def main() -> int:
    """Main entry point."""
    args = parse_args()

    if not args.all and not args.slug:
        print(
            "ERROR: Use --all to extract all objectives or --slug to extract a specific one"
        )
        return 1

    try:
        objectives = load_roadmap()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return 1

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.slug:
        for obj in objectives:
            if obj.get("slug") == args.slug:
                return extract_objective(obj, output_dir)
        print(f"ERROR: Objective '{args.slug}' not found in roadmap")
        return 1

    if args.all:
        for obj in objectives:
            extract_objective(obj, output_dir)
        print(f"\nSTATUS: extracted {len(objectives)} objective(s)")
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
