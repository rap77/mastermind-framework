"""
Integration tests for mastermind_cli.rag.search (Phase 20B).

Tests:
- 20.14: similarity_search() with fixture in test DB returns list with
         chunk_text and score in [0.0, 1.0]
- 20.15: similarity_search() with empty collection returns empty list
"""

from __future__ import annotations

import os
import uuid

import asyncpg
import pytest

from mastermind_cli.rag.embed import compute_hash, encode
from mastermind_cli.rag.search import similarity_search

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:devpassword@localhost:5434/mastermind_bd",
)

_TEST_BRAIN_ID = "test-rag-search-integration"
_TEST_COLLECTION = "domain_knowledge"


@pytest.fixture
async def pg_conn_search():
    """Real asyncpg connection with test row cleanup."""
    conn = await asyncpg.connect(DATABASE_URL)
    yield conn
    await conn.execute(
        "DELETE FROM brain_embeddings WHERE brain_id = $1",
        _TEST_BRAIN_ID,
    )
    await conn.close()


async def _insert_chunk(
    conn: asyncpg.Connection,
    text: str,
    source_ref: str = "test-source",
) -> None:
    """Helper: embed and insert a chunk into brain_embeddings."""
    vectors = encode([text])
    vector_literal = "[" + ",".join(str(v) for v in vectors[0]) + "]"
    chunk_hash = compute_hash(text + str(uuid.uuid4()))  # unique per call

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


@pytest.mark.integration
@pytest.mark.asyncio
async def test_similarity_search_returns_results(
    pg_conn_search: asyncpg.Connection,
) -> None:
    """20.14: similarity_search with DB fixture returns chunk_text and score in [0, 1]."""
    # Insert test chunks
    chunks = [
        "Python is a high-level programming language",
        "Machine learning uses statistical methods",
        "Neural networks are inspired by the brain",
    ]
    for chunk in chunks:
        await _insert_chunk(pg_conn_search, chunk)

    # Query
    results = await similarity_search(
        pg_conn_search,
        brain_id=_TEST_BRAIN_ID,
        collection=_TEST_COLLECTION,
        query_text="programming language",
        limit=5,
    )

    assert isinstance(results, list), "similarity_search must return a list"
    assert len(results) >= 1, "Must return at least one result when chunks exist"

    for result in results:
        assert "chunk_text" in result, "Each result must have chunk_text"
        assert "score" in result, "Each result must have score"
        assert "source_ref" in result, "Each result must have source_ref"
        score = result["score"]
        assert isinstance(score, float), "score must be a float"
        assert 0.0 <= score <= 1.0, f"score must be in [0, 1], got {score}"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_similarity_search_empty_collection(
    pg_conn_search: asyncpg.Connection,
) -> None:
    """20.15: similarity_search with empty collection returns empty list without crashing."""
    results = await similarity_search(
        pg_conn_search,
        brain_id="nonexistent-brain-xyz",
        collection=_TEST_COLLECTION,
        query_text="any query",
        limit=5,
    )

    assert isinstance(results, list), "Must return a list even when empty"
    assert len(results) == 0, "Must return empty list for nonexistent brain"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_similarity_search_empty_query_returns_empty(
    pg_conn_search: asyncpg.Connection,
) -> None:
    """Empty query string returns empty list without error."""
    results = await similarity_search(
        pg_conn_search,
        brain_id=_TEST_BRAIN_ID,
        collection=_TEST_COLLECTION,
        query_text="   ",
        limit=5,
    )
    assert results == []
