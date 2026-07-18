"""Universal gap records with optional domain-assurance metadata."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from mastermind_cli.project_state.database.base import Base


class GapRecord(Base):
    """A project gap shared by product, security, quality, and other lenses."""

    __tablename__ = "ps_gaps"

    gap_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        ForeignKey("ps_projects.project_id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    lens: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    threat: Mapped[str | None] = mapped_column(Text, nullable=True)
    impact: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    likelihood: Mapped[str | None] = mapped_column(String(32), nullable=True)
    evidence_refs: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    control_refs: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    residual_risk: Mapped[str | None] = mapped_column(String(32), nullable=True)
    treatment: Mapped[str | None] = mapped_column(String(32), nullable=True)
    approval_required: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    risk_acceptance_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    review_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
