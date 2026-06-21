"""TDD coverage for the initial window-scheduler service slice."""

from __future__ import annotations

from pathlib import Path

import pytest

from mastermind_cli.window_scheduler import dispose_engines, initialize_database
from mastermind_cli.window_scheduler.database.session import get_session_factory
from mastermind_cli.window_scheduler.models.backend_session import BackendSession
from mastermind_cli.window_scheduler.models.run_policy import RunPolicy
from mastermind_cli.window_scheduler.service import WindowSchedulerService


def _build_service(tmp_path: Path) -> WindowSchedulerService:
    """Create a scheduler service backed by a temporary SQLite database."""
    database_url = f"sqlite:///{tmp_path / 'window_scheduler.db'}"
    dispose_engines()
    initialize_database(database_url)
    return WindowSchedulerService(get_session_factory(database_url))


def _seed_run_policy(service: WindowSchedulerService) -> None:
    """Insert the minimum explicit run policy required by the scheduler."""
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


def _seed_backend(service: WindowSchedulerService, backend_id: str) -> None:
    """Insert a backend session record for switch tests."""
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


def test_backend_switch_requires_checkpoint_id(tmp_path: Path) -> None:
    """Reject backend switch events that do not reference a checkpoint."""
    service = _build_service(tmp_path)
    _seed_run_policy(service)

    with pytest.raises(ValueError, match="checkpoint_id"):
        service.record_backend_switch(
            event_id="evt-1",
            run_id="run-1",
            project_id="project-1",
            from_backend="claude-sub-01",
            to_backend="codex-sub-01",
            reason="window_exhausted",
            checkpoint_id=None,
            decision_outcome="switch",
        )


def test_checkpoint_requires_next_step_summary(tmp_path: Path) -> None:
    """Reject checkpoints that do not carry a resumable next step."""
    service = _build_service(tmp_path)

    with pytest.raises(ValueError, match="next_step_summary"):
        service.record_checkpoint(
            checkpoint_id="chk-1",
            run_id="run-1",
            project_id="project-1",
            task_id="task-1",
            step_id="step-1",
            context_summary={"summary": "work in progress"},
            next_step_summary="",
        )


def test_reset_estimate_requires_source_and_confidence(tmp_path: Path) -> None:
    """Reject availability updates that omit reset estimate provenance."""
    service = _build_service(tmp_path)
    _seed_backend(service, "claude-sub-01")

    with pytest.raises(ValueError, match="estimation_source"):
        service.record_availability_state(
            backend_id="claude-sub-01",
            state="exhausted",
            estimated_reset_at="2026-06-21T10:00:00Z",
            estimation_source=None,
            estimation_confidence=None,
        )


def test_valid_checkpoint_then_switch_persists_records(tmp_path: Path) -> None:
    """Persist a valid checkpoint and the backend switch that references it."""
    service = _build_service(tmp_path)
    _seed_run_policy(service)

    checkpoint = service.record_checkpoint(
        checkpoint_id="chk-1",
        run_id="run-1",
        project_id="project-1",
        task_id="task-1",
        step_id="step-1",
        context_summary={"summary": "checkpoint ready"},
        next_step_summary="Resume on fallback backend",
    )

    event = service.record_backend_switch(
        event_id="evt-1",
        run_id="run-1",
        project_id="project-1",
        from_backend="claude-sub-01",
        to_backend="codex-sub-01",
        reason="window_exhausted",
        checkpoint_id=checkpoint.checkpoint_id,
        decision_outcome="switched",
    )

    latest_checkpoint = service.get_latest_checkpoint("project-1")

    assert checkpoint.checkpoint_id == "chk-1"
    assert event.checkpoint_id == "chk-1"
    assert event.type == "backend_switch"
    assert latest_checkpoint is not None
    assert latest_checkpoint.checkpoint_id == "chk-1"


def test_backend_switch_requires_explicit_run_policy(tmp_path: Path) -> None:
    """Reject backend switch attempts for runs without an explicit policy."""
    service = _build_service(tmp_path)

    with pytest.raises(ValueError, match="run_policy"):
        service.record_backend_switch(
            event_id="evt-1",
            run_id="run-missing",
            project_id="project-1",
            from_backend="claude-sub-01",
            to_backend="codex-sub-01",
            reason="window_exhausted",
            checkpoint_id="chk-1",
            decision_outcome="switched",
        )
