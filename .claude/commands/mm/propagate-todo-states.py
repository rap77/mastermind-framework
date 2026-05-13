#!/usr/bin/env python3
"""
State propagation for todo.md v2 format.

Propagates child task states up to parent tasks according to the v2 spec:
- All children [x] → parent [x]
- Any child [~] or [x] (not all [x]) → parent [~]
- All children [ ] → parent [ ]

Usage:
    python3 .claude/commands/mm/propagate-todo-states.py [--dry-run]
"""

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
TODO_MD = PROJECT_ROOT / "tasks" / "todo.md"


def mm_info(msg: str) -> None:
    print(f"INFO: {msg}", flush=True)


def mm_error(msg: str) -> None:
    print(f"ERROR: {msg}", flush=True, file=sys.stderr)


def calculate_parent_state_from_file(
    todo_path: Path, parent_id: str
) -> dict[str, Any] | None:
    """Calculate state for a parent task by reading its children from file."""
    content = todo_path.read_text()
    children_states: list[str] = []

    # Find direct children (e.g., B1.1, B1.2 are children of B1, not B1.1.01)
    # Pattern matches: - [x] B1.1:, - [~] B1.2.01:, - [x] B3.2.01:, etc.
    # We need to match the parent_id followed by a dot and ANY alphanumeric sequence (but NOT more dots after that)
    # The negative lookahead (?!\.) ensures we don't match grandchildren
    # For example, for B3.2: matches B3.2.01 but NOT B3.2.01.01
    # NOTE: Children have indentation, so we allow optional whitespace at start with ^\s*
    pattern = re.compile(
        rf"^\s*-\s\[([ x~])\]\s{re.escape(parent_id)}\.[A-Z0-9]+(?!\.):", re.MULTILINE
    )

    for match in pattern.finditer(content):
        children_states.append(f"[{match.group(1)}]")

    # Calculate parent state
    # IMPORTANT: If no children found, this is likely a leaf task (no subtasks)
    # Return None to signal "no change needed" for leaf tasks
    if not children_states:
        return None  # Leaf task - don't update

    completed = sum(1 for s in children_states if s == "[x]")

    if all(s == "[x]" for s in children_states):
        return {
            "state": "[x]",
            "children_count": len(children_states),
            "completed": completed,
        }
    elif any(s in ["[~]", "[x]"] for s in children_states):
        return {
            "state": "[~]",
            "children_count": len(children_states),
            "completed": completed,
        }
    else:
        return {"state": "[ ]", "children_count": len(children_states), "completed": 0}


def update_parent_state(content: str, parent_id: str, new_state: str) -> str:
    """Update parent task state in content."""
    # NOTE: Allow optional whitespace at start for indented parents
    pattern = re.compile(
        rf"^(\s*-\s\[)[ x~](\]\s{re.escape(parent_id)}:)", re.MULTILINE
    )

    def replace_func(match: re.Match[str]) -> str:
        return f"{match.group(1)}{new_state[1]}{match.group(2)}"

    return pattern.sub(replace_func, content)


def get_all_parents_by_level(content: str) -> dict[int, list[tuple[str, str]]]:
    """
    Group all parent tasks by their nesting level.

    Returns:
        {
            1: [("B3", "[~]"), ("B2", "[x]"), ...],           # Top-level
            2: [("B3.1", "[x]"), ("B3.2", "[~]"), ...],      # Second-level
            3: [("B3.2.01", "[x]"), ("B3.2.02", "[x]"), ...] # Third-level
        }
    """
    # Find ALL parent tasks (any task with dot notation ending with :)
    # NOTE: Allow optional whitespace at start for indented tasks
    parent_pattern = re.compile(
        r"^\s*-\s\[([ x~])\]\s([A-Z0-9]+(?:\.[A-Z0-9]+)+):", re.MULTILINE
    )

    parents_by_level: dict[int, list[tuple[str, str]]] = {}

    for state, task_id in parent_pattern.findall(content):
        # Count the dots to determine level
        # B1 = 0 dots = level 1
        # B1.1 = 1 dot = level 2
        # B1.1.01 = 2 dots = level 3
        dot_count = task_id.count(".")
        level = dot_count + 1

        if level not in parents_by_level:
            parents_by_level[level] = []

        parents_by_level[level].append((task_id, f"[{state}]"))

    return parents_by_level


def main(dry_run: bool = False) -> int:
    """Main execution with multi-level parent support."""
    if not TODO_MD.exists():
        mm_error(f"todo.md not found at {TODO_MD}")
        return 1

    content = TODO_MD.read_text()

    # Get all parents grouped by level
    parents_by_level = get_all_parents_by_level(content)

    if not parents_by_level:
        mm_info("No parent tasks found")
        return 0

    # Show what we found
    total_parents = sum(len(parents) for parents in parents_by_level.values())
    max_level = max(parents_by_level.keys())
    mm_info(f"Found {total_parents} parent tasks across {max_level} levels")
    for level in sorted(parents_by_level.keys()):
        mm_info(f"  Level {level}: {len(parents_by_level[level])} parents")

    # Process BOTTOM-UP (highest level first)
    # This ensures parents calculate state from already-updated children
    updates: list[dict[str, Any]] = []

    for level in sorted(parents_by_level.keys(), reverse=True):
        mm_info(f"\nProcessing Level {level}:")

        level_updates = []

        for parent_id, current_state in parents_by_level[level]:
            info = calculate_parent_state_from_file(TODO_MD, parent_id)

            # Skip leaf tasks (no children found)
            if info is None:
                continue

            if current_state != info["state"]:
                update = {
                    "id": parent_id,
                    "old": current_state,
                    "new": info["state"],
                    "children": info["children_count"],
                    "completed": info["completed"],
                    "level": level,
                }
                level_updates.append(update)
                updates.append(update)

                # Show what we're updating
                if info["state"] == "[x]":
                    mm_info(f"  {parent_id}: All children complete → {info['state']}")
                elif info["state"] == "[~]":
                    mm_info(
                        f"  {parent_id}: {info['completed']}/{info['children']} subtasks complete → {info['state']}"
                    )
                else:
                    mm_info(f"  {parent_id}: No children started → {info['state']}")

        if level_updates:
            mm_info(f"  Level {level}: {len(level_updates)} updates needed")
        else:
            mm_info(f"  Level {level}: all parents correct")

    mm_info(f"\nTotal updates needed: {len(updates)}")

    if updates:
        if dry_run:
            mm_info("Dry run - no changes made")
            return 0

        # Create backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = TODO_MD.parent / f"{TODO_MD.name}.backup_propagation_{timestamp}"
        backup_path.write_text(content)
        mm_info(f"Backup created: {backup_path.name}")

        # Apply updates (already in correct bottom-up order)
        new_content = content
        for update in updates:
            new_content = update_parent_state(
                new_content, str(update["id"]), str(update["new"])
            )

        # Write updated content
        TODO_MD.write_text(new_content)
        mm_info("Updated todo.md with propagated states (multi-level)")
    else:
        mm_info("All parent states are correct at all levels")

    return 0


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    sys.exit(main(dry_run))
