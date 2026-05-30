"""AvailabilityState model for window scheduler — temporal backend state."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from mastermind_cli.window_scheduler.database.base import Base


class AvailabilityState(Base):
    """Temporal state record for a backend window.

    Tracks operational and temporal state of each backend.
    Corresponds to canonical entity B in docs/canonical/19-WINDOW-SCHEDULER-DATA-SCHEMA.md.
    """

    __tablename__ = "ws_availability_states"

    backend_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("ws_backend_sessions.backend_id"),
        primary_key=True,
    )
    state: Mapped[str] = mapped_column(
        String(32), nullable=False, index=True
    )  # active, exhausted, cooling_down, paused, disabled, blocked
    window_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    window_exhausted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    estimated_reset_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # Schema constraint: all reset estimations must record estimation_source
    estimation_source: Mapped[str | None] = mapped_column(
        String(32), nullable=True
    )  # explicit | heuristic | manual
    # Schema constraint: all reset estimations must record estimation_confidence
    estimation_confidence: Mapped[str | None] = mapped_column(
        String(16), nullable=True
    )  # high | medium | low | unknown
    last_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
