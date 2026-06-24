"""Tests for the local maker-checker review harness."""

from mastermind_cli.orchestrator.runtime_contracts import (
    CapabilityRegistry,
    LoopSelector,
    ReviewHarness,
    ReviewRubricResolver,
    VerificationHarness,
    build_execution_envelope,
)
from mastermind_cli.types.interfaces import Brief


def test_review_harness_approves_verified_envelope() -> None:
    """Review should approve when verification passed and artifacts exist."""
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
    verification = VerificationHarness().verify(base_envelope, profile)
    rubric = ReviewRubricResolver().resolve(profile, policy)

    outcome = ReviewHarness().review(base_envelope, verification, rubric)

    assert outcome.performed is True
    assert outcome.approved is True
    assert outcome.recommended_next_action == "continue"


def test_review_harness_blocks_failed_verification() -> None:
    """Review should block approval if verification failed."""
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
    verification = VerificationHarness().verify(base_envelope, profile)
    rubric = ReviewRubricResolver().resolve(profile, policy)

    outcome = ReviewHarness().review(base_envelope, verification, rubric)

    assert outcome.approved is False
    assert outcome.recommended_next_action == "patch"
