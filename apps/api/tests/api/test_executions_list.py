"""Tests for GET /api/executions/history (paginated list).

Requirements: SV-01 (Strategy Vault — execution history list)
"""

import uuid
from datetime import datetime, timedelta

import pytest

from mastermind_cli.state.database import DatabaseConnection


async def _insert_execution(
    db_path: str,
    task_id: str,
    brief: str,
    status: str = "success",
    created_at: datetime | None = None,
) -> str:
    """Helper: insert an execution_history record for tests."""
    exec_id = str(uuid.uuid4())
    ts = (created_at or datetime.utcnow()).isoformat()
    async with DatabaseConnection(db_path) as db:
        await db.create_execution_history_schema()
        await db.conn.execute(
            """INSERT INTO execution_history
               (id, task_id, brief, status, duration_ms, brain_count,
                created_at, milestones_json, brain_outputs_json, graph_snapshot_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [exec_id, task_id, brief[:200], status, 1000, 3, ts, "[]", "{}", "{}"],
        )
        await db.conn.commit()
    return exec_id


@pytest.mark.asyncio
async def test_get_executions_history_empty(client, auth_headers) -> None:
    """No executions → empty list with has_more=false and next_cursor=null."""
    response = await client.get("/api/executions/history", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["executions"] == []
    assert data["next_cursor"] is None
    assert data["has_more"] is False


@pytest.mark.asyncio
async def test_get_executions_history_auth_required(client) -> None:
    """Missing JWT → 401 or 403."""
    response = await client.get("/api/executions/history")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_get_executions_history_pagination(client, auth_headers, db_path) -> None:
    """Create 12 executions, limit=5 → first page has 5 items, has_more=True."""
    # Insert 12 executions with different timestamps
    for i in range(12):
        ts = datetime(2026, 3, 1, 12, 0, 0) + timedelta(minutes=i)
        await _insert_execution(
            db_path,
            task_id=f"task-{i:03d}",
            brief=f"Brief {i}",
            created_at=ts,
        )

    response = await client.get("/api/executions/history?limit=5", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["executions"]) == 5
    assert data["has_more"] is True
    assert data["next_cursor"] is not None


@pytest.mark.asyncio
async def test_get_executions_history_cursor_pagination(
    client, auth_headers, db_path
) -> None:
    """Cursor pagination: second page returns the next batch of results."""
    for i in range(8):
        ts = datetime(2026, 3, 1, 12, 0, 0) + timedelta(minutes=i)
        await _insert_execution(
            db_path,
            task_id=f"task-cursor-{i:03d}",
            brief=f"Brief cursor {i}",
            created_at=ts,
        )

    # First page (limit=3)
    r1 = await client.get("/api/executions/history?limit=3", headers=auth_headers)
    assert r1.status_code == 200
    d1 = r1.json()
    assert len(d1["executions"]) == 3
    assert d1["has_more"] is True
    cursor = d1["next_cursor"]
    assert cursor is not None

    # Second page using cursor
    r2 = await client.get(
        f"/api/executions/history?limit=3&cursor={cursor}", headers=auth_headers
    )
    assert r2.status_code == 200
    d2 = r2.json()
    assert len(d2["executions"]) > 0

    # No overlap between pages
    ids_p1 = {e["id"] for e in d1["executions"]}
    ids_p2 = {e["id"] for e in d2["executions"]}
    assert ids_p1.isdisjoint(ids_p2)


@pytest.mark.asyncio
async def test_get_executions_history_sort_order_newest(
    client, auth_headers, db_path
) -> None:
    """Default sort is 'newest' (descending created_at)."""
    base_ts = datetime(2026, 3, 1, 12, 0, 0)
    for i in range(3):
        await _insert_execution(
            db_path,
            task_id=f"task-sort-{i}",
            brief=f"Sort test {i}",
            created_at=base_ts + timedelta(minutes=i),
        )

    response = await client.get(
        "/api/executions/history?limit=10", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["executions"]) == 3

    # Verify descending order (newest first)
    dates = [e["created_at"] for e in data["executions"]]
    assert dates == sorted(dates, reverse=True) or len(set(dates)) == 1


@pytest.mark.asyncio
async def test_get_executions_history_sort_oldest(
    client, auth_headers, db_path
) -> None:
    """sort=oldest returns ascending order."""
    base_ts = datetime(2026, 3, 1, 12, 0, 0)
    for i in range(3):
        await _insert_execution(
            db_path,
            task_id=f"task-oldest-{i}",
            brief=f"Oldest test {i}",
            created_at=base_ts + timedelta(minutes=i),
        )

    response = await client.get(
        "/api/executions/history?limit=10&sort=oldest", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["executions"]) == 3

    dates = [e["created_at"] for e in data["executions"]]
    assert dates == sorted(dates)


@pytest.mark.asyncio
async def test_get_executions_history_cursor_invalid(
    client, auth_headers, db_path
) -> None:
    """Invalid cursor → graceful reset to beginning (no 500 error)."""
    await _insert_execution(db_path, task_id="task-inv", brief="Invalid cursor test")

    response = await client.get(
        "/api/executions/history?cursor=INVALID_CURSOR_DATA", headers=auth_headers
    )
    # Should not crash — graceful degradation
    assert response.status_code == 200
    data = response.json()
    assert "executions" in data


@pytest.mark.asyncio
async def test_get_executions_history_limit_max(client, auth_headers) -> None:
    """limit > 20 is clamped to 20 (max limit enforced)."""
    response = await client.get(
        "/api/executions/history?limit=100", headers=auth_headers
    )
    # Should be rejected (422) due to Query(le=20)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_executions_history_response_shape(
    client, auth_headers, db_path
) -> None:
    """Response has correct field shapes for ExecutionSummary items."""
    await _insert_execution(
        db_path,
        task_id="task-shape",
        brief="Shape test brief",
        status="success",
    )

    response = await client.get("/api/executions/history?limit=5", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    assert len(data["executions"]) >= 1
    exec_item = data["executions"][0]

    # Required fields for ExecutionSummary
    assert "id" in exec_item
    assert "task_id" in exec_item
    assert "brief" in exec_item
    assert "status" in exec_item
    assert "duration_ms" in exec_item
    assert "brain_count" in exec_item
    assert "created_at" in exec_item
