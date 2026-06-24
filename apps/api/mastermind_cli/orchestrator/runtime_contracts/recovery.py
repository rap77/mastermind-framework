"""Bounded recovery decision engine for runtime contracts."""

from __future__ import annotations

from mastermind_cli.orchestrator.runtime_contracts.models import (
    ExecutionEnvelope,
    FailureRecord,
    LoopPolicy,
    RecoveryAction,
    RecoveryDecision,
    ReviewOutcome,
    VerificationOutcome,
)


class FailureClassifier:
    """Normalize failures from execution, verification, and review."""

    def classify(
        self,
        base_envelope: ExecutionEnvelope,
        verification_outcome: VerificationOutcome | None,
        review_outcome: ReviewOutcome | None,
        previous_recovery_state: FailureRecord | None = None,
    ) -> FailureRecord | None:
        """Return a normalized failure snapshot when recovery is needed."""
        if base_envelope.status == "error":
            return FailureRecord(
                failure_class="execution_error",
                reason=base_envelope.summary,
                attempt_count=previous_recovery_state.attempt_count + 1
                if previous_recovery_state
                else 0,
                retryable=True,
                previous_action=previous_recovery_state.previous_action
                if previous_recovery_state
                else None,
            )
        if verification_outcome is not None and not verification_outcome.passed:
            return FailureRecord(
                failure_class="verification_failed",
                reason="verification checks failed",
                attempt_count=previous_recovery_state.attempt_count + 1
                if previous_recovery_state
                else 0,
                retryable=True,
                previous_action=previous_recovery_state.previous_action
                if previous_recovery_state
                else None,
            )
        if review_outcome is not None and not review_outcome.approved:
            return FailureRecord(
                failure_class="review_failed",
                reason="review rubric blocked approval",
                attempt_count=previous_recovery_state.attempt_count + 1
                if previous_recovery_state
                else 0,
                retryable=False,
                previous_action=previous_recovery_state.previous_action
                if previous_recovery_state
                else None,
            )
        return None


class RecoveryHarness:
    """Choose the next bounded action after a normalized failure."""

    def decide(
        self, failure_record: FailureRecord, loop_policy: LoopPolicy
    ) -> RecoveryDecision:
        """Return the bounded recovery decision."""
        if failure_record.attempt_count >= loop_policy.max_iterations:
            return RecoveryDecision(
                action="stop",
                reason="max recovery attempts reached",
                updated_loop_policy=None,
                escalate_to_human=True,
            )
        if not failure_record.retryable:
            return RecoveryDecision(
                action="escalate",
                reason=failure_record.reason,
                updated_loop_policy=None,
                escalate_to_human=True,
            )
        if failure_record.failure_class == "execution_error":
            action: RecoveryAction = (
                "retry" if failure_record.attempt_count == 0 else "replan"
            )
        elif failure_record.failure_class == "verification_failed":
            action = "patch"
        else:
            action = "replan"
        return RecoveryDecision(
            action=action,
            reason=failure_record.reason,
            updated_loop_policy=None,
            escalate_to_human=action in {"escalate", "stop"},
        )
