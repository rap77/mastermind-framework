"""Tests for deterministic adaptive delivery route planning."""

from dataclasses import FrozenInstanceError, replace

import pytest

from mastermind_cli.orchestrator.runtime_contracts import (
    AdaptiveRoutePlanner,
    DeliveryStageSelection,
    DeliveryUnit,
    StageDefinition,
)


def _unit(unit_id: str = "unit-publication") -> DeliveryUnit:
    return DeliveryUnit(
        unit_id=unit_id,
        name="Publication",
        objective_ref="objective-42",
        requirement_refs=("REQ-1",),
        dependency_unit_ids=(),
        owned_artifact_types=("publication",),
        input_contract_refs=(),
        output_contract_refs=("contract:publication",),
        acceptance_criteria=("Publication is approved",),
        risk_level="medium",
        route_profile="standard",
        status="pending",
    )


def _stage(
    stage_id: str,
    *,
    required: bool,
    prerequisites: tuple[str, ...] = (),
    output_artifact_types: tuple[str, ...] = (),
) -> StageDefinition:
    return StageDefinition(
        stage_id=stage_id,
        name=stage_id,
        required=required,
        prerequisites=prerequisites,
        capability_refs=(f"capability:{stage_id}",),
        input_artifact_types=(),
        output_artifact_types=output_artifact_types,
        gate_policy="gate:delivery",
        approval_policy="approval:delivery",
        recovery_policy="recovery:bounded",
        max_attempts=2,
    )


def _selection(
    stage: StageDefinition,
    *,
    decision: str,
    rationale: str,
    depth: str = "standard",
) -> DeliveryStageSelection:
    return DeliveryStageSelection(
        unit_id="unit-publication",
        stage=stage,
        decision=decision,  # type: ignore[arg-type]
        rationale=rationale,
        depth=depth,
    )


def test_planner_records_execute_skip_and_block_with_rationale() -> None:
    """Every selected concern should retain its action and explanation."""
    selections = (
        _selection(
            _stage("production", required=True),
            decision="execute",
            rationale="The publication must be produced",
        ),
        _selection(
            _stage("environment-design", required=False),
            decision="skip",
            rationale="The existing environment is sufficient",
            depth="minimal",
        ),
        _selection(
            _stage("independent-review", required=False),
            decision="block",
            rationale="No independent reviewer is available",
            depth="deep",
        ),
    )

    route = AdaptiveRoutePlanner().plan(
        objective_id="objective-42",
        adapter_id="knowledge-delivery@1.2.0",
        units=(_unit(),),
        selections=selections,
    )

    assert tuple(
        (decision.concern, decision.decision, decision.rationale, decision.depth)
        for decision in route.decisions
    ) == (
        (
            "environment-design",
            "skip",
            "The existing environment is sufficient",
            "minimal",
        ),
        (
            "independent-review",
            "block",
            "No independent reviewer is available",
            "deep",
        ),
        (
            "production",
            "execute",
            "The publication must be produced",
            "standard",
        ),
    )


def test_projection_changes_depth_without_changing_required_artifacts() -> None:
    """Depth should affect route detail while preserving stage artifact contracts."""
    production = _stage(
        "production",
        required=True,
        output_artifact_types=("publication", "production-log"),
    )
    standard_selection = _selection(
        production,
        decision="execute",
        rationale="Standard production path",
        depth="standard",
    )
    deep_selection = replace(
        standard_selection,
        rationale="Deep production path",
        depth="deep",
    )
    planner = AdaptiveRoutePlanner()

    standard = planner.plan(
        objective_id="objective-42",
        adapter_id="knowledge-delivery@1.2.0",
        units=(_unit(),),
        selections=(standard_selection,),
    )
    deep = planner.plan(
        objective_id="objective-42",
        adapter_id="knowledge-delivery@1.2.0",
        units=(_unit(),),
        selections=(deep_selection,),
    )

    standard_projection = planner.project_unit(
        standard,
        unit_id="unit-publication",
        selections=(standard_selection,),
    )
    deep_projection = planner.project_unit(
        deep,
        unit_id="unit-publication",
        selections=(deep_selection,),
    )

    assert standard.decisions[0].depth == "standard"
    assert deep.decisions[0].depth == "deep"
    assert standard_projection.stages[0].output_artifact_types == (
        "publication",
        "production-log",
    )
    assert deep_projection.stages[0].output_artifact_types == (
        "publication",
        "production-log",
    )
    with pytest.raises(FrozenInstanceError):
        standard_projection.unit_id = "other-unit"  # type: ignore[misc]


