"""Domain-agnostic data contracts for adaptive delivery runs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .models import RiskLevel


ApprovalPolicy = Literal["minimal", "standard", "strict", "segregated"]
DeliveryReadinessStatus = Literal["ready", "blocked", "escalated"]
DeliveryUnitStatus = Literal[
    "pending", "ready", "active", "blocked", "produced", "verified", "integrated"
]
DeliveryRouteAction = Literal["execute", "skip", "block"]
DeliveryIntegrationStatus = Literal["passed", "failed", "blocked", "conditional"]


def _require_non_empty(value: str, label: str) -> None:
    if not value.strip():
        raise ValueError(f"{label} must not be empty")


def _require_non_empty_entries(values: tuple[str, ...], label: str) -> None:
    if any(not value.strip() for value in values):
        raise ValueError(f"{label} entries must not be empty")


def _require_choice(value: str, allowed: frozenset[str], label: str) -> None:
    if value not in allowed:
        raise ValueError(f"Unsupported {label}: {value}")


@dataclass(frozen=True, slots=True)
class AdaptiveDeliveryRequest:
    """Approved delivery intent and boundary inputs for readiness evaluation."""

    objective_id: str
    delivery_intent: str
    domain: str
    delivery_mode: str
    requirement_refs: tuple[str, ...]
    constraint_refs: tuple[str, ...]
    acceptance_criteria: tuple[str, ...]
    candidate_unit_refs: tuple[str, ...]
    dependency_refs: tuple[str, ...]
    target_artifact_types: tuple[str, ...]
    requires_write: bool
    approval_policy: ApprovalPolicy
    security_profile_ref: str | None
    budget: int
    checkpoint_ref: str | None

    def __post_init__(self) -> None:
        _require_non_empty(self.objective_id, "objective_id")
        _require_non_empty(self.delivery_intent, "delivery_intent")
        _require_non_empty(self.domain, "domain")
        _require_non_empty(self.delivery_mode, "delivery_mode")
        if not self.acceptance_criteria:
            raise ValueError("acceptance_criteria must not be empty")
        _require_non_empty_entries(self.acceptance_criteria, "acceptance_criteria")
        _require_choice(
            self.approval_policy,
            frozenset({"minimal", "standard", "strict", "segregated"}),
            "approval policy",
        )
        if self.budget < 0:
            raise ValueError("budget must not be negative")

        for label, values in (
            ("requirement_refs", self.requirement_refs),
            ("constraint_refs", self.constraint_refs),
            ("candidate_unit_refs", self.candidate_unit_refs),
            ("dependency_refs", self.dependency_refs),
            ("target_artifact_types", self.target_artifact_types),
        ):
            _require_non_empty_entries(values, label)
        if self.security_profile_ref is not None:
            _require_non_empty(self.security_profile_ref, "security_profile_ref")
        if self.checkpoint_ref is not None:
            _require_non_empty(self.checkpoint_ref, "checkpoint_ref")


@dataclass(frozen=True, slots=True)
class DeliveryReadinessProfile:
    """Auditable readiness result produced before delivery decomposition."""

    objective_id: str
    status: DeliveryReadinessStatus
    adapter_id: str | None
    permissions_compatible: bool
    blocker_refs: tuple[str, ...]
    rationale: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_non_empty(self.objective_id, "objective_id")
        _require_choice(
            self.status,
            frozenset({"ready", "blocked", "escalated"}),
            "delivery readiness status",
        )
        if self.adapter_id is not None:
            _require_non_empty(self.adapter_id, "adapter_id")
        _require_non_empty_entries(self.blocker_refs, "blocker_refs")
        _require_non_empty_entries(self.rationale, "rationale")


@dataclass(frozen=True, slots=True)
class DeliveryUnit:
    """Traceable unit with explicit dependencies, ownership, and acceptance."""

    unit_id: str
    name: str
    objective_ref: str
    requirement_refs: tuple[str, ...]
    dependency_unit_ids: tuple[str, ...]
    owned_artifact_types: tuple[str, ...]
    input_contract_refs: tuple[str, ...]
    output_contract_refs: tuple[str, ...]
    acceptance_criteria: tuple[str, ...]
    risk_level: RiskLevel
    route_profile: str
    status: DeliveryUnitStatus

    def __post_init__(self) -> None:
        _require_non_empty(self.unit_id, "unit_id")
        _require_non_empty(self.name, "name")
        _require_non_empty(self.objective_ref, "objective_ref")
        _require_non_empty(self.route_profile, "route_profile")
        _require_choice(
            self.risk_level,
            frozenset({"low", "medium", "high", "critical"}),
            "risk level",
        )
        _require_choice(
            self.status,
            frozenset(
                {
                    "pending",
                    "ready",
                    "active",
                    "blocked",
                    "produced",
                    "verified",
                    "integrated",
                }
            ),
            "delivery unit status",
        )
        if not self.acceptance_criteria:
            raise ValueError("acceptance_criteria must not be empty")
        for label, values in (
            ("requirement_refs", self.requirement_refs),
            ("dependency_unit_ids", self.dependency_unit_ids),
            ("owned_artifact_types", self.owned_artifact_types),
            ("input_contract_refs", self.input_contract_refs),
            ("output_contract_refs", self.output_contract_refs),
            ("acceptance_criteria", self.acceptance_criteria),
        ):
            _require_non_empty_entries(values, label)


@dataclass(frozen=True, slots=True)
class DeliveryRouteDecision:
    """Unit-scoped execute, skip, or block decision for a delivery concern."""

    unit_id: str
    concern: str
    decision: DeliveryRouteAction
    rationale: str
    depth: str
    prerequisite_refs: tuple[str, ...]
    risk_level: RiskLevel

    def __post_init__(self) -> None:
        _require_non_empty(self.unit_id, "unit_id")
        _require_non_empty(self.concern, "concern")
        _require_non_empty(self.rationale, "rationale")
        _require_non_empty(self.depth, "depth")
        _require_choice(
            self.decision,
            frozenset({"execute", "skip", "block"}),
            "delivery route decision",
        )
        _require_choice(
            self.risk_level,
            frozenset({"low", "medium", "high", "critical"}),
            "risk level",
        )
        _require_non_empty_entries(self.prerequisite_refs, "prerequisite_refs")


@dataclass(frozen=True, slots=True)
class DeliveryRoutePlan:
    """Versioned adapter route decisions for all units in one objective."""

    route_plan_id: str
    objective_id: str
    adapter_id: str
    unit_ids: tuple[str, ...]
    decisions: tuple[DeliveryRouteDecision, ...]

    def __post_init__(self) -> None:
        _require_non_empty(self.route_plan_id, "route_plan_id")
        _require_non_empty(self.objective_id, "objective_id")
        _require_non_empty(self.adapter_id, "adapter_id")
        if not self.unit_ids:
            raise ValueError("unit_ids must not be empty")
        if not self.decisions:
            raise ValueError("decisions must not be empty")
        _require_non_empty_entries(self.unit_ids, "unit_ids")
        if len(self.unit_ids) != len(set(self.unit_ids)):
            raise ValueError("unit_ids must be unique")
        unknown_unit_ids = {decision.unit_id for decision in self.decisions}.difference(
            self.unit_ids
        )
        if unknown_unit_ids:
            raise ValueError("route decisions must reference declared unit_ids")


@dataclass(frozen=True, slots=True)
class IntegrationVerdict:
    """Evidence-backed objective verdict across all integrated delivery units."""

    status: DeliveryIntegrationStatus
    objective_id: str
    unit_ids: tuple[str, ...]
    requirement_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    blocker_refs: tuple[str, ...]
    residual_risks: tuple[str, ...]
    conditions: tuple[str, ...]
    condition_owner: str | None
    condition_expires_at: str | None
    contract_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_non_empty(self.objective_id, "objective_id")
        _require_choice(
            self.status,
            frozenset({"passed", "failed", "blocked", "conditional"}),
            "delivery integration status",
        )
        for label, values in (
            ("unit_ids", self.unit_ids),
            ("requirement_refs", self.requirement_refs),
            ("evidence_refs", self.evidence_refs),
            ("blocker_refs", self.blocker_refs),
            ("residual_risks", self.residual_risks),
            ("conditions", self.conditions),
            ("contract_refs", self.contract_refs),
        ):
            _require_non_empty_entries(values, label)
        if not self.evidence_refs:
            raise ValueError("evidence_refs must not be empty")
        if self.status == "conditional":
            if not self.conditions:
                raise ValueError("conditional verdict requires conditions")
            if self.condition_owner is None:
                raise ValueError("conditional verdict requires condition_owner")
            if self.condition_expires_at is None:
                raise ValueError("conditional verdict requires condition_expires_at")
        if self.condition_owner is not None:
            _require_non_empty(self.condition_owner, "condition_owner")
        if self.condition_expires_at is not None:
            _require_non_empty(self.condition_expires_at, "condition_expires_at")
