-- ============================================================
-- SCHEMA REAL — MasterMind PostgreSQL (extraído 2026-04-22)
-- Fuente: dump directo de la BD (no hay migrations — schema
-- fue aplicado directamente con psql)
-- ============================================================
-- Host: localhost:5433
-- Database: mastermind_bd
-- User: postgres
-- Password: devpassword (dev only)
-- ============================================================

-- ============================================================
-- DATOS SEMILLA — IDs fijos (determinísticos)
-- ============================================================
-- organizations:
--   RAP Software  → a0000000-0000-0000-0000-000000000001
--   Prosell C.A.  → a0000000-0000-0000-0000-000000000002
--
-- projects:
--   MasterMind Framework → b0000000-0000-0000-0000-000000000001
--     org_id: a0000000-0000-0000-0000-000000000001
--   Prosell E-Commerce   → b0000000-0000-0000-0000-000000000002
--     org_id: a0000000-0000-0000-0000-000000000002
-- ============================================================

-- ============================================================
-- NOTA CRÍTICA: Row Level Security (RLS)
-- Las tablas artifacts, backend_sessions, decisions, dev_sessions
-- tienen RLS activado. Para queries directas (bypass RLS),
-- conectar como superuser (postgres). Para queries con RLS,
-- establecer la variable de sesión ANTES de cada query:
--   SET mm_flow.org_id = 'a0000000-0000-0000-0000-000000000001';
-- db_client.py conecta como postgres → bypass RLS automático.
-- ============================================================

-- ============================================================
-- ORGANIZATIONS
-- ============================================================
CREATE TABLE public.organizations (
    id           uuid                     DEFAULT uuid_generate_v4() NOT NULL,
    slug         character varying(100)   NOT NULL,
    name         character varying(255)   NOT NULL,
    created_at   timestamp with time zone DEFAULT now() NOT NULL,
    updated_at   timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT organizations_pkey PRIMARY KEY (id),
    CONSTRAINT organizations_slug_key UNIQUE (slug)
);

-- ============================================================
-- PROJECTS
-- Required on INSERT: org_id, slug, name
-- Optional (have defaults): project_type='software', metadata='{}'
-- ============================================================
CREATE TABLE public.projects (
    id           uuid                     DEFAULT uuid_generate_v4() NOT NULL,
    org_id       uuid                     NOT NULL,
    slug         character varying(100)   NOT NULL,
    name         character varying(255)   NOT NULL,
    project_type character varying(50)    DEFAULT 'software' NOT NULL,
    metadata     jsonb                    DEFAULT '{}' NOT NULL,
    created_at   timestamp with time zone DEFAULT now() NOT NULL,
    updated_at   timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT projects_pkey PRIMARY KEY (id),
    CONSTRAINT projects_org_id_slug_key UNIQUE (org_id, slug),
    CONSTRAINT projects_org_id_fkey FOREIGN KEY (org_id) REFERENCES organizations(id) ON DELETE CASCADE
);

