-- MM-Flow PostgreSQL Schema
-- Phase A Day 1: Multi-backend orchestration tables
-- Run: docker exec -i mastermind-postgres-1 psql -U postgres -d mastermind_bd < mm-flow-schema.sql

-- Required extensions (already enabled in init-db.sql)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- ORGANIZATIONS
-- ============================================================================

CREATE TABLE IF NOT EXISTS organizations (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug         VARCHAR(100) UNIQUE NOT NULL,
    name         VARCHAR(255) NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- PROJECTS
-- ============================================================================

CREATE TABLE IF NOT EXISTS projects (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id          UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    slug            VARCHAR(100) NOT NULL,
    name            VARCHAR(255) NOT NULL,
    project_type    VARCHAR(50) NOT NULL DEFAULT 'software',
    metadata        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(org_id, slug)
);

-- ============================================================================
-- WORKSPACES (per project, tracks active branch/session)
-- ============================================================================

CREATE TABLE IF NOT EXISTS workspaces (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id      UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    branch          VARCHAR(255) NOT NULL DEFAULT 'master',
    active_backend  VARCHAR(50) NOT NULL DEFAULT 'claude',
    current_phase   INTEGER NOT NULL DEFAULT 1,
    metadata        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- MM_FLOW_STATE (phase lifecycle state machine)
-- ============================================================================

CREATE TABLE IF NOT EXISTS mm_flow_state (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id          UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    project_id      UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    phase           INTEGER NOT NULL,
    status          VARCHAR(50) NOT NULL DEFAULT 'pending',
    -- status: pending | in_progress | completed | failed | paused
    state_data      JSONB NOT NULL DEFAULT '{}',
    backend_used    VARCHAR(50),
    tokens_consumed INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for fast phase queries
CREATE INDEX IF NOT EXISTS idx_mm_flow_state_org_project_phase
    ON mm_flow_state(org_id, project_id, phase);
CREATE INDEX IF NOT EXISTS idx_mm_flow_state_status
    ON mm_flow_state(status);

-- RLS: only see rows for your org
ALTER TABLE mm_flow_state ENABLE ROW LEVEL SECURITY;

CREATE POLICY mm_flow_state_org_isolation ON mm_flow_state
    USING (org_id = current_setting('mm_flow.org_id', TRUE)::UUID);

-- ============================================================================
-- BACKEND_SESSIONS (token tracking per backend per project)
-- ============================================================================

CREATE TABLE IF NOT EXISTS backend_sessions (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id              UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    project_id          UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    backend             VARCHAR(50) NOT NULL,
    tokens_used         INTEGER NOT NULL DEFAULT 0,
    tokens_limit        INTEGER NOT NULL,
    session_started     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    session_ended       TIMESTAMPTZ,
    last_reset          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    next_reset_time     TIMESTAMPTZ,                          -- Calculated next reset timestamp
    depletion_timestamp TIMESTAMPTZ,                          -- When tokens hit < 5K (for analysis)
    reset_cycle_hours   FLOAT NOT NULL,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Migration helper: add new columns if table already exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'backend_sessions' AND column_name = 'next_reset_time'
    ) THEN
        ALTER TABLE backend_sessions ADD COLUMN next_reset_time TIMESTAMPTZ;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'backend_sessions' AND column_name = 'depletion_timestamp'
    ) THEN
        ALTER TABLE backend_sessions ADD COLUMN depletion_timestamp TIMESTAMPTZ;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_backend_sessions_project_backend
    ON backend_sessions(project_id, backend, is_active);

-- RLS
ALTER TABLE backend_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY backend_sessions_org_isolation ON backend_sessions
    USING (org_id = current_setting('mm_flow.org_id', TRUE)::UUID);

-- ============================================================================
-- BACKEND_CAPABILITIES (static metadata, seeded once)
-- ============================================================================

CREATE TABLE IF NOT EXISTS backend_capabilities (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    backend                 VARCHAR(50) UNIQUE NOT NULL,
    display_name            VARCHAR(255) NOT NULL,
    token_limit             INTEGER NOT NULL,
    tokens_per_minute       INTEGER NOT NULL,
    requests_per_day        INTEGER NOT NULL,
    reset_cycles_per_day    INTEGER NOT NULL DEFAULT 1,
    reset_cycle_hours       FLOAT NOT NULL DEFAULT 24.0,
    priority_order          INTEGER NOT NULL DEFAULT 99,
    metadata                JSONB NOT NULL DEFAULT '{}',
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- CONTEXT_CHECKPOINTS (snapshot state before backend switch)
-- ============================================================================

CREATE TABLE IF NOT EXISTS context_checkpoints (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id                  UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    project_id              UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    workspace_id            UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    phase                   INTEGER NOT NULL,
    reason                  VARCHAR(100) NOT NULL,
    -- reason: backend_switch | periodic | low_tokens | max_errors | night_mode
    state_data              JSONB NOT NULL DEFAULT '{}',
    conversation_history    JSONB NOT NULL DEFAULT '[]',
    from_backend            VARCHAR(50),
    to_backend              VARCHAR(50),
    tokens_at_checkpoint    INTEGER NOT NULL DEFAULT 0,
    embedding               vector(1536),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_context_checkpoints_org_project_phase
    ON context_checkpoints(org_id, project_id, phase);
CREATE INDEX IF NOT EXISTS idx_context_checkpoints_created_at
    ON context_checkpoints(created_at DESC);

-- RLS
ALTER TABLE context_checkpoints ENABLE ROW LEVEL SECURITY;

CREATE POLICY context_checkpoints_org_isolation ON context_checkpoints
    USING (org_id = current_setting('mm_flow.org_id', TRUE)::UUID);

-- ============================================================================
-- BRAIN_CONSULTATIONS (audit trail for brain calls)
-- ============================================================================

CREATE TABLE IF NOT EXISTS brain_consultations (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id                  UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    project_id              UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    phase                   INTEGER NOT NULL,
    brain_id                INTEGER NOT NULL,
    -- brain_id: 1-7 matching the 7 MasterMind brains
    consultation_input      TEXT NOT NULL DEFAULT '',
    consultation_output     TEXT NOT NULL DEFAULT '',
    confidence              FLOAT NOT NULL DEFAULT 0.0,
    validated               BOOLEAN NOT NULL DEFAULT FALSE,
    backend_used            VARCHAR(50),
    tokens_used             INTEGER NOT NULL DEFAULT 0,
    metadata                JSONB NOT NULL DEFAULT '{}',
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_brain_consultations_org_project
    ON brain_consultations(org_id, project_id, phase, brain_id);

-- ============================================================================
-- CROSS_PHASE_CONTRACTS (validation rules between phases)
-- ============================================================================

CREATE TABLE IF NOT EXISTS cross_phase_contracts (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_phase      INTEGER NOT NULL,
    to_phase        INTEGER NOT NULL,
    contract_text   TEXT NOT NULL,
    -- Plain text rule: "from_phase output must include X before to_phase can begin"
    is_required     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(from_phase, to_phase)
);

-- ============================================================================
-- GRANTS
-- ============================================================================

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

DO $$
BEGIN
    RAISE NOTICE 'MM-Flow schema created successfully (9 tables)';
END $$;
