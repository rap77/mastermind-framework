"""Deterministic concern-stage planning for adaptive delivery units."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, replace

from .delivery_models import (
    DeliveryRouteAction,
    DeliveryRouteDecision,
    DeliveryRoutePlan,
    DeliveryUnit,
)
from .models import HarnessCompositionPlan, StageDefinition


def _require_text(value: str, label: str) -> None:
    if not value.strip():
        raise ValueError(f"{label} must not be empty")


@dataclass(frozen=True, slots=True)
class DeliveryStageSelection:
    """Policy decision and requested depth for one unit concern stage."""

    unit_id: str
    stage: StageDefinition
    decision: DeliveryRouteAction
    rationale: str
    depth: str

    def __post_init__(self) -> None:
        _require_text(self.unit_id, "unit_id")
        _require_text(self.rationale, "rationale")
        _require_text(self.depth, "depth")
        if self.decision not in {"execute", "skip", "block"}:
            raise ValueError(f"Unsupported delivery route decision: {self.decision}")


@dataclass(frozen=True, slots=True)
class DeliveryRouteProjection:
    """Executable unit stages projected from an auditable delivery route."""

    route_plan_id: str
    objective_id: str
    unit_id: str
    stages: tuple[StageDefinition, ...]

    def apply(self, plan: HarnessCompositionPlan) -> HarnessCompositionPlan:
        """Return a composition plan whose primary harness uses projected stages."""
        if plan.objective_profile.objective_id != self.objective_id:
            raise ValueError(
                "Delivery route objective does not match composition plan objective"
            )
        primary_harness = replace(plan.primary_harness, stages=self.stages)
        return replace(plan, primary_harness=primary_harness)


class AdaptiveRoutePlanner:
    """Validate, normalize, and project unit-scoped concern-stage decisions."""

    def plan(
        self,
        *,
        objective_id: str,
        adapter_id: str,
        units: tuple[DeliveryUnit, ...],
        selections: tuple[DeliveryStageSelection, ...],
    ) -> DeliveryRoutePlan:
        """Create a deterministic route while enforcing stage prerequisites."""
        _require_text(objective_id, "objective_id")
        _require_text(adapter_id, "adapter_id")
        units_by_id = {unit.unit_id: unit for unit in units}
        if not units_by_id:
            raise ValueError("units must not be empty")
        if len(units_by_id) != len(units):
            raise ValueError("Delivery unit IDs must be unique")

        mismatched_units = sorted(
            unit.unit_id for unit in units if unit.objective_ref != objective_id
        )
        if mismatched_units:
            raise ValueError(
                "Delivery units reference a different objective: "
                + ", ".join(mismatched_units)
            )

        selections_by_key: dict[tuple[str, str], DeliveryStageSelection] = {}
        for selection in selections:
            if selection.unit_id not in units_by_id:
                raise ValueError(
                    f"Stage selection references unknown unit '{selection.unit_id}'"
                )
            key = (selection.unit_id, selection.stage.stage_id)
            if key in selections_by_key:
                raise ValueError(
                    f"Duplicate stage selection '{selection.stage.stage_id}' "
                    f"for unit '{selection.unit_id}'"
                )
            selections_by_key[key] = selection

        for unit_id in sorted(units_by_id):
            unit_selections = {
                stage_id: selection
                for (selected_unit_id, stage_id), selection in selections_by_key.items()
                if selected_unit_id == unit_id
            }
            if not unit_selections:
                raise ValueError(f"Delivery unit '{unit_id}' has no stage decisions")
            self._validate_unit_selections(unit_id, unit_selections)

        decisions = tuple(
            DeliveryRouteDecision(
                unit_id=unit_id,
                concern=stage_id,
                decision=selection.decision,
                rationale=selection.rationale,
                depth=selection.depth,
                prerequisite_refs=tuple(sorted(set(selection.stage.prerequisites))),
                risk_level=units_by_id[unit_id].risk_level,
            )
            for (unit_id, stage_id), selection in sorted(selections_by_key.items())
        )
        unit_ids = tuple(sorted(units_by_id))
        return DeliveryRoutePlan(
            route_plan_id=self._route_plan_id(
                objective_id=objective_id,
                adapter_id=adapter_id,
                unit_ids=unit_ids,
                decisions=decisions,
            ),
            objective_id=objective_id,
            adapter_id=adapter_id,
            unit_ids=unit_ids,
            decisions=decisions,
        )

    def project_unit(
        self,
        route: DeliveryRoutePlan,
        *,
        unit_id: str,
        selections: tuple[DeliveryStageSelection, ...],
    ) -> DeliveryRouteProjection:
        """Project one executable unit route for the existing bundle composer."""
        if unit_id not in route.unit_ids:
            raise ValueError(f"Route does not declare unit '{unit_id}'")
        route_decisions = {
            decision.concern: decision
            for decision in route.decisions
            if decision.unit_id == unit_id
        }
        unit_selections = {
            selection.stage.stage_id: selection
            for selection in selections
            if selection.unit_id == unit_id
        }
        if set(route_decisions) != set(unit_selections):
            raise ValueError(
                f"Projection selections do not match route decisions for unit '{unit_id}'"
            )

        blocked = sorted(
            concern
            for concern, decision in route_decisions.items()
            if decision.decision == "block"
        )
        if blocked:
            raise ValueError(
                f"Blocked unit '{unit_id}' cannot be projected: " + ", ".join(blocked)
            )

        for concern, decision in route_decisions.items():
            selection = unit_selections[concern]
            if (
                selection.decision != decision.decision
                or selection.rationale != decision.rationale
                or selection.depth != decision.depth
            ):
                raise ValueError(
                    f"Projection selection for '{concern}' does not match route decision"
                )

        return DeliveryRouteProjection(
            route_plan_id=route.route_plan_id,
            objective_id=route.objective_id,
            unit_id=unit_id,
            stages=tuple(
                unit_selections[concern].stage
                for concern, decision in sorted(route_decisions.items())
                if decision.decision == "execute"
            ),
        )

    @staticmethod
    def _validate_unit_selections(
        unit_id: str,
        selections: dict[str, DeliveryStageSelection],
    ) -> None:
        for stage_id, selection in sorted(selections.items()):
            if selection.stage.required and selection.decision == "skip":
                raise ValueError(
                    f"Required stage '{stage_id}' for unit '{unit_id}' cannot skip"
                )
            if selection.decision != "execute":
                continue
            for prerequisite in sorted(set(selection.stage.prerequisites)):
                prerequisite_selection = selections.get(prerequisite)
                if (
                    prerequisite_selection is None
                    or prerequisite_selection.decision != "execute"
                ):
                    raise ValueError(
                        f"Stage '{stage_id}' for unit '{unit_id}' requires "
                        f"prerequisite '{prerequisite}' to execute"
                    )

        states: dict[str, int] = {}
        stack: list[str] = []
        positions: dict[str, int] = {}

        def visit(stage_id: str) -> tuple[str, ...]:
            states[stage_id] = 1
            positions[stage_id] = len(stack)
            stack.append(stage_id)
            for prerequisite in sorted(set(selections[stage_id].stage.prerequisites)):
                if states.get(prerequisite, 0) == 0:
                    cycle = visit(prerequisite)
                    if cycle:
                        return cycle
                elif states[prerequisite] == 1:
                    return tuple(sorted(stack[positions[prerequisite] :]))
            stack.pop()
            positions.pop(stage_id)
            states[stage_id] = 2
            return ()

        for stage_id in sorted(selections):
            if selections[stage_id].decision != "execute":
                continue
            if states.get(stage_id, 0) == 0 and (cycle := visit(stage_id)):
                raise ValueError(
                    f"Stage prerequisite cycle for unit '{unit_id}': "
                    + ", ".join(cycle)
                )

    @staticmethod
    def _route_plan_id(
        *,
        objective_id: str,
        adapter_id: str,
        unit_ids: tuple[str, ...],
        decisions: tuple[DeliveryRouteDecision, ...],
    ) -> str:
        payload = {
            "adapter_id": adapter_id,
            "decisions": [asdict(decision) for decision in decisions],
            "objective_id": objective_id,
            "unit_ids": unit_ids,
        }
        canonical = json.dumps(payload, separators=(",", ":"), sort_keys=True)
        digest = hashlib.sha256(canonical.encode()).hexdigest()
        return f"delivery-route:{digest}"
