"""Checkpoint model for task continuity."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from mastermind_cli.project_state.database.base import Base


class Checkpoint(Base):
    """Checkpoint used to resume a task with minimum context."""

    __tablename__ = "ps_checkpoints"

    checkpoint_id: Mapped[str] = mapped_column(String(255), primary_key=True)
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
    run_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    context_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    resume_state: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    next_step_summary: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
