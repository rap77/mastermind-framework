"""SchedulerEvent model for window scheduler — auditable event record."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from mastermind_cli.window_scheduler.database.base import Base


class SchedulerEvent(Base):
    """Auditable event record for scheduler transitions.

    Records every important scheduler event for later audit and review.
    Corresponds to canonical entity D in docs/canonical/19-WINDOW-SCHEDULER-DATA-SCHEMA.md.
    Schema constraint: no backend_switch without checkpoint_id.
    """

    __tablename__ = "ws_scheduler_events"

    event_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    run_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    task_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    type: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )  # window_started | window_exhausted | backend_switch | pause_for_user | automatic_resume | retry_scheduled | all_backends_blocked
    from_backend: Mapped[str | None] = mapped_column(String(255), nullable=True)
    to_backend: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Schema constraint: no backend_switch without checkpoint_id
    checkpoint_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    execution_mode: Mapped[str | None] = mapped_column(String(32), nullable=True)
    estimated_reset_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    decision_outcome: Mapped[str | None] = mapped_column(String(64), nullable=True)
    eligibility_basis: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_step_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
