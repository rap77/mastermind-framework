"""Bounded domain-security assurance passes and evidence verdicts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from mastermind_cli.experience.redaction import redact_pii

from .models import EvidenceRecord, SecurityControl

SecurityApplicability = Literal["applicable", "not_applicable"]
SecurityEvidenceStatus = Literal[
    "passed",
    "failed",
    "inconclusive",
    "skipped",
    "missing",
    "not_applicable",
]
SecurityPassId = Literal[
    "asset",
    "trust-boundary",
    "threat",
    "control",
    "evidence",
    "residual-risk",
]
RiskTreatment = Literal["mitigate", "avoid", "transfer", "accept", "escalate"]

_SAFE_REFERENCE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/#-]{0,254}\Z")
_RISK_TREATMENTS = frozenset({"mitigate", "avoid", "transfer", "accept", "escalate"})


def _require_text(value: str, label: str) -> None:
    if not value.strip():
        raise ValueError(f"{label} must not be empty")


@dataclass(frozen=True, slots=True)
class ControlEvidenceRequirement:
    """Policy/profile requirement evaluated independently from observed evidence."""

    control_id: str
    applicability: SecurityApplicability
    applicability_rationale: str | None
    expected_evidence: tuple[str, ...]
    source_version: str

    def __post_init__(self) -> None:
        _require_text(self.control_id, "control_id")
        _require_text(self.source_version, "source_version")
        if self.applicability not in {"applicable", "not_applicable"}:
            raise ValueError(f"Unsupported applicability: {self.applicability}")
        if self.applicability == "not_applicable" and not (
            self.applicability_rationale and self.applicability_rationale.strip()
        ):
            raise ValueError("N/A applicability requires a rationale")
        if self.applicability == "applicable" and not self.expected_evidence:
            raise ValueError("Applicable controls require expected evidence")
        if any(not item.strip() for item in self.expected_evidence):
            raise ValueError("expected_evidence entries must not be empty")


@dataclass(frozen=True, slots=True)
class ObservedControlEvidence:
    """Security observation metadata wrapping generic HSR evidence records."""

    control_id: str
    evidence: tuple[EvidenceRecord, ...]
    verification_method: str
    performed_at: str | None
    verifier: str

    def __post_init__(self) -> None:
        _require_text(self.control_id, "control_id")
        _require_text(self.verification_method, "verification_method")
        _require_text(self.verifier, "verifier")
        if any(item.performed for item in self.evidence) and not self.performed_at:
            raise ValueError("Performed evidence requires performed_at")


@dataclass(frozen=True, slots=True)
class ControlEvidenceVerdict:
    """Sanitized assurance verdict containing references, never raw evidence."""

    control_id: str
    applicability: SecurityApplicability
    applicability_rationale: str | None
    expected_evidence: tuple[str, ...]
    observed_evidence_refs: tuple[str, ...]
    verification_method: str | None
    performed_at: str | None
    verifier: str | None
    status: SecurityEvidenceStatus
    limitations: tuple[str, ...]
    source_version: str

    @property
    def passed(self) -> bool:
        """Return true only for performed, passing evidence."""
        return self.status == "passed"


class ControlEvidenceVerifier:
    """Convert generic execution evidence into a security-specific verdict."""

    def verify(
        self,
        requirement: ControlEvidenceRequirement,
        observed_evidence: ObservedControlEvidence | None,
    ) -> ControlEvidenceVerdict:
        """Evaluate evidence fail-closed without retaining raw evidence fields."""
        if requirement.applicability == "not_applicable":
            return self._verdict(
                requirement,
                status="not_applicable",
                observed_evidence=None,
                limitations=("Control applicability was explicitly assessed as N/A.",),
            )
        if observed_evidence is None:
            return self._verdict(
                requirement,
                status="missing",
                observed_evidence=None,
                limitations=("No observed evidence was supplied.",),
            )
        if observed_evidence.control_id != requirement.control_id:
            raise ValueError("Observed evidence control_id must match requirement")
        evidence_records = observed_evidence.evidence
        if not evidence_records:
            return self._verdict(
                requirement,
                status="missing",
                observed_evidence=observed_evidence,
                limitations=("No observed evidence was supplied.",),
            )

        for item in evidence_records:
            if item.check_id != requirement.control_id:
                raise ValueError("Observed evidence check_id must match control_id")
            if (
                not _SAFE_REFERENCE.fullmatch(item.evidence_id)
                or redact_pii(item.evidence_id) != item.evidence_id
            ):
                raise ValueError("Observed evidence must use safe opaque references")

        limitations = tuple(
            dict.fromkeys(
                limitation
                for item in evidence_records
                for limitation in item.limitations
            )
        )
        if any(item.result == "skipped" for item in evidence_records):
            return self._verdict(
                requirement,
                status="skipped",
                observed_evidence=observed_evidence,
                limitations=limitations + ("Evidence collection was skipped.",),
            )
        if any(not item.performed for item in evidence_records):
            return self._verdict(
                requirement,
                status="inconclusive",
                observed_evidence=observed_evidence,
                limitations=limitations + ("Evidence was not performed.",),
            )
        if any(item.result == "fail" for item in evidence_records):
            status: SecurityEvidenceStatus = "failed"
        elif any(item.result == "inconclusive" for item in evidence_records):
            status = "inconclusive"
        elif all(item.passed for item in evidence_records):
            status = "passed"
        else:
            status = "inconclusive"
        return self._verdict(
            requirement,
            status=status,
            observed_evidence=observed_evidence,
            limitations=limitations,
        )

    @staticmethod
    def _verdict(
        requirement: ControlEvidenceRequirement,
        *,
        status: SecurityEvidenceStatus,
        observed_evidence: ObservedControlEvidence | None,
        limitations: tuple[str, ...],
    ) -> ControlEvidenceVerdict:
        """Project only safe assurance fields into the returned verdict."""
        return ControlEvidenceVerdict(
            control_id=requirement.control_id,
            applicability=requirement.applicability,
            applicability_rationale=(
                redact_pii(requirement.applicability_rationale)
                if requirement.applicability_rationale
                else None
            ),
            expected_evidence=tuple(
                redact_pii(item) for item in requirement.expected_evidence
            ),
            observed_evidence_refs=tuple(
                sorted(
                    item.evidence_id
                    for item in (
                        observed_evidence.evidence if observed_evidence else ()
                    )
                )
            ),
            verification_method=(
                observed_evidence.verification_method if observed_evidence else None
            ),
            performed_at=observed_evidence.performed_at if observed_evidence else None,
            verifier=observed_evidence.verifier if observed_evidence else None,
            status=status,
            limitations=tuple(dict.fromkeys(redact_pii(item) for item in limitations)),
            source_version=requirement.source_version,
        )


@dataclass(frozen=True, slots=True)
class ResidualRiskRecord:
    """Residual-risk assessment only; approval remains a separate SAP5 concern."""

    risk_id: str
    treatment: RiskTreatment | None

    def __post_init__(self) -> None:
        _require_text(self.risk_id, "risk_id")
        if self.treatment is not None and self.treatment not in _RISK_TREATMENTS:
            raise ValueError(f"Unsupported risk treatment: {self.treatment}")


@dataclass(frozen=True, slots=True)
class SecurityAssuranceSnapshot:
    """One iteration's typed inputs across all security assurance lenses."""

    critical_assets: tuple[str, ...]
    data_classes: tuple[str, ...]
    actors: tuple[str, ...]
    trust_boundaries: tuple[str, ...]
    threats: tuple[str, ...]
    controls: tuple[SecurityControl, ...]
    evidence_verdicts: tuple[ControlEvidenceVerdict, ...]
    residual_risks: tuple[ResidualRiskRecord, ...]


