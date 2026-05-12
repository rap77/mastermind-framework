"""Tests for GET /health endpoint.

Requirements: B3.2, B3.5
- GET /health returns HTTP 200
- Response body contains {"status": "ok", "db": "postgresql"}
"""

import os

import pytest
from fastapi.testclient import TestClient

# Set JWT_SECRET before importing create_app
os.environ["JWT_SECRET"] = "test_secret_for_unit_tests_only"

from mastermind_cli.api.app import create_app  # noqa: E402


@pytest.fixture
def client() -> TestClient:
    """Synchronous test client against in-memory app."""
    app = create_app(":memory:")
    return TestClient(app)


def test_health_returns_200(client: TestClient) -> None:
    """B3.5: GET /health returns HTTP 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_response_contains_status_ok(client: TestClient) -> None:
    """B3.5: GET /health body contains status=ok."""
    response = client.get("/health")
    data = response.json()
    assert data["status"] == "ok"


def test_health_response_contains_db_field(client: TestClient) -> None:
    """B3.5: GET /health body contains db=postgresql."""
    response = client.get("/health")
    data = response.json()
    assert "db" in data
    assert data["db"] == "postgresql"
