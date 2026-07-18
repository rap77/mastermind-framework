"""Repository for objective planning projection state."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from mastermind_cli.project_state.models.planning_projection import (
    ObjectiveDocumentRecord,
    ObjectiveEventRecord,
    ObjectiveProjectionState,
    ObjectiveSyncState,
)


class PlanningProjectionRepository:
    """Persist and query objective planning projection records."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a SQLAlchemy session."""
        self.session = session

    def record_document_snapshot(
        self,
        *,
        document_id: str,
        objective_slug: str,
        doc_type: str,
        source_path: str,
        content_hash: str,
        version: int,
        is_canonical: bool,
        created_at: datetime,
        updated_at: datetime,
    ) -> ObjectiveDocumentRecord:
        """Persist a filesystem-backed objective document snapshot."""
        record = ObjectiveDocumentRecord(
            document_id=document_id,
            objective_slug=objective_slug,
            doc_type=doc_type,
            source_path=source_path,
            content_hash=content_hash,
            version=version,
            is_canonical=is_canonical,
            created_at=created_at,
            updated_at=updated_at,
        )
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def record_event(
        self,
        *,
        event_id: str,
        objective_slug: str,
        event_type: str,
        payload_json: str,
        actor: str,
        source_path: str | None,
        occurred_at: datetime,
    ) -> ObjectiveEventRecord:
        """Persist an immutable planning event."""
        record = ObjectiveEventRecord(
            event_id=event_id,
            objective_slug=objective_slug,
            event_type=event_type,
            payload_json=payload_json,
            actor=actor,
            source_path=source_path,
            occurred_at=occurred_at,
        )
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def upsert_projection(
        self,
        *,
        objective_slug: str,
        current_status: str,
        current_task: str | None,
        current_handoff_path: str | None,
        recommended_next: str | None,
        last_event_id: str | None,
        last_synced_at: datetime,
    ) -> ObjectiveProjectionState:
        """Persist the current denormalized objective projection state."""
        record = self.session.get(ObjectiveProjectionState, objective_slug)
        if record is None:
            record = ObjectiveProjectionState(
                objective_slug=objective_slug,
                current_status=current_status,
                current_task=current_task,
                current_handoff_path=current_handoff_path,
                recommended_next=recommended_next,
                last_event_id=last_event_id,
                last_synced_at=last_synced_at,
            )
            self.session.add(record)
        else:
            record.current_status = current_status
            record.current_task = current_task
            record.current_handoff_path = current_handoff_path
            record.recommended_next = recommended_next
            record.last_event_id = last_event_id
            record.last_synced_at = last_synced_at
        self.session.commit()
        self.session.refresh(record)
        return record

    def upsert_sync_state(
        self,
        *,
        surface: str,
        last_scan_at: datetime,
        last_hash: str | None,
        last_error: str | None,
        sync_version: int,
    ) -> ObjectiveSyncState:
        """Persist the sync status for a planning surface."""
        record = self.session.get(ObjectiveSyncState, surface)
        if record is None:
            record = ObjectiveSyncState(
                surface=surface,
                last_scan_at=last_scan_at,
                last_hash=last_hash,
                last_error=last_error,
                sync_version=sync_version,
            )
            self.session.add(record)
        else:
            record.last_scan_at = last_scan_at
            record.last_hash = last_hash
            record.last_error = last_error
            record.sync_version = sync_version
        self.session.commit()
        self.session.refresh(record)
        return record

    def get_latest_document(
        self, objective_slug: str, doc_type: str
    ) -> ObjectiveDocumentRecord | None:
        """Return the latest document snapshot for an objective/doc type."""
        result = self.session.execute(
            select(ObjectiveDocumentRecord)
            .where(
                ObjectiveDocumentRecord.objective_slug == objective_slug,
                ObjectiveDocumentRecord.doc_type == doc_type,
            )
            .order_by(ObjectiveDocumentRecord.version.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
