#!/usr/bin/env python3
"""Block commits when active objective-task progress has not been checkpointed.

This guard exists because objective execution progress must be recorded through
the handler (`--mark-in-progress` / `--mark-done`) and projected into
`execution-state.json`, `todo.md`, and `HANDOFF-CURRENT.md`.

If code is staged while an active task still has no durable progress advancement
in the staged objective artifacts, the commit is rejected. This prevents the
"code committed, task ledger still pending" failure mode.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def find_project_root() -> Path:
    """Find repo root from current execution context."""
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0 and result.stdout.strip():
        return Path(result.stdout.strip())
    return Path.cwd()


PROJECT_ROOT = find_project_root()
RUNTIME_STATE = PROJECT_ROOT / ".planning" / "task-progress.json"


def run_git(*args: str) -> subprocess.CompletedProcess[str]:
    """Run a git command in the repo root."""
    return subprocess.run(
        ["git", *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def load_json_path(path: Path) -> dict[str, Any] | None:
    """Load JSON from a filesystem path."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def load_json_from_git(rev_spec: str, repo_path: str) -> dict[str, Any] | None:
    """Load JSON from git object-ish:path syntax."""
    result = run_git("show", f"{rev_spec}:{repo_path}")
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def load_json_from_index(repo_path: str) -> dict[str, Any] | None:
    """Load staged JSON content from the git index."""
    result = run_git("show", f":{repo_path}")
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def staged_files() -> list[str]:
    """Return staged file paths."""
    result = run_git("diff", "--cached", "--name-only")
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def status_rank(status: str) -> int:
    """Rank statuses so advancement can be compared."""
    return {
        "pending": 0,
        "in_progress": 1,
        "completed": 2,
    }.get(status, -1)


def is_code_like_path(path: str) -> bool:
    """Return True for paths that represent code/docs changes outside planning."""
    if path.startswith(".planning/"):
        return False
    if path.startswith(".gitignore"):
        return False
    return True


def main() -> int:
    """Validate staged commit against active-task checkpoint rules."""
    runtime = load_json_path(RUNTIME_STATE)
    if not runtime:
        return 0

    active_task = runtime.get("task_id")
    objective_slug = runtime.get("objective_slug")
    if not active_task or not objective_slug:
        return 0

    runtime_subtasks = runtime.get("subtasks", {})
    if not runtime_subtasks:
        return 0

    # If runtime task is already fully complete, no barrier needed.
    if all(item.get("status") == "completed" for item in runtime_subtasks.values()):
        return 0

    files = staged_files()
    if not files:
        return 0

    # Only gate commits that stage actual code/content outside planning.
    if not any(is_code_like_path(path) for path in files):
        return 0

    objective_base = f".planning/changes/{objective_slug}"
    execution_state_path = f"{objective_base}/execution-state.json"
    todo_path = f"{objective_base}/todo.md"
    handoff_path = f"{objective_base}/HANDOFF-CURRENT.md"

    missing = [
        path
        for path in (execution_state_path, todo_path, handoff_path)
        if path not in files
    ]
    if missing:
        print(
            "ERROR: Active objective commit is missing required checkpoint artifacts."
        )
        print(f"  Active task: {active_task}")
        print("  Missing staged files:")
        for path in missing:
            print(f"    - {path}")
        print(
            "Use the handler checkpoint flow before committing: "
            "complete-task-handler.py --mark-in-progress/--mark-done"
        )
        return 1

    head_state = load_json_from_git("HEAD", execution_state_path) or {}
    staged_state = load_json_from_index(execution_state_path)
    if staged_state is None:
        print("ERROR: Could not read staged execution-state.json from index.")
        return 1

    head_task = head_state.get("tasks", {}).get(active_task, {})
    staged_task = staged_state.get("tasks", {}).get(active_task, {})
    staged_subtasks = staged_task.get("subtasks", {})
    if not staged_subtasks:
        print(
            "ERROR: Staged execution-state.json does not contain active task subtasks."
        )
        return 1

    advanced = False
    for subtask_id, staged_info in staged_subtasks.items():
        staged_status = str(staged_info.get("status", "pending"))
        head_status = str(
            head_task.get("subtasks", {}).get(subtask_id, {}).get("status", "pending")
        )
        if status_rank(staged_status) > status_rank(head_status):
            advanced = True
            break

    root_head = str(head_task.get("status", "pending"))
    root_staged = str(staged_task.get("status", "pending"))
    if status_rank(root_staged) > status_rank(root_head):
        advanced = True

    if not advanced:
        print(
            "ERROR: Commit contains code changes but no durable task progress advancement."
        )
        print(f"  Active task: {active_task}")
        print(f"  Objective: {objective_slug}")
        print(
            "  Staged execution-state.json did not advance any subtask/root-task status."
        )
        print(
            "Checkpoint the task first with the handler, then stage objective artifacts and commit."
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
