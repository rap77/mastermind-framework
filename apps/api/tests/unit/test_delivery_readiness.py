"""Tests for adaptive delivery readiness evaluation."""

from mastermind_cli.orchestrator.runtime_contracts import (
    AdaptiveDeliveryRequest,
    DeliveryReadinessEvaluator,
)


def _request(
    *, requires_write: bool = True, checkpoint_ref: str | None = None
) -> AdaptiveDeliveryRequest:
    return AdaptiveDeliveryRequest(
        objective_id="objective-42",
        delivery_intent="Publish a validated operating handbook",
        domain="knowledge-management",
        delivery_mode="document-production",
        requirement_refs=("REQ-1", "REQ-2"),
        constraint_refs=("CONSTRAINT-1",),
        acceptance_criteria=("Outline approved", "Handbook approved"),
        candidate_unit_refs=("unit-outline", "unit-handbook"),
        dependency_refs=("dependency:outline-ready",),
        target_artifact_types=("outline", "handbook"),
        requires_write=requires_write,
        approval_policy="standard",
        security_profile_ref="security-profile-1",
        budget=8,
        checkpoint_ref=checkpoint_ref,
    )


def test_ready_request_records_resolved_adapter_and_compatible_permissions() -> None:
    """A fully resolved request should be ready for decomposition."""
    request = _request()

    readiness = DeliveryReadinessEvaluator().evaluate(
        request,
        adapter_id="knowledge-delivery@1",
        available_permissions=frozenset({"write"}),
        evaluable_criteria=frozenset(request.acceptance_criteria),
        available_dependency_refs=frozenset(request.dependency_refs),
        available_checkpoint_refs=frozenset(),
    )

    assert readiness.status == "ready"
    assert readiness.adapter_id == "knowledge-delivery@1"
    assert readiness.permissions_compatible is True
    assert readiness.blocker_refs == ()


def test_missing_permission_and_criteria_block_readiness_deterministically() -> None:
    """Missing production permission or evaluable criteria should block delivery."""
    request = _request()

    readiness = DeliveryReadinessEvaluator().evaluate(
        request,
        adapter_id="knowledge-delivery@1",
        available_permissions=frozenset(),
        evaluable_criteria=frozenset({"Outline approved"}),
        available_dependency_refs=frozenset(request.dependency_refs),
        available_checkpoint_refs=frozenset(),
    )

    assert readiness.status == "blocked"
    assert readiness.permissions_compatible is False
    assert readiness.blocker_refs == (
        "permission:write",
        "acceptance-criterion:Handbook approved",
    )


def test_missing_adapter_or_requested_checkpoint_escalates_readiness() -> None:
    """Unsafe adapter or resume ambiguity should require explicit escalation."""
    request = _request(checkpoint_ref="checkpoint-7")

    readiness = DeliveryReadinessEvaluator().evaluate(
        request,
        adapter_id=None,
        available_permissions=frozenset({"write"}),
        evaluable_criteria=frozenset(request.acceptance_criteria),
        available_dependency_refs=frozenset(request.dependency_refs),
        available_checkpoint_refs=frozenset(),
    )

    assert readiness.status == "escalated"
    assert readiness.blocker_refs == (
        "adapter:not-resolved",
        "checkpoint:checkpoint-7",
    )


def test_missing_declared_dependency_blocks_readiness() -> None:
    """A request should not advance while declared dependencies are unavailable."""
    request = _request(requires_write=False)

    readiness = DeliveryReadinessEvaluator().evaluate(
        request,
        adapter_id="knowledge-delivery@1",
        available_permissions=frozenset(),
        evaluable_criteria=frozenset(request.acceptance_criteria),
        available_dependency_refs=frozenset(),
        available_checkpoint_refs=frozenset(),
    )

    assert readiness.status == "blocked"
    assert readiness.permissions_compatible is True
    assert readiness.blocker_refs == ("dependency:dependency:outline-ready",)
