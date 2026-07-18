"""Tests for the RAG self-contamination checker."""

from __future__ import annotations

import json
from pathlib import Path

from mastermind_cli.rag.contamination import evaluate_self_contamination


def _write_eval_pairs(tmp_path: Path, pairs: list[dict[str, object]]) -> Path:
    """Write an evaluation-pairs fixture."""
    fixture_path = tmp_path / "eval_pairs.json"
    fixture_path.write_text(json.dumps({"pairs": pairs}), encoding="utf-8")
    return fixture_path


def test_evaluate_self_contamination_passes_for_non_brain_refs(tmp_path: Path) -> None:
    """Non-brain source refs should pass the contamination check."""
    eval_pairs_path = _write_eval_pairs(
        tmp_path,
        [{"query": "query-1", "relevant_chunk_refs": ["FUENTE-001"]}],
    )

    result = evaluate_self_contamination(
        eval_pairs_path=eval_pairs_path,
        brain_id="brain-01-product-strategy",
        output_path=None,
    )

    assert result.passed is True
    assert result.contaminated_chunk_refs == []
    assert result.checked_pairs == 1


def test_evaluate_self_contamination_fails_for_brain_refs(tmp_path: Path) -> None:
    """Brain-prefixed refs should be rejected as self-contamination."""
    eval_pairs_path = _write_eval_pairs(
        tmp_path,
        [
            {
                "query": "query-1",
                "relevant_chunk_refs": ["brain-01-product-strategy-answer-1"],
            }
        ],
    )

    result = evaluate_self_contamination(
        eval_pairs_path=eval_pairs_path,
        brain_id="brain-01-product-strategy",
        output_path=None,
    )

    assert result.passed is False
    assert result.contaminated_chunk_refs == ["brain-01-product-strategy-answer-1"]


def test_evaluate_self_contamination_passes_for_other_brain_refs(
    tmp_path: Path,
) -> None:
    """Other-brain output refs should not count as self-contamination."""
    eval_pairs_path = _write_eval_pairs(
        tmp_path,
        [
            {
                "query": "query-1",
                "relevant_chunk_refs": ["brain-02-ux-design-answer-1"],
            }
        ],
    )

    result = evaluate_self_contamination(
        eval_pairs_path=eval_pairs_path,
        brain_id="brain-01-product-strategy",
        output_path=None,
    )

    assert result.passed is True
    assert result.contaminated_chunk_refs == []
