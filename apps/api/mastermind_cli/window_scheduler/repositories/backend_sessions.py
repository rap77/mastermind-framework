"""Repository for window scheduler backend inventory."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from mastermind_cli.window_scheduler.models.backend_session import BackendSession


class BackendSessionsRepository:
    """Persistence access for scheduler backend sessions."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a shared SQLAlchemy session."""
        self.session = session

    def get_by_id(self, backend_id: str) -> BackendSession | None:
        """Return a backend session by ID, if present."""
        result = self.session.execute(
            select(BackendSession).where(BackendSession.backend_id == backend_id)
        )
        return result.scalar_one_or_none()
