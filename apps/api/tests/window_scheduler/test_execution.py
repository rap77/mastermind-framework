"""TDD coverage for WS-04 execution integration over scheduler decisions."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from mastermind_cli.window_scheduler import dispose_engines, initialize_database
from mastermind_cli.window_scheduler.database.session import get_session_factory
from mastermind_cli.window_scheduler.models.backend_session import BackendSession
from mastermind_cli.window_scheduler.models.run_policy import RunPolicy
from mastermind_cli.window_scheduler.service import WindowSchedulerService


def _build_service(tmp_path: Path) -> WindowSchedulerService:
    """Create a scheduler service backed by a temporary SQLite database."""
    database_url = f"sqlite:///{tmp_path / 'window_scheduler_execution.db'}"
    dispose_engines()
    initialize_database(database_url)
    return WindowSchedulerService(get_session_factory(database_url))


def _seed_run_policy(service: WindowSchedulerService) -> None:
    """Insert a base policy record for execution tests."""
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
                pause_on_low_confidence_reset=True,
            )
        )
        session.commit()


def _seed_backend(
    service: WindowSchedulerService, backend_id: str, priority: int
) -> None:
    """Insert a backend session for execution tests."""
    with service.session_factory() as session:
        session.add(
            BackendSession(
                backend_id=backend_id,
                provider="claude",
                account_id=f"acct-{backend_id}",
                auth_mode="subscription",
                model_family="claude",
                priority=priority,
                cost_tier="low",
                risk_tier="medium",
                overnight_allowed=True,
                automatic_switch_allowed=True,
                human_confirmation_required=False,
                enabled=True,
            )
        )
        session.commit()


def test_execute_switch_decision_creates_checkpoint_and_backend_switch_event(
    tmp_path: Path,
) -> None:
    """A switch execution should create a checkpoint first, then a switch event."""
    service = _build_service(tmp_path)
    _seed_run_policy(service)
    _seed_backend(service, "claude-sub-01", priority=10)
    _seed_backend(service, "codex-sub-01", priority=20)
    service.record_availability_state(
        backend_id="claude-sub-01",
        state="exhausted",
        estimated_reset_at=datetime(2026, 6, 21, 10, 0, tzinfo=timezone.utc),
        estimation_source="heuristic",
        estimation_confidence="medium",
    )
    service.record_availability_state(
        backend_id="codex-sub-01",
        state="active",
        estimated_reset_at=None,
        estimation_source=None,
        estimation_confidence=None,
    )

    decision = service.plan_switch_decision(
        run_id="run-1", current_backend_id="claude-sub-01", switches_used=0
    )
    event = service.execute_decision(
        event_id="evt-switch-1",
        checkpoint_id="chk-switch-1",
        run_id="run-1",
        project_id="project-1",
        current_backend_id="claude-sub-01",
        decision=decision,
        task_id="task-1",
        step_id="step-1",
        context_summary={"summary": "checkpoint before switching"},
        next_step_summary="Resume work on codex backend",
    )

    latest_checkpoint = service.get_latest_checkpoint("project-1")

    assert latest_checkpoint is not None
    assert latest_checkpoint.checkpoint_id == "chk-switch-1"
    assert event.type == "backend_switch"
    assert event.checkpoint_id == "chk-switch-1"
    assert event.to_backend == "codex-sub-01"


def test_execute_retry_decision_persists_retry_scheduled_event(tmp_path: Path) -> None:
    """A retry decision should persist a retry_scheduled event without checkpoint creation."""
    service = _build_service(tmp_path)
    _seed_run_policy(service)
    _seed_backend(service, "claude-sub-01", priority=10)
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
    event = service.execute_decision(
        event_id="evt-retry-1",
        checkpoint_id="chk-unused",
        run_id="run-1",
        project_id="project-1",
        current_backend_id="claude-sub-01",
        decision=decision,
        task_id="task-1",
        step_id="step-1",
        context_summary={"summary": "waiting for reset"},
        next_step_summary="Retry once reset window opens",
    )

    assert event.type == "retry_scheduled"
    assert event.estimated_reset_at == reset_at
    assert service.get_latest_checkpoint("project-1") is None


def test_execute_pause_decision_persists_pause_for_user_event(tmp_path: Path) -> None:
    """A pause decision should persist a pause event without checkpoint creation."""
    service = _build_service(tmp_path)
    _seed_run_policy(service)
    _seed_backend(service, "claude-sub-01", priority=10)
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
    event = service.execute_decision(
        event_id="evt-pause-1",
        checkpoint_id="chk-unused",
        run_id="run-1",
        project_id="project-1",
        current_backend_id="claude-sub-01",
        decision=decision,
        task_id="task-1",
        step_id="step-1",
        context_summary={"summary": "low confidence reset"},
        next_step_summary="Ask user whether to wait or switch providers",
    )

    assert event.type == "pause_for_user"
    assert event.to_backend == "claude-sub-01"
    assert service.get_latest_checkpoint("project-1") is None
