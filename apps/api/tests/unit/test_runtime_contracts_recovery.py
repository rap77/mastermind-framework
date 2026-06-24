"""Tests for the bounded recovery decision engine."""

from mastermind_cli.orchestrator.runtime_contracts import (
    RecoveryHarness,
    FailureRecord,
    LoopPolicy,
)


def test_recovery_harness_patches_verification_failures() -> None:
    """Verification failures should route to bounded patch first."""
    decision = RecoveryHarness().decide(
        FailureRecord(
            failure_class="verification_failed",
            reason="verification checks failed",
            attempt_count=0,
            retryable=True,
        ),
        LoopPolicy(
            base_loop="execute+verify-light",
            additional_loops=("verify-light",),
            max_iterations=2,
            time_budget_ms=15000,
            tool_budget=2,
            requires_review=True,
            requires_verification=True,
            recovery_policy_id="recovery-bounded",
        ),
    )

    assert decision.action == "patch"
    assert decision.escalate_to_human is False


def test_recovery_harness_stops_after_max_attempts() -> None:
    """No-progress should stop once attempts cross the bounded limit."""
    decision = RecoveryHarness().decide(
        FailureRecord(
            failure_class="execution_error",
            reason="runtime exception",
            attempt_count=3,
            retryable=True,
        ),
        LoopPolicy(
            base_loop="execute+verify-light",
            additional_loops=("verify-light",),
            max_iterations=2,
            time_budget_ms=15000,
            tool_budget=2,
            requires_review=True,
            requires_verification=True,
            recovery_policy_id="recovery-bounded",
        ),
    )

    assert decision.action == "stop"
    assert decision.escalate_to_human is True
