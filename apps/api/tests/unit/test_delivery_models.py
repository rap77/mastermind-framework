"""Tests for adaptive delivery runtime data contracts."""

import pytest

from mastermind_cli.orchestrator.runtime_contracts import (
    AdaptiveDeliveryRequest,
    DeliveryReadinessProfile,
    DeliveryRouteDecision,
    DeliveryRoutePlan,
    DeliveryUnit,
    IntegrationVerdict,
)


def test_adaptive_delivery_request_captures_approved_delivery_intent() -> None:
    """Requests should preserve the inputs needed to assess delivery readiness."""
    request = AdaptiveDeliveryRequest(
        objective_id="objective-42",
        delivery_intent="Publish a validated operating handbook",
        domain="knowledge-management",
        delivery_mode="document-production",
        requirement_refs=("REQ-1", "REQ-2"),
        constraint_refs=("CONSTRAINT-1",),
        acceptance_criteria=("Handbook passes editorial review",),
        candidate_unit_refs=("unit-outline", "unit-handbook"),
        dependency_refs=("unit-handbook:unit-outline",),
        target_artifact_types=("outline", "handbook"),
        requires_write=True,
        approval_policy="standard",
        security_profile_ref="security-profile-1",
        budget=8,
        checkpoint_ref=None,
    )

    assert request.objective_id == "objective-42"
    assert request.acceptance_criteria == ("Handbook passes editorial review",)
    assert request.target_artifact_types == ("outline", "handbook")


def test_delivery_readiness_profile_records_boundary_findings() -> None:
    """Readiness profiles should explain whether delivery may proceed."""
    readiness = DeliveryReadinessProfile(
        objective_id="objective-42",
        status="blocked",
        adapter_id=None,
        permissions_compatible=True,
        blocker_refs=("adapter:not-resolved",),
        rationale=("No compatible domain adapter was resolved",),
    )

    assert readiness.status == "blocked"
    assert readiness.blocker_refs == ("adapter:not-resolved",)


def test_delivery_unit_makes_dependencies_and_artifact_ownership_explicit() -> None:
    """Units should expose dependencies, owned artifacts, and acceptance paths."""
    unit = DeliveryUnit(
        unit_id="unit-handbook",
        name="Operating handbook",
        objective_ref="objective-42",
        requirement_refs=("REQ-2",),
        dependency_unit_ids=("unit-outline",),
        owned_artifact_types=("handbook",),
        input_contract_refs=("contract:outline-v1",),
        output_contract_refs=("contract:handbook-v1",),
        acceptance_criteria=("Handbook passes editorial review",),
        risk_level="medium",
        route_profile="document-standard",
        status="pending",
    )

    assert unit.dependency_unit_ids == ("unit-outline",)
    assert unit.owned_artifact_types == ("handbook",)
    assert unit.output_contract_refs == ("contract:handbook-v1",)


def test_delivery_route_plan_records_unit_scoped_decisions() -> None:
    """Route plans should preserve execute, skip, or block decisions per unit."""
    decision = DeliveryRouteDecision(
        unit_id="unit-handbook",
        concern="production",
        decision="execute",
        rationale="The handbook artifact must be produced",
        depth="standard",
        prerequisite_refs=("unit-outline",),
        risk_level="medium",
    )
    route = DeliveryRoutePlan(
        route_plan_id="route-42",
        objective_id="objective-42",
        adapter_id="document-delivery@1",
        unit_ids=("unit-outline", "unit-handbook"),
        decisions=(decision,),
    )

    assert route.decisions[0].unit_id == "unit-handbook"
    assert route.decisions[0].decision == "execute"
    assert route.decisions[0].prerequisite_refs == ("unit-outline",)


def test_delivery_integration_verdict_preserves_evidence_and_residual_risk() -> None:
    """Integration verdicts should retain traceability and explicit blockers."""
    verdict = IntegrationVerdict(
        status="passed",
        objective_id="objective-42",
        unit_ids=("unit-outline", "unit-handbook"),
        requirement_refs=("REQ-1", "REQ-2"),
        evidence_refs=("evidence:editorial-review",),
        blocker_refs=(),
        residual_risks=("Publication date may move",),
        conditions=(),
        condition_owner=None,
        condition_expires_at=None,
    )

    assert verdict.status == "passed"
    assert verdict.evidence_refs == ("evidence:editorial-review",)
    assert verdict.residual_risks == ("Publication date may move",)


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"objective_id": " "}, "objective_id must not be empty"),
        ({"delivery_intent": ""}, "delivery_intent must not be empty"),
        ({"domain": ""}, "domain must not be empty"),
        ({"delivery_mode": ""}, "delivery_mode must not be empty"),
        ({"acceptance_criteria": ()}, "acceptance_criteria must not be empty"),
        (
            {"acceptance_criteria": (" ",)},
            "acceptance_criteria entries must not be empty",
        ),
        ({"requirement_refs": ("",)}, "requirement_refs entries must not be empty"),
        ({"approval_policy": "automatic"}, "Unsupported approval policy"),
        ({"budget": -1}, "budget must not be negative"),
    ],
)
def test_adaptive_delivery_request_rejects_invalid_or_ambiguous_boundaries(
    overrides: dict[str, object], message: str
) -> None:
    """Requests without unambiguous scope and acceptance should fail immediately."""
    values: dict[str, object] = {
        "objective_id": "objective-42",
        "delivery_intent": "Publish a validated operating handbook",
        "domain": "knowledge-management",
        "delivery_mode": "document-production",
        "requirement_refs": ("REQ-1",),
        "constraint_refs": (),
        "acceptance_criteria": ("Handbook passes editorial review",),
        "candidate_unit_refs": (),
        "dependency_refs": (),
        "target_artifact_types": ("handbook",),
        "requires_write": True,
        "approval_policy": "standard",
        "security_profile_ref": None,
        "budget": 8,
        "checkpoint_ref": None,
    }
    values.update(overrides)

    with pytest.raises(ValueError, match=message):
        AdaptiveDeliveryRequest(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"conditions": ()}, "conditional verdict requires conditions"),
        ({"condition_owner": None}, "conditional verdict requires condition_owner"),
        (
            {"condition_expires_at": None},
            "conditional verdict requires condition_expires_at",
        ),
    ],
)
def test_conditional_integration_verdict_requires_complete_conditions(
    overrides: dict[str, object], message: str
) -> None:
    """Conditional acceptance should fail without accountable expiry metadata."""
    values: dict[str, object] = {
        "status": "conditional",
        "objective_id": "objective-42",
        "unit_ids": ("unit-handbook",),
        "requirement_refs": ("REQ-1",),
        "evidence_refs": ("evidence:editorial-review",),
        "blocker_refs": (),
        "residual_risks": ("Final approval is pending",),
        "conditions": ("Obtain final approval",),
        "condition_owner": "editorial-owner",
        "condition_expires_at": "2026-08-01T00:00:00Z",
    }
    values.update(overrides)

    with pytest.raises(ValueError, match=message):
        IntegrationVerdict(**values)  # type: ignore[arg-type]
