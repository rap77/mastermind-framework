#!/usr/bin/env python3
"""Handler para /mm:complete-task.

Lanza task-executor agent para ejecutar subtareas pendientes.

REFACTOR v2:
- Sin temp files - estado en task-progress.json
- Output estructurado machine-parseable
- Detección git mejorada con git log --grep
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
# NOTE: This CLI tool uses print() instead of logger for structured output.
# The handler must emit machine-parseable messages (LAUNCH:, PAYLOAD:, STATUS:)
# that the calling command can parse. Logger output doesn't guarantee this format.
logging.basicConfig(
    level=logging.INFO,
    format="[mm] %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def _find_project_root() -> Path:
    """Find project root via git, fallback to file-relative path."""
    try:
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
    # Fallback: this file lives at <root>/.claude/commands/mm/
    return Path(__file__).resolve().parent.parent.parent.parent


def _read_stack_from_config(project_root: Path) -> list[str]:
    """Read stack list from .mastermind/config.yaml (no external deps)."""
    config_path = project_root / ".mastermind" / "config.yaml"
    if not config_path.exists():
        return []
    in_stack = False
    stack: list[str] = []
    for line in config_path.read_text().splitlines():
        stripped = line.strip()
        if stripped == "stack:":
            in_stack = True
            continue
        if in_stack:
            if stripped.startswith("- "):
                stack.append(stripped[2:].strip())
            elif stripped and not line[0].isspace():
                break
    return stack


def _read_project_id_from_config(project_root: Path) -> str | None:
    """Read project_id from .mastermind/config.yaml (written by /mm:init after DB registration)."""
    config_path = project_root / ".mastermind" / "config.yaml"
    if not config_path.exists():
        return None
    for line in config_path.read_text().splitlines():
        if line.strip().startswith("project_id:"):
            value = line.split(":", 1)[1].strip().strip('"').strip("'")
            return value if value else None
    return None


PROJECT_ROOT = _find_project_root()
TASKS_DIR = PROJECT_ROOT / "tasks"
PLANNING_DIR = PROJECT_ROOT / ".planning"
RUNTIME_STATE_PATH = PLANNING_DIR / "task-progress.json"
PLAN_MD = TASKS_DIR / "plan.md"
TODO_MD = TASKS_DIR / "todo.md"


# ============================================================================
# Output Helpers - Structured, machine-parseable
# ============================================================================


def mm_info(msg: str) -> None:
    """Print INFO message."""
    print(f"INFO: {msg}", flush=True)


def mm_task(task_id: str, title: str) -> None:
    """Print task header."""
    print(f"TASK: {task_id}", flush=True)
    print(f"TITLE: {title}", flush=True)


def mm_subtask(subtask_id: str, status: str, description: str = "") -> None:
    """Print subtask line."""
    desc = f" ({description})" if description else ""
    print(f"SUBTASK: {subtask_id} {status}{desc}", flush=True)


def mm_git(count: int, total: int, completed: list[str]) -> None:
    """Print git status."""
    completed_str = ",".join(completed) if completed else "none"
    print(f"GIT: {count}/{total} subtasks have commits [{completed_str}]", flush=True)


def mm_pending(count: int) -> None:
    """Print pending count."""
    print(f"PENDING: {count} subtasks to execute", flush=True)


def mm_launch(task_id: str) -> None:
    """Print launch command (no DB session — legacy path)."""
    payload = get_task_payload(task_id)
    print("LAUNCH: task-executor", flush=True)
    print(f"PAYLOAD: {json.dumps(payload)}", flush=True)


def _open_db_session(task_id: str, pending_count: int) -> str | None:
    """Open a dev session in the DB. Returns session UUID or None if DB unavailable."""
    try:
        sys.path.insert(0, str(PLANNING_DIR.parent / ".claude" / "commands" / "mm"))
        from db_client import MasterMindDB  # noqa: PLC0415

        project_id = _read_project_id_from_config(PROJECT_ROOT)
        with MasterMindDB() as db:
            if not db.available:
                return None
            return db.save_session(
                started_by="complete-task-handler",
                phase_number=None,
                project_id=project_id,
            )
    except Exception:
        return None


def _mm_launch_with_db(task_id: str, db_session_id: str | None) -> None:
    """Print launch command including db_session_id in payload."""
    payload = get_task_payload(task_id)
    if db_session_id:
        payload["db_session_id"] = db_session_id
    print("LAUNCH: task-executor", flush=True)
    print(f"PAYLOAD: {json.dumps(payload)}", flush=True)


def mm_status(msg: str) -> None:
    """Print status message."""
    print(f"STATUS: {msg}", flush=True)


def mm_error(msg: str) -> None:
    """Print error message."""
    print(f"ERROR: {msg}", flush=True, file=sys.stderr)


# ============================================================================
# Git Detection - Improved with git log --grep
# ============================================================================


def get_git_commits_for_task(task_id: str) -> set[str]:
    """Get subtask IDs that have commits in git using --grep.

    Uses git log --grep for more reliable detection.
    Pattern: matches "D1.1", "D1.2", etc. in commit messages.
    """
    completed = set()

    # Pattern 1: grep for task ID in commit messages
    # Matches: "D1.1:", "(D1.1)", "[D1.1]", etc.
    patterns = [
        rf"{re.escape(task_id)}\.(\d+)",
    ]

    for pattern in patterns:
        result = subprocess.run(
            ["git", "log", "--all", "--pretty=format:%s", "-100"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

        for line in result.stdout.split("\n"):
            match = re.search(pattern, line)
            if match:
                subtask_num = match.group(1)
                completed.add(f"{task_id}.{subtask_num}")

    return completed


# ============================================================================
# Task Parsing
# ============================================================================


def read_task_from_plan(task_id: str) -> dict[str, str]:
    """Read task details from plan.md.

    Args:
        task_id: Task identifier (e.g., "D1").

    Returns:
        Dictionary with "id" and "title" keys.

    Raises:
        ValueError: If task_id not found in plan.md.
        FileNotFoundError: If plan.md doesn't exist.
        OSError: If file cannot be read.
    """
    try:
        content = PLAN_MD.read_text()
    except FileNotFoundError:
        raise FileNotFoundError(f"plan.md not found at {PLAN_MD}")
    except OSError as e:
        raise OSError(f"Failed to read plan.md: {e}")

    pattern = rf"### {task_id}:([^\n]+)\n(.*?)(?=\n### |\Z)"
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        raise ValueError(f"Task {task_id} not found in plan.md")

    title = match.group(1).strip()
    return {"id": task_id, "title": title}


def read_subtasks_from_todo(task_id: str) -> list[dict[str, Any]]:
    """Read subtasks from todo.md.

    Args:
        task_id: Task identifier (e.g., "D1").

    Returns:
        List of subtask dictionaries with "id", "description", "completed" keys.

    Raises:
        ValueError: If task_id not found in todo.md.
        FileNotFoundError: If todo.md doesn't exist.
        OSError: If file cannot be read.
    """
    try:
        content = TODO_MD.read_text()
    except FileNotFoundError:
        raise FileNotFoundError(f"todo.md not found at {TODO_MD}")
    except OSError as e:
        raise OSError(f"Failed to read todo.md: {e}")

    pattern = rf"### {task_id}:([^\n]+)\n(.*?)(?=\n### |\n---|\Z)"
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        raise ValueError(f"Task {task_id} not found in todo.md")

    section = match.group(2)
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


# ============================================================================
# State Management
# ============================================================================


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
        "phase": 19,  # Current MM-Flow phase
        "subtasks": {
            st["id"]: {
                "description": st["description"],
                "status": "completed" if st["completed"] else "pending",
                "retries": 0,
            }
            for st in subtasks
        },
        "last_checkpoint": None,
        "context_budget_exit": None,
    }

    PLANNING_DIR.mkdir(parents=True, exist_ok=True)
    try:
        RUNTIME_STATE_PATH.write_text(json.dumps(runtime_state, indent=2))
    except OSError as e:
        mm_error(f"Failed to write runtime state: {e}")
        raise

    return runtime_state


def update_subtask_status(
    subtask_id: str,
    status: str,
    error: str | None = None,
    commit_sha: str | None = None,
) -> None:
    """Update a single subtask status in task-progress.json.

    Args:
        subtask_id: Subtask ID (e.g., "D1.1").
        status: New status (pending, in_progress, completed, failed, skipped).
        error: Optional error message if failed.
        commit_sha: Optional git commit SHA if committed.
    """
    if not RUNTIME_STATE_PATH.exists():
        return

    state = json.loads(RUNTIME_STATE_PATH.read_text())

    if subtask_id in state["subtasks"]:
        state["subtasks"][subtask_id]["status"] = status
        state["subtasks"][subtask_id]["updated_at"] = datetime.now().isoformat()

        if error:
            state["subtasks"][subtask_id]["error"] = error

        if commit_sha:
            state["subtasks"][subtask_id]["commit_sha"] = commit_sha

        state["last_checkpoint"] = subtask_id

        try:
            RUNTIME_STATE_PATH.write_text(json.dumps(state, indent=2))
        except OSError as e:
            mm_error(f"Failed to write runtime state: {e}")
            raise


def get_task_payload(task_id: str) -> dict[str, Any]:
    """Get the full task payload for the agent.

    Args:
        task_id: Task identifier.

    Returns:
        Dict ready to be passed to task-executor agent.

    Raises:
        ValueError: If task_id not found in plan.md or todo.md.
        FileNotFoundError: If required files don't exist.
        OSError: If files cannot be read.
    """
    try:
        task = read_task_from_plan(task_id)
        subtasks = read_subtasks_from_todo(task_id)
        git_completed = get_git_commits_for_task(task_id)

        # Filter to pending subtasks only
        pending_subtasks = [
            st
            for st in subtasks
            if st["id"] not in git_completed and not st["completed"]
        ]

        project_id = _read_project_id_from_config(PROJECT_ROOT)
        return {
            "task_id": task_id,
            "task_title": task["title"],
            "subtasks": pending_subtasks,
            "total_subtasks": len(subtasks),
            "pending_count": len(pending_subtasks),
            "context_budget_threshold": 0.75,  # Exit at 75% context
            "working_directory": str(PROJECT_ROOT),
            "stack": _read_stack_from_config(PROJECT_ROOT),
            "project_id": project_id,
        }
    except (ValueError, FileNotFoundError, OSError):
        # Re-raise expected exceptions with context
        raise
    except Exception as e:
        # Catch truly unexpected errors
        raise RuntimeError(f"Unexpected error building payload: {e}") from e


# ============================================================================
# Permission Detection
# ============================================================================


def detect_required_permissions(
    task_id: str, pending_subtasks: list[dict[str, Any]]
) -> list[str]:
    """Detect required tool permissions based on subtask descriptions.

    Args:
        task_id: Task identifier.
        pending_subtasks: List of pending subtask dictionaries.

    Returns:
        List of permission warnings to show before launching agent.
    """
    warnings: list[str] = []

    # Patterns that indicate Bash permission is needed
    bash_patterns = [
        r"\bborrar\b",
        r"\beliminar\b",
        r"\bdelete\b",
        r"\bremove\b",
        r"\bejecutar\b",
        r"\brun\b",
        r"\bnpm\b",
        r"\bpytest\b",
        r"\buv\s+run\b",
    ]

    # Patterns that indicate Write permission is needed
    write_patterns = [
        r"\bcrear\b",
        r"\bescribir\b",
        r"\bwrite\b",
        r"\bcrear\s+archivo\b",
        r"\bcreate\s+file\b",
        r"\badd\b.*\bfile\b",
    ]

    for st in pending_subtasks:
        desc_lower = st["description"].lower()

        # Check Bash patterns
        if any(
            re.search(pattern, desc_lower, re.IGNORECASE) for pattern in bash_patterns
        ):
            warnings.append(
                f"⚠️  Subtask {st['id']}: '{st['description']}' requires BASH permission"
            )

        # Check Write patterns
        if any(
            re.search(pattern, desc_lower, re.IGNORECASE) for pattern in write_patterns
        ):
            warnings.append(
                f"⚠️  Subtask {st['id']}: '{st['description']}' requires WRITE permission"
            )

    return warnings


# ============================================================================
# Main Logic
# ============================================================================


def start_task(task_id: str) -> None:
    """Start or resume a task.

    Args:
        task_id: Task identifier (e.g., "D1").
    """
    mm_info(f"Starting task {task_id}")

    # Read task and subtasks
    task = read_task_from_plan(task_id)
    subtasks = read_subtasks_from_todo(task_id)

    mm_task(task_id, task["title"])

    # Show all subtasks with status
    for st in subtasks:
        status = "[x]" if st["completed"] else "[ ]"
        mm_subtask(st["id"], status, st["description"])

    # Check git for existing commits
    git_completed = get_git_commits_for_task(task_id)
    expected_ids = {f"{task_id}.{i+1}" for i in range(len(subtasks))}

    mm_git(len(git_completed), len(subtasks), sorted(git_completed))

    # Check if task is complete
    if git_completed == expected_ids:
        mm_status("TASK COMPLETE - all subtasks have git commits")
        mark_all_complete(task_id, subtasks)
        return

    # Filter pending subtasks
    pending_subtasks = [
        st for st in subtasks if st["id"] not in git_completed and not st["completed"]
    ]

    if not pending_subtasks:
        mm_status("TASK COMPLETE - marking done")
        mark_all_complete(task_id, subtasks)
        return

    mm_pending(len(pending_subtasks))

    # Show pending subtasks
    for st in pending_subtasks:
        mm_subtask(st["id"], "pending", st["description"])

    # Detect required permissions BEFORE launching agent
    permission_warnings = detect_required_permissions(task_id, pending_subtasks)
    if permission_warnings:
        mm_info("PERMISSION CHECK:")
        for warning in permission_warnings:
            print(warning, flush=True)
        mm_info(
            "Please ensure Claude Code has these permissions enabled in settings.json"
        )

    # Initialize runtime state
    runtime_state = init_runtime_state(task_id, subtasks)
    mm_info(f"Runtime state: {RUNTIME_STATE_PATH}")
    mm_info(f"Session ID: {runtime_state['session_id']}")

    # Open dev session in DB (non-blocking — continues if DB unavailable)
    db_session_id = _open_db_session(task_id, len(pending_subtasks))
    if db_session_id:
        mm_info(f"DB session opened: {db_session_id}")

    # Launch task-executor
    _mm_launch_with_db(task_id, db_session_id)


def resume_task(task_id: str) -> None:
    """Resume a task from checkpoint.

    Args:
        task_id: Task identifier (e.g., "D1").
    """
    mm_info(f"Resuming task {task_id}")

    if not RUNTIME_STATE_PATH.exists():
        mm_error("No runtime state found. Run without --continue first.")
        mm_info(f"Starting fresh task {task_id}")
        start_task(task_id)
        return

    state = json.loads(RUNTIME_STATE_PATH.read_text())

    if state.get("task_id") != task_id:
        mm_error(f"Runtime state is for task {state.get('task_id')}, not {task_id}")
        return

    mm_info(f"Previous session: {state['session_id']}")
    mm_info(f"Last checkpoint: {state.get('last_checkpoint', 'none')}")

    # Show current status from runtime state
    completed = [
        sid for sid, info in state["subtasks"].items() if info["status"] == "completed"
    ]
    pending = [
        sid for sid, info in state["subtasks"].items() if info["status"] == "pending"
    ]

    mm_info(f"Completed: {len(completed)}/{len(state['subtasks'])}")
    if completed:
        mm_info(f"Completed subtasks: {sorted(completed)}")

    # Check if task is actually complete
    if not pending:
        mm_status("TASK COMPLETE - all subtasks completed in runtime state")
        return

    mm_pending(len(pending))
    if pending:
        mm_info(f"Pending subtasks: {sorted(pending)}")

    # Build pending subtasks list from runtime state
    pending_subtasks = []
    for sid in pending:
        st_info = state["subtasks"][sid]
        pending_subtasks.append(
            {
                "id": sid,
                "description": st_info["description"],
                "completed": False,
            }
        )

    # Detect permissions for pending subtasks
    permission_warnings = detect_required_permissions(task_id, pending_subtasks)
    if permission_warnings:
        mm_info("PERMISSION CHECK:")
        for warning in permission_warnings:
            print(warning, flush=True)
        mm_info(
            "Please ensure Claude Code has these permissions enabled in settings.json"
        )

    # Update runtime state with new session
    session_id = f"sess-resume-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    state["session_id"] = session_id
    state["resumed_at"] = datetime.now().isoformat()
    try:
        RUNTIME_STATE_PATH.write_text(json.dumps(state, indent=2))
    except OSError as e:
        mm_error(f"Failed to update runtime state: {e}")
        raise

    mm_info(f"Runtime state: {RUNTIME_STATE_PATH}")
    mm_info(f"Session ID: {session_id}")

    # Launch task-executor with pending subtasks
    payload = {
        "task_id": task_id,
        "task_title": read_task_from_plan(task_id)["title"],
        "subtasks": pending_subtasks,
        "total_subtasks": len(state["subtasks"]),
        "pending_count": len(pending_subtasks),
        "context_budget_threshold": 0.75,
        "resume": True,
        "resumed_from_checkpoint": state.get("last_checkpoint"),
    }
    print("LAUNCH: task-executor", flush=True)
    print(f"PAYLOAD: {json.dumps(payload)}", flush=True)
    mm_status("RESUMING FROM CHECKPOINT")


def mark_all_complete(task_id: str, subtasks: list[dict[str, Any]]) -> None:
    """Mark all subtasks as complete in todo.md and commit.

    Note: This does NOT verify acceptance criteria in plan.md.
    Use /mm:verify-criteria to manually verify what was implemented.

    Args:
        task_id: Task identifier.
        subtasks: List of subtask dicts.
    """
    # Mark in todo.md
    todo_content = TODO_MD.read_text()

    def replace_todo_checkboxes(match: re.Match[str]) -> str:
        section = match.group(0)
        return re.sub(r"- \[ \]", "- [x]", section)

    pattern = rf"(### {task_id}:.*?)(?=\n###|\n---|\Z)"
    todo_content = re.sub(
        pattern, replace_todo_checkboxes, todo_content, flags=re.DOTALL
    )

    TODO_MD.write_text(todo_content)

    # Commit todo.md only
    task = read_task_from_plan(task_id)
    task_letter = task_id[0]
    commit_msg = f"feat(phase-{task_letter}): {task['title']}"

    subprocess.run(
        ["git", "add", "tasks/todo.md"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    result = subprocess.run(
        ["git", "commit", "-m", commit_msg],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        mm_info(f"Committed: {commit_msg}")
        mm_info("NOTE: Use /mm:verify-criteria to mark acceptance criteria in plan.md")
    else:
        mm_info("No changes to commit")


def show_status() -> None:
    """Show status of all tasks."""
    mm_info("Task Status Overview")

    # Read all tasks
    content = PLAN_MD.read_text()

    for match in re.finditer(r"### ([A-Z]\d):([^\n]+)\n", content):
        task_id = match.group(1)
        title = match.group(2).strip()

        try:
            subtasks = read_subtasks_from_todo(task_id)
            completed = sum(1 for st in subtasks if st["completed"])
            total = len(subtasks)

            status = "✅" if completed == total else f"{completed}/{total}"
            print(f"  {task_id} {status}: {title}", flush=True)
        except ValueError:
            print(f"  {task_id}: (no subtasks found)", flush=True)


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: mm-complete-task <TASK_ID> [--continue] [--status]", flush=True)
        print("       mm-complete-task --status  # Show all tasks", flush=True)
        sys.exit(1)

    # Status mode
    if sys.argv[1] == "--status":
        show_status()
        return

    task_id = sys.argv[1].upper()
    resume_mode = "--continue" in sys.argv

    if resume_mode:
        resume_task(task_id)
    else:
        start_task(task_id)


if __name__ == "__main__":
    main()
