#!/usr/bin/env python3
"""Helpers to resolve the active planning surface for MM harness commands."""

from __future__ import annotations

from pathlib import Path


def get_planning_dir(root_dir: Path) -> Path:
    """Return the preferred planning directory for the current repository.

    Preference order:
    1. ``.planning`` when it already contains active planning artifacts.
    2. ``.mm-flow/planning`` as the legacy fallback.
    3. ``.planning`` when it exists but is still sparse.
    4. ``.mm-flow/planning`` otherwise.
    """

    primary = root_dir / ".planning"
    legacy = root_dir / ".mm-flow" / "planning"
    candidates = (primary, legacy)

    for candidate in candidates:
        if (
            (candidate / "changes").exists()
            or (candidate / "roadmap").exists()
            or (candidate / "HANDOFF-CURRENT.md").exists()
        ):
            return candidate

    if primary.exists():
        return primary
    return legacy


def planning_relpath(root_dir: Path) -> str:
    """Return the preferred planning directory as a repo-relative string."""

    return str(get_planning_dir(root_dir).relative_to(root_dir))
