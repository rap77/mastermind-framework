"""Fail-closed security readiness and expiring risk-acceptance contracts."""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Literal

from mastermind_cli.experience.redaction import redact_pii

SecuritySeverity = Literal["critical", "high", "medium", "low"]
SecurityFindingStatus = Literal["open", "closed", "accepted", "reopened"]
RiskAcceptanceStatus = Literal["proposed", "approved", "active", "expired", "reopened"]
SecurityReadinessStatus = Literal["ready", "blocked"]

_SEVERITIES = frozenset({"critical", "high", "medium", "low"})
_FINDING_STATUSES = frozenset({"open", "closed", "accepted", "reopened"})
_EVIDENCE_STATUSES = frozenset(
    {"passed", "failed", "inconclusive", "skipped", "missing", "not_applicable"}
)
_ACCEPTANCE_STATUSES = frozenset(
    {"proposed", "approved", "active", "expired", "reopened"}
)
_READINESS_STATUSES = frozenset({"ready", "blocked"})
_SAFE_REFERENCE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/#-]{0,254}\Z")


def _require_text(value: str, label: str) -> None:
    if not value.strip():
        raise ValueError(f"{label} must not be empty")


def _require_safe_text(value: str, label: str) -> None:
    _require_text(value, label)
    if redact_pii(value) != value:
        raise ValueError(f"{label} must not contain sensitive values")


def _require_safe_references(values: tuple[str, ...], label: str) -> None:
    if not values:
        raise ValueError(f"{label} must not be empty")
    if any(
        not _SAFE_REFERENCE.fullmatch(value) or redact_pii(value) != value
        for value in values
    ):
        raise ValueError(f"{label} must contain only safe opaque references")


