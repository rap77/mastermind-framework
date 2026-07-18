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
import os
import re
import subprocess
import sys
import fcntl
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from planning_paths import get_planning_dir, planning_relpath

# Configure logging
# NOTE: This CLI tool uses emit() instead of logger for structured output.
# The handler must emit machine-parseable messages (LAUNCH:, PAYLOAD:, STATUS:)
# that the calling command can parse. Logger output doesn't guarantee this format.
logging.basicConfig(
    level=logging.INFO,
    format="[mm] %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def emit(
    *parts: object,
    sep: str = " ",
    end: str = "\n",
    file: object | None = None,
    flush: bool = True,
) -> None:
    """Write a single structured line to stdout or stderr."""
    stream = sys.stderr if file is sys.stderr else sys.stdout
    stream.write(sep.join(str(part) for part in parts) + end)
    if flush:
        stream.flush()


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


def _find_objective_canonical_doc(objective_slug: str) -> Path | None:
    """Find the main canonical doc for an objective if one exists."""
    canonical_dir = PROJECT_ROOT / "docs" / "canonical"
    if not canonical_dir.exists():
        return None

    base_slug = re.sub(r"[-_]?v\\d+$", "", objective_slug.lower())
    slug_variants = [objective_slug.lower(), base_slug]

    for path in canonical_dir.glob("*.md"):
        path_name = path.name.lower()
        if any(
            slug_variant and slug_variant in path_name for slug_variant in slug_variants
        ):
            return path

    wildcard_variants = [slug.replace("-", "*") for slug in slug_variants if slug]
    for pattern in wildcard_variants:
        matches = sorted(canonical_dir.glob(f"*{pattern}*.md"))
        if matches:
            return matches[0]

    return None


def _preferred_command_dir() -> Path | None:
    """Return the local command adapter/canonical dir if the project has one."""
    claude_dir = PROJECT_ROOT / ".claude" / "commands" / "mm"
    if claude_dir.exists():
        return claude_dir
    mm_flow_dir = PROJECT_ROOT / ".mm-flow" / "commands" / "mm"
    if mm_flow_dir.exists():
        return mm_flow_dir
    return None


def _preferred_skill_dir() -> Path | None:
    """Return the local skill adapter/canonical dir if the project has one."""
    claude_dir = PROJECT_ROOT / ".claude" / "skills" / "mm"
    if claude_dir.exists():
        return claude_dir
    mm_flow_dir = PROJECT_ROOT / ".mm-flow" / "skills" / "mm"
    if mm_flow_dir.exists():
        return mm_flow_dir
    return None


def _critical_flow_paths() -> list[tuple[str, Path]]:
    """Return handler/skill paths that must exist before launching execution."""
    command_dir = _preferred_command_dir()
    skill_dir = _preferred_skill_dir()
    paths: list[tuple[str, Path]] = []
    if command_dir is not None:
        paths.extend(
            [
                ("complete-task handler", command_dir / "complete-task-handler.py"),
                ("update-todo-times handler", command_dir / "update-todo-times.py"),
                ("safe-commit handler", command_dir / "safe-commit-handler.py"),
            ]
        )
    if skill_dir is not None:
        paths.append(("safe-commit skill", skill_dir / "safe-commit" / "SKILL.md"))
    return paths


def _writable_flow_paths(
    task_id: str, objective_slug: str | None = None
) -> list[tuple[str, Path]]:
    """Return planning files/directories that execution must be able to write."""
    state_path = get_objective_state_path(
        objective_slug=objective_slug, task_id=None if objective_slug else task_id
    )
    _, todo_path = get_active_paths(task_id, objective_slug=objective_slug)
    handoff_path = get_objective_handoff_path(task_id, objective_slug=objective_slug)
    return [
        ("runtime state directory", RUNTIME_STATE_PATH.parent),
        ("runtime state file parent", RUNTIME_STATE_PATH.parent),
        ("objective todo", todo_path),
        (
            "objective handoff",
            handoff_path if handoff_path is not None else todo_path.parent,
        ),
        (
            "objective execution-state",
            state_path if state_path is not None else todo_path.parent,
        ),
    ]


def validate_execution_prerequisites(
    task_id: str, objective_slug: str | None = None
) -> list[str]:
    """Validate that critical handlers/skills and planning files are available.

    Returns:
        List of fatal issues. Empty list means execution may proceed.
    """
    issues: list[str] = []

    for label, path in _critical_flow_paths():
        if not path.exists():
            issues.append(f"missing {label}: {path.relative_to(PROJECT_ROOT)}")

    for label, path in _writable_flow_paths(task_id, objective_slug=objective_slug):
        target = path if path.is_dir() else path.parent
        if not target.exists():
            issues.append(f"missing writable target for {label}: {target}")
            continue
        if not os.access(target, os.W_OK):
            issues.append(f"{label} is not writable: {target}")

    return issues


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
PLANNING_DIR = get_planning_dir(PROJECT_ROOT)
PLANNING_LABEL = planning_relpath(PROJECT_ROOT)
RUNTIME_STATE_PATH = PLANNING_DIR / "task-progress.json"
OBJECTIVE_STATE_FILENAME = "execution-state.json"
ALLOWED_SUBTASK_STATUSES = {
    "pending",
    "in_progress",
    "completed",
    "failed",
    "skipped",
}


@dataclass
class TaskSource:
    """Source files used to execute a task."""

    mode: str
    plan_path: Path
    todo_path: Path
    objective_slug: str | None = None


@dataclass
class TaskRef:
    """Normalized task reference with optional objective scope."""

    task_id: str
    objective_slug: str | None = None


def _resolve_notify_script_path() -> Path | None:
    """Resolve the completion notifier with preference for the neutral core path."""
    candidates = [
        PROJECT_ROOT / ".mm-flow" / "commands" / "mm" / "notify-complete.py",
        Path(__file__).resolve().parent / "notify-complete.py",
        PROJECT_ROOT / ".claude" / "commands" / "mm" / "notify-complete.py",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


# ============================================================================
# Output Helpers - Structured, machine-parseable
# ============================================================================


def mm_info(msg: str) -> None:
    """Print INFO message."""
    sys.stdout.write(f"INFO: {msg}\n")
    sys.stdout.flush()


def mm_task(task_id: str, title: str) -> None:
    """Print task header."""
    sys.stdout.write(f"TASK: {task_id}\n")
    sys.stdout.write(f"TITLE: {title}\n")
    sys.stdout.flush()


def mm_subtask(subtask_id: str, status: str, description: str = "") -> None:
    """Print subtask line."""
    desc = f" ({description})" if description else ""
    sys.stdout.write(f"SUBTASK: {subtask_id} {status}{desc}\n")
    sys.stdout.flush()


def mm_git(count: int, total: int, completed: list[str]) -> None:
    """Print informational Git history without changing execution state."""
    completed_str = ",".join(completed) if completed else "none"
    sys.stdout.write(
        f"GIT_INFO: {count}/{total} subtasks have commits [{completed_str}] (informational only)\n"
    )
    sys.stdout.flush()


def mm_pending(count: int) -> None:
    """Print pending count."""
    sys.stdout.write(f"PENDING: {count} subtasks to execute\n")
    sys.stdout.flush()


def mm_launch(task_id: str, objective_slug: str | None = None) -> None:
    """Print launch command."""
    payload = get_task_payload(task_id, objective_slug=objective_slug)
    sys.stdout.write("LAUNCH: task-executor\n")
    sys.stdout.write(f"PAYLOAD: {json.dumps(payload)}\n")
    sys.stdout.flush()


def _open_db_session(_task_id: str, _pending_count: int) -> str | None:
    """Open a dev session in the DB. Returns session UUID or None if DB unavailable."""
    try:
        sys.path.insert(0, str(PLANNING_DIR.parent / ".claude" / "commands" / "mm"))
        from db_client import MasterMindDB

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


def _mm_launch_with_db(
    task_id: str, db_session_id: str | None, objective_slug: str | None = None
) -> None:
    """Print launch command including db_session_id in payload."""
    payload = get_task_payload(task_id, objective_slug=objective_slug)
    if db_session_id:
        payload["db_session_id"] = db_session_id
    emit("LAUNCH: task-executor", flush=True)
    emit(f"PAYLOAD: {json.dumps(payload)}", flush=True)


def mm_status(msg: str) -> None:
    """Print status message."""
    emit(f"STATUS: {msg}", flush=True)


def mm_error(msg: str) -> None:
    """Print error message."""
    emit(f"ERROR: {msg}", flush=True, file=sys.stderr)


def mm_model_brief(brief: str) -> None:
    """Print a model-resume brief."""
    emit("MODEL_BRIEF_START", flush=True)
    emit(brief.rstrip(), flush=True)
    emit("MODEL_BRIEF_END", flush=True)


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


def objective_artifact_path(objective_dir: Path, name: str) -> Path:
    """Return an objective artifact path only when it cannot escape its scope."""
    if name not in {
        "tasks.md",
        "todo.md",
        OBJECTIVE_STATE_FILENAME,
        "HANDOFF-CURRENT.md",
    }:
        raise ValueError(f"Unsupported objective artifact: {name}")
    objective_root = objective_dir.resolve()
    path = objective_dir / name
    try:
        path.resolve(strict=False).relative_to(objective_root)
    except (OSError, RuntimeError, ValueError) as exc:
        raise ValueError(
            f"Artifact `{name}` must stay within objective `{objective_dir.name}`"
        ) from exc
    return path


def _split_objective_task_ref(raw: str) -> TaskRef:
    """Parse `objective/task` or bare `task` references."""
    raw = raw.strip()
    if "/" not in raw:
        return TaskRef(task_id=raw.upper())
    objective_slug, task_id = raw.rsplit("/", 1)
    objective_slug = objective_slug.strip().lower()
    get_objective_dir(objective_slug)
    return TaskRef(task_id=task_id.upper(), objective_slug=objective_slug)


def _planned_subtasks_from_plan(plan_path: Path, task_id: str) -> list[dict[str, Any]]:
    """Return explicit plan topology or scoped legacy todo topology."""
    if not plan_path.exists():
        raise ValueError(f"Plan topology file does not exist: {plan_path}")
    content = plan_path.read_text(encoding="utf-8")
    task_matches = list(
        re.finditer(
            rf"^##\s+{re.escape(task_id)}:.*?(?=^##\s+[A-Z]{{1,4}}\d+:|\Z)",
            content,
            re.MULTILINE | re.DOTALL,
        )
    )
    if len(task_matches) != 1:
        raise ValueError(f"Plan topology for {task_id} must have one root task")
    explicit_matches = list(
        re.finditer(
            r"^### Execution Subtasks\n(?P<body>.*?)(?=^### |\Z)",
            task_matches[0].group(0),
            re.MULTILINE | re.DOTALL,
        )
    )
    if len(explicit_matches) > 1:
        raise ValueError(
            f"Plan topology for {task_id} requires one Execution Subtasks block"
        )
    todo_path = plan_path.with_name("todo.md")
    todo_subtasks = _legacy_subtasks_from_todo(todo_path, task_id)
    if not explicit_matches:
        if todo_subtasks:
            return todo_subtasks
        raise ValueError(
            f"Topology for {task_id} is only a scaffold; refine tasks.md or rerun discovery with task-specific execution subtasks"
        )
    explicit: list[dict[str, Any]] = []
    seen: set[str] = set()
    for line in explicit_matches[0].group("body").splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(
            rf"-\s+(?P<id>{re.escape(task_id)}\.\d+):\s*(?P<description>\S.*)",
            line,
        )
        if match is None:
            raise ValueError(f"Malformed plan topology for {task_id}: {line}")
        subtask_id = match.group("id")
        if subtask_id in seen:
            raise ValueError(f"Duplicate subtask ID in plan topology: {subtask_id}")
        seen.add(subtask_id)
        explicit.append(
            {
                "id": subtask_id,
                "description": match.group("description").strip(),
                "completed": False,
            }
        )
    if not explicit:
        raise ValueError(f"Plan topology for {task_id} has no execution subtasks")
    if todo_subtasks and [
        (entry["id"], entry["description"]) for entry in todo_subtasks
    ] != [(entry["id"], entry["description"]) for entry in explicit]:
        raise ValueError(f"Plan and todo topology conflict for {task_id}")
    return explicit


def _legacy_subtasks_from_todo(todo_path: Path, task_id: str) -> list[dict[str, Any]]:
    """Return explicit child IDs scoped under one legacy todo root task."""
    if not todo_path.exists():
        return []
    content = todo_path.read_text(encoding="utf-8")
    if len(re.findall(r"^## Execution Checklist$", content, re.MULTILINE)) > 1:
        raise ValueError(
            "Objective todo contains duplicate Execution Checklist sections"
        )
    if "<!-- topology-source: tasks.md -->" in content:
        return []
    parent_matches = list(
        re.finditer(
            rf"^[-]\s\[[ x~]\]\s+{re.escape(task_id)}\s*(?::|—|-).*?$",
            content,
            re.MULTILINE,
        )
    )
    if len(parent_matches) > 1:
        raise ValueError(f"Todo topology contains duplicate root task {task_id}")
    if not parent_matches:
        return []
    start = parent_matches[0].end()
    next_parent = re.search(
        r"^-\s\[[ x~]\]\s+[A-Z]{1,4}\d+\s*(?::|—|-)",
        content[start:],
        re.MULTILINE,
    )
    body = (
        content[start : start + next_parent.start()] if next_parent else content[start:]
    )
    explicit: list[dict[str, Any]] = []
    seen: set[str] = set()
    child_pattern = re.compile(
        rf"^\s{{2,}}-\s\[[ x~]\]\s+(?P<id>{re.escape(task_id)}\.\d+):\s*(?P<description>\S.*)$"
    )
    for line in body.splitlines():
        if not line.strip():
            continue
        match = child_pattern.fullmatch(line)
        if match is None:
            if re.match(r"^\s{2,}-\s*\[", line) or re.match(
                rf"^\s{{2,}}-\s+{re.escape(task_id)}\.", line
            ):
                raise ValueError(f"Malformed todo topology for {task_id}: {line}")
            continue
        subtask_id = match.group("id")
        if subtask_id in seen:
            raise ValueError(f"Duplicate subtask ID in todo topology: {subtask_id}")
        seen.add(subtask_id)
        description = match.group("description").strip()
        generic_descriptions = {
            f"Review requirements and design context for {task_id}",
            f"Implement {task_id} end-to-end",
            f"Run validation for {task_id}",
        }
        if description in generic_descriptions:
            raise ValueError(
                f"Legacy todo topology for {task_id} uses generic placeholders; refine the objective package"
            )
        explicit.append(
            {
                "id": subtask_id,
                "description": description,
                "completed": False,
            }
        )
    return explicit


def ensure_objective_todo(objective_dir: Path, task_id: str) -> Path:
    """Ensure an objective-local todo.md exists for complete-task execution."""
    todo_path = objective_artifact_path(objective_dir, "todo.md")
    tasks_path = objective_artifact_path(objective_dir, "tasks.md")
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
        "<!-- topology-source: tasks.md -->",
        "",
        "## Execution Checklist",
        "",
    ]
    for current_task_id, title in task_matches:
        lines.append(f"- [ ] {current_task_id}: {title.strip()}")
        for subtask in _planned_subtasks_from_plan(tasks_path, current_task_id):
            lines.append(f"  - [ ] {subtask['id']}: {subtask['description']}")
        lines.append("")
    todo_path.write_text("\n".join(lines), encoding="utf-8")
    return todo_path


