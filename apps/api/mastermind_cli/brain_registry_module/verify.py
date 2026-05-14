"""
Brain Registry verification script.

Runs after seed to verify the brain_registry table has exactly 7 rows.

Usage:
    uv run python -m mastermind_cli.brain_registry_module.verify
    DATABASE_URL=postgresql://... uv run python -m mastermind_cli.brain_registry_module.verify
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys

import asyncpg

log = logging.getLogger(__name__)

_DEFAULT_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:devpassword@localhost:5434/mastermind_bd",
)


async def verify_brain_registry(
    database_url: str = _DEFAULT_DATABASE_URL,
    expected_count: int = 7,
) -> bool:
    """Verify brain_registry has exactly expected_count rows.

    Args:
        database_url: PostgreSQL DSN to connect to.
        expected_count: Expected number of brain rows (default: 7).

    Returns:
        True if count matches expected_count, False otherwise.
    """
    conn: asyncpg.Connection = await asyncpg.connect(database_url)
    try:
        count = await conn.fetchval("SELECT COUNT(*) FROM brain_registry")
        log.info("brain_registry row count: %s (expected: %s)", count, expected_count)

        if count == expected_count:
            rows = await conn.fetch(
                "SELECT brain_id, name, enabled FROM brain_registry ORDER BY brain_id"
            )
            for row in rows:
                log.info(
                    "  brain_id=%s name=%s enabled=%s",
                    row["brain_id"],
                    row["name"],
                    row["enabled"],
                )
            return True
        else:
            log.error("FAIL: Expected %s rows, got %s", expected_count, count)
            return False
    finally:
        await conn.close()


def main() -> None:
    """Entry point for running verification from the CLI."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    url = _DEFAULT_DATABASE_URL
    ok = asyncio.run(verify_brain_registry(url))
    if ok:
        print("PASS: SELECT COUNT(*) FROM brain_registry = 7")
        sys.exit(0)
    else:
        print("FAIL: brain_registry count mismatch")
        sys.exit(1)


if __name__ == "__main__":
    main()