def _require_aware(value: datetime, label: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{label} must be timezone-aware")


@dataclass(frozen=True, slots=True)
class HumanRiskAuthority:
    """Explicit human principal and delegated risk authority."""

    principal_id: str
    authority: str
    is_human: bool = True

    def __post_init__(self) -> None:
        _require_safe_references((self.principal_id,), "principal_id")
        _require_text(self.authority, "authority")


@dataclass(frozen=True, slots=True)
class SecurityReadinessFinding:
    """Minimal finding projection; verifier evidence remains immutable."""

    finding_id: str
    severity: SecuritySeverity
    status: SecurityFindingStatus
    evidence_status: str
    risk_acceptance_id: str | None = None

    def __post_init__(self) -> None:
        _require_safe_references((self.finding_id,), "finding_id")
        if self.severity not in _SEVERITIES:
            raise ValueError(f"Unsupported severity: {self.severity}")
        if self.status not in _FINDING_STATUSES:
            raise ValueError(f"Unsupported finding status: {self.status}")
        if self.evidence_status not in _EVIDENCE_STATUSES:
            raise ValueError(f"Unsupported evidence status: {self.evidence_status}")
        if self.status == "accepted" and not self.risk_acceptance_id:
            raise ValueError("Accepted finding requires risk_acceptance_id")
        if self.status != "accepted" and self.risk_acceptance_id is not None:
            raise ValueError("Only accepted findings may reference risk acceptance")


@dataclass(frozen=True, slots=True)
class RiskAcceptanceRecord:
    """Auditable metadata for one exactly scoped, expiring risk decision."""

    acceptance_id: str
    finding_id: str
    decision: Literal["accept"]
    status: RiskAcceptanceStatus
    owner: HumanRiskAuthority
    scope: tuple[str, ...]
    rationale: str
    compensating_controls: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    proposed_at: datetime
    review_at: datetime
    expires_at: datetime
    approved_by: HumanRiskAuthority | None = None
    approved_at: datetime | None = None
    activated_at: datetime | None = None
    expired_at: datetime | None = None
    reopened_at: datetime | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "scope", tuple(self.scope))
        object.__setattr__(
            self, "compensating_controls", tuple(self.compensating_controls)
        )
        object.__setattr__(self, "evidence_refs", tuple(self.evidence_refs))
        _require_safe_references((self.acceptance_id,), "acceptance_id")
        _require_safe_references((self.finding_id,), "finding_id")
        if self.status not in _ACCEPTANCE_STATUSES:
            raise ValueError(f"Unsupported acceptance status: {self.status}")
        if self.decision != "accept":
            raise ValueError(f"Unsupported risk decision: {self.decision}")
        if not self.owner.is_human or self.owner.authority != "risk-owner":
            raise ValueError("Risk owner requires human authority")
        if self.scope != (self.finding_id,):
            raise ValueError("Risk acceptance scope must exactly match its finding")
        _require_safe_text(self.rationale, "rationale")
        _require_safe_references(self.compensating_controls, "compensating_controls")
        _require_safe_references(self.evidence_refs, "evidence_refs")
        for label, timestamp in (
            ("proposed_at", self.proposed_at),
            ("review_at", self.review_at),
            ("expires_at", self.expires_at),
        ):
            _require_aware(timestamp, label)
        if self.review_at <= self.proposed_at:
            raise ValueError("review_at must be after proposed_at")
        if self.expires_at <= self.review_at:
            raise ValueError("expires_at must be after review_at")
        if (self.approved_by is None) != (self.approved_at is None):
            raise ValueError(
                "Approval authority and timestamp must be recorded together"
            )
        if self.approved_by is not None and (
            not self.approved_by.is_human
            or self.approved_by.authority != "security-approver"
        ):
            raise ValueError("Risk approver requires human authority")
        for label, optional_timestamp in (
            ("approved_at", self.approved_at),
            ("activated_at", self.activated_at),
            ("expired_at", self.expired_at),
            ("reopened_at", self.reopened_at),
        ):
            if optional_timestamp is not None:
                _require_aware(optional_timestamp, label)
        self._validate_lifecycle_metadata()

    def _validate_lifecycle_metadata(self) -> None:
        """Reject records whose metadata does not prove their lifecycle status."""
        approval = self.approved_by is not None and self.approved_at is not None
        if self.status == "proposed":
            if any(
                value is not None
                for value in (
                    self.approved_by,
                    self.approved_at,
                    self.activated_at,
                    self.expired_at,
                    self.reopened_at,
                )
            ):
                raise ValueError(
                    "proposed status cannot contain later lifecycle metadata"
                )
            return
        if not approval:
            raise ValueError(f"{self.status} status requires approval metadata")
        if self.approved_at is not None and self.approved_at < self.proposed_at:
            raise ValueError("approved_at must not precede proposed_at")
        if self.status == "approved":
            if any(
                value is not None
                for value in (self.activated_at, self.expired_at, self.reopened_at)
            ):
                raise ValueError(
                    "approved status cannot contain later lifecycle metadata"
                )
            return
        if self.activated_at is None:
            raise ValueError(f"{self.status} status requires activated_at")
        if self.approved_at is not None and self.activated_at < self.approved_at:
            raise ValueError("activated_at must not precede approved_at")
        if self.status == "active":
            if self.expired_at is not None or self.reopened_at is not None:
                raise ValueError(
                    "active status cannot contain later lifecycle metadata"
                )
            return
        if self.expired_at is None:
            raise ValueError(f"{self.status} status requires expired_at")
        if self.expired_at < self.expires_at:
            raise ValueError("expired_at must not precede expires_at")
        if self.status == "expired":
            if self.reopened_at is not None:
                raise ValueError("expired status cannot contain reopened_at")
            return
        if self.reopened_at is None:
            raise ValueError("reopened status requires reopened_at")
        if self.reopened_at < self.expired_at:
            raise ValueError("reopened_at must not precede expired_at")


@dataclass(frozen=True, slots=True)
class SecurityReadinessVerdict:
    """Structured independent readiness result with explicit blockers."""

    policy_id: str
    status: SecurityReadinessStatus
    blocking_finding_ids: tuple[str, ...]
    accepted_finding_ids: tuple[str, ...]
    reasons: tuple[str, ...]
    evaluated_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "blocking_finding_ids", tuple(self.blocking_finding_ids)
        )
        object.__setattr__(
            self, "accepted_finding_ids", tuple(self.accepted_finding_ids)
        )
        object.__setattr__(self, "reasons", tuple(self.reasons))
        _require_text(self.policy_id, "policy_id")
        if self.status not in _READINESS_STATUSES:
            raise ValueError(f"Unsupported readiness status: {self.status}")
        _require_aware(self.evaluated_at, "evaluated_at")
        if self.status == "ready" and self.blocking_finding_ids:
            raise ValueError("Ready verdict cannot contain blocking findings")


