"""Test audit logging for all mutations.

Requirements: UI-07
"""

import pytest

from mastermind_cli.state.database import DatabaseConnection


@pytest.mark.asyncio
async def test_audit_log_created(client, auth_headers, db_path):
    """POST /api/tasks creates an audit_log entry."""
    await client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"brief": "Audit test task"},
    )

    async with DatabaseConnection(db_path) as db:
        cursor = await db.conn.execute(
            "SELECT COUNT(*) FROM audit_log WHERE endpoint = '/api/tasks' AND method = 'POST'"
        )
        row = await cursor.fetchone()
        assert row[0] >= 1


@pytest.mark.asyncio
async def test_audit_entries_include_user(client, auth_headers, db_path):
    """Audit entries have user_id, endpoint, method, request_hash, response_status."""
    await client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"brief": "Audit structure test"},
    )

    async with DatabaseConnection(db_path) as db:
        cursor = await db.conn.execute(
            """SELECT user_id, endpoint, method, request_hash, response_status
               FROM audit_log WHERE endpoint = '/api/tasks' AND method = 'POST'
               ORDER BY timestamp DESC LIMIT 1"""
        )
        row = await cursor.fetchone()
        assert row is not None
        user_id, endpoint, method, request_hash, status = row
        assert user_id is not None
        assert endpoint == "/api/tasks"
        assert method == "POST"
        assert request_hash is not None
        assert status == 201


@pytest.mark.asyncio
async def test_read_operations_not_logged(client, auth_headers, db_path):
    """GET requests do not create audit entries."""
    # Count before
    async with DatabaseConnection(db_path) as db:
        before = await (
            await db.conn.execute("SELECT COUNT(*) FROM audit_log WHERE method = 'GET'")
        ).fetchone()
        count_before = before[0] if before else 0

    await client.get("/api/tasks", headers=auth_headers)

    async with DatabaseConnection(db_path) as db:
        after = await (
            await db.conn.execute("SELECT COUNT(*) FROM audit_log WHERE method = 'GET'")
        ).fetchone()
        count_after = after[0] if after else 0

    assert count_after == count_before


@pytest.mark.asyncio
async def test_audit_log_query(client, auth_headers, db_path):
    """Audit log can be queried by user_id."""
    await client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"brief": "Query test"},
    )

    from tests.api.conftest import TEST_USER_ID

    async with DatabaseConnection(db_path) as db:
        cursor = await db.conn.execute(
            "SELECT COUNT(*) FROM audit_log WHERE user_id = ?",
            [TEST_USER_ID],
        )
        row = await cursor.fetchone()
        assert row[0] >= 1
