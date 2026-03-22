"""Test task management endpoints (CRUD operations).

Requirements: UI-06, BE-02
"""

import json

import pytest


@pytest.mark.asyncio
async def test_create_task(client, auth_headers):
    """POST /api/tasks creates task and returns task_id."""
    response = await client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"brief": "Build a landing page"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "pending"
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_task_validation(client, auth_headers):
    """Empty brief returns 422."""
    response = await client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"brief": ""},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_tasks(client, auth_headers):
    """GET /api/tasks returns list of user's tasks."""
    # Create a task first
    await client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"brief": "Task for list test"},
    )

    response = await client.get("/api/tasks", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert "total" in data
    assert isinstance(data["tasks"], list)
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_get_task(client, auth_headers):
    """GET /api/tasks/{id} returns task; 404 for unknown."""
    create = await client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"brief": "Task for get test"},
    )
    task_id = create.json()["task_id"]

    response = await client.get(f"/api/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == task_id

    not_found = await client.get("/api/tasks/nonexistent-id", headers=auth_headers)
    assert not_found.status_code == 404


@pytest.mark.asyncio
async def test_cancel_task(client, auth_headers):
    """DELETE /api/tasks/{id} cancels task."""
    create = await client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"brief": "Task to cancel"},
    )
    task_id = create.json()["task_id"]

    response = await client.delete(f"/api/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task_id


@pytest.mark.asyncio
@pytest.mark.skip(reason="Export is a frontend-only feature — no backend API endpoint")
async def test_export_json(client, auth_headers):
    """Export JSON — frontend feature, no backend endpoint."""


@pytest.mark.asyncio
@pytest.mark.skip(reason="Export is a frontend-only feature — no backend API endpoint")
async def test_export_yaml(client, auth_headers):
    """Export YAML — frontend feature, no backend endpoint."""


@pytest.mark.asyncio
@pytest.mark.skip(reason="Export is a frontend-only feature — no backend API endpoint")
async def test_export_markdown(client, auth_headers):
    """Export Markdown — frontend feature, no backend endpoint."""


@pytest.mark.asyncio
async def test_session_isolation(client, auth_headers, auth_headers_b):
    """User A cannot access User B's tasks."""
    # Create task as user B
    create_b = await client.post(
        "/api/tasks",
        headers=auth_headers_b,
        json={"brief": "User B private task"},
    )
    task_id_b = create_b.json()["task_id"]

    # User A list — must NOT include user B's task
    list_a = await client.get("/api/tasks", headers=auth_headers)
    task_ids_a = [t["id"] for t in list_a.json()["tasks"]]
    assert task_id_b not in task_ids_a

    # User A get — must get 404
    get_resp = await client.get(f"/api/tasks/{task_id_b}", headers=auth_headers)
    assert get_resp.status_code == 404


# ===== BE-02: Graph Endpoint Contract Tests =====


class TestTaskGraphBE02:
    """Tests for GET /api/tasks/{id}/graph — BE-02 React Flow compatibility.

    Requirements: BE-02
    Covers: layout_positions field presence, source/target edge field names,
            empty flow_config shape, 404 for unknown task.
    """

    @pytest.mark.asyncio
    async def test_graph_empty_flow_config_returns_valid_shape(
        self, client, auth_headers
    ):
        """Empty flow_config returns response with all required keys including layout_positions."""
        # Create a task (no flow_config set — defaults to empty)
        create = await client.post(
            "/api/tasks",
            headers=auth_headers,
            json={"brief": "Graph shape test task"},
        )
        assert create.status_code == 201
        task_id = create.json()["task_id"]

        response = await client.get(f"/api/tasks/{task_id}/graph", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        # BE-02: all required keys must be present
        assert "nodes" in data
        assert "edges" in data
        assert "max_level" in data
        assert "max_parallelism" in data
        assert "layout_positions" in data

        # Empty task → empty collections
        assert data["nodes"] == []
        assert data["edges"] == []
        assert data["max_level"] == 0
        assert data["max_parallelism"] == 0

    @pytest.mark.asyncio
    async def test_graph_layout_positions_field_is_null(self, client, auth_headers):
        """layout_positions is null when server does not compute layout (Phase 08 deferred)."""
        create = await client.post(
            "/api/tasks",
            headers=auth_headers,
            json={"brief": "Layout positions null test"},
        )
        task_id = create.json()["task_id"]

        response = await client.get(f"/api/tasks/{task_id}/graph", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        # layout_positions must be null (not missing, not an empty dict)
        assert "layout_positions" in data
        assert data["layout_positions"] is None

    @pytest.mark.asyncio
    async def test_graph_edges_use_source_target_fields(self, client, auth_headers):
        """Edge objects serialize with 'source' and 'target' keys — React Flow compatible."""
        # Create task then update its flow_config directly via DB
        create = await client.post(
            "/api/tasks",
            headers=auth_headers,
            json={"brief": "Edge field names test"},
        )
        assert create.status_code == 201
        task_id = create.json()["task_id"]

        # Patch flow_config into the DB record
        import sqlite3
        import os

        db_path = os.environ.get("MM_DB_PATH", "/tmp/mastermind_test.db")
        flow_config = {
            "nodes": {
                "brain-01": [],
                "brain-02": ["brain-01"],
            },
            "edges": {
                "brain-02": ["brain-01"],
            },
        }
        conn = sqlite3.connect(db_path)
        conn.execute(
            "UPDATE executions SET flow_config = ? WHERE id = ?",
            [json.dumps(flow_config), task_id],
        )
        conn.commit()
        conn.close()

        response = await client.get(f"/api/tasks/{task_id}/graph", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert len(data["edges"]) == 1
        edge = data["edges"][0]

        # BE-02: React Flow requires 'source' and 'target'
        assert "source" in edge, f"Edge missing 'source' key. Got: {list(edge.keys())}"
        assert "target" in edge, f"Edge missing 'target' key. Got: {list(edge.keys())}"
        assert edge["source"] == "brain-01"
        assert edge["target"] == "brain-02"

        # Must NOT have old 'from'/'to' field names
        assert "from" not in edge
        assert "to" not in edge

    @pytest.mark.asyncio
    async def test_graph_returns_404_for_unknown_task(self, client, auth_headers):
        """GET /api/tasks/{id}/graph returns 404 for unknown task_id."""
        response = await client.get(
            "/api/tasks/nonexistent-task-id-99999/graph", headers=auth_headers
        )
        assert response.status_code == 404
