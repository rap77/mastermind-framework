"""Decision record model for the project state thin slice."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from mastermind_cli.project_state.database.base import Base


class DecisionRecord(Base):
    """Decision record linked to a project and optionally a task."""

    __tablename__ = "ps_decision_records"

    decision_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        ForeignKey("ps_projects.project_id"),
        nullable=False,
        index=True,
    )
    task_id: Mapped[str | None] = mapped_column(
        ForeignKey("ps_tasks.task_id"),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    rationale_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict[str, object]] = mapped_column(
        "metadata", JSON, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