def get_objective_dir(objective_slug: str) -> Path:
    """Return the active planning directory for an objective slug."""
    if (
        not objective_slug
        or objective_slug in {".", ".."}
        or not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", objective_slug)
        or Path(objective_slug).is_absolute()
        or Path(objective_slug).name != objective_slug
    ):
        raise ValueError(
            "Objective slug must be a safe single path component "
            "using lowercase letters, numbers, dots, underscores, or hyphens"
        )
    changes_dir = (PLANNING_DIR / "changes").resolve()
    expected_dir = changes_dir / objective_slug
    try:
        resolved_dir = expected_dir.resolve()
        relative = resolved_dir.relative_to(changes_dir)
    except (OSError, RuntimeError, ValueError) as exc:
        raise ValueError(
            f"Objective `{objective_slug}` must resolve to its canonical directory"
        ) from exc
    if relative.parts != (objective_slug,):
        raise ValueError(
            f"Objective `{objective_slug}` must resolve to its canonical directory"
        )
    return resolved_dir


def runtime_state_matches_active_objective(state: dict[str, Any]) -> bool:
    """Return whether runtime state still points at a real active objective."""

    objective_slug = state.get("objective_slug")
    plan_path = state.get("plan_path")
    todo_path = state.get("todo_path")
    if not isinstance(objective_slug, str) or not objective_slug:
        return False
    try:
        objective_dir = get_objective_dir(objective_slug)
    except ValueError:
        return False
    if not objective_dir.exists():
        return False
    if not isinstance(plan_path, str) or not isinstance(todo_path, str):
        return False
    try:
        canonical_plan = objective_artifact_path(objective_dir, "tasks.md").resolve()
        canonical_todo = objective_artifact_path(objective_dir, "todo.md").resolve()
        resolved_plan = Path(plan_path).resolve()
        resolved_todo = Path(todo_path).resolve()
        resolved_plan.relative_to(objective_dir)
        resolved_todo.relative_to(objective_dir)
    except (OSError, RuntimeError, ValueError):
        return False
    return (
        resolved_plan == canonical_plan
        and resolved_todo == canonical_todo
        and resolved_plan.exists()
        and resolved_todo.exists()
    )


def resolve_task_source(task_id: str, objective_slug: str | None = None) -> TaskSource:
    """Resolve a task from an active objective package."""
    changes_dir = (PLANNING_DIR / "changes").resolve()
    if not changes_dir.exists():
        raise ValueError(
            f"Task {task_id} not found in objective packages under {PLANNING_LABEL}/changes/"
        )

    candidate_dirs = []
    if objective_slug:
        candidate_dir = get_objective_dir(objective_slug)
        if candidate_dir.exists() and candidate_dir.is_dir():
            candidate_dirs = [candidate_dir]
    else:
        candidate_dirs = sorted(
            get_objective_dir(path.name)
            for path in changes_dir.iterdir()
            if path.is_dir()
        )

    matches: list[TaskSource] = []
    for objective_dir in candidate_dirs:
        plan_path = objective_artifact_path(objective_dir, "tasks.md")
        if task_heading_exists(plan_path, task_id):
            matches.append(
                TaskSource(
                    mode="objective",
                    plan_path=plan_path,
                    todo_path=objective_artifact_path(objective_dir, "todo.md"),
                    objective_slug=objective_dir.name,
                )
            )

    if len(matches) == 1:
        return matches[0]

    if len(matches) > 1:
        objective_list = ", ".join(
            sorted(match.objective_slug or "unknown" for match in matches)
        )
        raise ValueError(
            f"Task {task_id} is ambiguous across active objectives: {objective_list}. "
            f"Use <objective>/{task_id}."
        )

    if objective_slug:
        raise ValueError(
            f"Task {task_id} not found under active objective "
            f"{PLANNING_LABEL}/changes/{objective_slug}/"
        )

    raise ValueError(
        f"Task {task_id} not found in objective packages under {PLANNING_LABEL}/changes/"
    )


def get_active_paths(
    task_id: str | None = None, objective_slug: str | None = None
) -> tuple[Path, Path]:
    """Return the active plan/todo paths for the objective flow."""
    if task_id:
        source = resolve_task_source(
            get_root_task_id(task_id), objective_slug=objective_slug
        )
        return source.plan_path, source.todo_path

    state = load_runtime_state()
    if state is not None:
        return Path(state["plan_path"]), Path(state["todo_path"])

    raise ValueError(
        "No active planning source available. Run /mm:discover --existing --objective <name> first."
    )


