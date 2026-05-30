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
from dataclasses import dataclass
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
PLANNING_DIR = PROJECT_ROOT / ".mm-flow" / "planning"
RUNTIME_STATE_PATH = PLANNING_DIR / "task-progress.json"
NOTIFY_SCRIPT_PATH = PROJECT_ROOT / ".claude" / "commands" / "mm" / "notify-complete.py"
OBJECTIVE_STATE_FILENAME = "execution-state.json"


@dataclass
class TaskSource:
    """Source files used to execute a task."""

    mode: str
    plan_path: Path
    todo_path: Path
    objective_slug: str | None = None


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
    """Print launch command."""
    payload = get_task_payload(task_id)
    print("LAUNCH: task-executor", flush=True)
    print(f"PAYLOAD: {json.dumps(payload)}", flush=True)


def _open_db_session(_task_id: str, _pending_count: int) -> str | None:
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


def mm_model_brief(brief: str) -> None:
    """Print a model-resume brief."""
    print("MODEL_BRIEF_START", flush=True)
    print(brief.rstrip(), flush=True)
    print("MODEL_BRIEF_END", flush=True)


def task_heading_exists(plan_path: Path, task_id: str) -> bool:
    """Return True if the plan file contains a heading for the task."""
    if not plan_path.exists():
        return False
    content = plan_path.read_text(encoding="utf-8")
    task_id_esc = re.escape(task_id)
    return bool(
        re.search(
            rf"^#{{2,6}}\s+(?:PHASE\s+)?{task_id_esc}:",
            content,
            re.MULTILINE,
        )
    )


def ensure_objective_todo(objective_dir: Path, task_id: str) -> Path:
    """Ensure an objective-local todo.md exists for complete-task execution."""
    todo_path = objective_dir / "todo.md"
    tasks_path = objective_dir / "tasks.md"
    if todo_path.exists() or not tasks_path.exists():
        return todo_path

    tasks_text = tasks_path.read_text(encoding="utf-8")
    task_matches = re.findall(
        r"^##\s+([A-Z]{1,4}\d+):\s*(.+)$", tasks_text, re.MULTILINE
    )
    if not task_matches:
        return todo_path

    lines = [
        f"# Todo — {objective_dir.name}",
        "",
        "## Execution Checklist",
        "",
    ]
    for current_task_id, title in task_matches:
        lines.extend(
            [
                f"- [ ] {current_task_id}: {title.strip()}",
                f"  - [ ] {current_task_id}.1: Execute {current_task_id} end-to-end",
                "",
            ]
        )
    todo_path.write_text("\n".join(lines), encoding="utf-8")
    return todo_path


def resolve_task_source(task_id: str) -> TaskSource:
    """Resolve a task from an active objective package."""
    changes_dir = PROJECT_ROOT / ".mm-flow" / "planning" / "changes"
    if changes_dir.exists():
        for objective_dir in sorted(changes_dir.iterdir()):
            if not objective_dir.is_dir():
                continue
            plan_path = objective_dir / "tasks.md"
            if task_heading_exists(plan_path, task_id):
                todo_path = ensure_objective_todo(objective_dir, task_id)
                return TaskSource(
                    mode="objective",
                    plan_path=plan_path,
                    todo_path=todo_path,
                    objective_slug=objective_dir.name,
                )

    raise ValueError(
        f"Task {task_id} not found in objective packages under .mm-flow/planning/changes/"
    )


def get_active_paths(task_id: str | None = None) -> tuple[Path, Path]:
    """Return the active plan/todo paths for the objective flow."""
    if task_id:
        source = resolve_task_source(get_root_task_id(task_id))
        return source.plan_path, source.todo_path

    if RUNTIME_STATE_PATH.exists():
        try:
            state = json.loads(RUNTIME_STATE_PATH.read_text(encoding="utf-8"))
            plan_path = state.get("plan_path")
            todo_path = state.get("todo_path")
            if plan_path and todo_path:
                return Path(plan_path), Path(todo_path)
        except (json.JSONDecodeError, OSError):
            pass

    raise ValueError(
        "No active planning source available. Run /mm:discover --existing --objective <name> first."
    )


