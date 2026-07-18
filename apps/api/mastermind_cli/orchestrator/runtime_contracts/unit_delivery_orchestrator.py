"""Dependency-ready, plan-governed execution of delivery units.

Progress, stage results, and checkpoints share one atomic persistence record.
Recovery of external capability side effects remains the shared executor's
idempotency and recovery boundary.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Literal, Protocol

from .delivery_models import DeliveryUnit
from .models import RunBundle
from .production_plans import ProductionPlan
from .run_bundle_stage_executor import (
    RunBundleStageExecutor,
    StageExecutionRecord,
)


UnitDeliveryStatus = Literal["verified", "blocked"]


@dataclass(frozen=True, slots=True)
class UnitDeliveryCheckpoint:
    """Exact resumable position persisted after one unit execution attempt."""

    checkpoint_id: str
    unit_id: str
    production_plan_ref: str | None
    completed_step_ids: tuple[str, ...]
    completed_stage_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class UnitDeliveryTransition:
    """Atomic unit progress, stage results, and checkpoint mutation."""

    unit_id: str
    status: UnitDeliveryStatus
    production_plan_ref: str | None
    completed_step_ids: tuple[str, ...]
    stage_records: tuple[StageExecutionRecord, ...]
    checkpoint: UnitDeliveryCheckpoint

    def __post_init__(self) -> None:
        if self.unit_id != self.checkpoint.unit_id:
            raise ValueError("Transition unit does not match checkpoint")
        if self.production_plan_ref != self.checkpoint.production_plan_ref:
            raise ValueError("Transition production plan does not match checkpoint")
        if self.completed_step_ids != self.checkpoint.completed_step_ids:
            raise ValueError("Transition step progress does not match checkpoint")
        completed_stage_ids = tuple(
            record.result.stage_id
            for record in self.stage_records
            if record.result.status == "passed"
        )
        if completed_stage_ids != self.checkpoint.completed_stage_ids:
            raise ValueError("Transition stage progress does not match checkpoint")


@dataclass(frozen=True, slots=True)
class UnitDeliveryReport:
    """Ordered durable transitions produced by one unit delivery loop."""

    transitions: tuple[UnitDeliveryTransition, ...]


class UnitTransitionPersistence(Protocol):
    """Atomic persistence boundary for unit progress and checkpoint state."""

    def persist(self, transition: UnitDeliveryTransition) -> None:
        """Persist one immutable unit transition atomically."""
        ...


class UnitDeliveryOrchestrator:
    """Run each dependency-ready unit end-to-end through the shared executor."""

    def __init__(
        self,
        stage_executor: RunBundleStageExecutor,
        persistence: UnitTransitionPersistence,
        *,
        plan_is_approved: Callable[[ProductionPlan], bool],
    ) -> None:
        """Initialize shared execution, persistence, and approval boundaries."""
        self._stage_executor = stage_executor
        self._persistence = persistence
        self._plan_is_approved = plan_is_approved

    def execute(
        self,
        *,
        units: tuple[DeliveryUnit, ...],
        bundles: Mapping[str, RunBundle],
        production_plans: Mapping[str, ProductionPlan],
        mutating_unit_ids: tuple[str, ...],
    ) -> UnitDeliveryReport:
        """Preflight all units, then execute stable dependency-ready units."""
        units_by_id = self._preflight(
            units=units,
            bundles=bundles,
            production_plans=production_plans,
            mutating_unit_ids=mutating_unit_ids,
        )
        pending = set(units_by_id)
        statuses: dict[str, UnitDeliveryStatus] = {}
        transitions: list[UnitDeliveryTransition] = []

        while pending:
            blocked = sorted(
                unit_id
                for unit_id in pending
                if any(
                    statuses.get(dependency_id) == "blocked"
                    for dependency_id in units_by_id[unit_id].dependency_unit_ids
                )
            )
            for unit_id in blocked:
                transition = self._blocked_transition(
                    unit_id,
                    production_plans.get(unit_id),
                )
                self._persistence.persist(transition)
                transitions.append(transition)
                statuses[unit_id] = "blocked"
                pending.remove(unit_id)

            ready = sorted(
                unit_id
                for unit_id in pending
                if all(
                    statuses.get(dependency_id) == "verified"
                    for dependency_id in units_by_id[unit_id].dependency_unit_ids
                )
            )
            if not ready:
                if pending:
                    raise ValueError(
                        "Delivery unit dependency graph cannot make progress"
                    )
                break

            for unit_id in ready:
                plan = production_plans.get(unit_id)
                stage_report = self._stage_executor.execute(bundles[unit_id])
                passed_stage_ids = tuple(
                    record.result.stage_id
                    for record in stage_report.stages
                    if record.result.status == "passed"
                )
                status: UnitDeliveryStatus = (
                    "verified"
                    if all(
                        record.result.status in {"passed", "skipped"}
                        for record in stage_report.stages
                    )
                    else "blocked"
                )
                completed_step_ids = (
                    tuple(
                        step.step_id
                        for step in plan.steps
                        if step.stage_id in passed_stage_ids
                    )
                    if plan is not None
                    else ()
                )
                transition = self._transition(
                    unit_id=unit_id,
                    status=status,
                    plan=plan,
                    completed_step_ids=completed_step_ids,
                    completed_stage_ids=passed_stage_ids,
                    stage_records=stage_report.stages,
                )
                self._persistence.persist(transition)
                transitions.append(transition)
                statuses[unit_id] = status
                pending.remove(unit_id)

        return UnitDeliveryReport(transitions=tuple(transitions))

    def _preflight(
        self,
        *,
        units: tuple[DeliveryUnit, ...],
        bundles: Mapping[str, RunBundle],
        production_plans: Mapping[str, ProductionPlan],
        mutating_unit_ids: tuple[str, ...],
    ) -> dict[str, DeliveryUnit]:
        """Reject all invalid plans and graphs before invoking any capability."""
        units_by_id = {unit.unit_id: unit for unit in units}
        if not units_by_id:
            raise ValueError("units must not be empty")
        if len(units_by_id) != len(units):
            raise ValueError("Delivery unit IDs must be unique")
        unit_ids = set(units_by_id)
        mutating = set(mutating_unit_ids)
        if len(mutating) != len(mutating_unit_ids):
            raise ValueError("mutating_unit_ids must be unique")
        if unknown := sorted(mutating - unit_ids):
            raise ValueError(f"Unknown mutating unit: {unknown[0]}")

        for unit_id in sorted(unit_ids):
            unit = units_by_id[unit_id]
            unknown_dependencies = set(unit.dependency_unit_ids) - unit_ids
            if unknown_dependencies:
                raise ValueError(
                    f"Delivery unit '{unit_id}' has unknown dependencies: "
                    + ", ".join(sorted(unknown_dependencies))
                )
            bundle = bundles.get(unit_id)
            if bundle is None:
                raise ValueError(f"Delivery unit '{unit_id}' requires a RunBundle")
            if bundle.objective_id != unit.objective_ref:
                raise ValueError(f"RunBundle objective does not match unit '{unit_id}'")

            plan = production_plans.get(unit_id)
            if unit_id in mutating and plan is None:
                raise ValueError(
                    f"Mutating unit '{unit_id}' requires a versioned production plan"
                )
            if plan is None:
                continue
            self._validate_plan(unit, bundle, plan)
            if unit_id in mutating and not self._plan_is_approved(plan):
                raise ValueError(
                    f"Production plan '{plan.versioned_id}' is not approved"
                )

        self._validate_acyclic(units_by_id)
        return units_by_id

    @staticmethod
    def _validate_plan(
        unit: DeliveryUnit,
        bundle: RunBundle,
        plan: ProductionPlan,
    ) -> None:
        if plan.unit_id != unit.unit_id:
            raise ValueError(f"Production plan does not match unit '{unit.unit_id}'")
        graph = bundle.stage_graph
        if graph is None:
            raise ValueError(f"RunBundle for unit '{unit.unit_id}' has no stage graph")
        planned_stage_ids = {step.stage_id for step in plan.steps}
        bundle_stage_ids = {node.stage.stage_id for node in graph.nodes}
        if planned_stage_ids != bundle_stage_ids:
            raise ValueError(
                f"Production plan stages do not match RunBundle for unit '{unit.unit_id}'"
            )
        unit_requirements = set(unit.requirement_refs)
        if any(
            not set(step.requirement_refs).issubset(unit_requirements)
            for step in plan.steps
        ):
            raise ValueError(
                f"Production plan references requirements outside unit '{unit.unit_id}'"
            )

    @staticmethod
    def _validate_acyclic(units_by_id: Mapping[str, DeliveryUnit]) -> None:
        remaining = set(units_by_id)
        resolved: set[str] = set()
        while remaining:
            ready = {
                unit_id
                for unit_id in remaining
                if set(units_by_id[unit_id].dependency_unit_ids).issubset(resolved)
            }
            if not ready:
                raise ValueError("Delivery unit dependency cycle detected")
            resolved.update(ready)
            remaining.difference_update(ready)

    @classmethod
    def _blocked_transition(
        cls,
        unit_id: str,
        plan: ProductionPlan | None,
    ) -> UnitDeliveryTransition:
        return cls._transition(
            unit_id=unit_id,
            status="blocked",
            plan=plan,
            completed_step_ids=(),
            completed_stage_ids=(),
            stage_records=(),
        )

    @staticmethod
    def _transition(
        *,
        unit_id: str,
        status: UnitDeliveryStatus,
        plan: ProductionPlan | None,
        completed_step_ids: tuple[str, ...],
        completed_stage_ids: tuple[str, ...],
        stage_records: tuple[StageExecutionRecord, ...],
    ) -> UnitDeliveryTransition:
        plan_ref = plan.versioned_id if plan is not None else None
        checkpoint = UnitDeliveryCheckpoint(
            checkpoint_id=f"{unit_id}:{plan_ref or 'unplanned'}:{status}",
            unit_id=unit_id,
            production_plan_ref=plan_ref,
            completed_step_ids=completed_step_ids,
            completed_stage_ids=completed_stage_ids,
        )
        return UnitDeliveryTransition(
            unit_id=unit_id,
            status=status,
            production_plan_ref=plan_ref,
            completed_step_ids=completed_step_ids,
            stage_records=stage_records,
            checkpoint=checkpoint,
        )
