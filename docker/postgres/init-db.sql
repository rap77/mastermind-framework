-- MasterMind PostgreSQL Initialization Script
-- Phase 13: Vertical Slice - Executions Table
-- Runs automatically on PostgreSQL container first startup

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create executions table (Rust Control Plane)
CREATE TABLE IF NOT EXISTS executions (
    id TEXT PRIMARY KEY,
    brief TEXT NOT NULL,
    flow_config TEXT NOT NULL,
    user_id TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_executions_user_id ON executions(user_id);
CREATE INDEX IF NOT EXISTS idx_executions_status ON executions(status);
CREATE INDEX IF NOT EXISTS idx_executions_created_at ON executions(created_at DESC);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Phase C1: Central Agent Registry — brain_registry table
CREATE TABLE IF NOT EXISTS brain_registry (
    brain_id        INTEGER     PRIMARY KEY,
    name            TEXT        NOT NULL,
    model_quality   TEXT        NOT NULL,
    model_balanced  TEXT        NOT NULL,
    model_budget    TEXT        NOT NULL,
    capabilities    TEXT[]      NOT NULL DEFAULT '{}',
    trigger_conditions TEXT[]   NOT NULL DEFAULT '{}',
    enabled         BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_brain_registry_enabled
ON brain_registry(enabled) WHERE enabled = TRUE;

CREATE INDEX IF NOT EXISTS idx_brain_registry_capabilities
ON brain_registry USING GIN(capabilities);

CREATE INDEX IF NOT EXISTS idx_brain_registry_trigger_conditions
ON brain_registry USING GIN(trigger_conditions);

-- Phase C1: schema_migrations tracking table
CREATE TABLE IF NOT EXISTS schema_migrations (
    migration_name TEXT PRIMARY KEY,
    applied_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Mark the brain_registry migration as already applied (created here)
INSERT INTO schema_migrations (migration_name)
VALUES ('001_create_brain_registry.sql')
ON CONFLICT DO NOTHING;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'MasterMind PostgreSQL database initialized successfully';
END $$;
