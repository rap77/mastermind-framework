#!/usr/bin/env python3
"""
Migrate todo.md from v1 (header-based) to v2 (list-based) format.

V1 Format:
## Phase
### A1: Task Name
- [ ] Subtask

V2 Format:
## Phase
- [ ] A1: Task Name
  - [ ] Subtask

Usage:
    python3 .claude/commands/mm/migrate-todo-format.py [--dry-run] [--backup]

Options:
    --dry-run    Show changes without writing
    --backup     Create backup before migrating
"""

import re
import sys
from pathlib import Path
from datetime import datetime


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
TODO_MD = PROJECT_ROOT / "tasks" / "todo.md"


def mm_info(msg: str) -> None:
    print(f"INFO: {msg}", flush=True)


def mm_error(msg: str) -> None:
    print(f"ERROR: {msg}", flush=True, file=sys.stderr)


def mm_warn(msg: str) -> None:
    print(f"WARN: {msg}", flush=True)


def create_backup(path: Path) -> Path:
    """Create backup with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = path.parent / f"{path.name}.backup_{timestamp}"
    backup_path.write_text(path.read_text())
    mm_info(f"Backup created: {backup_path}")
    return backup_path


def parse_v1_format(content: str) -> list[dict]:
    """
    Parse v1 format into structured data.

    Returns:
        List of phases with their tasks and subtasks.
    """
    lines = content.split("\n")
    phases = []
    current_phase = None
    current_task = None

    for line in lines:
        # Phase header (##)
        phase_match = re.match(r"^##\s+(.+?)(?:\s*\((COMPLETE|✅)\))?\s*$", line)
        if phase_match:
            if current_task and current_phase:
                current_phase["tasks"].append(current_task)
                current_task = None
            if current_phase:
                phases.append(current_phase)
            current_phase = {
                "title": phase_match.group(1),
                "status": phase_match.group(2) if phase_match.group(2) else None,
                "tasks": [],
            }
            current_task = None
            continue

        # Task header (### or ####)
        task_match = re.match(
            r"^#{3,4}\s+([A-Z0-9.]+):\s*(.*?)(?:\s*\((\d+)\s*hours?\))?\s*$", line
        )
        if task_match and current_phase:
            if current_task:
                current_phase["tasks"].append(current_task)
            task_id = task_match.group(1)
            current_task = {
                "id": task_id,
                "title": task_match.group(2).strip(),
                "hours": task_match.group(3) if task_match.group(3) else None,
                "subtasks": [],
            }
            continue

        # Subtask checkbox
        checkbox_match = re.match(r"^-\s\[([ x])\]\s*(.+)", line)
        if checkbox_match and current_task:
            current_task["subtasks"].append(
                {
                    "state": checkbox_match.group(1),
                    "text": checkbox_match.group(2).strip(),
                }
            )
            continue

    # Don't forget the last one
    if current_phase:
        phases.append(current_phase)

    return phases


def detect_sequential_dependencies(subtasks: list[dict]) -> list[tuple[int, str]]:
    """
    Detect sequential dependencies by analyzing subtask text.

    Returns:
        List of (index, dependency_id) tuples.
    """
    dependencies = []

    for i, subtask in enumerate(subtasks):
        text = subtask["text"].lower()

        # Look for patterns like "Implement X after Y", "Add Z based on Y"
        if " after " in text or " following " in text or " based on " in text:
            # Assume dependency on previous subtask
            if i > 0:
                prev_id = f"{i:02d}"
                dependencies.append((i, prev_id))

    return dependencies


def convert_to_v2(phases: list[dict]) -> str:
    """
    Convert parsed v1 data to v2 format.

    Returns:
        v2 formatted markdown string.
    """
    output = []

    for phase in phases:
        # Phase header
        status_marker = f" ({phase['status']})" if phase["status"] else ""
        output.append(f"## {phase['title']}{status_marker}")
        output.append("")  # Blank line after phase header

        # Tasks
        for task in phase["tasks"]:
            task_id = task["id"]
            task_title = task["title"]
            hours = f" ({task['hours']} hours)" if task["hours"] else ""

            # Check if all subtasks are completed to determine task state
            if task["subtasks"]:
                all_completed = all(s["state"] == "x" for s in task["subtasks"])
                any_in_progress = any(s["state"] == "~" for s in task["subtasks"])
                if all_completed:
                    task_state = "x"
                elif any_in_progress:
                    task_state = "~"
                else:
                    task_state = " "
            else:
                task_state = " "

            output.append(f"- [{task_state}] {task_id}: {task_title}{hours}")

            # Subtasks with indentation
            for idx, subtask in enumerate(task["subtasks"]):
                subtask_id = f"{task_id}.{idx+1:02d}"
                state = subtask["state"]
                text = subtask["text"]

                # Detect dependencies
                deps = detect_sequential_dependencies(task["subtasks"])
                dep_list = [d[1] for d in deps if d[0] == idx]
                requires = f" [requires: {', '.join(dep_list)}]" if dep_list else ""

                output.append(f"  - [{state}] {subtask_id}: {text}{requires}")

            output.append("")  # Blank line after task

    return "\n".join(output)


def validate_v2_output(content: str) -> list[str]:
    """
    Validate v2 format output.

    Returns:
        List of validation errors (empty if valid).
    """
    errors = []

    # Check for proper indentation
    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("- ["):
            indent = len(line) - len(line.lstrip())
            if indent % 2 != 0:
                errors.append(
                    f"Line {i}: Indentation not multiple of 2: {indent} spaces"
                )

    # Check for proper state values
    state_pattern = re.compile(r"-\s\[([^x~ ])\]")
    for match in state_pattern.finditer(content):
        errors.append(f"Invalid state: [{match.group(1)}] - must be [x], [~], or [ ]")

    return errors


def migrate_todo_md(dry_run: bool = False, backup: bool = False) -> int:
    """
    Migrate todo.md from v1 to v2 format.

    Returns:
        0 on success, 1 on error.
    """
    if not TODO_MD.exists():
        mm_error(f"File not found: {TODO_MD}")
        return 1

    mm_info(f"Reading: {TODO_MD}")
    content = TODO_MD.read_text()

    # Parse v1 format
    mm_info("Parsing v1 format...")
    phases = parse_v1_format(content)

    if not phases:
        mm_error("No phases found in todo.md")
        return 1

    mm_info(f"Found {len(phases)} phases")
    for phase in phases:
        mm_info(f"  - {phase['title']}: {len(phase['tasks'])} tasks")

    # Convert to v2
    mm_info("Converting to v2 format...")
    v2_content = convert_to_v2(phases)

    # Validate
    mm_info("Validating v2 output...")
    errors = validate_v2_output(v2_content)
    if errors:
        mm_error("Validation errors found:")
        for error in errors:
            mm_error(f"  - {error}")
        return 1

    # Show diff
    mm_info("=" * 60)
    mm_info("PREVIEW (first 50 lines):")
    mm_info("=" * 60)
    for line in v2_content.split("\n")[:50]:
        print(line)
    if len(v2_content.split("\n")) > 50:
        print(f"... ({len(v2_content.split('\n')) - 50} more lines)")
    mm_info("=" * 60)

    if dry_run:
        mm_info("DRY RUN - No changes written")
        return 0

    # Create backup
    if backup:
        create_backup(TODO_MD)

    # Write migrated content
    mm_info(f"Writing: {TODO_MD}")
    TODO_MD.write_text(v2_content)

    mm_info("✅ Migration complete!")
    return 0


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help"]:
        print(__doc__)
        return 0

    dry_run = "--dry-run" in sys.argv
    backup = "--backup" in sys.argv

    return migrate_todo_md(dry_run=dry_run, backup=backup)


if __name__ == "__main__":
    sys.exit(main())
