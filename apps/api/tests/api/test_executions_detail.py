"""Tests for GET /api/executions/{id} (execution detail).

Requirements: SV-02 (Strategy Vault — execution detail with brain outputs)
"""

import json
import uuid
from datetime import datetime

import pytest

from mastermind_cli.state.database import DatabaseConnection


async def _insert_execution_full(
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

    async with DatabaseConnection(db_path) as db:
        await db.create_execution_history_schema()
        await db.conn.execute(
            """INSERT INTO execution_history
               (id, task_id, brief, status, duration_ms, brain_count,
                created_at, milestones_json, brain_outputs_json, graph_snapshot_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [
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
            ],
        )
        await db.conn.commit()
    return exec_id


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
    exec_id = await _insert_execution_full(
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
    exec_id = await _insert_execution_full(
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
    exec_id = await _insert_execution_full(
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
    exec_id = await _insert_execution_full(
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
