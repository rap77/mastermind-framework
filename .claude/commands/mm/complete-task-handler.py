#!/usr/bin/env python3
"""Handler para /mm:complete-task.

Lanza agentes background para subtareas pendientes y monitorea progreso.
"""

import json
import logging
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[mm] %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path.home() / "proy/mastermind"
TASKS_DIR = PROJECT_ROOT / "tasks"
PLANNING_DIR = PROJECT_ROOT / ".planning"
RUNTIME_STATE_PATH = PLANNING_DIR / "task-progress.json"
PLAN_MD = TASKS_DIR / "plan.md"
TODO_MD = TASKS_DIR / "todo.md"


def read_task_from_plan(task_id: str) -> dict[str, str]:
    """Read task details from plan.md.

    Args:
        task_id: Task identifier (e.g., "C1").

    Returns:
        Dictionary with "id" and "title" keys.

    Raises:
        ValueError: If task_id not found in plan.md.
    """
    content = PLAN_MD.read_text()

    pattern = rf"### {task_id}:([^\n]+)\n(.*?)(?=\n### |\Z)"
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        raise ValueError(f"Task {task_id} not found in plan.md")

    title = match.group(1).strip()

    return {"id": task_id, "title": title}


def read_subtasks_from_todo(task_id: str) -> list[dict[str, Any]]:
    """Read subtasks from todo.md.

    Args:
        task_id: Task identifier (e.g., "C1").

    Returns:
        List of subtask dictionaries with "id", "description", "completed" keys.

    Raises:
        ValueError: If task_id not found in todo.md.
    """
    content = TODO_MD.read_text()

    pattern = rf"### {task_id}:([^\n]+)\n(.*?)(?=\n### |\n---|\Z)"
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        raise ValueError(f"Task {task_id} not found in todo.md")

    section = match.group(2)

    # Extract subtasks with nested checkboxes
    lines = section.split("\n")
    subtasks: list[dict[str, Any]] = []
    task_prefix = f"{task_id}."
    current_num = 1

    for line in lines:
        if line.strip().startswith("- ["):
            match = re.match(r"- \[([ x])\] (.+)", line)
            if match:
                status, text = match.groups()
                subtasks.append(
                    {
                        "id": f"{task_prefix}{current_num}",
                        "description": text.strip(),
                        "completed": status == "x",
                    }
                )
                current_num += 1

    return subtasks


def init_runtime_state(task_id: str, subtasks: list[dict[str, Any]]) -> dict[str, Any]:
    """Initialize runtime state file.

    Args:
        task_id: Task identifier.
        subtasks: List of subtask dictionaries.

    Returns:
        Runtime state dictionary with session info and subtask statuses.
    """
    session_id = f"sess-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    runtime_state: dict[str, Any] = {
        "task_id": task_id,
        "session_id": session_id,
        "started_at": datetime.now().isoformat(),
        "subtasks": {
            st["id"]: {
                "description": st["description"],
                "status": "pending" if not st["completed"] else "completed",
            }
            for st in subtasks
        },
        "last_checkpoint": None,
    }

    PLANNING_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME_STATE_PATH.write_text(json.dumps(runtime_state, indent=2))

    return runtime_state