def load_runtime_state() -> dict[str, Any] | None:
    """Load runtime state only when its persisted structure is valid."""
    if not RUNTIME_STATE_PATH.exists():
        return None
    try:
        state = json.loads(RUNTIME_STATE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(state, dict):
        return None
    if not runtime_state_matches_active_objective(state):
        return None
    task_id = state.get("task_id")
    session_id = state.get("session_id")
    subtasks = state.get("subtasks", {})
    if not isinstance(task_id, str) or not task_id:
        return None
    if not isinstance(session_id, str) or not session_id:
        return None
    if not isinstance(subtasks, dict):
        return None
    if any(
        not isinstance(subtask_id, str) or not _is_valid_subtask_state(subtask)
        for subtask_id, subtask in subtasks.items()
    ):
        return None
    if not _is_valid_timestamp(state.get("started_at")) or not _is_valid_timestamp(
        state.get("resumed_at")
    ):
        return None
    if not _runtime_timestamps_are_compatible(state):
        return None
    return state


def _require_runtime_state() -> dict[str, Any]:
    """Return validated runtime state or raise a controlled validation error."""
    state = load_runtime_state()
    if state is not None:
        return state
    if RUNTIME_STATE_PATH.exists():
        raise ValueError("Runtime state is invalid")
    raise ValueError("No runtime state found")


def _is_valid_timestamp(value: Any) -> bool:
    """Return whether a persisted timestamp is absent or valid ISO datetime text."""
    if value is None:
        return True
    if not isinstance(value, str) or not value.strip() or "T" not in value:
        return False
    try:
        datetime.fromisoformat(value)
    except ValueError:
        return False
    return True


def _runtime_timestamps_are_compatible(state: dict[str, Any]) -> bool:
    """Reject mixed offset-aware and offset-naive runtime timestamps."""
    values = [state.get("started_at"), state.get("resumed_at")]
    for subtask in state.get("subtasks", {}).values():
        if isinstance(subtask, dict):
            values.extend(
                subtask.get(field)
                for field in ("started_at", "completed_at", "updated_at")
            )
    parsed = [
        datetime.fromisoformat(value) for value in values if isinstance(value, str)
    ]
    awareness = {
        value.tzinfo is not None and value.utcoffset() is not None for value in parsed
    }
    return len(awareness) <= 1


def _is_valid_duration(value: Any) -> bool:
    """Return whether a persisted duration is numeric and nonnegative."""
    return (
        isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0
    )


def _is_valid_subtask_state(value: Any) -> bool:
    """Validate scalar fields consumed from a runtime or durable subtask."""
    if not isinstance(value, dict):
        return False
    if value.get("status") not in ALLOWED_SUBTASK_STATUSES:
        return False
    if "description" in value and (
        not isinstance(value["description"], str) or not value["description"]
    ):
        return False
    if any(
        not _is_valid_timestamp(value.get(field))
        for field in ("started_at", "completed_at", "updated_at")
    ):
        return False
    if "duration_seconds" in value and not _is_valid_duration(
        value["duration_seconds"]
    ):
        return False
    if "retries" in value and (
        not isinstance(value["retries"], int)
        or isinstance(value["retries"], bool)
        or value["retries"] < 0
    ):
        return False
    return True


def _is_valid_objective_state(state: Any) -> bool:
    """Return whether a durable objective ledger has valid nested state fields."""
    if not isinstance(state, dict) or not isinstance(state.get("tasks"), dict):
        return False
    planned_objective = state.get("status") == "planned"
    for task_id, task in state["tasks"].items():
        if not isinstance(task_id, str) or not isinstance(task, dict):
            return False
        if "subtasks" not in task:
            depends_on = task.get("depends_on", [])
            if (
                not planned_objective
                or task.get("status") != "pending"
                or not isinstance(depends_on, list)
                or any(
                    not isinstance(dependency, str) or not dependency.strip()
                    for dependency in depends_on
                )
            ):
                return False
            continue
        if (
            not isinstance(task["subtasks"], dict)
            or task.get("status") not in ALLOWED_SUBTASK_STATUSES
            or any(
                not _is_valid_timestamp(task.get(field))
                for field in ("started_at", "completed_at")
            )
        ):
            return False
        if any(
            not isinstance(subtask_id, str) or not _is_valid_subtask_state(subtask)
            for subtask_id, subtask in task["subtasks"].items()
        ):
            return False
    return True


def _has_timing_evidence(value: Any) -> bool:
    """Return whether a runtime timestamp contains non-empty evidence."""
    return isinstance(value, str) and bool(value.strip())


def _now_compatible_with(value: str | None) -> datetime:
    """Return now with timezone awareness matching an ISO timestamp."""
    if not value:
        return datetime.now()
    parsed = datetime.fromisoformat(value)
    return (
        datetime.now(tz=parsed.tzinfo) if parsed.tzinfo is not None else datetime.now()
    )


def runtime_task_complete(state: dict[str, Any]) -> bool:
    """Return True when all subtasks in runtime state are completed."""
    subtasks = state.get("subtasks", {})
    if not subtasks:
        return False
    return all(subtask.get("status") == "completed" for subtask in subtasks.values())


def get_objective_handoff_path(
    task_id: str | None = None, objective_slug: str | None = None
) -> Path | None:
    """Return the active objective handoff path if available."""
    if objective_slug:
        return objective_artifact_path(
            get_objective_dir(objective_slug), "HANDOFF-CURRENT.md"
        )

    if task_id:
        try:
            source = resolve_task_source(get_root_task_id(task_id))
        except ValueError:
            return None
        if source.objective_slug:
            return objective_artifact_path(
                get_objective_dir(source.objective_slug), "HANDOFF-CURRENT.md"
            )

    state = load_runtime_state()
    if state is not None:
        objective_slug = state.get("objective_slug")
        if isinstance(objective_slug, str) and objective_slug:
            return objective_artifact_path(
                get_objective_dir(objective_slug), "HANDOFF-CURRENT.md"
            )

    return None


def get_objective_state_path(
    objective_slug: str | None = None, task_id: str | None = None
) -> Path | None:
    """Return the durable execution-state path for an objective."""
    if objective_slug:
        return objective_artifact_path(
            get_objective_dir(objective_slug), OBJECTIVE_STATE_FILENAME
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
        return None
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        raise ValueError(f"Objective state is invalid: {state_path}")
    if not isinstance(state, dict) or not isinstance(state.get("tasks"), dict):
        raise ValueError(f"Objective state is invalid: {state_path}")
    if not _is_valid_objective_state(state):
        raise ValueError(f"Objective state is invalid: {state_path}")
    if state.get("objective_slug") != state_path.parent.name:
        raise ValueError(f"Objective state is invalid: {state_path}")
    return state


def save_objective_state(state: dict[str, Any]) -> None:
    """Persist objective execution state."""
    objective_slug = state.get("objective_slug")
    state_path = get_objective_state_path(objective_slug=objective_slug)
    if state_path is None:
        raise ValueError("Cannot resolve objective execution-state path")
    try:
        state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"Failed to persist objective execution state: {exc}") from exc


def get_root_task_id(identifier: str) -> str:
    """Return the root task ID for a task or subtask identifier."""
    return identifier.split(".", 1)[0]


def seed_objective_task_state(
    source: TaskSource, task_id: str, subtasks: list[dict[str, Any]]
) -> None:
    """Ensure a durable execution-state entry exists for the active objective task."""
    if not source.objective_slug:
        raise ValueError("Objective slug is required for durable seeding")

    state = load_objective_state(objective_slug=source.objective_slug) or {
        "objective_slug": source.objective_slug,
        "plan_path": str(source.plan_path),
        "todo_path": str(source.todo_path),
        "tasks": {},
        "updated_at": None,
    }
    tasks = state.setdefault("tasks", {})
    if state.get("status") == "planned":
        for root_task_id in get_task_ids_from_plan(source.plan_path):
            planned_subtasks = _planned_subtasks_from_plan(
                source.plan_path, root_task_id
            )
            planned_entry = tasks.setdefault(root_task_id, {"status": "pending"})
            existing_subtasks = planned_entry.get("subtasks", {})
            if not isinstance(existing_subtasks, dict):
                existing_subtasks = {}
            planned_entry["subtasks"] = {
                child["id"]: {
                    "description": child["description"],
                    "status": existing_subtasks.get(child["id"], {}).get(
                        "status", "pending"
                    ),
                    "started_at": existing_subtasks.get(child["id"], {}).get(
                        "started_at"
                    ),
                    "completed_at": existing_subtasks.get(child["id"], {}).get(
                        "completed_at"
                    ),
                    "duration_seconds": existing_subtasks.get(child["id"], {}).get(
                        "duration_seconds", 0
                    ),
                    "updated_at": existing_subtasks.get(child["id"], {}).get(
                        "updated_at"
                    ),
                }
                for child in planned_subtasks
            }
            planned_entry["status"] = _aggregate_parent_status(
                [child["status"] for child in planned_entry["subtasks"].values()]
            )
            planned_entry.setdefault("started_at", None)
            planned_entry.setdefault("completed_at", None)
            planned_entry["plan_path"] = str(source.plan_path)
            planned_entry["todo_path"] = str(source.todo_path)
        state["status"] = "active"
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
    task_entry.setdefault("started_at", None)
    task_entry.setdefault("completed_at", None)

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

    task_entry["status"] = _aggregate_parent_status(
        [entry["status"] for entry in task_entry["subtasks"].values()]
    )
    if task_entry["status"] != "completed":
        task_entry["completed_at"] = None
    state["updated_at"] = datetime.now().isoformat()
    save_objective_state(state)


def get_task_ids_from_plan(plan_path: Path) -> list[str]:
    """Return ordered root task IDs from an objective tasks.md file."""
    if not plan_path.exists():
        raise ValueError(f"Plan topology file does not exist: {plan_path}")
    content = plan_path.read_text(encoding="utf-8")
    task_ids = re.findall(r"^##\s+([A-Z]{1,4}\d+):", content, re.MULTILINE)
    if len(task_ids) != len(set(task_ids)):
        raise ValueError("Plan topology contains duplicate root task IDs")
    for task_id in task_ids:
        _planned_subtasks_from_plan(plan_path, task_id)
    return task_ids


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


def _task_acceptance_block_pattern(task_id: str) -> str:
    """Return a regex that captures the acceptance criteria block for a root task."""
    return (
        rf"(^##\s+{re.escape(task_id)}:.*?"
        r"^### Acceptance Criteria\n)"
        r"(?P<body>.*?)(?=^### |\n## |\Z)"
    )


def _has_exactly_one_acceptance_block(plan_text: str, task_id: str) -> bool:
    """Return whether one root task contains exactly one acceptance section."""
    section = re.search(
        rf"^##\s+{re.escape(task_id)}:.*?(?=^##\s+[A-Z]{{1,4}}\d+:|\Z)",
        plan_text,
        re.MULTILINE | re.DOTALL,
    )
    return (
        section is not None
        and len(
            re.findall(r"^### Acceptance Criteria$", section.group(0), re.MULTILINE)
        )
        == 1
    )


def _acceptance_checkbox_states(body: str) -> list[str] | None:
    """Parse a complete acceptance block or reject malformed criteria."""
    states: list[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped.startswith("-"):
            continue
        match = re.fullmatch(r"-\s*\[([^\]]*)\]\s+.+", stripped)
        if match is None or match.group(1) not in {" ", "x", "~"}:
            return None
        states.append(match.group(1))
    return states or None


def sync_task_acceptance_criteria(
    task_id: str, objective_slug: str | None = None
) -> bool:
    """Project task-level acceptance criteria checkboxes from durable task state.

    The current objective flow treats acceptance at the root-task level: once the
    durable ledger marks a root task as completed, its declared acceptance
    criteria are projected to `[x]`; otherwise they are projected to `[ ]`.
    """
    objective_state = load_objective_state(
        objective_slug=objective_slug, task_id=None if objective_slug else task_id
    )
    if not objective_state:
        return False

    try:
        plan_path, _todo_path = get_active_paths(task_id, objective_slug=objective_slug)
        plan_text = plan_path.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError, ValueError):
        return False

    if not _has_exactly_one_acceptance_block(plan_text, task_id):
        return False

    expected_subtask_ids = {
        subtask["id"] for subtask in _planned_subtasks_from_plan(plan_path, task_id)
    }
    durable_complete = _durable_task_is_complete(
        task_id,
        objective_slug or objective_state["objective_slug"],
        expected_subtask_ids,
    )
    desired_checkbox = "x" if durable_complete else " "
    pattern = _task_acceptance_block_pattern(task_id)
    match = re.search(pattern, plan_text, re.MULTILINE | re.DOTALL)
    if not match:
        return False

    body = match.group("body")
    checkbox_states = _acceptance_checkbox_states(body)
    if checkbox_states is None:
        return False
    updated_body = re.sub(
        r"(^-\s\[)([ x~])(\]\s+)",
        rf"\g<1>{desired_checkbox}\g<3>",
        body,
        flags=re.MULTILINE,
    )
    if updated_body != body:
        updated_plan = (
            plan_text[: match.start("body")]
            + updated_body
            + plan_text[match.end("body") :]
        )
        try:
            plan_path.write_text(updated_plan, encoding="utf-8")
        except OSError as exc:
            mm_error(f"Failed to sync acceptance criteria for {task_id}: {exc}")
            return False

    try:
        persisted_text = plan_path.read_text(encoding="utf-8")
    except OSError:
        return False
    persisted_match = re.search(pattern, persisted_text, re.MULTILINE | re.DOTALL)
    if persisted_match is None:
        return False
    persisted_states = _acceptance_checkbox_states(persisted_match.group("body"))
    return persisted_states is not None and all(
        state == desired_checkbox for state in persisted_states
    )


def task_acceptance_criteria_satisfied(
    task_id: str, objective_slug: str | None = None
) -> bool:
    """Return True when all declared acceptance criteria are marked complete."""
    try:
        plan_path, _todo_path = get_active_paths(task_id, objective_slug=objective_slug)
        plan_text = plan_path.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError, ValueError):
        return False

    if not _has_exactly_one_acceptance_block(plan_text, task_id):
        return False

    match = re.search(
        _task_acceptance_block_pattern(task_id), plan_text, re.MULTILINE | re.DOTALL
    )
    if not match:
        return False

    objective_state = load_objective_state(
        objective_slug=objective_slug, task_id=None if objective_slug else task_id
    )
    if objective_state is None:
        return False
    expected_subtask_ids = {
        subtask["id"] for subtask in _planned_subtasks_from_plan(plan_path, task_id)
    }
    if not _durable_task_is_complete(
        task_id,
        objective_slug or objective_state["objective_slug"],
        expected_subtask_ids,
    ):
        return False
    checkboxes = _acceptance_checkbox_states(match.group("body"))
    return checkboxes is not None and all(checkbox == "x" for checkbox in checkboxes)


def require_verified_acceptance_projection(task_id: str, objective_slug: str) -> None:
    """Project and verify acceptance before reporting durable completion."""
    projected = sync_task_acceptance_criteria(task_id, objective_slug=objective_slug)
    if not projected or not task_acceptance_criteria_satisfied(
        task_id, objective_slug=objective_slug
    ):
        raise ValueError(f"Cannot complete {task_id}: acceptance projection failed")


