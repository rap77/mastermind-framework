"""Unit tests for the offline RAG Recall@K evaluator."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from mastermind_cli.rag.recall_eval import evaluate_recall, load_eval_pairs


def _write_eval_pairs(tmp_path: Path, pairs: list[dict[str, object]]) -> Path:
    """Write a temporary evaluation-pairs fixture."""
    fixture_path = tmp_path / "eval_pairs.json"
    fixture_path.write_text(json.dumps({"pairs": pairs}), encoding="utf-8")
    return fixture_path


def test_load_eval_pairs_accepts_envelope_format(tmp_path: Path) -> None:
    """Load evaluation pairs from an object containing a `pairs` list."""
    fixture_path = _write_eval_pairs(
        tmp_path,
        [
            {
                "query": "continuous discovery interviews",
                "relevant_chunk_refs": ["FUENTE-002"],
            }
        ],
    )

    pairs = load_eval_pairs(fixture_path)

    assert len(pairs) == 1
    assert pairs[0].query == "continuous discovery interviews"
    assert pairs[0].relevant_chunk_refs == ["FUENTE-002"]


@pytest.mark.asyncio
async def test_evaluate_recall_passes_at_threshold(tmp_path: Path) -> None:
    """Recall@5 passes when 7 of 10 labeled pairs hit relevant source refs."""
    fixture_path = _write_eval_pairs(
        tmp_path,
        [
            {"query": f"query-{index}", "relevant_chunk_refs": [f"FUENTE-{index:03d}"]}
            for index in range(1, 11)
        ],
    )
    output_path = tmp_path / "recall_results.json"

    async def fake_search(
        conn: object,
        brain_id: str,
        collection: str,
        query_text: str,
        limit: int = 5,
    ) -> list[dict[str, object]]:
        del conn, brain_id, collection, limit
        pair_number = int(query_text.split("-")[-1])
        if pair_number <= 7:
            return [{"source_ref": f"FUENTE-{pair_number:03d}"}]
        return [{"source_ref": "FUENTE-999"}]

    with patch("mastermind_cli.rag.recall_eval.similarity_search", new=fake_search):
        result = await evaluate_recall(
            conn=object(),  # type: ignore[arg-type]
            eval_pairs_path=fixture_path,
            output_path=output_path,
        )

    assert result.hits == 7
    assert result.total == 10
    assert result.recall_at_k == 0.7
    assert result.passes_sli is True
    assert output_path.exists()
    written = json.loads(output_path.read_text(encoding="utf-8"))
    assert written["passes_sli"] is True
    assert written["hits"] == 7


@pytest.mark.asyncio
async def test_evaluate_recall_fails_below_threshold(tmp_path: Path) -> None:
    """Recall@5 fails when only 6 of 10 labeled pairs hit."""
    fixture_path = _write_eval_pairs(
        tmp_path,
        [
            {"query": f"query-{index}", "relevant_chunk_refs": [f"FUENTE-{index:03d}"]}
            for index in range(1, 11)
        ],
    )

    async def fake_search(
        conn: object,
        brain_id: str,
        collection: str,
        query_text: str,
        limit: int = 5,
    ) -> list[dict[str, object]]:
        del conn, brain_id, collection, limit
        pair_number = int(query_text.split("-")[-1])
        if pair_number <= 6:
            return [{"source_ref": f"FUENTE-{pair_number:03d}"}]
        return []

    with patch("mastermind_cli.rag.recall_eval.similarity_search", new=fake_search):
        result = await evaluate_recall(
            conn=object(),  # type: ignore[arg-type]
            eval_pairs_path=fixture_path,
            output_path=None,
        )

    assert result.hits == 6
    assert result.total == 10
    assert result.recall_at_k == 0.6
    assert result.passes_sli is False


@pytest.mark.asyncio
async def test_evaluate_recall_with_empty_retrieval_results(tmp_path: Path) -> None:
    """Recall@5 returns 0.0 when retrieval returns no hits for any pair."""
    fixture_path = _write_eval_pairs(
        tmp_path,
        [
            {"query": "query-1", "relevant_chunk_refs": ["FUENTE-001"]},
            {"query": "query-2", "relevant_chunk_refs": ["FUENTE-002"]},
        ],
    )

    async def fake_search(
        conn: object,
        brain_id: str,
        collection: str,
        query_text: str,
        limit: int = 5,
    ) -> list[dict[str, object]]:
        del conn, brain_id, collection, query_text, limit
        return []

    with patch("mastermind_cli.rag.recall_eval.similarity_search", new=fake_search):
        result = await evaluate_recall(
            conn=object(),  # type: ignore[arg-type]
            eval_pairs_path=fixture_path,
            output_path=None,
        )

    assert result.hits == 0
    assert result.total == 2
    assert result.recall_at_k == 0.0
    assert result.passes_sli is False
