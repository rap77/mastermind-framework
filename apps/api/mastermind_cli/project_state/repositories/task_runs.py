"""Task run repository for project state."""

from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from mastermind_cli.project_state.models.task_run import TaskRun


class TaskRunsRepository:
    """Repository for task run records."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a shared SQLAlchemy session."""
        self.session = session

    def get_by_id(self, project_id: str, run_id: str) -> TaskRun | None:
        """Return a task run by project and run ID, or None if missing."""
        result = self.session.execute(
            select(TaskRun).where(
                TaskRun.project_id == project_id,
                TaskRun.run_id == run_id,
            )
        )
        return result.scalar_one_or_none()

    def list_active_by_project(self, project_id: str, limit: int) -> list[TaskRun]:
        """Return active task runs ordered by most recent start time."""
        result = self.session.execute(
            select(TaskRun)
            .where(
                TaskRun.project_id == project_id,
                TaskRun.ended_at.is_(None),
            )
            .order_by(desc(TaskRun.started_at))
            .limit(limit)
        )
        return list(result.scalars().all())
