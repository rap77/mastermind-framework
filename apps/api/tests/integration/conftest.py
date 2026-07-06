"""Shared fixtures for integration tests.

Integration tests connect to a real PostgreSQL instance instead of SQLite.
The DSN is read from the ``DATABASE_URL`` environment variable, which the
bundled ``docker-compose.yml`` publishes for the ``api`` and
``control-plane`` services.

When ``DATABASE_URL`` is missing, the ``_database_url_for_integration``
session fixture skips the entire integration test run with a clear hint,
preventing accidental attempts to use a hardcoded credential.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest


def _has_database_url() -> bool:
    """Return True when ``DATABASE_URL`` is configured for integration tests."""
    return bool(os.getenv("DATABASE_URL"))


@pytest.fixture(scope="session", autouse=True)
def _database_url_for_integration() -> None:
    """Skip the integration suite when ``DATABASE_URL`` is not configured.

    The Docker Compose stack (``docker compose up -d postgres``) sets
    ``POSTGRES_URL`` automatically; copy it to ``DATABASE_URL`` (or export
    it explicitly) before running ``pytest -m integration``. Skipping here
    prevents the tests from guessing a default credential at runtime.
    """
    if not _has_database_url():
        postgres_url = os.getenv("POSTGRES_URL")
        if postgres_url:
            os.environ["DATABASE_URL"] = postgres_url
    if not _has_database_url():
        pytest.skip(
            "DATABASE_URL is not configured; start the dev Postgres stack "
            "with `docker compose up -d postgres` (which publishes "
            "POSTGRES_URL) or export DATABASE_URL directly.",
            allow_module_level=True,
        )


def integration_data_path(*parts: str) -> Path:
    """Resolve a path under ``tests/integration/data``."""
    return Path(__file__).resolve().parent.joinpath("data", *parts)
