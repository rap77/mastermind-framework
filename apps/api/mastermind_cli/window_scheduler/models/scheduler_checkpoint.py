"""SchedulerCheckpoint model for window scheduler — minimal resume point."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from mastermind_cli.window_scheduler.database.base import Base


class SchedulerCheckpoint(Base):
    """Minimal resume point for task continuation.

    Captures the minimum context needed to resume execution on another backend.
    Corresponds to canonical entity E in docs/canonical/19-WINDOW-SCHEDULER-DATA-SCHEMA.md.
    Schema constraint: no checkpoint without next_step_summary.
    """

    __tablename__ = "ws_scheduler_checkpoints"

    checkpoint_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    run_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    task_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    step_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    context_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    artifacts: Mapped[list[str]] = mapped_column(JSON, default=list)
    # Schema constraint: no checkpoint without next_step_summary
    next_step_summary: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