def mark_task_complete(task_id: str, title: str) -> str:
    """Mark task as complete in plan.md and todo.md.

    Args:
        task_id: Task identifier.
        title: Task title for commit message.

    Returns:
        Commit message that was created.
    """
    # Update todo.md subtasks
    todo_content = TODO_MD.read_text()

    def replace_todo_checkboxes(match: re.Match[str]) -> str:
        section = match.group(0)
        return re.sub(r"- \[ \]", "- [x]", section)

    pattern = rf"(### {task_id}:.*?)(?=\n###|\n---|\Z)"
    todo_content = re.sub(
        pattern, replace_todo_checkboxes, todo_content, flags=re.DOTALL
    )

    TODO_MD.write_text(todo_content)

    # Commit
    task_letter = task_id[0]
    commit_msg = f"feat(phase-{task_letter}): {title}"

    subprocess.run(
        ["git", "add", "tasks/todo.md"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", commit_msg],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
    )

    return commit_msg


def launch_background_agent(
    task_id: str, task: dict[str, str], subtasks: list[dict]
) -> str:
    """Launch task-executor agent in background.

    Args:
        task_id: Task identifier.
        task: Task dict with 'id' and 'title'.
        subtasks: List of subtask dicts.

    Returns:
        Process ID or agent identifier.
    """
    # Filter pending subtasks
    pending = [st for st in subtasks if not st["completed"]]

    if not pending:
        logger.info(f"✓ All subtasks already complete for {task_id}")
        return mark_task_complete(task_id, task["title"])

    # Prepare payload for agent
    payload = {
        "task_id": task_id,
        "task_title": task["title"],
        "subtasks": pending,
        "plan_context": PLAN_MD.read_text(),
    }

    # Create temp file with payload
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(payload, f, indent=2)
        payload_path = f.name

    # Create marker file for tracking
    agent_marker = PLANNING_DIR / f".agent-{task_id}-running"
    agent_marker.write_text(
        json.dumps(
            {
                "launched_at": datetime.now().isoformat(),
                "task_id": task_id,
                "payload_path": payload_path,
            }
        )
    )

    # Print payload path for the .md command to read
    # This is the CRITICAL line that makes the command work
    logger.info("")
    logger.info("=== PAYLOAD READY ===")
    logger.info(f"Payload path: {payload_path}")
    logger.info("Read this file and pass its content to Agent() tool")
    logger.info("===================")

    return f"agent-{task_id}"


def main() -> None:
    """Main entry point for mm-complete-task command."""
    if len(sys.argv) < 2:
        logger.error("Uso: mm-complete-task <TASK_ID> [--continue]")
        logger.error("Ejemplo: mm-complete-task C1")
        logger.error("Ejemplo: mm-complete-task C1 --continue")
        sys.exit(1)

    task_id = sys.argv[1].upper()
    resume_mode = "--continue" in sys.argv

    logger.info(f"Task {task_id}: Leyendo plan.md...")
    task = read_task_from_plan(task_id)
    logger.info(f"  {task['title']}")

    logger.info("Leyendo todo.md...")
    subtasks = read_subtasks_from_todo(task_id)
    logger.info(f"  Found {len(subtasks)} subtasks")

    # Count completed
    completed_count = sum(1 for st in subtasks if st["completed"])
    if completed_count == len(subtasks):
        logger.info(f"✓ Task {task_id} already complete!")
        # Still commit to mark it
        commit_msg = mark_task_complete(task_id, task["title"])
        logger.info(f"Commit: {commit_msg}")
        return

    if resume_mode and RUNTIME_STATE_PATH.exists():
        logger.info("Resuming from previous session...")
        logger.info(f"  Completed: {completed_count}/{len(subtasks)} subtasks")
        # Load existing state to preserve session_id
        existing_state = json.loads(RUNTIME_STATE_PATH.read_text())
        logger.info(f"  Previous session: {existing_state['session_id']}")
    else:
        logger.info("Creating runtime state...")
        runtime_state = init_runtime_state(task_id, subtasks)
        logger.info(f"  Session ID: {runtime_state['session_id']}")
        logger.info(f"  Runtime state: {RUNTIME_STATE_PATH}")

    # Launch background agent
    agent_id = launch_background_agent(task_id, task, subtasks)

    logger.info("✓ Agent launched in background")
    logger.info(f"  Agent ID: {agent_id}")
    logger.info(f"  Monitor progress: tail -f {RUNTIME_STATE_PATH}")
    logger.info(f"  View logs: .planning/.agent-{task_id}-running")
    logger.info("")
    logger.info("The agent will execute the full cycle for each subtask:")
    logger.info("  1. /build    → implement")
    logger.info("  2. /test     → verify tests")
    logger.info("  3. /review   → code review (superpowers)")
    logger.info("  4. code-reviewer → 5-axis review (agent-skills)")
    logger.info("  5. Mark complete in todo.md")
    logger.info("  6. Save checkpoint to Engram")
    logger.info("  7. Git commit after each subtask")


if __name__ == "__main__":
    main()
