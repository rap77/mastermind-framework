"""Integration tests for brain-registry SQL migrations."""

from __future__ import annotations

import os

import asyncpg
import pytest

from mastermind_cli.brain_registry_module.migrate import run_migrations

EXPECTED_COLUMNS = {
    "token_budget_per_phase",
    "tokens_consumed_total",
}


def _database_url() -> str:
    """Return ``DATABASE_URL`` from the environment, skipping if missing."""
    url = os.getenv("DATABASE_URL")
    if not url:
        pytest.skip("DATABASE_URL is not configured")
    return url


@pytest.mark.integration
@pytest.mark.asyncio
async def test_brain_registry_migration_adds_budget_columns() -> None:
    """The brain-registry migration should add the budget tracking columns."""
    url = _database_url()
    applied = await run_migrations(url)
    assert applied in ([], ["002_add_budget_columns.sql"])

    conn: asyncpg.Connection = await asyncpg.connect(url)
    try:
        rows = await conn.fetch(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'brain_registry'
              AND column_name = ANY($1::text[])
            ORDER BY column_name
            """,
            list(EXPECTED_COLUMNS),
        )
        columns = {row["column_name"] for row in rows}
        assert EXPECTED_COLUMNS.issubset(columns)
    finally:
        await conn.close()
