"""Planning projection models for objective document history and sync state."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from mastermind_cli.project_state.database.base import Base


class ObjectiveDocumentRecord(Base):
    """Versioned filesystem-backed planning document snapshot."""

    __tablename__ = "ps_objective_documents"
    __table_args__ = (
        UniqueConstraint(
            "objective_slug",
            "doc_type",
            "version",
            name="uq_ps_objective_documents_version",
        ),
    )

    document_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    objective_slug: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    doc_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    source_path: Mapped[str] = mapped_column(String(512), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_canonical: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )


class ObjectiveEventRecord(Base):
    """Immutable event emitted when a planning document or objective changes."""

    __tablename__ = "ps_objective_events"

    event_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    objective_slug: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    actor: Mapped[str] = mapped_column(String(255), nullable=False)
    source_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )


class ObjectiveProjectionState(Base):
    """Current denormalized objective state derived from documents and events."""

    __tablename__ = "ps_objective_projection"

    objective_slug: Mapped[str] = mapped_column(String(255), primary_key=True)
    current_status: Mapped[str] = mapped_column(String(64), nullable=False)
    current_task: Mapped[str | None] = mapped_column(String(255), nullable=True)
    current_handoff_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    recommended_next: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_event_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )


class ObjectiveSyncState(Base):
    """Surface-level sync tracking for file-backed objective projections."""

    __tablename__ = "ps_objective_sync_state"

    surface: Mapped[str] = mapped_column(String(64), primary_key=True)
    last_scan_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    sync_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
