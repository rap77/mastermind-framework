"""
Unit tests for RAGContextBuilder — Phase 21.

Tests:
- 21.07: build() with mock similarity_search returns block with [RETRIEVED CONTEXT]
         and [END RETRIEVED CONTEXT]
- 21.08: build() with both collections empty returns "" (no empty block)
- 21.09: build() with only domain_knowledge results omits project_memory section
- 21.10: build() with real fixture takes < 200ms (time.perf_counter)
- 21.11: import does not raise ImportError
"""

from __future__ import annotations

import time
from unittest.mock import patch

import pytest

from mastermind_cli.rag.context_builder import RAGContextBuilder


# ---------------------------------------------------------------------------
# 21.11 — Import smoke test (runs at module load)
# ---------------------------------------------------------------------------


def test_import_does_not_raise() -> None:
    """21.11: from mastermind_cli.rag.context_builder import RAGContextBuilder — no ImportError."""
    from mastermind_cli.rag.context_builder import RAGContextBuilder as _CB  # noqa: F401

    assert _CB is not None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fake_conn() -> object:
    """Create a minimal fake asyncpg.Connection object."""
    return object()


_DOMAIN_ROW = {
    "chunk_text": "Marty Cagan: empowered teams",
    "score": 0.87,
    "source_ref": "FUENTE-001",
}
_MEMORY_ROW = {
    "chunk_text": "Phase 20 brain feed note",
    "score": 0.91,
    "source_ref": "BRAIN-FEED-01",
}


# ---------------------------------------------------------------------------
# 21.07: build() with mock → returns [RETRIEVED CONTEXT] block
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_build_returns_retrieved_context_block() -> None:
    """21.07: build() with mocked similarity_search returns block bounded by markers."""
    conn = _fake_conn()
    builder = RAGContextBuilder(conn)  # type: ignore[arg-type]

    domain_results = [_DOMAIN_ROW]
    memory_results = [_MEMORY_ROW]

    async def fake_search(c, brain_id, collection, query, limit=5):
        if collection == "domain_knowledge":
            return domain_results
        return memory_results

    with patch("mastermind_cli.rag.context_builder.similarity_search", new=fake_search):
        result = await builder.build("brain-01-product", "discovery strategy")

    assert result.startswith("[RETRIEVED CONTEXT]")
    assert result.strip().endswith("[END RETRIEVED CONTEXT]")
    assert "domain_knowledge" in result
    assert "project_memory" in result
    assert "FUENTE-001" in result
    assert "BRAIN-FEED-01" in result
    assert "0.87" in result
    assert "0.91" in result


# ---------------------------------------------------------------------------
# 21.08: build() with both empty → returns "" (empty string, no block)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_build_both_empty_returns_empty_string() -> None:
    """21.08: build() with both collections empty returns '' — not a block with no content."""
    conn = _fake_conn()
    builder = RAGContextBuilder(conn)  # type: ignore[arg-type]

    async def fake_search_empty(c, brain_id, collection, query, limit=5):
        return []

    with patch(
        "mastermind_cli.rag.context_builder.similarity_search", new=fake_search_empty
    ):
        result = await builder.build("brain-01-product", "discovery strategy")

    assert result == ""
    assert "[RETRIEVED CONTEXT]" not in result


# ---------------------------------------------------------------------------
# 21.09: build() with only domain_knowledge → omits project_memory section
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_build_only_domain_omits_memory_section() -> None:
    """21.09: build() with only domain_knowledge results omits project_memory subsection."""
    conn = _fake_conn()
    builder = RAGContextBuilder(conn)  # type: ignore[arg-type]

    async def fake_search(c, brain_id, collection, query, limit=5):
        if collection == "domain_knowledge":
            return [_DOMAIN_ROW]
        return []  # project_memory empty

    with patch("mastermind_cli.rag.context_builder.similarity_search", new=fake_search):
        result = await builder.build("brain-01-product", "discovery strategy")

    assert "[RETRIEVED CONTEXT]" in result
    assert "domain_knowledge" in result
    assert "project_memory" not in result
    assert "[END RETRIEVED CONTEXT]" in result


# ---------------------------------------------------------------------------
# 21.10: build() with fixture takes < 200ms
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_build_timing_under_200ms() -> None:
    """21.10: build() with mocked similarity_search completes in < 200ms."""
    conn = _fake_conn()
    builder = RAGContextBuilder(conn)  # type: ignore[arg-type]

    domain_results = [_DOMAIN_ROW] * 5
    memory_results = [_MEMORY_ROW] * 3

    async def fake_search(c, brain_id, collection, query, limit=5):
        if collection == "domain_knowledge":
            return domain_results[:limit]
        return memory_results[:limit]

    with patch("mastermind_cli.rag.context_builder.similarity_search", new=fake_search):
        t0 = time.perf_counter()
        await builder.build("brain-01-product", "discovery strategy")
        elapsed_ms = (time.perf_counter() - t0) * 1000

    assert elapsed_ms < 200, f"build() took {elapsed_ms:.1f}ms — expected < 200ms"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_build_blank_query_returns_empty_string() -> None:
    """build() with blank query short-circuits and returns '' without DB calls."""
    conn = _fake_conn()
    builder = RAGContextBuilder(conn)  # type: ignore[arg-type]

    async def fake_search_never_called(*args, **kwargs):
        raise AssertionError("similarity_search should not be called for blank query")

    with patch(
        "mastermind_cli.rag.context_builder.similarity_search",
        new=fake_search_never_called,
    ):
        result = await builder.build("brain-01-product", "   ")

    assert result == ""


@pytest.mark.asyncio
async def test_build_only_memory_omits_domain_section() -> None:
    """build() with only project_memory results omits domain_knowledge subsection."""
    conn = _fake_conn()
    builder = RAGContextBuilder(conn)  # type: ignore[arg-type]

    async def fake_search(c, brain_id, collection, query, limit=5):
        if collection == "project_memory":
            return [_MEMORY_ROW]
        return []

    with patch("mastermind_cli.rag.context_builder.similarity_search", new=fake_search):
        result = await builder.build("brain-01-product", "discovery")

    assert "[RETRIEVED CONTEXT]" in result
    assert "domain_knowledge" not in result
    assert "project_memory" in result
    assert "[END RETRIEVED CONTEXT]" in result
