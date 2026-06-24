"""Shared FastAPI dependencies for the MasterMind API.

This module provides shared dependency functions that are used across
multiple route modules. Centralizing them here allows tests to override
them in one place via app.dependency_overrides.
"""

import os

from fastapi import Request
from mastermind_cli.orchestrator.governance import GovernanceInterceptor

__all__ = ["get_db_path", "get_project_state_db_url", "get_governance"]


async def get_db_path() -> str:
    """Database path dependency — override via app.dependency_overrides in tests."""
    return ":memory:"


async def get_project_state_db_url() -> str:
    """Project state database URL dependency."""
    return os.environ.get(
        "MM_PROJECT_STATE_DB_URL",
        os.environ.get(
            "POSTGRES_URL", "sqlite+aiosqlite:///./mastermind_project_state.db"
        ),
    )


async def get_governance(request: Request) -> GovernanceInterceptor | None:
    """Governance dependency; reads the app-scoped provider."""
    governance = getattr(request.app.state, "governance", None)
    if isinstance(governance, GovernanceInterceptor):
        return governance
    return None
