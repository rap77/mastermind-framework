"""Self-contamination checks for the RAG evaluation gate."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from .recall_eval import load_eval_pairs

_REPO_ROOT = Path(__file__).parents[4]
_DEFAULT_OUTPUT_PATH = (
    _REPO_ROOT
    / ".mm-flow/planning/changes/rag-evaluation-gate/artifacts/brain1-contamination-results.json"
)


@dataclass(frozen=True)
class ContaminationResult:
    """Summary of a self-contamination check."""

    brain_id: str
    passed: bool
    contaminated_chunk_refs: list[str]
    checked_pairs: int
    measured_at: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return asdict(self)


def _is_self_contaminated_ref(brain_id: str, chunk_ref: str) -> bool:
    """Return True when a chunk ref looks like same-brain output."""
    normalized_brain_id = brain_id.strip().lower().replace("_", "-")
    normalized_ref = chunk_ref.strip().lower()
    return normalized_brain_id in normalized_ref


def evaluate_self_contamination(
    eval_pairs_path: Path,
    brain_id: str,
    output_path: Path | None = _DEFAULT_OUTPUT_PATH,
) -> ContaminationResult:
    """Check whether the evaluation corpus reuses same-brain answers as targets."""
    pairs = load_eval_pairs(eval_pairs_path)
    contaminated_chunk_refs: list[str] = []

    for pair in pairs:
        for chunk_ref in pair.relevant_chunk_refs:
            if _is_self_contaminated_ref(brain_id, chunk_ref):
                contaminated_chunk_refs.append(chunk_ref)

    result = ContaminationResult(
        brain_id=brain_id,
        passed=not contaminated_chunk_refs,
        contaminated_chunk_refs=contaminated_chunk_refs,
        checked_pairs=len(pairs),
        measured_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )

    payload = result.to_dict()
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    return result
