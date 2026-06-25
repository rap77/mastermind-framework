"""Tests for GET /api/executions/{id} (execution detail).

Requirements: SV-02 (Strategy Vault — execution detail with brain outputs)
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import closing
from datetime import datetime
from datetime import timedelta

import pytest

from mastermind_cli.project_state.database.session import (
    dispose_engines,
    get_session_factory,
    initialize_database,
)
from mastermind_cli.project_state.repositories.artifacts import ArtifactRepository
from mastermind_cli.project_state.models.checkpoint import Checkpoint
from mastermind_cli.project_state.models.project import Project
from mastermind_cli.project_state.models.task import Task
from mastermind_cli.project_state.models.task_run import TaskRun
from tests.api.conftest import TEST_USER_ID


@pytest.fixture(autouse=True)
def cleanup_project_state_engines() -> None:
    """Dispose cached SQLAlchemy engines after each test."""
    yield
    dispose_engines()


def _insert_execution_full(
    db_path: str,
    task_id: str,
    brief: str,
    status: str = "success",
    milestones: list | None = None,
    brain_outputs: dict | None = None,
    graph_snapshot: dict | None = None,
) -> str:
    """Helper: insert a full execution_history record for detail tests."""
    exec_id = str(uuid.uuid4())
    ts = datetime.utcnow().isoformat()

    _milestones = milestones or []
    _brain_outputs = brain_outputs or {}
    _graph_snapshot = graph_snapshot or {}

    with closing(sqlite3.connect(db_path)) as connection:
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
            (
                exec_id,
                task_id,
                brief[:200],
                status,
                5000,
                len(_brain_outputs) or 1,
                ts,
                json.dumps(_milestones),
                json.dumps(_brain_outputs),
                json.dumps(_graph_snapshot),
            ),
        )
        connection.commit()
    return exec_id


def _insert_project_state_execution_detail(
    db_path: str,
    *,
    run_id: str,
    task_id: str,
    brief: str,
    status: str = "completed",
) -> None:
    """Helper: insert canonical project_state task/run records for detail tests."""
    database_url = f"sqlite:///{db_path}.project_state"
    dispose_engines()
    initialize_database(database_url)
    session_factory = get_session_factory(database_url)
    started_at = datetime(2026, 6, 1, 12, 0, 0)
    ended_at = started_at + timedelta(seconds=5)
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
                    created_at=started_at,
                    updated_at=started_at,
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
                created_at=started_at,
                updated_at=ended_at,
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
                started_at=started_at,
                ended_at=ended_at,
                metadata_json={},
            )
        )
        session.commit()


def _insert_execution_output_artifact(
    db_path: str,
    *,
    run_id: str,
    task_id: str,
    brain_outputs: dict[str, object],
) -> None:
    """Insert a transitional canonical execution output artifact for a run."""
    database_url = f"sqlite:///{db_path}.project_state"
    dispose_engines()
    session_factory = get_session_factory(database_url)
    created_at = datetime(2026, 6, 1, 12, 0, 5)
    with session_factory() as session:
        repo = ArtifactRepository(session)
        repo.create_version(
            version_id=f"version-{run_id}",
            artifact_id=f"execution-output:{run_id}",
            project_id=f"user-tasks:{TEST_USER_ID}",
            artifact_type="execution_output_bundle",
            version=1,
            content_hash=f"hash-{run_id}",
            created_at=created_at,
            metadata_json={
                "run_id": run_id,
                "task_id": task_id,
                "format_version": 1,
                "brain_outputs": brain_outputs,
            },
        )


def _insert_execution_checkpoint(
    db_path: str,
    *,
    task_id: str,
    run_id: str,
    label: str,
    created_at: datetime,
) -> None:
    """Insert a canonical checkpoint for execution milestone enrichment."""
    database_url = f"sqlite:///{db_path}.project_state"
    dispose_engines()
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        session.add(
            Checkpoint(
                checkpoint_id=f"checkpoint-{run_id}-{int(created_at.timestamp())}",
                project_id=f"user-tasks:{TEST_USER_ID}",
                task_id=task_id,
                run_id=run_id,
                context_summary={},
                resume_state={},
                next_step_summary=label,
                created_at=created_at,
            )
        )
        session.commit()


@pytest.mark.asyncio
async def test_get_execution_detail_success(client, auth_headers, db_path) -> None:
    """GET /api/executions/{id} returns full Execution schema."""
    brain_outputs = {
        "brain-01": {
            "brain_id": "brain-01",
            "status": "complete",
            "output": "## Analysis\nThis is the output.",
            "duration_ms": 1500,
            "timestamp": 1711296000000,
        }
    }
    exec_id = _insert_execution_full(
        db_path,
        task_id="task-detail-001",
        brief="Detail test brief",
        status="success",
        brain_outputs=brain_outputs,
    )

    response = await client.get(f"/api/executions/{exec_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == exec_id
    assert data["task_id"] == "task-detail-001"
    assert data["brief"] == "Detail test brief"
    assert data["status"] == "success"
    assert "duration_ms" in data
    assert "brain_count" in data
    assert "created_at" in data
    assert "milestones" in data
    assert "brain_outputs" in data
    assert "graph_snapshot" in data


@pytest.mark.asyncio
async def test_get_execution_detail_not_found(client, auth_headers) -> None:
    """GET /api/executions/{id} returns 404 for nonexistent ID."""
    response = await client.get(
        "/api/executions/nonexistent-execution-id", headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_execution_detail_auth_required(client) -> None:
    """Missing JWT → 401."""
    response = await client.get("/api/executions/some-exec-id")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_get_execution_detail_includes_milestones(
    client, auth_headers, db_path
) -> None:
    """Execution detail includes milestones array."""
    milestones = [
        {"index": 0, "timestamp": 1000, "label": "Task started", "brain_count": 0},
        {"index": 1, "timestamp": 2000, "label": "Brain #1 complete", "brain_count": 1},
        {"index": 2, "timestamp": 3000, "label": "Task complete", "brain_count": 3},
    ]
    exec_id = _insert_execution_full(
        db_path,
        task_id="task-milestones-001",
        brief="Milestones test",
        milestones=milestones,
    )

    response = await client.get(f"/api/executions/{exec_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    assert len(data["milestones"]) == 3
    assert data["milestones"][0]["label"] == "Task started"
    assert data["milestones"][2]["label"] == "Task complete"


@pytest.mark.asyncio
async def test_get_execution_detail_includes_graph_snapshot(
    client, auth_headers, db_path
) -> None:
    """Execution detail includes graph_snapshot."""
    graph_snapshot = {
        "nodes": [{"id": "master", "type": "master"}],
        "edges": [],
    }
    exec_id = _insert_execution_full(
        db_path,
        task_id="task-snapshot-001",
        brief="Graph snapshot test",
        graph_snapshot=graph_snapshot,
    )

    response = await client.get(f"/api/executions/{exec_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    assert data["graph_snapshot"] == graph_snapshot


@pytest.mark.asyncio
async def test_get_execution_detail_brain_outputs_markdown(
    client, auth_headers, db_path
) -> None:
    """Brain outputs contain Markdown-formatted output strings."""
    brain_outputs = {
        "brain-01": {
            "brain_id": "brain-01",
            "status": "complete",
            "output": "## Product Strategy\n\n### Key Insights\n- Insight 1\n- Insight 2",
            "duration_ms": 2000,
            "timestamp": 1711296000000,
        },
        "brain-04": {
            "brain_id": "brain-04",
            "status": "complete",
            "output": "## Frontend Architecture\n\nRecommended stack: Next.js 16",
            "duration_ms": 1500,
            "timestamp": 1711296002000,
        },
    }
    exec_id = _insert_execution_full(
        db_path,
        task_id="task-markdown-001",
        brief="Markdown output test",
        brain_outputs=brain_outputs,
    )

    response = await client.get(f"/api/executions/{exec_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    assert "brain-01" in data["brain_outputs"]
    assert "brain-04" in data["brain_outputs"]
    assert "## Product Strategy" in data["brain_outputs"]["brain-01"]["output"]
    assert "## Frontend Architecture" in data["brain_outputs"]["brain-04"]["output"]


@pytest.mark.asyncio
async def test_get_execution_detail_reads_project_state_minimal_projection(
    client, auth_headers, db_path
) -> None:
    """GET /api/executions/{id} can return a minimal canonical projection from project_state."""
    _insert_project_state_execution_detail(
        db_path,
        run_id="run-detail-canonical-001",
        task_id="task-detail-canonical-001",
        brief="Canonical detail execution",
        status="completed",
    )

    response = await client.get(
        "/api/executions/run-detail-canonical-001",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == "run-detail-canonical-001"
    assert data["task_id"] == "task-detail-canonical-001"
    assert data["brief"] == "Canonical detail execution"
    assert data["status"] == "success"
    assert data["duration_ms"] == 5000
    assert data["brain_count"] == 1
    assert len(data["milestones"]) >= 2
    assert data["brain_outputs"] == {}
    assert data["graph_snapshot"] == {}


@pytest.mark.asyncio
async def test_get_execution_detail_reads_canonical_output_artifact_and_graph_snapshot(
    client, auth_headers, db_path
) -> None:
    """Execution detail enriches canonical detail from output artifacts and flow_config."""
    _insert_project_state_execution_detail(
        db_path,
        run_id="run-detail-rich-001",
        task_id="task-detail-rich-001",
        brief="Canonical rich detail execution",
        status="completed",
    )
    _insert_execution_output_artifact(
        db_path,
        run_id="run-detail-rich-001",
        task_id="task-detail-rich-001",
        brain_outputs={
            "brain-01": {
                "brain_id": "brain-01",
                "status": "complete",
                "output": "## Product Strategy",
                "duration_ms": 2000,
                "timestamp": 1711296000000,
            }
        },
    )

    database_url = f"sqlite:///{db_path}.project_state"
    dispose_engines()
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        task = session.get(Task, "task-detail-rich-001")
        assert task is not None
        task.metadata_json = {
            **task.metadata_json,
            "flow_config": json.dumps(
                {
                    "nodes": {"brain-01": []},
                    "edges": {},
                }
            ),
        }
        session.commit()

    response = await client.get(
        "/api/executions/run-detail-rich-001",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()

    assert "brain-01" in data["brain_outputs"]
    assert data["brain_outputs"]["brain-01"]["output"] == "## Product Strategy"
    assert data["graph_snapshot"]["nodes"] == {"brain-01": []}
    assert data["graph_snapshot"]["edges"] == {}
    assert data["brain_count"] == 1


@pytest.mark.asyncio
async def test_get_execution_detail_derives_brain_count_and_checkpoint_milestones(
    client, auth_headers, db_path
) -> None:
    """Canonical detail uses output bundle size and checkpoints for richer projection."""
    _insert_project_state_execution_detail(
        db_path,
        run_id="run-detail-multi-001",
        task_id="task-detail-multi-001",
        brief="Canonical multi brain detail",
        status="completed",
    )
    _insert_execution_output_artifact(
        db_path,
        run_id="run-detail-multi-001",
        task_id="task-detail-multi-001",
        brain_outputs={
            "brain-01": {
                "brain_id": "brain-01",
                "status": "complete",
                "output": "## One",
                "duration_ms": 2000,
                "timestamp": 1711296000000,
            },
            "brain-04": {
                "brain_id": "brain-04",
                "status": "complete",
                "output": "## Two",
                "duration_ms": 1000,
                "timestamp": 1711296002000,
            },
        },
    )
    _insert_execution_checkpoint(
        db_path,
        task_id="task-detail-multi-001",
        run_id="run-detail-multi-001",
        label="Checkpoint midway",
        created_at=datetime(2026, 6, 1, 12, 0, 3),
    )

    response = await client.get(
        "/api/executions/run-detail-multi-001",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()

    assert data["brain_count"] == 2
    labels = [item["label"] for item in data["milestones"]]
    assert "Task started" in labels
    assert "Checkpoint midway" in labels
    assert "Task complete" in labels
