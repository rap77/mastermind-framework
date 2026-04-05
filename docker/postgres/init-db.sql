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

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'MasterMind PostgreSQL database initialized successfully';
END $$;
