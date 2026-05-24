"""Checkpoint repository for project state."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from mastermind_cli.project_state.models.checkpoint import Checkpoint


class CheckpointsRepository:
    """Repository for task checkpoints."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a shared SQLAlchemy session."""
        self.session = session

    def list_recent_by_project(self, project_id: str, limit: int) -> list[Checkpoint]:
        """Return recent checkpoints for a project ordered by creation time."""
        result = self.session.execute(
            select(Checkpoint)
            .where(Checkpoint.project_id == project_id)
            .order_by(desc(Checkpoint.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())

    def get_latest_by_task(self, project_id: str, task_id: str) -> Checkpoint | None:
        """Return the most recent checkpoint for a specific task, if any."""
        result = self.session.execute(
            select(Checkpoint)
            .where(Checkpoint.project_id == project_id, Checkpoint.task_id == task_id)
            .order_by(desc(Checkpoint.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

    def get_latest_by_project(self, project_id: str) -> Checkpoint | None:
        """Return the most recent checkpoint for a project, if any."""
        result = self.session.execute(
            select(Checkpoint)
            .where(Checkpoint.project_id == project_id)
            .order_by(desc(Checkpoint.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

    def create_checkpoint(
        self,
        checkpoint_id: str,
        project_id: str,
        task_id: str,
        run_id: str | None,
        context_summary: dict[str, object],
        resume_state: dict[str, object],
        next_step_summary: str,
        created_at: datetime,
    ) -> Checkpoint:
        """Create and persist a new task checkpoint."""
        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            project_id=project_id,
            task_id=task_id,
            run_id=run_id,
            context_summary=context_summary,
            resume_state=resume_state,
            next_step_summary=next_step_summary,
            created_at=created_at,
        )
        self.session.add(checkpoint)
        self.session.commit()
        self.session.refresh(checkpoint)
        return checkpoint
