"""Tests for GET /api/executions/history (paginated list).

Requirements: SV-01 (Strategy Vault — execution history list)
"""

from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timedelta

import pytest

from mastermind_cli.project_state.database.session import (
    dispose_engines,
    get_session_factory,
    initialize_database,
)
from mastermind_cli.project_state.models.project import Project
from mastermind_cli.project_state.models.task import Task
from mastermind_cli.project_state.models.task_run import TaskRun
from tests.api.conftest import TEST_USER_ID


@pytest.fixture(autouse=True)
def cleanup_project_state_engines() -> None:
    """Dispose cached SQLAlchemy engines after each test."""
    yield
    dispose_engines()


def _insert_execution(
    db_path: str,
    task_id: str,
    brief: str,
    status: str = "success",
    created_at: datetime | None = None,
) -> str:
    """Helper: insert an execution_history record for tests."""
    exec_id = str(uuid.uuid4())
    ts = (created_at or datetime.utcnow()).isoformat()
    with sqlite3.connect(db_path) as connection:
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
        connection.execute(
            """INSERT INTO execution_history
               (id, task_id, brief, status, duration_ms, brain_count,
                created_at, milestones_json, brain_outputs_json, graph_snapshot_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (exec_id, task_id, brief[:200], status, 1000, 3, ts, "[]", "{}", "{}"),
        )
        connection.commit()
    return exec_id


def _insert_project_state_run(
    db_path: str,
    *,
    run_id: str,
    task_id: str,
    brief: str,
    status: str = "completed",
    started_at: datetime | None = None,
    ended_at: datetime | None = None,
) -> None:
    """Helper: insert canonical project_state task/run records for history tests."""
    database_url = f"sqlite:///{db_path}.project_state"
    dispose_engines()
    initialize_database(database_url)
    session_factory = get_session_factory(database_url)
    ts = started_at or datetime.utcnow()
    with session_factory() as session:
        project = session.get(Project, f"user-tasks:{TEST_USER_ID}")
        if project is None:
            session.add(
                Project(
                    project_id=f"user-tasks:{TEST_USER_ID}",
                    name="User task workspace",
                    status="active",
                    adapter_id="legacy-tasks",
                    metadata_json={"user_id": TEST_USER_ID},
                    created_at=ts,
                    updated_at=ts,
                )
            )
        session.add(
            Task(
                task_id=task_id,
                project_id=f"user-tasks:{TEST_USER_ID}",
                title=brief[:500],
                status=status,
                priority="normal",
                owner_type="user",
                owner_id=TEST_USER_ID,
                metadata_json={"brief": brief, "flow_config": "{}"},
                constraints={},
                completion_criteria={},
                created_at=ts,
                updated_at=ended_at or ts,
            )
        )
        session.add(
            TaskRun(
                run_id=run_id,
                project_id=f"user-tasks:{TEST_USER_ID}",
                task_id=task_id,
                actor_type="user",
                actor_id=TEST_USER_ID,
                status=status,
                started_at=ts,
                ended_at=ended_at,
                metadata_json={},
            )
        )
        session.commit()


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
        _insert_execution(
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
        _insert_execution(
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
        _insert_execution(
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
        _insert_execution(
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
    _insert_execution(db_path, task_id="task-inv", brief="Invalid cursor test")

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
    _insert_execution(
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


@pytest.mark.asyncio
async def test_get_executions_history_reads_project_state_runs_first(
    client, auth_headers, db_path
) -> None:
    """Canonical task runs should back the history list before legacy fallback."""
    started = datetime(2026, 6, 1, 12, 0, 0)
    ended = started + timedelta(seconds=4)
    _insert_project_state_run(
        db_path,
        run_id="run-canonical-001",
        task_id="task-canonical-001",
        brief="Canonical execution brief",
        status="completed",
        started_at=started,
        ended_at=ended,
    )

    response = await client.get("/api/executions/history?limit=5", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    assert len(data["executions"]) == 1
    item = data["executions"][0]
    assert item["id"] == "run-canonical-001"
    assert item["task_id"] == "task-canonical-001"
    assert item["brief"] == "Canonical execution brief"
    assert item["brain_count"] == 1
    assert item["duration_ms"] == 4000


@pytest.mark.asyncio
async def test_get_executions_history_derives_brain_count_from_output_artifact(
    client, auth_headers, db_path
) -> None:
    """History summary derives brain_count from canonical output artifacts when available."""
    from mastermind_cli.project_state.repositories.artifacts import ArtifactRepository

    started = datetime(2026, 6, 1, 12, 0, 0)
    ended = started + timedelta(seconds=4)
    _insert_project_state_run(
        db_path,
        run_id="run-canonical-002",
        task_id="task-canonical-002",
        brief="Canonical execution with two brains",
        status="completed",
        started_at=started,
        ended_at=ended,
    )

    database_url = f"sqlite:///{db_path}.project_state"
    dispose_engines()
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        ArtifactRepository(session).create_version(
            version_id="version-run-canonical-002",
            artifact_id="execution-output:run-canonical-002",
            project_id=f"user-tasks:{TEST_USER_ID}",
            artifact_type="execution_output_bundle",
            version=1,
            content_hash="hash-run-canonical-002",
            created_at=ended,
            metadata_json={
                "run_id": "run-canonical-002",
                "task_id": "task-canonical-002",
                "format_version": 1,
                "brain_outputs": {
                    "brain-01": {"brain_id": "brain-01", "status": "complete"},
                    "brain-04": {"brain_id": "brain-04", "status": "complete"},
                },
            },
        )

    response = await client.get("/api/executions/history?limit=5", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    item = next(
        entry for entry in data["executions"] if entry["id"] == "run-canonical-002"
    )
    assert item["brain_count"] == 2
