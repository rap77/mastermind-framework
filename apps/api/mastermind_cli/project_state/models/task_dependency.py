"""Task dependency model for project task graph."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from mastermind_cli.project_state.database.base import Base


class TaskDependency(Base):
    """Dependency edge between two tasks in a project."""

    __tablename__ = "ps_task_dependencies"

    dependency_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    task_id: Mapped[str] = mapped_column(
        ForeignKey("ps_tasks.task_id"),
        nullable=False,
        index=True,
    )
    depends_on_task_id: Mapped[str] = mapped_column(
        ForeignKey("ps_tasks.task_id"),
        nullable=False,
        index=True,
    )
    dependency_type: Mapped[str] = mapped_column(
        String(64), nullable=False, default="blocks"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
