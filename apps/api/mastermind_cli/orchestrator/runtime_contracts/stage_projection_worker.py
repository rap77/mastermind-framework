"""Retry committed stage transition projections from the project-state outbox."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from mastermind_cli.project_state.models.stage_checkpoint import (
    StageTransitionOutbox,
)

StageProjector = Callable[[dict[str, object]], None]


@dataclass(frozen=True, slots=True)
class ProjectionFailure:
    """One outbox event that its destination projector did not confirm."""

    event_id: str
    reason: str


@dataclass(frozen=True, slots=True)
class ProjectionBatchResult:
    """Observable result of one pending-outbox processing pass."""

    attempted: int
    processed: int
    failures: tuple[ProjectionFailure, ...]

    @property
    def failed_event_ids(self) -> tuple[str, ...]:
        """Return failed event IDs in deterministic processing order."""
        return tuple(failure.event_id for failure in self.failures)


class StageProjectionWorker:
    """Project pending events and acknowledge only confirmed destinations."""

    def __init__(
        self,
        session: Session,
        *,
        projectors: Mapping[str, StageProjector],
    ) -> None:
        """Initialize the worker with the authoritative session and destinations."""
        self._session = session
        self._projectors = dict(projectors)

    def process_pending(self) -> ProjectionBatchResult:
        """Attempt each pending event once, leaving failures available for retry."""
        pending = tuple(
            self._session.execute(
                select(
                    StageTransitionOutbox.event_id,
                    StageTransitionOutbox.destination,
                    StageTransitionOutbox.payload,
                )
                .where(StageTransitionOutbox.processed_at.is_(None))
                .order_by(
                    StageTransitionOutbox.created_at, StageTransitionOutbox.event_id
                )
            )
        )
        self._session.rollback()

        processed = 0
        failures: list[ProjectionFailure] = []
        for event_id, destination, payload in pending:
            projector = self._projectors.get(destination)
            if projector is None:
                failures.append(
                    ProjectionFailure(
                        event_id=event_id,
                        reason=f"No projector registered for destination {destination}",
                    )
                )
                continue
            try:
                projector(payload)
            except Exception as error:  # Projector adapters define their own errors.
                failures.append(ProjectionFailure(event_id=event_id, reason=str(error)))
                continue

            self._session.execute(
                update(StageTransitionOutbox)
                .where(
                    StageTransitionOutbox.event_id == event_id,
                    StageTransitionOutbox.processed_at.is_(None),
                )
                .values(processed_at=datetime.now(UTC))
            )
            self._session.commit()
            processed += 1

        return ProjectionBatchResult(
            attempted=len(pending),
            processed=processed,
            failures=tuple(failures),
        )
