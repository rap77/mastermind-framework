"""Domain security overlay and source-resolution contract tests."""

from datetime import date

import pytest

from mastermind_cli.orchestrator.runtime_contracts.models import (
    SecurityControl,
    SecurityOverlay,
)
from mastermind_cli.orchestrator.runtime_contracts.security_overlays import (
    DomainOverlayDeclaration,
    DomainOverlayRegistry,
    SecuritySource,
    SecuritySourceEscalation,
    SecuritySourceRef,
)


@pytest.mark.parametrize(
    ("domain", "expected_control_ids"),
    [
        (
            "software",
            {
                "software-authentication-authorization",
                "software-input-validation",
                "software-supply-chain",
            },
        ),
        (
            "marketing",
            {
                "marketing-consent-tracking",
                "marketing-customer-data",
                "marketing-third-party-scripts",
            },
        ),
        (
            "finance",
            {
                "finance-transaction-authorization",
                "finance-segregation-of-duties",
                "finance-ledger-integrity",
            },
        ),
    ],
)
def test_default_domain_adapters_resolve_distinct_control_sets(
    domain: str,
    expected_control_ids: set[str],
) -> None:
    """Each built-in domain resolves its own required security controls."""
    resolution = DomainOverlayRegistry().resolve(
        domain=domain,
        jurisdiction="AR",
        as_of=date(2026, 7, 16),
    )

    assert resolution.overlay.domain == domain
    assert {control.control_id for control in resolution.overlay.controls} == (
        expected_control_ids
    )


def test_resolution_retains_exact_source_version_and_jurisdiction() -> None:
    """Resolved controls preserve their source version and jurisdiction context."""
    resolution = DomainOverlayRegistry().resolve(
        domain="finance",
        jurisdiction="AR",
        as_of=date(2026, 7, 16),
    )

    assert resolution.jurisdiction == "AR"
    assert len(resolution.sources) == 1
    source = resolution.sources[0]
    assert source.source_id == "MM-SEC-FINANCE"
    assert source.version == "2026.1"
    assert source.jurisdiction == "GLOBAL"
    assert {control.source_version for control in resolution.overlay.controls} == {
        "MM-SEC-FINANCE@2026.1"
    }


@pytest.mark.parametrize(
    ("sources", "expected_reason"),
    [
        ((), "missing"),
        (
            (
                SecuritySource(
                    source_id="DOMAIN-SOURCE",
                    version="1",
                    authority="Domain owner",
                    jurisdiction="GLOBAL",
                    effective_date=date(2026, 1, 1),
                    review_by=date(2026, 6, 30),
                ),
            ),
            "stale",
        ),
        (
            (
                SecuritySource(
                    source_id="DOMAIN-SOURCE",
                    version="1",
                    authority="Domain owner",
                    jurisdiction="GLOBAL",
                    effective_date=date(2026, 1, 1),
                    review_by=date(2027, 1, 1),
                    contradicts=("DOMAIN-SOURCE-ALT@1",),
                ),
            ),
            "contradictory",
        ),
    ],
)
def test_unusable_sources_raise_typed_escalation(
    sources: tuple[SecuritySource, ...],
    expected_reason: str,
) -> None:
    """Missing, stale, and contradictory sources raise typed escalations."""
    declaration = DomainOverlayDeclaration(
        domain="specialized",
        overlay=SecurityOverlay(
            overlay_id="specialized-security",
            version="1",
            scope="domain",
            domain="specialized",
            controls=(
                SecurityControl(
                    control_id="specialized-access",
                    enforcement="required",
                    source_version="DOMAIN-SOURCE@1",
                ),
            ),
        ),
        source_refs=(SecuritySourceRef("DOMAIN-SOURCE", "1"),),
    )
    registry = DomainOverlayRegistry(
        declarations=(declaration,),
        sources=sources,
    )

    with pytest.raises(SecuritySourceEscalation) as raised:
        registry.resolve(
            domain="specialized",
            jurisdiction="AR",
            as_of=date(2026, 7, 16),
        )

    assert raised.value.reason == expected_reason
    assert raised.value.domain == "specialized"
    assert raised.value.jurisdiction == "AR"
    assert raised.value.source_refs == ("DOMAIN-SOURCE@1",)