@dataclass(frozen=True, slots=True)
class AssurancePassRubric:
    """Distinct bounded rubric and terminal stop rule for one assurance pass."""

    pass_id: SecurityPassId
    rubric_id: str
    criteria: tuple[str, ...]
    max_iterations: int
    stop_rule: str


ASSURANCE_PASS_RUBRICS = (
    AssurancePassRubric(
        "asset",
        "security-assets-v1",
        ("critical assets classified", "data classes classified", "actors identified"),
        2,
        "stop-asset-inventory-incomplete",
    ),
    AssurancePassRubric(
        "trust-boundary",
        "security-trust-boundaries-v1",
        ("trust boundaries mapped",),
        2,
        "stop-trust-boundary-map-incomplete",
    ),
    AssurancePassRubric(
        "threat",
        "security-threat-model-v1",
        ("threats identified",),
        3,
        "stop-threat-model-incomplete",
    ),
    AssurancePassRubric(
        "control",
        "security-control-mapping-v1",
        ("versioned controls mapped",),
        2,
        "stop-control-map-incomplete",
    ),
    AssurancePassRubric(
        "evidence",
        "security-control-evidence-v1",
        ("every control has a passing or justified N/A verdict",),
        3,
        "stop-control-evidence-unverified",
    ),
    AssurancePassRubric(
        "residual-risk",
        "security-residual-risk-v1",
        ("residual risks have treatment decisions",),
        2,
        "stop-residual-risk-unassessed",
    ),
)


