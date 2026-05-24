"""Task run model for project execution state."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from mastermind_cli.project_state.database.base import Base


class TaskRun(Base):
    """Task run record for active execution and runtime observability."""

    __tablename__ = "ps_task_runs"

    run_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        ForeignKey("ps_projects.project_id"),
        nullable=False,
        index=True,
    )
    task_id: Mapped[str] = mapped_column(
        ForeignKey("ps_tasks.task_id"),
        nullable=False,
        index=True,
    )
    actor_type: Mapped[str] = mapped_column(String(64), nullable=False)
    actor_id: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    metadata_json: Mapped[dict[str, object]] = mapped_column(
        "metadata", JSON, default=dict
    )