def get_root_task_statuses(todo_path: Path) -> list[tuple[str, str, str]]:
    """Return ordered root task statuses from todo.md as (task_id, checkbox, title)."""
    if not todo_path.exists():
        return []
    content = todo_path.read_text(encoding="utf-8")
    pattern = re.compile(
        r"^-\s\[(?P<status>[ x~])\]\s+(?P<task_id>[A-Z]{1,4}\d+)\s*(?::|—|-)\s*(?P<title>.+)$",
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


def sync_objective_todo_from_state(
    task_id: str, objective_slug: str | None = None
) -> None:
    """Render exact plan topology and durable status into todo.md."""
    objective_state = load_objective_state(
        objective_slug=objective_slug, task_id=None if objective_slug else task_id
    )
    if not objective_state:
        return

    plan_path, todo_path = get_active_paths(task_id, objective_slug=objective_slug)
    original_content = todo_path.read_text(encoding="utf-8")
    checklist_lines = ["## Execution Checklist", ""]
    for root_id in get_task_ids_from_plan(plan_path):
        task_entry = objective_state.get("tasks", {}).get(root_id, {})
        parent_checkbox = checkbox_for_status(task_entry.get("status", "pending"))
        title = get_task_title_from_plan(plan_path, root_id) or root_id
        checklist_lines.append(f"- [{parent_checkbox}] {root_id}: {title}")
        for planned in _planned_subtasks_from_plan(plan_path, root_id):
            subtask_entry = task_entry.get("subtasks", {}).get(planned["id"], {})
            desired = checkbox_for_status(subtask_entry.get("status", "pending"))
            checklist_lines.append(
                f"  - [{desired}] {planned['id']}: {planned['description']}"
            )
        checklist_lines.append(
            f"  - depends_on: {get_task_dependencies_from_plan(plan_path, root_id)}"
        )
        validation = (
            " | ".join(get_task_validation_commands_from_plan(plan_path, root_id))
            or "not declared"
        )
        checklist_lines.extend([f"  - validation: {validation}", ""])
    checklist = "\n".join(checklist_lines).rstrip() + "\n"
    pattern = re.compile(
        r"^## Execution Checklist\n.*?(?=^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    checklist_matches = list(pattern.finditer(original_content))
    if len(checklist_matches) > 1:
        raise ValueError(
            "Objective todo contains duplicate Execution Checklist sections"
        )
    if checklist_matches:
        todo_content = pattern.sub(checklist, original_content, count=1)
    else:
        todo_content = original_content.rstrip() + "\n\n" + checklist

    if todo_content != original_content:
        try:
            todo_path.write_text(todo_content, encoding="utf-8")
        except OSError as exc:
            raise ValueError(
                f"Failed to persist objective todo projection: {exc}"
            ) from exc
        if todo_path.read_text(encoding="utf-8") != todo_content:
            raise ValueError("Objective todo projection read-back mismatch")

    sync_objective_handoff(task_id, objective_slug=objective_slug)


def get_execution_subtasks(
    task_id: str, objective_slug: str | None = None
) -> list[dict[str, Any]]:
    """Read plan-owned subtasks and overlay durable completion state."""
    sync_objective_todo_from_state(task_id, objective_slug=objective_slug)
    plan_path, _todo_path = get_active_paths(task_id, objective_slug=objective_slug)
    subtasks = _planned_subtasks_from_plan(plan_path, task_id)
    objective_state = load_objective_state(
        objective_slug=objective_slug, task_id=None if objective_slug else task_id
    )
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


def _aggregate_parent_status(statuses: list[str]) -> str:
    """Derive deterministic parent state from current planned child states."""
    if statuses and all(status == "completed" for status in statuses):
        return "completed"
    if any(status == "failed" for status in statuses):
        return "failed"
    if any(status in {"in_progress", "completed"} for status in statuses):
        return "in_progress"
    if statuses and all(status == "skipped" for status in statuses):
        return "skipped"
    return "pending"


def _salvage_subtask_state(raw: Any, planned: dict[str, Any]) -> dict[str, Any]:
    """Salvage validated durable fields into a plan-owned subtask record."""
    source = raw if isinstance(raw, dict) else {}
    status = source.get("status")
    result: dict[str, Any] = {
        "description": planned["description"],
        "status": status if status in ALLOWED_SUBTASK_STATUSES else "pending",
        "started_at": (
            source.get("started_at")
            if _is_valid_timestamp(source.get("started_at"))
            else None
        ),
        "completed_at": (
            source.get("completed_at")
            if _is_valid_timestamp(source.get("completed_at"))
            else None
        ),
        "duration_seconds": (
            source.get("duration_seconds", 0)
            if _is_valid_duration(source.get("duration_seconds", 0))
            else 0
        ),
        "updated_at": (
            source.get("updated_at")
            if _is_valid_timestamp(source.get("updated_at"))
            else None
        ),
    }
    for field in ("error", "commit_sha"):
        if isinstance(source.get(field), str) and source[field]:
            result[field] = source[field]
    if isinstance(source.get("retries"), int) and source["retries"] >= 0:
        result["retries"] = source["retries"]
    return result


def _merge_runtime_subtask(
    durable: dict[str, Any], runtime: dict[str, Any]
) -> dict[str, Any]:
    """Merge lower-authority runtime evidence without regressing durable state."""
    merged = dict(durable)
    rank = {"pending": 0, "in_progress": 1, "failed": 2, "skipped": 2, "completed": 3}
    if (
        durable["status"] != "completed"
        and rank[runtime["status"]] >= rank[durable["status"]]
    ):
        merged["status"] = runtime["status"]
    for field in ("started_at", "completed_at", "updated_at"):
        if _has_timing_evidence(runtime.get(field)):
            merged[field] = runtime[field]
    if (
        _is_valid_duration(runtime.get("duration_seconds", 0))
        and runtime.get("duration_seconds", 0) > 0
    ):
        merged["duration_seconds"] = runtime["duration_seconds"]
    return merged


def _runtime_evidence_for_resync(
    objective_slug: str, task_id: str
) -> dict[str, Any] | None:
    """Load scope-validated runtime evidence for field-level resync salvage."""
    if not RUNTIME_STATE_PATH.exists():
        return None
    state = load_runtime_state()
    if (
        state is None
        or state.get("objective_slug") != objective_slug
        or state.get("task_id") != task_id
        or not isinstance(state.get("subtasks"), dict)
        or not runtime_state_matches_active_objective(state)
    ):
        return None
    return state


def _normalize_runtime_state_to_plan(
    state: dict[str, Any], task_id: str, objective_slug: str
) -> dict[str, Any]:
    """Persist runtime topology exactly as declared by the scoped plan."""
    source = resolve_task_source(task_id, objective_slug=objective_slug)
    planned_subtasks = _planned_subtasks_from_plan(source.plan_path, task_id)
    if not planned_subtasks:
        raise ValueError(f"No planned subtasks found for {task_id}")
    normalized: dict[str, Any] = {}
    for planned in planned_subtasks:
        current = state["subtasks"].get(planned["id"])
        if _is_valid_subtask_state(current):
            normalized[planned["id"]] = {
                **current,
                "description": planned["description"],
            }
        else:
            normalized[planned["id"]] = {
                "description": planned["description"],
                "status": "pending",
                "retries": 0,
                "started_at": None,
                "completed_at": None,
                "duration_seconds": 0,
                "updated_at": None,
            }
    state["subtasks"] = normalized
    state["plan_path"] = str(source.plan_path)
    state["todo_path"] = str(source.todo_path)
    RUNTIME_STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return state


def _normalize_durable_task_to_plan(
    objective_state: dict[str, Any], source: TaskSource, task_id: str
) -> set[str]:
    """Normalize one valid durable task exactly to current plan topology."""
    planned_subtasks = _planned_subtasks_from_plan(source.plan_path, task_id)
    if not planned_subtasks:
        raise ValueError(f"No planned subtasks found for {task_id}")
    tasks = objective_state.setdefault("tasks", {})
    task_entry = tasks.setdefault(
        task_id,
        {
            "status": "pending",
            "subtasks": {},
            "started_at": None,
            "completed_at": None,
        },
    )
    durable_subtasks = task_entry.get("subtasks", {})
    normalized: dict[str, Any] = {}
    for planned in planned_subtasks:
        existing = durable_subtasks.get(planned["id"], {})
        normalized[planned["id"]] = {
            **existing,
            "description": planned["description"],
            "status": existing.get("status", "pending"),
            "started_at": existing.get("started_at"),
            "completed_at": existing.get("completed_at"),
            "duration_seconds": existing.get("duration_seconds", 0),
            "updated_at": existing.get("updated_at"),
        }
    task_entry["subtasks"] = normalized
    task_entry["status"] = _aggregate_parent_status(
        [subtask["status"] for subtask in normalized.values()]
    )
    if task_entry["status"] != "completed":
        task_entry["completed_at"] = None
    task_entry["plan_path"] = str(source.plan_path)
    task_entry["todo_path"] = str(source.todo_path)
    objective_state["plan_path"] = str(source.plan_path)
    objective_state["todo_path"] = str(source.todo_path)
    objective_state["updated_at"] = datetime.now().isoformat()
    save_objective_state(objective_state)
    return set(normalized)


def _advance_runtime_from_durable_completion(
    state: dict[str, Any], objective_state: dict[str, Any], task_id: str
) -> dict[str, Any]:
    """Copy sticky durable completion into runtime without other regressions."""
    durable_subtasks = (
        objective_state.get("tasks", {}).get(task_id, {}).get("subtasks", {})
    )
    advanced: list[str] = []
    for subtask_id, runtime_subtask in state["subtasks"].items():
        durable_subtask = durable_subtasks.get(subtask_id, {})
        if (
            durable_subtask.get("status") == "completed"
            and runtime_subtask.get("status") != "completed"
        ):
            runtime_subtask["status"] = "completed"
            for field in ("started_at", "completed_at", "updated_at"):
                if _has_timing_evidence(durable_subtask.get(field)):
                    runtime_subtask[field] = durable_subtask[field]
            durable_duration = durable_subtask.get("duration_seconds")
            if _is_valid_duration(durable_duration) and durable_duration > 0:
                runtime_subtask["duration_seconds"] = durable_duration
            advanced.append(subtask_id)
    if advanced:
        RUNTIME_STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
        mm_info(f"Reconciled from ledger — marking as completed: {sorted(advanced)}")
    return state


def bootstrap_objective_state_from_artifacts(
    objective_slug: str, plan_path: Path, todo_path: Path
) -> dict[str, Any]:
    """Recover exact durable state from plan topology and validated evidence."""
    state_path = get_objective_state_path(objective_slug=objective_slug)
    raw_state: dict[str, Any] = {}
    if state_path is not None and state_path.exists():
        try:
            loaded_state = json.loads(state_path.read_text(encoding="utf-8"))
            if isinstance(loaded_state, dict):
                raw_state = loaded_state
        except (json.JSONDecodeError, OSError):
            raw_state = {}
    raw_tasks = raw_state.get("tasks", {})
    if not isinstance(raw_tasks, dict):
        raw_tasks = {}
    state: dict[str, Any] = {
        "objective_slug": objective_slug,
        "plan_path": str(plan_path),
        "todo_path": str(todo_path),
        "tasks": {},
        "updated_at": datetime.now().isoformat(),
        "bootstrapped_from_artifacts": True,
    }
    if isinstance(raw_state.get("status"), str) and raw_state["status"]:
        state["status"] = raw_state["status"]
    for root_task_id in get_task_ids_from_plan(plan_path):
        runtime_state = _runtime_evidence_for_resync(objective_slug, root_task_id)
        planned_subtasks = _planned_subtasks_from_plan(plan_path, root_task_id)
        raw_task = raw_tasks.get(root_task_id, {})
        if not isinstance(raw_task, dict):
            raw_task = {}
        raw_subtasks = raw_task.get("subtasks", {})
        if not isinstance(raw_subtasks, dict):
            raw_subtasks = {}
        task_entry: dict[str, Any] = {
            "status": "pending",
            "subtasks": {},
            "started_at": raw_task.get("started_at")
            if _is_valid_timestamp(raw_task.get("started_at"))
            else None,
            "completed_at": raw_task.get("completed_at")
            if _is_valid_timestamp(raw_task.get("completed_at"))
            else None,
            "plan_path": str(plan_path),
            "todo_path": str(todo_path),
        }
        if isinstance(raw_task.get("depends_on"), list) and all(
            isinstance(value, str) for value in raw_task["depends_on"]
        ):
            task_entry["depends_on"] = list(raw_task["depends_on"])
        for planned in planned_subtasks:
            subtask_state = _salvage_subtask_state(
                raw_subtasks.get(planned["id"]), planned
            )
            if runtime_state is not None and planned["id"] in runtime_state["subtasks"]:
                runtime_subtask = runtime_state["subtasks"][planned["id"]]
                if isinstance(runtime_subtask, dict):
                    runtime_status = runtime_subtask.get("status")
                    if runtime_status in ALLOWED_SUBTASK_STATUSES:
                        sanitized_runtime = _salvage_subtask_state(
                            runtime_subtask, planned
                        )
                        subtask_state = _merge_runtime_subtask(
                            subtask_state, sanitized_runtime
                        )
            task_entry["subtasks"][planned["id"]] = subtask_state

        task_entry["status"] = _aggregate_parent_status(
            [entry["status"] for entry in task_entry["subtasks"].values()]
        )
        state["tasks"][root_task_id] = task_entry

    active_task = raw_state.get("active_task")
    if isinstance(active_task, str) and active_task in state["tasks"]:
        state["active_task"] = active_task

    save_objective_state(state)
    return state


def sync_objective_handoff(task_id: str, objective_slug: str | None = None) -> None:
    """Synchronize objective HANDOFF-CURRENT.md from objective todo/task state."""
    handoff_path = get_objective_handoff_path(task_id, objective_slug=objective_slug)
    if handoff_path is None:
        return

    plan_path, todo_path = get_active_paths(task_id, objective_slug=objective_slug)

    objective_state = load_objective_state(
        objective_slug=objective_slug, task_id=None if objective_slug else task_id
    )
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
        objective_slug = handoff_path.parent.name
        next_task_lines = [
            f"- `/mm:archive-objective {objective_slug}`",
            "- After archive: `/mm:activate-next-objective`.",
        ]
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
    objective_slug = handoff_path.parent.name
    validation_target = next_pending[0] if next_pending else "objective completion"
    handoff_text = "\n".join(
        [
            f"# Handoff — {objective_slug}",
            "",
            "## Current objective",
            f"- `{objective_slug}`",
            "",
            "## Decisions already made",
            "- Per-objective planning artifacts are the source of truth for this objective.",
            "- `execution-state.json` is the durable ledger; `todo.md` and `HANDOFF-CURRENT.md` are projected artifacts.",
            "- Do not restart from historical kickoff notes when durable state already exists.",
            "",
            "## Blockers / risks",
            "- This objective previously drifted from implementation progress because the planning surface and harness paths diverged.",
            f"- Use `python3 .claude/commands/mm/complete-task-handler.py --resync-objective {objective_slug}` after repairing objective artifacts.",
            "- Do not manually edit `todo.md`, `HANDOFF-CURRENT.md`, `task-progress.json`, or `execution-state.json`.",
            "",
            "## Completed tasks",
            *completed_lines,
            "",
            "## Exact next recommended task",
            *next_task_lines,
            "",
            f"## Validation commands for {validation_target}",
            *validation_lines,
            "",
        ]
    )

    try:
        handoff_path.write_text(handoff_text, encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"Failed to persist objective handoff: {exc}") from exc


def sync_global_handoff_for_objective(objective_slug: str) -> None:
    """Rewrite the root handoff as a thin pointer to the objective-local source."""

    objective_dir = get_objective_dir(objective_slug)
    objective_handoff = objective_artifact_path(objective_dir, "HANDOFF-CURRENT.md")
    objective_state = objective_artifact_path(objective_dir, OBJECTIVE_STATE_FILENAME)
    root_statuses = get_root_task_statuses(
        objective_artifact_path(objective_dir, "todo.md")
    )
    if root_statuses and all(status == "x" for _, status, _ in root_statuses):
        next_task_lines = [
            f"- `/mm:archive-objective {objective_slug}`",
            "- After archive: `/mm:activate-next-objective`.",
        ]
    else:
        next_task_lines = [
            f"- Read `{objective_handoff.relative_to(PROJECT_ROOT)}` and follow its current next-step section."
        ]
    content = "\n".join(
        [
            f"# Handoff — {objective_slug}",
            "",
            "## Project naming",
            "- Canonical project identifier for memory/planning: `mastermind-framework`",
            f"- Local repository directory: `{PROJECT_ROOT}`",
            f"- Active planning surface: `{PLANNING_LABEL}`",
            "",
            "## Current objective",
            f"- `{objective_slug}`",
            "",
            "## Source of truth",
            f"- `{objective_handoff.relative_to(PROJECT_ROOT)}`",
            f"- `{(objective_dir / 'tasks.md').relative_to(PROJECT_ROOT)}`",
            f"- `{(objective_dir / 'todo.md').relative_to(PROJECT_ROOT)}`",
            f"- `{objective_state.relative_to(PROJECT_ROOT)}`",
            "",
            "## Decisions already made",
            "- The detailed handoff lives with the active objective package, not in the root handoff.",
            "- Handler-managed state must stay aligned with the active planning surface before task execution resumes.",
            "- Do not manually edit derived progress artifacts; use handler commands or objective resync.",
            "",
            "## Blockers / risks",
            "- Historical `.mm-flow/planning` artifacts may still exist, but they are not the active source of truth when `.planning/` is present.",
            f"- If objective artifacts drift again, run `python3 .claude/commands/mm/complete-task-handler.py --resync-objective {objective_slug}`.",
            "",
            "## Exact next recommended task",
            *next_task_lines,
            "",
            "## Validation commands",
            f"- python3 .claude/commands/mm/discover-contract-check.py --objective {objective_slug}",
            f"- python3 .claude/commands/mm/complete-task-handler.py --resync-objective {objective_slug}",
            "",
        ]
    )
    try:
        (PLANNING_DIR / "HANDOFF-CURRENT.md").write_text(content, encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"Failed to persist root handoff: {exc}") from exc


def resync_objective_artifacts(objective_slug: str) -> None:
    """Bootstrap durable state and rewrite objective/global handoffs."""

    objective_dir = get_objective_dir(objective_slug)
    plan_path = objective_artifact_path(objective_dir, "tasks.md")
    handoff_path = objective_artifact_path(objective_dir, "HANDOFF-CURRENT.md")
    if not objective_dir.exists():
        raise ValueError(
            f"Objective `{objective_slug}` not found under {PLANNING_LABEL}/changes/"
        )
    if not plan_path.exists():
        raise ValueError(f"Objective `{objective_slug}` is missing tasks.md")
    if not handoff_path.exists():
        raise ValueError(f"Objective `{objective_slug}` is missing HANDOFF-CURRENT.md")

    task_ids = get_task_ids_from_plan(plan_path)
    if not task_ids:
        raise ValueError(f"Objective `{objective_slug}` has no root tasks in tasks.md")

    raw_runtime_slug: str | None = None
    if RUNTIME_STATE_PATH.exists():
        try:
            raw_runtime = json.loads(RUNTIME_STATE_PATH.read_text(encoding="utf-8"))
            if isinstance(raw_runtime, dict) and isinstance(
                raw_runtime.get("objective_slug"), str
            ):
                raw_runtime_slug = raw_runtime["objective_slug"]
        except (json.JSONDecodeError, OSError):
            pass

    with _objective_artifact_transaction(objective_slug):
        todo_path = ensure_objective_todo(objective_dir, objective_slug)
        bootstrap_objective_state_from_artifacts(objective_slug, plan_path, todo_path)
        runtime_state = load_runtime_state()
        if (
            runtime_state is not None
            and runtime_state.get("objective_slug") == objective_slug
            and runtime_state.get("task_id") in task_ids
        ):
            _normalize_runtime_state_to_plan(
                runtime_state, runtime_state["task_id"], objective_slug
            )

        for task_id in task_ids:
            if not sync_task_acceptance_criteria(
                task_id, objective_slug=objective_slug
            ):
                raise ValueError(
                    f"Cannot resync {objective_slug}: acceptance projection failed for {task_id}"
                )
        sync_objective_todo_from_state(task_ids[0], objective_slug=objective_slug)
        sync_objective_handoff(task_ids[0], objective_slug=objective_slug)
        sync_global_handoff_for_objective(objective_slug)
        if (
            RUNTIME_STATE_PATH.exists()
            and load_runtime_state() is None
            and raw_runtime_slug == objective_slug
        ):
            RUNTIME_STATE_PATH.unlink()


def audit_task_consistency(
    task_id: str, objective_slug: str | None = None
) -> list[str]:
    """Compare runtime truth against todo/handoff artifacts for a root task."""
    issues: list[str] = []
    if not RUNTIME_STATE_PATH.exists():
        return issues

    try:
        state = load_runtime_state()
        if state is None:
            raise ValueError("Runtime state is invalid")
        runtime_objective_slug = state["objective_slug"]
        if objective_slug is not None and runtime_objective_slug != objective_slug:
            raise ValueError(
                f"Runtime state belongs to objective `{runtime_objective_slug}`, "
                f"not requested objective `{objective_slug}`"
            )
        _, todo_path = get_active_paths(task_id, objective_slug=objective_slug)
        todo_content = todo_path.read_text(encoding="utf-8")
    except (OSError, ValueError) as exc:
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

    handoff_path = get_objective_handoff_path(task_id, objective_slug=objective_slug)
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


def reconcile_artifacts_from_runtime(
    task_id: str, objective_slug: str | None = None
) -> bool:
    """Normalize runtime, persist exact durable truth, then project artifacts."""
    snapshot: dict[Path, bytes | None] | None = None
    try:
        state = load_runtime_state()
        if state is None:
            raise ValueError("Runtime state is invalid")
        runtime_objective_slug = state["objective_slug"]
        if objective_slug is not None and runtime_objective_slug != objective_slug:
            raise ValueError(
                f"Runtime state belongs to objective `{runtime_objective_slug}`, "
                f"not requested objective `{objective_slug}`"
            )
        if state.get("task_id") != task_id:
            raise ValueError(
                f"Runtime state is for task {state.get('task_id')}, not {task_id}"
            )
        source = resolve_task_source(task_id, objective_slug=runtime_objective_slug)
        objective_dir = get_objective_dir(runtime_objective_slug)
        snapshot = _snapshot_artifacts(_objective_transaction_paths(objective_dir))
        objective_state = load_objective_state(objective_slug=runtime_objective_slug)
        if objective_state is None:
            objective_state = bootstrap_objective_state_from_artifacts(
                runtime_objective_slug, source.plan_path, source.todo_path
            )
        state = _normalize_runtime_state_to_plan(state, task_id, runtime_objective_slug)
        expected_subtask_ids = _normalize_durable_task_to_plan(
            objective_state, source, task_id
        )
        state = _advance_runtime_from_durable_completion(
            state, objective_state, task_id
        )
    except (OSError, ValueError) as exc:
        if snapshot is not None:
            _restore_artifacts(snapshot)
        mm_error(f"Failed to reconcile artifacts: {exc}")
        return False

    if not reconcile_objective_state_from_runtime(
        task_id,
        expected_objective_slug=runtime_objective_slug,
        expected_subtask_ids=expected_subtask_ids,
        runtime_state=state,
    ):
        if snapshot is not None:
            _restore_artifacts(snapshot)
        return False
    persisted_state = load_objective_state(objective_slug=runtime_objective_slug)
    if persisted_state is None:
        if snapshot is not None:
            _restore_artifacts(snapshot)
        mm_error("Durable reconciliation could not be verified")
        return False
    persisted_subtasks = persisted_state["tasks"][task_id]["subtasks"]
    if set(persisted_subtasks) != expected_subtask_ids or any(
        persisted_subtasks[subtask_id]["status"]
        != state["subtasks"][subtask_id]["status"]
        for subtask_id in expected_subtask_ids
    ):
        if snapshot is not None:
            _restore_artifacts(snapshot)
        mm_error("Durable reconciliation verification failed")
        return False
    try:
        if not sync_task_acceptance_criteria(
            task_id, objective_slug=runtime_objective_slug
        ):
            raise ValueError("acceptance projection failed")
        sync_objective_todo_from_state(task_id, objective_slug=runtime_objective_slug)
    except (OSError, ValueError) as exc:
        if snapshot is not None:
            _restore_artifacts(snapshot)
        mm_error(f"Failed to reconcile artifacts: {exc}")
        return False
    return True


def reconcile_objective_state_from_runtime(
    task_id: str,
    expected_objective_slug: str | None = None,
    expected_subtask_ids: set[str] | None = None,
    runtime_state: dict[str, Any] | None = None,
) -> bool:
    """Persist runtime subtask truth into execution-state.json for a root task."""
    runtime_state = runtime_state or load_runtime_state()
    if not runtime_state:
        mm_error("No runtime state to reconcile objective state from")
        return False

    objective_slug = runtime_state.get("objective_slug")
    if not objective_slug:
        mm_error(
            "Runtime state has no objective_slug; cannot reconcile objective state"
        )
        return False
    if expected_objective_slug and objective_slug != expected_objective_slug:
        mm_error(
            f"Runtime objective `{objective_slug}` does not match requested "
            f"objective `{expected_objective_slug}`"
        )
        return False

    objective_state = load_objective_state(objective_slug=objective_slug)
    if objective_state is None:
        mm_error(
            f"No objective execution state found for `{objective_slug}` during reconcile"
        )
        return False

    now_iso = datetime.now().isoformat()
    task_entry = objective_state["tasks"].get(task_id)
    if not isinstance(task_entry, dict):
        mm_error(f"Objective state has no planned task {task_id}")
        return False
    durable_subtasks = task_entry["subtasks"]
    if expected_subtask_ids and set(durable_subtasks) != expected_subtask_ids:
        mm_error(
            f"Objective durable subtask set does not match plan for {task_id}: "
            f"expected={sorted(expected_subtask_ids)} "
            f"actual={sorted(durable_subtasks)}"
        )
        return False
    runtime_subtasks = {
        subtask_id: subtask_state
        for subtask_id, subtask_state in runtime_state["subtasks"].items()
        if subtask_id in durable_subtasks
    }
    if not runtime_subtasks:
        mm_error(f"No planned runtime subtasks found for {task_id}")
        return False

    for subtask_id, runtime_subtask in runtime_subtasks.items():
        subtask_entry = durable_subtasks[subtask_id]
        runtime_description = runtime_subtask.get("description")
        if isinstance(runtime_description, str) and runtime_description:
            subtask_entry["description"] = runtime_description
        subtask_entry["status"] = runtime_subtask.get("status", "pending")
        for field in ("started_at", "completed_at", "updated_at"):
            runtime_value = runtime_subtask.get(field)
            if _has_timing_evidence(runtime_value):
                subtask_entry[field] = runtime_value
        runtime_duration = runtime_subtask.get("duration_seconds")
        if isinstance(runtime_duration, (int, float)) and runtime_duration > 0:
            subtask_entry["duration_seconds"] = runtime_duration

    subtask_states = [
        subtask_state.get("status", "pending")
        for subtask_state in durable_subtasks.values()
    ]
    parent_status = _aggregate_parent_status(subtask_states)
    if parent_status == "completed":
        task_entry["status"] = "completed"
        task_entry["completed_at"] = max(
            (
                subtask_state.get("completed_at")
                for subtask_state in durable_subtasks.values()
                if subtask_state.get("completed_at")
            ),
            default=now_iso,
        )
        task_entry["started_at"] = task_entry.get("started_at") or min(
            (
                subtask_state.get("started_at")
                for subtask_state in durable_subtasks.values()
                if subtask_state.get("started_at")
            ),
            default=runtime_state.get("started_at"),
        )
    else:
        task_entry["status"] = parent_status
        task_entry["started_at"] = task_entry.get("started_at") or runtime_state.get(
            "started_at"
        )
        task_entry["completed_at"] = None

    objective_state["updated_at"] = now_iso
    try:
        save_objective_state(objective_state)
    except (OSError, ValueError) as exc:
        mm_error(str(exc))
        return False
    return True


def _durable_task_is_complete(
    task_id: str, objective_slug: str, expected_subtask_ids: set[str]
) -> bool:
    """Return whether durable parent and exact planned subtasks are completed."""
    objective_state = load_objective_state(objective_slug=objective_slug)
    if objective_state is None:
        return False
    task_entry = objective_state["tasks"].get(task_id)
    if not isinstance(task_entry, dict) or task_entry.get("status") != "completed":
        return False
    durable_subtasks = task_entry.get("subtasks", {})
    return set(durable_subtasks) == expected_subtask_ids and all(
        durable_subtasks[subtask_id].get("status") == "completed"
        for subtask_id in expected_subtask_ids
    )


def _require_completed_projection_verification(
    task_id: str, objective_slug: str
) -> None:
    """Verify completed acceptance, todo, and handoff projections before emission."""
    if not task_acceptance_criteria_satisfied(task_id, objective_slug=objective_slug):
        raise ValueError(f"Cannot complete {task_id}: acceptance read-back failed")
    runtime_state = load_runtime_state()
    if (
        runtime_state is not None
        and runtime_state.get("task_id") == task_id
        and runtime_state.get("objective_slug") == objective_slug
    ):
        objective_state = load_objective_state(objective_slug=objective_slug)
        if objective_state is None:
            raise ValueError(f"Cannot complete {task_id}: durable state is missing")
        _advance_runtime_from_durable_completion(
            runtime_state, objective_state, task_id
        )
    issues = audit_task_consistency(task_id, objective_slug=objective_slug)
    if issues:
        raise ValueError(
            f"Cannot complete {task_id}: projection verification failed: "
            + "; ".join(issues)
        )
    handoff_path = get_objective_handoff_path(task_id, objective_slug=objective_slug)
    if handoff_path is None or not handoff_path.exists():
        raise ValueError(f"Cannot complete {task_id}: handoff projection is missing")
    handoff_text = handoff_path.read_text(encoding="utf-8")
    if not re.search(rf"^-\s\[x\]\s+{re.escape(task_id)}:", handoff_text, re.MULTILINE):
        raise ValueError(
            f"Cannot complete {task_id}: handoff completion read-back failed"
        )


def get_objective_task_status(
    task_id: str, objective_slug: str | None = None
) -> str | None:
    """Return durable status for a root task from objective execution state."""
    objective_state = load_objective_state(
        objective_slug=objective_slug, task_id=None if objective_slug else task_id
    )
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
    notify_script_path = _resolve_notify_script_path()
    if notify_script_path is None:
        return

    try:
        result = subprocess.run(
            ["python3", str(notify_script_path), task_id, "complete"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
        if result.returncode != 0:
            emit(
                f"Notification script failed for {task_id}: {result.stderr.strip()}",
                file=sys.stderr,
            )
            return
        current_state = load_runtime_state()
        if (
            current_state is None
            or current_state.get("task_id") != task_id
            or not runtime_task_complete(current_state)
        ):
            emit(
                f"WARNING: Notification metadata skipped for {task_id}: runtime changed",
                file=sys.stderr,
            )
            return
        current_state["completion_notified_at"] = datetime.now().isoformat()
        temp_path = RUNTIME_STATE_PATH.with_name(
            f".{RUNTIME_STATE_PATH.name}.notification-{os.getpid()}.tmp"
        )
        try:
            temp_path.write_text(json.dumps(current_state, indent=2), encoding="utf-8")
            temp_path.replace(RUNTIME_STATE_PATH)
        except OSError as exc:
            temp_path.unlink(missing_ok=True)
            emit(
                f"WARNING: Notification delivered for {task_id}, but metadata was not saved: {exc}",
                file=sys.stderr,
            )
            return
        mm_info(f"Notification delivered for {task_id}")
    except Exception as exc:
        emit(
            f"WARNING: Could not trigger completion notification for {task_id}: {exc}",
            file=sys.stderr,
        )


def ensure_runtime_can_start_task(
    task_id: str, objective_slug: str | None = None
) -> None:
    """Block starting a new task if a previous runtime task is incomplete or inconsistent."""
    state = load_runtime_state()
    if state is None:
        if RUNTIME_STATE_PATH.exists():
            try:
                raw_state = json.loads(RUNTIME_STATE_PATH.read_text(encoding="utf-8"))
                raw_slug = raw_state.get("objective_slug")
                if (
                    isinstance(raw_slug, str)
                    and not get_objective_dir(raw_slug).exists()
                ):
                    return
            except (json.JSONDecodeError, OSError, ValueError, AttributeError):
                pass
            mm_error("Runtime state is invalid; repair or resync it before continuing")
            sys.exit(1)
        return

    active_task_id = state.get("task_id")
    if not active_task_id:
        return

    # Same task: reconcile if needed, then allow resume/start logic to continue.
    runtime_objective_slug = state.get("objective_slug")
    same_scope = objective_slug is None or objective_slug == runtime_objective_slug
    if active_task_id == task_id and same_scope:
        issues = audit_task_consistency(task_id, objective_slug=runtime_objective_slug)
        if issues:
            mm_info(
                "Detected stale artifact mismatch before execution — reconciling from runtime state"
            )
            for issue in issues:
                mm_error(f"SYNC: {issue}")
            if not reconcile_artifacts_from_runtime(
                task_id, objective_slug=runtime_objective_slug
            ):
                mm_error("Runtime artifact reconciliation failed")
                sys.exit(1)
        return

    if runtime_task_complete(state):
        return

    issues = audit_task_consistency(
        active_task_id, objective_slug=runtime_objective_slug
    )
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


def get_git_commits_for_task(
    task_id: str, objective_slug: str | None = None
) -> set[str]:
    """Return exact subtask tokens from scoped conventional commit subjects."""
    if not objective_slug:
        return set()
    pattern = re.compile(
        rf"^(?:feat|fix|docs|style|refactor|test|chore)"
        rf"\({re.escape(objective_slug)}\):\s+.*?"
        rf"(?<![A-Za-z0-9.])(?P<id>{re.escape(task_id)}\.\d+)"
        rf"(?![A-Za-z0-9.])"
    )
    result = subprocess.run(
        ["git", "log", "HEAD", "--pretty=format:%s", "-200"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    if result.returncode != 0:
        return set()
    return {
        match.group("id")
        for subject in result.stdout.splitlines()
        if (match := pattern.search(subject.strip())) is not None
    }


# ============================================================================
# Task Parsing
# ============================================================================


def read_task_from_plan(
    task_id: str, objective_slug: str | None = None
) -> dict[str, str]:
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
    plan_path, _ = get_active_paths(task_id, objective_slug=objective_slug)
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
        _, todo_path = get_active_paths(task_id, objective_slug=objective_slug)
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


def read_subtasks_from_todo(
    task_id: str, objective_slug: str | None = None
) -> list[dict[str, Any]]:
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
    _, todo_path = get_active_paths(task_id, objective_slug=objective_slug)
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
    seed_objective_task_state(source, task_id, subtasks)
    try:
        RUNTIME_STATE_PATH.write_text(json.dumps(runtime_state, indent=2))
    except OSError as e:
        mm_error(f"Failed to write runtime state: {e}")
        raise

    return runtime_state


def _snapshot_artifacts(paths: tuple[Path, ...]) -> dict[Path, bytes | None]:
    """Capture byte-exact state for rollback of expected checkpoint failures."""
    return {path: path.read_bytes() if path.exists() else None for path in paths}


def _restore_artifacts(snapshot: dict[Path, bytes | None]) -> None:
    """Restore a checkpoint snapshot after an expected transactional failure."""
    for path, content in snapshot.items():
        if content is None:
            if path.exists():
                path.unlink()
        else:
            path.write_bytes(content)


@contextmanager
def _objective_artifact_transaction(
    objective_slug: str,
) -> Iterator[dict[Path, bytes | None]]:
    """Restore all handler-managed objective artifacts when a command fails."""
    objective_dir = get_objective_dir(objective_slug)
    snapshot = _snapshot_artifacts(_objective_transaction_paths(objective_dir))
    try:
        yield snapshot
    except BaseException:
        _restore_artifacts(snapshot)
        raise


@contextmanager
def _mutation_lock() -> Iterator[None]:
    """Serialize complete-task mutations within the active planning surface."""
    PLANNING_DIR.mkdir(parents=True, exist_ok=True)
    lock_path = PLANNING_DIR / ".complete-task.lock"
    with lock_path.open("a+", encoding="utf-8") as lock_file:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError(
                "another complete-task mutation is active; retry after it finishes"
            ) from exc
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def update_subtask_status(
    subtask_id: str,
    status: str,
    error: str | None = None,
    commit_sha: str | None = None,
) -> None:
    """Apply a checkpoint transition atomically across state and projections."""
    state = _require_runtime_state()
    objective_dir = get_objective_dir(state["objective_slug"])
    snapshot = _snapshot_artifacts(_objective_transaction_paths(objective_dir))
    try:
        _apply_subtask_status(subtask_id, status, error, commit_sha)
    except (OSError, ValueError):
        _restore_artifacts(snapshot)
        raise


def _apply_subtask_status(
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
    if status not in ALLOWED_SUBTASK_STATUSES:
        raise ValueError(f"Unsupported runtime subtask status: {status}")
    state = _require_runtime_state()
    objective_slug = state["objective_slug"]
    root_task_id = get_root_task_id(subtask_id)
    if state.get("task_id") != root_task_id:
        raise ValueError(
            f"Runtime state is for task {state.get('task_id')}, not {root_task_id}"
        )
    source = resolve_task_source(root_task_id, objective_slug=objective_slug)
    objective_state = load_objective_state(objective_slug=objective_slug)
    if objective_state is None:
        raise ValueError(f"No objective execution state found for `{objective_slug}`")
    state = _normalize_runtime_state_to_plan(state, root_task_id, objective_slug)
    expected_subtask_ids = _normalize_durable_task_to_plan(
        objective_state, source, root_task_id
    )
    if subtask_id not in expected_subtask_ids:
        raise ValueError(f"Subtask {subtask_id} is not declared in tasks.md")
    state = _advance_runtime_from_durable_completion(
        state, objective_state, root_task_id
    )
    task_entry = objective_state["tasks"][root_task_id]
    if (
        task_entry["subtasks"][subtask_id]["status"] == "completed"
        and status != "completed"
    ):
        sync_task_acceptance_criteria(root_task_id, objective_slug=objective_slug)
        sync_objective_todo_from_state(root_task_id, objective_slug=objective_slug)
        return

    now = _now_compatible_with(state.get("started_at"))
    now_iso = now.isoformat()
    runtime_subtask = state["subtasks"][subtask_id]
    runtime_subtask["status"] = status
    runtime_subtask["updated_at"] = now_iso
    if status == "completed" and runtime_subtask.get("started_at"):
        started_at = datetime.fromisoformat(runtime_subtask["started_at"])
        runtime_subtask["completed_at"] = now_iso
        runtime_subtask["duration_seconds"] = round(
            (now - started_at).total_seconds(), 2
        )
    elif status == "in_progress":
        runtime_subtask["started_at"] = now_iso
        runtime_subtask["completed_at"] = None
    if error:
        runtime_subtask["error"] = error
    if commit_sha:
        runtime_subtask["commit_sha"] = commit_sha
    state["last_checkpoint"] = subtask_id
    RUNTIME_STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")

    durable_subtask = task_entry["subtasks"][subtask_id]
    for field in (
        "description",
        "status",
        "started_at",
        "completed_at",
        "duration_seconds",
        "updated_at",
        "error",
        "commit_sha",
    ):
        if field in runtime_subtask:
            durable_subtask[field] = runtime_subtask[field]
    task_entry["status"] = _aggregate_parent_status(
        [entry["status"] for entry in task_entry["subtasks"].values()]
    )
    if task_entry["status"] == "completed":
        task_entry["completed_at"] = now_iso
        task_entry["started_at"] = task_entry.get("started_at") or state.get(
            "started_at"
        )
    else:
        task_entry["completed_at"] = None
        if task_entry["status"] == "in_progress":
            task_entry["started_at"] = task_entry.get("started_at") or now_iso
    objective_state["updated_at"] = now_iso
    save_objective_state(objective_state)
    if task_entry["status"] == "completed":
        require_verified_acceptance_projection(root_task_id, objective_slug)
    else:
        if not sync_task_acceptance_criteria(
            root_task_id, objective_slug=objective_slug
        ):
            raise ValueError(
                f"Cannot checkpoint {root_task_id}: acceptance projection failed"
            )
    sync_objective_todo_from_state(root_task_id, objective_slug=objective_slug)


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
        update_subtask_status(subtask_id, "failed", error=f"{type(e).__name__}: {e!s}")
        raise


def get_task_payload(task_id: str, objective_slug: str | None = None) -> dict[str, Any]:
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
        source = resolve_task_source(task_id, objective_slug=objective_slug)
        task = read_task_from_plan(task_id, objective_slug=source.objective_slug)
        subtasks = get_execution_subtasks(task_id, objective_slug=source.objective_slug)

        # Filter to pending subtasks from durable state only. Git history is
        # informational, not a progress source of truth in the objective flow.
        pending_subtasks = [st for st in subtasks if not st["completed"]]

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


def _has_checkpoint(task_id: str, objective_slug: str | None = None) -> bool:
    """Return True if there's a real checkpoint to resume from.

       Checks:
    1. task-progress.json exists for this task_id
       2. Has at least one completed subtask (not just initialized)
    """
    state = load_runtime_state()
    if state is None:
        return False
    if state.get("task_id") != task_id:
        return False
    if objective_slug is not None and state.get("objective_slug") != objective_slug:
        return False
    completed = [
        sid
        for sid, info in state["subtasks"].items()
        if info.get("status") == "completed"
    ]
    return len(completed) > 0


def build_model_brief(
    task_id: str, resume_mode: bool = False, objective_slug: str | None = None
) -> str:
    """Build a concise model handoff brief for a root task.

    Args:
        task_id: Root task identifier.
        resume_mode: Whether the brief is for an explicit resume flow.

    Returns:
        Markdown brief that another model can follow without a long custom prompt.
    """
    source = resolve_task_source(task_id, objective_slug=objective_slug)
    task = read_task_from_plan(task_id, objective_slug=source.objective_slug)
    objective_dir = source.plan_path.parent
    objective_state_path = objective_artifact_path(
        objective_dir, OBJECTIVE_STATE_FILENAME
    )
    handoff_path = objective_artifact_path(objective_dir, "HANDOFF-CURRENT.md")
    requirements_path = objective_dir / "requirements.md"
    design_path = objective_dir / "design.md"
    canonical_doc_path = (
        _find_objective_canonical_doc(source.objective_slug)
        if source.objective_slug
        else None
    )
    objective_state = load_objective_state(objective_slug=source.objective_slug) or {}
    task_state = objective_state.get("tasks", {}).get(task_id, {})
    task_status = task_state.get("status", "pending")
    validation_commands = get_task_validation_commands_from_plan(
        source.plan_path, task_id
    )

    # Only suggest --continue if there's a real checkpoint to resume from.
    # If resume_mode=True but no checkpoint exists, fall back to fresh start.
    has_checkpoint = _has_checkpoint(task_id, objective_slug=source.objective_slug)
    suggest_continue = resume_mode and has_checkpoint

    read_files = [
        "docs/canonical/45-HYBRID-SPEC-FLOW-AND-RULES.md",
    ]
    if canonical_doc_path is not None:
        read_files.append(str(canonical_doc_path.relative_to(PROJECT_ROOT)))
    read_files.extend(
        [
            str(requirements_path.relative_to(PROJECT_ROOT)),
            str(design_path.relative_to(PROJECT_ROOT)),
            str(source.plan_path.relative_to(PROJECT_ROOT)),
            str(source.todo_path.relative_to(PROJECT_ROOT)),
            str(handoff_path.relative_to(PROJECT_ROOT)),
            str(objective_state_path.relative_to(PROJECT_ROOT)),
        ]
    )

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


def _objective_transaction_paths(objective_dir: Path) -> tuple[Path, ...]:
    """Return handler-managed objective artifacts for transactional snapshots."""
    return (
        RUNTIME_STATE_PATH,
        objective_artifact_path(objective_dir, OBJECTIVE_STATE_FILENAME),
        objective_artifact_path(objective_dir, "tasks.md"),
        objective_artifact_path(objective_dir, "todo.md"),
        objective_artifact_path(objective_dir, "HANDOFF-CURRENT.md"),
        PLANNING_DIR / "HANDOFF-CURRENT.md",
    )


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
        mm_error(
            f"Cannot start {task_id}: no durable completion evidence exists for prior tasks."
        )
        sys.exit(1)

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
            continue
        projected = sync_task_acceptance_criteria(
            prior_id, objective_slug=source.objective_slug
        )
        expected_ids = {
            subtask["id"]
            for subtask in _planned_subtasks_from_plan(source.plan_path, prior_id)
        }
        if (
            not projected
            or not _durable_task_is_complete(
                prior_id, source.objective_slug, expected_ids
            )
            or not task_acceptance_criteria_satisfied(
                prior_id, objective_slug=source.objective_slug
            )
        ):
            mm_error(
                f"Cannot start {task_id}: {prior_id} acceptance criteria are not satisfied in tasks.md."
            )
            mm_error(f"Run: /mm:complete-task {prior_id} --continue")
            blocked = True

    if blocked:
        sys.exit(1)


def start_task(task_id: str, objective_slug: str | None = None) -> None:
    """Run the complete fresh-start flow as one objective transaction."""
    source = resolve_task_source(task_id, objective_slug=objective_slug)
    if not source.objective_slug:
        raise ValueError(f"Task {task_id} has no objective scope")
    with _objective_artifact_transaction(source.objective_slug):
        _start_task(task_id, objective_slug=source.objective_slug)


def _start_task(task_id: str, objective_slug: str | None = None) -> None:
    """Start or resume a task.

    Args:
        task_id: Task identifier (e.g., "D1").
    """
    source = resolve_task_source(task_id, objective_slug=objective_slug)
    load_objective_state(objective_slug=source.objective_slug)
    mm_info(f"Starting task {task_id}")
    ensure_runtime_can_start_task(task_id, objective_slug=source.objective_slug)
    mm_info(
        f"Planning source: {source.mode} ({source.plan_path.relative_to(PROJECT_ROOT)})"
    )
    validate_previous_tasks_complete(task_id, source)
    sync_objective_todo_from_state(task_id, objective_slug=source.objective_slug)

    # Read task and subtasks
    task = read_task_from_plan(task_id, objective_slug=source.objective_slug)
    subtasks = get_execution_subtasks(task_id, objective_slug=source.objective_slug)

    mm_task(task_id, task["title"])
    mm_model_brief(build_model_brief(task_id, objective_slug=source.objective_slug))

    # Show all subtasks with status
    for st in subtasks:
        status = "[x]" if st["completed"] else "[ ]"
        mm_subtask(st["id"], status, st["description"])

    git_completed = get_git_commits_for_task(
        task_id, objective_slug=source.objective_slug
    )
    mm_git(len(git_completed), len(subtasks), sorted(git_completed))
    runtime_state: dict[str, Any] | None = None

    # Filter pending subtasks from durable execution state.
    pending_subtasks = [st for st in subtasks if not st["completed"]]

    if not pending_subtasks:
        expected_subtask_ids = {subtask["id"] for subtask in subtasks}
        if not _durable_task_is_complete(
            task_id, source.objective_slug, expected_subtask_ids
        ):
            mm_error(
                f"Cannot complete {task_id}: durable state is not exactly completed"
            )
            sys.exit(1)
        require_verified_acceptance_projection(task_id, source.objective_slug)
        sync_objective_todo_from_state(task_id, objective_slug=source.objective_slug)
        _require_completed_projection_verification(task_id, source.objective_slug)
        mm_status("TASK COMPLETE - all subtasks completed in durable state")
        return

    fatal_issues = validate_execution_prerequisites(
        task_id, objective_slug=source.objective_slug
    )
    if fatal_issues:
        for issue in fatal_issues:
            mm_error(f"FLOW BLOCKED: {issue}")
        mm_status("BLOCKED - repair mm-flow/Claude adapter before continuing")
        sys.exit(1)

    mm_pending(len(pending_subtasks))

    # Show pending subtasks
    for st in pending_subtasks:
        mm_subtask(st["id"], "pending", st["description"])

    # Detect required permissions BEFORE launching agent
    permission_warnings = detect_required_permissions(task_id, pending_subtasks)
    if permission_warnings:
        mm_info("PERMISSION CHECK:")
        for warning in permission_warnings:
            emit(warning, flush=True)
        mm_info(
            "Please ensure Claude Code has these permissions enabled in settings.json"
        )

    # Initialize runtime state for pending planned work.
    if runtime_state is None:
        runtime_state = init_runtime_state(task_id, subtasks, source)
    mm_info(f"Runtime state: {RUNTIME_STATE_PATH}")
    mm_info(f"Session ID: {runtime_state['session_id']}")

    # Open dev session in DB (non-blocking — continues if DB unavailable)
    db_session_id = _open_db_session(task_id, len(pending_subtasks))
    if db_session_id:
        mm_info(f"DB session opened: {db_session_id}")

    # Launch task-executor
    _mm_launch_with_db(task_id, db_session_id, objective_slug=source.objective_slug)


def resume_task(task_id: str, objective_slug: str | None = None) -> None:
    """Run the complete resume flow as one objective transaction."""
    source = resolve_task_source(task_id, objective_slug=objective_slug)
    if not source.objective_slug:
        raise ValueError(f"Task {task_id} has no objective scope")
    with _objective_artifact_transaction(source.objective_slug):
        _resume_task(task_id, objective_slug=source.objective_slug)


def _resume_task(task_id: str, objective_slug: str | None = None) -> None:
    """Resume a task from checkpoint.

    Args:
        task_id: Task identifier (e.g., "D1").
    """
    source = resolve_task_source(task_id, objective_slug=objective_slug)
    mm_info(f"Resuming task {task_id}")

    if not RUNTIME_STATE_PATH.exists():
        raise ValueError(
            f"No runtime state found for {task_id}; start without --continue or "
            f"run --resync-objective {source.objective_slug}"
        )

    state = load_runtime_state()
    if state is None:
        mm_error("Runtime state is invalid; repair or resync it before continuing")
        sys.exit(1)

    runtime_objective_slug = state["objective_slug"]
    if objective_slug is not None and runtime_objective_slug != objective_slug:
        mm_error(
            f"Runtime state belongs to objective `{runtime_objective_slug}`, "
            f"not requested objective `{objective_slug}`"
        )
        sys.exit(1)

    if state.get("task_id") != task_id:
        mm_error(f"Runtime state is for task {state.get('task_id')}, not {task_id}")
        sys.exit(1)

    objective_state = load_objective_state(objective_slug=runtime_objective_slug)
    if objective_state is None:
        raise ValueError(
            f"No durable ledger found for `{runtime_objective_slug}`; run "
            f"--resync-objective {runtime_objective_slug} before resuming"
        )
    try:
        state = _normalize_runtime_state_to_plan(state, task_id, runtime_objective_slug)
        if objective_state is not None:
            state = _advance_runtime_from_durable_completion(
                state, objective_state, task_id
            )
    except (OSError, ValueError) as exc:
        mm_error(f"Cannot resume {task_id}: {exc}")
        sys.exit(1)

    ensure_runtime_can_start_task(task_id, objective_slug=runtime_objective_slug)

    planned_subtasks = _planned_subtasks_from_plan(source.plan_path, task_id)
    planned_subtasks_by_id = {subtask["id"]: subtask for subtask in planned_subtasks}
    if not planned_subtasks_by_id:
        mm_error(f"No planned subtasks found for {task_id}; cannot resume safely")
        sys.exit(1)

    ledger_subtasks: dict[str, Any] = {}
    if objective_state:
        ledger_subtasks = (
            objective_state.get("tasks", {}).get(task_id, {}).get("subtasks", {})
        )

    expected_subtask_ids = set(planned_subtasks_by_id)

    sync_objective_todo_from_state(task_id, objective_slug=runtime_objective_slug)
    mm_task(
        task_id,
        read_task_from_plan(task_id, objective_slug=runtime_objective_slug)["title"],
    )
    mm_model_brief(
        build_model_brief(
            task_id, resume_mode=True, objective_slug=runtime_objective_slug
        )
    )

    mm_info(f"Previous session: {state['session_id']}")
    mm_info(f"Last checkpoint: {state.get('last_checkpoint', 'none')}")

    # Detectar subtareas colgadas en in_progress > 1 hora
    stale_subtasks = []
    stale_threshold_hours = 1

    for sid, st in state["subtasks"].items():
        if st.get("status") == "in_progress" and st.get("started_at"):
            try:
                started = datetime.fromisoformat(st["started_at"])
                hours_since = (
                    _now_compatible_with(st["started_at"]) - started
                ).total_seconds() / 3600
                if hours_since > stale_threshold_hours:
                    stale_subtasks.append((sid, hours_since))
            except (ValueError, TypeError):
                pass

    git_completed = get_git_commits_for_task(
        task_id, objective_slug=runtime_objective_slug
    )
    mm_git(len(git_completed), len(state["subtasks"]), sorted(git_completed))

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
        sid
        for sid in expected_subtask_ids
        if state["subtasks"].get(sid, {}).get("status") == "completed"
    ]
    pending = [
        sid
        for sid in expected_subtask_ids
        if state["subtasks"].get(sid, {}).get("status") != "completed"
    ]

    mm_info(f"Completed: {len(completed)}/{len(expected_subtask_ids)}")
    if completed:
        mm_info(f"Completed subtasks: {sorted(completed)}")

    # Check if task is actually complete
    if expected_subtask_ids and not pending:
        reconciled = reconcile_objective_state_from_runtime(
            task_id,
            expected_objective_slug=runtime_objective_slug,
            expected_subtask_ids=expected_subtask_ids,
        )
        if not reconciled:
            mm_error(f"Cannot complete {task_id}: durable reconciliation failed")
            sys.exit(1)
        if not _durable_task_is_complete(
            task_id, runtime_objective_slug, expected_subtask_ids
        ):
            mm_error(
                f"Cannot complete {task_id}: durable state is not exactly completed"
            )
            sys.exit(1)
        require_verified_acceptance_projection(task_id, runtime_objective_slug)
        sync_objective_todo_from_state(task_id, objective_slug=runtime_objective_slug)
        _require_completed_projection_verification(task_id, runtime_objective_slug)
        mm_status("TASK COMPLETE - all subtasks completed in runtime state")
        return

    fatal_issues = validate_execution_prerequisites(
        task_id, objective_slug=runtime_objective_slug
    )
    if fatal_issues:
        for issue in fatal_issues:
            mm_error(f"FLOW BLOCKED: {issue}")
        mm_status("BLOCKED - repair mm-flow/Claude adapter before continuing")
        sys.exit(1)

    mm_pending(len(pending))
    if pending:
        mm_info(f"Pending subtasks: {sorted(pending)}")

    # Build pending subtasks list from runtime state
    pending_subtasks = []
    for sid in sorted(pending):
        st_info = (
            state["subtasks"].get(sid)
            or ledger_subtasks.get(sid)
            or planned_subtasks_by_id[sid]
        )
        pending_subtasks.append(
            {
                "id": sid,
                "description": st_info.get("description", sid),
                "completed": False,
            }
        )

    # Detect permissions for pending subtasks
    permission_warnings = detect_required_permissions(task_id, pending_subtasks)
    if permission_warnings:
        mm_info("PERMISSION CHECK:")
        for warning in permission_warnings:
            emit(warning, flush=True)
        mm_info(
            "Please ensure Claude Code has these permissions enabled in settings.json"
        )

    # Update runtime state with new session
    resumed_at = _now_compatible_with(state.get("started_at"))
    session_id = f"sess-resume-{resumed_at.strftime('%Y%m%d-%H%M%S')}"
    state["session_id"] = session_id
    state["resumed_at"] = resumed_at.isoformat()
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
        "task_title": read_task_from_plan(
            task_id, objective_slug=runtime_objective_slug
        )["title"],
        "planning_mode": state.get("source_mode", "objective"),
        "objective_slug": state.get("objective_slug"),
        "plan_path": state.get("plan_path"),
        "todo_path": state.get("todo_path"),
        "subtasks": pending_subtasks,
        "total_subtasks": len(expected_subtask_ids),
        "pending_count": len(pending_subtasks),
        "context_budget_threshold": 0.75,
        "resume": True,
        "resumed_from_checkpoint": state.get("last_checkpoint"),
    }
    emit("LAUNCH: task-executor", flush=True)
    emit(f"PAYLOAD: {json.dumps(payload)}", flush=True)
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
    changes_dir = (PLANNING_DIR / "changes").resolve()
    if not changes_dir.exists():
        raise ValueError(f"No objective packages found under {PLANNING_LABEL}/changes")

    resolved_objectives: list[tuple[Path, Path, dict[str, Any] | None]] = []
    for objective_entry in sorted(changes_dir.iterdir()):
        if not objective_entry.is_dir():
            continue
        objective_dir = get_objective_dir(objective_entry.name)
        tasks_path = objective_artifact_path(objective_dir, "tasks.md")
        if not tasks_path.exists():
            continue
        objective_state = load_objective_state(objective_slug=objective_dir.name)
        resolved_objectives.append((objective_dir, tasks_path, objective_state))

    projection_paths: list[Path] = []
    for objective_dir, _tasks_path, _objective_state in resolved_objectives:
        projection_paths.extend(
            [
                objective_artifact_path(objective_dir, "todo.md"),
                objective_artifact_path(objective_dir, "HANDOFF-CURRENT.md"),
            ]
        )
    snapshot = _snapshot_artifacts(tuple(projection_paths))
    try:
        for objective_dir, tasks_path, objective_state in resolved_objectives:
            if objective_state and objective_state.get("status") == "planned":
                continue
            ensure_objective_todo(objective_dir, objective_dir.name)
            if objective_state and objective_state.get("tasks"):
                first_task_ids = get_task_ids_from_plan(tasks_path)
                if first_task_ids:
                    sync_objective_todo_from_state(
                        first_task_ids[0], objective_slug=objective_dir.name
                    )
    except (OSError, ValueError):
        _restore_artifacts(snapshot)
        raise

    mm_info("Task Status Overview")
    for objective_dir, tasks_path, objective_state in resolved_objectives:
        todo_path = objective_artifact_path(objective_dir, "todo.md")
        if not todo_path.exists():
            continue
        emit(f"\n  [{objective_dir.name}]", flush=True)
        objective_content = tasks_path.read_text(encoding="utf-8")
        for match in re.finditer(
            r"^## ([A-Z]{1,4}\d+):([^\n]+)$", objective_content, re.MULTILINE
        ):
            task_id = match.group(1)
            title = match.group(2).strip()
            durable_status = get_objective_task_status(
                task_id, objective_slug=objective_dir.name
            )
            if durable_status == "completed":
                checkbox_state = "x"
            elif durable_status == "in_progress":
                checkbox_state = "~"
            else:
                checkbox_state = " "

            task_entry = (
                objective_state.get("tasks", {}).get(task_id, {})
                if objective_state
                else {}
            )
            subtask_entries = task_entry.get("subtasks", {})
            total = len(subtask_entries)
            completed = sum(
                1
                for subtask in subtask_entries.values()
                if subtask.get("status") == "completed"
            )
            if checkbox_state == "x":
                status = "✅"
            elif checkbox_state == "~":
                status = f"[~] {completed}/{total}"
            else:
                status = f"[ ] {completed}/{total}"
            sync_suffix = ""
            state = load_runtime_state()
            if (
                state is not None
                and state.get("task_id") == task_id
                and state.get("objective_slug") == objective_dir.name
            ):
                issues = audit_task_consistency(
                    task_id, objective_slug=objective_dir.name
                )
                if issues:
                    sync_suffix = f" ⚠ sync:{len(issues)}"
            emit(f"    {task_id} {status}: {title}{sync_suffix}", flush=True)


def reset_stale_subtasks(task_id: str, objective_slug: str | None = None) -> None:
    """Reset stale in_progress subtasks to pending.

    Finds subtasks in in_progress > 1 hour and resets them to pending,
    incrementing retries counter.

    Args:
        task_id: Task identifier (e.g., "B2").
    """
    source = resolve_task_source(task_id, objective_slug=objective_slug)
    try:
        state = _require_runtime_state()
    except (OSError, ValueError) as exc:
        mm_error(str(exc))
        sys.exit(1)

    runtime_objective_slug = state["objective_slug"]
    if runtime_objective_slug != source.objective_slug:
        mm_error(
            f"Runtime state belongs to objective `{runtime_objective_slug}`, "
            f"not requested objective `{source.objective_slug}`"
        )
        sys.exit(1)

    if state.get("task_id") != task_id:
        mm_error(f"Runtime state is for task {state.get('task_id')}, not {task_id}")
        sys.exit(1)

    objective_state = load_objective_state(objective_slug=runtime_objective_slug)
    if objective_state is None:
        raise ValueError(
            f"No objective execution state found for `{runtime_objective_slug}`"
        )

    stale_ids: list[str] = []
    stale_threshold = 1 * 60 * 60
    for sid, subtask in state["subtasks"].items():
        if subtask.get("status") != "in_progress" or not subtask.get("started_at"):
            continue
        try:
            started = datetime.fromisoformat(subtask["started_at"])
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Invalid stale timestamp for {sid}: {exc}") from exc
        if (
            _now_compatible_with(subtask["started_at"]) - started
        ).total_seconds() > stale_threshold:
            stale_ids.append(sid)

    if not stale_ids:
        mm_info("No stale subtasks found (all in_progress < 1 hour)")
        return

    with _objective_artifact_transaction(runtime_objective_slug):
        state = _normalize_runtime_state_to_plan(state, task_id, runtime_objective_slug)
        _normalize_durable_task_to_plan(objective_state, source, task_id)
        state = _advance_runtime_from_durable_completion(
            state, objective_state, task_id
        )

        reset_count = 0

        for sid in stale_ids:
            subtask = state["subtasks"].get(sid)
            if subtask is None:
                continue
            if subtask.get("status") != "in_progress":
                continue
            retries = subtask.get("retries", 0) + 1
            subtask["status"] = "pending"
            subtask["started_at"] = None
            subtask["retries"] = retries
            durable = objective_state["tasks"][task_id]["subtasks"][sid]
            durable["status"] = "pending"
            durable["started_at"] = None
            durable["retries"] = retries
            reset_count += 1
            mm_info(f"Reset {sid} to pending (retry #{retries})")

        if reset_count > 0:
            state["last_checkpoint"] = None
            durable_task = objective_state["tasks"][task_id]
            durable_task["status"] = _aggregate_parent_status(
                [entry["status"] for entry in durable_task["subtasks"].values()]
            )
            durable_task["completed_at"] = None
            RUNTIME_STATE_PATH.write_text(json.dumps(state, indent=2))
            save_objective_state(objective_state)
            mm_info(f"Reset {reset_count} stale subtask(s)")
            mm_info(f"Usá /mm:complete-task {task_id} --continue para reanudar")
        if not sync_task_acceptance_criteria(
            task_id, objective_slug=runtime_objective_slug
        ):
            raise ValueError(f"Cannot reset {task_id}: acceptance projection failed")
        sync_objective_todo_from_state(task_id, objective_slug=runtime_objective_slug)


def mark_done(subtask_id: str) -> None:
    """Mark a subtask complete through normalized runtime/durable state.

    This is the canonical way for task-executor to mark subtasks done. Derived
    todo, acceptance, and handoff artifacts are projected only after durable
    state is persisted.

    Args:
        subtask_id: Subtask ID to mark done (e.g., "B1.09").
    """
    subtask_id = subtask_id.upper()

    try:
        state = _require_runtime_state()
    except ValueError as exc:
        mm_error(str(exc))
        sys.exit(1)

    objective_slug = state["objective_slug"]

    try:
        update_subtask_status(subtask_id, "completed")
    except (OSError, ValueError) as e:
        mm_error(f"Failed to mark {subtask_id} as complete: {e}")
        sys.exit(1)

    mm_info(f"Marked {subtask_id} as complete")

    # Re-read state to report parent propagation result
    updated_state = load_runtime_state()
    if updated_state is not None:
        try:
            if "." in subtask_id:
                parent_id = subtask_id.rsplit(".", 1)[0]
                _, todo_path = get_active_paths(
                    subtask_id, objective_slug=objective_slug
                )
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
        except (OSError, ValueError):
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

    try:
        _require_runtime_state()
    except (OSError, ValueError) as exc:
        mm_error(str(exc))
        sys.exit(1)

    try:
        update_subtask_status(subtask_id, "in_progress")
    except (OSError, ValueError) as e:
        mm_error(f"Failed to mark {subtask_id} as in_progress: {e}")
        sys.exit(1)

    mm_info(f"Marked {subtask_id} as in_progress")


def _normalize_task_id(raw: str) -> str:
    """Strip objective-slug prefix that agents sometimes prepend (e.g. 'bulk-upload-csv-import/T4' → 'T4')."""
    return raw.upper().split("/")[-1]


def _main_unlocked() -> None:
    """Main entry point."""
    help_flags = {"-h", "--help", "help"}

    if len(sys.argv) < 2:
        emit(
            "Usage: mm-complete-task <TASK_ID> [--continue] [--status] [--reset-stale] [--reconcile]",
            flush=True,
        )
        emit("       mm-complete-task --status  # Show all tasks", flush=True)
        emit(
            "       mm-complete-task --mark-done <SUBTASK_ID>       # Mark subtask complete",
            flush=True,
        )
        emit(
            "       mm-complete-task --mark-in-progress <SUBTASK_ID>  # Mark subtask started",
            flush=True,
        )
        emit(
            "       mm-complete-task --reconcile <TASK_ID>  # Repair todo/handoff from runtime truth",
            flush=True,
        )
        emit(
            "       mm-complete-task --resync-objective <OBJECTIVE>  # Rebuild execution-state/todo/handoffs from objective artifacts",
            flush=True,
        )
        emit(
            "       mm-complete-task --brief <TASK_ID>  # Print a concise model handoff brief",
            flush=True,
        )
        sys.exit(1)

    if sys.argv[1] in help_flags:
        emit(
            "Usage: mm-complete-task <TASK_ID> [--continue] [--status] [--reset-stale] [--reconcile]",
            flush=True,
        )
        emit("       mm-complete-task --status  # Show all tasks", flush=True)
        emit(
            "       mm-complete-task --mark-done <SUBTASK_ID>       # Mark subtask complete",
            flush=True,
        )
        emit(
            "       mm-complete-task --mark-in-progress <SUBTASK_ID>  # Mark subtask started",
            flush=True,
        )
        emit(
            "       mm-complete-task --reconcile <TASK_ID>  # Repair todo/handoff from runtime truth",
            flush=True,
        )
        emit(
            "       mm-complete-task --resync-objective <OBJECTIVE>  # Rebuild execution-state/todo/handoffs from objective artifacts",
            flush=True,
        )
        emit(
            "       mm-complete-task --brief <TASK_ID>  # Print a concise model handoff brief",
            flush=True,
        )
        return

    # Status mode
    if sys.argv[1] == "--status":
        try:
            show_status()
        except (OSError, ValueError) as exc:
            mm_error(str(exc))
            sys.exit(1)
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
        try:
            task_ref = _split_objective_task_ref(sys.argv[2])
        except (OSError, ValueError) as exc:
            mm_error(str(exc))
            sys.exit(1)
        task_id = task_ref.task_id
        if not reconcile_artifacts_from_runtime(
            task_id, objective_slug=task_ref.objective_slug
        ):
            sys.exit(1)
        issues = audit_task_consistency(task_id, objective_slug=task_ref.objective_slug)
        if issues:
            for issue in issues:
                mm_error(f"SYNC: {issue}")
            sys.exit(1)
        mm_status(f"RECONCILED {task_id}")
        return

    if sys.argv[1] == "--resync-objective":
        if len(sys.argv) < 3:
            mm_error("Usage: mm-complete-task --resync-objective <OBJECTIVE>")
            mm_error("Example: mm-complete-task --resync-objective window-scheduler")
            sys.exit(1)
        objective_slug = sys.argv[2].strip().lower()
        try:
            resync_objective_artifacts(objective_slug)
        except (OSError, ValueError) as exc:
            mm_error(str(exc))
            sys.exit(1)
        mm_status(f"RESYNCED {objective_slug}")
        return

    if sys.argv[1] == "--brief":
        if len(sys.argv) < 3:
            mm_error("Usage: mm-complete-task --brief <TASK_ID>")
            mm_error("Example: mm-complete-task --brief AV2")
            sys.exit(1)
        try:
            task_ref = _split_objective_task_ref(sys.argv[2])
            brief = build_model_brief(
                task_ref.task_id, objective_slug=task_ref.objective_slug
            )
        except (OSError, ValueError) as exc:
            mm_error(str(exc))
            sys.exit(1)
        mm_model_brief(brief)
        return

    positional_args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]
    if not positional_args:
        mm_error("Usage: mm-complete-task <TASK_ID> [--continue|--brief|--reset-stale]")
        sys.exit(1)

    try:
        task_ref = _split_objective_task_ref(positional_args[0])
    except (OSError, ValueError) as exc:
        mm_error(str(exc))
        sys.exit(1)
    task_id = task_ref.task_id

    if "--brief" in sys.argv:
        try:
            brief = build_model_brief(task_id, objective_slug=task_ref.objective_slug)
        except (OSError, ValueError) as exc:
            mm_error(str(exc))
            sys.exit(1)
        mm_model_brief(brief)
        return

    # Reset stale mode
    if "--reset-stale" in sys.argv:
        try:
            reset_stale_subtasks(task_id, objective_slug=task_ref.objective_slug)
        except (OSError, ValueError) as exc:
            mm_error(str(exc))
            sys.exit(1)
        return

    resume_mode = "--continue" in sys.argv

    try:
        if resume_mode:
            resume_task(task_id, objective_slug=task_ref.objective_slug)
        else:
            start_task(task_id, objective_slug=task_ref.objective_slug)
    except (OSError, ValueError) as exc:
        mm_error(f"Cannot complete {task_id}: {exc}")
        sys.exit(1)


def main() -> None:
    """Run read-only modes directly and serialize every mutating CLI flow."""
    read_only = any(arg in {"-h", "--help", "help", "--brief"} for arg in sys.argv[1:])
    if read_only or len(sys.argv) < 2:
        _main_unlocked()
        return
    try:
        with _mutation_lock():
            _main_unlocked()
    except (OSError, ValueError) as exc:
        mm_error(str(exc))
        sys.exit(1)


if __name__ == "__main__":
    main()
