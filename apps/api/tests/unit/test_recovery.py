"""Tests for bounded runtime recovery routing."""

import pytest

from mastermind_cli.orchestrator.runtime_contracts import (
    FailureRecord,
    LoopPolicy,
    RecoveryHarness,
)


@pytest.fixture
def loop_policy() -> LoopPolicy:
    """Return a recovery policy with finite attempt, time, and tool budgets."""
    return LoopPolicy(
        base_loop="execute+verify",
        additional_loops=("recovery",),
        max_iterations=2,
        time_budget_ms=1_000,
        tool_budget=3,
        requires_review=True,
        requires_verification=True,
        recovery_policy_id="bounded-recovery",
    )


def test_recovery_routes_retry_then_replan_within_budgets(
    loop_policy: LoopPolicy,
) -> None:
    """A transient execution failure should retry once, then replan."""
    harness = RecoveryHarness()

    retry = harness.decide(
        FailureRecord("execution_error", "timeout", 0, True),
        loop_policy,
        time_consumed_ms=100,
        tools_consumed=1,
    )
    replan = harness.decide(
        FailureRecord("execution_error", "timeout", 1, True),
        loop_policy,
        time_consumed_ms=200,
        tools_consumed=2,
    )

    assert retry.action == "retry"
    assert replan.action == "replan"
    assert retry.escalate_to_human is False
    assert replan.escalate_to_human is False


@pytest.mark.parametrize(
    ("attempt_count", "time_consumed_ms", "tools_consumed", "reason"),
    [
        (2, 100, 1, "max recovery attempts reached"),
        (0, 1_000, 1, "recovery time budget exhausted"),
        (0, 100, 3, "recovery tool budget exhausted"),
    ],
)
def test_recovery_stops_and_escalates_when_any_bound_is_exhausted(
    loop_policy: LoopPolicy,
    attempt_count: int,
    time_consumed_ms: int,
    tools_consumed: int,
    reason: str,
) -> None:
    """Recovery must stop safely at every declared budget boundary."""
    decision = RecoveryHarness().decide(
        FailureRecord("execution_error", "timeout", attempt_count, True),
        loop_policy,
        time_consumed_ms=time_consumed_ms,
        tools_consumed=tools_consumed,
    )

    assert decision.action == "stop"
    assert decision.escalate_to_human is True
    assert decision.reason == reason
