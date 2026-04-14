"""Shared fixtures for API tests.

This module provides pytest fixtures for FastAPI API testing:

Fixtures:
- db_path: Creates a temporary SQLite database with test schema and users
- app: Creates a FastAPI application instance with test DB path override
- client: Async HTTP client for testing API endpoints
- sync_client: Synchronous HTTP client (TestClient wrapper)
- auth_headers: Bearer token headers for test user A
- auth_headers_b: Bearer token headers for test user B
- valid_jwt: Raw JWT access token for test user A
- valid_refresh_token: Raw JWT refresh token for test user A

Test Users:
- User A: TEST_USER_ID / TEST_USERNAME
- User B: TEST_USER_ID_B / TEST_USERNAME_B

Note: JWT_SECRET is set before create_app import because jwt_handler reads
it at module load time, not at runtime.
"""

from __future__ import annotations

# pyright: reportMissingImports=false

import asyncio
import os
from pathlib import Path

import bcrypt
import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

# Set JWT_SECRET BEFORE importing create_app (jwt_handler reads it at import time)
os.environ["JWT_SECRET"] = "test_secret_for_unit_tests_only"

from mastermind_cli.api.app import create_app
from mastermind_cli.api.dependencies import get_db_path
from mastermind_cli.api.routes.auth import create_access_token, create_refresh_token
from mastermind_cli.state.database import DatabaseConnection

TEST_USER_ID = "test-user-id-001"
TEST_USER_ID_B = "test-user-id-002"
TEST_USERNAME = "testuser"
TEST_USERNAME_B = "testuserb"
TEST_PASSWORD = "testpass123"
TEST_PASSWORD_HASH = bcrypt.hashpw(
    TEST_PASSWORD.encode(), bcrypt.gensalt(rounds=4)
).decode()
TEST_PASSWORD_HASH_B = bcrypt.hashpw(
    TEST_PASSWORD.encode(), bcrypt.gensalt(rounds=4)
).decode()


def _run_setup(path: str) -> None:
    async def setup() -> None:
        async with DatabaseConnection(path) as db:
            await db.create_task_schema()
            await db.create_auth_schema()
            await db.create_audit_trail_schema()
            await db.conn.execute(
                "INSERT INTO users (id, username, password_hash) VALUES (?, ?, ?)",
                [TEST_USER_ID, TEST_USERNAME, TEST_PASSWORD_HASH],
            )
            await db.conn.execute(
                "INSERT INTO users (id, username, password_hash) VALUES (?, ?, ?)",
                [TEST_USER_ID_B, TEST_USERNAME_B, TEST_PASSWORD_HASH_B],
            )
            await db.conn.commit()

    asyncio.run(setup())


@pytest.fixture
def db_path(tmp_path: Path) -> str:
    """Create a temporary SQLite database with test schema and users."""
    path = str(tmp_path / "test.db")
    _run_setup(path)
    return path


@pytest.fixture
def app(db_path: str) -> FastAPI:
    """Create a FastAPI application instance with test DB path override."""
    application = create_app(db_path)
    application.dependency_overrides[get_db_path] = lambda: db_path
    return application


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncClient:
    """Async HTTP client for testing API endpoints."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


@pytest.fixture
def sync_client(app: FastAPI) -> TestClient:
    """Synchronous HTTP client (TestClient wrapper)."""
    return TestClient(app)


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """Bearer token headers for test user A."""
    token = create_access_token(TEST_USER_ID)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_b() -> dict[str, str]:
    """Bearer token headers for test user B."""
    token = create_access_token(TEST_USER_ID_B)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def valid_jwt() -> str:
    """Raw JWT access token for test user A."""
    return create_access_token(TEST_USER_ID)


@pytest.fixture
def valid_refresh_token() -> str:
    """Raw JWT refresh token for test user A."""
    return create_refresh_token(TEST_USER_ID)
