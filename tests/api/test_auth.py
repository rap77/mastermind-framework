"""Test authentication endpoints and JWT token management.

Requirements: UI-02, UI-03, UI-07
"""

from datetime import datetime, timedelta

import pytest
from jose import jwt

from tests.api.conftest import TEST_USER_ID, TEST_USERNAME, TEST_PASSWORD

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"


@pytest.mark.asyncio
async def test_login_success(client):
    """Valid credentials return access_token + refresh_token."""
    response = await client.post(
        "/api/auth/login",
        json={"username": TEST_USERNAME, "password": TEST_PASSWORD},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"].lower() == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    """Wrong password returns 401."""
    response = await client.post(
        "/api/auth/login",
        json={"username": TEST_USERNAME, "password": "wrongpassword"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token_rotation(client):
    """Refresh returns new access_token AND new refresh_token."""
    import asyncio

    login = await client.post(
        "/api/auth/login",
        json={"username": TEST_USERNAME, "password": TEST_PASSWORD},
    )
    old_refresh = login.json()["refresh_token"]

    # Wait 1s so the new JWT has a different `exp` (second-resolution) and differs
    await asyncio.sleep(1.1)

    response = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": old_refresh},
    )
    assert response.status_code == 200
    new_tokens = response.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens
    assert new_tokens["refresh_token"] != old_refresh


@pytest.mark.asyncio
async def test_old_refresh_token_rejected(client):
    """After rotation, old refresh_token is rejected."""
    import asyncio

    login = await client.post(
        "/api/auth/login",
        json={"username": TEST_USERNAME, "password": TEST_PASSWORD},
    )
    old_refresh = login.json()["refresh_token"]

    # Wait 1s so new JWT has different exp and a different hash is stored
    await asyncio.sleep(1.1)

    # First use — rotates and deletes old session
    await client.post("/api/auth/refresh", json={"refresh_token": old_refresh})

    # Second use of old token must fail (session was deleted during rotation)
    response = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": old_refresh},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_expired_token_rejected(client):
    """Expired access token returns 401 on protected endpoints."""
    expired = jwt.encode(
        {
            "sub": TEST_USER_ID,
            "exp": datetime.utcnow() - timedelta(seconds=1),
            "type": "access",
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    response = await client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {expired}"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_api_key_creation(client, auth_headers):
    """Authenticated user can create API key with mm_ prefix."""
    response = await client.post(
        "/api/auth/api-keys",
        headers=auth_headers,
        json={"name": "test-key"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["key"].startswith("mm_")
    assert data["name"] == "test-key"


@pytest.mark.asyncio
async def test_api_key_authentication(client, auth_headers):
    """API key can authenticate on protected endpoints."""
    create_resp = await client.post(
        "/api/auth/api-keys",
        headers=auth_headers,
        json={"name": "cli-key"},
    )
    api_key = create_resp.json()["key"]

    response = await client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_api_key_isolation(client, auth_headers, auth_headers_b):
    """User A's API key cannot access User B's tasks."""
    # Create task as user B
    task_resp = await client.post(
        "/api/tasks",
        headers=auth_headers_b,
        json={"brief": "Task for user B"},
    )
    task_id = task_resp.json()["task_id"]

    # User A creates an API key
    key_resp = await client.post(
        "/api/auth/api-keys",
        headers=auth_headers,
        json={"name": "a-key"},
    )
    api_key_a = key_resp.json()["key"]

    # User A tries to access user B's task — must get 404
    response = await client.get(
        f"/api/tasks/{task_id}",
        headers={"Authorization": f"Bearer {api_key_a}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_logout(client, auth_headers):
    """Logout returns 200."""
    response = await client.post("/api/auth/logout", headers=auth_headers)
    assert response.status_code == 200
