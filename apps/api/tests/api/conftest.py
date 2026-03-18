"""Shared fixtures for API tests."""

import asyncio

import bcrypt
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

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
def db_path(tmp_path):
    path = str(tmp_path / "test.db")
    _run_setup(path)
    return path


@pytest.fixture
def app(db_path):
    application = create_app(db_path)
    application.dependency_overrides[get_db_path] = lambda: db_path
    return application


@pytest_asyncio.fixture
async def client(app):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


@pytest.fixture
def sync_client(app):
    return TestClient(app)


@pytest.fixture
def auth_headers():
    token = create_access_token(TEST_USER_ID)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_b():
    token = create_access_token(TEST_USER_ID_B)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def valid_jwt():
    return create_access_token(TEST_USER_ID)


@pytest.fixture
def valid_refresh_token():
    return create_refresh_token(TEST_USER_ID)
