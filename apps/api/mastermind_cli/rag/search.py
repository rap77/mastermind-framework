"""
RAG similarity search — Phase 20B.

Provides cosine-similarity search over brain_embeddings using asyncpg
and the pgvector <=> distance operator.

Usage:
    from mastermind_cli.rag.search import similarity_search

    results = await similarity_search(conn, "brain-01", "domain_knowledge", "query text")
"""

from __future__ import annotations

from typing import Any

import asyncpg

from .embed import encode


async def similarity_search(
    conn: asyncpg.Connection,
    brain_id: str,
    collection: str,
    query_text: str,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Find the most similar chunks to ``query_text`` in brain_embeddings.

    Embeds the query with the default sentence-transformer model, then runs
    a nearest-neighbour search using the pgvector cosine-distance operator
    ``<=>``.  Returns results ordered by ascending distance (most similar
    first), with a normalised score where 1.0 is a perfect match.

    Args:
        conn: Open asyncpg connection.
        brain_id: Brain identifier to filter rows.
        collection: Collection type (``'domain_knowledge'`` or
            ``'project_memory'``).
        query_text: Natural-language query to embed.
        limit: Maximum number of results to return.  Defaults to 5.

    Returns:
        List of dicts with keys ``chunk_text``, ``score``, and ``source_ref``.
        ``score`` is in ``[0.0, 1.0]`` — higher is more similar.  Returns an
        empty list when the collection is empty or no embeddings match the
        filter.

    Raises:
        asyncpg.PostgresError: On database connectivity or query errors.
    """
    if not query_text.strip():
        return []

    # Embed the query (returns a list with one vector)
    query_vectors = encode([query_text])
    query_vector = query_vectors[0]

    # Format as pgvector literal: '[0.1,0.2,...,0.768]'
    vector_literal = "[" + ",".join(str(v) for v in query_vector) + "]"

    rows = await conn.fetch(
        """
        SELECT
            chunk_text,
            source_ref,
            1.0 - (embedding <=> $1::vector) AS score
        FROM brain_embeddings
        WHERE brain_id = $2
          AND collection_type = $3
          AND embedding IS NOT NULL
        ORDER BY embedding <=> $1::vector
        LIMIT $4
        """,
        vector_literal,
        brain_id,
        collection,
        limit,
    )

    return [
        {
            "chunk_text": row["chunk_text"],
            "score": float(row["score"]),
            "source_ref": row["source_ref"],
        }
        for row in rows
    ]
