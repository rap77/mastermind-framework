#!/usr/bin/env python3
"""Validate the minimum planning contract produced by /mm:discover.

This script checks that discovery left behind the required artifacts and the
minimum structural sections needed for another model to resume safely.
"""

from __future__ import annotations

import logging
import re
from argparse import ArgumentParser, Namespace
from pathlib import Path

from planning_paths import get_planning_dir, planning_relpath

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path.cwd()

PLANNING_BASE = get_planning_dir(PROJECT_ROOT)
PLANNING_LABEL = planning_relpath(PROJECT_ROOT)
HANDOFF_PATH = PLANNING_BASE / "HANDOFF-CURRENT.md"
CHANGES_DIR = PLANNING_BASE / "changes"
ARCHIVE_DIR = PLANNING_BASE / "archive"


def read_text(path: Path) -> str:
    """Return file contents or an empty string when the file is missing."""
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def parse_args() -> Namespace:
    """Parse validator arguments."""
    parser = ArgumentParser(
        description="Validate the planning contract produced by /mm:discover."
    )
    parser.add_argument(
        "--objective",
        default=None,
        help=f"Validate a per-objective package in {PLANNING_LABEL}/changes/<objective>/ instead of the legacy global contract.",
    )
    return parser.parse_args()


def infer_active_objective() -> str | None:
    """Infer the active objective from handoff or from a single changes directory."""
    handoff_text = read_text(HANDOFF_PATH)
    match = re.search(r"`([^`]+)`", handoff_text)
    if match:
        return match.group(1).strip()

    changes_dir = PLANNING_BASE / "changes"
    if not changes_dir.exists():
        return None
    directories = sorted(path.name for path in changes_dir.iterdir() if path.is_dir())
    if len(directories) == 1:
        return directories[0]
    return None


def validate_handoff(text: str) -> list[str]:
    """Validate minimum required sections in the active planning handoff."""
    issues: list[str] = []
    if not text:
        return ["HANDOFF-CURRENT.md missing"]

    section_checks = {
        "current objective": ["current objective", "goal"],
        "decisions": ["decisions already made", "decisions"],
        "blockers": ["blockers", "risks"],
        "next task": ["exact next recommended task", "next step", "next task"],
        "validation": ["validation commands", "how to validate"],
    }

    lowered = text.lower()
    for label, alternatives in section_checks.items():
        if not any(option in lowered for option in alternatives):
            issues.append(f"handoff missing section: {label}")

    return issues


def validate_requirements(text: str, objective: str) -> list[str]:
    """Validate minimum required sections in requirements.md."""
    issues: list[str] = []
    if not text:
        return [f"{PLANNING_LABEL}/changes/{objective}/requirements.md missing"]

    section_checks = {
        "problem/purpose": ["## problem / purpose", "# requirements"],
        "scope": ["## scope"],
        "out of scope": ["## out of scope"],
        "non-negotiables": ["## non-negotiables"],
        "acceptance criteria": ["acceptance criteria"],
    }
    lowered = text.lower()
    for label, alternatives in section_checks.items():
        if not any(option in lowered for option in alternatives):
            issues.append(f"requirements.md missing section: {label}")
    return issues


def validate_design(text: str, objective: str) -> list[str]:
    """Validate minimum required sections in design.md."""
    issues: list[str] = []
    if not text:
        return [f"{PLANNING_LABEL}/changes/{objective}/design.md missing"]

    section_checks = {
        "architecture / boundaries": ["## architecture / boundaries"],
        "technical approach": ["## technical approach"],
        "dependencies": ["## dependencies"],
        "validation strategy": ["validation strategy"],
    }
    lowered = text.lower()
    for label, alternatives in section_checks.items():
        if not any(option in lowered for option in alternatives):
            issues.append(f"design.md missing section: {label}")
    return issues


def validate_objective_tasks(text: str, objective: str) -> list[str]:
    """Validate minimum required structure in objective tasks.md."""
    issues: list[str] = []
    if not text:
        return [f"{PLANNING_LABEL}/changes/{objective}/tasks.md missing"]

    if not re.findall(r"^##\s+[A-Z]{1,4}\d+:", text, re.MULTILINE):
        issues.append("tasks.md missing concrete task headings")
    required_sections = [
        "### Purpose",
        "### Depends On",
        "### Parallelizable",
        "### Files / Areas Likely Touched",
        "### Validation Commands",
        "### Acceptance Criteria",
    ]
    for section in required_sections:
        if section not in text:
            issues.append(f"tasks.md missing section: {section}")
    if "- [ ]" not in text and "- [x]" not in text:
        issues.append("tasks.md missing acceptance checkboxes")
    return issues


def find_next_task(todo_text: str) -> str | None:
    """Return the ID of the first incomplete top-level task in todo.md."""
    for line in todo_text.splitlines():
        match = re.match(r"^- \[[ ~]\] ([A-Z]{1,4}\d+):", line)
        if match:
            return match.group(1)
    return None


def validate_objective_contract(objective: str) -> list[str]:
    """Validate the per-objective planning package."""
    base_dir = CHANGES_DIR / objective
    issues: list[str] = []
    issues.extend(
        validate_requirements(read_text(base_dir / "requirements.md"), objective)
    )
    issues.extend(validate_design(read_text(base_dir / "design.md"), objective))
    issues.extend(validate_objective_tasks(read_text(base_dir / "tasks.md"), objective))
    issues.extend(validate_handoff(read_text(base_dir / "HANDOFF-CURRENT.md")))
    todo_text = read_text(base_dir / "todo.md")
    if not todo_text:
        issues.append(f"{PLANNING_LABEL}/changes/{objective}/todo.md missing")
    else:
        if (
            "- [ ]" not in todo_text
            and "- [~]" not in todo_text
            and "- [x]" not in todo_text
        ):
            issues.append("todo.md missing task checkboxes")
        if objective not in todo_text and "Execution Checklist" not in todo_text:
            issues.append("todo.md missing execution sections")
        if "depends_on:" not in todo_text:
            issues.append("todo.md missing dependency hints")
        if "validation:" not in todo_text:
            issues.append("todo.md missing validation hints")
    return issues


def main() -> int:
    """Run the planning contract validation and print a structured result."""
    args = parse_args()
    objective = args.objective or infer_active_objective()
    if not objective:
        logger.error("STATUS: FAILED")
        logger.error(
            "- Could not infer an active objective. Pass --objective <name> or refresh %s/HANDOFF-CURRENT.md.",
            PLANNING_LABEL,
        )
        return 1

    issues: list[str] = validate_objective_contract(objective)

    if issues:
        logger.error("STATUS: FAILED")
        for issue in issues:
            logger.error("- %s", issue)
        return 1

    base_dir = CHANGES_DIR / objective
    next_task = find_next_task(read_text(base_dir / "todo.md"))

    logger.info("STATUS: PASSED")
    logger.info(
        "- Objective planning contract is structurally complete for %s", objective
    )
    if next_task:
        logger.info("- Next: /mm:complete-task %s", next_task)
    else:
        logger.info("- All tasks complete — run /mm:archive-objective to close")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
