"""Minimal service layer for the first window-scheduler coding slice."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session, sessionmaker

from mastermind_cli.window_scheduler.models.availability_state import AvailabilityState
from mastermind_cli.window_scheduler.models.scheduler_checkpoint import (
    SchedulerCheckpoint,
)
from mastermind_cli.window_scheduler.models.scheduler_event import SchedulerEvent
from mastermind_cli.window_scheduler.repositories.availability_states import (
    AvailabilityStatesRepository,
)
from mastermind_cli.window_scheduler.repositories.run_policies import (
    RunPoliciesRepository,
)
from mastermind_cli.window_scheduler.repositories.scheduler_checkpoints import (
    SchedulerCheckpointsRepository,
)
from mastermind_cli.window_scheduler.repositories.scheduler_events import (
    SchedulerEventsRepository,
)
from mastermind_cli.window_scheduler.validators import (
    require_checkpoint_id_for_switch,
    require_next_step_summary,
    require_reset_estimation_metadata,
)


class WindowSchedulerService:
    """Small orchestration-safe API for scheduler persistence and invariants."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        """Initialize the service with a SQLAlchemy session factory."""
        self.session_factory = session_factory

    def record_checkpoint(
        self,
        *,
        checkpoint_id: str,
        run_id: str,
        project_id: str,
        task_id: str,
        step_id: str,
        context_summary: dict[str, object],
        next_step_summary: str,
    ) -> SchedulerCheckpoint:
        """Persist a resumable checkpoint after validating its minimum payload."""
        normalized_summary = require_next_step_summary(next_step_summary)
        checkpoint = SchedulerCheckpoint(
            checkpoint_id=checkpoint_id,
            run_id=run_id,
            project_id=project_id,
            task_id=task_id,
            step_id=step_id,
            context_summary=context_summary,
            next_step_summary=normalized_summary,
        )
        with self.session_factory() as session:
            repository = SchedulerCheckpointsRepository(session)
            return repository.create(checkpoint)

    def record_event(self, event: SchedulerEvent) -> SchedulerEvent:
        """Persist an already-constructed scheduler event."""
        with self.session_factory() as session:
            repository = SchedulerEventsRepository(session)
            return repository.create(event)

    def record_backend_switch(
        self,
        *,
        event_id: str,
        run_id: str,
        project_id: str,
        from_backend: str,
        to_backend: str,
        reason: str,
        checkpoint_id: str | None,
        decision_outcome: str,
        task_id: str | None = None,
    ) -> SchedulerEvent:
        """Persist a backend-switch event after enforcing scheduler invariants."""
        normalized_checkpoint_id = require_checkpoint_id_for_switch(checkpoint_id)
        with self.session_factory() as session:
            policies = RunPoliciesRepository(session)
            if policies.get_by_id(run_id) is None:
                raise ValueError(
                    "run_policy is required before recording backend_switch"
                )

            repository = SchedulerEventsRepository(session)
            event = SchedulerEvent(
                event_id=event_id,
                run_id=run_id,
                project_id=project_id,
                task_id=task_id,
                type="backend_switch",
                from_backend=from_backend,
                to_backend=to_backend,
                reason=reason,
                checkpoint_id=normalized_checkpoint_id,
                decision_outcome=decision_outcome,
            )
            return repository.create(event)

    def record_availability_state(
        self,
        *,
        backend_id: str,
        state: str,
        estimated_reset_at: datetime | str | None,
        estimation_source: str | None,
        estimation_confidence: str | None,
        last_verified_at: datetime | None = None,
    ) -> AvailabilityState:
        """Persist an availability update after validating reset-estimate metadata."""
        normalized_reset = _coerce_datetime(estimated_reset_at)
        source, confidence = require_reset_estimation_metadata(
            normalized_reset, estimation_source, estimation_confidence
        )
        verified_at = last_verified_at or datetime.now(timezone.utc)
        with self.session_factory() as session:
            repository = AvailabilityStatesRepository(session)
            return repository.upsert(
                backend_id=backend_id,
                state=state,
                estimated_reset_at=normalized_reset,
                estimation_source=source,
                estimation_confidence=confidence,
                last_verified_at=verified_at,
            )

    def get_latest_checkpoint(self, project_id: str) -> SchedulerCheckpoint | None:
        """Return the latest checkpoint recorded for a project, if any."""
        with self.session_factory() as session:
            repository = SchedulerCheckpointsRepository(session)
            return repository.get_latest_by_project(project_id)


def _coerce_datetime(value: datetime | str | None) -> datetime | None:
    """Convert ISO-like string timestamps into timezone-aware datetimes."""
    if value is None or isinstance(value, datetime):
        return value
    normalized = value.strip()
    if not normalized:
        return None
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed
