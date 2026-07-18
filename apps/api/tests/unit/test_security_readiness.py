"""Security readiness veto and risk-acceptance lifecycle tests."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from mastermind_cli.orchestrator import runtime_contracts
from mastermind_cli.orchestrator.runtime_contracts.security_readiness import (
    HumanRiskAuthority,
    RiskAcceptanceRecord,
    RiskAcceptanceService,
    SecurityReadinessFinding,
    SecurityReadinessPolicy,
    SecurityReadinessVerdict,
)

NOW = datetime(2026, 7, 16, 20, 0, tzinfo=timezone.utc)
OWNER = HumanRiskAuthority(
    principal_id="human:service-owner",
    authority="risk-owner",
)
APPROVER = HumanRiskAuthority(
    principal_id="human:security-approver",
    authority="security-approver",
)


def test_security_readiness_contracts_are_exported() -> None:
    """The runtime-contract package exports the public readiness API."""
    assert runtime_contracts.HumanRiskAuthority is HumanRiskAuthority
    assert runtime_contracts.RiskAcceptanceRecord is RiskAcceptanceRecord
    assert runtime_contracts.SecurityReadinessPolicy is SecurityReadinessPolicy
    assert runtime_contracts.SecurityReadinessVerdict is SecurityReadinessVerdict
    assert runtime_contracts.RiskAcceptanceService is RiskAcceptanceService
    assert runtime_contracts.SecurityReadinessFinding is SecurityReadinessFinding


def _finding(
    *,
    finding_id: str = "SEC-001",
    severity: str = "medium",
    status: str = "open",
    evidence_status: str = "passed",
    risk_acceptance_id: str | None = None,
) -> SecurityReadinessFinding:
    return SecurityReadinessFinding(
        finding_id=finding_id,
        severity=severity,
        status=status,
        evidence_status=evidence_status,
        risk_acceptance_id=risk_acceptance_id,
    )


def _proposed_acceptance(
    service: RiskAcceptanceService,
    finding: SecurityReadinessFinding,
) -> RiskAcceptanceRecord:
    return service.propose(
        acceptance_id="RA-001",
        finding=finding,
        owner=OWNER,
        scope=(finding.finding_id,),
        rationale="Temporary exposure while the replacement control is deployed.",
        compensating_controls=("control:restricted-network-path",),
        evidence_refs=("evidence://security/SEC-001/1",),
        review_at=NOW + timedelta(days=7),
        expires_at=NOW + timedelta(days=30),
        proposed_at=NOW,
    )


def _active_acceptance(
    service: RiskAcceptanceService,
    finding: SecurityReadinessFinding,
) -> RiskAcceptanceRecord:
    proposed = _proposed_acceptance(service, finding)
    approved = service.approve(proposed, approved_by=APPROVER, approved_at=NOW)
    return service.activate(approved, activated_at=NOW)


@pytest.mark.parametrize("severity", ["critical", "high"])
def test_open_critical_and_high_findings_apply_policy_veto(severity: str) -> None:
    """Open critical and high findings always block readiness."""
    finding = _finding(severity=severity)

    verdict = SecurityReadinessPolicy().evaluate((finding,), (), evaluated_at=NOW)

    assert verdict == SecurityReadinessVerdict(
        policy_id="policy-security-assurance",
        status="blocked",
        blocking_finding_ids=("SEC-001",),
        accepted_finding_ids=(),
        reasons=(f"SEC-001:{severity}:open",),
        evaluated_at=NOW,
    )


@pytest.mark.parametrize(
    "evidence_status",
    ["missing", "skipped", "inconclusive", "failed", "not_applicable"],
)
def test_unperformed_or_nonpassing_evidence_remains_blocking(
    evidence_status: str,
) -> None:
    """Non-passing evidence prevents readiness even for low-severity findings."""
    finding = _finding(severity="low", evidence_status=evidence_status)

    verdict = SecurityReadinessPolicy().evaluate((finding,), (), evaluated_at=NOW)

    assert verdict.status == "blocked"
    assert verdict.blocking_finding_ids == (finding.finding_id,)
    assert verdict.reasons == (f"SEC-001:evidence:{evidence_status}",)


def test_closed_finding_without_passing_evidence_remains_blocking() -> None:
    """Closing a finding does not bypass its evidence requirement."""
    finding = _finding(status="closed", evidence_status="missing")

    verdict = SecurityReadinessPolicy().evaluate((finding,), (), evaluated_at=NOW)

    assert verdict.status == "blocked"
    assert verdict.blocking_finding_ids == (finding.finding_id,)


def test_medium_finding_requires_active_exactly_scoped_acceptance() -> None:
    """A medium finding becomes ready only with its active scoped acceptance."""
    service = RiskAcceptanceService()
    finding = _finding()
    acceptance = _active_acceptance(service, finding)
    accepted_finding = service.apply_active(acceptance, finding, applied_at=NOW)

    verdict = SecurityReadinessPolicy().evaluate(
        (accepted_finding,), (acceptance,), evaluated_at=NOW
    )

    assert verdict.status == "ready"
    assert verdict.accepted_finding_ids == (finding.finding_id,)
    assert verdict.blocking_finding_ids == ()


def test_acceptance_requires_human_owner_and_approver_authority() -> None:
    """Risk acceptance requires human actors at proposal and approval stages."""
    service = RiskAcceptanceService()
    finding = _finding()

    with pytest.raises(ValueError, match="human authority"):
        service.propose(
            acceptance_id="RA-001",
            finding=finding,
            owner=replace(OWNER, is_human=False),
            scope=(finding.finding_id,),
            rationale="Temporary exposure while a replacement control is deployed.",
            compensating_controls=("control:restricted-network-path",),
            evidence_refs=("evidence://security/SEC-001/1",),
            review_at=NOW + timedelta(days=7),
            expires_at=NOW + timedelta(days=30),
            proposed_at=NOW,
        )

    proposed = _proposed_acceptance(service, finding)
    with pytest.raises(ValueError, match="human authority"):
        service.approve(
            proposed,
            approved_by=replace(APPROVER, is_human=False),
            approved_at=NOW,
        )


def test_acceptance_requires_exact_scope_rationale_review_and_expiry() -> None:
    """Risk acceptance requires complete scope, rationale, and lifecycle dates."""
    service = RiskAcceptanceService()
    finding = _finding()
    valid = {
        "acceptance_id": "RA-001",
        "finding": finding,
        "owner": OWNER,
        "scope": (finding.finding_id,),
        "rationale": "Temporary exposure while a replacement control is deployed.",
        "compensating_controls": ("control:restricted-network-path",),
        "evidence_refs": ("evidence://security/SEC-001/1",),
        "review_at": NOW + timedelta(days=7),
        "expires_at": NOW + timedelta(days=30),
        "proposed_at": NOW,
    }

    for override, message in (
        ({"scope": ("SEC-OTHER",)}, "exactly match"),
        ({"rationale": " "}, "rationale"),
        ({"review_at": None}, "review_at"),
        ({"expires_at": None}, "expires_at"),
    ):
        with pytest.raises(ValueError, match=message):
            service.propose(**(valid | override))


def test_risk_acceptance_lifecycle_is_strict_and_timestamped() -> None:
    """Valid lifecycle transitions retain their state and timestamp evidence."""
    service = RiskAcceptanceService()
    finding = _finding()
    proposed = _proposed_acceptance(service, finding)
    assert proposed.status == "proposed"

    approved = service.approve(proposed, approved_by=APPROVER, approved_at=NOW)
    assert approved.status == "approved"
    assert approved.decision == "accept"
    assert approved.approved_by == APPROVER
    assert approved.approved_at == NOW

    active = service.activate(approved, activated_at=NOW)
    accepted_finding = service.apply_active(active, finding, applied_at=NOW)
    expired = service.expire(active, expired_at=active.expires_at)
    reopened, reopened_finding = service.reopen(expired, accepted_finding)

    assert active.status == "active"
    assert expired.status == "expired"
    assert reopened.status == "reopened"
    assert reopened_finding.status == "reopened"
    assert reopened_finding.risk_acceptance_id is None


def test_expiry_cannot_reopen_an_unlinked_finding() -> None:
    """Expiry cannot reopen a finding that lacks an active acceptance link."""
    service = RiskAcceptanceService()
    finding = _finding()
    active = _active_acceptance(service, finding)
    expired = service.expire(active, expired_at=active.expires_at)

    with pytest.raises(ValueError, match="active risk acceptance"):
        service.reopen(expired, finding)


def test_expired_acceptance_cannot_be_applied_to_a_finding() -> None:
    """An acceptance cannot be applied at or after its expiry timestamp."""
    service = RiskAcceptanceService()
    finding = _finding()
    active = _active_acceptance(service, finding)

    with pytest.raises(ValueError, match="before expires_at"):
        service.apply_active(active, finding, applied_at=active.expires_at)


def test_invalid_lifecycle_transitions_fail_closed() -> None:
    """Invalid risk-acceptance lifecycle transitions fail closed."""
    service = RiskAcceptanceService()
    finding = _finding()
    proposed = _proposed_acceptance(service, finding)

    with pytest.raises(ValueError, match="proposed -> active"):
        service.activate(proposed, activated_at=NOW)
    with pytest.raises(ValueError, match="proposed -> expired"):
        service.expire(proposed, expired_at=NOW + timedelta(days=30))
    with pytest.raises(ValueError, match="proposed -> reopened"):
        service.reopen(proposed, finding)


def test_expired_acceptance_reopens_finding_and_cannot_permit_readiness() -> None:
    """Expired acceptance reopens the finding and restores the readiness veto."""
    service = RiskAcceptanceService()
    finding = _finding()
    active = _active_acceptance(service, finding)
    accepted_finding = service.apply_active(active, finding, applied_at=NOW)

    expired, reopened_finding = service.expire_and_reopen(
        active,
        accepted_finding,
        evaluated_at=active.expires_at,
    )
    verdict = SecurityReadinessPolicy().evaluate(
        (reopened_finding,), (expired,), evaluated_at=active.expires_at
    )

    assert expired.status == "reopened"
    assert reopened_finding.status == "reopened"
    assert verdict.status == "blocked"
    assert verdict.blocking_finding_ids == (finding.finding_id,)


def test_acceptance_does_not_modify_evidence_or_profile_policy() -> None:
    """Acceptance does not alter evidence status or readiness policy semantics."""
    service = RiskAcceptanceService()
    policy = SecurityReadinessPolicy(policy_id="project-security-policy")
    finding = _finding(evidence_status="passed")
    active = _active_acceptance(service, finding)

    accepted_finding = service.apply_active(active, finding, applied_at=NOW)

    assert accepted_finding.evidence_status == finding.evidence_status
    assert policy.policy_id == "project-security-policy"
    assert policy.acceptable_severities == frozenset({"medium"})


def test_policy_normalizes_mutable_severity_sets() -> None:
    """Policy construction snapshots mutable severity collections."""
    veto_severities = {"critical", "high"}
    acceptable_severities = {"medium"}
    policy = SecurityReadinessPolicy(
        veto_severities=veto_severities,  # type: ignore[arg-type]
        acceptable_severities=acceptable_severities,  # type: ignore[arg-type]
    )

    veto_severities.remove("critical")
    acceptable_severities.add("critical")

    assert policy.veto_severities == frozenset({"critical", "high"})
    assert policy.acceptable_severities == frozenset({"medium"})


def test_acceptance_normalizes_mutable_reference_collections() -> None:
    """Acceptance construction snapshots mutable control and evidence references."""
    service = RiskAcceptanceService()
    controls = ["control:restricted-network-path"]
    evidence = ["evidence://security/SEC-001/1"]

    acceptance = service.propose(
        acceptance_id="RA-001",
        finding=_finding(),
        owner=OWNER,
        scope=("SEC-001",),
        rationale="Temporary exposure while the replacement control is deployed.",
        compensating_controls=controls,  # type: ignore[arg-type]
        evidence_refs=evidence,  # type: ignore[arg-type]
        review_at=NOW + timedelta(days=7),
        expires_at=NOW + timedelta(days=30),
        proposed_at=NOW,
    )
    controls.append("control:mutated")
    evidence.append("evidence://mutated")

    assert acceptance.compensating_controls == ("control:restricted-network-path",)
    assert acceptance.evidence_refs == ("evidence://security/SEC-001/1",)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("severity", "urgent", "severity"),
        ("status", "waived", "finding status"),
        ("evidence_status", "unknown", "evidence status"),
    ],
)
def test_invalid_finding_contract_values_fail_closed(
    field: str,
    value: str,
    message: str,
) -> None:
    """Unsupported finding contract values are rejected before evaluation."""
    with pytest.raises(ValueError, match=message):
        _finding(**{field: value})


def test_invalid_acceptance_status_and_verdict_status_fail_closed() -> None:
    """Unsupported acceptance and verdict values fail closed."""
    service = RiskAcceptanceService()
    proposed = _proposed_acceptance(service, _finding())

    with pytest.raises(ValueError, match="acceptance status"):
        replace(proposed, status="waived")
    with pytest.raises(ValueError, match="risk decision"):
        replace(proposed, decision="waive")
    with pytest.raises(ValueError, match="readiness status"):
        SecurityReadinessVerdict(
            policy_id="policy-security-assurance",
            status="unknown",
            blocking_finding_ids=(),
            accepted_finding_ids=(),
            reasons=(),
            evaluated_at=NOW,
        )


def test_acceptance_status_rejects_missing_lifecycle_metadata() -> None:
    """Approved acceptance state requires its approval metadata."""
    proposed = _proposed_acceptance(RiskAcceptanceService(), _finding())

    with pytest.raises(ValueError, match="approved status requires approval metadata"):
        replace(proposed, status="approved")


def test_acceptance_rejects_secret_like_metadata() -> None:
    """Secret-like acceptance rationale values are rejected."""
    service = RiskAcceptanceService()
    finding = _finding()
    secret = "sk-" + ("a" * 16)

    with pytest.raises(ValueError, match="sensitive values"):
        service.propose(
            acceptance_id="RA-001",
            finding=finding,
            owner=OWNER,
            scope=(finding.finding_id,),
            rationale=f"Temporary workaround {secret}",
            compensating_controls=("control:restricted-network-path",),
            evidence_refs=("evidence://security/SEC-001/1",),
            review_at=NOW + timedelta(days=7),
            expires_at=NOW + timedelta(days=30),
            proposed_at=NOW,
        )
