"""Adaptive Delivery recovery routing over the shared bounded primitives."""

from __future__ import annotations

from .models import FailureRecord, LoopPolicy, RecoveryDecision
from .recovery import RecoveryHarness


class DeliveryRecoveryService:
    """Apply delivery attempt and work budgets before shared recovery routing."""

    def __init__(self, recovery_harness: RecoveryHarness | None = None) -> None:
        """Initialize with the shared recovery harness."""
        self._recovery_harness = recovery_harness or RecoveryHarness()

    def decide(
        self,
        *,
        failure_class: str,
        reason: str,
        retryable: bool,
        active_attempt: int,
        loop_policy: LoopPolicy,
        budget_consumed: int,
        budget_remaining: int,
        recovery_cost: int,
    ) -> RecoveryDecision:
        """Return a bounded decision without consuming unavailable work budget."""
        if active_attempt < 1:
            raise ValueError("active_attempt must be at least 1")
        if budget_consumed < 0 or budget_remaining < 0:
            raise ValueError("delivery recovery budgets must not be negative")
        if recovery_cost < 1:
            raise ValueError("recovery_cost must be at least 1")
        if active_attempt >= loop_policy.max_iterations:
            return RecoveryDecision(
                action="stop",
                reason="max recovery attempts reached",
                updated_loop_policy=None,
                escalate_to_human=True,
            )
        if recovery_cost > budget_remaining:
            return RecoveryDecision(
                action="stop",
                reason="delivery recovery budget exhausted",
                updated_loop_policy=None,
                escalate_to_human=True,
            )
        return self._recovery_harness.decide(
            FailureRecord(
                failure_class=failure_class,
                reason=reason,
                attempt_count=active_attempt - 1,
                retryable=retryable,
            ),
            loop_policy,
        )
