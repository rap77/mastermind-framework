"""Repository for window scheduler run policies."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from mastermind_cli.window_scheduler.models.run_policy import RunPolicy


class RunPoliciesRepository:
    """Persistence access for explicit scheduler run policies."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a shared SQLAlchemy session."""
        self.session = session

    def get_by_id(self, run_id: str) -> RunPolicy | None:
        """Return the explicit run policy for a run, if present."""
        result = self.session.execute(
            select(RunPolicy).where(RunPolicy.run_id == run_id)
        )
        return result.scalar_one_or_none()
