"""Pgvector-backed indexing and retrieval for first-party memory items."""

from __future__ import annotations

import math
import hashlib
import re
from typing import Any

from sqlalchemy import text

from mastermind_cli.project_state.database.session import get_engine

from .contracts import EmbeddingProvider
from .models import MemoryIndexPayload


_VECTOR_TYPE_PATTERN = re.compile(r"vector\((\d+)\)")


def _read_existing_embedding_dimensions(connection: Any) -> int | None:
    """Return the current pgvector column dimension when the table already exists."""
    result = connection.execute(
        text(
            """
            SELECT format_type(a.atttypid, a.atttypmod)
            FROM pg_attribute AS a
            JOIN pg_class AS c ON c.oid = a.attrelid
            JOIN pg_namespace AS n ON n.oid = c.relnamespace
            WHERE n.nspname = 'public'
              AND c.relname = 'mm_memory_embeddings'
              AND a.attname = 'embedding'
              AND NOT a.attisdropped
            """
        )
    ).fetchone()
    if not result:
        return None

    match = _VECTOR_TYPE_PATTERN.search(str(result[0]))
    if not match:
        return None
    return int(match.group(1))


def _read_embedding_row_count(connection: Any) -> int:
    """Return the number of rows currently stored in the embedding table."""
    result = connection.execute(
        text("SELECT COUNT(*) FROM mm_memory_embeddings")
    ).scalar()
    return int(result or 0)


def _ensure_pgvector_memory_schema(engine: Any, dimensions: int) -> None:
    """Create pgvector-owned memory embedding structures."""
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        existing_dimensions = _read_existing_embedding_dimensions(connection)
        if existing_dimensions is None:
            connection.execute(
                text(
                    f"""
                    CREATE TABLE IF NOT EXISTS mm_memory_embeddings (
                        memory_id VARCHAR(255) PRIMARY KEY
                            REFERENCES mm_memory_items(memory_id) ON DELETE CASCADE,
                        project_id VARCHAR(255),
                        brain_id VARCHAR(255),
                        niche VARCHAR(128),
                        source_ref VARCHAR(255),
                        embedding vector({dimensions}) NOT NULL,
                        embedding_model VARCHAR(255) NOT NULL,
                        content_hash VARCHAR(64) NOT NULL,
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
                )
            )
        elif existing_dimensions != dimensions:
            row_count = _read_embedding_row_count(connection)
            if row_count > 0:
                raise ValueError(
                    "Existing mm_memory_embeddings schema uses "
                    f"{existing_dimensions} dimensions but the configured model "
                    f"requires {dimensions}. Limpia/reindexa embeddings o usa un "
                    "modelo con la misma dimensión."
                )
            connection.execute(
                text(
                    f"""
                    ALTER TABLE mm_memory_embeddings
                    ALTER COLUMN embedding TYPE vector({dimensions})
                    """
                )
            )
        connection.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS idx_mm_memory_embeddings_project_id
                ON mm_memory_embeddings (project_id)
                """
            )
        )
        connection.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS idx_mm_memory_embeddings_hnsw
                ON mm_memory_embeddings
                USING hnsw (embedding vector_cosine_ops)
                """
            )
        )


def _validate_postgres_url(database_url: str) -> None:
    """Validate that the configured URL targets PostgreSQL."""
    if not database_url.startswith(("postgresql://", "postgres://")):
        raise ValueError("Pgvector provider requires a PostgreSQL URL")


def _vector_literal(values: list[float]) -> str:
    """Return a pgvector-compatible literal."""
    literal_values: list[str] = []
    for value in values:
        if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
            raise ValueError("pgvector embeddings must be finite numeric values")
        literal_values.append(str(float(value)))
    return "[" + ",".join(literal_values) + "]"


class PgvectorMemoryIndexProvider:
    """Persist semantic memory embeddings into a dedicated pgvector table."""

    def __init__(
        self,
        database_url: str,
        embedding_provider: EmbeddingProvider,
        *,
        embedding_model: str = "sentence-transformers/all-mpnet-base-v2",
        dimensions: int | None = None,
    ) -> None:
        """Initialize the pgvector provider against a PostgreSQL database."""
        _validate_postgres_url(database_url)

        self._engine = get_engine(database_url)
        self._embedding_provider = embedding_provider
        self._embedding_model = embedding_model
        self._dimensions = dimensions
        self._schema_ready = False

    async def upsert(self, payload: MemoryIndexPayload) -> None:
        """Insert or refresh the embedding row for a canonical memory payload."""
        embeddings = await self._embedding_provider.embed_texts(
            [payload.embedding_text]
        )
        if not embeddings:
            return

        vector = embeddings[0]
        dimensions = self._resolve_dimensions(vector)
        if len(vector) != dimensions:
            raise ValueError(
                f"Expected embedding dimension {dimensions}, got {len(vector)}"
            )

        self._ensure_schema()
        vector_literal = _vector_literal(vector)
        content_hash = self._content_hash(payload.embedding_text)

        with self._engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO mm_memory_embeddings (
                        memory_id,
                        project_id,
                        brain_id,
                        niche,
                        source_ref,
                        embedding,
                        embedding_model,
                        content_hash,
                        updated_at
                    ) VALUES (
                        :memory_id,
                        :project_id,
                        :brain_id,
                        :niche,
                        :source_ref,
                        CAST(:embedding AS vector),
                        :embedding_model,
                        :content_hash,
                        NOW()
                    )
                    ON CONFLICT (memory_id) DO UPDATE SET
                        project_id = EXCLUDED.project_id,
                        brain_id = EXCLUDED.brain_id,
                        niche = EXCLUDED.niche,
                        source_ref = EXCLUDED.source_ref,
                        embedding = EXCLUDED.embedding,
                        embedding_model = EXCLUDED.embedding_model,
                        content_hash = EXCLUDED.content_hash,
                        updated_at = NOW()
                    """
                ),
                {
                    "memory_id": payload.memory_id,
                    "project_id": payload.project_id,
                    "brain_id": payload.brain_id,
                    "niche": payload.niche,
                    "source_ref": payload.source_ref,
                    "embedding": vector_literal,
                    "embedding_model": self._embedding_model,
                    "content_hash": content_hash,
                },
            )

    def _ensure_schema(self) -> None:
        """Create pgvector-owned memory embedding structures once."""
        if self._schema_ready:
            return
        if self._dimensions is None:
            raise ValueError("Pgvector schema requires a known embedding dimension")
        _ensure_pgvector_memory_schema(self._engine, self._dimensions)
        self._schema_ready = True

    def _content_hash(self, value: str) -> str:
        """Return a stable SHA-256 digest for the embedded content."""
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def _resolve_dimensions(self, vector: list[float]) -> int:
        """Infer the embedding dimension from the first generated vector."""
        if self._dimensions is None:
            self._dimensions = len(vector)
        return self._dimensions


