"""Tests for deterministic adaptive delivery decomposition."""

import pytest

from mastermind_cli.orchestrator.runtime_contracts import (
    AdaptiveDeliveryRequest,
    DeliveryUnit,
    DeliveryUnitDecomposer,
)


def _request() -> AdaptiveDeliveryRequest:
    return AdaptiveDeliveryRequest(
        objective_id="objective-42",
        delivery_intent="Publish a validated operating handbook",
        domain="knowledge-management",
        delivery_mode="document-production",
        requirement_refs=("REQ-1", "REQ-2"),
        constraint_refs=(),
        acceptance_criteria=("Outline approved", "Handbook approved"),
        candidate_unit_refs=("unit-outline", "unit-handbook"),
        dependency_refs=(),
        target_artifact_types=("outline", "handbook"),
        requires_write=True,
        approval_policy="standard",
        security_profile_ref=None,
        budget=8,
        checkpoint_ref=None,
    )


def _unit(
    unit_id: str,
    requirement_ref: str,
    artifact_type: str,
    *,
    dependencies: tuple[str, ...] = (),
) -> DeliveryUnit:
    return DeliveryUnit(
        unit_id=unit_id,
        name=unit_id,
        objective_ref="objective-42",
        requirement_refs=(requirement_ref,),
        dependency_unit_ids=dependencies,
        owned_artifact_types=(artifact_type,),
        input_contract_refs=(),
        output_contract_refs=(f"contract:{artifact_type}",),
        acceptance_criteria=(f"Accept {requirement_ref}",),
        risk_level="low",
        route_profile="standard",
        status="pending",
    )


def test_decomposition_orders_units_and_preserves_requirement_acceptance_paths() -> (
    None
):
    """Every requirement should map to an accepted unit in stable dependency order."""
    units = (
        _unit(
            "unit-handbook",
            "REQ-2",
            "handbook",
            dependencies=("unit-outline",),
        ),
        _unit("unit-outline", "REQ-1", "outline"),
    )

    decomposition = DeliveryUnitDecomposer().decompose(_request(), units)

    assert tuple(unit.unit_id for unit in decomposition) == (
        "unit-outline",
        "unit-handbook",
    )
    assert {
        requirement_ref: unit.acceptance_criteria
        for unit in decomposition
        for requirement_ref in unit.requirement_refs
    } == {
        "REQ-1": ("Accept REQ-1",),
        "REQ-2": ("Accept REQ-2",),
    }


def test_decomposition_rejects_requirement_without_acceptance_path() -> None:
    """An in-scope requirement without a unit must fail before route planning."""
    units = (_unit("unit-outline", "REQ-1", "outline"),)

    with pytest.raises(
        ValueError,
        match="In-scope requirements lack a delivery unit and acceptance path: REQ-2",
    ):
        DeliveryUnitDecomposer().decompose(_request(), units)


def test_decomposition_rejects_dependency_cycles_deterministically() -> None:
    """Cycles should report their stable member set rather than input ordering."""
    units = (
        _unit("unit-handbook", "REQ-2", "handbook", dependencies=("unit-outline",)),
        _unit("unit-outline", "REQ-1", "outline", dependencies=("unit-handbook",)),
    )

    with pytest.raises(
        ValueError,
        match="Delivery unit dependency cycle detected: unit-handbook, unit-outline",
    ):
        DeliveryUnitDecomposer().decompose(_request(), units)


def test_decomposition_rejects_artifact_ownership_conflicts_deterministically() -> None:
    """One artifact type cannot have multiple owners in the same decomposition."""
    units = (
        _unit("unit-handbook", "REQ-2", "publication"),
        _unit("unit-outline", "REQ-1", "publication"),
    )

    with pytest.raises(
        ValueError,
        match=(
            "Artifact ownership conflict for 'publication': "
            "unit-handbook, unit-outline"
        ),
    ):
        DeliveryUnitDecomposer().decompose(_request(), units)
