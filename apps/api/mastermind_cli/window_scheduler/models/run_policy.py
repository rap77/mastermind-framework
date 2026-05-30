"""RunPolicy model for window scheduler — active execution policy."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from mastermind_cli.window_scheduler.database.base import Base


class RunPolicy(Base):
    """Active execution policy for a run.

    Represents the governing policy for a specific execution run.
    Corresponds to canonical entity C in docs/canonical/19-WINDOW-SCHEDULER-DATA-SCHEMA.md.
    Schema constraint: every run must have an explicit run_policy.

    Note: project_id references ps_projects in project_state module. FK is not
    enforced at DB level to keep window_scheduler as a standalone reusable core module.
    """

    __tablename__ = "ws_run_policies"

    run_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    adapter_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    execution_mode: Mapped[str] = mapped_column(
        String(32), nullable=False
    )  # automatic | pause_and_ask | hybrid
    overnight_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    max_switches_per_run: Mapped[int] = mapped_column(Integer, default=0)
    allow_paid_api_fallback: Mapped[bool] = mapped_column(Boolean, default=False)
    require_human_for_high_risk_actions: Mapped[bool] = mapped_column(
        Boolean, default=False
    )
    max_cost_tier: Mapped[str] = mapped_column(String(32), nullable=False)
    pause_on_low_confidence_reset: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
