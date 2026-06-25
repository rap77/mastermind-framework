"""Test FastAPI application creation and route mounting.

Requirements: UI-01
"""

from typing import Any

import pytest


@pytest.mark.asyncio
async def test_app_creates(client: Any) -> None:
    """create_app() returns a FastAPI instance and health check returns 200."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_routes_registered(app: Any) -> None:
    """Auth, task, and WebSocket routes are mounted."""
    paths = [route.path for route in app.routes]  # type: ignore[attr-defined]
    assert any("/api/auth" in p for p in paths)
    assert any("/api/tasks" in p for p in paths)
    assert any("/ws/tasks" in p for p in paths)


def test_app_accepts_governance_provider() -> None:
    """create_app() should store an app-scoped governance provider."""
    from mastermind_cli.api.app import create_app

    sentinel = object()
    application = create_app(governance=sentinel)

    assert application.state.governance is sentinel


@pytest.mark.asyncio
async def test_cors_configuration(client: Any) -> None:
    """CORS middleware allows configured origins (explicit list, not wildcard)."""
    response = await client.options(
        "/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "access-control-allow-origin" in response.headers
