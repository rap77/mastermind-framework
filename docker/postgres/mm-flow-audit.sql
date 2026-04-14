-- IMPORTANT: CREATE POLICY statements are NOT idempotent (no IF NOT EXISTS in PostgreSQL).
-- Run this script ONCE only. Re-running will fail on policy creation.
-- To re-apply: DROP the relevant tables/policies first.
--
-- RLS GOTCHA (read before writing FASE 2+ code):
-- All Python transactions touching audit tables (phase_executions, decisions,
-- verification_gates, brain_feedback, dev_sessions, artifacts, phase_metrics)
-- MUST execute: SET LOCAL mm_flow.org_id = '<uuid>' before any DML or SELECT.
-- Without it, RLS policy evaluates org_id = NULL (always false) → zero rows returned silently.
-- See PostgreSQL current_setting() with missing_ok=TRUE behavior.

-- MM-Flow Audit Trail System
-- Comprehensive development history, decisions, sessions, and verification gates
-- Phase A: Audit Trail & Governance Pillar
-- Run: docker exec -i mastermind-postgres-1 psql -U postgres -d mastermind_bd < mm-flow-audit.sql

-- Extensions (already enabled in init-db.sql)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- PHASE_EXECUTIONS: Track each phase run with complete execution metadata
-- ============================================================================

