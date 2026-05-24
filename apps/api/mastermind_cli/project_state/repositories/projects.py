"""Project repository for project state."""

from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from mastermind_cli.project_state.models.project import Project


class ProjectsRepository:
    """Repository for project records."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a shared SQLAlchemy session."""
        self.session = session

    def list_projects(self, limit: int = 100) -> list[Project]:
        """Return recent projects ordered by update time."""
        result = self.session.execute(
            select(Project)
            .order_by(desc(Project.updated_at), desc(Project.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())

    def get_by_id(self, project_id: str) -> Project | None:
        """Return a project by ID, or None if it does not exist."""
        result = self.session.execute(
            select(Project).where(Project.project_id == project_id)
        )
        return result.scalar_one_or_none()
