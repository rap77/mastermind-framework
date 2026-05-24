#!/usr/bin/env python3
"""Update todo.md with actual execution times from task-progress.json.

Usage:
    python3 update-todo-times.py [task_id]

If task_id is provided, only updates that task. Otherwise, updates all tasks.

FIXED v2:
- Supports BOTH format styles:
  - New: "- [ ] A1: Task Title"
  - Old: "### A1: Task Title"
- Correctly matches task IDs and updates time tracking
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


def find_project_root() -> Path:
    """Find project root via git, fallback to current working directory."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=Path.cwd(),
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except Exception:
        pass
    return Path.cwd()


PROJECT_ROOT = find_project_root()
PLANNING_DIR = PROJECT_ROOT / ".planning"
RUNTIME_STATE_PATH = PLANNING_DIR / "task-progress.json"


def get_active_paths() -> tuple[Path | None, Path | None]:
    """Return the active plan/todo paths from runtime state."""
    if not RUNTIME_STATE_PATH.exists():
        return None, None
    try:
        state = json.loads(RUNTIME_STATE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None, None

    plan_path = state.get("plan_path")
    todo_path = state.get("todo_path")
    if not plan_path or not todo_path:
        return None, None
    return Path(plan_path), Path(todo_path)


def extract_estimate_from_plan(task_id: str) -> str:
    """Extract time estimate from plan.md for a task.

    Looks for patterns like "(6 hours)", "(2 days)", etc.
    Returns the estimate string or "N/A" if not found.
    """
    plan_path, _ = get_active_paths()
    if not plan_path or not plan_path.exists():
        return "N/A"

    content = plan_path.read_text(encoding="utf-8")

    # Match task heading and extract estimate from title or first line
    pattern = r"#{2,6}\s+" + re.escape(task_id) + r":([^\n]+)"
    match = re.search(pattern, content)

    if match:
        title = match.group(1)
        # Look for estimate patterns: (X hours), (X days), (X hrs)
        estimate_match = re.search(
            r"\((\d+(?:\.\d+)?)\s+(hour|hr|day|week|min|second)s?\)",
            title,
            re.IGNORECASE,
        )
        if estimate_match:
            return estimate_match.group(0)

    return "N/A"


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def calculate_deviation(estimate_str: str, actual_seconds: float) -> str:
    """Calculate deviation between estimate and actual.

    Returns a string like "+0.5h" or "-15m".
    """
    if estimate_str == "N/A":
        return "N/A"

    # Parse estimate
    match = re.match(
        r"\((\d+(?:\.\d+)?)\s+(hour|hr|day|week|min|second)s?\)",
        estimate_str,
        re.IGNORECASE,
    )
    if not match:
        return "N/A"

    estimate_value = float(match.group(1))
    estimate_unit = match.group(2).lower()

    # Convert estimate to seconds
    unit_multipliers = {
        "second": 1,
        "min": 60,
        "hour": 3600,
        "hr": 3600,
        "day": 86400,
        "week": 604800,
    }

    estimate_seconds = estimate_value * unit_multipliers.get(estimate_unit, 1)

    # Calculate deviation
    deviation_seconds = actual_seconds - estimate_seconds

    if abs(deviation_seconds) < 60:
        return f"{deviation_seconds:+.0f}s"
    elif abs(deviation_seconds) < 3600:
        return f"{deviation_seconds / 60:+.1f}m"
    else:
        return f"{deviation_seconds / 3600:+.1f}h"


def find_task_section_new_format(
    task_id: str, todo_content: str
) -> tuple[int | None, int | None, str | None, str | None]:
    """Find task section using new format: "- [ ] A1: Task Title".

    Returns:
        Tuple of (start, end, heading, section) or (None, None, None, None) if not found.
    """
    lines = todo_content.splitlines(keepends=True)
    offset = 0
    start_offset: int | None = None
    end_offset: int | None = None
    heading: str | None = None

    heading_pattern = re.compile(rf"^\- \[[ x~]\]\s+{re.escape(task_id)}:(.+)$")
    next_task_pattern = re.compile(r"^\- \[[ x~]\]\s+[A-Z]{1,4}\d+:")

    for index, line in enumerate(lines):
        if start_offset is None and heading_pattern.match(line.rstrip("\n")):
            start_offset = offset
            heading = line.rstrip("\n")
            end_offset = start_offset + len(line)

            for next_line in lines[index + 1 :]:
                if next_task_pattern.match(
                    next_line.rstrip("\n")
                ) or next_line.startswith("##"):
                    break
                end_offset += len(next_line)
            break
        offset += len(line)

    if start_offset is None or end_offset is None or heading is None:
        return None, None, None, None

    section = todo_content[start_offset + len(heading) : end_offset]
    return start_offset, end_offset, heading, section


def find_task_section_old_format(
    task_id: str, todo_content: str
) -> tuple[int | None, int | None, str | None, str | None]:
    """Find task section using old format: "### A1: Task Title".

    Returns:
        Tuple of (start, end, heading, section) or (None, None, None, None) if not found.
    """
    pattern = rf"(^(### {re.escape(task_id)}:.+?$)(.*?)(?=^###|^---|^##|\Z))"
    match = re.search(pattern, todo_content, re.MULTILINE | re.DOTALL)

    if match:
        heading = match.group(2)
        section = match.group(3)
        return match.start(2), match.end(3), heading, section

    return None, None, None, None


def update_task_section(
    task_id: str, todo_content: str, progress_data: dict[str, Any]
) -> str:
    """Update a single task section in todo.md with time tracking.

    Args:
        task_id: Task identifier (e.g., "B2").
        todo_content: Full todo.md content.
        progress_data: Runtime state from task-progress.json.

    Returns:
        Updated todo.md content.
    """
    # Try new format first, then old format
    start, end, heading, section = find_task_section_new_format(task_id, todo_content)

    if start is None:
        start, end, heading, section = find_task_section_old_format(
            task_id, todo_content
        )

    if start is None:
        # Task not found - return unchanged
        return todo_content

    # Get estimate from plan.md
    estimate = extract_estimate_from_plan(task_id)

    # Calculate totals from progress data
    subtasks = progress_data.get("subtasks", {})
    total_duration = 0
    completed_count = 0
    total_count = 0

    for subtask_id, subtask_data in subtasks.items():
        if subtask_id.startswith(task_id):
            total_count += 1
            if subtask_data.get("duration_seconds"):
                total_duration += subtask_data["duration_seconds"]
            if subtask_data.get("status") == "completed":
                completed_count += 1

    # Calculate additional metrics
    avg_duration = total_duration / completed_count if completed_count > 0 else 0
    completion_rate = (completed_count / total_count * 100) if total_count > 0 else 0

    # Estimate remaining time (linear projection)
    if completed_count > 0 and completed_count < total_count:
        remaining_subtasks = total_count - completed_count
        estimated_remaining = avg_duration * remaining_subtasks
        estimated_total = total_duration + estimated_remaining
        eta = format_duration(estimated_total)
    else:
        eta = format_duration(total_duration) if total_duration > 0 else "in progress"

    # Format strings
    actual_time = (
        format_duration(total_duration) if total_duration > 0 else "in progress"
    )
    deviation = (
        calculate_deviation(estimate, total_duration) if total_duration > 0 else "—"
    )
    avg_time = format_duration(avg_duration) if avg_duration > 0 else "—"

    # Build time tracking line with enhanced metrics
    time_line = f"⏱️ **Estimate**: {estimate} | **Actual**: {actual_time} | **Deviation**: {deviation} | **Progress**: {completed_count}/{total_count} ({completion_rate:.0f}%)\n"
    time_line += f"📊 **Avg/subtask**: {avg_time} | **ETA**: {eta}\n"

    # Check if time line already exists
    if "⏱️ **Estimate**:" in section:
        # Update existing time line
        # Need to replace both lines
        section = re.sub(
            r"⏱️ \*\*Estimate\*\*:.*\n📊 \*\*Avg/subtask\*\*:.*\n", time_line, section
        )
    else:
        # Insert time line after heading (before subtasks)
        section = "\n" + time_line + "\n" + section.lstrip("\n")

    # Update individual subtasks with their times
    for subtask_id, subtask_data in subtasks.items():
        if subtask_id.startswith(task_id) and "." in subtask_id:
            # Find subtask line (format: "- [x] A1.01: description")
            subtask_pattern = rf"(^(\- \[[ x~]\]\s+{re.escape(subtask_id)}:.+?$))"
            subtask_match = re.search(subtask_pattern, section, re.MULTILINE)

            if subtask_match:
                subtask_line = subtask_match.group(1)

                # Get subtask duration
                duration = subtask_data.get("duration_seconds", 0)
                if duration > 0:
                    duration_str = format_duration(duration)
                    time_badge = f" ⏱️ {duration_str}"

                    # Add or update time badge at end of line
                    if "⏱️" in subtask_line:
                        subtask_line = re.sub(r" ⏱️ [^\n]*", time_badge, subtask_line)
                    else:
                        subtask_line = subtask_line.rstrip("\n") + time_badge + "\n"

                    section = section.replace(subtask_match.group(1), subtask_line)

    # Replace the section
    updated_section = heading + section
    return todo_content[:start] + updated_section + todo_content[end:]


def update_task_in_todo(task_id: str) -> bool:
    """Update a single task in todo.md with time tracking.

    This function is designed to be imported and called from other modules
    (like complete-task-handler.py) for incremental time tracking updates.

    Args:
        task_id: Task identifier (e.g., "B2" or "B2.6").

    Returns:
        True if update succeeded, False otherwise.

    Raises:
        FileNotFoundError: If required files don't exist.
        OSError: If files cannot be read or written.
    """
    if not RUNTIME_STATE_PATH.exists():
        return False

    _, todo_path = get_active_paths()
    if not todo_path or not todo_path.exists():
        return False

    try:
        progress_data = json.loads(RUNTIME_STATE_PATH.read_text())
        todo_content = todo_path.read_text(encoding="utf-8")

        updated_content = update_task_section(task_id, todo_content, progress_data)

        if updated_content != todo_content:
            todo_path.write_text(updated_content, encoding="utf-8")
            return True
        return False

    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return False


def main():
    """Main entry point."""
    if not RUNTIME_STATE_PATH.exists():
        print("No task-progress.json found. Run /mm:complete-task first.")
        sys.exit(1)

    progress_data = json.loads(RUNTIME_STATE_PATH.read_text())
    task_id = sys.argv[1].upper() if len(sys.argv) > 1 else progress_data.get("task_id")

    if not task_id:
        print("No task ID found in progress data and none provided.")
        sys.exit(1)

    _, todo_path = get_active_paths()
    if not todo_path or not todo_path.exists():
        print("todo.md not found for the active objective/task runtime state")
        sys.exit(1)

    todo_content = todo_path.read_text(encoding="utf-8")

    # Update the task section
    updated_content = update_task_section(task_id, todo_content, progress_data)

    # Write back
    todo_path.write_text(updated_content, encoding="utf-8")
    print(f"✅ Updated time tracking for task {task_id} in todo.md")

    # Check if task is complete and notify
    subtasks = progress_data.get("subtasks", {})
    total_count = len(subtasks)
    completed_count = sum(
        1 for st in subtasks.values() if st.get("status") == "completed"
    )

    if completed_count == total_count and total_count > 0:
        # Calculate total time
        total_duration = sum(st.get("duration_seconds", 0) for st in subtasks.values())

        print(f"\n🎉 Task {task_id} COMPLETE!")
        print(f"⏱️ Total time: {format_duration(total_duration)}")
        print(
            f"📊 Average per subtask: {format_duration(total_duration / total_count)}"
        )

        # Play notification sound
        notify_script = Path(__file__).parent / "notify-complete.py"
        try:
            import subprocess

            subprocess.run(
                ["python3", str(notify_script), task_id, "complete"],
                capture_output=True,
                text=True,
            )
        except Exception as e:
            print(f"⚠️ Could not play notification: {e}")


if __name__ == "__main__":
    main()
