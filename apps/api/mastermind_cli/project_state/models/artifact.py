"""Artifact versioning and lineage models for the project state domain."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from mastermind_cli.project_state.database.base import Base


class ArtifactVersion(Base):
    """A versioned snapshot of a project artifact (spec, plan, task, etc.).

    Each row represents one immutable version of a logical artifact.
    ``artifact_id`` is a stable UUID that identifies the *logical* artifact
    (grouping key).  ``version_id`` is a per-row UUID used as the primary key
    and as the foreign key target for ``ArtifactLink``.
    The combination (artifact_id, version) is unique.
    """

    __tablename__ = "ps_artifact_versions"
    __table_args__ = (
        UniqueConstraint("artifact_id", "version", name="uq_artifact_version"),
    )

    version_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    artifact_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(
        ForeignKey("ps_projects.project_id"),
        nullable=False,
        index=True,
    )
    artifact_type: Mapped[str] = mapped_column(String(64), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    metadata_json: Mapped[dict[str, object]] = mapped_column(
        "metadata", JSON, default=dict
    )


class ArtifactLink(Base):
    """A directed causal link between two artifact versions."""

    __tablename__ = "ps_artifact_links"

    link_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    source_artifact_id: Mapped[str] = mapped_column(
        ForeignKey("ps_artifact_versions.version_id"),
        nullable=False,
        index=True,
    )
    target_artifact_id: Mapped[str] = mapped_column(
        ForeignKey("ps_artifact_versions.version_id"),
        nullable=False,
        index=True,
    )
    link_type: Mapped[str] = mapped_column(String(64), nullable=False)
    task_id: Mapped[str | None] = mapped_column(
        ForeignKey("ps_tasks.task_id"),
        nullable=True,
        index=True,
    )
    decision_id: Mapped[str | None] = mapped_column(
        ForeignKey("ps_decision_records.decision_id"),
        nullable=True,
        index=True,
    )
    checkpoint_id: Mapped[str | None] = mapped_column(
        ForeignKey("ps_checkpoints.checkpoint_id"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
