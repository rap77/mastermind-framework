"""Application service for projecting planning files into the database."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from mastermind_cli.project_state.models.planning_projection import (
    ObjectiveDocumentRecord,
    ObjectiveEventRecord,
    ObjectiveSyncState,
)
from mastermind_cli.project_state.repositories.planning_projection import (
    PlanningProjectionRepository,
)


class PlanningProjectionService:
    """Project filesystem-backed planning state into database rows."""

    def __init__(self, session: Session) -> None:
        """Initialize the service with a shared SQLAlchemy session."""
        self.repository = PlanningProjectionRepository(session)

    @staticmethod
    def _now() -> datetime:
        """Return the current UTC timestamp."""
        return datetime.now(timezone.utc)

    @staticmethod
    def _hash_content(content: str) -> str:
        """Return a stable content hash for a planning document."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @staticmethod
    def _maybe_str(payload: dict[str, object], key: str) -> str | None:
        """Return a string field from payload only when it is present."""
        value = payload.get(key)
        return value if isinstance(value, str) else None

    def record_document_write(
        self,
        *,
        objective_slug: str,
        doc_type: str,
        source_path: str,
        content: str,
        actor: str,
        version: int | None = None,
        is_canonical: bool = True,
    ) -> ObjectiveDocumentRecord:
        """Persist a document snapshot and emit a matching event."""
        now = self._now()
        document_id = str(uuid.uuid4())
        event_id = str(uuid.uuid4())
        content_hash = self._hash_content(content)
        if version is None:
            latest = self.repository.get_latest_document(objective_slug, doc_type)
            version = 1 if latest is None else latest.version + 1
        snapshot = self.repository.record_document_snapshot(
            document_id=document_id,
            objective_slug=objective_slug,
            doc_type=doc_type,
            source_path=source_path,
            content_hash=content_hash,
            version=version,
            is_canonical=is_canonical,
            created_at=now,
            updated_at=now,
        )
        self.repository.record_event(
            event_id=event_id,
            objective_slug=objective_slug,
            event_type="DocumentWritten",
            payload_json=json.dumps(
                {
                    "document_id": document_id,
                    "doc_type": doc_type,
                    "source_path": source_path,
                    "content_hash": content_hash,
                    "version": version,
                    "is_canonical": is_canonical,
                },
                sort_keys=True,
            ),
            actor=actor,
            source_path=source_path,
            occurred_at=now,
        )
        return snapshot

    def record_objective_activity(
        self,
        *,
        objective_slug: str,
        event_type: str,
        payload: dict[str, object],
        actor: str,
        source_path: str | None = None,
    ) -> ObjectiveEventRecord:
        """Persist an objective-level event and refresh projection state."""
        now = self._now()
        event = self.repository.record_event(
            event_id=str(uuid.uuid4()),
            objective_slug=objective_slug,
            event_type=event_type,
            payload_json=json.dumps(payload, sort_keys=True),
            actor=actor,
            source_path=source_path,
            occurred_at=now,
        )
        self.repository.upsert_projection(
            objective_slug=objective_slug,
            current_status=str(payload.get("current_status", "active")),
            current_task=self._maybe_str(payload, "current_task"),
            current_handoff_path=self._maybe_str(payload, "current_handoff_path"),
            recommended_next=self._maybe_str(payload, "recommended_next"),
            last_event_id=event.event_id,
            last_synced_at=now,
        )
        return event

    def mark_surface_synced(
        self,
        *,
        surface: str,
        content: str,
        error: str | None = None,
        sync_version: int = 1,
    ) -> ObjectiveSyncState:
        """Persist the sync status for a filesystem planning surface."""
        return self.repository.upsert_sync_state(
            surface=surface,
            last_scan_at=self._now(),
            last_hash=self._hash_content(content),
            last_error=error,
            sync_version=sync_version,
        )
