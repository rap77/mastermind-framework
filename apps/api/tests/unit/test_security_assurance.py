"""Security assurance pass and control-evidence contract tests."""

from __future__ import annotations

from dataclasses import asdict

import pytest

from mastermind_cli.orchestrator import runtime_contracts
from mastermind_cli.orchestrator.runtime_contracts.models import (
    EvidenceRecord,
    SecurityControl,
)
from mastermind_cli.orchestrator.runtime_contracts.security_assurance import (
    ASSURANCE_PASS_RUBRICS,
    ControlEvidenceRequirement,
    ControlEvidenceVerifier,
    ObservedControlEvidence,
    ResidualRiskRecord,
    SecurityAssuranceLoop,
    SecurityAssuranceSnapshot,
)


def _evidence(
    *,
    evidence_id: str = "evidence://control/access-control/1",
    performed: bool = True,
    result: str = "pass",
    limitations: tuple[str, ...] = ("Only the public API was sampled.",),
) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id=evidence_id,
        check_id="access-control",
        performed=performed,
        method="tool",
        result=result,
        summary="Raw scanner output must not enter the assurance verdict.",
        command_or_procedure=None,
        tool=None,
        environment=None,
        exit_status=None,
        artifact_refs=("artifact://security/access-control/1",),
        metrics=(),
        detail_schema_ref=None,
        details_ref="evidence-detail://security/access-control/1",
        limitations=limitations,
        recorded_at="2026-07-16T20:00:00Z",
    )


def _requirement(
    *,
    applicability: str = "applicable",
    rationale: str | None = None,
) -> ControlEvidenceRequirement:
    return ControlEvidenceRequirement(
        control_id="access-control",
        applicability=applicability,
        applicability_rationale=rationale,
        expected_evidence=("automated authorization test",),
        source_version="MM-SEC-SOFTWARE@2026.1",
    )


def _observation(
    evidence: tuple[EvidenceRecord, ...],
) -> ObservedControlEvidence:
    return ObservedControlEvidence(
        control_id="access-control",
        evidence=evidence,
        verification_method="automated-test",
        performed_at="2026-07-16T20:00:00Z",
        verifier="security-assurance",
    )


def _snapshot(
    *,
    critical_assets: tuple[str, ...] = ("asset:customer-records",),
    evidence_passed: bool = True,
) -> SecurityAssuranceSnapshot:
    verifier = ControlEvidenceVerifier()
    evidence = _observation((_evidence(),)) if evidence_passed else None
    verdict = verifier.verify(_requirement(), evidence)
    return SecurityAssuranceSnapshot(
        critical_assets=critical_assets,
        data_classes=("restricted",),
        actors=("actor:operator",),
        trust_boundaries=("boundary:public-api",),
        threats=("threat:unauthorized-access",),
        controls=(
            SecurityControl(
                control_id="access-control",
                enforcement="mandatory",
                source_version="MM-SEC-SOFTWARE@2026.1",
            ),
        ),
        evidence_verdicts=(verdict,),
        residual_risks=(
            ResidualRiskRecord(
                risk_id="risk:unauthorized-access",
                treatment="mitigate",
            ),
        ),
    )


def test_assurance_passes_have_distinct_rubrics_and_bounded_stop_rules() -> None:
    """Assurance passes expose separate criteria and finite retry bounds."""
    assert tuple(rubric.pass_id for rubric in ASSURANCE_PASS_RUBRICS) == (
        "asset",
        "trust-boundary",
        "threat",
        "control",
        "evidence",
        "residual-risk",
    )
    assert len({rubric.rubric_id for rubric in ASSURANCE_PASS_RUBRICS}) == 6
    assert len({rubric.stop_rule for rubric in ASSURANCE_PASS_RUBRICS}) == 6
    assert all(rubric.criteria for rubric in ASSURANCE_PASS_RUBRICS)
    assert all(1 <= rubric.max_iterations <= 3 for rubric in ASSURANCE_PASS_RUBRICS)


def test_security_assurance_contracts_are_exported() -> None:
    """The runtime-contract package exports the public assurance API."""
    assert runtime_contracts.SecurityAssuranceLoop is SecurityAssuranceLoop
    assert runtime_contracts.ControlEvidenceVerifier is ControlEvidenceVerifier
    assert runtime_contracts.ControlEvidenceRequirement is ControlEvidenceRequirement


