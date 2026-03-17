"""Shared FastAPI dependencies for the MasterMind API.

This module provides shared dependency functions that are used across
multiple route modules. Centralizing them here allows tests to override
them in one place via app.dependency_overrides.
"""


def get_db_path() -> str:
    """Database path dependency — override via app.dependency_overrides in tests."""
    return ":memory:"
