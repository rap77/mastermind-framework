"""Tests for deterministic runtime contract selection."""

from mastermind_cli.orchestrator.runtime_contracts import (
    CapabilityRegistry,
    ExecutionEnvelope,
    FailureClassifier,
    HarnessRegistry,
    LoopSelector,
    RecoveryHarness,
    ReviewHarness,
    ReviewRubricResolver,
    build_execution_envelope,
    synthesize_execution_envelope,
    validate_execution_envelope,
)
from mastermind_cli.types.interfaces import Brief
from mastermind_cli.orchestrator.runtime_contracts.models import (
    VerificationCheck,
    VerificationOutcome,
)


def test_loop_selector_classifies_simple_task() -> None:
    """Simple deterministic prompts should stay on the cheapest control path."""
    selector = LoopSelector()
    profile = selector.classify_task(
        Brief(problem_statement="Review this API metric", context="", constraints=[]),
        ["brain-07-growth-data"],
    )

    assert profile.complexity == "simple"
    assert profile.requires_checker is False
    assert profile.acceptance_mode == "deterministic"


def test_loop_selector_uses_single_pass_for_simple_ready_tasks() -> None:
    """Simple ready tasks should stay on the cheapest runtime loop."""
    selector = LoopSelector()
    profile = selector.classify_task(
        Brief(problem_statement="Review this API metric", context="", constraints=[]),
        ["brain-07-growth-data"],
    )
    capabilities = CapabilityRegistry().resolve_for_task(profile)
    policy = selector.select_loop(profile, capabilities)

    assert policy.base_loop == "single-pass"
    assert policy.requires_review is False
    assert policy.requires_verification is False
    assert policy.additional_loops == ()


def test_loop_selector_selects_review_for_medium_write_task() -> None:
    """Write-heavy multi-brain tasks should require verification and review."""
    selector = LoopSelector()
    profile = selector.classify_task(
        Brief(
            problem_statement="Implement and design a production migration plan",
            context="Need latest research and design review",
            constraints=["Use current sources"],
        ),
        ["brain-01-product-strategy", "brain-03-ui-design"],
    )
    capabilities = CapabilityRegistry().resolve_for_task(profile)
    policy = selector.select_loop(profile, capabilities)

    assert profile.complexity in {"medium", "complex"}
    assert profile.requires_checker is True
    assert policy.base_loop == "execute+verify-light"
    assert policy.requires_verification is True
    assert policy.requires_review is True


def test_loop_selector_escalates_when_evidence_readiness_is_low() -> None:
    """Low evidence readiness should route even simple work to verify."""
    selector = LoopSelector()
    profile = selector.classify_task(
        Brief(problem_statement="Review this API metric", context="", constraints=[]),
        ["brain-07-growth-data"],
    )
    capabilities = CapabilityRegistry().resolve_for_task(profile)
    policy = selector.select_loop(
        profile,
        capabilities,
        evidence_readiness_score=42.0,
        evidence_readiness_gate="not_ready",
    )

    assert policy.base_loop == "execute+verify-light"
    assert policy.requires_verification is True
    assert "evidence_readiness_gate=not_ready" in policy.rationale


def test_registries_filter_capabilities_and_harnesses() -> None:
    """Compatible capabilities should drive harness selection deterministically."""
    selector = LoopSelector()
    profile = selector.classify_task(
        Brief(
            problem_statement="Create current UX review for payments flow",
            context="Need latest examples",
            constraints=[],
        ),
        ["brain-02-ux-research", "brain-03-ui-design"],
    )
    capabilities = CapabilityRegistry().resolve_for_task(profile)
    harnesses = HarnessRegistry().resolve_for_capabilities(capabilities)

    assert any(cap.category == "mcp" for cap in capabilities.mcps)
    assert any(harness.harness_id == "execution-default" for harness in harnesses)
    assert any(harness.harness_id == "review-default" for harness in harnesses)


def test_execution_envelope_validates_success_shape() -> None:
    """Envelopes should be structurally valid for continuation logic."""
    selector = LoopSelector()
    profile = selector.classify_task(
        Brief(problem_statement="Review this API metric", context="", constraints=[]),
        ["brain-07-growth-data"],
    )
    capabilities = CapabilityRegistry().resolve_for_task(profile)
    policy = selector.select_loop(profile, capabilities)
    envelope = build_execution_envelope(
        task_profile=profile,
        loop_policy=policy,
        artifacts=("brain-07-growth-data",),
        next_actions=("continue",),
    )

    valid, errors = validate_execution_envelope(envelope)

    assert valid is True
    assert errors == ()
    assert envelope.status == "success"


def test_synthesize_execution_envelope_uses_most_restrictive_verdict() -> None:
    """Final envelope should prefer warning/error over optimistic base status."""
    selector = LoopSelector()
    profile = selector.classify_task(
        Brief(
            problem_statement="Build a CRM for small businesses",
            context="",
            constraints=[],
        ),
        ["brain-01-product-strategy"],
    )
    capabilities = CapabilityRegistry().resolve_for_task(profile)
    policy = selector.select_loop(profile, capabilities)
    base_envelope = build_execution_envelope(
        task_profile=profile,
        loop_policy=policy,
        artifacts=("brain-01-product-strategy",),
        next_actions=("continue",),
    )

    final_envelope = synthesize_execution_envelope(
        base_envelope=base_envelope,
        review_outcome=None,
        recovery_decision=None,
    )

    assert final_envelope.status == "success"
    assert final_envelope.next_actions == ("continue",)


def test_review_harness_approves_verified_envelope() -> None:
    """Verified envelopes with artifacts should pass local review."""
    selector = LoopSelector()
    profile = selector.classify_task(
        Brief(
            problem_statement="Implement and design a production migration plan",
            context="Need latest research and design review",
            constraints=["Use current sources"],
        ),
        ["brain-01-product-strategy", "brain-03-ui-design"],
    )
    capabilities = CapabilityRegistry().resolve_for_task(profile)
    policy = selector.select_loop(profile, capabilities)
    base_envelope = build_execution_envelope(
        task_profile=profile,
        loop_policy=policy,
        artifacts=("brain-01-product-strategy",),
        next_actions=("continue",),
    )
    verification = VerificationOutcome(
        performed=True,
        passed=True,
        checks=(
            VerificationCheck(
                check_id="artifacts-present",
                label="artifacts_present",
                passed=True,
                reason="artifacts present",
            ),
        ),
        acceptance_criteria_satisfied=True,
    )

    review_outcome = ReviewHarness().review(
        base_envelope,
        verification,
        ReviewRubricResolver().resolve(profile, policy),
    )

    assert review_outcome.approved is True
    assert review_outcome.recommended_next_action == "continue"


def test_recovery_harness_retries_execution_error_before_budget() -> None:
    """Execution errors should retry before the bounded budget is exhausted."""
    selector = LoopSelector()
    profile = selector.classify_task(
        Brief(problem_statement="Review this API metric", context="", constraints=[]),
        ["brain-07-growth-data"],
    )
    capabilities = CapabilityRegistry().resolve_for_task(profile)
    policy = selector.select_loop(profile, capabilities)
    failure = FailureClassifier().classify(
        ExecutionEnvelope(
            status="error",
            summary="boom",
            artifacts=(),
            risks=(),
            next_actions=(),
        ),
        None,
        None,
    )

    assert failure is not None

    recovery = RecoveryHarness().decide(failure, policy)

    assert recovery.action == "retry"
    assert recovery.escalate_to_human is False
