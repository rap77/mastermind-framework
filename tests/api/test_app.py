"""Test FastAPI application creation and route mounting.

Requirements: UI-01
"""


def test_app_creates(app):
    """create_app() returns a FastAPI instance and health check returns 200."""
    from fastapi.testclient import TestClient

    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_routes_registered(app):
    """Auth, task, and WebSocket routes are mounted."""
    paths = [route.path for route in app.routes]  # type: ignore[attr-defined]
    assert any("/api/auth" in p for p in paths)
    assert any("/api/tasks" in p for p in paths)
    assert any("/ws/tasks" in p for p in paths)


def test_cors_configuration(sync_client):
    """CORS middleware allows all origins."""
    response = sync_client.options(
        "/",
        headers={
            "Origin": "http://example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "access-control-allow-origin" in response.headers
