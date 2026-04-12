-- MM-Flow Seed Data
-- Phase A Day 1: Initial organizations, projects, workspaces + backend capabilities
-- Run after mm-flow-schema.sql

-- ============================================================================
-- ORGANIZATIONS
-- ============================================================================

INSERT INTO organizations (id, slug, name) VALUES
    ('a0000000-0000-0000-0000-000000000001', 'acme-corp',    'Acme Corp'),
    ('a0000000-0000-0000-0000-000000000002', 'prosell-sass', 'Prosell SaaS')
ON CONFLICT (slug) DO NOTHING;

-- ============================================================================
-- PROJECTS
-- ============================================================================

INSERT INTO projects (id, org_id, slug, name, project_type) VALUES
    (
        'b0000000-0000-0000-0000-000000000001',
        'a0000000-0000-0000-0000-000000000001',
        'mastermind',
        'MasterMind Framework',
        'software'
    ),
    (
        'b0000000-0000-0000-0000-000000000002',
        'a0000000-0000-0000-0000-000000000002',
        'paperclip-v3',
        'Paperclip Clone v3.0',
        'software'
    )
ON CONFLICT (org_id, slug) DO NOTHING;

-- ============================================================================
-- WORKSPACES
-- ============================================================================

INSERT INTO workspaces (id, project_id, branch, active_backend, current_phase) VALUES
    (
        'c0000000-0000-0000-0000-000000000001',
        'b0000000-0000-0000-0000-000000000001',
        'master',
        'claude',
        19
    ),
    (
        'c0000000-0000-0000-0000-000000000002',
        'b0000000-0000-0000-0000-000000000002',
        'master',
        'claude',
        1
    )
ON CONFLICT DO NOTHING;

-- ============================================================================
-- BACKEND_CAPABILITIES (static config from config.py)
-- ============================================================================

INSERT INTO backend_capabilities
    (backend, display_name, token_limit, tokens_per_minute, requests_per_day,
     reset_cycles_per_day, reset_cycle_hours, priority_order)
VALUES
    ('z_ai',       'z.ai (Fast inference)',    200000, 100000, 20000, 5, 4.8,  1),
    ('openrouter', 'OpenRouter (Multi-model)', 128000,  40000,  5000, 1, 24.0, 2),
    ('claude',     'Claude (Anthropic)',        100000,  50000, 10000, 1, 24.0, 3)
ON CONFLICT (backend) DO UPDATE SET
    token_limit           = EXCLUDED.token_limit,
    tokens_per_minute     = EXCLUDED.tokens_per_minute,
    requests_per_day      = EXCLUDED.requests_per_day,
    reset_cycles_per_day  = EXCLUDED.reset_cycles_per_day,
    reset_cycle_hours     = EXCLUDED.reset_cycle_hours,
    priority_order        = EXCLUDED.priority_order;

-- ============================================================================
-- BACKEND_SESSIONS (initial sessions for mastermind project)
-- ============================================================================

INSERT INTO backend_sessions
    (org_id, project_id, backend, tokens_used, tokens_limit, reset_cycle_hours, is_active)
VALUES
    ('a0000000-0000-0000-0000-000000000001',
     'b0000000-0000-0000-0000-000000000001',
     'z_ai',       0, 200000, 4.8,  TRUE),
    ('a0000000-0000-0000-0000-000000000001',
     'b0000000-0000-0000-0000-000000000001',
     'openrouter',  0, 128000, 24.0, FALSE),
    ('a0000000-0000-0000-0000-000000000001',
     'b0000000-0000-0000-0000-000000000001',
     'claude',      0, 100000, 24.0, FALSE)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- CROSS_PHASE_CONTRACTS (basic validation rules)
-- ============================================================================

INSERT INTO cross_phase_contracts (from_phase, to_phase, contract_text) VALUES
    (1,  2,  'Phase 1 (Discussion) must produce a validated problem statement and user stories before Phase 2 (Planning) begins.'),
    (2,  3,  'Phase 2 (Planning) must produce an approved technical design with task breakdown before Phase 3 (Execution) begins.'),
    (3,  4,  'Phase 3 (Execution) must pass Brain #7 quality gate with confidence >= 0.7 before Phase 4 (Verification) begins.'),
    (4,  5,  'Phase 4 (Verification) must confirm all acceptance criteria are met before Phase 5 can begin.'),
    (18, 19, 'Phase 18 (Multi-channel Gateway) must be complete with all tests passing before Phase 19 begins.')
ON CONFLICT (from_phase, to_phase) DO NOTHING;

DO $$
BEGIN
    RAISE NOTICE 'MM-Flow seed data inserted: 2 orgs, 2 projects, 2 workspaces, 3 backends, 3 sessions';
END $$;
