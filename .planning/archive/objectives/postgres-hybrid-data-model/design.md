# Design — postgres-hybrid-data-model

## Architecture / Boundaries
- All changes are limited to `rust_control_plane/migrations/` — two new `.sql` files.
- No Rust source changes required for migration files to be applied.
- Python FastAPI backend remains on SQLite; no cross-service schema dependencies introduced.

## Technical Approach

### Migration file naming convention
Follow the existing sequence: next is `011_add_checkpoints.sql`, then `012_add_token_usage_events.sql`.

### checkpoints table (hybrid)
Relational fields (identity + querying):
- `id` UUID PK
- `project_id` UUID (nullable FK to future projects table)
- `task_id` TEXT NOT NULL (references the MM task id, e.g. "T1")
- `session_id` UUID NOT NULL
- `created_at` TIMESTAMPTZ DEFAULT NOW()

JSONB fields (flexible payload):
- `resume_state` JSONB NOT NULL — context summary, next step, open questions, constraints

Indexes:
- `idx_checkpoints_task_id` on `task_id`
- `idx_checkpoints_session_id` on `session_id`
- `idx_checkpoints_created_at` on `created_at`

### token_usage_events table (hybrid)
Relational fields:
- `id` UUID PK
- `brain_id` TEXT NOT NULL
- `session_id` UUID
- `model` TEXT NOT NULL
- `input_tokens` INTEGER NOT NULL
- `output_tokens` INTEGER NOT NULL
- `cache_read_tokens` INTEGER DEFAULT 0
- `cache_write_tokens` INTEGER DEFAULT 0
- `created_at` TIMESTAMPTZ DEFAULT NOW()

JSONB fields:
- `provider_metadata` JSONB DEFAULT '{}'::jsonb — cache info, request ids, pricing snapshot

Indexes:
- `idx_token_usage_brain_id` on `brain_id`
- `idx_token_usage_session_id` on `session_id`
- `idx_token_usage_created_at` on `created_at`
- `idx_token_usage_model` on `model`

## Dependencies
- Depends on `project-state-mvp` (done)
- Enables: `context-projection`, `token-cost-quality-telemetry`

## Validation Strategy
- SQL syntax check: `psql --dry-run` or review manually (no running PG instance required in dev).
- Rust test suite: `cargo test -p rust_control_plane` — must pass without changes.
- Migration content review: verify relational vs JSONB split matches canonical doc 27.

## Important Tradeoffs
- `task_id` is TEXT (not UUID FK) to decouple from a future `planning_tasks` table — avoids
  blocking this migration on a larger schema design decision.
- `project_id` is nullable UUID — allows checkpoints to exist before a projects table is added.
- No pgvector columns yet — deferred to the RAG objectives to avoid premature indexing cost.

## Context Notes
- Canonical design reference: `docs/canonical/27-POSTGRES-HYBRID-DATA-MODEL.md`
- Existing migrations: `rust_control_plane/migrations/001–010`
- `checkpoints.resume_state` JSONB mirrors the Engram checkpoint shape (context summary,
  next step, open questions, constraints) so data can be seeded from MM handoff files.
