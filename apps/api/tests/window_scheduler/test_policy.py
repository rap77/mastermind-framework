"""TDD coverage for WS-02 eligibility and switch-policy behavior."""

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
    database_url = f"sqlite:///{tmp_path / 'window_scheduler_policy.db'}"
    dispose_engines()
    initialize_database(database_url)
    return WindowSchedulerService(get_session_factory(database_url))


def _seed_run_policy(
    service: WindowSchedulerService,
    *,
    run_id: str = "run-1",
    max_cost_tier: str = "medium",
    overnight_mode: bool = True,
    max_switches_per_run: int = 3,
    require_human_for_high_risk_actions: bool = False,
) -> None:
    """Insert a policy record for policy-evaluation tests."""
    with service.session_factory() as session:
        session.add(
            RunPolicy(
                run_id=run_id,
                project_id="project-1",
                execution_mode="hybrid",
                overnight_mode=overnight_mode,
                max_switches_per_run=max_switches_per_run,
                allow_paid_api_fallback=False,
                require_human_for_high_risk_actions=(
                    require_human_for_high_risk_actions
                ),
                max_cost_tier=max_cost_tier,
                pause_on_low_confidence_reset=True,
            )
        )
        session.commit()


def _seed_backend(
    service: WindowSchedulerService,
    *,
    backend_id: str,
    priority: int,
    cost_tier: str = "low",
    overnight_allowed: bool = True,
    automatic_switch_allowed: bool = True,
    human_confirmation_required: bool = False,
    enabled: bool = True,
) -> None:
    """Insert a backend session for eligibility/policy tests."""
    with service.session_factory() as session:
        session.add(
            BackendSession(
                backend_id=backend_id,
                provider="claude",
                account_id=f"acct-{backend_id}",
                auth_mode="subscription",
                model_family="claude",
                priority=priority,
                cost_tier=cost_tier,
                risk_tier="medium",
                overnight_allowed=overnight_allowed,
                automatic_switch_allowed=automatic_switch_allowed,
                human_confirmation_required=human_confirmation_required,
                enabled=enabled,
            )
        )
        session.commit()


def test_eligible_backends_filter_out_disabled_costly_and_exhausted_options(
    tmp_path: Path,
) -> None:
    """Return only backends that satisfy enabled/cost/availability constraints."""
    service = _build_service(tmp_path)
    _seed_run_policy(service, max_cost_tier="medium")
    _seed_backend(service, backend_id="eligible-low", priority=5, cost_tier="low")
    _seed_backend(service, backend_id="too-expensive", priority=10, cost_tier="high")
    _seed_backend(service, backend_id="disabled", priority=8, enabled=False)
    _seed_backend(service, backend_id="exhausted", priority=9, cost_tier="low")

    service.record_availability_state(
        backend_id="eligible-low",
        state="active",
        estimated_reset_at=None,
        estimation_source=None,
        estimation_confidence=None,
    )
    service.record_availability_state(
        backend_id="too-expensive",
        state="active",
        estimated_reset_at=None,
        estimation_source=None,
        estimation_confidence=None,
    )
    service.record_availability_state(
        backend_id="disabled",
        state="active",
        estimated_reset_at=None,
        estimation_source=None,
        estimation_confidence=None,
    )
    service.record_availability_state(
        backend_id="exhausted",
        state="exhausted",
        estimated_reset_at=datetime(2026, 6, 21, 10, 0, tzinfo=timezone.utc),
        estimation_source="heuristic",
        estimation_confidence="medium",
    )

    eligible = service.get_eligible_backends(run_id="run-1")

    assert [candidate.backend_id for candidate in eligible] == ["eligible-low"]


def test_switch_policy_prefers_continue_when_current_backend_is_still_eligible(
    tmp_path: Path,
) -> None:
    """Continue on the current backend when it is still policy-compliant and active."""
    service = _build_service(tmp_path)
    _seed_run_policy(service)
    _seed_backend(service, backend_id="claude-sub-01", priority=10)
    _seed_backend(service, backend_id="codex-sub-01", priority=5)
    service.record_availability_state(
        backend_id="claude-sub-01",
        state="active",
        estimated_reset_at=None,
        estimation_source=None,
        estimation_confidence=None,
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

    assert decision.outcome == "continue"
    assert decision.selected_backend_id == "claude-sub-01"


def test_switch_policy_moves_to_best_eligible_backend_when_current_is_exhausted(
    tmp_path: Path,
) -> None:
    """Switch to the highest-priority eligible backend when the current one is exhausted."""
    service = _build_service(tmp_path)
    _seed_run_policy(service)
    _seed_backend(service, backend_id="claude-sub-01", priority=10)
    _seed_backend(service, backend_id="codex-sub-01", priority=20)
    _seed_backend(service, backend_id="fallback-sub-01", priority=5)
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
    service.record_availability_state(
        backend_id="fallback-sub-01",
        state="active",
        estimated_reset_at=None,
        estimation_source=None,
        estimation_confidence=None,
    )

    decision = service.plan_switch_decision(
        run_id="run-1", current_backend_id="claude-sub-01", switches_used=0
    )

    assert decision.outcome == "switch"
    assert decision.selected_backend_id == "codex-sub-01"


def test_switch_policy_pauses_when_high_risk_requires_human_confirmation(
    tmp_path: Path,
) -> None:
    """Pause instead of switching automatically when policy requires human review."""
    service = _build_service(tmp_path)
    _seed_run_policy(service, require_human_for_high_risk_actions=True)
    _seed_backend(service, backend_id="claude-sub-01", priority=10)
    _seed_backend(service, backend_id="codex-sub-01", priority=20)
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
        run_id="run-1",
        current_backend_id="claude-sub-01",
        switches_used=0,
        task_risk_tier="high",
    )

    assert decision.outcome == "pause_for_user"
    assert decision.selected_backend_id == "codex-sub-01"


def test_switch_policy_blocks_when_switch_budget_is_exhausted(tmp_path: Path) -> None:
    """Pause when the run has already consumed its switch budget."""
    service = _build_service(tmp_path)
    _seed_run_policy(service, max_switches_per_run=1)
    _seed_backend(service, backend_id="claude-sub-01", priority=10)
    _seed_backend(service, backend_id="codex-sub-01", priority=20)
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
        run_id="run-1", current_backend_id="claude-sub-01", switches_used=1
    )

    assert decision.outcome == "pause_for_user"
    assert decision.selected_backend_id == "codex-sub-01"
