"""Artifact versioning and lineage repository."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import asc, select
from sqlalchemy.orm import Session

from mastermind_cli.project_state.models.artifact import ArtifactLink, ArtifactVersion


class ArtifactRepository:
    """Repository for artifact versions and causal links."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a SQLAlchemy session."""
        self.session = session

    def create_version(
        self,
        version_id: str,
        artifact_id: str,
        project_id: str,
        artifact_type: str,
        version: int,
        content_hash: str,
        created_at: datetime,
        metadata_json: dict[str, object],
    ) -> ArtifactVersion:
        """Persist a new artifact version and return it."""
        record = ArtifactVersion(
            version_id=version_id,
            artifact_id=artifact_id,
            project_id=project_id,
            artifact_type=artifact_type,
            version=version,
            content_hash=content_hash,
            created_at=created_at,
            metadata_json=metadata_json,
        )
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def create_link(
        self,
        link_id: str,
        source_artifact_id: str,
        target_artifact_id: str,
        link_type: str,
        created_at: datetime,
        task_id: str | None = None,
        decision_id: str | None = None,
        checkpoint_id: str | None = None,
    ) -> ArtifactLink:
        """Persist a new causal link between two artifact versions and return it."""
        link = ArtifactLink(
            link_id=link_id,
            source_artifact_id=source_artifact_id,
            target_artifact_id=target_artifact_id,
            link_type=link_type,
            task_id=task_id,
            decision_id=decision_id,
            checkpoint_id=checkpoint_id,
            created_at=created_at,
        )
        self.session.add(link)
        self.session.commit()
        self.session.refresh(link)
        return link

    def get_versions_by_artifact_id(self, artifact_id: str) -> list[ArtifactVersion]:
        """Return all versions for a logical artifact sorted ascending by version."""
        result = self.session.execute(
            select(ArtifactVersion)
            .where(ArtifactVersion.artifact_id == artifact_id)
            .order_by(asc(ArtifactVersion.version))
        )
        return list(result.scalars().all())
