#!/usr/bin/env python3
"""Update time tracking in todo.md from task-progress.json runtime state."""

from __future__ import annotations

import json
import re
import sys
from datetime import timedelta
from pathlib import Path


def _find_project_root() -> Path:
    """Find project root via git, fallback to file-relative path."""
    try:
        import subprocess

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


def _format_duration(seconds: float) -> str:
    """Format seconds as human-readable duration."""
    if seconds <= 0:
        return "—"
    td = timedelta(seconds=seconds)
    total_minutes = td.total_seconds() / 60
    if total_minutes < 1:
        return f"{td.total_seconds():.0f}s"
    if total_minutes < 60:
        return f"{total_minutes:.1f}m"
    hours = total_minutes / 60
    return f"{hours:.1f}h" if hours < 10 else f"{hours:.0f}h"


def _calculate_stats(subtasks: dict) -> tuple[int, int, float, float]:
    """Calculate progress stats from subtasks."""
    total = len(subtasks)
    completed = 0
    total_duration = 0.0
    for _sid, data in subtasks.items():
        if data.get("status") == "completed":
            completed += 1
            total_duration += data.get("duration_seconds", 0) or 0
    avg = total_duration / completed if completed > 0 else 0.0
    return completed, total, total_duration, avg


def _build_time_tracking_line(
    completed: int,
    total: int,
    total_duration: float,
    avg_per_subtask: float,
    in_progress: bool,
) -> tuple[str, str]:
    """Build the two time tracking lines."""
    progress = (
        f"{completed}/{total} ({int(completed / total * 100) if total > 0 else 0}%)"
    )
    if in_progress:
        actual_str, eta_str, deviation_str = "in progress", "in progress", "—"
    else:
        actual_str = _format_duration(total_duration)
        deviation = (
            (total_duration - avg_per_subtask * total) if avg_per_subtask > 0 else 0
        )
        deviation_str = (
            "—"
            if abs(deviation) < 1
            else (
                f"+{_format_duration(deviation)}"
                if deviation > 0
                else f"-{_format_duration(abs(deviation))}"
            )
        )
        remaining = total - completed
        eta = avg_per_subtask * remaining if avg_per_subtask > 0 else 0
        eta_str = _format_duration(eta) if remaining > 0 else "done"
    return (
        f"⏱️ **Estimate**: N/A | **Actual**: {actual_str} | **Deviation**: {deviation_str} | **Progress**: {progress}",
        f"📊 **Avg/subtask**: {_format_duration(avg_per_subtask)} | **ETA**: {eta_str}",
    )


def _update_todo_time_tracking(
    todo_path: Path, task_id: str, runtime_state: dict
) -> bool:
    """Update time tracking for a specific task in todo.md."""
    if not todo_path.exists():
        return False
    content = todo_path.read_text(encoding="utf-8")
    task_pattern = re.compile(
        rf"(?P<block>^-\s*\[[ x~]\]\s*{re.escape(task_id)}:.*?)(?=^\-\s*\[[ x~]\]\s*[A-Z]{{1,4}}\d+:|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = task_pattern.search(content)
    if not match:
        return False

    task_block = match.group("block")
    subtasks = runtime_state.get("subtasks", {})
    task_prefix = task_id + "."
    task_subtasks = {
        sid: data for sid, data in subtasks.items() if sid.startswith(task_prefix)
    }

    if not task_subtasks:
        subtask_lines = re.findall(
            r"^\s*-\s*\[[ x~]\]\s*\w+\.\d+:", task_block, re.MULTILINE
        )
        total = len(subtask_lines)
        completed = len(re.findall(r"-\s*\[x\]", task_block))
        in_progress = (
            any(s.get("status") == "in_progress" for s in subtasks.values())
            if subtasks
            else "~" in task_block
        )
        total_duration = sum(
            s.get("duration_seconds", 0) or 0
            for s in subtasks.values()
            if s.get("status") == "completed"
        )
        avg_per_subtask = total_duration / completed if completed > 0 else 0.0
    else:
        completed, total, total_duration, avg_per_subtask = _calculate_stats(
            task_subtasks
        )
        in_progress = any(
            s.get("status") == "in_progress" for s in task_subtasks.values()
        )

    line1, line2 = _build_time_tracking_line(
        completed,
        total if task_subtasks else len(task_subtasks) or 1,
        total_duration,
        avg_per_subtask,
        in_progress,
    )

    # Remove any previously appended metric lines inside this root-task block, then reinsert
    # a single normalized pair right after the root task line.
    without_metrics = re.sub(
        r"^\s*[⏱️📊].*\n?",
        "",
        task_block,
        flags=re.MULTILINE,
    ).rstrip()
    lines = without_metrics.splitlines()
    if not lines:
        return False
    new_block = "\n".join([lines[0], line1, line2, *lines[1:]]).rstrip() + "\n"

    todo_path.write_text(
        content[: match.start("block")] + new_block + content[match.end("block") :],
        encoding="utf-8",
    )
    return True


def _find_runtime_state(cwd: Path) -> tuple[dict | None, Path | None, Path | None]:
    """Find and read task-progress.json from cwd upward.

    Returns:
        (runtime_state, runtime_path, resolved_todo_path) or (None, None, None)
    """
    project_root = _find_project_root()
    project_root_resolved = project_root.resolve()

    # Phase 1: Search cwd tree for .planning/task-progress.json
    check_dir = cwd
    for _ in range(10):
        candidate = check_dir / ".planning" / "task-progress.json"
        if candidate.exists():
            try:
                state = json.loads(candidate.read_text(encoding="utf-8"))
                todo_path_str = state.get("todo_path", "")
                if todo_path_str:
                    todo_path = Path(todo_path_str)
                    if todo_path.is_absolute():
                        if todo_path.exists():
                            return state, candidate, todo_path
                    else:
                        resolved = check_dir / todo_path
                        if resolved.exists():
                            return state, candidate, resolved
            except (json.JSONDecodeError, OSError):
                pass
        check_dir = check_dir.parent

    # Phase 2: Fallback to project root's .mm-flow/planning/task-progress.json
    try:
        cwd.resolve().relative_to(project_root_resolved)
        in_project = True
    except ValueError:
        in_project = False

    if in_project:
        fallback = project_root / ".mm-flow" / "planning" / "task-progress.json"
        if fallback.exists():
            try:
                state = json.loads(fallback.read_text(encoding="utf-8"))
                todo_path_str = state.get("todo_path", "")
                if todo_path_str:
                    todo_path = Path(todo_path_str)
                    if todo_path.exists():
                        return state, fallback, todo_path
            except (json.JSONDecodeError, OSError):
                pass

    return None, None, None


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: update-todo-times.py <task_id>", file=sys.stderr)
        return 1

    task_id = sys.argv[1]
    cwd = Path.cwd()

    runtime_state, _runtime_path, todo_path = _find_runtime_state(cwd)
    if runtime_state is None or todo_path is None:
        print("No runtime state found", file=sys.stderr)
        return 1

    try:
        updated = _update_todo_time_tracking(todo_path, task_id, runtime_state)
        print(
            f"Updated time tracking for {task_id}"
            if updated
            else f"No changes needed for {task_id}"
        )
        return 0
    except Exception as e:
        print(f"Failed to update time tracking: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
