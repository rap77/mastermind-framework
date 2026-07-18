"""Unit tests for objective-wide integration acceptance composition."""

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
from typing import Any, Literal, cast

import pytest

from mastermind_cli.orchestrator import runtime_contracts
from mastermind_cli.orchestrator.runtime_contracts.integration_acceptance import (
    ConditionalAcceptanceTerms,
    IntegrationAcceptanceEvidence,
    IntegrationAcceptanceService,
)
from mastermind_cli.orchestrator.runtime_contracts.models import (
    ApprovalRecord,
    ReviewOutcome,
)
from mastermind_cli.orchestrator.runtime_contracts.security_readiness import (
    SecurityReadinessVerdict,
)

NOW = datetime(2026, 7, 17, 20, 0, tzinfo=timezone.utc)


def _approval(
    *,
    decision: Literal[
        "approved", "changes_requested", "rejected", "expired"
    ] = "approved",
) -> ApprovalRecord:
    """Return one run approval applicable to the acceptance evidence."""
    return ApprovalRecord(
        approval_id="approval:final",
        scope="run",
        decision=decision,
        actor="human:delivery-approver",
        rationale="Objective evidence was reviewed.",
        artifact_versions=("artifact:handbook@1",),
        decided_at=NOW.isoformat(),
        expires_at=(NOW + timedelta(days=7)).isoformat(),
    )


def _evidence() -> IntegrationAcceptanceEvidence:
    """Return complete, passing integration evidence across all core lenses."""
    return IntegrationAcceptanceEvidence(
        objective_id="objective-42",
        requirement_refs=("REQ-1", "REQ-2"),
        satisfied_requirement_refs=("REQ-1", "REQ-2"),
        unit_ids=("unit-outline", "unit-handbook"),
        completed_unit_ids=("unit-outline", "unit-handbook"),
        approved_excluded_unit_ids=(),
        contract_refs=("contract:outline", "contract:handbook"),
        compatible_contract_refs=("contract:outline", "contract:handbook"),
        dependency_refs=("dependency:editorial",),
        satisfied_dependency_refs=("dependency:editorial",),
        quality_requirement_refs=("quality:accuracy",),
        passed_quality_refs=("quality:accuracy",),
        expected_side_effect_refs=("side-effect:publish",),
        observed_side_effect_refs=("side-effect:publish",),
        unsafe_side_effect_refs=(),
        residual_risk_refs=("risk:schedule",),
        recorded_residual_risk_refs=("risk:schedule",),
        required_approval_refs=("approval:final",),
        approvals=(_approval(),),
        evidence_refs=("evidence:unit-outline", "evidence:unit-handbook"),
        evaluated_at=NOW,
    )


def _security(
    *, status: Literal["ready", "blocked"] = "ready"
) -> SecurityReadinessVerdict:
    """Return an injectable security verdict."""
    blockers = ("SEC-001",) if status == "blocked" else ()
    return SecurityReadinessVerdict(
        policy_id="policy-security-assurance",
        status=status,
        blocking_finding_ids=blockers,
        accepted_finding_ids=(),
        reasons=("SEC-001:high:open",) if blockers else (),
        evaluated_at=NOW,
    )


def _review(*, approved: bool = True) -> ReviewOutcome:
    """Return an injectable independent review outcome."""
    return ReviewOutcome(
        performed=True,
        approved=approved,
        findings=() if approved else ("contract_regression",),
        risk_flags=() if approved else ("review_blocker",),
        recommended_next_action="continue" if approved else "patch",
    )


def test_acceptance_contracts_are_exported_and_immutable() -> None:
    """Public evidence and result contracts must be typed immutable values."""
    evidence = _evidence()

    assert (
        runtime_contracts.IntegrationAcceptanceEvidence is IntegrationAcceptanceEvidence
    )
    assert (
        runtime_contracts.IntegrationAcceptanceService is IntegrationAcceptanceService
    )
    with pytest.raises(FrozenInstanceError):
        evidence.objective_id = "changed"  # type: ignore[misc]


