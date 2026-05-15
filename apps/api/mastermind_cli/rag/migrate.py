"""
RAG module migration runner.

Applies SQL migrations from the rag/migrations/ directory to PostgreSQL.
Uses the shared schema_migrations table to track applied migrations.

Usage:
    uv run python -m mastermind_cli.rag.migrate
    DATABASE_URL=postgresql://... uv run python -m mastermind_cli.rag.migrate
"""

from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path

import asyncpg

log = logging.getLogger(__name__)

MIGRATIONS_DIR = Path(__file__).parent / "migrations"
_DEFAULT_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:devpassword@localhost:5434/mastermind_bd",
)


async def _ensure_migrations_table(conn: asyncpg.Connection) -> None:
    """Create schema_migrations table if it does not exist.

    Args:
        conn: Open asyncpg connection.
    """
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            migration_name TEXT PRIMARY KEY,
            applied_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)


async def _applied_migrations(conn: asyncpg.Connection) -> set[str]:
    """Return the set of already-applied migration names.

    Args:
        conn: Open asyncpg connection.

    Returns:
        Set of migration_name strings already in schema_migrations.
    """
    rows = await conn.fetch("SELECT migration_name FROM schema_migrations")
    return {row["migration_name"] for row in rows}


async def run_migrations(database_url: str = _DEFAULT_DATABASE_URL) -> list[str]:
    """Apply all pending RAG SQL migrations in order.

    Reads *.sql files from rag/migrations/, skips already-applied ones, and
    records each in schema_migrations after successful execution.

    Args:
        database_url: PostgreSQL DSN to connect to.

    Returns:
        List of migration names applied in this run.

    Raises:
        asyncpg.PostgresError: If any migration SQL fails.
    """
    sql_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not sql_files:
        log.info("No SQL migration files found in %s", MIGRATIONS_DIR)
        return []

    conn: asyncpg.Connection = await asyncpg.connect(database_url)
    try:
        await _ensure_migrations_table(conn)
        applied = await _applied_migrations(conn)

        newly_applied: list[str] = []
        for sql_file in sql_files:
            name = sql_file.name
            if name in applied:
                log.info("Skipping already-applied migration: %s", name)
                continue

            log.info("Applying migration: %s", name)
            sql = sql_file.read_text()
            await conn.execute(sql)
            await conn.execute(
                "INSERT INTO schema_migrations (migration_name) VALUES ($1)",
                name,
            )
            newly_applied.append(name)
            log.info("Applied migration: %s", name)

        return newly_applied
    finally:
        await conn.close()


def main() -> None:
    """Entry point for running RAG migrations from the CLI."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    url = _DEFAULT_DATABASE_URL
    applied = asyncio.run(run_migrations(url))
    if applied:
        print(f"Applied {len(applied)} migration(s): {', '.join(applied)}")
    else:
        print("No new migrations to apply.")


if __name__ == "__main__":
    main()
