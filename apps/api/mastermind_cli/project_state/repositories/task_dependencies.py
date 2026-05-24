"""Task dependency repository for project state."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from mastermind_cli.project_state.models.task_dependency import TaskDependency


class TaskDependenciesRepository:
    """Repository for task dependency edges."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a shared SQLAlchemy session."""
        self.session = session

    def list_by_task(self, task_id: str) -> list[TaskDependency]:
        """Return dependency edges for a task."""
        result = self.session.execute(
            select(TaskDependency).where(TaskDependency.task_id == task_id)
        )
        return list(result.scalars().all())
