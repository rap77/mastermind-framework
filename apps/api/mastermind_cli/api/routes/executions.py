"""Execution history REST endpoints for Strategy Vault.

Provides paginated execution history and per-execution detail views
for the Strategy Vault frontend screen.

Endpoints:
    GET /api/executions/history   - Paginated list (cursor-based)
    GET /api/executions/{id}      - Full execution detail with brain outputs

Requirements: SV-01, SV-02
"""

import base64
import json
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from mastermind_cli.api.dependencies import get_db_path
from mastermind_cli.api.models.execution import (
    BrainOutput,
    Execution,
    ExecutionHistoryResponse,
    ExecutionSummary,
    SnapshotMilestone,
)
from mastermind_cli.api.routes.auth import get_current_user_any
from mastermind_cli.state.database import DatabaseConnection

router = APIRouter()

_DEFAULT_LIMIT = 10
_MAX_LIMIT = 20


def _encode_cursor(execution_id: str) -> str:
    """Base64-encode an execution ID for cursor-based pagination."""
    return base64.urlsafe_b64encode(execution_id.encode()).decode()


def _decode_cursor(cursor: str) -> str | None:
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
        return [SnapshotMilestone(**m) for m in data]
    except Exception:
        return []


def _parse_brain_outputs(raw: str) -> dict[str, BrainOutput]:
    """Parse brain outputs from JSON string. Returns {} on error."""
    try:
        data = json.loads(raw) if isinstance(raw, str) else raw
        if not isinstance(data, dict):
            return {}
        return {k: BrainOutput(**v) for k, v in data.items()}
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
    """Convert a DB row to ExecutionSummary.

    Row columns: id, task_id, brief, status, duration_ms, brain_count, created_at
    """
    created_at = row[6]
    if isinstance(created_at, str):
        # SQLite stores timestamps as strings
        try:
            created_at = datetime.fromisoformat(created_at)
        except ValueError:
            created_at = datetime.utcnow()

    return ExecutionSummary(
        id=row[0],
        task_id=row[1],
        brief=str(row[2])[:200],
        status=row[3] if row[3] in {"success", "error", "running"} else "running",
        duration_ms=int(row[4]) if row[4] else 0,
        brain_count=int(row[5]) if row[5] else 1,
        created_at=created_at,
    )


def _row_to_execution(row: tuple[Any, ...]) -> Execution:
    """Convert a full DB row to Execution.

    Row columns: id, task_id, brief, status, duration_ms, brain_count,
                 created_at, milestones_json, brain_outputs_json, graph_snapshot_json
    """
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
        status=row[3] if row[3] in {"success", "error", "running"} else "running",
        duration_ms=int(row[4]) if row[4] else 0,
        brain_count=max(1, int(row[5]) if row[5] else 1),
        created_at=created_at,
        milestones=_parse_milestones(row[7] or "[]"),
        brain_outputs=_parse_brain_outputs(row[8] or "{}"),
        graph_snapshot=_parse_graph_snapshot(row[9] or "{}"),
    )


