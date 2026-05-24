#!/usr/bin/env python3
"""Automatically update todo.md with time tracking after each checkpoint.

This script is called by task-executor after completing each subtask.
It reads task-progress.json and updates todo.md with actual times.
"""

import json
import subprocess
from pathlib import Path


def main():
    """Update time tracking for the current task."""
    planning_dir = Path(__file__).parent.parent.parent.parent / ".planning"
    progress_file = planning_dir / "task-progress.json"

    if not progress_file.exists():
        return  # No active task

    progress_data = json.loads(progress_file.read_text())
    task_id = progress_data.get("task_id")

    if not task_id:
        return  # No task ID in progress data

    # Call update-todo-times.py
    update_script = Path(__file__).parent / "update-todo-times.py"
    result = subprocess.run(
        ["python3", str(update_script), task_id], capture_output=True, text=True
    )

    if result.returncode == 0:
        print(f"[checkpoint-time-tracker] ✅ Updated time tracking for task {task_id}")
    else:
        print(
            f"[checkpoint-time-tracker] ⚠️ Failed to update time tracking: {result.stderr}"
        )


if __name__ == "__main__":
    main()
