"""Versioned plan-before-production contracts for delivery units."""

from __future__ import annotations

from dataclasses import dataclass


def _require_text(value: str, label: str) -> None:
    if not value.strip():
        raise ValueError(f"{label} must not be empty")


def _require_entries(
    values: tuple[str, ...],
    label: str,
    *,
    allow_empty: bool = False,
) -> None:
    if not allow_empty and not values:
        raise ValueError(f"{label} must not be empty")
    if any(not value.strip() for value in values):
        raise ValueError(f"{label} entries must not be empty")


@dataclass(frozen=True, slots=True)
class ProductionPlanStep:
    """One ordered, traceable production or verification step."""

    step_id: str
    stage_id: str
    target_artifact_refs: tuple[str, ...]
    requirement_refs: tuple[str, ...]
    dependency_refs: tuple[str, ...]
    contract_refs: tuple[str, ...]
    verification_refs: tuple[str, ...]
    side_effect_refs: tuple[str, ...]
    rollback_considerations: tuple[str, ...]
    completion_criteria: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_text(self.step_id, "step_id")
        _require_text(self.stage_id, "stage_id")
        for label, values, allow_empty in (
            ("target_artifact_refs", self.target_artifact_refs, False),
            ("requirement_refs", self.requirement_refs, False),
            ("dependency_refs", self.dependency_refs, True),
            ("contract_refs", self.contract_refs, False),
            ("verification_refs", self.verification_refs, False),
            ("side_effect_refs", self.side_effect_refs, True),
            ("rollback_considerations", self.rollback_considerations, False),
            ("completion_criteria", self.completion_criteria, False),
        ):
            _require_entries(values, label, allow_empty=allow_empty)


@dataclass(frozen=True, slots=True)
class ProductionPlan:
    """Immutable versioned plan governing one delivery unit's side effects."""

    plan_id: str
    version: str
    unit_id: str
    steps: tuple[ProductionPlanStep, ...]

    def __post_init__(self) -> None:
        _require_text(self.plan_id, "plan_id")
        _require_text(self.version, "version")
        _require_text(self.unit_id, "unit_id")
        if not self.steps:
            raise ValueError("steps must not be empty")
        step_ids = tuple(step.step_id for step in self.steps)
        stage_ids = tuple(step.stage_id for step in self.steps)
        if len(step_ids) != len(set(step_ids)):
            raise ValueError("Production plan step IDs must be unique")
        if len(stage_ids) != len(set(stage_ids)):
            raise ValueError("Production plan stage IDs must be unique")
        declared_steps: set[str] = set()
        for step in self.steps:
            unknown_dependencies = set(step.dependency_refs) - declared_steps
            if unknown_dependencies:
                raise ValueError(
                    f"Production step '{step.step_id}' has unordered dependencies: "
                    + ", ".join(sorted(unknown_dependencies))
                )
            declared_steps.add(step.step_id)

    @property
    def versioned_id(self) -> str:
        """Return the approval and lineage identity for this plan version."""
        return f"{self.plan_id}@{self.version}"