-- ============================================================
-- WORKSPACES
-- Required on INSERT: project_id
-- Optional (have defaults): branch='master', active_backend='claude',
--   current_phase=1, metadata='{}'
-- ============================================================
CREATE TABLE public.workspaces (
    id             uuid                     DEFAULT uuid_generate_v4() NOT NULL,
    project_id     uuid                     NOT NULL,
    branch         character varying(255)   DEFAULT 'master' NOT NULL,
    active_backend character varying(50)    DEFAULT 'claude' NOT NULL,
    current_phase  integer                  DEFAULT 1 NOT NULL,
    metadata       jsonb                    DEFAULT '{}' NOT NULL,
    created_at     timestamp with time zone DEFAULT now() NOT NULL,
    updated_at     timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT workspaces_pkey PRIMARY KEY (id),
    CONSTRAINT workspaces_project_id_fkey FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- ============================================================
-- BRAIN_CONSULTATIONS
-- Required on INSERT: org_id, project_id, phase, brain_id
-- Optional (have defaults): consultation_input='', consultation_output='',
--   confidence=0.0, validated=false, tokens_used=0, metadata='{}'
-- ============================================================
CREATE TABLE public.brain_consultations (
    id                   uuid                     DEFAULT uuid_generate_v4() NOT NULL,
    org_id               uuid                     NOT NULL,
    project_id           uuid                     NOT NULL,
    phase                integer                  NOT NULL,
    brain_id             integer                  NOT NULL,
    consultation_input   text                     DEFAULT '' NOT NULL,
    consultation_output  text                     DEFAULT '' NOT NULL,
    confidence           double precision         DEFAULT 0.0 NOT NULL,
    validated            boolean                  DEFAULT false NOT NULL,
    backend_used         character varying(50),
    tokens_used          integer                  DEFAULT 0 NOT NULL,
    metadata             jsonb                    DEFAULT '{}' NOT NULL,
    created_at           timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT brain_consultations_pkey PRIMARY KEY (id),
    CONSTRAINT brain_consultations_org_id_fkey FOREIGN KEY (org_id) REFERENCES organizations(id) ON DELETE CASCADE,
    CONSTRAINT brain_consultations_project_id_fkey FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
-- Index: (org_id, project_id, phase, brain_id)

-- ============================================================
-- BACKEND_SESSIONS
-- Required on INSERT: org_id, project_id, backend, tokens_limit, reset_cycle_hours
-- Optional (have defaults): tokens_used=0, session_started=now(),
--   is_active=true, metadata='{}'
-- COLUMN NOTE: uses 'backend' (NOT 'provider'), 'session_ended' (NOT 'expires_at')
-- RLS: requires SET mm_flow.org_id = '...' or superuser connection
-- ============================================================
CREATE TABLE public.backend_sessions (
    id                   uuid                     DEFAULT uuid_generate_v4() NOT NULL,
    org_id               uuid                     NOT NULL,
    project_id           uuid                     NOT NULL,
    backend              character varying(50)    NOT NULL,   -- 'claude' | 'openrouter' | 'z_ai'
    tokens_used          integer                  DEFAULT 0 NOT NULL,
    tokens_limit         integer                  NOT NULL,
    session_started      timestamp with time zone DEFAULT now() NOT NULL,
    session_ended        timestamp with time zone,            -- NULL = still active
    last_reset           timestamp with time zone DEFAULT now() NOT NULL,
    reset_cycle_hours    double precision         NOT NULL,
    is_active            boolean                  DEFAULT true NOT NULL,
    metadata             jsonb                    DEFAULT '{}' NOT NULL,
    created_at           timestamp with time zone DEFAULT now() NOT NULL,
    updated_at           timestamp with time zone DEFAULT now() NOT NULL,
    next_reset_time      timestamp with time zone,
    depletion_timestamp  timestamp with time zone,
    CONSTRAINT backend_sessions_pkey PRIMARY KEY (id),
    CONSTRAINT backend_sessions_org_id_fkey FOREIGN KEY (org_id) REFERENCES organizations(id) ON DELETE CASCADE,
    CONSTRAINT backend_sessions_project_id_fkey FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
-- Index: (project_id, backend, is_active)
-- RLS policy: org_id = current_setting('mm_flow.org_id')::uuid

-- ============================================================
-- DECISIONS
-- Required on INSERT: org_id, project_id, decision_type, title,
--   rationale, chosen_option, made_by
-- Optional (have defaults): confidence=0.5, impact_level='medium',
--   status='pending'
-- Optional (nullable): phase_execution_id, alternatives,
--   impact_description, approved_by, approval_confidence, tags, engram_link
-- RLS: requires SET mm_flow.org_id = '...' or superuser connection
-- ============================================================
CREATE TABLE public.decisions (
    id                   uuid                     DEFAULT uuid_generate_v4() NOT NULL,
    org_id               uuid                     NOT NULL,
    project_id           uuid                     NOT NULL,
    phase_execution_id   uuid,
    decision_type        character varying(100)   NOT NULL,
    title                character varying(255)   NOT NULL,
    rationale            text                     NOT NULL,
    alternatives         text,
    chosen_option        text                     NOT NULL,
    confidence           double precision         DEFAULT 0.5 NOT NULL,
    impact_level         character varying(50)    DEFAULT 'medium' NOT NULL,
    impact_description   text,
    made_by              character varying(255)   NOT NULL,
    approved_by          character varying(255),
    approval_confidence  double precision,
    status               character varying(50)    DEFAULT 'pending' NOT NULL,
    tags                 text[],
    engram_link          character varying(255),
    created_at           timestamp with time zone DEFAULT now() NOT NULL,
    updated_at           timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT decisions_pkey PRIMARY KEY (id),
    CONSTRAINT decisions_org_id_fkey FOREIGN KEY (org_id) REFERENCES organizations(id) ON DELETE CASCADE,
    CONSTRAINT decisions_project_id_fkey FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    CONSTRAINT decisions_phase_execution_id_fkey FOREIGN KEY (phase_execution_id) REFERENCES phase_executions(id) ON DELETE SET NULL
);
-- RLS policy: org_id = current_setting('mm_flow.org_id')::uuid

-- ============================================================
-- ARTIFACTS
-- Required on INSERT: org_id, project_id, artifact_type, name
-- Optional (have defaults): metadata='{}'
-- Optional (nullable): phase_execution_id, description, file_path,
--   file_size_bytes, file_hash, git_commit_hash, git_commit_message,
--   created_by, related_decision_id
-- COLUMN NOTE: NO 'content' column — use file_path + description
-- RLS: requires SET mm_flow.org_id = '...' or superuser connection
-- ============================================================
CREATE TABLE public.artifacts (
    id                   uuid                     DEFAULT uuid_generate_v4() NOT NULL,
    org_id               uuid                     NOT NULL,
    project_id           uuid                     NOT NULL,
    phase_execution_id   uuid,
    artifact_type        character varying(100)   NOT NULL,
    name                 character varying(255)   NOT NULL,
    description          text,
    file_path            character varying(512),
    file_size_bytes      integer,
    file_hash            character varying(64),
    git_commit_hash      character varying(40),
    git_commit_message   text,
    created_by           character varying(255),
    related_decision_id  uuid,
    metadata             jsonb                    DEFAULT '{}' NOT NULL,
    created_at           timestamp with time zone DEFAULT now() NOT NULL,
    updated_at           timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT artifacts_pkey PRIMARY KEY (id),
    CONSTRAINT artifacts_org_id_fkey FOREIGN KEY (org_id) REFERENCES organizations(id) ON DELETE CASCADE,
    CONSTRAINT artifacts_project_id_fkey FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    CONSTRAINT artifacts_phase_execution_id_fkey FOREIGN KEY (phase_execution_id) REFERENCES phase_executions(id) ON DELETE SET NULL,
    CONSTRAINT artifacts_related_decision_id_fkey FOREIGN KEY (related_decision_id) REFERENCES decisions(id) ON DELETE SET NULL
);
-- RLS policy: org_id = current_setting('mm_flow.org_id')::uuid

-- ============================================================
-- DEV_SESSIONS
-- Required on INSERT: org_id, project_id, started_by
-- Optional (have defaults): status='active', session_date=now(),
--   started_at=now(), tokens_consumed=0, tasks_completed=0,
--   tasks_total=0, commits_count=0, metadata='{}'
-- Optional (nullable): workspace_id, phase_number, duration_minutes,
--   ended_at, backend_used, commit_hashes, discoveries, blockers,
--   next_steps
-- COLUMN NOTE: NO 'session_id', 'state_data', 'expires_at' — uses 'id', 'metadata', 'ended_at'
-- RLS: requires SET mm_flow.org_id = '...' or superuser connection
-- ============================================================
CREATE TABLE public.dev_sessions (
    id               uuid                          DEFAULT uuid_generate_v4() NOT NULL,
    org_id           uuid                          NOT NULL,
    project_id       uuid                          NOT NULL,
    workspace_id     uuid,
    phase_number     integer,
    session_date     timestamp without time zone   DEFAULT now() NOT NULL,
    duration_minutes integer,
    status           character varying(50)         DEFAULT 'active' NOT NULL,
    started_at       timestamp with time zone      DEFAULT now() NOT NULL,
    ended_at         timestamp with time zone,
    started_by       character varying(255)        NOT NULL,
    backend_used     character varying(50),
    tokens_consumed  integer                       DEFAULT 0 NOT NULL,
    tasks_completed  integer                       DEFAULT 0 NOT NULL,
    tasks_total      integer                       DEFAULT 0 NOT NULL,
    commits_count    integer                       DEFAULT 0 NOT NULL,
    commit_hashes    text[],
    discoveries      text,
    blockers         text,
    next_steps       text,
    metadata         jsonb                         DEFAULT '{}' NOT NULL,
    created_at       timestamp with time zone      DEFAULT now() NOT NULL,
    updated_at       timestamp with time zone      DEFAULT now() NOT NULL,
    CONSTRAINT dev_sessions_pkey PRIMARY KEY (id),
    CONSTRAINT dev_sessions_org_id_fkey FOREIGN KEY (org_id) REFERENCES organizations(id) ON DELETE CASCADE,
    CONSTRAINT dev_sessions_project_id_fkey FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    CONSTRAINT dev_sessions_workspace_id_fkey FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE SET NULL
);
-- RLS policy: org_id = current_setting('mm_flow.org_id')::uuid

-- ============================================================
-- EXPERIENCE_RECORDS
-- Required on INSERT: brain_id (TEXT), session_id (UUID)
-- Optional (nullable): quality_score, insights='[]', patterns='[]'
-- COLUMN NOTE: brain_id is TEXT (e.g. 'brain-01-product'), NOT integer
-- NO 'project_id', 'experience', 'context' columns
-- ============================================================
CREATE TABLE public.experience_records (
    id            uuid                     DEFAULT gen_random_uuid() NOT NULL,
    brain_id      text                     NOT NULL,   -- e.g. 'brain-01-product'
    session_id    uuid                     NOT NULL,
    quality_score real,
    insights      jsonb                    DEFAULT '[]',
    patterns      jsonb                    DEFAULT '[]',
    created_at    timestamp with time zone DEFAULT now(),
    CONSTRAINT experience_records_pkey PRIMARY KEY (id)
);
-- Index: brain_id, created_at
