"""Deterministic validation and ordering of adaptive delivery units."""

from __future__ import annotations

import heapq

from .delivery_models import AdaptiveDeliveryRequest, DeliveryUnit


class DeliveryUnitDecomposer:
    """Validate proposed delivery units and return a stable dependency order."""

    def decompose(
        self,
        request: AdaptiveDeliveryRequest,
        units: tuple[DeliveryUnit, ...],
    ) -> tuple[DeliveryUnit, ...]:
        """Validate traceability and ownership, then topologically order units."""
        units_by_id = {unit.unit_id: unit for unit in units}
        if len(units_by_id) != len(units):
            raise ValueError("Delivery unit IDs must be unique")

        mismatched_objectives = sorted(
            unit.unit_id for unit in units if unit.objective_ref != request.objective_id
        )
        if mismatched_objectives:
            raise ValueError(
                "Delivery units reference a different objective: "
                + ", ".join(mismatched_objectives)
            )

        in_scope_requirements = set(request.requirement_refs)
        assigned_requirements = {
            requirement_ref
            for unit in units
            for requirement_ref in unit.requirement_refs
        }
        unknown_requirements = sorted(assigned_requirements - in_scope_requirements)
        if unknown_requirements:
            raise ValueError(
                "Delivery units reference out-of-scope requirements: "
                + ", ".join(unknown_requirements)
            )
        uncovered_requirements = sorted(in_scope_requirements - assigned_requirements)
        if uncovered_requirements:
            raise ValueError(
                "In-scope requirements lack a delivery unit and acceptance path: "
                + ", ".join(uncovered_requirements)
            )

        owners_by_artifact: dict[str, list[str]] = {}
        for unit in units:
            for artifact_type in unit.owned_artifact_types:
                owners_by_artifact.setdefault(artifact_type, []).append(unit.unit_id)
        for artifact_type in sorted(owners_by_artifact):
            owners = sorted(set(owners_by_artifact[artifact_type]))
            if len(owners) > 1:
                raise ValueError(
                    f"Artifact ownership conflict for '{artifact_type}': "
                    + ", ".join(owners)
                )

        declared_unit_ids = set(units_by_id)
        for unit in sorted(units, key=lambda candidate: candidate.unit_id):
            unknown_dependencies = sorted(
                set(unit.dependency_unit_ids) - declared_unit_ids
            )
            if unknown_dependencies:
                raise ValueError(
                    f"Delivery unit '{unit.unit_id}' has unknown dependencies: "
                    + ", ".join(unknown_dependencies)
                )

        cycle = self._find_cycle(units_by_id)
        if cycle:
            raise ValueError(
                "Delivery unit dependency cycle detected: " + ", ".join(cycle)
            )

        dependency_count = {
            unit.unit_id: len(set(unit.dependency_unit_ids)) for unit in units
        }
        dependents: dict[str, list[str]] = {unit_id: [] for unit_id in units_by_id}
        for unit in units:
            for dependency_id in set(unit.dependency_unit_ids):
                dependents[dependency_id].append(unit.unit_id)

        ready = [unit_id for unit_id, count in dependency_count.items() if count == 0]
        heapq.heapify(ready)
        ordered_ids: list[str] = []
        while ready:
            unit_id = heapq.heappop(ready)
            ordered_ids.append(unit_id)
            for dependent_id in sorted(dependents[unit_id]):
                dependency_count[dependent_id] -= 1
                if dependency_count[dependent_id] == 0:
                    heapq.heappush(ready, dependent_id)

        return tuple(units_by_id[unit_id] for unit_id in ordered_ids)

    @staticmethod
    def _find_cycle(units_by_id: dict[str, DeliveryUnit]) -> tuple[str, ...]:
        state: dict[str, int] = {}
        stack: list[str] = []
        stack_positions: dict[str, int] = {}

        def visit(unit_id: str) -> tuple[str, ...]:
            state[unit_id] = 1
            stack_positions[unit_id] = len(stack)
            stack.append(unit_id)
            for dependency_id in sorted(set(units_by_id[unit_id].dependency_unit_ids)):
                dependency_state = state.get(dependency_id, 0)
                if dependency_state == 0:
                    cycle = visit(dependency_id)
                    if cycle:
                        return cycle
                elif dependency_state == 1:
                    return tuple(sorted(stack[stack_positions[dependency_id] :]))
            stack.pop()
            stack_positions.pop(unit_id)
            state[unit_id] = 2
            return ()

        for unit_id in sorted(units_by_id):
            if state.get(unit_id, 0) == 0:
                cycle = visit(unit_id)
                if cycle:
                    return cycle
        return ()
