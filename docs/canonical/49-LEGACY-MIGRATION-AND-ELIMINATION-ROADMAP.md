# Legacy Migration and Elimination Roadmap

## Index

- [Goal](#goal)
- [Target End State](#target-end-state)
- [Strategy](#strategy)
- [Phases](#phases)
  - [Phase 0 — Freeze and visibility](#phase-0--freeze-and-visibility)
  - [Phase 1 — Remove legacy auth and API-key flow](#phase-1--remove-legacy-auth-and-api-key-flow)
  - [Phase 2 — Move tasks and executions to `project_state`](#phase-2--move-tasks-and-executions-to-project_state)
  - [Phase 3 — Remove legacy audit path](#phase-3--remove-legacy-audit-path)
  - [Phase 4 — Resolve analytics / experiences / distillation storage](#phase-4--resolve-analytics--experiences--distillation-storage)
  - [Phase 5 — Make new layers PostgreSQL-only](#phase-5--make-new-layers-postgresql-only)
  - [Phase 6 — Remove YAML registry and v1 compatibility wrappers](#phase-6--remove-yaml-registry-and-v1-compatibility-wrappers)
  - [Phase 7 — Delete the SQLite runtime core](#phase-7--delete-the-sqlite-runtime-core)
- [Execution Rules](#execution-rules)
- [Immediate Next Step](#immediate-next-step)
- [Related Artifacts](#related-artifacts)

## Goal

Remove the backend legacy stack completely by migrating active runtime behavior to the new PostgreSQL-based harness first, then deleting dead paths.

## Target End State

- PostgreSQL is the only supported operational database
- pgvector is the only supported vector retrieval path
- `project_state` is the canonical runtime state surface
- `brain_registry` in PostgreSQL is the only supported brain registry
- `mmsk_` API keys via `/api/keys` are the only supported API-key flow
- No runtime dependency remains on `mastermind_cli/state/database.py`
- No YAML fallback or v1 compatibility wrapper remains in execution paths

## Strategy

### 1. Freeze legacy

- No new features in legacy modules
- Only critical fixes and migration support
- New internal callers must use the target path only

### 2. Migrate by substitution

Each legacy surface must have:

- a target replacement
- internal caller migration
- exit criteria

### 3. Cut traffic before deletion

- Internal callers move first
- External compatibility is deprecated second
- Physical deletion happens only when runtime traffic is gone

## Phases

### Phase 0 — Freeze and visibility

Scope:

- document canonical vs legacy paths
- add deprecation markers where legacy is still exposed
- block new internal callers from using legacy

Exit criteria:

- legacy is documented
- no new internal usage is introduced

### Phase 1 — Remove legacy auth and API-key flow

Legacy:

- `mm_`
- `/api/auth/api-keys`
- SQLite `api_keys`
- `mastermind_cli/auth/api_keys.py`

Target:

- `mmsk_`
- `/api/keys`
- bcrypt-backed `api_keys_v2`

Exit criteria:

- no internal caller uses `mm_`
- websocket/auth runtime no longer depends on legacy key validation
- legacy endpoint can be disabled safely

### Phase 2 — Move tasks and executions to `project_state`

Legacy:

- SQLite `tasks`
- SQLite `executions`
- task graph and execution state reads from `state/database.py`

Target:

- `project_state` repositories and schemas
- harness-native execution state

Exit criteria:

- task/execution HTTP routes no longer read or write SQLite runtime tables
- runtime services no longer require `DatabaseConnection`

### Phase 3 — Remove legacy audit path

Legacy:

- SQLite `audit_log`
- mutation audit middleware writing to the legacy database

Target:

- `project_state` activity / telemetry / audit surfaces

Exit criteria:

- no request path writes to SQLite audit tables

### Phase 4 — Resolve analytics / experiences / distillation storage

Legacy:

- SQLite `experience_records`
- SQLite `knowledge_templates`
- analytics and experience routes/services tied to `DatabaseConnection`

Target:

- migrate to PostgreSQL-backed storage
- or archive/delete if no longer part of the canonical product path

Exit criteria:

- no active product feature depends on SQLite experience storage

### Phase 5 — Make new layers PostgreSQL-only

Scope:

- remove SQLite fallback from `project_state`
- remove SQLite fallback from `window_scheduler`
- require `MM_PROJECT_STATE_DB_URL` or `POSTGRES_URL`

Exit criteria:

- no canonical layer falls back to SQLite

### Phase 6 — Remove YAML registry and v1 compatibility wrappers

Legacy:

- YAML/hardcoded brain registry fallback
- `compatibility/legacy_wrapper.py`
- v1 wrapper execution paths

Target:

- PostgreSQL `brain_registry` as sole source of truth

Exit criteria:

- no runtime path depends on YAML or `LegacyBrainAdapter`

### Phase 7 — Delete the SQLite runtime core

Legacy:

- `mastermind_cli/state/database.py`
- `mastermind_cli/state/logger.py`
- any remaining SQLite runtime tables and fixtures

Exit criteria:

- no production module imports the legacy runtime database layer
- SQLite is absent from backend runtime paths

## Execution Rules

- Do not delete a legacy surface before its replacement is live
- Prefer migrating internal callers before changing external contracts
- Keep tests focused on the target architecture as soon as a phase starts
- Treat SQLite support inside canonical layers as temporary debt, not a permanent option

## Immediate Next Step

Start with **Phase 1** and **Phase 2**:

1. finish removing legacy auth/runtime key validation
2. define the canonical execution model that replaces SQLite `executions`

## Related Artifacts

- `docs/canonical/21-PROJECT-STATE-OPERATIONAL-MEMORY-ARCHITECTURE.md`
- `docs/canonical/27-POSTGRES-HYBRID-DATA-MODEL.md`
- `docs/canonical/29-INITIAL-POSTGRES-SCHEMA-SLICE.md`
- `docs/canonical/36-INITIAL-BACKEND-IMPLEMENTATION-PLAN.md`
- `docs/canonical/50-LEGACY-SURFACE-MIGRATION-MATRIX.md`