CREATE TABLE IF NOT EXISTS phase_executions (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id              UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    project_id          UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    workspace_id        UUID REFERENCES workspaces(id) ON DELETE SET NULL,
    phase_number        INTEGER NOT NULL,
    execution_number    INTEGER NOT NULL DEFAULT 1,  -- 1st run, 2nd retry, etc.
    status              VARCHAR(50) NOT NULL DEFAULT 'pending',
    -- status: pending | in_progress | completed | failed | rolled_back
    started_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at        TIMESTAMPTZ,
    duration_seconds    INTEGER,
    backend_used        VARCHAR(50),
    tokens_consumed     INTEGER NOT NULL DEFAULT 0,
    tokens_input        INTEGER NOT NULL DEFAULT 0,
    tokens_output       INTEGER NOT NULL DEFAULT 0,
    output_summary      TEXT,                          -- Brief summary of outputs
    error_message       TEXT,                          -- If status = failed
    git_commit_hash     VARCHAR(40),                   -- Commit ID at completion
    triggered_by        VARCHAR(255),                  -- User, scheduler, brain_7, etc.
    metadata            JSONB NOT NULL DEFAULT '{}',  -- Extensible: niche-specific data
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_phase_executions_org_project_phase
    ON phase_executions(org_id, project_id, phase_number);
CREATE INDEX IF NOT EXISTS idx_phase_executions_completed_at
    ON phase_executions(completed_at DESC);
CREATE INDEX IF NOT EXISTS idx_phase_executions_status
    ON phase_executions(status);

ALTER TABLE phase_executions ENABLE ROW LEVEL SECURITY;
CREATE POLICY phase_executions_org_isolation ON phase_executions
    USING (org_id = current_setting('mm_flow.org_id', TRUE)::UUID);

-- ============================================================================
-- DECISIONS: Capture all decisions with rationale, alternatives, confidence
-- ============================================================================

CREATE TABLE IF NOT EXISTS decisions (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id              UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    project_id          UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    phase_execution_id  UUID REFERENCES phase_executions(id) ON DELETE SET NULL,
    decision_type       VARCHAR(100) NOT NULL,
    -- decision_type: architectural | technical | product | process | tool_selection
    title               VARCHAR(255) NOT NULL,
    rationale           TEXT NOT NULL,                 -- Why this decision?
    alternatives        TEXT,                          -- Other options considered
    chosen_option       TEXT NOT NULL,                 -- What we chose
    confidence          FLOAT NOT NULL DEFAULT 0.5,    -- 0.0 to 1.0
    impact_level        VARCHAR(50) NOT NULL DEFAULT 'medium',
    -- impact_level: critical | high | medium | low
    impact_description  TEXT,                          -- How it affects the project
    made_by             VARCHAR(255) NOT NULL,         -- User, Brain #N, decision engine
    approved_by         VARCHAR(255),                  -- Who signed off?
    approval_confidence FLOAT,
    status              VARCHAR(50) NOT NULL DEFAULT 'pending',
    -- status: pending | approved | rejected | superseded | archived
    tags                TEXT[],                        -- For filtering/search
    engram_link         VARCHAR(255),                  -- Reference to engram memory
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_decisions_org_project_phase_execution
    ON decisions(org_id, project_id, phase_execution_id);
CREATE INDEX IF NOT EXISTS idx_decisions_status
    ON decisions(status);
CREATE INDEX IF NOT EXISTS idx_decisions_decision_type
    ON decisions(decision_type);

ALTER TABLE decisions ENABLE ROW LEVEL SECURITY;
CREATE POLICY decisions_org_isolation ON decisions
    USING (org_id = current_setting('mm_flow.org_id', TRUE)::UUID);

-- ============================================================================
-- DEV_SESSIONS: Log development sessions with tasks, commits, discoveries
-- ============================================================================

CREATE TABLE IF NOT EXISTS dev_sessions (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id              UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    project_id          UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    workspace_id        UUID REFERENCES workspaces(id) ON DELETE SET NULL,
    phase_number        INTEGER,                       -- Which phase was being worked on
    session_date        TIMESTAMP NOT NULL DEFAULT NOW(),
    duration_minutes    INTEGER,
    status              VARCHAR(50) NOT NULL DEFAULT 'active',
    -- status: active | paused | completed | abandoned
    started_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at            TIMESTAMPTZ,
    started_by          VARCHAR(255) NOT NULL,         -- User name
    backend_used        VARCHAR(50),
    tokens_consumed     INTEGER NOT NULL DEFAULT 0,
    tasks_completed     INTEGER NOT NULL DEFAULT 0,
    tasks_total         INTEGER NOT NULL DEFAULT 0,
    commits_count       INTEGER NOT NULL DEFAULT 0,
    commit_hashes       TEXT[],                        -- Array of git commit hashes
    discoveries         TEXT,                          -- Key findings/learnings
    blockers            TEXT,                          -- Issues encountered
    next_steps          TEXT,                          -- What to do next
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dev_sessions_org_project
    ON dev_sessions(org_id, project_id);
CREATE INDEX IF NOT EXISTS idx_dev_sessions_date
    ON dev_sessions(session_date DESC);
CREATE INDEX IF NOT EXISTS idx_dev_sessions_phase
    ON dev_sessions(phase_number);

ALTER TABLE dev_sessions ENABLE ROW LEVEL SECURITY;
CREATE POLICY dev_sessions_org_isolation ON dev_sessions
    USING (org_id = current_setting('mm_flow.org_id', TRUE)::UUID);

-- ============================================================================
-- VERIFICATION_GATES: Brain #7 quality gates and automated checks
-- ============================================================================

CREATE TABLE IF NOT EXISTS verification_gates (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id              UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    project_id          UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    phase_execution_id  UUID NOT NULL REFERENCES phase_executions(id) ON DELETE CASCADE,
    gate_type           VARCHAR(100) NOT NULL,
    -- gate_type: test_coverage | security_scan | performance | spec_compliance | brain_7_approval | contract_validation
    gate_name           VARCHAR(255) NOT NULL,
    description         TEXT,
    required            BOOLEAN NOT NULL DEFAULT TRUE,
    status              VARCHAR(50) NOT NULL DEFAULT 'pending',
    -- status: pending | running | passed | failed | waived
    result              JSONB NOT NULL DEFAULT '{}',  -- Gate-specific results
    -- test_coverage: { "covered": 85, "required": 80, "status": "PASS" }
    -- security_scan: { "vulnerabilities": 0, "status": "PASS" }
    -- performance: { "metrics": {...}, "status": "PASS" }
    score               FLOAT,                         -- 0.0 to 1.0
    evaluated_by        VARCHAR(255),                  -- Brain #7 or automated process
    evaluation_notes    TEXT,
    retry_count         INTEGER NOT NULL DEFAULT 0,
    max_retries         INTEGER NOT NULL DEFAULT 1,
    waived_by           VARCHAR(255),                  -- Who waived this gate?
    waive_reason        TEXT,
    executed_at         TIMESTAMPTZ,
    completed_at        TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_verification_gates_org_project_phase
    ON verification_gates(org_id, project_id, phase_execution_id);
CREATE INDEX IF NOT EXISTS idx_verification_gates_status
    ON verification_gates(status);
CREATE INDEX IF NOT EXISTS idx_verification_gates_gate_type
    ON verification_gates(gate_type);

ALTER TABLE verification_gates ENABLE ROW LEVEL SECURITY;
CREATE POLICY verification_gates_org_isolation ON verification_gates
    USING (org_id = current_setting('mm_flow.org_id', TRUE)::UUID);

-- ============================================================================
-- ARTIFACTS: Track generated files (plans, specs, tests, docs) with links
-- ============================================================================

CREATE TABLE IF NOT EXISTS artifacts (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id              UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    project_id          UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    phase_execution_id  UUID REFERENCES phase_executions(id) ON DELETE SET NULL,
    artifact_type       VARCHAR(100) NOT NULL,
    -- artifact_type: plan | spec | test | doc | report | design | guide | other
    name                VARCHAR(255) NOT NULL,
    description         TEXT,
    file_path           VARCHAR(512),                  -- Relative path in repo
    file_size_bytes     INTEGER,
    file_hash           VARCHAR(64),                   -- SHA-256 for integrity
    git_commit_hash     VARCHAR(40),                   -- Commit where artifact was created
    git_commit_message  TEXT,
    created_by          VARCHAR(255),                  -- User or Brain #N
    related_decision_id UUID REFERENCES decisions(id) ON DELETE SET NULL,
    metadata            JSONB NOT NULL DEFAULT '{}',  -- Version, status, etc.
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_artifacts_org_project_phase
    ON artifacts(org_id, project_id, phase_execution_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_artifact_type
    ON artifacts(artifact_type);
CREATE INDEX IF NOT EXISTS idx_artifacts_created_at
    ON artifacts(created_at DESC);

ALTER TABLE artifacts ENABLE ROW LEVEL SECURITY;
CREATE POLICY artifacts_org_isolation ON artifacts
    USING (org_id = current_setting('mm_flow.org_id', TRUE)::UUID);

-- ============================================================================
-- PHASE_METRICS: Niche-specific KPIs per phase (extensible)
-- ============================================================================

CREATE TABLE IF NOT EXISTS phase_metrics (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id              UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    project_id          UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    phase_execution_id  UUID NOT NULL REFERENCES phase_executions(id) ON DELETE CASCADE,
    niche               VARCHAR(100) NOT NULL,         -- 'software', 'saas', 'hardware'
    metric_name         VARCHAR(255) NOT NULL,
    -- software: test_coverage, cyclomatic_complexity, code_review_approval_time
    -- saas: deployment_success_rate, uptime_percentage, mrr_impact
    -- hardware: manufacturing_yield, defect_rate, time_to_production
    metric_value        FLOAT,
    metric_unit         VARCHAR(50),                   -- '%', 'ms', 'days', 'count'
    target_value        FLOAT,
    status              VARCHAR(50),                   -- 'pass' | 'warn' | 'fail'
    description         TEXT,
    metadata            JSONB NOT NULL DEFAULT '{}',
    measured_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_phase_metrics_org_project_phase
    ON phase_metrics(org_id, project_id, phase_execution_id);
CREATE INDEX IF NOT EXISTS idx_phase_metrics_niche_metric
    ON phase_metrics(niche, metric_name);

ALTER TABLE phase_metrics ENABLE ROW LEVEL SECURITY;
CREATE POLICY phase_metrics_org_isolation ON phase_metrics
    USING (org_id = current_setting('mm_flow.org_id', TRUE)::UUID);

-- ============================================================================
-- AUDIT_LOG: High-level audit log for compliance/traceability
-- ============================================================================

CREATE TABLE IF NOT EXISTS audit_log (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id              UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    project_id          UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    action_type         VARCHAR(100) NOT NULL,
    -- action_type: phase_started | phase_completed | decision_made | gate_passed | gate_failed | artifact_created | session_started | session_ended
    actor                VARCHAR(255) NOT NULL,         -- User name or system
    actor_type          VARCHAR(50),                   -- 'user' | 'brain' | 'system'
    description         TEXT NOT NULL,
    phase_number        INTEGER,
    related_entity_type VARCHAR(100),                  -- 'phase_execution' | 'decision' | 'verification_gate'
    related_entity_id   UUID,
    severity            VARCHAR(50) DEFAULT 'info',
    -- severity: info | warning | error | critical
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_log_org_project
    ON audit_log(org_id, project_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at
    ON audit_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_log_action_type
    ON audit_log(action_type);

ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY audit_log_org_isolation ON audit_log
    USING (org_id = current_setting('mm_flow.org_id', TRUE)::UUID);

-- ============================================================================
-- BRAIN_FEEDBACK: Engram sync target - decisions from brain agents
-- ============================================================================

CREATE TABLE IF NOT EXISTS brain_feedback (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id              UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    project_id          UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    phase_execution_id  UUID REFERENCES phase_executions(id) ON DELETE SET NULL,
    brain_id            INTEGER NOT NULL,              -- 1-7 for dev, 8-23 for marketing, etc.
    feedback_type       VARCHAR(100) NOT NULL,
    -- feedback_type: insight | risk_flag | opportunity | lesson_learned | recommendation
    title               VARCHAR(255) NOT NULL,
    content             TEXT NOT NULL,
    confidence          FLOAT,
    impact_on_phase     VARCHAR(100),                  -- 'critical' | 'high' | 'medium' | 'low'
    engram_sync_id      VARCHAR(255),                  -- Reference to engram observation
    engram_synced_at    TIMESTAMPTZ,
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_brain_feedback_org_project_phase
    ON brain_feedback(org_id, project_id, phase_execution_id);
CREATE INDEX IF NOT EXISTS idx_brain_feedback_brain_id
    ON brain_feedback(brain_id);

ALTER TABLE brain_feedback ENABLE ROW LEVEL SECURITY;
CREATE POLICY brain_feedback_org_isolation ON brain_feedback
    USING (org_id = current_setting('mm_flow.org_id', TRUE)::UUID);

-- ============================================================================
-- NICHE_METRICS_CONFIG: Define which metrics apply to each niche
-- ============================================================================

CREATE TABLE IF NOT EXISTS niche_metrics_config (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    niche               VARCHAR(100) NOT NULL UNIQUE,  -- 'software', 'saas', 'hardware'
    metrics             JSONB NOT NULL DEFAULT '{}',  -- Array of metric definitions
    -- Example:
    -- {
    --   "metrics": [
    --     { "name": "test_coverage", "unit": "%", "target": 80, "weight": 0.3 },
    --     { "name": "uptime", "unit": "%", "target": 99.9, "weight": 0.4 }
    --   ]
    -- }
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Seed niche configs
INSERT INTO niche_metrics_config (niche, metrics) VALUES
(
    'software',
    '{
      "metrics": [
        {"name": "test_coverage", "unit": "%", "target": 80, "weight": 0.3},
        {"name": "code_review_time", "unit": "hours", "target": 24, "weight": 0.2},
        {"name": "cyclomatic_complexity", "unit": "score", "target": 10, "weight": 0.2},
        {"name": "security_vulnerabilities", "unit": "count", "target": 0, "weight": 0.3}
      ]
    }'::jsonb
)
ON CONFLICT (niche) DO NOTHING;

INSERT INTO niche_metrics_config (niche, metrics) VALUES
(
    'saas',
    '{
      "metrics": [
        {"name": "deployment_success_rate", "unit": "%", "target": 99, "weight": 0.3},
        {"name": "uptime", "unit": "%", "target": 99.9, "weight": 0.4},
        {"name": "mrr_impact", "unit": "$", "target": 5000, "weight": 0.3}
      ]
    }'::jsonb
)
ON CONFLICT (niche) DO NOTHING;

INSERT INTO niche_metrics_config (niche, metrics) VALUES
(
    'hardware',
    '{
      "metrics": [
        {"name": "manufacturing_yield", "unit": "%", "target": 95, "weight": 0.4},
        {"name": "defect_rate", "unit": "ppm", "target": 100, "weight": 0.3},
        {"name": "time_to_production", "unit": "weeks", "target": 8, "weight": 0.3}
      ]
    }'::jsonb
)
ON CONFLICT (niche) DO NOTHING;

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Timeline view: all significant events in order
CREATE OR REPLACE VIEW phase_execution_timeline AS
SELECT
    org_id,
    project_id,
    phase_number,
    'phase_started' AS event_type,
    started_at AS event_at,
    'Phase ' || phase_number || ' execution started' AS description,
    id::TEXT AS entity_id
FROM phase_executions
WHERE status != 'pending'
UNION ALL
SELECT
    org_id,
    project_id,
    phase_number,
    'decision_made' AS event_type,
    updated_at AS event_at,
    'Decision: ' || title AS description,
    id::TEXT AS entity_id
FROM decisions
WHERE status IN ('approved', 'pending')
UNION ALL
SELECT
    org_id,
    project_id,
    phase_execution_id::TEXT::INTEGER,
    'gate_evaluated' AS event_type,
    completed_at AS event_at,
    gate_type || ' gate: ' || status AS description,
    id::TEXT AS entity_id
FROM verification_gates
WHERE completed_at IS NOT NULL
ORDER BY org_id, project_id, phase_number, event_at DESC;

-- Session summary view
CREATE OR REPLACE VIEW session_summary AS
SELECT
    id,
    org_id,
    project_id,
    phase_number,
    started_at,
    ended_at,
    duration_minutes,
    tasks_completed,
    commits_count,
    discoveries,
    blockers,
    ROW_NUMBER() OVER (PARTITION BY org_id, project_id ORDER BY started_at DESC) AS session_rank
FROM dev_sessions;

-- ============================================================================
-- GRANTS AND PERMISSIONS
-- ============================================================================

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO postgres;

-- ============================================================================
-- FINAL NOTIFICATION
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE 'MM-Flow Audit Trail schema created successfully';
    RAISE NOTICE '  - 8 audit tables (phase_executions, decisions, dev_sessions, verification_gates, artifacts, phase_metrics, audit_log, brain_feedback)';
    RAISE NOTICE '  - 1 config table (niche_metrics_config)';
    RAISE NOTICE '  - 2 views (phase_execution_timeline, session_summary)';
    RAISE NOTICE '  - All tables have RLS policies for org isolation';
END $$;
