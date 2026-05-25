#!/usr/bin/env python3
"""Archive a completed objective package from .planning/changes to archive/objectives."""

from __future__ import annotations

import json
import shutil
import subprocess
from argparse import ArgumentParser, Namespace
from datetime import datetime
from pathlib import Path


def project_root() -> Path:
    """Find project root via git, fallback to file-relative path."""
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
PLANNING_DIR = ROOT / ".planning"
CHANGES_DIR = PLANNING_DIR / "changes"
ARCHIVE_OBJECTIVES_DIR = PLANNING_DIR / "archive" / "objectives"
GLOBAL_HANDOFF = PLANNING_DIR / "HANDOFF-CURRENT.md"


def parse_args() -> Namespace:
    """Parse CLI args."""
    parser = ArgumentParser(description="Archive a completed objective package.")
    parser.add_argument(
        "--objective",
        default=None,
        help="Objective slug under .planning/changes/<objective>.",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Only print the archive decision/result without moving files.",
    )
    return parser.parse_args()


def infer_objective() -> str | None:
    """Infer objective from global handoff or single changes dir."""
    if GLOBAL_HANDOFF.exists():
        text = GLOBAL_HANDOFF.read_text(encoding="utf-8")
        import re

        match = re.search(r"`([^`]+)`", text)
        if match:
            candidate = match.group(1).strip()
            if (CHANGES_DIR / candidate).exists():
                return candidate

    if CHANGES_DIR.exists():
        dirs = [path.name for path in CHANGES_DIR.iterdir() if path.is_dir()]
        if len(dirs) == 1:
            return dirs[0]
    return None


def load_execution_state(objective_dir: Path) -> dict | None:
    """Load objective execution-state.json if present."""
    path = objective_dir / "execution-state.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def is_completed(objective_dir: Path) -> tuple[bool, str]:
    """Return completion status and reason."""
    state = load_execution_state(objective_dir)
    if state and state.get("tasks"):
        statuses = [task.get("status", "pending") for task in state["tasks"].values()]
        if statuses and all(status == "completed" for status in statuses):
            return True, "execution-state.json shows all root tasks completed"
        return False, "execution-state.json still has pending/in-progress root tasks"

    handoff_path = objective_dir / "HANDOFF-CURRENT.md"
    if handoff_path.exists():
        text = handoff_path.read_text(encoding="utf-8")
        if (
            "**COMPLETE**" in text
            or "objective package has no pending root tasks" in text
        ):
            return True, "handoff indicates objective complete"
    return False, "objective completion could not be proven"


def write_completion_summary(
    objective_dir: Path, archive_dir: Path, reason: str
) -> None:
    """Write completion summary into the archived objective package."""
    handoff_path = archive_dir / "HANDOFF-CURRENT.md"
    summary_path = archive_dir / "COMPLETION-SUMMARY.md"
    handoff_excerpt = ""
    if handoff_path.exists():
        handoff_excerpt = handoff_path.read_text(encoding="utf-8").strip()
    summary = "\n".join(
        [
            f"# Completion Summary — {archive_dir.name}",
            "",
            f"- Archived at: {datetime.now().isoformat(timespec='seconds')}",
            f"- Completion basis: {reason}",
            f"- Source moved from: {objective_dir}",
            "",
            "## Handoff Snapshot",
            handoff_excerpt or "- No handoff snapshot available.",
            "",
        ]
    )
    summary_path.write_text(summary, encoding="utf-8")


def main() -> int:
    """Archive a completed objective package."""
    args = parse_args()
    objective = args.objective or infer_objective()
    if not objective:
        print("STATUS: FAILED")
        print("- Could not infer objective. Pass --objective <slug>.")
        return 1

    objective_dir = CHANGES_DIR / objective
    if not objective_dir.exists():
        print("STATUS: FAILED")
        print(f"- Active objective package missing: {objective_dir}")
        return 1

    completed, reason = is_completed(objective_dir)
    if not completed:
        print("STATUS: FAILED")
        print(f"- Objective `{objective}` is not archive-safe: {reason}")
        return 1

    archive_dir = ARCHIVE_OBJECTIVES_DIR / objective
    if archive_dir.exists():
        print("STATUS: FAILED")
        print(f"- Archive destination already exists: {archive_dir}")
        return 1

    print("STATUS: PASSED")
    print(f"- Objective `{objective}` is archive-safe: {reason}")
    if args.summary_only:
        return 0

    ARCHIVE_OBJECTIVES_DIR.mkdir(parents=True, exist_ok=True)
    shutil.move(str(objective_dir), str(archive_dir))
    write_completion_summary(objective_dir, archive_dir, reason)
    print(f"- Archived to: {archive_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
