"""Regression tests for aiosqlite event-loop compatibility on Python 3.14."""

from __future__ import annotations

from pathlib import Path

import aiosqlite
import pytest

from mastermind_cli.state.database import DatabaseConnection


@pytest.mark.asyncio
async def test_aiosqlite_connect_completes_under_current_event_loop(
    tmp_path: Path,
) -> None:
    """Plain aiosqlite.connect should not hang under the running loop."""
    db_path = tmp_path / "compat.db"

    async with aiosqlite.connect(str(db_path)) as conn:
        await conn.execute("CREATE TABLE sample (id INTEGER PRIMARY KEY)")
        await conn.commit()


@pytest.mark.asyncio
async def test_database_connection_connects_and_creates_schema(
    tmp_path: Path,
) -> None:
    """DatabaseConnection should connect and initialize schemas without hanging."""
    db_path = tmp_path / "mastermind.db"

    async with DatabaseConnection(str(db_path)) as db:
        await db.create_task_schema()
        await db.create_auth_schema()

        cursor = await db.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        table_names = {row[0] for row in await cursor.fetchall()}

    assert "tasks" in table_names
    assert "users" in table_names