def test_passing_verdict_covers_requirements_units_contracts_and_evidence() -> None:
    """A pass must expose traceability and every applicable acceptance lens."""
    result = IntegrationAcceptanceService().evaluate(
        _evidence(), security_verdict=_security(), review_outcome=_review()
    )

    assert result.verdict.status == "passed"
    assert result.verdict.requirement_refs == ("REQ-1", "REQ-2")
    assert result.verdict.unit_ids == ("unit-outline", "unit-handbook")
    assert result.verdict.contract_refs == (
        "contract:outline",
        "contract:handbook",
    )
    assert result.verdict.evidence_refs == (
        "evidence:unit-outline",
        "evidence:unit-handbook",
    )
    assert tuple(check.category for check in result.checks) == (
        "requirements",
        "units",
        "contracts",
        "dependencies",
        "quality",
        "side_effects",
        "residual_risks",
        "approvals",
    )
    assert all(check.status in {"passed", "not_applicable"} for check in result.checks)


@pytest.mark.parametrize(
    ("overrides", "category", "blocker"),
    [
        ({"satisfied_requirement_refs": ("REQ-1",)}, "requirements", "REQ-2"),
        ({"completed_unit_ids": ("unit-outline",)}, "units", "unit-handbook"),
        (
            {"compatible_contract_refs": ("contract:outline",)},
            "contracts",
            "contract:handbook",
        ),
        ({"satisfied_dependency_refs": ()}, "dependencies", "dependency:editorial"),
        ({"passed_quality_refs": ()}, "quality", "quality:accuracy"),
        ({"observed_side_effect_refs": ()}, "side_effects", "side-effect:publish"),
        (
            {"unsafe_side_effect_refs": ("side-effect:publish",)},
            "side_effects",
            "side-effect:publish",
        ),
        ({"recorded_residual_risk_refs": ()}, "residual_risks", "risk:schedule"),
        ({"approvals": ()}, "approvals", "approval:final"),
    ],
)
def test_each_applicable_acceptance_lens_fails_closed(
    overrides: dict[str, object], category: str, blocker: str
) -> None:
    """Missing objective evidence must remain visible in its own lens."""
    evidence = replace(_evidence(), **cast(Any, overrides))

    result = IntegrationAcceptanceService().evaluate(
        evidence, security_verdict=_security(), review_outcome=_review()
    )

    check = next(item for item in result.checks if item.category == category)
    assert result.verdict.status in {"failed", "blocked"}
    assert blocker in check.blocker_refs
    assert f"{category}:{blocker}" in result.verdict.blocker_refs


def test_approved_unit_exclusion_counts_as_complete() -> None:
    """Explicit approved exclusions may satisfy unit completeness."""
    evidence = replace(
        _evidence(),
        completed_unit_ids=("unit-outline",),
        approved_excluded_unit_ids=("unit-handbook",),
    )

    result = IntegrationAcceptanceService().evaluate(
        evidence, security_verdict=_security(), review_outcome=_review()
    )

    unit_check = next(item for item in result.checks if item.category == "units")
    assert unit_check.status == "passed"
    assert result.verdict.status == "passed"


def test_conditional_acceptance_requires_complete_unexpired_terms() -> None:
    """Conditional success must carry accountable conditions and future expiry."""
    terms = ConditionalAcceptanceTerms(
        owner="human:risk-owner",
        conditions=("Revalidate schedule risk before publication",),
        expires_at=NOW + timedelta(days=2),
    )

    result = IntegrationAcceptanceService().evaluate(
        _evidence(),
        security_verdict=_security(),
        review_outcome=_review(),
        conditional_terms=terms,
    )

    assert result.verdict.status == "conditional"
    assert result.verdict.condition_owner == "human:risk-owner"
    assert result.verdict.conditions == terms.conditions
    assert result.verdict.condition_expires_at == terms.expires_at.isoformat()

    with pytest.raises(ValueError, match="future"):
        IntegrationAcceptanceService().evaluate(
            _evidence(),
            security_verdict=_security(),
            review_outcome=_review(),
            conditional_terms=replace(terms, expires_at=NOW),
        )
