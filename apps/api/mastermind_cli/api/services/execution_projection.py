"""Canonical/legacy execution projection service for Strategy Vault."""

from __future__ import annotations

import base64
import json
import sqlite3
from datetime import datetime
from typing import Any

from sqlalchemy import asc, desc, select

from mastermind_cli.api.models.execution import (
    BrainOutput,
    Execution,
    ExecutionHistoryResponse,
    ExecutionSummary,
    SnapshotMilestone,
)
from mastermind_cli.types.status import ExecutionStatus
from mastermind_cli.project_state.database.session import get_session_factory
from mastermind_cli.project_state.models.artifact import ArtifactVersion
from mastermind_cli.project_state.models.checkpoint import Checkpoint
from mastermind_cli.project_state.models.task import Task
from mastermind_cli.project_state.models.task_run import TaskRun


def user_task_project_id(user_id: str) -> str:
    """Return the transitional project_state scope for legacy user executions."""
    return f"user-tasks:{user_id}"


def encode_cursor(execution_id: str) -> str:
    """Base64-encode an execution ID for cursor-based pagination."""
    return base64.urlsafe_b64encode(execution_id.encode()).decode()


def decode_cursor(cursor: str) -> str | None:
    """Decode a cursor back to execution ID. Returns None on invalid cursor."""
    try:
        return base64.urlsafe_b64decode(cursor.encode()).decode()
    except Exception:
        return None


def _parse_milestones(raw: str) -> list[SnapshotMilestone]:
    """Parse milestones from JSON string. Returns [] on error."""
    try:
        data = json.loads(raw) if isinstance(raw, str) else raw
        if not isinstance(data, list):
            return []
        return [SnapshotMilestone(**milestone) for milestone in data]
    except Exception:
        return []


def _parse_brain_outputs(raw: str) -> dict[str, BrainOutput]:
    """Parse brain outputs from JSON string. Returns {} on error."""
    try:
        data = json.loads(raw) if isinstance(raw, str) else raw
        if not isinstance(data, dict):
            return {}
        return {key: BrainOutput(**value) for key, value in data.items()}
    except Exception:
        return {}


def _parse_graph_snapshot(raw: str) -> dict[str, object]:
    """Parse graph snapshot from JSON string. Returns {} on error."""
    try:
        data = json.loads(raw) if isinstance(raw, str) else raw
        if not isinstance(data, dict):
            return {}
        return dict(data)
    except Exception:
        return {}


def _row_to_summary(row: tuple[Any, ...]) -> ExecutionSummary:
    """Convert a DB row to ExecutionSummary."""
    created_at = row[6]
    if isinstance(created_at, str):
        try:
            created_at = datetime.fromisoformat(created_at)
        except ValueError:
            created_at = datetime.utcnow()

    return ExecutionSummary(
        id=row[0],
        task_id=row[1],
        brief=str(row[2])[:200],
        status=(
            ExecutionStatus(str(row[3]))
            if row[3] in {"success", "error", "running"}
            else ExecutionStatus.RUNNING
        ),
        duration_ms=int(row[4]) if row[4] else 0,
        brain_count=int(row[5]) if row[5] else 1,
        created_at=created_at,
    )


def _row_to_execution(row: tuple[Any, ...]) -> Execution:
    """Convert a full legacy DB row to Execution."""
    created_at = row[6]
    if isinstance(created_at, str):
        try:
            created_at = datetime.fromisoformat(created_at)
        except ValueError:
            created_at = datetime.utcnow()

    return Execution(
        id=row[0],
        task_id=row[1],
        brief=str(row[2])[:200],
        status=(
            ExecutionStatus(str(row[3]))
            if row[3] in {"success", "error", "running"}
            else ExecutionStatus.RUNNING
        ),
        duration_ms=int(row[4]) if row[4] else 0,
        brain_count=max(1, int(row[5]) if row[5] else 1),
        created_at=created_at,
        milestones=_parse_milestones(row[7] or "[]"),
        brain_outputs=_parse_brain_outputs(row[8] or "{}"),
        graph_snapshot=_parse_graph_snapshot(row[9] or "{}"),
    )


