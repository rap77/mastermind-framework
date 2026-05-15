-- Migration 001: Create brain_embeddings table
-- Phase 20A - pgvector RAG Foundation

-- Ensure pgvector extension is enabled
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS brain_embeddings (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    brain_id        TEXT        NOT NULL,
    collection_type TEXT        NOT NULL CHECK (collection_type IN ('domain_knowledge', 'project_memory')),
    source_ref      TEXT,
    chunk_text      TEXT        NOT NULL,
    chunk_hash      TEXT        UNIQUE NOT NULL,
    embedding       vector(768),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- HNSW index for cosine similarity search (Phase 20A)
-- m=16: trade-off between build time and recall quality
-- ef_construction=64: higher = better recall during build, slower construction
CREATE INDEX IF NOT EXISTS idx_brain_embeddings_hnsw
    ON brain_embeddings
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Index for brain_id + collection_type filtering (most common query pattern)
CREATE INDEX IF NOT EXISTS idx_brain_embeddings_brain_collection
    ON brain_embeddings (brain_id, collection_type);
