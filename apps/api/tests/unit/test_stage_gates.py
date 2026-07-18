"""Tests for deterministic stage gate evaluation."""

from dataclasses import replace

from mastermind_cli.orchestrator.runtime_contracts.models import EvidenceRecord
from mastermind_cli.orchestrator.runtime_contracts.stage_gates import GateEvaluator


def _evidence(
    *,
    evidence_id: str = "evidence-001",
    check_id: str = "pytest-unit",
    performed: bool = True,
    result: str = "pass",
) -> EvidenceRecord:
    """Create typed command evidence for a stage gate."""
    return EvidenceRecord(
        evidence_id=evidence_id,
        check_id=check_id,
        performed=performed,
        method="command",
        result=result,  # type: ignore[arg-type]
        summary="Targeted unit test evidence.",
        command_or_procedure="uv run pytest -q tests/unit",
        tool=None,
        environment=None,
        exit_status=0 if performed else None,
        artifact_refs=(),
        metrics=(),
        detail_schema_ref=None,
        details_ref=None,
        limitations=(),
        recorded_at="2026-07-16T12:00:00Z",
    )


def test_gate_passes_only_with_matching_performed_pass_evidence() -> None:
    """A gate should pass from matching typed execution evidence."""
    evaluation = GateEvaluator().evaluate(
        "pytest-unit",
        (_evidence(), _evidence(evidence_id="other", check_id="ruff")),
    )

    assert evaluation.passed is True
    assert evaluation.evidence_refs == ("evidence-001",)
    assert evaluation.rationale == "Required check pytest-unit passed."


def test_gate_rejects_missing_evidence() -> None:
    """A summary or unrelated check must not satisfy the required gate."""
    evaluation = GateEvaluator().evaluate(
        "pytest-unit",
        (_evidence(check_id="ruff"),),
    )

    assert evaluation.passed is False
    assert evaluation.evidence_refs == ()
    assert evaluation.rationale == "Required check pytest-unit has no evidence."


def test_gate_rejects_an_unperformed_check() -> None:
    """A skipped check must remain non-passing even when its ID matches."""
    skipped = replace(_evidence(), performed=False, result="skipped", exit_status=None)

    evaluation = GateEvaluator().evaluate("pytest-unit", (skipped,))

    assert evaluation.passed is False
    assert evaluation.evidence_refs == ("evidence-001",)
    assert evaluation.rationale == "Required check pytest-unit did not pass."
