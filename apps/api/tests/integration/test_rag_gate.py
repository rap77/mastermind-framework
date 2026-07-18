"""Integration smoke tests for the RAG evaluation gate."""

from __future__ import annotations

import asyncio
import json
import os
import uuid
from pathlib import Path

import asyncpg
import pytest
from click.testing import CliRunner

from mastermind_cli.commands.evaluation import evaluation
from mastermind_cli.rag.embed import compute_hash, encode

_TEST_BRAIN_ID = "test-rag-gate-integration"
_TEST_COLLECTION = "domain_knowledge"
_RELEVANT_SOURCE_REF = "FUENTE-900"
_DISTRACTOR_SOURCE_REF = "FUENTE-999"


async def _insert_chunk(
    conn: asyncpg.Connection,
    text: str,
    source_ref: str,
) -> None:
    """Insert one embedded chunk into brain_embeddings."""
    vectors = encode([text])
    vector_literal = "[" + ",".join(str(v) for v in vectors[0]) + "]"
    chunk_hash = compute_hash(text + str(uuid.uuid4()))

    await conn.execute(
        """
        INSERT INTO brain_embeddings
            (brain_id, collection_type, source_ref, chunk_text, chunk_hash, embedding)
        VALUES ($1, $2, $3, $4, $5, $6::vector)
        ON CONFLICT (chunk_hash) DO NOTHING
        """,
        _TEST_BRAIN_ID,
        _TEST_COLLECTION,
        source_ref,
        text,
        chunk_hash,
        vector_literal,
    )


async def _seed_gate_data(rows: list[tuple[str, str]]) -> None:
    """Seed gate test rows into PostgreSQL."""
    conn = await asyncpg.connect(os.environ["DATABASE_URL"])
    try:
        for text, source_ref in rows:
            await _insert_chunk(conn, text, source_ref)
    finally:
        await conn.close()


async def _cleanup_gate_data() -> None:
    """Remove gate test rows from PostgreSQL."""
    conn = await asyncpg.connect(os.environ["DATABASE_URL"])
    try:
        await conn.execute(
            "DELETE FROM brain_embeddings WHERE brain_id = $1",
            _TEST_BRAIN_ID,
        )
    finally:
        await conn.close()


def _write_eval_pairs(tmp_path: Path, pairs: list[dict[str, object]]) -> Path:
    """Write a labeled evaluation-pairs JSON fixture."""
    path = tmp_path / "brain1_recall_pairs.json"
    path.write_text(json.dumps({"pairs": pairs}), encoding="utf-8")
    return path


@pytest.mark.integration
def test_rag_gate_passes_with_real_retrieval(tmp_path: Path) -> None:
    """Gate should pass when Recall@5 reaches the 0.70 threshold on real data."""
    try:
        asyncio.run(
            _seed_gate_data(
                [(f"query-{index}", _RELEVANT_SOURCE_REF) for index in range(1, 8)]
                + [("distractor-chunk", _DISTRACTOR_SOURCE_REF)]
            )
        )

        eval_pairs_path = _write_eval_pairs(
            tmp_path,
            [
                {
                    "query": f"query-{index}",
                    "relevant_chunk_refs": [_RELEVANT_SOURCE_REF],
                }
                for index in range(1, 8)
            ]
            + [
                {
                    "query": f"miss-{index}",
                    "relevant_chunk_refs": [f"FUENTE-{index:03d}"],
                }
                for index in range(8, 11)
            ],
        )
        output_path = tmp_path / "gate-pass.json"

        result = CliRunner().invoke(
            evaluation,
            [
                "rag-gate",
                "--database-url",
                os.environ["DATABASE_URL"],
                "--brain-id",
                _TEST_BRAIN_ID,
                "--collection",
                _TEST_COLLECTION,
                "--eval-pairs-path",
                str(eval_pairs_path),
                "--limit",
                "5",
                "--output-path",
                str(output_path),
            ],
        )

        assert result.exit_code == 0
        assert output_path.exists()
        payload = json.loads(output_path.read_text(encoding="utf-8"))
        assert payload["passes_sli"] is True
        assert payload["recall_at_k"] == 0.7
    finally:
        asyncio.run(_cleanup_gate_data())


@pytest.mark.integration
def test_rag_gate_fails_below_threshold(tmp_path: Path) -> None:
    """Gate should fail when Recall@5 falls below the 0.70 threshold."""
    try:
        asyncio.run(
            _seed_gate_data(
                [(f"query-{index}", _RELEVANT_SOURCE_REF) for index in range(1, 7)]
                + [("distractor-chunk", _DISTRACTOR_SOURCE_REF)]
            )
        )

        eval_pairs_path = _write_eval_pairs(
            tmp_path,
            [
                {
                    "query": f"query-{index}",
                    "relevant_chunk_refs": [_RELEVANT_SOURCE_REF],
                }
                for index in range(1, 7)
            ]
            + [
                {
                    "query": f"miss-{index}",
                    "relevant_chunk_refs": [f"FUENTE-{index:03d}"],
                }
                for index in range(7, 11)
            ],
        )
        output_path = tmp_path / "gate-fail.json"

        result = CliRunner().invoke(
            evaluation,
            [
                "rag-gate",
                "--database-url",
                os.environ["DATABASE_URL"],
                "--brain-id",
                _TEST_BRAIN_ID,
                "--collection",
                _TEST_COLLECTION,
                "--eval-pairs-path",
                str(eval_pairs_path),
                "--limit",
                "5",
                "--output-path",
                str(output_path),
            ],
        )

        assert result.exit_code != 0
        assert "RAG evaluation gate failed" in result.output
        assert output_path.exists()
        payload = json.loads(output_path.read_text(encoding="utf-8"))
        assert payload["passes_sli"] is False
        assert payload["recall_at_k"] == 0.6
    finally:
        asyncio.run(_cleanup_gate_data())


@pytest.mark.integration
def test_rag_gate_handles_empty_collection(tmp_path: Path) -> None:
    """Gate should fail cleanly when the collection has no rows."""
    eval_pairs_path = _write_eval_pairs(
        tmp_path,
        [
            {"query": "query-1", "relevant_chunk_refs": ["FUENTE-001"]},
            {"query": "query-2", "relevant_chunk_refs": ["FUENTE-002"]},
        ],
    )
    output_path = tmp_path / "gate-empty.json"

    result = CliRunner().invoke(
        evaluation,
        [
            "rag-gate",
            "--database-url",
            os.environ["DATABASE_URL"],
            "--brain-id",
            "test-rag-gate-empty",
            "--collection",
            _TEST_COLLECTION,
            "--eval-pairs-path",
            str(eval_pairs_path),
            "--limit",
            "5",
            "--output-path",
            str(output_path),
        ],
    )

    assert result.exit_code != 0
    assert output_path.exists()
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["passes_sli"] is False
    assert payload["hits"] == 0