def _normalize_execution_status(status: str) -> ExecutionStatus:
    """Map transitional task/run statuses to the execution API contract."""
    if status in {"success", "error", "running"}:
        return ExecutionStatus(status)
    if status == "completed":
        return ExecutionStatus.SUCCESS
    if status == "failed":
        return ExecutionStatus.ERROR
    return ExecutionStatus.RUNNING


def _read_canonical_brain_outputs(
    database_url: str,
    *,
    project_id: str,
    run_id: str,
) -> dict[str, BrainOutput]:
    """Load canonical brain outputs from the transitional execution artifact."""
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        artifact = session.execute(
            select(ArtifactVersion)
            .where(
                ArtifactVersion.project_id == project_id,
                ArtifactVersion.artifact_type == "execution_output_bundle",
                ArtifactVersion.artifact_id == f"execution-output:{run_id}",
            )
            .order_by(desc(ArtifactVersion.version))
            .limit(1)
        ).scalar_one_or_none()

    if artifact is None:
        return {}

    raw = artifact.metadata_json.get("brain_outputs")
    if not isinstance(raw, dict):
        return {}

    parsed: dict[str, BrainOutput] = {}
    for key, value in raw.items():
        if isinstance(key, str) and isinstance(value, dict):
            try:
                parsed[key] = BrainOutput(**value)
            except Exception:
                continue
    return parsed


def _derive_brain_count(
    database_url: str,
    *,
    project_id: str,
    run_id: str,
) -> int:
    """Derive brain_count from canonical brain outputs when available."""
    brain_outputs = _read_canonical_brain_outputs(
        database_url,
        project_id=project_id,
        run_id=run_id,
    )
    return max(1, len(brain_outputs)) if brain_outputs else 1


def _build_minimal_milestones(
    database_url: str,
    *,
    run: TaskRun,
    brain_count: int,
) -> list[SnapshotMilestone]:
    """Build a canonical milestone timeline from run timestamps plus checkpoints."""
    started_ms = int(run.started_at.timestamp() * 1000)
    milestones: list[SnapshotMilestone] = [
        SnapshotMilestone(
            index=0,
            timestamp=started_ms,
            label="Task started",
            brain_count=0,
        )
    ]

    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        checkpoints = list(
            session.execute(
                select(Checkpoint)
                .where(
                    Checkpoint.project_id == run.project_id,
                    Checkpoint.task_id == run.task_id,
                    Checkpoint.run_id == run.run_id,
                )
                .order_by(asc(Checkpoint.created_at))
            ).scalars()
        )

    for checkpoint in checkpoints:
        milestones.append(
            SnapshotMilestone(
                index=len(milestones),
                timestamp=int(checkpoint.created_at.timestamp() * 1000),
                label=checkpoint.next_step_summary[:200],
                brain_count=brain_count,
            )
        )

    if run.ended_at is not None:
        label = (
            "Task complete"
            if _normalize_execution_status(run.status) == "success"
            else "Task failed"
        )
        milestones.append(
            SnapshotMilestone(
                index=len(milestones),
                timestamp=int(run.ended_at.timestamp() * 1000),
                label=label,
                brain_count=brain_count,
            )
        )
    return milestones[:10]


def _task_run_to_summary(
    run: TaskRun,
    task: Task,
    *,
    database_url: str,
) -> ExecutionSummary:
    """Convert canonical task/run records into the legacy history summary shape."""
    duration_ms = 0
    if run.ended_at is not None:
        duration_ms = max(
            0,
            int((run.ended_at - run.started_at).total_seconds() * 1000),
        )

    brief = task.metadata_json.get("brief")
    brief_text = brief if isinstance(brief, str) and brief else task.title
    brain_count = _derive_brain_count(
        database_url,
        project_id=run.project_id,
        run_id=run.run_id,
    )

    return ExecutionSummary(
        id=run.run_id,
        task_id=run.task_id,
        brief=str(brief_text)[:200],
        status=_normalize_execution_status(run.status),
        duration_ms=duration_ms,
        brain_count=brain_count,
        created_at=run.started_at,
    )


