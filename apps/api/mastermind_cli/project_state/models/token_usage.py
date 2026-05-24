"""Token usage telemetry model for the project state thin slice."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Float, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from mastermind_cli.project_state.database.base import Base


class TokenUsageEvent(Base):
    """Token and cost usage event tied to project/task/run context."""

    __tablename__ = "ps_token_usage_events"

    usage_event_id: Mapped[str] = mapped_column(String(255), primary_key=True)
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
    run_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    provider: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    model: Mapped[str] = mapped_column(String(255), nullable=False)
    auth_mode: Mapped[str] = mapped_column(String(64), nullable=False)
    prompt_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estimated_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    metadata_json: Mapped[dict[str, object]] = mapped_column(
        "metadata", JSON, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
