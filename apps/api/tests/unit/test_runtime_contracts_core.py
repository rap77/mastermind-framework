"""Tests for the deterministic harness core."""

from mastermind_cli.orchestrator.runtime_contracts import HarnessCore, RuntimeRequest
from mastermind_cli.types.interfaces import Brief


def test_harness_core_selects_runtime_contracts_deterministically() -> None:
    """The core should choose the same minimum runtime for the same request."""
    core = HarnessCore()

    selection = core.select_runtime(
        RuntimeRequest(
            brief=Brief(
                problem_statement="Implement and design a production migration plan",
                context="Need latest research and design review",
                constraints=["Use current sources"],
            ),
            brain_ids=("brain-01-product-strategy", "brain-03-ui-design"),
        )
    )

    assert selection.loop_policy.base_loop == "execute+verify-light"
    assert selection.loop_policy.requires_verification is True
    assert selection.loop_policy.requires_review is True
    assert selection.task_profile.requires_checker is True
    assert any(
        harness.harness_id == "review-default" for harness in selection.harnesses
    )


def test_harness_core_builds_a_valid_execution_result() -> None:
    """The core should emit a canonical execution result from a selection."""
    core = HarnessCore()
    selection = core.select_runtime(
        RuntimeRequest(
            brief=Brief(
                problem_statement="Implement and design a production migration plan",
                context="Need latest research and design review",
                constraints=["Use current sources"],
            ),
            brain_ids=("brain-01-product-strategy", "brain-03-ui-design"),
        )
    )

    result = core.build_execution_result(
        selection,
        artifacts=("brain-01-product-strategy",),
        risks=("risk: production migration",),
        next_actions=("continue",),
    )

    assert result.base_envelope.status == "warning"
    assert result.verification_outcome is not None
    assert result.review_outcome is not None
    assert result.review_outcome.approved is True
    assert result.recovery_decision is None
    assert result.execution_envelope.status == "success"
    assert result.execution_envelope.review is not None


def test_harness_core_rejects_empty_brain_request() -> None:
    """The core should fail loudly when the request has no target brains."""
    core = HarnessCore()

    try:
        core.select_runtime(
            RuntimeRequest(
                brief=Brief(problem_statement="Build a CRM"),
                brain_ids=(),
            )
        )
    except ValueError as exc:
        assert "at least one brain id" in str(exc)
    else:
        raise AssertionError("Expected ValueError for empty brain request")
