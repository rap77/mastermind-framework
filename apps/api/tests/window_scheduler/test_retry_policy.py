"""TDD coverage for WS-03 reset-estimation and retry behavior."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from mastermind_cli.window_scheduler import dispose_engines, initialize_database
from mastermind_cli.window_scheduler.database.session import get_session_factory
from mastermind_cli.window_scheduler.models.backend_session import BackendSession
from mastermind_cli.window_scheduler.models.run_policy import RunPolicy
from mastermind_cli.window_scheduler.service import WindowSchedulerService


def _build_service(tmp_path: Path) -> WindowSchedulerService:
    """Create a scheduler service backed by a temporary SQLite database."""
    database_url = f"sqlite:///{tmp_path / 'window_scheduler_retry.db'}"
    dispose_engines()
    initialize_database(database_url)
    return WindowSchedulerService(get_session_factory(database_url))


def _seed_run_policy(
    service: WindowSchedulerService,
    *,
    pause_on_low_confidence_reset: bool = True,
) -> None:
    """Insert a policy record for retry-policy tests."""
    with service.session_factory() as session:
        session.add(
            RunPolicy(
                run_id="run-1",
                project_id="project-1",
                execution_mode="hybrid",
                overnight_mode=True,
                max_switches_per_run=3,
                allow_paid_api_fallback=False,
                require_human_for_high_risk_actions=False,
                max_cost_tier="medium",
                pause_on_low_confidence_reset=pause_on_low_confidence_reset,
            )
        )
        session.commit()


def _seed_backend(service: WindowSchedulerService, backend_id: str) -> None:
    """Insert a backend session for retry-policy tests."""
    with service.session_factory() as session:
        session.add(
            BackendSession(
                backend_id=backend_id,
                provider="claude",
                account_id=f"acct-{backend_id}",
                auth_mode="subscription",
                model_family="claude",
                priority=10,
                cost_tier="low",
                risk_tier="medium",
                overnight_allowed=True,
                automatic_switch_allowed=True,
                human_confirmation_required=False,
                enabled=True,
            )
        )
        session.commit()


def test_switch_policy_schedules_retry_when_no_eligible_backend_but_reset_is_known(
    tmp_path: Path,
) -> None:
    """Retry later when the current exhausted backend has a credible reset estimate."""
    service = _build_service(tmp_path)
    _seed_run_policy(service)
    _seed_backend(service, "claude-sub-01")
    reset_at = datetime(2026, 6, 21, 10, 0, tzinfo=timezone.utc)
    service.record_availability_state(
        backend_id="claude-sub-01",
        state="exhausted",
        estimated_reset_at=reset_at,
        estimation_source="heuristic",
        estimation_confidence="medium",
    )

    decision = service.plan_switch_decision(
        run_id="run-1", current_backend_id="claude-sub-01", switches_used=0
    )

    assert decision.outcome == "retry_scheduled"
    assert decision.selected_backend_id == "claude-sub-01"
    assert decision.retry_at == reset_at


def test_switch_policy_pauses_on_low_confidence_reset_when_policy_demands_it(
    tmp_path: Path,
) -> None:
    """Pause for the user when reset confidence is too low and policy says to pause."""
    service = _build_service(tmp_path)
    _seed_run_policy(service, pause_on_low_confidence_reset=True)
    _seed_backend(service, "claude-sub-01")
    reset_at = datetime(2026, 6, 21, 10, 0, tzinfo=timezone.utc)
    service.record_availability_state(
        backend_id="claude-sub-01",
        state="exhausted",
        estimated_reset_at=reset_at,
        estimation_source="heuristic",
        estimation_confidence="low",
    )

    decision = service.plan_switch_decision(
        run_id="run-1", current_backend_id="claude-sub-01", switches_used=0
    )

    assert decision.outcome == "pause_for_user"
    assert decision.selected_backend_id == "claude-sub-01"
    assert decision.retry_at is None


def test_switch_policy_allows_low_confidence_retry_when_policy_allows_it(
    tmp_path: Path,
) -> None:
    """Schedule retry even for low-confidence resets when policy opts into that behavior."""
    service = _build_service(tmp_path)
    _seed_run_policy(service, pause_on_low_confidence_reset=False)
    _seed_backend(service, "claude-sub-01")
    reset_at = datetime(2026, 6, 21, 10, 0, tzinfo=timezone.utc)
    service.record_availability_state(
        backend_id="claude-sub-01",
        state="exhausted",
        estimated_reset_at=reset_at,
        estimation_source="heuristic",
        estimation_confidence="low",
    )

    decision = service.plan_switch_decision(
        run_id="run-1", current_backend_id="claude-sub-01", switches_used=0
    )

    assert decision.outcome == "retry_scheduled"
    assert decision.selected_backend_id == "claude-sub-01"
    assert decision.retry_at == reset_at


def test_switch_policy_normalizes_retry_reset_to_utc(tmp_path: Path) -> None:
    """Retry decisions should normalize reset estimates into UTC."""
    service = _build_service(tmp_path)
    _seed_run_policy(service, pause_on_low_confidence_reset=False)
    _seed_backend(service, "claude-sub-01")
    reset_at = datetime(2026, 6, 21, 6, 0, tzinfo=timezone(timedelta(hours=-4)))
    service.record_availability_state(
        backend_id="claude-sub-01",
        state="exhausted",
        estimated_reset_at=reset_at,
        estimation_source="heuristic",
        estimation_confidence="medium",
    )

    decision = service.plan_switch_decision(
        run_id="run-1", current_backend_id="claude-sub-01", switches_used=0
    )

    assert decision.retry_at == datetime(2026, 6, 21, 10, 0, tzinfo=timezone.utc)
