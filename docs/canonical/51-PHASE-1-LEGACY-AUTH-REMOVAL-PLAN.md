# Phase 1 Implementation Plan — Legacy Auth Removal

## Index

- [Goal](#goal)
- [Scope](#scope)
- [Target End State](#target-end-state)
- [Legacy Surfaces in Scope](#legacy-surfaces-in-scope)
- [Workstreams](#workstreams)
  - [Workstream A — Remove runtime acceptance of `mm_`](#workstream-a--remove-runtime-acceptance-of-mm_)
  - [Workstream B — Remove legacy endpoint flow](#workstream-b--remove-legacy-endpoint-flow)
  - [Workstream C — Migrate CLI and internal callers](#workstream-c--migrate-cli-and-internal-callers)
  - [Workstream D — Remove compatibility exports and aliases](#workstream-d--remove-compatibility-exports-and-aliases)
  - [Workstream E — Rewrite tests to the canonical path](#workstream-e--rewrite-tests-to-the-canonical-path)
- [Execution Order](#execution-order)
- [Risks](#risks)
- [Exit Criteria](#exit-criteria)
- [Files Expected to Change](#files-expected-to-change)

## Goal

Remove the legacy API-key and runtime auth path so the backend accepts only the canonical API-key flow:

- `mmsk_`
- `/api/keys`
- bcrypt-backed verification

## Scope

This phase removes:

- legacy `mm_` API-key acceptance
- legacy `/api/auth/api-keys` endpoints
- legacy auth helpers and compatibility aliases
- internal callers still depending on the old path

This phase does **not** yet move API-key storage off SQLite. That is deferred to the runtime/postgres migration phases.

## Target End State

- only `/api/keys` remains as the supported API-key route
- only `mmsk_` keys are accepted at runtime
- websocket auth no longer accepts `mm_`
- CLI/runtime callers no longer import legacy auth helpers
- no compatibility alias remains in `mastermind_cli.auth.api_keys`

## Legacy Surfaces in Scope

### Runtime

- `apps/api/mastermind_cli/api/routes/auth.py`
- `apps/api/mastermind_cli/api/websocket.py`

### CLI / internal callers

- `apps/api/mastermind_cli/commands/orchestrate.py`

### Legacy auth module

- `apps/api/mastermind_cli/auth/api_keys.py`
- `apps/api/mastermind_cli/auth/__init__.py`
- `apps/api/mastermind_cli/types/auth.py`

### Tests and docs

- `apps/api/tests/api/test_auth.py`
- `apps/api/tests/unit/test_auth_api_keys.py`
- `apps/api/tests/unit/test_auth_api_key_legacy_aliases.py`
- `apps/api/tests/unit/test_auth_legacy_deprecation.py`
- `apps/api/tests/api/test_websocket.py`
- `apps/api/tests/api/test_sessions.py`
- `apps/api/README.md`

## Workstreams

### Workstream A — Remove runtime acceptance of `mm_`

#### Changes

- delete the legacy `mm_` branch from `get_current_user_any()` in `api/routes/auth.py`
- delete the legacy `mm_` branch from websocket token validation in `api/websocket.py`
- keep the standard `mmsk_` path only

#### Verification

- requests authenticated with `mmsk_` still succeed
- requests authenticated with `mm_` fail deterministically
- websocket auth accepts standard keys only

### Workstream B — Remove legacy endpoint flow

#### Changes

- remove:
  - `POST /api/auth/api-keys`
  - `GET /api/auth/api-keys`
  - `DELETE /api/auth/api-keys/{api_key_id}`
- remove deprecation-header helper once the endpoint is gone

#### Verification

- `/api/keys` still supports create/list/revoke
- legacy endpoint tests are removed or rewritten
- no OpenAPI route remains for `/api/auth/api-keys`

### Workstream C — Migrate CLI and internal callers

#### Changes

- stop importing `validate_legacy_api_key` in `commands/orchestrate.py`
- decide the canonical CLI auth contract:
  - either validate `mmsk_` directly
  - or route through a shared canonical auth service

#### Verification

- orchestrate no longer imports legacy auth
- no internal production caller imports `validate_legacy_api_key`

### Workstream D — Remove compatibility exports and aliases

#### Changes

- delete backward-compatible aliases from `auth/api_keys.py`
- simplify `auth/__init__.py` so it no longer exports legacy compatibility helpers
- remove legacy API-key generation helper from `types/auth.py`

#### Verification

- `rg` finds no production imports of:
  - `generate_legacy_api_key`
  - `validate_legacy_api_key`
  - `get_current_legacy_api_key`
  - `generate_api_key` alias
  - `validate_api_key` alias

### Workstream E — Rewrite tests to the canonical path

#### Changes

- remove tests whose only purpose is validating the deprecated endpoint
- rewrite auth/session/websocket coverage to use `/api/keys` and `mmsk_`
- keep only canonical-path auth tests

#### Verification

- auth/session/websocket tests pass without relying on legacy helpers or endpoints
- no test fixture emits `mm_` as the default API-key example

## Execution Order

1. migrate internal callers and tests to canonical `mmsk_` path
2. remove runtime acceptance of `mm_`
3. remove legacy `/api/auth/api-keys` endpoints
4. remove compatibility exports and aliases
5. clean docs and final test sweep

This order preserves working internal callers while shrinking the supported surface.

## Risks

### Medium — CLI auth coupling

`commands/orchestrate.py` still imports legacy validation directly. This must be replaced before deleting the module surface.

### Medium — WebSocket auth coverage

The websocket tests recently had separate hanging behavior; this phase must isolate auth-path changes from unrelated websocket lifecycle bugs.

### Low — Frontend impact

The frontend is already aligned to `/api/keys`, so this phase should mostly affect backend compatibility and tests.

## Exit Criteria

- no production code accepts `mm_`
- no production code exposes `/api/auth/api-keys`
- no production code imports legacy API-key helpers
- canonical `/api/keys` flow remains green
- docs identify only `/api/keys` as supported

## Files Expected to Change

### Primary

- `apps/api/mastermind_cli/api/routes/auth.py`
- `apps/api/mastermind_cli/api/websocket.py`
- `apps/api/mastermind_cli/commands/orchestrate.py`
- `apps/api/mastermind_cli/auth/api_keys.py`
- `apps/api/mastermind_cli/auth/__init__.py`
- `apps/api/mastermind_cli/types/auth.py`

### Tests

- `apps/api/tests/api/test_auth.py`
- `apps/api/tests/api/test_sessions.py`
- `apps/api/tests/api/test_websocket.py`
- `apps/api/tests/unit/test_auth_api_keys.py`
- `apps/api/tests/unit/test_auth_api_key_legacy_aliases.py`
- `apps/api/tests/unit/test_auth_legacy_deprecation.py`

### Docs

- `apps/api/README.md`
- `docs/canonical/50-LEGACY-SURFACE-MIGRATION-MATRIX.md`
