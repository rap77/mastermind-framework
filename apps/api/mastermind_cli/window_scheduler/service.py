"""Minimal service layer for the first window-scheduler coding slice."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session, sessionmaker

from mastermind_cli.window_scheduler.models.availability_state import AvailabilityState
from mastermind_cli.window_scheduler.models.scheduler_checkpoint import (
    SchedulerCheckpoint,
)
from mastermind_cli.window_scheduler.models.scheduler_event import SchedulerEvent
from mastermind_cli.window_scheduler.policy import (
    EligibleBackend,
    SwitchDecision,
    compute_eligible_backends,
    plan_switch_decision as choose_switch_decision,
)
from mastermind_cli.window_scheduler.repositories.availability_states import (
    AvailabilityStatesRepository,
)
from mastermind_cli.window_scheduler.repositories.backend_sessions import (
    BackendSessionsRepository,
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
            persisted = repository.upsert(
                backend_id=backend_id,
                state=state,
                estimated_reset_at=normalized_reset,
                estimation_source=source,
                estimation_confidence=confidence,
                last_verified_at=verified_at,
            )
            persisted.estimated_reset_at = _normalize_datetime(
                persisted.estimated_reset_at
            )
            persisted.last_verified_at = _normalize_datetime(persisted.last_verified_at)
            return persisted

    def get_latest_checkpoint(self, project_id: str) -> SchedulerCheckpoint | None:
        """Return the latest checkpoint recorded for a project, if any."""
        with self.session_factory() as session:
            repository = SchedulerCheckpointsRepository(session)
            return repository.get_latest_by_project(project_id)

    def list_recent_events(
        self,
        *,
        project_id: str,
        run_id: str | None = None,
        limit: int = 20,
    ) -> list[SchedulerEvent]:
        """Return recent scheduler events for a project, optionally scoped to a run."""
        with self.session_factory() as session:
            repository = SchedulerEventsRepository(session)
            return repository.list_recent(
                project_id=project_id,
                run_id=run_id,
                limit=limit,
            )

    def get_eligible_backends(self, *, run_id: str) -> list[EligibleBackend]:
        """Return the eligible backend set for the given run policy."""
        with self.session_factory() as session:
            policies = RunPoliciesRepository(session)
            policy = policies.get_by_id(run_id)
            if policy is None:
                raise ValueError("run_policy is required before evaluating eligibility")

            backends = BackendSessionsRepository(session).list_enabled()
            backend_ids = [backend.backend_id for backend in backends]
            availability_rows = AvailabilityStatesRepository(
                session
            ).list_by_backend_ids(backend_ids)
            availability_by_backend = {row.backend_id: row for row in availability_rows}
            return compute_eligible_backends(
                backends=backends,
                availability_by_backend=availability_by_backend,
                policy=policy,
            )

    def plan_switch_decision(
        self,
        *,
        run_id: str,
        current_backend_id: str,
        switches_used: int,
        task_risk_tier: str | None = None,
    ) -> SwitchDecision:
        """Return the next switch-policy outcome for the active run."""
        with self.session_factory() as session:
            policies = RunPoliciesRepository(session)
            policy = policies.get_by_id(run_id)
            if policy is None:
                raise ValueError(
                    "run_policy is required before planning backend_switch"
                )
            current_availability = AvailabilityStatesRepository(session).get_by_id(
                current_backend_id
            )

        eligible = self.get_eligible_backends(run_id=run_id)
        return choose_switch_decision(
            current_backend_id=current_backend_id,
            eligible_backends=eligible,
            policy=policy,
            switches_used=switches_used,
            task_risk_tier=task_risk_tier,
            current_availability=current_availability,
        )

    def execute_decision(
        self,
        *,
        event_id: str,
        checkpoint_id: str,
        run_id: str,
        project_id: str,
        current_backend_id: str,
        decision: SwitchDecision,
        task_id: str,
        step_id: str,
        context_summary: dict[str, object],
        next_step_summary: str,
    ) -> SchedulerEvent:
        """Persist the side effects of a scheduler decision."""
        if decision.outcome == "switch":
            checkpoint = self.record_checkpoint(
                checkpoint_id=checkpoint_id,
                run_id=run_id,
                project_id=project_id,
                task_id=task_id,
                step_id=step_id,
                context_summary=context_summary,
                next_step_summary=next_step_summary,
            )
            return self.record_backend_switch(
                event_id=event_id,
                run_id=run_id,
                project_id=project_id,
                from_backend=current_backend_id,
                to_backend=_require_selected_backend(decision),
                reason=decision.reason,
                checkpoint_id=checkpoint.checkpoint_id,
                decision_outcome=decision.outcome,
                task_id=task_id,
            )

        event = SchedulerEvent(
            event_id=event_id,
            run_id=run_id,
            project_id=project_id,
            task_id=task_id,
            type=decision.outcome,
            from_backend=current_backend_id,
            to_backend=decision.selected_backend_id,
            reason=decision.reason,
            estimated_reset_at=_normalize_datetime(decision.retry_at),
            decision_outcome=decision.outcome,
            eligibility_basis=decision.eligibility_basis,
            next_step_summary=next_step_summary,
        )
        persisted = self.record_event(event)
        persisted.estimated_reset_at = _normalize_datetime(persisted.estimated_reset_at)
        return persisted


def _coerce_datetime(value: datetime | str | None) -> datetime | None:
    """Convert ISO-like string timestamps into timezone-aware datetimes."""
    if value is None:
        return value
    if isinstance(value, datetime):
        return _normalize_datetime(value)
    normalized = value.strip()
    if not normalized:
        return None
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(
            "estimated_reset_at must be a valid ISO 8601 datetime string"
        ) from exc
    return _normalize_datetime(parsed)


def _normalize_datetime(value: datetime | None) -> datetime | None:
    """Ensure datetimes returned from persistence are UTC-aware."""
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _require_selected_backend(decision: SwitchDecision) -> str:
    """Return the selected backend from a decision or raise if absent."""
    if decision.selected_backend_id is None:
        raise ValueError("selected_backend_id is required for this decision")
    return decision.selected_backend_id
