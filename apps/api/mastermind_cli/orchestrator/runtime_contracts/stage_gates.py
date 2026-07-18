"""Deterministic gate evaluation against typed stage evidence."""

from __future__ import annotations

from dataclasses import dataclass

from .models import EvidenceRecord


@dataclass(frozen=True, slots=True)
class GateEvaluation:
    """Typed verdict for one required stage check."""

    gate_policy: str
    passed: bool
    evidence_refs: tuple[str, ...]
    rationale: str


class GateEvaluator:
    """Evaluate one gate policy from matching execution evidence."""

    def evaluate(
        self,
        gate_policy: str,
        evidence: tuple[EvidenceRecord, ...],
    ) -> GateEvaluation:
        """Pass only when all evidence for the required check was performed and passed."""
        matching = tuple(item for item in evidence if item.check_id == gate_policy)
        evidence_refs = tuple(sorted(item.evidence_id for item in matching))
        if not matching:
            return GateEvaluation(
                gate_policy=gate_policy,
                passed=False,
                evidence_refs=(),
                rationale=f"Required check {gate_policy} has no evidence.",
            )
        if not all(item.passed for item in matching):
            return GateEvaluation(
                gate_policy=gate_policy,
                passed=False,
                evidence_refs=evidence_refs,
                rationale=f"Required check {gate_policy} did not pass.",
            )
        return GateEvaluation(
            gate_policy=gate_policy,
            passed=True,
            evidence_refs=evidence_refs,
            rationale=f"Required check {gate_policy} passed.",
        )