@pytest.mark.parametrize("prerequisite_decision", ["skip", "block"])
def test_planner_rejects_execute_after_non_executed_prerequisite(
    prerequisite_decision: str,
) -> None:
    """An executed stage cannot depend on a skipped or blocked concern."""
    design = _stage("design", required=False)
    production = _stage(
        "production",
        required=True,
        prerequisites=("design",),
    )

    with pytest.raises(
        ValueError,
        match=(
            "Stage 'production' for unit 'unit-publication' requires "
            "prerequisite 'design' to execute"
        ),
    ):
        AdaptiveRoutePlanner().plan(
            objective_id="objective-42",
            adapter_id="knowledge-delivery@1.2.0",
            units=(_unit(),),
            selections=(
                _selection(
                    design,
                    decision=prerequisite_decision,
                    rationale="Policy decision",
                ),
                _selection(
                    production,
                    decision="execute",
                    rationale="Production is required",
                ),
            ),
        )


def test_planner_rejects_skipping_a_required_stage() -> None:
    """A required concern may execute or block, but cannot disappear as skipped."""
    with pytest.raises(
        ValueError,
        match="Required stage 'production' for unit 'unit-publication' cannot skip",
    ):
        AdaptiveRoutePlanner().plan(
            objective_id="objective-42",
            adapter_id="knowledge-delivery@1.2.0",
            units=(_unit(),),
            selections=(
                _selection(
                    _stage("production", required=True),
                    decision="skip",
                    rationale="Production was considered unnecessary",
                ),
            ),
        )


def test_route_is_deterministic_regardless_of_unit_and_selection_order() -> None:
    """Equivalent unordered inputs should produce the same route and identity."""
    design = _selection(
        _stage("design", required=True),
        decision="execute",
        rationale="Design is required",
    )
    production = _selection(
        _stage("production", required=True, prerequisites=("design",)),
        decision="execute",
        rationale="Production is required",
        depth="deep",
    )
    second_design = replace(design, unit_id="unit-release")
    second_production = replace(production, unit_id="unit-release")
    units = (_unit(), _unit("unit-release"))
    selections = (production, second_design, design, second_production)
    planner = AdaptiveRoutePlanner()

    first = planner.plan(
        objective_id="objective-42",
        adapter_id="knowledge-delivery@1.2.0",
        units=units,
        selections=selections,
    )
    second = planner.plan(
        objective_id="objective-42",
        adapter_id="knowledge-delivery@1.2.0",
        units=tuple(reversed(units)),
        selections=tuple(reversed(selections)),
    )

    assert first == second
    assert first.unit_ids == ("unit-publication", "unit-release")
    assert first.route_plan_id.startswith("delivery-route:")


def test_planner_rejects_cyclic_prerequisite_paths() -> None:
    """Concern-stage cycles must fail before projection into an executable graph."""
    with pytest.raises(
        ValueError,
        match=(
            "Stage prerequisite cycle for unit 'unit-publication': design, production"
        ),
    ):
        AdaptiveRoutePlanner().plan(
            objective_id="objective-42",
            adapter_id="knowledge-delivery@1.2.0",
            units=(_unit(),),
            selections=(
                _selection(
                    _stage("design", required=True, prerequisites=("production",)),
                    decision="execute",
                    rationale="Design is required",
                ),
                _selection(
                    _stage("production", required=True, prerequisites=("design",)),
                    decision="execute",
                    rationale="Production is required",
                ),
            ),
        )