class PgvectorVectorSearchProvider:
    """Search semantic memory embeddings using pgvector cosine distance."""

    def __init__(
        self,
        database_url: str,
        embedding_provider: EmbeddingProvider,
        *,
        dimensions: int | None = None,
    ) -> None:
        """Initialize the pgvector search provider against PostgreSQL."""
        _validate_postgres_url(database_url)

        self._engine = get_engine(database_url)
        self._embedding_provider = embedding_provider
        self._dimensions = dimensions
        self._schema_ready = False

    async def search(
        self,
        query: str,
        scope: dict[str, str | None] | None = None,
        limit: int = 10,
    ) -> list[str]:
        """Return ranked memory IDs using pgvector cosine distance."""
        normalized_query = query.strip()
        if not normalized_query:
            return []

        embeddings = await self._embedding_provider.embed_texts([normalized_query])
        if not embeddings:
            return []

        vector = embeddings[0]
        dimensions = self._resolve_dimensions(vector)
        if len(vector) != dimensions:
            raise ValueError(
                f"Expected embedding dimension {dimensions}, got {len(vector)}"
            )

        self._ensure_schema()
        vector_literal = _vector_literal(vector)
        where_clauses = ["embedding IS NOT NULL"]
        params: dict[str, object] = {"embedding": vector_literal, "limit": limit}

        if scope:
            if scope.get("project_id"):
                where_clauses.append("project_id = :project_id")
                params["project_id"] = scope["project_id"]
            if scope.get("brain_id"):
                where_clauses.append("brain_id = :brain_id")
                params["brain_id"] = scope["brain_id"]
            if scope.get("niche"):
                where_clauses.append("niche = :niche")
                params["niche"] = scope["niche"]

        statement = text(
            f"""
            SELECT memory_id
            FROM mm_memory_embeddings
            WHERE {" AND ".join(where_clauses)}
            ORDER BY embedding <=> CAST(:embedding AS vector)
            LIMIT :limit
            """
        )

        with self._engine.begin() as connection:
            rows = connection.execute(statement, params).fetchall()

        return [str(row[0]) for row in rows]

    def _ensure_schema(self) -> None:
        """Create pgvector-owned memory embedding structures once."""
        if self._schema_ready:
            return
        if self._dimensions is None:
            raise ValueError("Pgvector schema requires a known embedding dimension")
        _ensure_pgvector_memory_schema(self._engine, self._dimensions)
        self._schema_ready = True

    def _resolve_dimensions(self, vector: list[float]) -> int:
        """Infer the embedding dimension from the first generated vector."""
        if self._dimensions is None:
            self._dimensions = len(vector)
        return self._dimensions


__all__ = ["PgvectorMemoryIndexProvider", "PgvectorVectorSearchProvider"]
