# Legacy Surface Migration Matrix

## Purpose

Track every major legacy backend surface, its target replacement, and the action required to eliminate it.

| Surface | Key files | Legacy type | Target | Phase | Action | Risk |
|---|---|---|---|---|---|---|
| Runtime SQLite core | `apps/api/mastermind_cli/state/database.py` | SQLite operational DB | `project_state` + Postgres runtime services | 7 | delete after migrations | High |
| Runtime SQLite logger | `apps/api/mastermind_cli/state/logger.py` | SQLite execution logging | Postgres-backed telemetry or archive | 7 | migrate or delete | Medium |
| Legacy auth helpers | `apps/api/mastermind_cli/auth/api_keys.py` | `mm_`, SHA-256, aliases | `/api/keys`, `mmsk_`, bcrypt | 1 | migrate then delete | High |
| Legacy auth exports | `apps/api/mastermind_cli/auth/__init__.py` | compatibility exports | canonical auth module only | 1 | simplify exports | Medium |
| Legacy auth routes | `apps/api/mastermind_cli/api/routes/auth.py` | `/api/auth/api-keys`, SQLite sessions/api_keys | canonical auth + `/api/keys` | 1 | split/remove legacy branches | High |
| Standard API keys on SQLite | `apps/api/mastermind_cli/api/routes/keys.py` | still backed by SQLite `api_keys_v2` | Postgres canonical auth storage | 1-2 | migrate backing store | High |
| WebSocket legacy auth | `apps/api/mastermind_cli/api/websocket.py` | accepts `mm_`, SQLite lookup | standard API-key / canonical auth only | 1 | remove legacy auth branch | Medium |
| CLI orchestrate legacy auth | `apps/api/mastermind_cli/commands/orchestrate.py` | validates legacy API keys | canonical auth credential path | 1 | migrate caller | Medium |
| Task runtime routes | `apps/api/mastermind_cli/api/routes/tasks.py` | SQLite `executions` | `project_state` runtime model | 2 | migrate | High |
| Execution routes | `apps/api/mastermind_cli/api/routes/executions.py` | SQLite execution history access | Postgres runtime projection | 2 | migrate | High |
| Brain runtime route | `apps/api/mastermind_cli/api/routes/brain_runtime.py` | SQLite execution writes | canonical runtime state | 2 | migrate | Medium |
| Task runner service | `apps/api/mastermind_cli/api/services/task_runner.py` | SQLite task/execution writes | canonical runtime services | 2 | migrate | High |
| Execution writer service | `apps/api/mastermind_cli/api/services/execution_writer.py` | SQLite execution history writes | canonical runtime projection | 2 | migrate | High |
| App startup legacy DB init | `apps/api/mastermind_cli/api/app.py` | boots SQLite schemas | Postgres-only startup policy | 3 / 5 | remove | High |
| Legacy audit middleware | `apps/api/mastermind_cli/api/app.py` | SQLite `audit_log` | `project_state` audit/activity | 3 | migrate then delete | High |
| Analytics route | `apps/api/mastermind_cli/api/routes/analytics.py` | SQLite analytics reads | Postgres analytics or archive | 4 | decide + migrate/delete | Medium |
| Experiences route | `apps/api/mastermind_cli/api/routes/experiences.py` | SQLite experience reads | Postgres experience store or archive | 4 | decide + migrate/delete | Medium |
| Experience logger | `apps/api/mastermind_cli/experience/logger.py` | SQLite experience writes | Postgres experience store or archive | 4 | decide + migrate/delete | Medium |
| Distillation service | `apps/api/mastermind_cli/orchestration/distillation_service.py` | SQLite storage dependency | Postgres canonical storage | 4 | migrate | Medium |
| Analytics service | `apps/api/mastermind_cli/orchestration/analytics_service.py` | SQLite storage dependency | Postgres canonical storage | 4 | migrate | Medium |
| Brain memory tool | `apps/api/mastermind_cli/tools/brain_memory.py` | SQLite operational dependency | Postgres-backed memory projections | 4 | migrate | Low |
| YAML brain registry facade | `apps/api/mastermind_cli/brain_registry.py` | hardcoded/YAML compatibility | Postgres `brain_registry` only | 6 | delete fallback | High |
| Brains route fallback | `apps/api/mastermind_cli/api/routes/brains.py` | fallback to YAML | Postgres-only registry | 6 | remove fallback | Medium |
| Brain executor config path | `apps/api/mastermind_cli/orchestrator/brain_executor.py` | loads legacy registry configs | registry-backed runtime config | 6 | migrate | High |
| Coordinator simple registry fallback | `apps/api/mastermind_cli/orchestrator/coordinator.py` | compatibility registry wrapper | canonical registry abstraction | 6 | simplify | Medium |
| Legacy wrapper package | `apps/api/mastermind_cli/compatibility/__init__.py` | v1 compatibility package | none | 6 | delete | Low |
| Legacy brain adapters | `apps/api/mastermind_cli/compatibility/legacy_wrapper.py` | v1.x wrapper runtime | native harness execution only | 6 | delete | High |
| Project state SQLite fallback | `apps/api/mastermind_cli/api/dependencies.py` | fallback `sqlite+aiosqlite` URL | Postgres-only env config | 5 | remove fallback | Medium |
| Project state engine dual support | `apps/api/mastermind_cli/project_state/database/session.py` | SQLite + Postgres support | Postgres-only engine policy | 5 | remove SQLite mode | Medium |
| Window scheduler dual support | `apps/api/mastermind_cli/window_scheduler/database/session.py` | SQLite + Postgres support | Postgres-only engine policy | 5 | remove SQLite mode | Medium |
| Local SQLite shim | `aiosqlite/*`, `apps/api/aiosqlite/*` | tactical compatibility shim | none after SQLite removal | 7 | delete | Medium |
| Legacy-focused tests | `apps/api/tests/**/*legacy*`, SQLite-based API/runtime tests | coverage for removed paths | replace with canonical-path tests | phased | rewrite or delete | Medium |

## Notes

### Delete only after traffic is gone

For every row above:

1. migrate internal callers
2. disable fallback paths
3. remove tests tied only to the removed behavior
4. delete implementation

### Expected hardest migrations

- `state/database.py` consumers in runtime HTTP routes and services
- `tasks.py` / `executions.py` migration to `project_state`
- replacing SQLite-backed API-key storage behind `/api/keys`

### Expected easiest deletions

- compatibility exports once callers are gone
- deprecation-only tests after endpoint shutdown
- local `aiosqlite` shim after SQLite runtime removal
