-- MasterMind Framework — PostgreSQL schema
-- Migration target from SQLite (v3.0+)
-- pgvector extension for semantic search on ExperienceRecord embeddings

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Placeholder: schema will be generated from Pydantic models via migration tool
-- See apps/api/mastermind_cli/state/ for current SQLite schema
