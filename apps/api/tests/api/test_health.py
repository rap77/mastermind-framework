"""Tests for GET /health endpoint.

Requirements: B3.2, B3.5
- GET /health returns HTTP 200
- Response body contains {"status": "ok", "db": "sqlite"}
"""

from typing import Any

import pytest


@pytest.mark.asyncio
async def test_health_returns_200(client: Any) -> None:
    """B3.5: GET /health returns HTTP 200 OK."""
    response = await client.get("/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_response_contains_status_ok(client: Any) -> None:
    """B3.5: GET /health body contains status=ok."""
    response = await client.get("/health")
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_health_response_contains_db_field(client: Any) -> None:
    """B3.5: GET /health body contains db=sqlite."""
    response = await client.get("/health")
    data = response.json()
    assert "db" in data
    assert data["db"] == "sqlite"
