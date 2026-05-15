"""
Integration tests for brain_embeddings schema (Phase 20A).

Tests:
- 20.04: brain_embeddings table exists
- 20.05: HNSW index exists on brain_embeddings
- 20.06: INSERT of 768-dim dummy embedding works
- 20.07: All expected columns are present
"""

from __future__ import annotations

import os

import asyncpg
import pytest

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:devpassword@localhost:5434/mastermind_bd",
)

EXPECTED_COLUMNS = {
    "id",
    "brain_id",
    "collection_type",
    "source_ref",
    "chunk_text",
    "chunk_hash",
    "embedding",
    "created_at",
}


@pytest.fixture
async def pg_conn():
    """Provide a real asyncpg connection for integration tests."""
    conn = await asyncpg.connect(DATABASE_URL)
    yield conn
    # Clean up test rows inserted during tests
    await conn.execute(
        "DELETE FROM brain_embeddings WHERE brain_id = 'test-integration'"
    )
    await conn.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_brain_embeddings_table_exists(pg_conn: asyncpg.Connection) -> None:
    """20.04: SELECT to_regclass('public.brain_embeddings') IS NOT NULL passes."""
    result = await pg_conn.fetchval(
        "SELECT to_regclass('public.brain_embeddings') IS NOT NULL"
    )
    assert result is True, "brain_embeddings table must exist in public schema"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_hnsw_index_exists(pg_conn: asyncpg.Connection) -> None:
    """20.05: HNSW index exists in pg_indexes for brain_embeddings."""
    rows = await pg_conn.fetch(
        """
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE tablename = 'brain_embeddings'
          AND indexdef LIKE '%hnsw%'
        """
    )
    assert len(rows) >= 1, "At least one HNSW index must exist on brain_embeddings"

    # Verify the index uses vector_cosine_ops
    indexdefs = [row["indexdef"] for row in rows]
    assert any(
        "vector_cosine_ops" in defn for defn in indexdefs
    ), "HNSW index must use vector_cosine_ops"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_insert_dummy_embedding(pg_conn: asyncpg.Connection) -> None:
    """20.06: INSERT of 768-dim dummy embedding succeeds and SELECT returns it."""
    embedding_str = "[" + ",".join("0" for _ in range(768)) + "]"

    # Insert a dummy embedding
    await pg_conn.execute(
        """
        INSERT INTO brain_embeddings
            (brain_id, collection_type, chunk_text, chunk_hash, embedding)
        VALUES ($1, $2, $3, $4, $5::vector)
        ON CONFLICT (chunk_hash) DO NOTHING
        """,
        "test-integration",
        "domain_knowledge",
        "dummy chunk for testing",
        "test-hash-20-06-dummy",
        embedding_str,
    )

    # Verify retrieval
    row = await pg_conn.fetchrow(
        "SELECT chunk_text, embedding FROM brain_embeddings WHERE chunk_hash = $1",
        "test-hash-20-06-dummy",
    )
    assert row is not None, "Inserted row must be retrievable"
    assert row["chunk_text"] == "dummy chunk for testing"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_brain_embeddings_columns(pg_conn: asyncpg.Connection) -> None:
    """20.07: All expected columns are present in brain_embeddings."""
    rows = await pg_conn.fetch(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'brain_embeddings'
          AND table_schema = 'public'
        """
    )
    actual_columns = {row["column_name"] for row in rows}
    missing = EXPECTED_COLUMNS - actual_columns
    assert not missing, f"Missing columns in brain_embeddings: {missing}"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_collection_type_constraint(pg_conn: asyncpg.Connection) -> None:
    """collection_type CHECK constraint rejects invalid values."""
    with pytest.raises(asyncpg.CheckViolationError):
        await pg_conn.execute(
            """
            INSERT INTO brain_embeddings
                (brain_id, collection_type, chunk_text, chunk_hash)
            VALUES ($1, $2, $3, $4)
            """,
            "test-integration",
            "invalid_type",
            "bad chunk",
            "test-hash-constraint-fail",
        )
