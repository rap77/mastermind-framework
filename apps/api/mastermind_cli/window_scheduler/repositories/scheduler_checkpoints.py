"""Repository for scheduler checkpoints."""

from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from mastermind_cli.window_scheduler.models.scheduler_checkpoint import (
    SchedulerCheckpoint,
)


class SchedulerCheckpointsRepository:
    """Persistence access for resumable scheduler checkpoints."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a shared SQLAlchemy session."""
        self.session = session

    def create(self, checkpoint: SchedulerCheckpoint) -> SchedulerCheckpoint:
        """Persist a new scheduler checkpoint."""
        self.session.add(checkpoint)
        self.session.commit()
        self.session.refresh(checkpoint)
        return checkpoint

    def get_latest_by_project(self, project_id: str) -> SchedulerCheckpoint | None:
        """Return the most recent checkpoint for a project, if any."""
        result = self.session.execute(
            select(SchedulerCheckpoint)
            .where(SchedulerCheckpoint.project_id == project_id)
            .order_by(desc(SchedulerCheckpoint.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()
