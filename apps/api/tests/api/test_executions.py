"""Test task management endpoints (CRUD operations).

Requirements: UI-06
"""

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
