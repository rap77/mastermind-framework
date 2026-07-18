"""Tests for external capability idempotency and unknown-outcome recovery."""

from __future__ import annotations

from mastermind_cli.orchestrator.runtime_contracts.capability_invoker import (
    CapabilitySideEffectInvoker,
    ExternalOutcomeUnknown,
)
from mastermind_cli.orchestrator.runtime_contracts.run_bundle_stage_executor import (
    CapabilityExecutionResult,
)


def test_replayed_capability_key_suppresses_duplicate_side_effect() -> None:
    """A confirmed capability result is returned without invoking the effect twice."""
    calls: list[str] = []
    invoker = CapabilitySideEffectInvoker()

    def perform(idempotency_key: str) -> CapabilityExecutionResult:
        calls.append(idempotency_key)
        return CapabilityExecutionResult(
            artifact_refs=("artifact-001",),
            evidence=(),
            finding_refs=(),
        )

    first = invoker.invoke("stage-transition:key-001", perform)
    replay = invoker.invoke("stage-transition:key-001", perform)

    assert first.status == "passed"
    assert first.replayed is False
    assert replay == first.__class__(
        status="passed",
        execution_result=first.execution_result,
        replayed=True,
        recovery_reason=None,
    )
    assert calls == ["stage-transition:key-001"]


def test_unknown_external_outcome_routes_to_recovery_without_blind_retry() -> None:
    """An ambiguous external response remains unknown and is never retried blindly."""
    calls: list[str] = []
    invoker = CapabilitySideEffectInvoker()

    def perform(idempotency_key: str) -> CapabilityExecutionResult:
        calls.append(idempotency_key)
        raise ExternalOutcomeUnknown("provider timed out after accepting request")

    first = invoker.invoke("stage-transition:key-unknown", perform)
    replay = invoker.invoke("stage-transition:key-unknown", perform)

    assert first.status == "needs_recovery"
    assert first.execution_result is None
    assert first.recovery_reason == "provider timed out after accepting request"
    assert first.replayed is False
    assert replay.status == "needs_recovery"
    assert replay.replayed is True
    assert calls == ["stage-transition:key-unknown"]
