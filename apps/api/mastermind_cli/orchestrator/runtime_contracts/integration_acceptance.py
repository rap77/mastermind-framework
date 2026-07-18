"""Pure objective-wide integration acceptance and assurance composition."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from .delivery_models import DeliveryIntegrationStatus, IntegrationVerdict
from .models import ApprovalRecord, ReviewOutcome
from .security_readiness import SecurityReadinessVerdict

AcceptanceCategory = Literal[
    "requirements",
    "units",
    "contracts",
    "dependencies",
    "quality",
    "side_effects",
    "residual_risks",
    "approvals",
]
AcceptanceCheckStatus = Literal["passed", "failed", "blocked", "not_applicable"]


def _require_text(value: str, label: str) -> None:
    if not value.strip():
        raise ValueError(f"{label} must not be empty")


def _require_refs(values: tuple[str, ...], label: str) -> None:
    if any(not value.strip() for value in values):
        raise ValueError(f"{label} entries must not be empty")
    if len(values) != len(set(values)):
        raise ValueError(f"{label} entries must be unique")


def _require_aware(value: datetime, label: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{label} must be timezone-aware")


def _parse_timestamp(value: str, label: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{label} must be an ISO datetime") from exc
    _require_aware(parsed, label)
    return parsed


@dataclass(frozen=True, slots=True)
class ConditionalAcceptanceTerms:
    """Accountable, explicit, expiring terms for conditional acceptance."""

    owner: str
    conditions: tuple[str, ...]
    expires_at: datetime

    def __post_init__(self) -> None:
        _require_text(self.owner, "owner")
        if not self.conditions:
            raise ValueError("conditions must not be empty")
        _require_refs(self.conditions, "conditions")
        _require_aware(self.expires_at, "expires_at")


@dataclass(frozen=True, slots=True)
class IntegrationAcceptanceEvidence:
    """Immutable objective evidence supplied to the acceptance composer."""

    objective_id: str
    requirement_refs: tuple[str, ...]
    satisfied_requirement_refs: tuple[str, ...]
    unit_ids: tuple[str, ...]
    completed_unit_ids: tuple[str, ...]
    approved_excluded_unit_ids: tuple[str, ...]
    contract_refs: tuple[str, ...]
    compatible_contract_refs: tuple[str, ...]
    dependency_refs: tuple[str, ...]
    satisfied_dependency_refs: tuple[str, ...]
    quality_requirement_refs: tuple[str, ...]
    passed_quality_refs: tuple[str, ...]
    expected_side_effect_refs: tuple[str, ...]
    observed_side_effect_refs: tuple[str, ...]
    unsafe_side_effect_refs: tuple[str, ...]
    residual_risk_refs: tuple[str, ...]
    recorded_residual_risk_refs: tuple[str, ...]
    required_approval_refs: tuple[str, ...]
    approvals: tuple[ApprovalRecord, ...]
    evidence_refs: tuple[str, ...]
    evaluated_at: datetime

    def __post_init__(self) -> None:
        _require_text(self.objective_id, "objective_id")
        if not self.evidence_refs:
            raise ValueError("evidence_refs must not be empty")
        for label, values in (
            ("requirement_refs", self.requirement_refs),
            ("satisfied_requirement_refs", self.satisfied_requirement_refs),
            ("unit_ids", self.unit_ids),
            ("completed_unit_ids", self.completed_unit_ids),
            ("approved_excluded_unit_ids", self.approved_excluded_unit_ids),
            ("contract_refs", self.contract_refs),
            ("compatible_contract_refs", self.compatible_contract_refs),
            ("dependency_refs", self.dependency_refs),
            ("satisfied_dependency_refs", self.satisfied_dependency_refs),
            ("quality_requirement_refs", self.quality_requirement_refs),
            ("passed_quality_refs", self.passed_quality_refs),
            ("expected_side_effect_refs", self.expected_side_effect_refs),
            ("observed_side_effect_refs", self.observed_side_effect_refs),
            ("unsafe_side_effect_refs", self.unsafe_side_effect_refs),
            ("residual_risk_refs", self.residual_risk_refs),
            ("recorded_residual_risk_refs", self.recorded_residual_risk_refs),
            ("required_approval_refs", self.required_approval_refs),
            ("evidence_refs", self.evidence_refs),
        ):
            _require_refs(values, label)
        _require_aware(self.evaluated_at, "evaluated_at")
        self._require_subset(
            self.satisfied_requirement_refs,
            self.requirement_refs,
            "satisfied_requirement_refs",
        )
        self._require_subset(
            self.completed_unit_ids, self.unit_ids, "completed_unit_ids"
        )
        self._require_subset(
            self.approved_excluded_unit_ids,
            self.unit_ids,
            "approved_excluded_unit_ids",
        )
        if set(self.completed_unit_ids) & set(self.approved_excluded_unit_ids):
            raise ValueError("Completed and excluded units must not overlap")
        self._require_subset(
            self.compatible_contract_refs,
            self.contract_refs,
            "compatible_contract_refs",
        )
        self._require_subset(
            self.satisfied_dependency_refs,
            self.dependency_refs,
            "satisfied_dependency_refs",
        )
        self._require_subset(
            self.passed_quality_refs,
            self.quality_requirement_refs,
            "passed_quality_refs",
        )
        self._require_subset(
            self.observed_side_effect_refs,
            self.expected_side_effect_refs,
            "observed_side_effect_refs",
        )
        self._require_subset(
            self.unsafe_side_effect_refs,
            self.observed_side_effect_refs,
            "unsafe_side_effect_refs",
        )
        self._require_subset(
            self.recorded_residual_risk_refs,
            self.residual_risk_refs,
            "recorded_residual_risk_refs",
        )
        approval_ids = tuple(approval.approval_id for approval in self.approvals)
        _require_refs(approval_ids, "approval IDs")

    @staticmethod
    def _require_subset(
        observed: tuple[str, ...], declared: tuple[str, ...], label: str
    ) -> None:
        """Reject observations that are outside their declared acceptance scope."""
        if not set(observed).issubset(declared):
            raise ValueError(f"{label} must reference declared scope")


@dataclass(frozen=True, slots=True)
class AcceptanceCheckResult:
    """One explicit acceptance lens with independent applicability and blockers."""

    category: AcceptanceCategory
    status: AcceptanceCheckStatus
    required_refs: tuple[str, ...]
    satisfied_refs: tuple[str, ...]
    excluded_refs: tuple[str, ...]
    blocker_refs: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class IntegrationAcceptanceResult:
    """Composed verdict retaining independent security and review authorities."""

    verdict: IntegrationVerdict
    checks: tuple[AcceptanceCheckResult, ...]
    security_verdict: SecurityReadinessVerdict
    review_outcome: ReviewOutcome
    security_blocker_refs: tuple[str, ...]
    review_blocker_refs: tuple[str, ...]


class IntegrationAcceptanceService:
    """Compose deterministic acceptance checks without scoring or averaging vetoes."""

    def evaluate(
        self,
        evidence: IntegrationAcceptanceEvidence,
        *,
        security_verdict: SecurityReadinessVerdict,
        review_outcome: ReviewOutcome,
        conditional_terms: ConditionalAcceptanceTerms | None = None,
    ) -> IntegrationAcceptanceResult:
        """Evaluate core evidence and preserve security and review blockers."""
        checks = self._checks(evidence)
        failed_checks = tuple(check for check in checks if check.status == "failed")
        approval_blockers = tuple(
            blocker
            for check in checks
            if check.category == "approvals"
            for blocker in check.blocker_refs
        )
        security_blockers = security_verdict.blocking_finding_ids
        review_blockers = self._review_blockers(review_outcome)
        blocker_refs = tuple(
            [
                f"{check.category}:{blocker}"
                for check in checks
                for blocker in check.blocker_refs
            ]
            + [f"security:{blocker}" for blocker in security_blockers]
            + [f"review:{blocker}" for blocker in review_blockers]
        )

        status: DeliveryIntegrationStatus
        if security_blockers or review_blockers or approval_blockers:
            status = "blocked"
        elif failed_checks:
            status = "failed"
        elif conditional_terms is not None:
            if conditional_terms.expires_at <= evidence.evaluated_at:
                raise ValueError("conditional expiry must be in the future")
            status = "conditional"
        else:
            status = "passed"

        if status == "conditional":
            if conditional_terms is None:
                raise ValueError("conditional verdict requires terms")
            conditions = conditional_terms.conditions
            condition_owner = conditional_terms.owner
            condition_expires_at = conditional_terms.expires_at.isoformat()
        else:
            conditions = ()
            condition_owner = None
            condition_expires_at = None
        verdict = IntegrationVerdict(
            status=status,
            objective_id=evidence.objective_id,
            unit_ids=evidence.unit_ids,
            requirement_refs=evidence.requirement_refs,
            evidence_refs=evidence.evidence_refs,
            blocker_refs=blocker_refs,
            residual_risks=evidence.residual_risk_refs,
            conditions=conditions,
            condition_owner=condition_owner,
            condition_expires_at=condition_expires_at,
            contract_refs=evidence.contract_refs,
        )
        return IntegrationAcceptanceResult(
            verdict=verdict,
            checks=checks,
            security_verdict=security_verdict,
            review_outcome=review_outcome,
            security_blocker_refs=security_blockers,
            review_blocker_refs=review_blockers,
        )

    def _checks(
        self, evidence: IntegrationAcceptanceEvidence
    ) -> tuple[AcceptanceCheckResult, ...]:
        """Build all universal checks in stable canonical order."""
        unit_satisfied = tuple(
            unit_id
            for unit_id in evidence.unit_ids
            if unit_id in evidence.completed_unit_ids
            or unit_id in evidence.approved_excluded_unit_ids
        )
        approved = tuple(
            approval.approval_id
            for approval in evidence.approvals
            if self._approval_is_active(approval, evidence.evaluated_at)
        )
        return (
            self._coverage(
                "requirements",
                evidence.requirement_refs,
                evidence.satisfied_requirement_refs,
            ),
            self._coverage(
                "units",
                evidence.unit_ids,
                unit_satisfied,
                excluded=evidence.approved_excluded_unit_ids,
            ),
            self._coverage(
                "contracts", evidence.contract_refs, evidence.compatible_contract_refs
            ),
            self._coverage(
                "dependencies",
                evidence.dependency_refs,
                evidence.satisfied_dependency_refs,
            ),
            self._coverage(
                "quality",
                evidence.quality_requirement_refs,
                evidence.passed_quality_refs,
            ),
            self._coverage(
                "side_effects",
                evidence.expected_side_effect_refs,
                evidence.observed_side_effect_refs,
                extra_blockers=evidence.unsafe_side_effect_refs,
            ),
            self._coverage(
                "residual_risks",
                evidence.residual_risk_refs,
                evidence.recorded_residual_risk_refs,
            ),
            self._coverage(
                "approvals",
                evidence.required_approval_refs,
                approved,
                blocking=True,
            ),
        )

    @staticmethod
    def _coverage(
        category: AcceptanceCategory,
        required: tuple[str, ...],
        satisfied: tuple[str, ...],
        *,
        excluded: tuple[str, ...] = (),
        extra_blockers: tuple[str, ...] = (),
        blocking: bool = False,
    ) -> AcceptanceCheckResult:
        """Evaluate set coverage while retaining declared order and applicability."""
        blockers = tuple(
            dict.fromkeys(item for item in required if item not in satisfied)
        ) + tuple(
            item for item in extra_blockers if item not in required or item in satisfied
        )
        if blockers:
            status: AcceptanceCheckStatus = "blocked" if blocking else "failed"
        elif not required:
            status = "not_applicable"
        else:
            status = "passed"
        return AcceptanceCheckResult(
            category=category,
            status=status,
            required_refs=required,
            satisfied_refs=satisfied,
            excluded_refs=excluded,
            blocker_refs=tuple(dict.fromkeys(blockers)),
        )

    @staticmethod
    def _approval_is_active(approval: ApprovalRecord, evaluated_at: datetime) -> bool:
        """Return whether an explicit approval remains valid at evaluation time."""
        if approval.decision != "approved":
            return False
        if approval.expires_at is None:
            return True
        return (
            _parse_timestamp(approval.expires_at, "approval expires_at") > evaluated_at
        )

    @staticmethod
    def _review_blockers(review_outcome: ReviewOutcome) -> tuple[str, ...]:
        """Project only review authority blockers, without converting them to a score."""
        if not review_outcome.performed:
            return ("not-performed",)
        if review_outcome.approved:
            return ()
        return review_outcome.findings or ("not-approved",)