def test_assurance_loop_retries_only_until_a_pass_satisfies_its_rubric() -> None:
    """A later satisfying snapshot resolves each pending assurance pass."""
    first = _snapshot(critical_assets=())
    second = _snapshot()

    result = SecurityAssuranceLoop().run((first, second))

    assert result.passed is True
    assert result.stopped_at is None
    assert tuple(item.pass_id for item in result.pass_results) == (
        "asset",
        "trust-boundary",
        "threat",
        "control",
        "evidence",
        "residual-risk",
    )
    assert result.pass_results[0].iterations == 2
    assert all(item.passed for item in result.pass_results)


def test_assurance_loop_stops_at_the_pass_iteration_limit() -> None:
    """An unresolved pass stops after its declared iteration limit."""
    asset_rubric = ASSURANCE_PASS_RUBRICS[0]
    snapshots = tuple(
        _snapshot(critical_assets=()) for _ in range(asset_rubric.max_iterations + 2)
    )

    result = SecurityAssuranceLoop().run(snapshots)

    assert result.passed is False
    assert result.stopped_at == "asset"
    assert len(result.pass_results) == 1
    assert result.pass_results[0].iterations == asset_rubric.max_iterations
    assert result.pass_results[0].stop_reason == asset_rubric.stop_rule


def test_evidence_verdict_separates_requirement_observation_and_verdict() -> None:
    """Verdicts retain safe evidence metadata without raw observation content."""
    observed = _evidence()
    observation = _observation((observed,))

    verdict = ControlEvidenceVerifier().verify(_requirement(), observation)

    assert verdict.applicability == "applicable"
    assert verdict.expected_evidence == ("automated authorization test",)
    assert verdict.observed_evidence_refs == (observed.evidence_id,)
    assert verdict.status == "passed"
    assert verdict.passed is True
    assert verdict.verification_method == "automated-test"
    assert verdict.performed_at == "2026-07-16T20:00:00Z"
    assert verdict.verifier == "security-assurance"
    assert verdict.limitations == ("Only the public API was sampled.",)
    assert verdict.source_version == "MM-SEC-SOFTWARE@2026.1"
    serialized = asdict(verdict)
    assert observed.summary not in str(serialized)
    assert observed.details_ref not in str(serialized)


def test_evidence_verdict_redacts_sensitive_limitations() -> None:
    """Sensitive limitation values are redacted from the assurance verdict."""
    secret = "sk-" + ("a" * 16)
    observation = _observation((_evidence(limitations=(f"Scanner exposed {secret}",)),))

    verdict = ControlEvidenceVerifier().verify(_requirement(), observation)

    assert secret not in str(asdict(verdict))
    assert verdict.limitations == ("Scanner exposed [REDACTED_SECRET]",)


def test_not_applicable_requires_a_rationale_and_does_not_claim_compliance() -> None:
    """N/A controls require justification and never count as passing evidence."""
    with pytest.raises(ValueError, match="N/A applicability requires a rationale"):
        _requirement(applicability="not_applicable")

    verdict = ControlEvidenceVerifier().verify(
        _requirement(
            applicability="not_applicable",
            rationale="The project has no externally reachable service.",
        ),
        None,
    )

    assert verdict.status == "not_applicable"
    assert verdict.passed is False
    assert verdict.applicability_rationale == (
        "The project has no externally reachable service."
    )


@pytest.mark.parametrize(
    ("observed", "expected_status"),
    [
        (None, "missing"),
        (
            _observation((_evidence(performed=False, result="inconclusive"),)),
            "inconclusive",
        ),
        (_observation((_evidence(performed=False, result="skipped"),)), "skipped"),
    ],
)
def test_missing_unperformed_or_skipped_evidence_cannot_pass(
    observed: ObservedControlEvidence | None,
    expected_status: str,
) -> None:
    """Missing, skipped, and unperformed evidence cannot produce a pass."""
    verdict = ControlEvidenceVerifier().verify(_requirement(), observed)

    assert verdict.status == expected_status
    assert verdict.passed is False
    assert verdict.limitations


def test_evidence_pass_stops_when_a_required_control_has_no_passing_verdict() -> None:
    """The evidence pass remains blocked when a required verdict is missing."""
    snapshot = _snapshot(evidence_passed=False)

    result = SecurityAssuranceLoop().run((snapshot, snapshot, snapshot))

    assert result.passed is False
    assert result.stopped_at == "evidence"
    evidence_result = result.pass_results[-1]
    assert evidence_result.iterations <= evidence_result.max_iterations
    assert "access-control" in evidence_result.findings
