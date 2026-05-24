"""Task repository for project state."""

from __future__ import annotations

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from mastermind_cli.project_state.models.task import Task


class TasksRepository:
    """Repository for project task records."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a shared SQLAlchemy session."""
        self.session = session

    def get_by_id(self, project_id: str, task_id: str) -> Task | None:
        """Return a task by project and task ID, or None if it does not exist."""
        result = self.session.execute(
            select(Task).where(Task.project_id == project_id, Task.task_id == task_id)
        )
        return result.scalar_one_or_none()

    def list_recent_by_project(self, project_id: str, limit: int) -> list[Task]:
        """Return recent task snapshots for a project ordered by update time."""
        result = self.session.execute(
            select(Task)
            .where(Task.project_id == project_id)
            .order_by(desc(Task.updated_at), desc(Task.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())

    def list_by_project(self, project_id: str, limit: int) -> list[Task]:
        """Return tasks for a project ordered by update and creation times."""
        result = self.session.execute(
            select(Task)
            .where(Task.project_id == project_id)
            .order_by(desc(Task.updated_at), desc(Task.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())

    def count_by_project(self, project_id: str) -> int:
        """Count all tasks for a project."""
        result = self.session.execute(
            select(func.count()).select_from(Task).where(Task.project_id == project_id)
        )
        return int(result.scalar_one())

    def count_by_project_and_status(self, project_id: str, status: str) -> int:
        """Count tasks for a project filtered by status."""
        result = self.session.execute(
            select(func.count())
            .select_from(Task)
            .where(Task.project_id == project_id, Task.status == status)
        )
        return int(result.scalar_one())

    def update_status(
        self, project_id: str, task_id: str, new_status: str
    ) -> Task | None:
        """Update the status of a task and return the updated record, or None if not found."""
        task = self.get_by_id(project_id, task_id)
        if task is None:
            return None
        task.status = new_status
        return task
