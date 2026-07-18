"""Cold-vs-RAG quality comparison for the RAG evaluation gate."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from mastermind_cli.orchestrator.brain7_evaluator import evaluate_session

_REPO_ROOT = Path(__file__).parents[4]
_DEFAULT_OUTPUT_PATH = (
    _REPO_ROOT
    / ".mm-flow/planning/changes/rag-evaluation-gate/artifacts/brain1-quality-comparison.json"
)


@dataclass(frozen=True)
class QualityComparisonResult:
    """Summary of a Brain #7 cold-vs-RAG quality comparison."""

    brain_id: str
    cold_quality_score: float
    rag_quality_score: float
    delta: float
    passes: bool
    cold_high_value: bool
    rag_high_value: bool
    measured_at: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return asdict(self)


def compare_cold_vs_rag(
    brain_id: str,
    cold_output_json: dict[str, Any],
    rag_output_json: dict[str, Any],
    cold_duration_ms: int = 0,
    rag_duration_ms: int = 0,
    output_path: Path | None = _DEFAULT_OUTPUT_PATH,
) -> QualityComparisonResult:
    """Score a cold baseline and a RAG run using Brain #7 heuristics."""
    cold_result = evaluate_session(
        brain_id=brain_id,
        output_json=cold_output_json,
        duration_ms=cold_duration_ms,
        status="success",
    )
    rag_result = evaluate_session(
        brain_id=brain_id,
        output_json=rag_output_json,
        duration_ms=rag_duration_ms,
        status="success",
    )

    delta = round(rag_result.quality_score - cold_result.quality_score, 4)
    result = QualityComparisonResult(
        brain_id=brain_id,
        cold_quality_score=round(cold_result.quality_score, 4),
        rag_quality_score=round(rag_result.quality_score, 4),
        delta=delta,
        passes=delta > 0.0,
        cold_high_value=cold_result.high_value,
        rag_high_value=rag_result.high_value,
        measured_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")

    return result