def load_runtime_state() -> dict[str, Any] | None:
    """Load runtime state if it exists."""
    if not RUNTIME_STATE_PATH.exists():
        return None
    try:
        return json.loads(RUNTIME_STATE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def runtime_task_complete(state: dict[str, Any]) -> bool:
    """Return True when all subtasks in runtime state are completed."""
    subtasks = state.get("subtasks", {})
    if not subtasks:
        return False
    return all(subtask.get("status") == "completed" for subtask in subtasks.values())


def get_objective_handoff_path(task_id: str | None = None) -> Path | None:
    """Return the active objective handoff path if available."""
    if task_id:
        try:
            source = resolve_task_source(get_root_task_id(task_id))
        except ValueError:
            return None
        if source.objective_slug:
            return (
                PROJECT_ROOT
                / ".mm-flow"
                / "planning"
                / "changes"
                / source.objective_slug
                / "HANDOFF-CURRENT.md"
            )

    if RUNTIME_STATE_PATH.exists():
        try:
            state = json.loads(RUNTIME_STATE_PATH.read_text(encoding="utf-8"))
            objective_slug = state.get("objective_slug")
            if objective_slug:
                path = (
                    PROJECT_ROOT
                    / ".mm-flow"
                    / "planning"
                    / "changes"
                    / objective_slug
                    / "HANDOFF-CURRENT.md"
                )
                return path
        except (json.JSONDecodeError, OSError):
            pass

    return None


def get_objective_state_path(
    objective_slug: str | None = None, task_id: str | None = None
) -> Path | None:
    """Return the durable execution-state path for an objective."""
    if objective_slug:
        return (
            PROJECT_ROOT
            / ".mm-flow"
            / "planning"
            / "changes"
            / objective_slug
            / OBJECTIVE_STATE_FILENAME
        )

    if task_id:
        try:
            source = resolve_task_source(get_root_task_id(task_id))
        except ValueError:
            return None
        return get_objective_state_path(objective_slug=source.objective_slug)

    state = load_runtime_state()
    active_slug = state.get("objective_slug") if state else None
    if active_slug:
        return get_objective_state_path(objective_slug=active_slug)

    return None


def load_objective_state(
    objective_slug: str | None = None, task_id: str | None = None
) -> dict[str, Any] | None:
    """Load durable objective execution state if available."""
    state_path = get_objective_state_path(
        objective_slug=objective_slug, task_id=task_id
    )
    if state_path is None:
        return None
    if not state_path.exists():
        if objective_slug is None and task_id is not None:
            try:
                source = resolve_task_source(task_id)
            except ValueError:
                return None
            if source.objective_slug:
                return bootstrap_objective_state_from_artifacts(
                    source.objective_slug, source.plan_path, source.todo_path
                )
        elif objective_slug is not None:
            objective_dir = (
                PROJECT_ROOT / ".mm-flow" / "planning" / "changes" / objective_slug
            )
            plan_path = objective_dir / "tasks.md"
            todo_path = ensure_objective_todo(objective_dir, objective_slug)
            if plan_path.exists() and todo_path.exists():
                return bootstrap_objective_state_from_artifacts(
                    objective_slug, plan_path, todo_path
                )
        return None
    try:
        return json.loads(state_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def save_objective_state(state: dict[str, Any]) -> None:
    """Persist objective execution state."""
    objective_slug = state.get("objective_slug")
    state_path = get_objective_state_path(objective_slug=objective_slug)
    if state_path is None:
        return
    try:
        state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except OSError as exc:
        mm_error(f"Failed to write objective execution state: {exc}")


def get_root_task_id(identifier: str) -> str:
    """Return the root task ID for a task or subtask identifier."""
    return identifier.split(".", 1)[0]


def seed_objective_task_state(
    source: TaskSource, task_id: str, subtasks: list[dict[str, Any]]
) -> None:
    """Ensure a durable execution-state entry exists for the active objective task."""
    if not source.objective_slug:
        return

    state = load_objective_state(objective_slug=source.objective_slug) or {
        "objective_slug": source.objective_slug,
        "plan_path": str(source.plan_path),
        "todo_path": str(source.todo_path),
        "tasks": {},
        "updated_at": None,
    }
    tasks = state.setdefault("tasks", {})
    task_entry = tasks.setdefault(
        task_id,
        {
            "status": "pending",
            "subtasks": {},
            "started_at": None,
            "completed_at": None,
        },
    )
    task_entry["plan_path"] = str(source.plan_path)
    task_entry["todo_path"] = str(source.todo_path)
    task_entry.setdefault("subtasks", {})

    for subtask in subtasks:
        existing = task_entry["subtasks"].get(subtask["id"], {})
        task_entry["subtasks"][subtask["id"]] = {
            "description": subtask["description"],
            "status": existing.get(
                "status", "completed" if subtask["completed"] else "pending"
            ),
            "started_at": existing.get("started_at"),
            "completed_at": existing.get("completed_at"),
            "duration_seconds": existing.get("duration_seconds", 0),
            "updated_at": existing.get("updated_at"),
        }

    state["updated_at"] = datetime.now().isoformat()
    save_objective_state(state)


def get_task_ids_from_plan(plan_path: Path) -> list[str]:
    """Return ordered root task IDs from an objective tasks.md file."""
    if not plan_path.exists():
        return []
    content = plan_path.read_text(encoding="utf-8")
    return re.findall(r"^##\s+([A-Z]{1,4}\d+):", content, re.MULTILINE)


def get_task_title_from_plan(plan_path: Path, task_id: str) -> str | None:
    """Return the root task title from tasks.md."""
    if not plan_path.exists():
        return None
    content = plan_path.read_text(encoding="utf-8")
    match = re.search(rf"^##\s+{re.escape(task_id)}:\s*(.+)$", content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None


def get_task_validation_commands_from_plan(plan_path: Path, task_id: str) -> list[str]:
    """Return validation commands for a root task from tasks.md."""
    if not plan_path.exists():
        return []
    content = plan_path.read_text(encoding="utf-8")
    pattern = (
        rf"^##\s+{re.escape(task_id)}:.*?"
        r"^### Validation Commands\n"
        r"(.*?)(?=^### |\n## |\Z)"
    )
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    if not match:
        return []
    return [
        line.strip()[2:].strip()
        for line in match.group(1).splitlines()
        if line.strip().startswith("- ")
    ]


def get_task_dependencies_from_plan(plan_path: Path, task_id: str) -> str:
    """Return a normalized dependency summary for a root task."""
    if not plan_path.exists():
        return "none"
    content = plan_path.read_text(encoding="utf-8")
    pattern = (
        rf"^##\s+{re.escape(task_id)}:.*?"
        r"^### Depends On\n"
        r"(.*?)(?=^### |\n## |\Z)"
    )
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    if not match:
        return "none"
    dependency_block = match.group(1).strip()
    first_line = (
        dependency_block.splitlines()[0].strip() if dependency_block else "none"
    )
    return first_line or "none"


def get_root_task_statuses(todo_path: Path) -> list[tuple[str, str, str]]:
    """Return ordered root task statuses from todo.md as (task_id, checkbox, title)."""
    if not todo_path.exists():
        return []
    content = todo_path.read_text(encoding="utf-8")
    pattern = re.compile(
        r"^-\s\[(?P<status>[ x~])\]\s+(?P<task_id>[A-Z]{1,4}\d+):\s*(?P<title>.+)$",
        re.MULTILINE,
    )
    return [
        (match.group("task_id"), match.group("status"), match.group("title").strip())
        for match in pattern.finditer(content)
    ]


def checkbox_for_status(status: str) -> str:
    """Map durable/runtme status names to todo checkbox characters."""
    if status == "completed":
        return "x"
    if status == "in_progress":
        return "~"
    return " "


def sync_objective_todo_from_state(task_id: str) -> None:
    """Project todo.md checkbox state from durable objective execution state.

    The objective execution ledger is the source of truth. This function rewrites
    parent and subtask checkboxes so manual edits in todo.md cannot get ahead of
    the durable state.
    """
    objective_state = load_objective_state(task_id=task_id)
    if not objective_state:
        return

    try:
        plan_path, todo_path = get_active_paths(task_id)
        todo_content = todo_path.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError, ValueError):
        return

    original_content = todo_content
    for root_id in get_task_ids_from_plan(plan_path):
        task_entry = objective_state.get("tasks", {}).get(root_id, {})
        todo_content = re.sub(
            rf"(^-\s\[[ x~]\]\s+){re.escape(root_id)}:",
            rf"\g<1>{root_id}:",
            todo_content,
            count=0,
            flags=re.MULTILINE,
        )

        parent_checkbox = checkbox_for_status(task_entry.get("status", "pending"))
        todo_content = re.sub(
            rf"(^-\s\[)([ x~])(\]\s+{re.escape(root_id)}:)",
            rf"\g<1>{parent_checkbox}\g<3>",
            todo_content,
            count=1,
            flags=re.MULTILINE,
        )

        for subtask_id, subtask_entry in task_entry.get("subtasks", {}).items():
            desired = checkbox_for_status(subtask_entry.get("status", "pending"))
            todo_content = re.sub(
                rf"(^\s*-\s\[)([ x~])(\]\s+{re.escape(subtask_id)}:)",
                rf"\g<1>{desired}\g<3>",
                todo_content,
                count=1,
                flags=re.MULTILINE,
            )

    if todo_content != original_content:
        try:
            todo_path.write_text(todo_content, encoding="utf-8")
        except OSError as exc:
            mm_error(f"Failed to sync objective todo from durable state: {exc}")
            return

    sync_objective_handoff(task_id)


def get_execution_subtasks(task_id: str) -> list[dict[str, Any]]:
    """Read subtasks for execution, preferring durable objective state over todo."""
    sync_objective_todo_from_state(task_id)
    subtasks = read_subtasks_from_todo(task_id)
    objective_state = load_objective_state(task_id=task_id)
    if not objective_state:
        return subtasks

    task_entry = objective_state.get("tasks", {}).get(task_id, {})
    durable_subtasks = task_entry.get("subtasks", {})
    if not durable_subtasks:
        return subtasks

    for subtask in subtasks:
        durable = durable_subtasks.get(subtask["id"])
        if durable:
            subtask["completed"] = durable.get("status") == "completed"
    return subtasks


def bootstrap_objective_state_from_artifacts(
    objective_slug: str, plan_path: Path, todo_path: Path
) -> dict[str, Any]:
    """Create a durable objective execution state from tasks/todo artifacts.

    This is a one-time migration fallback for objectives created before
    `execution-state.json` existed. Runtime state, when present for the same
    objective, overrides the matching active root task.
    """
    state: dict[str, Any] = {
        "objective_slug": objective_slug,
        "plan_path": str(plan_path),
        "todo_path": str(todo_path),
        "tasks": {},
        "updated_at": datetime.now().isoformat(),
        "bootstrapped_from_artifacts": True,
    }

    root_status_map = {
        task_id: checkbox
        for task_id, checkbox, _title in get_root_task_statuses(todo_path)
    }
    runtime_state = load_runtime_state()
    runtime_task_id = runtime_state.get("task_id") if runtime_state else None
    runtime_same_objective = (
        runtime_state is not None
        and runtime_state.get("objective_slug") == objective_slug
    )

    for root_task_id in get_task_ids_from_plan(plan_path):
        subtasks = read_subtasks_from_todo(root_task_id)
        task_entry: dict[str, Any] = {
            "status": "pending",
            "subtasks": {},
            "started_at": None,
            "completed_at": None,
            "plan_path": str(plan_path),
            "todo_path": str(todo_path),
        }
        for subtask in subtasks:
            task_entry["subtasks"][subtask["id"]] = {
                "description": subtask["description"],
                "status": "completed" if subtask["completed"] else "pending",
                "started_at": None,
                "completed_at": None,
                "duration_seconds": 0,
                "updated_at": None,
            }

        if runtime_same_objective and runtime_task_id == root_task_id:
            for subtask_id, runtime_subtask in runtime_state.get(
                "subtasks", {}
            ).items():
                if subtask_id in task_entry["subtasks"]:
                    task_entry["subtasks"][subtask_id]["status"] = runtime_subtask.get(
                        "status", task_entry["subtasks"][subtask_id]["status"]
                    )
                    task_entry["subtasks"][subtask_id]["started_at"] = (
                        runtime_subtask.get("started_at")
                    )
                    task_entry["subtasks"][subtask_id]["completed_at"] = (
                        runtime_subtask.get("completed_at")
                    )
                    task_entry["subtasks"][subtask_id]["duration_seconds"] = (
                        runtime_subtask.get("duration_seconds", 0)
                    )
                    task_entry["subtasks"][subtask_id]["updated_at"] = (
                        runtime_subtask.get("updated_at")
                    )

        subtask_states = [s["status"] for s in task_entry["subtasks"].values()]
        parent_checkbox = root_status_map.get(root_task_id, " ")
        if subtask_states and all(status == "completed" for status in subtask_states):
            task_entry["status"] = "completed"
        elif (
            any(status == "in_progress" for status in subtask_states)
            or parent_checkbox == "~"
        ):
            task_entry["status"] = "in_progress"
        elif any(status == "completed" for status in subtask_states):
            task_entry["status"] = "in_progress"
        else:
            task_entry["status"] = "pending"

        state["tasks"][root_task_id] = task_entry

    save_objective_state(state)
    return state


def sync_objective_handoff(task_id: str) -> None:
    """Synchronize objective HANDOFF-CURRENT.md from objective todo/task state."""
    handoff_path = get_objective_handoff_path(task_id)
    if handoff_path is None or not handoff_path.exists():
        return

    try:
        plan_path, todo_path = get_active_paths(task_id)
        handoff_text = handoff_path.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError, ValueError):
        return

    objective_state = load_objective_state(task_id=task_id)
    if objective_state and objective_state.get("tasks"):
        root_statuses: list[tuple[str, str, str]] = []
        for root_id in get_task_ids_from_plan(plan_path):
            root_title = get_task_title_from_plan(plan_path, root_id) or root_id
            task_state = objective_state.get("tasks", {}).get(root_id, {})
            task_status = task_state.get("status", "pending")
            checkbox = (
                "x"
                if task_status == "completed"
                else "~"
                if task_status == "in_progress"
                else " "
            )
            root_statuses.append((root_id, checkbox, root_title))
    else:
        root_statuses = get_root_task_statuses(todo_path)
    if not root_statuses:
        return

    completed_lines = [
        f"- [x] {root_id}: {title}"
        for root_id, status, title in root_statuses
        if status == "x"
    ]
    if not completed_lines:
        completed_lines = ["- None yet."]

    next_pending = next(
        ((root_id, title) for root_id, status, title in root_statuses if status != "x"),
        None,
    )
    if next_pending is None:
        next_task_lines = ["- Objective package has no pending root tasks."]
        validation_lines = ["- None — objective currently appears complete."]
    else:
        next_task_id, _next_title = next_pending
        dependency_summary = get_task_dependencies_from_plan(plan_path, next_task_id)
        next_task_lines = [
            f"- `{next_task_id}` from `tasks.md` — depends on {dependency_summary}."
        ]
        validation_commands = get_task_validation_commands_from_plan(
            plan_path, next_task_id
        )
        validation_lines = [f"- {command}" for command in validation_commands] or [
            "- Validation commands not declared yet."
        ]

    handoff_text = re.sub(
        r"## Completed tasks\n.*?(?=\n## |\Z)",
        "## Completed tasks\n" + "\n".join(completed_lines) + "\n",
        handoff_text,
        flags=re.DOTALL,
    )
    handoff_text = re.sub(
        r"## Exact next recommended task\n.*?(?=\n## |\Z)",
        "## Exact next recommended task\n" + "\n".join(next_task_lines) + "\n",
        handoff_text,
        flags=re.DOTALL,
    )
    handoff_text = re.sub(
        r"## Validation commands for [^\n]+\n.*?(?=\n## |\Z)",
        "## Validation commands for "
        + (next_pending[0] if next_pending else "objective completion")
        + "\n"
        + "\n".join(validation_lines)
        + "\n",
        handoff_text,
        flags=re.DOTALL,
    )

    try:
        handoff_path.write_text(handoff_text, encoding="utf-8")
    except OSError as exc:
        mm_error(f"Failed to sync objective handoff: {exc}")


def audit_task_consistency(task_id: str) -> list[str]:
    """Compare runtime truth against todo/handoff artifacts for a root task."""
    issues: list[str] = []
    if not RUNTIME_STATE_PATH.exists():
        return issues

    try:
        state = json.loads(RUNTIME_STATE_PATH.read_text(encoding="utf-8"))
        _, todo_path = get_active_paths(task_id)
        todo_content = todo_path.read_text(encoding="utf-8")
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        return [f"artifact read failure: {exc}"]

    subtasks = {
        sid: sdata
        for sid, sdata in state.get("subtasks", {}).items()
        if sid.startswith(task_id + ".")
    }
    if not subtasks:
        return issues

    def expected_checkbox(status: str) -> str:
        if status == "completed":
            return "x"
        if status == "in_progress":
            return "~"
        return " "

    for subtask_id, subtask_data in subtasks.items():
        match = re.search(
            rf"^\s*-\s\[(?P<status>[ x~])\]\s+{re.escape(subtask_id)}:",
            todo_content,
            re.MULTILINE,
        )
        if not match:
            issues.append(f"todo missing subtask line for {subtask_id}")
            continue
        actual = match.group("status")
        expected = expected_checkbox(subtask_data.get("status", "pending"))
        if actual != expected:
            issues.append(
                f"todo subtask mismatch for {subtask_id}: todo=[{actual}] runtime={subtask_data.get('status')}"
            )

    total = len(subtasks)
    completed = sum(
        1 for data in subtasks.values() if data.get("status") == "completed"
    )
    in_progress = any(data.get("status") == "in_progress" for data in subtasks.values())
    expected_parent = (
        "x"
        if completed == total and total > 0
        else "~"
        if in_progress or completed > 0
        else " "
    )
    parent_match = re.search(
        rf"^-\s\[(?P<status>[ x~])\]\s+{re.escape(task_id)}:",
        todo_content,
        re.MULTILINE,
    )
    if not parent_match:
        issues.append(f"todo missing parent line for {task_id}")
    else:
        actual_parent = parent_match.group("status")
        if actual_parent != expected_parent:
            issues.append(
                f"todo parent mismatch for {task_id}: todo=[{actual_parent}] expected=[{expected_parent}]"
            )

    handoff_path = get_objective_handoff_path(task_id)
    if handoff_path and handoff_path.exists():
        handoff_text = handoff_path.read_text(encoding="utf-8")
        if expected_parent != "x" and re.search(
            rf"^-\s\[x\]\s+{re.escape(task_id)}:",
            handoff_text,
            re.MULTILINE,
        ):
            issues.append(
                f"handoff claims {task_id} completed while runtime is incomplete"
            )

    return issues


def reconcile_artifacts_from_runtime(task_id: str) -> None:
    """Rewrite objective todo/handoff for a root task from runtime state truth."""
    if not RUNTIME_STATE_PATH.exists():
        mm_error("No runtime state to reconcile from")
        return

    try:
        state = json.loads(RUNTIME_STATE_PATH.read_text(encoding="utf-8"))
        _, todo_path = get_active_paths(task_id)
        todo_content = todo_path.read_text(encoding="utf-8")
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        mm_error(f"Failed to reconcile artifacts: {exc}")
        return

    subtasks = {
        sid: sdata
        for sid, sdata in state.get("subtasks", {}).items()
        if sid.startswith(task_id + ".")
    }
    if not subtasks:
        mm_error(f"No runtime subtasks found for {task_id}")
        return

    def checkbox_for_status(status: str) -> str:
        if status == "completed":
            return "x"
        if status == "in_progress":
            return "~"
        return " "

    for subtask_id, subtask_data in subtasks.items():
        desired = checkbox_for_status(subtask_data.get("status", "pending"))
        todo_content = re.sub(
            rf"(^\s*-\s\[)([ x~])(\]\s+{re.escape(subtask_id)}:)",
            rf"\g<1>{desired}\g<3>",
            todo_content,
            count=1,
            flags=re.MULTILINE,
        )

    total = len(subtasks)
    completed = sum(
        1 for data in subtasks.values() if data.get("status") == "completed"
    )
    any_in_progress = any(
        data.get("status") == "in_progress" for data in subtasks.values()
    )
    desired_parent = (
        "x"
        if completed == total and total > 0
        else "~"
        if any_in_progress or completed > 0
        else " "
    )
    todo_content = re.sub(
        rf"(^-\s\[)([ x~])(\]\s+{re.escape(task_id)}:)",
        rf"\g<1>{desired_parent}\g<3>",
        todo_content,
        count=1,
        flags=re.MULTILINE,
    )

    try:
        todo_path.write_text(todo_content, encoding="utf-8")
    except OSError as exc:
        mm_error(f"Failed to write reconciled todo.md: {exc}")
        return

    try:
        update_incremental_time_tracking(task_id)
    except Exception as exc:
        mm_error(f"Time tracking refresh after reconcile failed: {exc}")

    sync_objective_handoff(task_id)


def sync_subtask_checkbox(subtask_id: str, checkbox: str) -> None:
    """Synchronize a subtask checkbox in todo.md to the desired value."""
    _, todo_path = get_active_paths(subtask_id)
    if not todo_path.exists():
        return
    try:
        todo_content = todo_path.read_text(encoding="utf-8")
        updated_content, count = re.subn(
            rf"(^\s*-\s?\[)([ x~])(\]\s+{re.escape(subtask_id)}:)",
            rf"\g<1>{checkbox}\g<3>",
            todo_content,
            count=1,
            flags=re.MULTILINE,
        )
        if count > 0:
            todo_path.write_text(updated_content, encoding="utf-8")
    except OSError as exc:
        mm_error(f"Failed to sync todo checkbox for {subtask_id}: {exc}")


def get_objective_task_status(task_id: str) -> str | None:
    """Return durable status for a root task from objective execution state."""
    objective_state = load_objective_state(task_id=task_id)
    if not objective_state:
        return None
    task_entry = objective_state.get("tasks", {}).get(task_id)
    if not task_entry:
        return None
    status = task_entry.get("status")
    return status if isinstance(status, str) else None


def trigger_completion_notification(task_id: str) -> None:
    """Play the completion notification exactly once per runtime task."""
    state = load_runtime_state()
    if state is None or state.get("task_id") != task_id:
        return
    if state.get("completion_notified_at"):
        return
    if not runtime_task_complete(state):
        return
    if not NOTIFY_SCRIPT_PATH.exists():
        return

    try:
        result = subprocess.run(
            ["python3", str(NOTIFY_SCRIPT_PATH), task_id, "complete"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
        if result.returncode != 0:
            mm_error(
                f"Notification script failed for {task_id}: {result.stderr.strip()}"
            )
            return
        state["completion_notified_at"] = datetime.now().isoformat()
        RUNTIME_STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
        mm_info(f"Notification delivered for {task_id}")
    except Exception as exc:
        mm_error(f"Could not trigger completion notification for {task_id}: {exc}")


def ensure_runtime_can_start_task(task_id: str) -> None:
    """Block starting a new task if a previous runtime task is incomplete or inconsistent."""
    state = load_runtime_state()
    if state is None:
        return

    active_task_id = state.get("task_id")
    if not active_task_id:
        return

    # Same task: reconcile if needed, then allow resume/start logic to continue.
    if active_task_id == task_id:
        issues = audit_task_consistency(task_id)
        if issues:
            mm_info(
                "Detected stale artifact mismatch before execution — reconciling from runtime state"
            )
            for issue in issues:
                mm_error(f"SYNC: {issue}")
            reconcile_artifacts_from_runtime(task_id)
        return

    if runtime_task_complete(state):
        return

    issues = audit_task_consistency(active_task_id)
    if issues:
        mm_error(
            f"Cannot start {task_id}: previous runtime task {active_task_id} is incomplete and artifacts are out of sync."
        )
        for issue in issues:
            mm_error(f"SYNC: {issue}")
        mm_error(
            f"Repair with: python3 .claude/commands/mm/complete-task-handler.py --reconcile {active_task_id}"
        )
        mm_error(f"Or resume with: /mm:continue-task {active_task_id}")
        sys.exit(1)

    mm_error(
        f"Cannot start {task_id}: previous runtime task {active_task_id} is still incomplete."
    )
    mm_error(f"Resume it first with: /mm:continue-task {active_task_id}")
    sys.exit(1)


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
    """Read task details from plan.md, with fallback to todo.md.

    Args:
        task_id: Task identifier (e.g., "D1", "13-01").

    Returns:
        Dictionary with "id" and "title" keys.

    Raises:
        ValueError: If task_id not found in plan.md or todo.md.
        FileNotFoundError: If plan.md doesn't exist.
        OSError: If file cannot be read.
    """
    plan_path, _ = get_active_paths(task_id)
    try:
        content = plan_path.read_text()
    except FileNotFoundError:
        raise FileNotFoundError(f"plan.md not found at {plan_path}")
    except OSError as e:
        raise OSError(f"Failed to read plan.md: {e}")

    # Match heading at any level (###, ####) — stop at any next heading or end
    # Also supports "## PHASE 20:" style headers (numeric phase IDs)
    task_id_esc = re.escape(task_id)
    pattern = rf"#{2,6}\s+(?:PHASE\s+)?{task_id_esc}:([^\n]+)\n(.*?)(?=\n#|\Z)"
    match = re.search(pattern, content, re.DOTALL)

    if match:
        return {"id": task_id, "title": match.group(1).strip()}

    # Fallback: read title from todo.md
    # Supports both heading style "### 20: Title" and list style "- [ ] 20: Title"
    try:
        _, todo_path = get_active_paths(task_id)
        todo_content = todo_path.read_text()
        todo_match = re.search(rf"### {task_id_esc}:([^\n]+)", todo_content)
        if todo_match:
            return {"id": task_id, "title": todo_match.group(1).strip()}
        # List-style parent task: "- [ ] 20: Title" or "- [~] 20: Title"
        list_match = re.search(
            rf"^-\s\[[ x~]\]\s+{task_id_esc}:([^\n]+)", todo_content, re.MULTILINE
        )
        if list_match:
            return {"id": task_id, "title": list_match.group(1).strip()}
    except OSError:
        pass

    raise ValueError(f"Task {task_id} not found in plan.md or todo.md")


def read_subtasks_from_todo(task_id: str) -> list[dict[str, Any]]:
    """Read subtasks from todo.md.

    Supports three structures:
    1. V2 Hierarchical: "- [ ] A1: Task" with "  - [ ] A1.01: subtask" (2-space indent)
    2. V1 Flat: checkboxes directly under task heading (e.g., "### B2:" followed by "- [ ] subtask")
    3. V1 Nested: subtask headings under task (e.g., "#### B2.1:" under "### B2:")

    Args:
        task_id: Task identifier (e.g., "D1" or "D1.1").

    Returns:
        List of subtask dictionaries with "id", "description", "completed" keys.

    Raises:
        ValueError: If task_id not found in todo.md.
        FileNotFoundError: If todo.md doesn't exist.
        OSError: If file cannot be read.
    """
    _, todo_path = get_active_paths(task_id)
    try:
        content = todo_path.read_text()
    except FileNotFoundError:
        raise FileNotFoundError(f"todo.md not found at {todo_path}")
    except OSError as e:
        raise OSError(f"Failed to read todo.md: {e}")

    # Try V2 hierarchical format first (handles parent tasks with dots like B2.6)
    subtasks = _read_v2_hierarchical_subtasks(content, task_id)
    if subtasks:
        return subtasks

    # Check if task_id contains a dot (e.g., "B2.1") - subtask heading
    if "." in task_id:
        return _read_subtask_heading(content, task_id)

    # No dot - parent task, try both flat and nested structures
    subtasks = _read_flat_subtasks(content, task_id)
    if subtasks:
        return subtasks

    # Try nested structure (subtask headings under parent)
    return _read_nested_subtasks(content, task_id)


def _read_v2_hierarchical_subtasks(content: str, task_id: str) -> list[dict[str, Any]]:
    """Read V2 hierarchical format: list-based with intermediate task headings.

    Example:
        - [~] B2: Core Feature Completion

        - [x] B2.1: Facebook Webhook Polling Completion
          - [x] B2.1.01: Review TODO comments
          - [x] B2.1.02: Implement error handling
    """
    # Find the parent task section
    # Lookahead handles: "## PHASE N" headers, letter+digit IDs (B2), and numeric IDs (21, 21.5)
    pattern = rf"^-\s\[([ x~])\]\s+{re.escape(task_id)}:.*?\n(.*?)(?=^##|^-\s\[[ x~]\]\s+(?:[A-Z]?\d+(?:\.\d+)?):|\Z)"
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)

    if not match:
        return []

    parent_section = match.group(2)

    # Find all subtask headings (e.g., "- [x] B2.1:", "- [x] B2.2:")
    subtask_pattern = (
        rf"^  -\s\[([ x~])\]\s+{re.escape(task_id)}\.(\d+):([^\n]+)\n((?:  -\[.*?\n)*)"
    )
    subtask_matches = re.finditer(subtask_pattern, parent_section, re.MULTILINE)

    subtasks: list[dict[str, Any]] = []

    for match in subtask_matches:
        checkbox_state = match.group(1)
        subtask_num = match.group(2)
        subtask_title = match.group(3).strip()
        subtask_body = match.group(4)  # Indented checkboxes (B2.1.01, etc.)

        full_subtask_id = f"{task_id}.{subtask_num}"

        sub_subtasks = re.findall(r"^  - \[([ x~])\]", subtask_body, re.MULTILINE)
        if sub_subtasks:
            is_complete = all(state == "x" for state in sub_subtasks)
        else:
            is_complete = checkbox_state == "x"

        subtasks.append(
            {
                "id": full_subtask_id,
                "description": subtask_title,
                "completed": is_complete,
            }
        )

    return subtasks


def _read_flat_subtasks(content: str, task_id: str) -> list[dict[str, Any]]:
    """Read flat structure: checkboxes directly under task heading.

    Example:
        ### B2: Core Feature Completion
        - [ ] Review TODO comments
        - [ ] Implement error handling
    """
    pattern = r"#{2,6}\s+" + re.escape(task_id) + r":([^\n]+)\n(.*?)(?=\n##|\n###|\Z)"
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        return []

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


def _read_nested_subtasks(content: str, task_id: str) -> list[dict[str, Any]]:
    """Read nested structure: subtask headings under parent task.

    Example:
        ### B2: Core Feature Completion

        #### B2.1: Facebook Webhook Polling Completion
        - [ ] Review TODO comments
        - [ ] Implement error handling

        #### B2.2: VIN Decode Integration Tests
        - [ ] Create test file
    """
    parent_pattern = (
        r"(#{2,6}\s+" + re.escape(task_id) + r":[^\n]+\n)(.*?)(?=\n##|\n### [A-Z]|\Z)"
    )
    parent_match = re.search(parent_pattern, content, re.DOTALL)

    if not parent_match:
        return []

    parent_section = parent_match.group(2)

    subtask_pattern = (
        r"#{3,4}\s+" + re.escape(task_id) + r"\.\d+:(.+?)\n(.*?)(?=\n#{3,4}|\Z)"
    )
    subtask_matches = re.finditer(subtask_pattern, parent_section, re.DOTALL)

    subtasks: list[dict[str, Any]] = []

    for match in subtask_matches:
        subtask_title = match.group(1).strip()
        subtask_body = match.group(2)

        heading_line = match.group(0).split("\n")[0]
        subtask_id_match = re.search(rf"{re.escape(task_id)}\.(\d+)", heading_line)
        if not subtask_id_match:
            continue
        subtask_num = subtask_id_match.group(1)
        full_subtask_id = f"{task_id}.{subtask_num}"

        checkboxes = re.findall(r"- \[([ x])\]", subtask_body)
        completed_count = sum(1 for c in checkboxes if c == "x")
        total_count = len(checkboxes)

        is_complete = total_count > 0 and completed_count == total_count

        subtasks.append(
            {
                "id": full_subtask_id,
                "description": subtask_title,
                "completed": is_complete,
            }
        )

    return subtasks


def _read_subtask_heading(content: str, task_id: str) -> list[dict[str, Any]]:
    """Read a specific subtask by ID (e.g., "B2.1").

    When calling /mm:complete-task B2.1, this finds the #### B2.1: section
    and returns its checkboxes as sub-subtasks.
    """
    pattern = (
        r"#{3,4}\s+" + re.escape(task_id) + r":([^\n]+)\n(.*?)(?=\n?#{3,4}|\n##|\Z)"
    )
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        raise ValueError(f"Subtask {task_id} not found in todo.md")

    section = match.group(2)
    lines = section.split("\n")
    subtasks: list[dict[str, Any]] = []

    current_letter = ord("a")

    for line in lines:
        if line.strip().startswith("- ["):
            match = re.match(r"- \[([ x])\] (.+)", line)
            if match:
                status, text = match.groups()
                subtasks.append(
                    {
                        "id": f"{task_id}.{chr(current_letter)}",
                        "description": text.strip(),
                        "completed": status == "x",
                    }
                )
                current_letter += 1

    return subtasks


# ============================================================================
# State Management
# ============================================================================


def init_runtime_state(
    task_id: str, subtasks: list[dict[str, Any]], source: TaskSource
) -> dict[str, Any]:
    """Initialize runtime state file.

    Args:
        task_id: Task identifier.
        subtasks: List of subtask dictionaries.

    Returns:
        Runtime state dictionary with session info and subtask statuses.
    """
    session_id = f"sess-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    now_iso = datetime.now().isoformat()

    runtime_state: dict[str, Any] = {
        "task_id": task_id,
        "source_mode": source.mode,
        "objective_slug": source.objective_slug,
        "plan_path": str(source.plan_path),
        "todo_path": str(source.todo_path),
        "session_id": session_id,
        "started_at": now_iso,
        "phase": 19,  # Current MM-Flow phase
        "subtasks": {
            st["id"]: {
                "description": st["description"],
                "status": "completed" if st["completed"] else "pending",
                "retries": 0,
                "started_at": None,
                "completed_at": None,
                "duration_seconds": 0,
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

    seed_objective_task_state(source, task_id, subtasks)

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
    objective_slug = state.get("objective_slug")
    root_task_id = get_root_task_id(subtask_id)

    if subtask_id in state["subtasks"]:
        now = datetime.now()
        now_iso = now.isoformat()

        state["subtasks"][subtask_id]["status"] = status
        state["subtasks"][subtask_id]["updated_at"] = now_iso

        # Calculate duration if completing
        if status == "completed" and state["subtasks"][subtask_id].get("started_at"):
            started_at_str = state["subtasks"][subtask_id]["started_at"]
            if started_at_str:
                started_at = datetime.fromisoformat(started_at_str)
                duration = (now - started_at).total_seconds()
                state["subtasks"][subtask_id]["completed_at"] = now_iso
                state["subtasks"][subtask_id]["duration_seconds"] = round(duration, 2)
        elif status == "in_progress":
            # Always refresh the clock when entering in_progress so resumed or
            # previously inconsistent runtime states do not inherit stale start
            # timestamps from an older session.
            state["subtasks"][subtask_id]["started_at"] = now_iso

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

        objective_state = load_objective_state(objective_slug=objective_slug) or (
            {
                "objective_slug": objective_slug,
                "plan_path": state.get("plan_path"),
                "todo_path": state.get("todo_path"),
                "tasks": {},
            }
            if objective_slug
            else None
        )
        if objective_state is not None:
            task_entry = objective_state.setdefault("tasks", {}).setdefault(
                root_task_id,
                {
                    "status": "pending",
                    "subtasks": {},
                    "started_at": None,
                    "completed_at": None,
                },
            )
            subtask_entry = task_entry.setdefault("subtasks", {}).setdefault(
                subtask_id,
                {
                    "description": state["subtasks"][subtask_id].get(
                        "description", subtask_id
                    )
                },
            )
            subtask_entry["description"] = state["subtasks"][subtask_id].get(
                "description", subtask_entry.get("description", subtask_id)
            )
            subtask_entry["status"] = status
            subtask_entry["started_at"] = state["subtasks"][subtask_id].get(
                "started_at"
            )
            subtask_entry["completed_at"] = state["subtasks"][subtask_id].get(
                "completed_at"
            )
            subtask_entry["duration_seconds"] = state["subtasks"][subtask_id].get(
                "duration_seconds", 0
            )
            subtask_entry["updated_at"] = now_iso
            if error:
                subtask_entry["error"] = error
            if commit_sha:
                subtask_entry["commit_sha"] = commit_sha

            subtask_states = [
                sub_state.get("status", "pending")
                for sub_state in task_entry.get("subtasks", {}).values()
            ]
            if subtask_states and all(s == "completed" for s in subtask_states):
                task_entry["status"] = "completed"
                task_entry["completed_at"] = now_iso
                task_entry.setdefault("started_at", state.get("started_at"))
            elif any(s == "in_progress" for s in subtask_states) or any(
                s == "completed" for s in subtask_states
            ):
                task_entry["status"] = "in_progress"
                task_entry["started_at"] = task_entry.get("started_at") or now_iso
                task_entry["completed_at"] = None
            else:
                task_entry["status"] = "pending"

            objective_state["updated_at"] = now_iso
            save_objective_state(objective_state)

    # If this subtask was just completed, check if all siblings are complete
    # and propagate completion to parent
    if status == "completed":
        sync_subtask_checkbox(subtask_id, "x")
        # Extract parent task ID from subtask_id (e.g., "B2.1" -> "B2", "B2.1.a" -> "B2.1")
        if "." in subtask_id:
            parts = subtask_id.rsplit(".", 1)
            parent_id = parts[0] if len(parts) == 2 else subtask_id

            try:
                propagate_parent_completion(parent_id)
            except Exception as e:
                # Don't fail the subtask update if propagation fails
                mm_error(f"Failed to propagate parent completion: {e}")

        # Update incremental time tracking after each checkpoint
        try:
            # Get the root parent task ID for time tracking
            # For B2.6.01, we want to update B2 (not B2.6)
            update_incremental_time_tracking(root_task_id)
        except Exception as e:
            # Don't fail the checkpoint if time tracking fails
            mm_error(f"Failed to update incremental time tracking: {e}")

    # If this subtask is now in_progress, mark all parents with ~
    if status == "in_progress":
        sync_subtask_checkbox(subtask_id, "~")
        if "." in subtask_id:
            parts = subtask_id.rsplit(".", 1)
            parent_id = parts[0] if len(parts) == 2 else subtask_id

            try:
                propagate_in_progress(parent_id)
            except Exception as e:
                # Don't fail the subtask update if propagation fails
                mm_error(f"Failed to propagate in_progress state: {e}")


def propagate_parent_completion(task_id: str) -> None:
    """Check if all subtasks of task_id are complete and mark parent as complete in todo.md.

    This function implements hierarchical completion propagation:
    - If all sub-subtasks of a subtask are complete (e.g., B2.1.a, B2.1.b), mark B2.1 as complete
    - If all subtasks of a parent are complete (e.g., B2.1-B2.6), mark B2 as complete
    - Cascades up the hierarchy automatically

    Args:
        task_id: Parent task ID to check (e.g., "B2" or "B2.1").

    Raises:
        FileNotFoundError: If todo.md doesn't exist.
        OSError: If files cannot be read or written.
    """
    _, todo_path = get_active_paths(task_id)
    if not todo_path.exists():
        mm_error(f"todo.md not found at {todo_path}")
        return

    # First, try to find leaf-level subtasks in task-progress.json
    has_json_subtasks = False
    if RUNTIME_STATE_PATH.exists():
        try:
            state = json.loads(RUNTIME_STATE_PATH.read_text())

            sibling_subtasks = {
                st_id: st_data
                for st_id, st_data in state["subtasks"].items()
                if st_id.startswith(task_id + ".")
            }

            if sibling_subtasks:
                has_json_subtasks = True

                all_complete = all(
                    st_data.get("status") == "completed"
                    for st_data in sibling_subtasks.values()
                )

                if not all_complete:
                    return
        except (json.JSONDecodeError, OSError) as e:
            mm_error(f"Failed to read task-progress.json: {e}")

    # Check todo.md for intermediate-level subtasks
    try:
        todo_content = todo_path.read_text()
    except (FileNotFoundError, OSError) as e:
        mm_error(f"Failed to read todo.md: {e}")
        return

    subtask_pattern = rf"^-\s\[([ x~])\]\s+{re.escape(task_id)}\.\d+:"
    subtask_matches = re.findall(subtask_pattern, todo_content, re.MULTILINE)

    if subtask_matches:
        all_complete = all(state == "x" for state in subtask_matches)

        if not all_complete:
            return
    elif not has_json_subtasks:
        return

    # All subtasks are complete - mark parent as complete in todo.md
    try:
        todo_content = todo_path.read_text()
    except (FileNotFoundError, OSError) as e:
        mm_error(f"Failed to read todo.md: {e}")
        return

    parent_pattern = rf"(^-\s?\[)([ ~])(\]\s+{re.escape(task_id)}:)"

    def replace_checkbox(match: re.Match[str]) -> str:
        return f"{match.group(1)}x{match.group(3)}"

    new_content, count = re.subn(
        parent_pattern, replace_checkbox, todo_content, count=1, flags=re.MULTILINE
    )

    if count == 0:
        already_complete = re.search(
            rf"^-\s\[x\]\s+{re.escape(task_id)}:", todo_content, re.MULTILINE
        )
        if already_complete:
            return
        else:
            mm_error(f"Could not find parent task checkbox for {task_id} in todo.md")
            return

    try:
        todo_path.write_text(new_content)
        mm_info(f"Marked parent task {task_id} as complete in todo.md")
    except OSError as e:
        mm_error(f"Failed to write todo.md: {e}")
        return

    # Cascade up the hierarchy
    if "." in task_id:
        parts = task_id.rsplit(".", 1)
        grandparent_id = parts[0] if len(parts) == 2 else None

        if grandparent_id:
            try:
                propagate_parent_completion(grandparent_id)
            except Exception as e:
                mm_error(
                    f"Failed to cascade completion to grandparent {grandparent_id}: {e}"
                )


def propagate_in_progress(task_id: str) -> None:
    """Mark parent task as in-progress (~) in todo.md when a child is in-progress.

    Args:
        task_id: Parent task ID to mark as in-progress (e.g., "B2" or "B2.6").

    Raises:
        FileNotFoundError: If todo.md doesn't exist.
        OSError: If files cannot be read or written.
    """
    _, todo_path = get_active_paths(task_id)
    if not todo_path.exists():
        mm_error(f"todo.md not found at {todo_path}")
        return

    try:
        todo_content = todo_path.read_text()
    except (FileNotFoundError, OSError) as e:
        mm_error(f"Failed to read todo.md: {e}")
        return

    parent_pattern = rf"(^-\s?\[)([ x])(\]\s+{re.escape(task_id)}:)"

    def replace_with_tilde(match: re.Match[str]) -> str:
        return f"{match.group(1)}~{match.group(3)}"

    new_content, count = re.subn(
        parent_pattern, replace_with_tilde, todo_content, count=1, flags=re.MULTILINE
    )

    if count == 0:
        already_in_progress = re.search(
            rf"^-\s\[~\]\s+{re.escape(task_id)}:", todo_content, re.MULTILINE
        )
        if already_in_progress:
            return
        else:
            mm_error(f"Could not find parent task checkbox for {task_id} in todo.md")
            return

    try:
        todo_path.write_text(new_content)
        mm_info(f"Marked parent task {task_id} as in-progress (~) in todo.md")
    except OSError as e:
        mm_error(f"Failed to write todo.md: {e}")
        return

    # Cascade up
    if "." in task_id:
        parts = task_id.rsplit(".", 1)
        grandparent_id = parts[0] if len(parts) == 2 else None

        if grandparent_id:
            try:
                propagate_in_progress(grandparent_id)
            except Exception as e:
                mm_error(
                    f"Failed to cascade in_progress to grandparent {grandparent_id}: {e}"
                )


def update_incremental_time_tracking(task_id: str) -> None:
    """Update time tracking in todo.md after each checkpoint.

    Calls update-todo-times.py to update estimate vs actual, deviation,
    avg time per subtask, and progress percentage.

    Args:
        task_id: Task identifier (e.g., "B2" or "B2.6").
    """
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(Path(__file__).parent / "update-todo-times.py"),
                task_id,
            ],
            capture_output=True,
            text=True,
            check=False,
            cwd=Path(__file__).parent.parent.parent.parent,
        )

        if result.returncode != 0:
            mm_error(f"update-todo-times.py failed: {result.stderr}")
        else:
            mm_info(f"Updated time tracking for task {task_id}")

    except FileNotFoundError:
        mm_info("update-todo-times.py not found - skipping time tracking update")
    except Exception as e:
        mm_error(f"Failed to update time tracking: {e}")


def execute_subtask_with_tracking(subtask_id: str, func: Any) -> Any:
    """Execute a subtask function with proper status tracking.

    Args:
        subtask_id: Subtask ID (e.g., "B2.6.03").
        func: Callable to execute.

    Returns:
        Result of func().

    Raises:
        Exception: If func raises (after marking as failed).
    """
    try:
        update_subtask_status(subtask_id, "in_progress")
        result = func()
        update_subtask_status(subtask_id, "completed")
        return result
    except Exception as e:
        update_subtask_status(
            subtask_id, "failed", error=f"{type(e).__name__}: {str(e)}"
        )
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
        source = resolve_task_source(task_id)
        task = read_task_from_plan(task_id)
        subtasks = get_execution_subtasks(task_id)

        # Filter to pending subtasks from durable state only. Git history is
        # informational, not a progress source of truth in the objective flow.
        pending_subtasks = [st for st in subtasks if not st["completed"]]

        # Mark parent as [~] in todo.md if some subtasks are done but not all.
        # This is safe because todo is reprojected from objective state first.
        has_completed = any(st["completed"] for st in subtasks)
        has_pending = len(pending_subtasks) > 0
        if has_completed and has_pending and source.todo_path.exists():
            try:
                todo_content = source.todo_path.read_text()
                task_escaped = re.escape(task_id)
                pattern = rf"(^\s*-\s?\[)([ ])(\]\s+{task_escaped}:)"
                new_content, count = re.subn(
                    pattern,
                    lambda m: f"{m.group(1)}~{m.group(3)}",
                    todo_content,
                    count=1,
                    flags=re.MULTILINE,
                )
                if count > 0:
                    source.todo_path.write_text(new_content)
                    mm_info(f"Marked parent {task_id} as [~] (in progress)")
            except OSError:
                pass  # Non-fatal — payload still returned

        project_id = _read_project_id_from_config(PROJECT_ROOT)
        return {
            "task_id": task_id,
            "task_title": task["title"],
            "planning_mode": source.mode,
            "objective_slug": source.objective_slug,
            "plan_path": str(source.plan_path),
            "todo_path": str(source.todo_path),
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


def _has_checkpoint(task_id: str) -> bool:
    """Return True if there's a real checkpoint to resume from.

       Checks:
    1. task-progress.json exists for this task_id
       2. Has at least one completed subtask (not just initialized)
    """
    if not RUNTIME_STATE_PATH.exists():
        return False
    try:
        state = json.loads(RUNTIME_STATE_PATH.read_text(encoding="utf-8"))
        if state.get("task_id") != task_id:
            return False
        # Must have at least one completed subtask to justify --continue
        completed = [
            sid
            for sid, info in state.get("subtasks", {}).items()
            if info.get("status") == "completed"
        ]
        return len(completed) > 0
    except (json.JSONDecodeError, OSError):
        return False


def build_model_brief(task_id: str, resume_mode: bool = False) -> str:
    """Build a concise model handoff brief for a root task.

    Args:
        task_id: Root task identifier.
        resume_mode: Whether the brief is for an explicit resume flow.

    Returns:
        Markdown brief that another model can follow without a long custom prompt.
    """
    source = resolve_task_source(task_id)
    task = read_task_from_plan(task_id)
    objective_dir = source.plan_path.parent
    objective_state_path = objective_dir / OBJECTIVE_STATE_FILENAME
    handoff_path = objective_dir / "HANDOFF-CURRENT.md"
    requirements_path = objective_dir / "requirements.md"
    design_path = objective_dir / "design.md"
    objective_state = load_objective_state(task_id=task_id) or {}
    task_state = objective_state.get("tasks", {}).get(task_id, {})
    task_status = task_state.get("status", "pending")
    validation_commands = get_task_validation_commands_from_plan(
        source.plan_path, task_id
    )

    # Only suggest --continue if there's a real checkpoint to resume from.
    # If resume_mode=True but no checkpoint exists, fall back to fresh start.
    has_checkpoint = _has_checkpoint(task_id)
    suggest_continue = resume_mode and has_checkpoint

    read_files = [
        "docs/canonical/45-HYBRID-SPEC-FLOW-AND-RULES.md",
        str(requirements_path.relative_to(PROJECT_ROOT)),
        str(design_path.relative_to(PROJECT_ROOT)),
        str(source.plan_path.relative_to(PROJECT_ROOT)),
        str(source.todo_path.relative_to(PROJECT_ROOT)),
        str(handoff_path.relative_to(PROJECT_ROOT)),
        str(objective_state_path.relative_to(PROJECT_ROOT)),
    ]

    lines = [
        f"Objective: {source.objective_slug}",
        f"Task: {task_id} — {task['title']}",
        f"Task status in ledger: {task_status}",
        "Read these files first and do not improvise outside them:",
    ]
    lines.extend(f"{idx}. {path}" for idx, path in enumerate(read_files, start=1))
    lines.extend(
        [
            "",
            "Rules:",
            "- Do not manually edit todo.md, HANDOFF-CURRENT.md, task-progress.json, or execution-state.json.",
            "- The complete-task handler is the only valid writer for progress state.",
            "- Do not start or commit a later task until this task is completed in execution-state.json.",
            "",
            "First commands:",
            f"- python3 .claude/commands/mm/discover-contract-check.py --objective {source.objective_slug}",
            "- python3 .claude/commands/mm/complete-task-handler.py --status",
        ]
    )

    if suggest_continue:
        lines.append(f"- /mm:continue-task {task_id}")
    else:
        lines.append(f"- /mm:complete-task {task_id}")

    if validation_commands:
        lines.extend(["", "Validation commands for this task:"])
        lines.extend(f"- {command}" for command in validation_commands)

    lines.extend(
        [
            "",
            "Before acting, confirm:",
            "1. the exact ledger status of this task",
            "2. the source-of-truth file for progress",
            "3. whether the task is blocked or ready",
            "4. the next handler command you will run",
        ]
    )
    return "\n".join(lines)


# ============================================================================
# Permission Detection
# ============================================================================


def detect_required_permissions(
    _task_id: str, pending_subtasks: list[dict[str, Any]]
) -> list[str]:
    """Detect required tool permissions based on subtask descriptions.

    Args:
        _task_id: Task identifier (unused, for future extensions).
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


def validate_previous_tasks_complete(task_id: str, source: "TaskSource") -> None:
    """Block execution if any prior task in the objective is not completed.

    Reads execution-state.json and the ordered task list from tasks.md.
    Exits with error if a preceding task is pending or in_progress.
    """
    all_task_ids = get_task_ids_from_plan(source.plan_path)
    if task_id not in all_task_ids:
        return  # Unknown ordering — skip validation

    current_index = all_task_ids.index(task_id)
    if current_index == 0:
        return  # First task — nothing precedes it

    objective_state = load_objective_state(objective_slug=source.objective_slug)
    if not objective_state:
        return  # No state yet — allow first run

    tasks_state = objective_state.get("tasks", {})
    blocked = False
    for prior_id in all_task_ids[:current_index]:
        prior_status = tasks_state.get(prior_id, {}).get("status", "pending")
        if prior_status != "completed":
            mm_error(
                f"Cannot start {task_id}: {prior_id} is '{prior_status}' — complete it first."
            )
            mm_error(f"Run: /mm:complete-task {prior_id}")
            blocked = True

    if blocked:
        sys.exit(1)


def start_task(task_id: str) -> None:
    """Start or resume a task.

    Args:
        task_id: Task identifier (e.g., "D1").
    """
    mm_info(f"Starting task {task_id}")
    ensure_runtime_can_start_task(task_id)

    source = resolve_task_source(task_id)
    mm_info(
        f"Planning source: {source.mode} ({source.plan_path.relative_to(PROJECT_ROOT)})"
    )
    validate_previous_tasks_complete(task_id, source)
    sync_objective_todo_from_state(task_id)

    # Read task and subtasks
    task = read_task_from_plan(task_id)
    subtasks = get_execution_subtasks(task_id)

    mm_task(task_id, task["title"])
    mm_model_brief(build_model_brief(task_id))

    # Show all subtasks with status
    for st in subtasks:
        status = "[x]" if st["completed"] else "[ ]"
        mm_subtask(st["id"], status, st["description"])

    # Git commits are informative only in the objective flow; they are not the
    # source of truth for completion.
    git_completed = get_git_commits_for_task(task_id)
    mm_git(len(git_completed), len(subtasks), sorted(git_completed))

    # Filter pending subtasks from durable execution state.
    pending_subtasks = [st for st in subtasks if not st["completed"]]

    if not pending_subtasks:
        mm_status("TASK COMPLETE - all subtasks completed in durable state")
        sync_objective_todo_from_state(task_id)
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
    runtime_state = init_runtime_state(task_id, subtasks, source)
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

    ensure_runtime_can_start_task(task_id)
    state = json.loads(RUNTIME_STATE_PATH.read_text())

    if state.get("task_id") != task_id:
        mm_error(f"Runtime state is for task {state.get('task_id')}, not {task_id}")
        return

    sync_objective_todo_from_state(task_id)
    mm_task(task_id, read_task_from_plan(task_id)["title"])
    mm_model_brief(build_model_brief(task_id, resume_mode=True))

    mm_info(f"Previous session: {state['session_id']}")
    mm_info(f"Last checkpoint: {state.get('last_checkpoint', 'none')}")

    # Detectar subtareas colgadas en in_progress > 1 hora
    stale_subtasks = []
    stale_threshold_hours = 1

    for sid, st in state["subtasks"].items():
        if st.get("status") == "in_progress" and st.get("started_at"):
            try:
                started = datetime.fromisoformat(st["started_at"])
                hours_since = (datetime.now() - started).total_seconds() / 3600
                if hours_since > stale_threshold_hours:
                    stale_subtasks.append((sid, hours_since))
            except (ValueError, TypeError):
                pass

    if stale_subtasks:
        mm_error("=" * 60)
        mm_error("⚠️  SUBTAREAS COLGADAS DETECTADAS")
        mm_error("=" * 60)
        for sid, hours in stale_subtasks:
            mm_error(f"  {sid}: lleva {hours:.1f}h en in_progress")
        mm_error("")
        mm_error("Esto indica que el agente se detuvo inesperadamente.")
        mm_error("")
        mm_error("Opciones:")
        mm_error(
            "  1. Continuar normalmente (se reintentarán desde el último checkpoint)"
        )
        mm_error(f"  2. Resetear a pending: /mm:complete-task {task_id} --reset-stale")
        mm_error("")
        mm_status("Verificá todo.md y task-progress.json antes de continuar")

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
        "planning_mode": state.get("source_mode", "objective"),
        "objective_slug": state.get("objective_slug"),
        "plan_path": state.get("plan_path"),
        "todo_path": state.get("todo_path"),
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
    """Legacy no-op retained only for backward compatibility.

    Objective-flow completion must come from handler-managed subtask checkpoints,
    never from bulk checkbox mutation or git-commit inference.
    """
    mm_error(
        f"mark_all_complete({task_id}) is deprecated in the objective flow. Use --mark-done per subtask."
    )


def show_status() -> None:
    """Show status of all tasks."""
    mm_info("Task Status Overview")
    changes_dir = PROJECT_ROOT / ".mm-flow" / "planning" / "changes"
    if not changes_dir.exists():
        mm_error("No objective packages found under .mm-flow/planning/changes")
        return

    for objective_dir in sorted(changes_dir.iterdir()):
        if not objective_dir.is_dir():
            continue
        tasks_path = objective_dir / "tasks.md"
        todo_path = ensure_objective_todo(objective_dir, objective_dir.name)
        if not tasks_path.exists() or not todo_path.exists():
            continue
        print(f"\n  [{objective_dir.name}]", flush=True)
        objective_state = load_objective_state(objective_slug=objective_dir.name)
        if objective_state and objective_state.get("tasks"):
            first_task_ids = get_task_ids_from_plan(tasks_path)
            if first_task_ids:
                sync_objective_todo_from_state(first_task_ids[0])
        objective_content = tasks_path.read_text(encoding="utf-8")
        for match in re.finditer(
            r"^## ([A-Z]{1,4}\d+):([^\n]+)$", objective_content, re.MULTILINE
        ):
            task_id = match.group(1)
            title = match.group(2).strip()
            durable_status = get_objective_task_status(task_id)
            if durable_status == "completed":
                checkbox_state = "x"
            elif durable_status == "in_progress":
                checkbox_state = "~"
            else:
                checkbox_state = " "

            objective_state = load_objective_state(task_id=task_id)
            task_entry = (
                objective_state.get("tasks", {}).get(task_id, {})
                if objective_state
                else {}
            )
            subtask_entries = task_entry.get("subtasks", {})
            total = len(subtask_entries) or len(read_subtasks_from_todo(task_id))
            completed = sum(
                1
                for subtask in subtask_entries.values()
                if subtask.get("status") == "completed"
            )
            if not subtask_entries:
                subtasks = read_subtasks_from_todo(task_id)
                completed = sum(1 for st in subtasks if st["completed"])
                total = len(subtasks)
            if checkbox_state == "x":
                status = "✅"
            elif checkbox_state == "~":
                status = f"[~] {completed}/{total}"
            else:
                status = f"[ ] {completed}/{total}"
            sync_suffix = ""
            if RUNTIME_STATE_PATH.exists():
                try:
                    state = json.loads(RUNTIME_STATE_PATH.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError):
                    state = {}
                if state.get("task_id") == task_id:
                    issues = audit_task_consistency(task_id)
                    if issues:
                        sync_suffix = f" ⚠ sync:{len(issues)}"
            print(f"    {task_id} {status}: {title}{sync_suffix}", flush=True)


def reset_stale_subtasks(task_id: str) -> None:
    """Reset stale in_progress subtasks to pending.

    Finds subtasks in in_progress > 1 hour and resets them to pending,
    incrementing retries counter.

    Args:
        task_id: Task identifier (e.g., "B2").
    """
    if not RUNTIME_STATE_PATH.exists():
        mm_error("No runtime state found")
        return

    try:
        state = json.loads(RUNTIME_STATE_PATH.read_text())
    except (json.JSONDecodeError, OSError) as e:
        mm_error(f"Failed to read runtime state: {e}")
        return

    if state.get("task_id") != task_id:
        mm_error(f"Runtime state is for task {state.get('task_id')}, not {task_id}")
        return

    stale_threshold = 1 * 60 * 60  # 1 hora en segundos
    reset_count = 0

    for sid, st in state["subtasks"].items():
        if st.get("status") == "in_progress" and st.get("started_at"):
            try:
                started = datetime.fromisoformat(st["started_at"])
                seconds_since = (datetime.now() - started).total_seconds()
                if seconds_since > stale_threshold:
                    # Reset to pending
                    state["subtasks"][sid]["status"] = "pending"
                    state["subtasks"][sid]["started_at"] = None
                    state["subtasks"][sid]["retries"] = st.get("retries", 0) + 1
                    reset_count += 1
                    mm_info(
                        f"Reset {sid} to pending (retry #{state['subtasks'][sid]['retries']})"
                    )
            except (ValueError, TypeError) as e:
                mm_error(f"Error processing {sid}: {e}")

    if reset_count > 0:
        state["last_checkpoint"] = None
        try:
            RUNTIME_STATE_PATH.write_text(json.dumps(state, indent=2))
        except OSError as e:
            mm_error(f"Failed to write runtime state: {e}")
            return
        mm_info(f"Reset {reset_count} stale subtask(s)")
        mm_info(f"Usá /mm:complete-task {task_id} --continue para reanudar")
    else:
        mm_info("No stale subtasks found (all in_progress < 1 hour)")


def mark_done(subtask_id: str) -> None:
    """Mark a single subtask as complete and propagate to parent.

    This is the canonical way for task-executor to mark subtasks done.
    It calls update_subtask_status() which internally triggers
    propagate_parent_completion() so todo.md is never edited directly.

    Args:
        subtask_id: Subtask ID to mark done (e.g., "B1.09").
    """
    subtask_id = subtask_id.upper()

    # Validate that task-progress.json exists and contains this subtask
    if not RUNTIME_STATE_PATH.exists():
        mm_error(f"No runtime state found at {RUNTIME_STATE_PATH}")
        mm_error("Run /mm:complete-task <TASK_ID> first to initialize state")
        sys.exit(1)

    try:
        state = json.loads(RUNTIME_STATE_PATH.read_text())
    except (json.JSONDecodeError, OSError) as e:
        mm_error(f"Failed to read task-progress.json: {e}")
        sys.exit(1)

    if subtask_id not in state.get("subtasks", {}):
        mm_error(f"Subtask {subtask_id} not found in task-progress.json")
        mm_error(f"Known subtasks: {sorted(state.get('subtasks', {}).keys())}")
        sys.exit(1)

    current_status = state["subtasks"][subtask_id].get("status", "unknown")

    if current_status == "completed":
        mm_info(f"{subtask_id} is already complete — ensuring todo.md is synced")
        sync_subtask_checkbox(subtask_id, "x")
        # Still propagate in case parent wasn't updated (idempotent)
        if "." in subtask_id:
            parent_id = subtask_id.rsplit(".", 1)[0]
            try:
                propagate_parent_completion(parent_id)
            except Exception as e:
                mm_error(f"Propagation failed: {e}")
            sync_objective_handoff(parent_id)
        return

    # Mark as complete — propagation happens inside update_subtask_status()
    try:
        update_subtask_status(subtask_id, "completed")
    except Exception as e:
        mm_error(f"Failed to mark {subtask_id} as complete: {e}")
        sys.exit(1)

    mm_info(f"Marked {subtask_id} as complete")
    if "." in subtask_id:
        sync_objective_handoff(subtask_id.rsplit(".", 1)[0])

    # Re-read state to report parent propagation result
    if RUNTIME_STATE_PATH.exists():
        try:
            updated_state = json.loads(RUNTIME_STATE_PATH.read_text())
            if "." in subtask_id:
                parent_id = subtask_id.rsplit(".", 1)[0]
                _, todo_path = get_active_paths(subtask_id)
                if todo_path.exists():
                    todo_content = todo_path.read_text(encoding="utf-8")
                    parent_done = re.search(
                        rf"^-\s\[x\]\s+{re.escape(parent_id)}:",
                        todo_content,
                        re.MULTILINE,
                    )
                    if parent_done:
                        mm_info(
                            f"Parent {parent_id} propagated to [x] (all subtasks done)"
                        )
                    else:
                        siblings = {
                            sid: sdata
                            for sid, sdata in updated_state.get("subtasks", {}).items()
                            if sid.startswith(parent_id + ".")
                        }
                        done_count = sum(
                            1
                            for s in siblings.values()
                            if s.get("status") == "completed"
                        )
                        mm_info(
                            f"Parent {parent_id} not yet complete "
                            f"({done_count}/{len(siblings)} siblings done)"
                        )
        except (json.JSONDecodeError, OSError, ValueError):
            pass  # Best-effort reporting — don't fail the command

    if "." in subtask_id:
        trigger_completion_notification(subtask_id.rsplit(".", 1)[0])


def mark_in_progress(subtask_id: str) -> None:
    """Mark a single subtask as in-progress and propagate [~] to parent.

    Called by task-executor at the START of each subtask so the parent
    immediately shows [~] in todo.md, giving real-time visibility.

    Args:
        subtask_id: Subtask ID to mark in-progress (e.g., "B1.01").
    """
    subtask_id = subtask_id.upper()

    if not RUNTIME_STATE_PATH.exists():
        mm_error(f"No runtime state found at {RUNTIME_STATE_PATH}")
        mm_error("Run /mm:complete-task <TASK_ID> first to initialize state")
        sys.exit(1)

    try:
        state = json.loads(RUNTIME_STATE_PATH.read_text())
    except (json.JSONDecodeError, OSError) as e:
        mm_error(f"Failed to read task-progress.json: {e}")
        sys.exit(1)

    if subtask_id not in state.get("subtasks", {}):
        mm_error(f"Subtask {subtask_id} not found in task-progress.json")
        mm_error(f"Known subtasks: {sorted(state.get('subtasks', {}).keys())}")
        sys.exit(1)

    current_status = state["subtasks"][subtask_id].get("status", "unknown")
    if current_status in ("completed",):
        mm_info(f"{subtask_id} is already complete — skipping in_progress mark")
        return

    try:
        update_subtask_status(subtask_id, "in_progress")
    except Exception as e:
        mm_error(f"Failed to mark {subtask_id} as in_progress: {e}")
        sys.exit(1)

    mm_info(f"Marked {subtask_id} as in_progress")
    if "." in subtask_id:
        sync_objective_handoff(subtask_id.rsplit(".", 1)[0])


def main() -> None:
    """Main entry point."""
    help_flags = {"-h", "--help", "help"}

    if len(sys.argv) < 2:
        print(
            "Usage: mm-complete-task <TASK_ID> [--continue] [--status] [--reset-stale] [--reconcile]",
            flush=True,
        )
        print("       mm-complete-task --status  # Show all tasks", flush=True)
        print(
            "       mm-complete-task --mark-done <SUBTASK_ID>       # Mark subtask complete",
            flush=True,
        )
        print(
            "       mm-complete-task --mark-in-progress <SUBTASK_ID>  # Mark subtask started",
            flush=True,
        )
        print(
            "       mm-complete-task --reconcile <TASK_ID>  # Repair todo/handoff from runtime truth",
            flush=True,
        )
        print(
            "       mm-complete-task --brief <TASK_ID>  # Print a concise model handoff brief",
            flush=True,
        )
        sys.exit(1)

    if sys.argv[1] in help_flags:
        print(
            "Usage: mm-complete-task <TASK_ID> [--continue] [--status] [--reset-stale] [--reconcile]",
            flush=True,
        )
        print("       mm-complete-task --status  # Show all tasks", flush=True)
        print(
            "       mm-complete-task --mark-done <SUBTASK_ID>       # Mark subtask complete",
            flush=True,
        )
        print(
            "       mm-complete-task --mark-in-progress <SUBTASK_ID>  # Mark subtask started",
            flush=True,
        )
        print(
            "       mm-complete-task --reconcile <TASK_ID>  # Repair todo/handoff from runtime truth",
            flush=True,
        )
        print(
            "       mm-complete-task --brief <TASK_ID>  # Print a concise model handoff brief",
            flush=True,
        )
        return

    # Status mode
    if sys.argv[1] == "--status":
        show_status()
        return

    # Mark-in-progress mode: --mark-in-progress <subtask_id>
    if sys.argv[1] == "--mark-in-progress":
        if len(sys.argv) < 3:
            mm_error("Usage: mm-complete-task --mark-in-progress <SUBTASK_ID>")
            mm_error("Example: mm-complete-task --mark-in-progress B1.01")
            sys.exit(1)
        mark_in_progress(sys.argv[2])
        return

    # Mark-done mode: --mark-done <subtask_id>
    if sys.argv[1] == "--mark-done":
        if len(sys.argv) < 3:
            mm_error("Usage: mm-complete-task --mark-done <SUBTASK_ID>")
            mm_error("Example: mm-complete-task --mark-done B1.09")
            sys.exit(1)
        mark_done(sys.argv[2])
        return

    if sys.argv[1] == "--reconcile":
        if len(sys.argv) < 3:
            mm_error("Usage: mm-complete-task --reconcile <TASK_ID>")
            mm_error("Example: mm-complete-task --reconcile PS1")
            sys.exit(1)
        task_id = sys.argv[2].upper()
        reconcile_artifacts_from_runtime(task_id)
        issues = audit_task_consistency(task_id)
        if issues:
            for issue in issues:
                mm_error(f"SYNC: {issue}")
            sys.exit(1)
        mm_status(f"RECONCILED {task_id}")
        return

    if sys.argv[1] == "--brief":
        if len(sys.argv) < 3:
            mm_error("Usage: mm-complete-task --brief <TASK_ID>")
            mm_error("Example: mm-complete-task --brief AV2")
            sys.exit(1)
        task_id = sys.argv[2].upper()
        mm_model_brief(build_model_brief(task_id))
        return

    # Reset stale mode
    if "--reset-stale" in sys.argv:
        if len(sys.argv) < 3:
            mm_error("Usage: mm-complete-task <TASK_ID> --reset-stale")
            sys.exit(1)
        task_id = sys.argv[1].upper()
        reset_stale_subtasks(task_id)
        return

    task_id = sys.argv[1].upper()
    resume_mode = "--continue" in sys.argv

    if resume_mode:
        resume_task(task_id)
    else:
        start_task(task_id)


if __name__ == "__main__":
    main()
