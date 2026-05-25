# Requirements — postgres-hybrid-data-model

## Problem / Purpose
The Rust Control Plane PostgreSQL schema (migrations 001–010) is missing two tables needed
by downstream objectives: `checkpoints` (required by `context-projection`) and
`token_usage_events` (required by `token-cost-quality-telemetry`). This objective adds those
two tables as proper hybrid schema: relational fields for identity/querying + JSONB for
flexible payload fields.

## Stakeholders / Users
- Primary: execution models resuming tasks from checkpoints
- Secondary: operators reading token usage telemetry in the dashboard

## Scope
- Add `checkpoints` table to `rust_control_plane/migrations/` (hybrid: relational + JSONB).
- Add `token_usage_events` table to `rust_control_plane/migrations/` (hybrid: relational + JSONB).
- Add appropriate indexes for query patterns (task_id lookups, session lookups, time ranges).
- No Python FastAPI changes — Python still uses SQLite for its own domain.
- No schema changes to existing tables.

## Out of Scope
- Full SQLite → PostgreSQL migration for the Python FastAPI backend (deferred v3.1+).
- pgvector embedding columns (deferred to `rag-pilot-brain-1-only` objective).
- Projection layer views or API endpoints (deferred to `context-projection` objective).
- Any change to existing migrations 001–010.

## Non-negotiables
- Use sqlx migration conventions already established in `rust_control_plane/migrations/`.
- Migration files must be pure SQL (no Rust code changes required to run them).
- Do not break existing Rust integration tests.
- JSONB fields must not store data that belongs in relational columns.

## Objective-level Acceptance Criteria
- [ ] Migration `011_add_checkpoints.sql` is present and valid SQL.
- [ ] Migration `012_add_token_usage_events.sql` is present and valid SQL.
- [ ] Both migrations follow the hybrid design: relational identity + JSONB payload.
- [ ] Indexes cover the primary query patterns for each table.
- [ ] No existing migration or Rust test is broken.
