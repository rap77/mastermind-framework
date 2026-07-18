"""Integration coverage for context-safe scheduler switches and resume state."""

from pathlib import Path

import pytest

from mastermind_cli.window_scheduler import dispose_engines, initialize_database
from mastermind_cli.window_scheduler.context_fit import (
    ContextCapabilityProfile,
    ContextBudgetEstimate,
    ContextFitAssessment,
    assess_context_fit_for_budget,
)
from mastermind_cli.window_scheduler.context_packager import (
    ContextPackResult,
    ContextSegment,
    pack_context,
)
from mastermind_cli.window_scheduler.database.session import get_session_factory
from mastermind_cli.window_scheduler.models.backend_session import BackendSession
from mastermind_cli.window_scheduler.models.run_policy import RunPolicy
from mastermind_cli.window_scheduler.service import WindowSchedulerService


@pytest.fixture(scope="session", autouse=True)
def _database_url_for_integration() -> None:
    """Keep this SQLite-backed persistence test independent of the Postgres gate."""


def _service(tmp_path: Path) -> WindowSchedulerService:
    """Build a scheduler service backed by a temporary SQLite database."""
    database_url = f"sqlite:///{tmp_path / 'context_safe_switch.db'}"
    dispose_engines()
    initialize_database(database_url)
    service = WindowSchedulerService(get_session_factory(database_url))
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
        session.add_all(
            [
                BackendSession(
                    backend_id="claude-sub-01",
                    provider="claude",
                    account_id="acct-claude",
                    auth_mode="subscription",
                    model_family="claude",
                    priority=10,
                    cost_tier="low",
                    risk_tier="medium",
                    overnight_allowed=True,
                    automatic_switch_allowed=True,
                    human_confirmation_required=False,
                    enabled=True,
                ),
                BackendSession(
                    backend_id="codex-sub-01",
                    provider="openai",
                    account_id="acct-codex",
                    auth_mode="subscription",
                    model_family="codex",
                    priority=20,
                    cost_tier="low",
                    risk_tier="medium",
                    overnight_allowed=True,
                    automatic_switch_allowed=True,
                    human_confirmation_required=False,
                    enabled=True,
                ),
            ]
        )
        session.commit()
    service.record_availability_state(
        backend_id="claude-sub-01",
        state="exhausted",
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
    return service


def _profile(*, long_context_quality: str = "high") -> ContextCapabilityProfile:
    """Build the candidate backend profile used by the integration scenarios."""
    return ContextCapabilityProfile(
        backend_id="codex-sub-01",
        max_context_window=100,
        recommended_working_window=60,
        max_output_window=20,
        long_context_quality=long_context_quality,
        compression_preference="summarize_history_keep_decisions",
    )


def _pack(*, token_budget: int = 80) -> ContextPackResult:
    """Build a realistic reference-only payload for a switch candidate."""
    return pack_context(
        [
            ContextSegment("objective:task-1", 20, "core_required"),
            ContextSegment("checkpoint:prior-1", 15, "core_required"),
            ContextSegment("decision:approved-1", 15, "decision_critical"),
            ContextSegment("history:old", 30, "optional_history"),
        ],
        token_budget=token_budget,
        output_token_reservation=10,
    )


def test_clean_fit_switches_and_persists_resume_references(tmp_path: Path) -> None:
    """A clean candidate switch persists its structured resume payload."""
    service = _service(tmp_path)
    assessment = assess_context_fit_for_budget(
        _profile(),
        budget=ContextBudgetEstimate(20, 15, 0, 0, 10),
    )

    decision = service.plan_switch_decision(
        run_id="run-1",
        current_backend_id="claude-sub-01",
        switches_used=0,
        context_fit_assessment=assessment,
        context_pack_result=_pack(),
        checkpoint_reference="checkpoint:prior-1",
    )
    event = service.execute_decision(
        event_id="evt-clean-1",
        checkpoint_id="chk-clean-1",
        run_id="run-1",
        project_id="project-1",
        current_backend_id="claude-sub-01",
        decision=decision,
        task_id="task-1",
        step_id="step-1",
        context_summary={"objective": "Complete the context-safe switch"},
        next_step_summary="Resume on codex with the selected references",
    )

    checkpoint = service.get_latest_checkpoint("project-1")

    assert decision.outcome == "switch"
    assert assessment.fit_state == "fits_cleanly"
    assert event.to_backend == "codex-sub-01"
    assert checkpoint is not None
    assert checkpoint.task_id == "task-1"
    assert checkpoint.step_id == "step-1"
    assert checkpoint.context_summary["objective"] == "Complete the context-safe switch"
    assert checkpoint.context_summary["context_references"] == [
        "checkpoint:prior-1",
        "objective:task-1",
        "decision:approved-1",
    ]
    assert checkpoint.context_summary["checkpoint_reference"] == "checkpoint:prior-1"
    assert checkpoint.context_summary["context_fit_state"] == "fits_cleanly"
    assert checkpoint.context_summary["switch_rationale"] == decision.reason


def test_compression_switch_persists_complete_context_safe_resume_state(
    tmp_path: Path,
) -> None:
    """A compressed switch retains all structured continuity metadata in SQLite."""
    service = _service(tmp_path)
    assessment = assess_context_fit_for_budget(
        _profile(),
        budget=ContextBudgetEstimate(35, 25, 10, 0, 10),
    )
    pack = _pack()

    decision = service.plan_switch_decision(
        run_id="run-1",
        current_backend_id="claude-sub-01",
        switches_used=0,
        context_fit_assessment=assessment,
        context_pack_result=pack,
        checkpoint_reference="checkpoint:prior-1",
    )
    service.execute_decision(
        event_id="evt-compressed-1",
        checkpoint_id="chk-compressed-1",
        run_id="run-1",
        project_id="project-1",
        current_backend_id="claude-sub-01",
        decision=decision,
        task_id="task-1",
        step_id="step-1",
        context_summary={"objective": "Complete the context-safe switch"},
        next_step_summary="Resume after compressing optional history",
    )

    checkpoint = service.get_latest_checkpoint("project-1")

    assert assessment.fit_state == "fits_with_compression"
    assert pack.compression_required is True
    assert decision.outcome == "switch"
    assert checkpoint is not None
    assert checkpoint.task_id == "task-1"
    assert checkpoint.step_id == "step-1"
    assert checkpoint.context_summary["objective"] == "Complete the context-safe switch"
    assert checkpoint.context_summary["context_references"] == [
        "checkpoint:prior-1",
        "objective:task-1",
        "decision:approved-1",
    ]
    assert checkpoint.context_summary["checkpoint_reference"] == "checkpoint:prior-1"
    assert checkpoint.context_summary["compression_strategy"] == (
        "summarize_history_keep_decisions"
    )
    assert checkpoint.context_summary["context_fit_state"] == "fits_with_compression"
    assert checkpoint.context_summary["switch_rationale"] == decision.reason


@pytest.mark.parametrize(
    ("assessment", "pack", "reason"),
    [
        (
            assess_context_fit_for_budget(
                _profile(long_context_quality="medium"),
                budget=ContextBudgetEstimate(35, 25, 10, 0, 10),
            ),
            _pack(),
            "context fit is unsafe_fit",
        ),
        (
            assess_context_fit_for_budget(
                _profile(),
                budget=ContextBudgetEstimate(20, 15, 0, 0, 10),
            ),
            _pack(token_budget=40),
            "context pack is blocked",
        ),
    ],
)
def test_unsafe_or_blocked_switch_does_not_persist_a_resume_checkpoint(
    tmp_path: Path,
    assessment: ContextFitAssessment,
    pack: ContextPackResult,
    reason: str,
) -> None:
    """Unsafe candidate context pauses without creating resumable switch state."""
    service = _service(tmp_path)

    decision = service.plan_switch_decision(
        run_id="run-1",
        current_backend_id="claude-sub-01",
        switches_used=0,
        context_fit_assessment=assessment,
        context_pack_result=pack,
        checkpoint_reference="checkpoint:prior-1",
    )
    event = service.execute_decision(
        event_id="evt-blocked-1",
        checkpoint_id="chk-blocked-1",
        run_id="run-1",
        project_id="project-1",
        current_backend_id="claude-sub-01",
        decision=decision,
        task_id="task-1",
        step_id="step-1",
        context_summary={"objective": "Complete the context-safe switch"},
        next_step_summary="Pause for operator review",
    )

    assert decision.outcome == "pause_for_user"
    assert decision.reason == reason
    assert event.type == "pause_for_user"
    assert service.get_latest_checkpoint("project-1") is None
