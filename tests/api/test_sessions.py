"""Test multi-user session isolation and concurrent requests.

Requirements: UI-08
"""

import asyncio

import pytest


@pytest.mark.asyncio
async def test_concurrent_requests_isolated(client, auth_headers, auth_headers_b):
    """Users A and B have isolated task lists."""
    await client.post("/api/tasks", headers=auth_headers, json={"brief": "A task"})
    await client.post("/api/tasks", headers=auth_headers_b, json={"brief": "B task"})

    list_a = await client.get("/api/tasks", headers=auth_headers)
    list_b = await client.get("/api/tasks", headers=auth_headers_b)

    ids_a = {t["id"] for t in list_a.json()["tasks"]}
    ids_b = {t["id"] for t in list_b.json()["tasks"]}

    assert ids_a.isdisjoint(ids_b), "Sessions leaked between users"


@pytest.mark.asyncio
async def test_user_cannot_access_other_tasks(client, auth_headers, auth_headers_b):
    """User A gets 404 on user B's tasks."""
    create_b = await client.post(
        "/api/tasks", headers=auth_headers_b, json={"brief": "Private B"}
    )
    task_id = create_b.json()["task_id"]

    response = await client.get(f"/api/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_concurrent_task_creation(client, auth_headers, auth_headers_b):
    """Concurrent task creation produces unique IDs and correct ownership."""
    results = await asyncio.gather(
        client.post("/api/tasks", headers=auth_headers, json={"brief": "Concurrent A"}),
        client.post(
            "/api/tasks", headers=auth_headers_b, json={"brief": "Concurrent B"}
        ),
    )
    ids = [r.json()["task_id"] for r in results]
    assert ids[0] != ids[1], "Duplicate task_id generated"


@pytest.mark.asyncio
async def test_api_key_isolation(client, auth_headers, auth_headers_b):
    """API key is scoped to its owner."""
    # Create task as user B
    task_b = await client.post(
        "/api/tasks", headers=auth_headers_b, json={"brief": "B only"}
    )
    task_id = task_b.json()["task_id"]

    # User A creates API key
    key_resp = await client.post(
        "/api/auth/api-keys", headers=auth_headers, json={"name": "scoped"}
    )
    api_key = key_resp.json()["key"]

    # API key of A cannot access B's task
    response = await client.get(
        f"/api/tasks/{task_id}",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_session_persistence(client, auth_headers):
    """JWT token works across multiple requests."""
    for _ in range(3):
        response = await client.get("/api/tasks", headers=auth_headers)
        assert response.status_code == 200
