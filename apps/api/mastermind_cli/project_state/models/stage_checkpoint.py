"""Authoritative stage transition, checkpoint, and projection outbox models."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from mastermind_cli.project_state.database.base import Base


class StageTransitionRecord(Base):
    """Immutable result for one canonical stage transition idempotency key."""

    __tablename__ = "ps_stage_transitions"
    __table_args__ = (
        UniqueConstraint(
            "run_id",
            "bundle_hash",
            "stage_id",
            "attempt",
            "transition_sequence",
            name="uq_ps_stage_transition_idempotency",
        ),
    )

    transition_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    run_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    bundle_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    stage_id: Mapped[str] = mapped_column(String(255), nullable=False)
    attempt: Mapped[int] = mapped_column(Integer, nullable=False)
    transition_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    result_payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    checkpoint_payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    evidence_refs: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    artifact_refs: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class StageCheckpointRecord(Base):
    """Current optimistic-lock checkpoint for one stage execution run."""

    __tablename__ = "ps_stage_checkpoints"

    run_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    checkpoint_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    bundle_id: Mapped[str] = mapped_column(String(255), nullable=False)
    objective_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    bundle_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    checkpoint_payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class StageTransitionOutbox(Base):
    """Retryable downstream projection event committed with a stage transition."""

    __tablename__ = "ps_stage_transition_outbox"
    __table_args__ = (
        UniqueConstraint(
            "transition_id",
            "destination",
            name="uq_ps_stage_transition_outbox_destination",
        ),
    )

    event_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    transition_id: Mapped[str] = mapped_column(
        ForeignKey("ps_stage_transitions.transition_id"),
        nullable=False,
        index=True,
    )
    destination: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
