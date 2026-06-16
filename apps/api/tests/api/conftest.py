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

import os
import sqlite3
from pathlib import Path

import bcrypt
import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from pytest import MonkeyPatch

# Set JWT_SECRET BEFORE importing create_app (jwt_handler reads it at import time)
os.environ["JWT_SECRET"] = "test_secret_for_unit_tests_only"

from mastermind_cli.api.app import create_app
from mastermind_cli.api.dependencies import get_db_path
from mastermind_cli.api.routes.auth import create_access_token, create_refresh_token
from mastermind_cli.project_state.database.session import dispose_engines

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
    with sqlite3.connect(path) as conn:
        conn.executescript("""
            PRAGMA journal_mode=WAL;

            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                brain_id TEXT NOT NULL,
                status TEXT NOT NULL,
                progress TEXT,
                result TEXT,
                error TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS executions (
                id TEXT PRIMARY KEY,
                flow_config TEXT NOT NULL,
                brief TEXT NOT NULL,
                created_at TIMESTAMP,
                status TEXT,
                user_id TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_status ON tasks(status);
            CREATE INDEX IF NOT EXISTS idx_brain_id ON tasks(brain_id);

            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                refresh_token_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                rotation_count INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS api_keys (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                key_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS audit_log (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                method TEXT NOT NULL,
                request_hash TEXT,
                response_status INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
            CREATE INDEX IF NOT EXISTS idx_sessions_refresh_token_hash ON sessions(refresh_token_hash);
            CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id);
            CREATE INDEX IF NOT EXISTS idx_api_keys_key_hash ON api_keys(key_hash);
            CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id, timestamp DESC);
        """)
        conn.execute(
            "INSERT INTO users (id, username, password_hash) VALUES (?, ?, ?)",
            (TEST_USER_ID, TEST_USERNAME, TEST_PASSWORD_HASH),
        )
        conn.execute(
            "INSERT INTO users (id, username, password_hash) VALUES (?, ?, ?)",
            (TEST_USER_ID_B, TEST_USERNAME_B, TEST_PASSWORD_HASH_B),
        )
        conn.commit()


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

    async def _override_db_path() -> str:
        """Provide the test database path to FastAPI dependencies."""
        return db_path

    application.dependency_overrides[get_db_path] = _override_db_path
    yield application
    dispose_engines()


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncClient:
    """Async HTTP client for testing API endpoints."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


@pytest.fixture(autouse=True)
def stub_background_brain_task(monkeypatch: MonkeyPatch) -> None:
    """Prevent API tests from running real background orchestration tasks."""

    async def _noop_run_brain_task(
        task_id: str,
        brief: str,
        flow: str | None,
        db_path: str,
    ) -> None:
        """No-op replacement for run_brain_task during API tests."""
        del task_id, brief, flow, db_path

    monkeypatch.setattr(
        "mastermind_cli.api.routes.tasks.run_brain_task",
        _noop_run_brain_task,
    )


@pytest.fixture(autouse=True)
def stub_tasks_database_connection(monkeypatch: MonkeyPatch) -> None:
    """Replace task route aiosqlite usage with a sqlite3-backed async shim."""

    class _Cursor:
        def __init__(self, cursor: sqlite3.Cursor):
            self._cursor = cursor

        async def fetchone(self):
            """Return one row from the wrapped sqlite3 cursor."""
            return self._cursor.fetchone()

        async def fetchall(self):
            """Return all rows from the wrapped sqlite3 cursor."""
            return self._cursor.fetchall()

    class _Conn:
        def __init__(self, connection: sqlite3.Connection):
            self._connection = connection

        async def execute(self, sql: str, params=None):
            """Execute SQL and expose an async-compatible cursor API."""
            return _Cursor(self._connection.execute(sql, params or []))

        async def commit(self):
            """Commit the underlying sqlite3 transaction."""
            self._connection.commit()

    class _FakeDatabaseConnection:
        def __init__(self, db_path: str = ":memory:"):
            self.db_path = db_path
            self._connection: sqlite3.Connection | None = None

        @property
        def conn(self) -> _Conn:
            assert self._connection is not None
            return _Conn(self._connection)

        async def __aenter__(self):
            self._connection = sqlite3.connect(self.db_path)
            return self

        async def __aexit__(self, exc_type, exc, tb):
            del exc_type, exc, tb
            assert self._connection is not None
            self._connection.close()
            self._connection = None

    monkeypatch.setattr(
        "mastermind_cli.api.routes.tasks.DatabaseConnection",
        _FakeDatabaseConnection,
    )


@pytest.fixture(autouse=True)
def stub_keys_database_connection(monkeypatch: MonkeyPatch) -> None:
    """Replace key route aiosqlite usage with a sqlite3-backed async shim."""

    class _Cursor:
        def __init__(self, cursor: sqlite3.Cursor):
            self._cursor = cursor

        async def fetchone(self):
            """Return one row from the wrapped sqlite3 cursor."""
            return self._cursor.fetchone()

        async def fetchall(self):
            """Return all rows from the wrapped sqlite3 cursor."""
            return self._cursor.fetchall()

    class _Conn:
        def __init__(self, connection: sqlite3.Connection):
            self._connection = connection

        async def execute(self, sql: str, params=None):
            """Execute SQL and expose an async-compatible cursor API."""
            return _Cursor(self._connection.execute(sql, params or []))

        async def commit(self):
            """Commit the underlying sqlite3 transaction."""
            self._connection.commit()

    class _FakeDatabaseConnection:
        def __init__(self, db_path: str = ":memory:"):
            self.db_path = db_path
            self._connection: sqlite3.Connection | None = None

        @property
        def conn(self) -> _Conn:
            assert self._connection is not None
            return _Conn(self._connection)

        async def __aenter__(self):
            self._connection = sqlite3.connect(self.db_path)
            return self

        async def __aexit__(self, exc_type, exc, tb):
            del exc_type, exc, tb
            assert self._connection is not None
            self._connection.close()
            self._connection = None

        async def create_api_keys_v2_schema(self):
            """Create the API-key schema expected by the keys routes."""
            assert self._connection is not None
            self._connection.executescript("""
                CREATE TABLE IF NOT EXISTS api_keys_v2 (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    key_hash TEXT NOT NULL,
                    prefix TEXT NOT NULL,
                    suffix TEXT NOT NULL,
                    name TEXT,
                    created_at TEXT NOT NULL,
                    last_used_at TEXT,
                    revoked_at TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_api_keys_v2_user_id
                    ON api_keys_v2(user_id, created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_api_keys_v2_prefix
                    ON api_keys_v2(prefix);
            """)
            self._connection.commit()

    monkeypatch.setattr(
        "mastermind_cli.api.routes.keys.DatabaseConnection",
        _FakeDatabaseConnection,
    )


@pytest.fixture(autouse=True)
def stub_auth_database_connection(monkeypatch: MonkeyPatch) -> None:
    """Replace auth route aiosqlite usage with a sqlite3-backed async shim."""

    class _Cursor:
        def __init__(self, cursor: sqlite3.Cursor):
            self._cursor = cursor

        async def fetchone(self):
            """Return one row from the wrapped sqlite3 cursor."""
            return self._cursor.fetchone()

    class _Conn:
        def __init__(self, connection: sqlite3.Connection):
            self._connection = connection

        async def execute(self, sql: str, params=None):
            """Execute SQL and expose an async-compatible cursor API."""
            return _Cursor(self._connection.execute(sql, params or []))

        async def commit(self):
            """Commit the underlying sqlite3 transaction."""
            self._connection.commit()

    class _FakeDatabaseConnection:
        def __init__(self, db_path: str = ":memory:"):
            self.db_path = db_path
            self._connection: sqlite3.Connection | None = None

        @property
        def conn(self) -> _Conn:
            assert self._connection is not None
            return _Conn(self._connection)

        async def __aenter__(self):
            self._connection = sqlite3.connect(self.db_path)
            return self

        async def __aexit__(self, exc_type, exc, tb):
            del exc_type, exc, tb
            assert self._connection is not None
            self._connection.close()
            self._connection = None

    monkeypatch.setattr(
        "mastermind_cli.api.routes.auth.DatabaseConnection",
        _FakeDatabaseConnection,
    )


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
