-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT valid_role CHECK (role IN ('admin', 'user'))
);

-- Sessions table (for JWT refresh tokens)
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    refresh_token_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    rotation_count INTEGER DEFAULT 0
);

-- API keys table
CREATE TABLE api_keys (
    key_hash TEXT PRIMARY KEY,
    owner TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    scopes JSONB DEFAULT '[]'::jsonb
);

-- Tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brain_id TEXT NOT NULL,
    status TEXT NOT NULL,
    progress JSONB DEFAULT '{}'::jsonb,
    result JSONB,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Executions table
CREATE TABLE executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    flow_config JSONB NOT NULL,
    brief TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    status TEXT NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Experience records table (from Phase 14)
CREATE TABLE experience_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brain_id TEXT NOT NULL,
    session_id UUID NOT NULL,
    quality_score REAL,
    insights JSONB DEFAULT '[]'::jsonb,
    patterns JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Activity log table (for event sourcing - RCP-03)
CREATE TABLE activity_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brain_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_brain_id ON tasks(brain_id);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);
CREATE INDEX idx_experience_records_brain_id ON experience_records(brain_id);
CREATE INDEX idx_experience_records_created_at ON experience_records(created_at);
CREATE INDEX idx_activity_log_brain_id ON activity_log(brain_id);
CREATE INDEX idx_activity_log_created_at ON activity_log(created_at);
CREATE INDEX idx_activity_log_event_type ON activity_log(event_type);
CREATE INDEX idx_users_role ON users(role);