def _derive_graph_snapshot(task: Task) -> dict[str, object]:
    """Derive a minimal replay snapshot from the canonical flow_config when available."""
    flow_config = task.metadata_json.get("flow_config")
    if not isinstance(flow_config, str) or not flow_config:
        return {}
    try:
        parsed = json.loads(flow_config)
    except json.JSONDecodeError:
        return {}
    if not isinstance(parsed, dict):
        return {}
    nodes = parsed.get("nodes")
    edges = parsed.get("edges")
    if nodes is None and edges is None:
        return {}
    if not isinstance(nodes, dict) and not isinstance(nodes, list):
        nodes = {}
    if not isinstance(edges, dict) and not isinstance(edges, list):
        edges = {}
    return {"nodes": nodes, "edges": edges}


def _task_run_to_execution(
    run: TaskRun,
    task: Task,
    *,
    database_url: str,
) -> Execution:
    """Convert canonical task/run records into a minimal execution detail projection."""
    duration_ms = 0
    if run.ended_at is not None:
        duration_ms = max(
            0,
            int((run.ended_at - run.started_at).total_seconds() * 1000),
        )

    brief = task.metadata_json.get("brief")
    brief_text = brief if isinstance(brief, str) and brief else task.title
    brain_outputs = _read_canonical_brain_outputs(
        database_url,
        project_id=run.project_id,
        run_id=run.run_id,
    )
    brain_count = max(1, len(brain_outputs)) if brain_outputs else 1

    return Execution(
        id=run.run_id,
        task_id=run.task_id,
        brief=str(brief_text)[:200],
        status=_normalize_execution_status(run.status),
        duration_ms=duration_ms,
        brain_count=brain_count,
        created_at=run.started_at,
        milestones=_build_minimal_milestones(
            database_url,
            run=run,
            brain_count=brain_count,
        ),
        brain_outputs=brain_outputs,
        graph_snapshot=_derive_graph_snapshot(task),
    )


def _ensure_legacy_execution_history_schema(connection: sqlite3.Connection) -> None:
    """Create the legacy execution_history table if it does not exist yet."""
    connection.executescript("""
        CREATE TABLE IF NOT EXISTS execution_history (
            id TEXT PRIMARY KEY,
            task_id TEXT UNIQUE NOT NULL,
            brief TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'running',
            duration_ms INTEGER NOT NULL DEFAULT 0,
            brain_count INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            milestones_json TEXT NOT NULL DEFAULT '[]',
            brain_outputs_json TEXT NOT NULL DEFAULT '{}',
            graph_snapshot_json TEXT NOT NULL DEFAULT '{}'
        );
        CREATE INDEX IF NOT EXISTS idx_execution_history_task_id
        ON execution_history(task_id);
        CREATE INDEX IF NOT EXISTS idx_execution_history_created_at
        ON execution_history(created_at DESC);
    """)


def _fetch_legacy_history_rows(
    *,
    db_path: str,
    cursor_id: str | None,
    limit: int,
    sort_direction: str,
    sort_asc: bool,
) -> list[tuple[Any, ...]]:
    """Read legacy execution history rows from SQLite without aiosqlite."""
    with sqlite3.connect(db_path) as connection:
        _ensure_legacy_execution_history_schema(connection)
        if cursor_id:
            cursor_row = connection.execute(
                "SELECT created_at FROM execution_history WHERE id = ?",
                (cursor_id,),
            ).fetchone()
            if cursor_row:
                cursor_ts = cursor_row[0]
                where = (
                    "(created_at > ? OR (created_at = ? AND id > ?))"
                    if sort_asc
                    else "(created_at < ? OR (created_at = ? AND id < ?))"
                )
                sql = f"""
                    SELECT id, task_id, brief, status, duration_ms, brain_count, created_at
                    FROM execution_history
                    WHERE {where}
                    ORDER BY created_at {sort_direction}, id {sort_direction}
                    LIMIT ?
                """
                return [
                    tuple(row)
                    for row in connection.execute(
                        sql,
                        (cursor_ts, cursor_ts, cursor_id, limit + 1),
                    ).fetchall()
                ]

        sql = f"""
            SELECT id, task_id, brief, status, duration_ms, brain_count, created_at
            FROM execution_history
            ORDER BY created_at {sort_direction}, id {sort_direction}
            LIMIT ?
        """
        return [tuple(row) for row in connection.execute(sql, (limit + 1,)).fetchall()]


