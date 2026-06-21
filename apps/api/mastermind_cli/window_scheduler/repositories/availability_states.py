"""Repository for window scheduler availability state."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from mastermind_cli.window_scheduler.models.availability_state import AvailabilityState


class AvailabilityStatesRepository:
    """Persistence access for backend availability observations."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a shared SQLAlchemy session."""
        self.session = session

    def upsert(
        self,
        *,
        backend_id: str,
        state: str,
        estimated_reset_at: datetime | None,
        estimation_source: str | None,
        estimation_confidence: str | None,
        last_verified_at: datetime | None,
    ) -> AvailabilityState:
        """Create or update the availability state for a backend."""
        result = self.session.execute(
            select(AvailabilityState).where(AvailabilityState.backend_id == backend_id)
        )
        record = result.scalar_one_or_none()
        if record is None:
            record = AvailabilityState(
                backend_id=backend_id,
                state=state,
                estimated_reset_at=estimated_reset_at,
                estimation_source=estimation_source,
                estimation_confidence=estimation_confidence,
                last_verified_at=last_verified_at,
            )
            self.session.add(record)
        else:
            record.state = state
            record.estimated_reset_at = estimated_reset_at
            record.estimation_source = estimation_source
            record.estimation_confidence = estimation_confidence
            record.last_verified_at = last_verified_at

        self.session.commit()
        self.session.refresh(record)
        return record
