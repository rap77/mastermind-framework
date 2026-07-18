"""Integration tests for independent delivery assurance vetoes."""

from dataclasses import replace
from datetime import datetime, timezone

import pytest

from mastermind_cli.orchestrator.runtime_contracts.integration_acceptance import (
    IntegrationAcceptanceEvidence,
    IntegrationAcceptanceService,
)
from mastermind_cli.orchestrator.runtime_contracts.models import ReviewOutcome
from mastermind_cli.orchestrator.runtime_contracts.security_readiness import (
    SecurityReadinessFinding,
    SecurityReadinessPolicy,
    SecurityReadinessVerdict,
)

NOW = datetime(2026, 7, 17, 20, 0, tzinfo=timezone.utc)


@pytest.fixture(scope="session", autouse=True)
def _database_url_for_integration() -> None:
    """Override the suite DB guard because this composition test performs no I/O."""


def _evidence() -> IntegrationAcceptanceEvidence:
    """Return complete evidence with no optional domain-specific lenses."""
    return IntegrationAcceptanceEvidence(
        objective_id="objective-42",
        requirement_refs=("REQ-1",),
        satisfied_requirement_refs=("REQ-1",),
        unit_ids=("unit-1",),
        completed_unit_ids=("unit-1",),
        approved_excluded_unit_ids=(),
        contract_refs=("contract-1",),
        compatible_contract_refs=("contract-1",),
        dependency_refs=(),
        satisfied_dependency_refs=(),
        quality_requirement_refs=(),
        passed_quality_refs=(),
        expected_side_effect_refs=(),
        observed_side_effect_refs=(),
        unsafe_side_effect_refs=(),
        residual_risk_refs=(),
        recorded_residual_risk_refs=(),
        required_approval_refs=(),
        approvals=(),
        evidence_refs=("evidence:objective-42",),
        evaluated_at=NOW,
    )


def _review(*, approved: bool) -> ReviewOutcome:
    """Return an explicit review verdict."""
    return ReviewOutcome(
        performed=True,
        approved=approved,
        findings=() if approved else ("review-defect",),
        risk_flags=() if approved else ("review-risk",),
        recommended_next_action="continue" if approved else "patch",
    )


def _security(*, blocked: bool) -> SecurityReadinessVerdict:
    """Evaluate a real security readiness policy for composition."""
    findings = (
        (
            SecurityReadinessFinding(
                finding_id="SEC-001",
                severity="high",
                status="open",
                evidence_status="passed",
            ),
        )
        if blocked
        else ()
    )
    return SecurityReadinessPolicy().evaluate(findings, (), evaluated_at=NOW)


def test_security_veto_survives_perfect_integration_and_review() -> None:
    """Complete core evidence and review cannot average away security blockers."""
    result = IntegrationAcceptanceService().evaluate(
        _evidence(),
        security_verdict=_security(blocked=True),
        review_outcome=_review(approved=True),
    )

    assert result.verdict.status == "blocked"
    assert result.security_blocker_refs == ("SEC-001",)
    assert result.review_blocker_refs == ()
    assert "security:SEC-001" in result.verdict.blocker_refs


def test_review_veto_survives_perfect_integration_and_security() -> None:
    """Passing security and core evidence cannot average away review blockers."""
    result = IntegrationAcceptanceService().evaluate(
        _evidence(),
        security_verdict=_security(blocked=False),
        review_outcome=_review(approved=False),
    )

    assert result.verdict.status == "blocked"
    assert result.security_blocker_refs == ()
    assert result.review_blocker_refs == ("review-defect",)
    assert "review:review-defect" in result.verdict.blocker_refs


def test_security_and_review_blockers_remain_separate_when_both_fail() -> None:
    """Each assurance authority retains its own blocker namespace and result."""
    result = IntegrationAcceptanceService().evaluate(
        replace(_evidence(), passed_quality_refs=()),
        security_verdict=_security(blocked=True),
        review_outcome=_review(approved=False),
    )

    assert result.verdict.status == "blocked"
    assert result.security_blocker_refs == ("SEC-001",)
    assert result.review_blocker_refs == ("review-defect",)
    assert result.security_verdict.status == "blocked"
    assert result.review_outcome.approved is False