def _fetch_legacy_execution_row(
    *,
    db_path: str,
    execution_id: str,
) -> tuple[Any, ...] | None:
    """Read one legacy execution detail row from SQLite without aiosqlite."""
    with sqlite3.connect(db_path) as connection:
        _ensure_legacy_execution_history_schema(connection)
        row = connection.execute(
            """SELECT id, task_id, brief, status, duration_ms, brain_count,
                      created_at, milestones_json, brain_outputs_json, graph_snapshot_json
               FROM execution_history
               WHERE id = ?""",
            (execution_id,),
        ).fetchone()
    return tuple(row) if row is not None else None


async def get_execution_history_projection(
    *,
    database_url: str,
    db_path: str,
    user_id: str,
    cursor: str | None,
    limit: int,
    sort: str,
) -> ExecutionHistoryResponse:
    """Return execution history from canonical data first, then legacy fallback."""
    sort_asc = sort.lower() == "oldest"
    sort_direction = "ASC" if sort_asc else "DESC"
    cursor_id = decode_cursor(cursor) if cursor else None

    project_id = user_task_project_id(user_id)
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        order_column = asc(TaskRun.started_at) if sort_asc else desc(TaskRun.started_at)
        id_order = asc(TaskRun.run_id) if sort_asc else desc(TaskRun.run_id)
        stmt = (
            select(TaskRun, Task)
            .join(
                Task,
                (Task.task_id == TaskRun.task_id)
                & (Task.project_id == TaskRun.project_id),
            )
            .where(TaskRun.project_id == project_id)
            .order_by(order_column, id_order)
        )

        if cursor_id:
            cursor_run = session.execute(
                select(TaskRun).where(
                    TaskRun.project_id == project_id,
                    TaskRun.run_id == cursor_id,
                )
            ).scalar_one_or_none()
            if cursor_run is not None:
                if sort_asc:
                    stmt = stmt.where(
                        (TaskRun.started_at > cursor_run.started_at)
                        | (
                            (TaskRun.started_at == cursor_run.started_at)
                            & (TaskRun.run_id > cursor_run.run_id)
                        )
                    )
                else:
                    stmt = stmt.where(
                        (TaskRun.started_at < cursor_run.started_at)
                        | (
                            (TaskRun.started_at == cursor_run.started_at)
                            & (TaskRun.run_id < cursor_run.run_id)
                        )
                    )

        rows = session.execute(stmt.limit(limit + 1)).all()

    if rows:
        has_more = len(rows) > limit
        page_rows = rows[:limit]
        executions = [
            _task_run_to_summary(run, task, database_url=database_url)
            for run, task in page_rows
        ]
        next_cursor = encode_cursor(page_rows[-1][0].run_id) if has_more else None
        return ExecutionHistoryResponse(
            executions=executions,
            next_cursor=next_cursor,
            has_more=has_more,
        )

    legacy_rows = _fetch_legacy_history_rows(
        db_path=db_path,
        cursor_id=cursor_id,
        limit=limit,
        sort_direction=sort_direction,
        sort_asc=sort_asc,
    )

    has_more = len(legacy_rows) > limit
    legacy_page_rows = legacy_rows[:limit]
    executions = [_row_to_summary(row) for row in legacy_page_rows]
    next_cursor = (
        encode_cursor(legacy_page_rows[-1][0])
        if has_more and legacy_page_rows
        else None
    )
    return ExecutionHistoryResponse(
        executions=executions,
        next_cursor=next_cursor,
        has_more=has_more,
    )


async def get_execution_detail_projection(
    *,
    database_url: str,
    db_path: str,
    user_id: str,
    execution_id: str,
) -> Execution:
    """Return execution detail from canonical data first, then legacy fallback."""
    project_id = user_task_project_id(user_id)
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        canonical_row = session.execute(
            select(TaskRun, Task)
            .join(
                Task,
                (Task.task_id == TaskRun.task_id)
                & (Task.project_id == TaskRun.project_id),
            )
            .where(
                TaskRun.project_id == project_id,
                TaskRun.run_id == execution_id,
            )
        ).one_or_none()
    if canonical_row is not None:
        run, task = canonical_row
        return _task_run_to_execution(run, task, database_url=database_url)

    row = _fetch_legacy_execution_row(db_path=db_path, execution_id=execution_id)

    if row is None:
        raise LookupError("Execution not found")

    return _row_to_execution(row)
