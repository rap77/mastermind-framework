"""Tests for the deterministic verification harness."""

from mastermind_cli.orchestrator.runtime_contracts import (
    CapabilityRegistry,
    LoopSelector,
    VerificationHarness,
    build_execution_envelope,
)
from mastermind_cli.types.interfaces import Brief


def test_verification_harness_passes_for_valid_envelope() -> None:
    """Verification should pass when artifacts and envelope shape are valid."""
    selector = LoopSelector()
    profile = selector.classify_task(
        Brief(problem_statement="Build a CRM for small businesses"),
        ["brain-01-product-strategy"],
    )
    policy = selector.select_loop(
        profile, CapabilityRegistry().resolve_for_task(profile)
    )
    base_envelope = build_execution_envelope(
        task_profile=profile,
        loop_policy=policy,
        artifacts=("brain-01-product-strategy",),
        next_actions=("continue",),
    )

    outcome = VerificationHarness().verify(base_envelope, profile)

    assert outcome.performed is True
    assert outcome.passed is True
    assert outcome.acceptance_criteria_satisfied is True


def test_verification_harness_fails_when_artifacts_missing() -> None:
    """Verification should fail when a task produced no artifacts."""
    selector = LoopSelector()
    profile = selector.classify_task(
        Brief(problem_statement="Build a CRM for small businesses"),
        ["brain-01-product-strategy"],
    )
    policy = selector.select_loop(
        profile, CapabilityRegistry().resolve_for_task(profile)
    )
    base_envelope = build_execution_envelope(
        task_profile=profile,
        loop_policy=policy,
        artifacts=(),
        next_actions=("continue",),
    )

    outcome = VerificationHarness().verify(base_envelope, profile)

    assert outcome.passed is False
    assert any(
        check.label == "artifacts_present" and not check.passed
        for check in outcome.checks
    )
