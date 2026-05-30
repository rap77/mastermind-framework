"""BackendSession model for window scheduler — backend inventory."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from mastermind_cli.window_scheduler.database.base import Base


class BackendSession(Base):
    """Backend inventory record for the scheduler.

    Represents a usable account/backend in the runtime.
    Corresponds to canonical entity A in docs/canonical/19-WINDOW-SCHEDULER-DATA-SCHEMA.md.
    """

    __tablename__ = "ws_backend_sessions"

    backend_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    provider: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    account_id: Mapped[str] = mapped_column(String(255), nullable=False)
    auth_mode: Mapped[str] = mapped_column(String(32), nullable=False)
    model_family: Mapped[str] = mapped_column(String(64), nullable=False)
    priority: Mapped[int] = mapped_column(default=0)
    cost_tier: Mapped[str] = mapped_column(String(32), nullable=False)
    risk_tier: Mapped[str] = mapped_column(String(32), nullable=False)
    overnight_allowed: Mapped[bool] = mapped_column(Boolean, default=False)
    automatic_switch_allowed: Mapped[bool] = mapped_column(Boolean, default=False)
    human_confirmation_required: Mapped[bool] = mapped_column(Boolean, default=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
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
