"""Idempotent boundary for capabilities with external side effects."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from threading import Lock
from typing import Literal

from .run_bundle_stage_executor import CapabilityExecutionResult

CapabilitySideEffectStatus = Literal["passed", "needs_recovery"]
CapabilitySideEffect = Callable[[str], CapabilityExecutionResult]


class ExternalOutcomeUnknown(RuntimeError):
    """Signal that an external system may have accepted a side effect."""


@dataclass(frozen=True, slots=True)
class CapabilitySideEffectResult:
    """Confirmed result or explicit recovery state for one idempotency key."""

    status: CapabilitySideEffectStatus
    execution_result: CapabilityExecutionResult | None
    replayed: bool
    recovery_reason: str | None


class CapabilitySideEffectInvoker:
    """Suppress duplicate effects and preserve ambiguous outcomes for recovery."""

    def __init__(self) -> None:
        """Initialize an empty invocation result cache."""
        self._results: dict[str, CapabilitySideEffectResult] = {}
        self._lock = Lock()

    def invoke(
        self,
        idempotency_key: str,
        side_effect: CapabilitySideEffect,
    ) -> CapabilitySideEffectResult:
        """Invoke once per key; unknown outcomes become non-retryable recovery state."""
        if not idempotency_key.strip():
            raise ValueError("idempotency_key must not be empty")

        with self._lock:
            persisted = self._results.get(idempotency_key)
            if persisted is not None:
                return replace(persisted, replayed=True)

            try:
                execution_result = side_effect(idempotency_key)
            except ExternalOutcomeUnknown as error:
                result = CapabilitySideEffectResult(
                    status="needs_recovery",
                    execution_result=None,
                    replayed=False,
                    recovery_reason=str(error),
                )
            else:
                result = CapabilitySideEffectResult(
                    status="passed",
                    execution_result=execution_result,
                    replayed=False,
                    recovery_reason=None,
                )
            self._results[idempotency_key] = result
            return result
