# Tasks — postgres-hybrid-data-model

## Execution Rules
- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Each task must declare purpose, dependencies, likely file touchpoints, validation commands, and acceptance criteria.

## T1: Define and stabilize the slice

### Purpose
Clarify the exact objective boundary before implementation expands.

### Depends On
None

### Parallelizable
no

### Files / Areas Likely Touched
- requirements.md
- design.md
- tasks.md

### Validation Commands
- Review requirements/design/tasks package for consistency.

### Acceptance Criteria
- [ ] The exact boundary of the objective is implemented or tightened.
- [ ] Existing architecture constraints are preserved and documented.

## T2: Implement the smallest coherent deliverable

### Purpose
Add two migration files to the Rust control plane: `checkpoints` and `token_usage_events`.

### Depends On
T1

### Parallelizable
no

### Files / Areas Likely Touched
- `rust_control_plane/migrations/011_add_checkpoints.sql` (new)
- `rust_control_plane/migrations/012_add_token_usage_events.sql` (new)

### Validation Commands
- `grep -E "CREATE TABLE checkpoints" rust_control_plane/migrations/011_add_checkpoints.sql`
- `grep -E "CREATE TABLE token_usage_events" rust_control_plane/migrations/012_add_token_usage_events.sql`
- `grep -E "JSONB" rust_control_plane/migrations/011_add_checkpoints.sql`
- `grep -E "JSONB" rust_control_plane/migrations/012_add_token_usage_events.sql`
- `cd rust_control_plane && cargo test 2>&1 | tail -5`

### Acceptance Criteria
- [ ] `011_add_checkpoints.sql` creates the `checkpoints` table with relational + JSONB fields.
- [ ] `012_add_token_usage_events.sql` creates `token_usage_events` with relational + JSONB fields.
- [ ] Both files include appropriate indexes.
- [ ] `cargo test` passes in `rust_control_plane/`.

## T3: Close the continuity loop

### Purpose
Refresh handoff and validation context for the next model/session.

### Depends On
T2

### Parallelizable
no

### Files / Areas Likely Touched
- `.planning/changes/postgres-hybrid-data-model/HANDOFF-CURRENT.md`
- `.planning/changes/postgres-hybrid-data-model/tasks.md`
- `.planning/changes/postgres-hybrid-data-model/todo.md`

### Validation Commands
- `python3 .claude/commands/mm/discover-contract-check.py --objective postgres-hybrid-data-model`
- `python3 .claude/commands/mm/complete-task-handler.py --status`

### Acceptance Criteria
- [ ] Handoff notes are refreshed with next recommended work (`context-projection` objective).
- [ ] Contract check passes.
- [ ] Validation commands are documented and pass.