@dataclass(frozen=True, slots=True)
class SecurityReadinessPolicy:
    """Apply evidence and severity vetoes without mutating profile policy."""

    policy_id: str = "policy-security-assurance"
    veto_severities: frozenset[str] = frozenset({"critical", "high"})
    acceptable_severities: frozenset[str] = frozenset({"medium"})

    def __post_init__(self) -> None:
        object.__setattr__(self, "veto_severities", frozenset(self.veto_severities))
        object.__setattr__(
            self, "acceptable_severities", frozenset(self.acceptable_severities)
        )
        _require_text(self.policy_id, "policy_id")
        unknown = (self.veto_severities | self.acceptable_severities) - _SEVERITIES
        if unknown:
            raise ValueError(f"Unsupported policy severity: {sorted(unknown)}")
        if self.veto_severities & self.acceptable_severities:
            raise ValueError("Veto and acceptable severities must not overlap")
        if "critical" not in self.veto_severities:
            raise ValueError("Critical severity must remain a readiness veto")

    def evaluate(
        self,
        findings: tuple[SecurityReadinessFinding, ...],
        acceptances: tuple[RiskAcceptanceRecord, ...],
        *,
        evaluated_at: datetime,
    ) -> SecurityReadinessVerdict:
        """Evaluate current state; stale or malformed acceptance fails closed."""
        _require_aware(evaluated_at, "evaluated_at")
        acceptance_by_id = {
            acceptance.acceptance_id: acceptance for acceptance in acceptances
        }
        if len(acceptance_by_id) != len(acceptances):
            raise ValueError("Duplicate risk acceptance IDs are not allowed")

        blockers: list[str] = []
        accepted: list[str] = []
        reasons: list[str] = []
        for finding in sorted(findings, key=lambda item: item.finding_id):
            if finding.evidence_status != "passed":
                blockers.append(finding.finding_id)
                reasons.append(
                    f"{finding.finding_id}:evidence:{finding.evidence_status}"
                )
                continue
            if finding.status == "closed":
                continue
            if finding.severity in self.veto_severities:
                blockers.append(finding.finding_id)
                reasons.append(
                    f"{finding.finding_id}:{finding.severity}:{finding.status}"
                )
                continue
            if finding.severity not in self.acceptable_severities:
                continue
            acceptance = (
                acceptance_by_id.get(finding.risk_acceptance_id)
                if finding.risk_acceptance_id
                else None
            )
            if not self._permits(finding, acceptance, evaluated_at):
                blockers.append(finding.finding_id)
                reasons.append(f"{finding.finding_id}:acceptance:not-active")
                continue
            accepted.append(finding.finding_id)

        return SecurityReadinessVerdict(
            policy_id=self.policy_id,
            status="blocked" if blockers else "ready",
            blocking_finding_ids=tuple(blockers),
            accepted_finding_ids=tuple(accepted),
            reasons=tuple(reasons),
            evaluated_at=evaluated_at,
        )

    @staticmethod
    def _permits(
        finding: SecurityReadinessFinding,
        acceptance: RiskAcceptanceRecord | None,
        evaluated_at: datetime,
    ) -> bool:
        return bool(
            finding.status == "accepted"
            and acceptance is not None
            and acceptance.status == "active"
            and acceptance.finding_id == finding.finding_id
            and acceptance.scope == (finding.finding_id,)
            and acceptance.activated_at is not None
            and acceptance.activated_at <= evaluated_at < acceptance.expires_at
        )


