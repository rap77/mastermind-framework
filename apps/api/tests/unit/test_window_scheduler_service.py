"""Unit tests for context-safe scheduler checkpoint persistence."""

from pathlib import Path

from mastermind_cli.window_scheduler import dispose_engines, initialize_database
from mastermind_cli.window_scheduler.context_fit import ContextFitAssessment
from mastermind_cli.window_scheduler.context_packager import ContextPackResult
from mastermind_cli.window_scheduler.database.session import get_session_factory
from mastermind_cli.window_scheduler.models.backend_session import BackendSession
from mastermind_cli.window_scheduler.models.run_policy import RunPolicy
from mastermind_cli.window_scheduler.service import WindowSchedulerService


def _service(tmp_path: Path) -> WindowSchedulerService:
    """Build a scheduler service backed by temporary SQLite storage."""
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


def test_execute_context_safe_switch_preserves_references_and_rationale(
    tmp_path: Path,
) -> None:
    """A context-safe switch writes structured resume metadata into its checkpoint."""
    service = _service(tmp_path)
    assessment = ContextFitAssessment(
        backend_id="codex-sub-01",
        fit_state="fits_with_compression",
        compression_required=True,
        risk_level="medium",
        recommended_strategy="summarize_history_keep_decisions",
    )
    pack = ContextPackResult(
        status="packed",
        input_token_capacity=100,
        output_token_reservation=10,
        selected_references=("objective:task-1", "checkpoint:prior-1"),
        omitted_references=("history:old",),
        omitted_optional_references=("history:old",),
        critical_references=("objective:task-1", "checkpoint:prior-1"),
        compression_required=True,
        compression_reason="history omitted",
    )

    decision = service.plan_switch_decision(
        run_id="run-1",
        current_backend_id="claude-sub-01",
        switches_used=0,
        context_fit_assessment=assessment,
        context_pack_result=pack,
        checkpoint_reference="checkpoint:prior-1",
    )
    service.execute_decision(
        event_id="evt-1",
        checkpoint_id="chk-1",
        run_id="run-1",
        project_id="project-1",
        current_backend_id="claude-sub-01",
        decision=decision,
        task_id="task-1",
        step_id="step-1",
        context_summary={"summary": "resume safely"},
        next_step_summary="Resume on codex",
    )

    checkpoint = service.get_latest_checkpoint("project-1")

    assert checkpoint is not None
    assert checkpoint.context_summary["context_references"] == [
        "objective:task-1",
        "checkpoint:prior-1",
    ]
    assert checkpoint.context_summary["checkpoint_reference"] == "checkpoint:prior-1"
    assert checkpoint.context_summary["compression_strategy"] == (
        "summarize_history_keep_decisions"
    )
    assert (
        "summarize_history_keep_decisions"
        in checkpoint.context_summary["switch_rationale"]
    )
