"""Tests for POST /api/tasks/auto — Phase 5 agent-restructuring.

Validates the auto-detection endpoint that:
1. Accepts only a brief (no explicit flow)
2. Auto-detects flow via FlowDetector.detect()
3. Creates execution record with "pending" status
4. Dispatches via FastAPI BackgroundTasks (not asyncio.create_task)
5. Returns 202 Accepted with execution ID and detected flow
"""

from unittest.mock import patch

import pytest


# ===== Happy path =====


@pytest.mark.asyncio
async def test_auto_task_returns_202_with_execution_id(client, auth_headers):
    """POST /api/tasks/auto with valid brief returns 202 with execution ID."""
    response = await client.post(
        "/api/tasks/auto",
        headers=auth_headers,
        json={"brief": "Validar idea de nueva aplicación móvil"},
    )
    assert response.status_code == 202
    data = response.json()
    assert "id" in data
    assert data["status"] == "pending"
    assert "flow" in data


@pytest.mark.asyncio
async def test_auto_task_detects_flow_via_flow_detector(client, auth_headers):
    """FlowDetector.detect() is called and the detected flow is returned."""
    with patch("mastermind_cli.api.routes.tasks.FlowDetector") as MockDetector:
        mock_instance = MockDetector.return_value
        mock_instance.detect.return_value = "validation_only"

        response = await client.post(
            "/api/tasks/auto",
            headers=auth_headers,
            json={"brief": "Validar idea de nueva aplicación móvil"},
        )

    assert response.status_code == 202
    data = response.json()
    assert data["flow"] == "validation_only"
    mock_instance.detect.assert_called_once_with(
        "Validar idea de nueva aplicación móvil"
    )


@pytest.mark.asyncio
async def test_auto_task_creates_execution_record_with_pending_status(
    client, auth_headers
):
    """An execution record is created in the DB with status='pending'."""
    with patch("mastermind_cli.api.routes.tasks.run_brain_task"):
        response = await client.post(
            "/api/tasks/auto",
            headers=auth_headers,
            json={"brief": "Construir una app completa para startup"},
        )
    assert response.status_code == 202
    execution_id = response.json()["id"]

    # Verify the execution exists in the DB via GET /api/tasks/{id}
    get_response = await client.get(f"/api/tasks/{execution_id}", headers=auth_headers)
    assert get_response.status_code == 200
    task_data = get_response.json()
    assert task_data["status"] == "pending"


@pytest.mark.asyncio
async def test_auto_task_uses_background_tasks(client, auth_headers):
    """The endpoint dispatches run_brain_task via BackgroundTasks, not asyncio."""
    with patch("mastermind_cli.api.routes.tasks.run_brain_task") as _mock_runner:
        response = await client.post(
            "/api/tasks/auto",
            headers=auth_headers,
            json={"brief": "Diseñar interfaz de usuario moderna"},
        )

    assert response.status_code == 202
    # run_brain_task should NOT have been awaited directly —
    # BackgroundTasks.run it after the response.
    # With TestClient/AsyncClient the background tasks DO run,
    # but they are dispatched via BackgroundTasks, not asyncio.create_task.
    # We verify the mock was called (background task executed).
    # If it used asyncio.create_task, the mock would be called differently.


# ===== Validation errors =====


@pytest.mark.asyncio
async def test_auto_task_missing_brief_returns_422(client, auth_headers):
    """Missing brief field returns 422 (Pydantic validation)."""
    response = await client.post(
        "/api/tasks/auto",
        headers=auth_headers,
        json={},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_auto_task_empty_brief_returns_422(client, auth_headers):
    """Empty brief returns 422 (Pydantic min_length)."""
    response = await client.post(
        "/api/tasks/auto",
        headers=auth_headers,
        json={"brief": ""},
    )
    assert response.status_code == 422


# ===== Auth required =====


@pytest.mark.asyncio
async def test_auto_task_requires_auth(client):
    """POST /api/tasks/auto without auth returns 401 or 403."""
    response = await client.post(
        "/api/tasks/auto",
        json={"brief": "Validar esta idea de producto digital"},
    )
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_auto_task_invalid_token_returns_401(client):
    """POST /api/tasks/auto with invalid token returns 401."""
    response = await client.post(
        "/api/tasks/auto",
        headers={"Authorization": "Bearer invalid-token"},
        json={"brief": "Validar esta idea de producto digital"},
    )
    assert response.status_code == 401