class RiskAcceptanceService:
    """Perform the only valid medium-risk acceptance lifecycle transitions."""

    def propose(
        self,
        *,
        acceptance_id: str,
        finding: SecurityReadinessFinding,
        owner: HumanRiskAuthority,
        scope: tuple[str, ...],
        rationale: str,
        compensating_controls: tuple[str, ...],
        evidence_refs: tuple[str, ...],
        review_at: datetime | None,
        expires_at: datetime | None,
        proposed_at: datetime,
    ) -> RiskAcceptanceRecord:
        """Propose an exactly scoped acceptance for an open medium finding."""
        if finding.severity != "medium" or finding.status not in {"open", "reopened"}:
            raise ValueError("Only open or reopened medium findings may be accepted")
        if review_at is None:
            raise ValueError("review_at is required")
        if expires_at is None:
            raise ValueError("expires_at is required")
        return RiskAcceptanceRecord(
            acceptance_id=acceptance_id,
            finding_id=finding.finding_id,
            decision="accept",
            status="proposed",
            owner=owner,
            scope=scope,
            rationale=rationale,
            compensating_controls=compensating_controls,
            evidence_refs=evidence_refs,
            proposed_at=proposed_at,
            review_at=review_at,
            expires_at=expires_at,
        )

    def approve(
        self,
        acceptance: RiskAcceptanceRecord,
        *,
        approved_by: HumanRiskAuthority,
        approved_at: datetime,
    ) -> RiskAcceptanceRecord:
        """Record explicit human approval for a proposed acceptance."""
        self._require_transition(acceptance, "proposed", "approved")
        if approved_at < acceptance.proposed_at or approved_at >= acceptance.expires_at:
            raise ValueError("approved_at must be within the acceptance lifetime")
        return replace(
            acceptance,
            status="approved",
            approved_by=approved_by,
            approved_at=approved_at,
        )

    def activate(
        self,
        acceptance: RiskAcceptanceRecord,
        *,
        activated_at: datetime,
    ) -> RiskAcceptanceRecord:
        """Activate an approved acceptance before its expiry."""
        self._require_transition(acceptance, "approved", "active")
        if acceptance.approved_at is None:
            raise ValueError("Approved acceptance is missing approval timestamp")
        if (
            activated_at < acceptance.approved_at
            or activated_at >= acceptance.expires_at
        ):
            raise ValueError("activated_at must be within the approved lifetime")
        return replace(acceptance, status="active", activated_at=activated_at)

    def apply_active(
        self,
        acceptance: RiskAcceptanceRecord,
        finding: SecurityReadinessFinding,
        *,
        applied_at: datetime,
    ) -> SecurityReadinessFinding:
        """Link active acceptance without changing verifier evidence."""
        _require_aware(applied_at, "applied_at")
        if acceptance.status != "active":
            raise ValueError("Only active acceptance may be applied")
        if (
            acceptance.activated_at is None
            or applied_at < acceptance.activated_at
            or applied_at >= acceptance.expires_at
        ):
            raise ValueError("Active acceptance must be applied before expires_at")
        if finding.finding_id != acceptance.finding_id:
            raise ValueError("Acceptance scope must exactly match the finding")
        if finding.severity != "medium" or finding.status not in {"open", "reopened"}:
            raise ValueError("Only open or reopened medium findings may be accepted")
        return replace(
            finding,
            status="accepted",
            risk_acceptance_id=acceptance.acceptance_id,
        )

    def expire(
        self,
        acceptance: RiskAcceptanceRecord,
        *,
        expired_at: datetime,
    ) -> RiskAcceptanceRecord:
        """Expire an active acceptance only at or after its fixed expiry."""
        self._require_transition(acceptance, "active", "expired")
        if expired_at < acceptance.expires_at:
            raise ValueError("Acceptance cannot expire before expires_at")
        return replace(acceptance, status="expired", expired_at=expired_at)

    def reopen(
        self,
        acceptance: RiskAcceptanceRecord,
        finding: SecurityReadinessFinding,
    ) -> tuple[RiskAcceptanceRecord, SecurityReadinessFinding]:
        """Reopen an expired acceptance and its exactly scoped finding."""
        self._require_transition(acceptance, "expired", "reopened")
        if finding.finding_id != acceptance.finding_id:
            raise ValueError("Acceptance scope must exactly match the finding")
        if (
            finding.status != "accepted"
            or finding.risk_acceptance_id != acceptance.acceptance_id
        ):
            raise ValueError(
                "Finding must reference the expired active risk acceptance"
            )
        if acceptance.expired_at is None:
            raise ValueError("Expired acceptance is missing expiry timestamp")
        return (
            replace(
                acceptance,
                status="reopened",
                reopened_at=acceptance.expired_at,
            ),
            replace(finding, status="reopened", risk_acceptance_id=None),
        )

    def expire_and_reopen(
        self,
        acceptance: RiskAcceptanceRecord,
        finding: SecurityReadinessFinding,
        *,
        evaluated_at: datetime,
    ) -> tuple[RiskAcceptanceRecord, SecurityReadinessFinding]:
        """Atomically project expiry into a reopened acceptance and finding."""
        expired = self.expire(acceptance, expired_at=evaluated_at)
        return self.reopen(expired, finding)

    @staticmethod
    def _require_transition(
        acceptance: RiskAcceptanceRecord,
        expected: RiskAcceptanceStatus,
        target: RiskAcceptanceStatus,
    ) -> None:
        if acceptance.status != expected:
            raise ValueError(f"Invalid transition: {acceptance.status} -> {target}")
