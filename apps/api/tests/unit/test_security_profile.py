"""Security profile composition contract tests."""

import pytest

from mastermind_cli.orchestrator.runtime_contracts.models import (
    ApprovedSecurityException,
    SecurityControl,
    SecurityEnforcement,
    SecurityOverlay,
    SecurityProfile,
)


def _control(
    control_id: str,
    enforcement: SecurityEnforcement,
) -> SecurityControl:
    return SecurityControl(
        control_id=control_id,
        enforcement=enforcement,
        source_version="security-baseline@1",
    )


def test_profile_composition_applies_deterministic_precedence() -> None:
    """More specific overlays deterministically override prior control settings."""
    baseline = SecurityOverlay(
        overlay_id="global-security",
        version="1.0.0",
        scope="global",
        controls=(_control("access-control", "required"),),
    )
    domain = SecurityOverlay(
        overlay_id="finance-security",
        version="1.0.0",
        scope="domain",
        domain="finance",
        controls=(_control("access-control", "mandatory"),),
    )
    jurisdiction_ar = SecurityOverlay(
        overlay_id="argentina-finance",
        version="2026-01",
        scope="jurisdiction",
        jurisdiction="AR",
        controls=(_control("audit-retention", "required"),),
    )
    jurisdiction_uy = SecurityOverlay(
        overlay_id="uruguay-finance",
        version="2026-01",
        scope="jurisdiction",
        jurisdiction="UY",
        controls=(_control("data-residency", "required"),),
    )
    project = SecurityOverlay(
        overlay_id="ledger-project",
        version="3",
        scope="project",
        project_id="project-ledger",
        controls=(_control("audit-retention", "mandatory"),),
    )

    profile = SecurityProfile.compose(
        security_profile_id="security-profile-ledger",
        profile_version="1",
        project_id="project-ledger",
        domain="finance",
        jurisdictions=("UY", "AR"),
        global_baseline=baseline,
        domain_overlay=domain,
        jurisdiction_overlays=(jurisdiction_uy, jurisdiction_ar),
        project_overlay=project,
    )

    assert profile.schema_version == "1.0"
    assert profile.applied_overlay_ids == (
        "global-security",
        "finance-security",
        "argentina-finance",
        "uruguay-finance",
        "ledger-project",
    )
    assert profile.controls == (
        _control("access-control", "mandatory"),
        _control("audit-retention", "mandatory"),
        _control("data-residency", "required"),
    )
    assert profile.source_versions == ("security-baseline@1",)


def test_profile_retains_canonical_security_context_metadata() -> None:
    """Composed profiles preserve the declared security context metadata."""
    baseline = SecurityOverlay(
        overlay_id="global-security",
        version="1.0.0",
        scope="global",
        controls=(_control("access-control", "required"),),
    )

    profile = SecurityProfile.compose(
        security_profile_id="security-profile-ledger",
        profile_version="1",
        project_id="project-ledger",
        domain="finance",
        jurisdictions=("AR",),
        global_baseline=baseline,
        data_classes=("restricted",),
        critical_assets=("asset:ledger",),
        actors=("actor:operator",),
        trust_boundaries=("boundary:public-api",),
        threat_categories=("unauthorized-transaction",),
        control_sets=("finance-baseline",),
        approval_policy="policy-security-assurance",
        risk_thresholds=(("critical", "blocked"),),
    )

    assert profile.data_classes == ("restricted",)
    assert profile.critical_assets == ("asset:ledger",)
    assert profile.actors == ("actor:operator",)
    assert profile.trust_boundaries == ("boundary:public-api",)
    assert profile.threat_categories == ("unauthorized-transaction",)
    assert profile.control_sets == ("finance-baseline",)
    assert profile.approval_policy == "policy-security-assurance"
    assert profile.risk_thresholds == (("critical", "blocked"),)


def test_weaker_overlay_fails_without_approved_exception() -> None:
    """An overlay cannot weaken an existing control without an exception."""
    baseline = SecurityOverlay(
        overlay_id="global-security",
        version="1.0.0",
        scope="global",
        controls=(_control("secrets", "mandatory"),),
    )
    project = SecurityOverlay(
        overlay_id="project-security",
        version="1",
        scope="project",
        project_id="project-a",
        controls=(_control("secrets", "required"),),
    )

    with pytest.raises(
        ValueError,
        match="weaken control 'secrets'.*approved exception",
    ):
        SecurityProfile.compose(
            security_profile_id="security-profile-a",
            profile_version="1",
            project_id="project-a",
            domain="software",
            jurisdictions=(),
            global_baseline=baseline,
            project_overlay=project,
        )


def test_approved_exception_can_explicitly_weaken_a_control() -> None:
    """An approved exception can explicitly reduce one control's enforcement."""
    baseline = SecurityOverlay(
        overlay_id="global-security",
        version="1.0.0",
        scope="global",
        controls=(_control("data-retention", "mandatory"),),
    )
    exception = SecurityOverlay(
        overlay_id="approved-retention-exception",
        version="1",
        scope="exception",
        controls=(_control("data-retention", "required"),),
        approved_exception=ApprovedSecurityException(
            exception_id="exception-123",
            control_ids=("data-retention",),
            rationale="Short-lived migration constraint",
            approved_by="security-review-board",
            approved_at="2026-07-16T00:00:00Z",
            expires_at="2026-08-16T00:00:00Z",
        ),
    )

    profile = SecurityProfile.compose(
        security_profile_id="security-profile-a",
        profile_version="2",
        project_id="project-a",
        domain="software",
        jurisdictions=(),
        global_baseline=baseline,
        approved_exceptions=(exception,),
    )

    assert profile.controls == (_control("data-retention", "required"),)
    assert profile.approved_exception_ids == ("exception-123",)


@pytest.mark.parametrize(
    ("scope", "context"),
    [
        ("domain", {}),
        ("jurisdiction", {}),
        ("project", {}),
        ("exception", {}),
    ],
)
def test_contextual_overlays_require_explicit_scope_metadata(
    scope: str,
    context: dict[str, str],
) -> None:
    """Contextual overlays reject construction without their required scope metadata."""
    with pytest.raises(ValueError, match=f"{scope} overlay"):
        SecurityOverlay(
            overlay_id=f"{scope}-security",
            version="1",
            scope=scope,
            controls=(_control("access-control", "required"),),
            **context,
        )
