"""Memory layer migration runner backed by Alembic.

Usage:
    DATABASE_URL=postgresql://... uv run python -m mastermind_cli.memory_layer.migrate

The PostgreSQL DSN MUST be provided via the ``DATABASE_URL`` environment
variable. The bundled Docker Compose stack exposes the value as
``POSTGRES_URL``; start it with ``docker compose up -d postgres``.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, text

from mastermind_cli.project_state.database.session import get_engine

logger = logging.getLogger(__name__)

MIGRATION_PATH = Path(__file__).with_name("alembic")
HEAD_REVISION = "0001_create_memory_tables"


def _resolve_database_url() -> str:
    """Return the PostgreSQL DSN from the ``DATABASE_URL`` environment."""
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    raise RuntimeError(
        "DATABASE_URL is not set. Export it directly or run "
        "`docker compose up -d postgres` to expose POSTGRES_URL."
    )


def _build_alembic_config(database_url: str) -> Config:
    """Build an Alembic config for the memory-layer migration package."""
    config = Config()
    config.set_main_option("script_location", str(MIGRATION_PATH))
    config.set_main_option("sqlalchemy.url", database_url)
    return config


def _current_revision(database_url: str) -> str | None:
    """Return the currently recorded Alembic revision, if any."""
    engine = get_engine(database_url)
    with engine.connect() as connection:
        table_names = inspect(connection).get_table_names()
        if "alembic_version" not in table_names:
            return None

        row = connection.execute(
            text("SELECT version_num FROM alembic_version")
        ).one_or_none()
        if row is None:
            return None
        return str(row[0])


def _upgrade_to_head(database_url: str) -> list[str]:
    """Apply memory-layer migrations up to Alembic head."""
    before = _current_revision(database_url)
    config = _build_alembic_config(database_url)
    engine = get_engine(database_url)

    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.upgrade(config, "head")

    after = _current_revision(database_url)
    if before != HEAD_REVISION and after == HEAD_REVISION:
        return [HEAD_REVISION]
    return []


def upgrade_to_head(database_url: str | None = None) -> list[str]:
    """Apply pending memory-layer Alembic migrations."""
    return _upgrade_to_head(database_url or _resolve_database_url())


def main() -> None:
    """Entry point for running memory-layer migrations from the CLI."""
    logging.basicConfig(level=logging.INFO, format="%(name)s %(levelname)s %(message)s")
    applied = upgrade_to_head()
    if applied:
        logger.info("Applied %d migration(s): %s", len(applied), ", ".join(applied))
    else:
        logger.info("No new migrations to apply.")


if __name__ == "__main__":
    main()
