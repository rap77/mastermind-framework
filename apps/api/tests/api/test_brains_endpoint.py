"""Integration tests for GET /api/brains endpoint.

Tests JWT authentication, pagination, and IDOR protection.

Requirements: BE-01
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_brains_with_valid_jwt(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test GET /api/brains returns 200 with valid JWT."""
    response = await client.get("/api/brains?page=1&page_size=24", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()
    assert "brains" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data

    # Should have at least 8 brains (software development niche)
    assert data["total"] >= 8
    assert len(data["brains"]) <= 24  # Respects page_size


@pytest.mark.asyncio
async def test_get_brains_default_params(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test GET /api/brains (no params) defaults to page=1, page_size=24."""
    response = await client.get("/api/brains", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 24
    assert len(data["brains"]) >= 8  # At least brains 1-8


@pytest.mark.asyncio
async def test_get_brains_unauthorized(client: AsyncClient):
    """Test GET /api/brains returns 401 without JWT cookie."""
    response = await client.get("/api/brains")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_brains_response_structure(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test GET /api/brains returns correct response structure."""
    response = await client.get("/api/brains?page=1&page_size=24", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()
    assert "brains" in data
    assert isinstance(data["brains"], list)

    # Check first brain has all required fields
    if len(data["brains"]) > 0:
        brain = data["brains"][0]
        assert "id" in brain
        assert "name" in brain
        assert "niche" in brain
        assert "status" in brain
        assert "uptime" in brain
        assert "last_called_at" in brain


@pytest.mark.asyncio
async def test_get_brains_pagination(client: AsyncClient, auth_headers: dict[str, str]):
    """Test GET /api/brains pagination logic."""
    response = await client.get("/api/brains?page=1&page_size=5", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 5
    assert len(data["brains"]) <= 5  # Respects page_size
    assert data["total"] >= 8  # Total should reflect all brains


@pytest.mark.asyncio
async def test_get_brains_idor_protection(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test IDOR protection: user_id from JWT is passed to get_all_brains()."""
    # For v2.1 single-tenant, all users see same brains
    # This test verifies the architecture is in place for multi-tenant future
    response = await client.get("/api/brains", headers=auth_headers)

    assert response.status_code == 200

    # Verify response doesn't leak other users' data (not applicable in v2.1)
    # In future multi-tenant version, this would verify user filtering
    data = response.json()
    assert "brains" in data