@router.get("/history", response_model=ExecutionHistoryResponse)
async def get_execution_history(
    cursor: Optional[str] = Query(
        default=None,
        description="Base64-encoded execution ID for cursor pagination (null = from newest)",
    ),
    limit: int = Query(
        default=_DEFAULT_LIMIT,
        ge=1,
        le=_MAX_LIMIT,
        description=f"Page size (default={_DEFAULT_LIMIT}, max={_MAX_LIMIT})",
    ),
    sort: str = Query(
        default="newest",
        description="Sort order: 'newest' (default) or 'oldest'",
    ),
    user_id: str = Depends(get_current_user_any),
    db_path: str = Depends(get_db_path),
) -> ExecutionHistoryResponse:
    """Get paginated execution history.

    Uses cursor-based pagination (stable under concurrent writes).
    The cursor is a base64-encoded execution ID.

    Returns:
        ExecutionHistoryResponse with executions, next_cursor, has_more
    """
    # Validate sort param — gracefully default to newest
    sort_asc = sort.lower() == "oldest"
    sort_direction = "ASC" if sort_asc else "DESC"

    # Decode cursor (invalid cursor → reset to beginning)
    cursor_id: str | None = None
    if cursor:
        cursor_id = _decode_cursor(cursor)
        # If decode failed, cursor_id is None → pagination starts from newest

    async with DatabaseConnection(db_path) as db:
        # Ensure schema exists (for tests that call endpoint without startup)
        await db.create_execution_history_schema()

        if cursor_id:
            # Cursor-based: fetch records after/before the cursor ID by rowid
            # SQLite doesn't have UUID ordering by insertion, so we use created_at
            # First, get the created_at of the cursor record
            cursor_row = await db.conn.execute(
                "SELECT created_at FROM execution_history WHERE id = ?",
                [cursor_id],
            )
            cursor_record = await cursor_row.fetchone()

            if cursor_record:
                cursor_ts = cursor_record[0]
                # Composite (created_at, id) comparison — avoids skipping records
                # with identical timestamps (race condition with concurrent writes)
                if sort_asc:
                    where = "(created_at > ? OR (created_at = ? AND id > ?))"
                else:
                    where = "(created_at < ? OR (created_at = ? AND id < ?))"
                sql = f"""
                    SELECT id, task_id, brief, status, duration_ms, brain_count, created_at
                    FROM execution_history
                    WHERE {where}
                    ORDER BY created_at {sort_direction}, id {sort_direction}
                    LIMIT ?
                """
                cursor_result = await db.conn.execute(
                    sql, [cursor_ts, cursor_ts, cursor_id, limit + 1]
                )
            else:
                # Cursor ID not found in DB → reset to beginning
                sql = f"""
                    SELECT id, task_id, brief, status, duration_ms, brain_count, created_at
                    FROM execution_history
                    ORDER BY created_at {sort_direction}, id {sort_direction}
                    LIMIT ?
                """
                cursor_result = await db.conn.execute(sql, [limit + 1])
        else:
            # No cursor → from the beginning (newest or oldest)
            sql = f"""
                SELECT id, task_id, brief, status, duration_ms, brain_count, created_at
                FROM execution_history
                ORDER BY created_at {sort_direction}, id {sort_direction}
                LIMIT ?
            """
            cursor_result = await db.conn.execute(sql, [limit + 1])

        raw_rows = await cursor_result.fetchall()
        rows: list[tuple[Any, ...]] = [tuple(r) for r in raw_rows]

    has_more = len(rows) > limit
    page_rows = rows[:limit]

    executions = [_row_to_summary(r) for r in page_rows]

    next_cursor: str | None = None
    if has_more and page_rows:
        last_id = page_rows[-1][0]
        next_cursor = _encode_cursor(last_id)

    return ExecutionHistoryResponse(
        executions=executions,
        next_cursor=next_cursor,
        has_more=has_more,
    )


@router.get("/{execution_id}", response_model=Execution)
async def get_execution_detail(
    execution_id: str,
    user_id: str = Depends(get_current_user_any),
    db_path: str = Depends(get_db_path),
) -> Execution:
    """Get full execution detail with brain outputs.

    Returns the complete Execution record including:
    - milestones: Timeline snapshots (max 10)
    - brain_outputs: Per-brain Markdown output dict
    - graph_snapshot: Final DAG state for replay

    Note: No caching — user might trigger new runs mid-session.

    Returns:
        Execution schema with all fields populated

    Raises:
        404: If execution not found
        401: If JWT missing/invalid
    """
    async with DatabaseConnection(db_path) as db:
        # Ensure schema exists
        await db.create_execution_history_schema()

        cursor = await db.conn.execute(
            """SELECT id, task_id, brief, status, duration_ms, brain_count,
                      created_at, milestones_json, brain_outputs_json, graph_snapshot_json
               FROM execution_history
               WHERE id = ?""",
            [execution_id],
        )
        row = await cursor.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Execution not found")

    return _row_to_execution(tuple(row))
