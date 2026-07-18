"""Tests for the executable RAG evaluation gate wrapper."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Coroutine
from unittest.mock import AsyncMock, patch

import pytest

from mastermind_cli.rag.gate import _run_gate, run
from mastermind_cli.rag.recall_eval import RecallPairResult, RecallResult


class _FakeConn:
    """Tiny asyncpg-like connection stub."""

    def __init__(self) -> None:
        self.closed = False

    async def close(self) -> None:
        self.closed = True


def _write_eval_pairs(tmp_path: Path, pairs: list[dict[str, object]]) -> Path:
    """Write an evaluation-pairs fixture for the gate wrapper."""
    fixture_path = tmp_path / "eval_pairs.json"
    fixture_path.write_text(json.dumps({"pairs": pairs}), encoding="utf-8")
    return fixture_path


@pytest.mark.asyncio
async def test_run_gate_closes_connection_and_returns_payload(
    tmp_path: Path,
) -> None:
    """The wrapper should delegate to Recall@K evaluation and close the DB conn."""
    fake_conn = _FakeConn()
    fake_result = RecallResult(
        brain_id="brain-01-product-strategy",
        collection="domain_knowledge",
        limit=5,
        threshold=0.7,
        hits=1,
        total=1,
        recall_at_k=1.0,
        passes_sli=True,
        eval_pairs_path=str(tmp_path / "pairs.json"),
        measured_at="2026-07-12T00:00:00Z",
        pair_results=[
            RecallPairResult(
                query="query",
                relevant_chunk_refs=["FUENTE-001"],
                retrieved_chunk_refs=["FUENTE-001"],
                hit=True,
            )
        ],
    )

    eval_pairs_path = _write_eval_pairs(
        tmp_path,
        [{"query": "query", "relevant_chunk_refs": ["FUENTE-001"]}],
    )

    args = argparse.Namespace(
        database_url="postgresql://example",
        brain_id="brain-01-product-strategy",
        collection="domain_knowledge",
        eval_pairs_path=str(eval_pairs_path),
        limit=5,
        output_path=str(tmp_path / "results.json"),
    )

    with (
        patch(
            "mastermind_cli.rag.gate.asyncpg.connect",
            new=AsyncMock(return_value=fake_conn),
        ),
        patch(
            "mastermind_cli.rag.gate.evaluate_recall",
            new=AsyncMock(return_value=fake_result),
        ),
    ):
        payload = await _run_gate(args)

    assert fake_conn.closed is True
    assert payload["passes_sli"] is True
    assert payload["hits"] == 1
    assert payload["brain_id"] == "brain-01-product-strategy"
    assert payload["contamination_passed"] is True


def test_run_returns_nonzero_when_gate_fails(tmp_path: Path) -> None:
    """The executable wrapper must fail the process when Recall@K misses threshold."""
    payload = {"passes_sli": False, "contamination_passed": True}
    eval_pairs_path = _write_eval_pairs(
        tmp_path,
        [{"query": "query", "relevant_chunk_refs": ["FUENTE-001"]}],
    )

    def _fake_asyncio_run(coro: Coroutine[Any, Any, dict[str, Any]]) -> dict[str, bool]:
        coro.close()
        return payload

    with (
        patch("mastermind_cli.rag.gate.asyncio.run", new=_fake_asyncio_run),
        patch("mastermind_cli.rag.gate.click.echo") as echo,
    ):
        exit_code = run(
            [
                "--database-url",
                "postgresql://example",
                "--eval-pairs-path",
                str(eval_pairs_path),
            ]
        )

    assert exit_code == 1
    echo.assert_called_once()


@pytest.mark.asyncio
async def test_run_gate_fails_on_contamination(tmp_path: Path) -> None:
    """The gate must fail when the contamination check detects same-brain refs."""
    fake_conn = _FakeConn()
    fake_result = RecallResult(
        brain_id="brain-01-product-strategy",
        collection="domain_knowledge",
        limit=5,
        threshold=0.7,
        hits=1,
        total=1,
        recall_at_k=1.0,
        passes_sli=True,
        eval_pairs_path=str(tmp_path / "pairs.json"),
        measured_at="2026-07-12T00:00:00Z",
        pair_results=[
            RecallPairResult(
                query="query",
                relevant_chunk_refs=["brain-01-product-strategy-answer-1"],
                retrieved_chunk_refs=["brain-01-product-strategy-answer-1"],
                hit=True,
            )
        ],
    )
    eval_pairs_path = _write_eval_pairs(
        tmp_path,
        [
            {
                "query": "query",
                "relevant_chunk_refs": ["brain-01-product-strategy-answer-1"],
            }
        ],
    )

    args = argparse.Namespace(
        database_url="postgresql://example",
        brain_id="brain-01-product-strategy",
        collection="domain_knowledge",
        eval_pairs_path=str(eval_pairs_path),
        limit=5,
        output_path=str(tmp_path / "results.json"),
    )

    with (
        patch(
            "mastermind_cli.rag.gate.asyncpg.connect",
            new=AsyncMock(return_value=fake_conn),
        ),
        patch(
            "mastermind_cli.rag.gate.evaluate_recall",
            new=AsyncMock(return_value=fake_result),
        ),
    ):
        payload = await _run_gate(args)

    assert fake_conn.closed is True
    assert payload["passes_sli"] is True
    assert payload["contamination_passed"] is False
