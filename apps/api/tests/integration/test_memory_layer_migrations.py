"""Integration tests for memory-layer SQL migrations."""

from __future__ import annotations

import os

import asyncpg
import pytest

from mastermind_cli.memory_layer.migrate import HEAD_REVISION, upgrade_to_head

EXPECTED_TABLES = {
    "mm_memory_items",
    "mm_memory_preferences",
    "mm_memory_sessions",
}


def _database_url() -> str:
    """Return ``DATABASE_URL`` from the environment.

    The session-scoped conftest in ``tests/integration/conftest.py`` skips
    the entire integration suite if the variable is missing, so reaching
    this point implies the URL is configured.
    """
    url = os.getenv("DATABASE_URL")
    if not url:
        pytest.skip("DATABASE_URL is not configured")
    return url


@pytest.mark.integration
@pytest.mark.asyncio
async def test_memory_layer_migration_creates_tables() -> None:
    """The memory-layer migration should create the canonical tables."""
    url = _database_url()
    applied = upgrade_to_head(url)
    assert applied in ([], [HEAD_REVISION])

    conn: asyncpg.Connection = await asyncpg.connect(url)
    try:
        rows = await conn.fetch(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name LIKE 'mm_memory_%'
            """
        )
        tables = {row["table_name"] for row in rows}
        assert EXPECTED_TABLES.issubset(tables)

        version_rows = await conn.fetch("SELECT version_num FROM alembic_version")
        assert {row["version_num"] for row in version_rows} == {HEAD_REVISION}
    finally:
        await conn.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_memory_layer_migration_is_idempotent() -> None:
    """Running the migration twice should not re-apply it."""
    url = _database_url()
    first = upgrade_to_head(url)
    second = upgrade_to_head(url)

    assert first == [] or first == [HEAD_REVISION]
    assert second == []
