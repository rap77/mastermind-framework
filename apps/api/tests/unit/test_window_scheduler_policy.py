"""Unit tests for context-safe scheduler switch decisions."""

import pytest

from mastermind_cli.window_scheduler.context_fit import ContextFitAssessment, FitState
from mastermind_cli.window_scheduler.context_packager import (
    ContextPackResult,
    ContextPackStatus,
)
from mastermind_cli.window_scheduler.models.run_policy import RunPolicy
from mastermind_cli.window_scheduler.policy import EligibleBackend, plan_switch_decision


def _policy(*, require_human_for_high_risk_actions: bool = False) -> RunPolicy:
    """Build the minimum run policy needed for pure switch-policy tests."""
    return RunPolicy(
        run_id="run-1",
        project_id="project-1",
        execution_mode="hybrid",
        overnight_mode=True,
        max_switches_per_run=3,
        allow_paid_api_fallback=False,
        require_human_for_high_risk_actions=require_human_for_high_risk_actions,
        max_cost_tier="medium",
        pause_on_low_confidence_reset=True,
    )


def _candidate() -> EligibleBackend:
    """Build an otherwise automatic eligible switch candidate."""
    return EligibleBackend(
        backend_id="codex-sub-01",
        priority=20,
        eligibility_basis="enabled + active + within cost/overnight policy constraints",
        automatic_switch_allowed=True,
        human_confirmation_required=False,
    )


def _assessment(
    fit_state: FitState, strategy: str = "keep_full_context"
) -> ContextFitAssessment:
    """Build a candidate context-fit assessment."""
    return ContextFitAssessment(
        backend_id="codex-sub-01",
        fit_state=fit_state,
        compression_required=fit_state == "fits_with_compression",
        risk_level="medium" if fit_state == "fits_with_compression" else "low",
        recommended_strategy=strategy,
    )


def _pack(*, status: ContextPackStatus = "packed") -> ContextPackResult:
    """Build a candidate context-pack result."""
    return ContextPackResult(
        status=status,
        input_token_capacity=100,
        output_token_reservation=10,
        selected_references=("objective", "checkpoint:chk-1"),
        omitted_references=("history",),
        omitted_optional_references=("history",),
        critical_references=("objective", "checkpoint:chk-1"),
        compression_required=True,
        compression_reason="history omitted",
    )


def test_clean_context_fit_permits_existing_automatic_switch() -> None:
    """A clean candidate preserves the established automatic switch outcome."""
    decision = plan_switch_decision(
        current_backend_id="claude-sub-01",
        eligible_backends=[_candidate()],
        policy=_policy(),
        switches_used=0,
        task_risk_tier=None,
        context_fit_assessment=_assessment("fits_cleanly"),
        context_pack_result=_pack(),
        checkpoint_reference="checkpoint:chk-1",
    )

    assert decision.outcome == "switch"
    assert decision.selected_backend_id == "codex-sub-01"


def test_compression_fit_requires_strategy_and_checkpoint_in_switch_rationale() -> None:
    """Compression switches are automatic only with explicit resumability inputs."""
    decision = plan_switch_decision(
        current_backend_id="claude-sub-01",
        eligible_backends=[_candidate()],
        policy=_policy(),
        switches_used=0,
        task_risk_tier=None,
        context_fit_assessment=_assessment(
            "fits_with_compression", "summarize_history_keep_decisions"
        ),
        context_pack_result=_pack(),
        checkpoint_reference="checkpoint:chk-1",
    )

    assert decision.outcome == "switch"
    assert "summarize_history_keep_decisions" in decision.reason
    assert "checkpoint:chk-1" in decision.reason


def test_blocked_context_pack_pauses_instead_of_authorizing_switch() -> None:
    """A blocked pack cannot pass through the automatic switch policy."""
    decision = plan_switch_decision(
        current_backend_id="claude-sub-01",
        eligible_backends=[_candidate()],
        policy=_policy(),
        switches_used=0,
        task_risk_tier=None,
        context_fit_assessment=_assessment("fits_cleanly"),
        context_pack_result=_pack(status="blocked"),
        checkpoint_reference="checkpoint:chk-1",
    )

    assert decision.outcome == "pause_for_user"
    assert "context pack is blocked" in decision.reason


@pytest.mark.parametrize("fit_state", ["unsafe_fit", "does_not_fit"])
def test_unsafe_context_fits_pause_instead_of_authorizing_switch(
    fit_state: FitState,
) -> None:
    """Unsafe candidate fits require an established user-approval pause."""
    decision = plan_switch_decision(
        current_backend_id="claude-sub-01",
        eligible_backends=[_candidate()],
        policy=_policy(),
        switches_used=0,
        task_risk_tier=None,
        context_fit_assessment=_assessment(fit_state),
        context_pack_result=_pack(),
        checkpoint_reference="checkpoint:chk-1",
    )

    assert decision.outcome == "pause_for_user"
    assert decision.reason == f"context fit is {fit_state}"


def test_compression_fit_without_checkpoint_reference_pauses() -> None:
    """Compression cannot switch automatically without an explicit resume reference."""
    decision = plan_switch_decision(
        current_backend_id="claude-sub-01",
        eligible_backends=[_candidate()],
        policy=_policy(),
        switches_used=0,
        task_risk_tier=None,
        context_fit_assessment=_assessment(
            "fits_with_compression", "summarize_history_keep_decisions"
        ),
        context_pack_result=_pack(),
        checkpoint_reference="",
    )

    assert decision.outcome == "pause_for_user"
    assert (
        "compression switch requires strategy and checkpoint reference"
        in decision.reason
    )


def test_context_gate_does_not_override_existing_high_risk_pause() -> None:
    """Existing risk policy still owns a high-risk switch decision."""
    decision = plan_switch_decision(
        current_backend_id="claude-sub-01",
        eligible_backends=[_candidate()],
        policy=_policy(require_human_for_high_risk_actions=True),
        switches_used=0,
        task_risk_tier="high",
        context_fit_assessment=_assessment("fits_cleanly"),
        context_pack_result=_pack(),
        checkpoint_reference="checkpoint:chk-1",
    )

    assert decision.outcome == "pause_for_user"
    assert decision.reason == "high-risk action requires human confirmation"