@dataclass(frozen=True, slots=True)
class AssurancePassResult:
    """Bounded result for one assurance pass."""

    pass_id: SecurityPassId
    rubric_id: str
    passed: bool
    iterations: int
    max_iterations: int
    findings: tuple[str, ...]
    stop_reason: str | None


@dataclass(frozen=True, slots=True)
class SecurityAssuranceResult:
    """Ordered assurance result that stops at the first exhausted pass."""

    passed: bool
    pass_results: tuple[AssurancePassResult, ...]
    stopped_at: SecurityPassId | None


class SecurityAssuranceLoop:
    """Run the six assurance passes with explicit bounds and stop semantics."""

    def run(
        self, snapshots: tuple[SecurityAssuranceSnapshot, ...]
    ) -> SecurityAssuranceResult:
        """Evaluate snapshots in order and stop when a pass exhausts its bound."""
        if not snapshots:
            raise ValueError("At least one assurance snapshot is required")
        results: list[AssurancePassResult] = []
        for rubric in ASSURANCE_PASS_RUBRICS:
            findings: tuple[str, ...] = ()
            for iteration, snapshot in enumerate(
                snapshots[: rubric.max_iterations], start=1
            ):
                findings = self._findings(rubric.pass_id, snapshot)
                if not findings:
                    results.append(
                        AssurancePassResult(
                            pass_id=rubric.pass_id,
                            rubric_id=rubric.rubric_id,
                            passed=True,
                            iterations=iteration,
                            max_iterations=rubric.max_iterations,
                            findings=(),
                            stop_reason=None,
                        )
                    )
                    break
            else:
                results.append(
                    AssurancePassResult(
                        pass_id=rubric.pass_id,
                        rubric_id=rubric.rubric_id,
                        passed=False,
                        iterations=min(len(snapshots), rubric.max_iterations),
                        max_iterations=rubric.max_iterations,
                        findings=findings,
                        stop_reason=rubric.stop_rule,
                    )
                )
                return SecurityAssuranceResult(
                    passed=False,
                    pass_results=tuple(results),
                    stopped_at=rubric.pass_id,
                )
        return SecurityAssuranceResult(
            passed=True,
            pass_results=tuple(results),
            stopped_at=None,
        )

    @staticmethod
    def _findings(
        pass_id: SecurityPassId, snapshot: SecurityAssuranceSnapshot
    ) -> tuple[str, ...]:
        """Apply the selected rubric without performing policy or risk approval."""
        if pass_id == "asset":
            findings = []
            if not snapshot.critical_assets:
                findings.append("critical_assets")
            if not snapshot.data_classes:
                findings.append("data_classes")
            if not snapshot.actors:
                findings.append("actors")
            return tuple(findings)
        if pass_id == "trust-boundary":
            return () if snapshot.trust_boundaries else ("trust_boundaries",)
        if pass_id == "threat":
            return () if snapshot.threats else ("threats",)
        if pass_id == "control":
            return () if snapshot.controls else ("controls",)
        if pass_id == "evidence":
            verdict_by_control = {
                verdict.control_id: verdict for verdict in snapshot.evidence_verdicts
            }
            return tuple(
                control.control_id
                for control in snapshot.controls
                if control.control_id not in verdict_by_control
                or verdict_by_control[control.control_id].status
                not in {"passed", "not_applicable"}
            )
        return tuple(
            risk.risk_id for risk in snapshot.residual_risks if risk.treatment is None
        ) or (() if snapshot.residual_risks else ("residual_risks",))
