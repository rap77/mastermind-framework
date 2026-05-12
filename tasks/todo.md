## TASK A: Foundation Integrity

- [x] A1: PostgreSQL Cleanup + Verification
  - [x] A1.01: Backend: auditar `database.py`, `config.py` buscando referencias a dual-write o `sqlite://`
  - [x] A1.02: Backend: remover código dual-write residual — PostgreSQL ya está activo con todas las tablas
  - [x] A1.03: Backend: ejecutar `uv run pytest` desde `apps/api/` y registrar resultado
  - [x] A1.04: Backend: si hay failures nuevas por el cleanup, arreglarlas
  - [x] A1.05: Backend: documentar H2 (test_cors_configuration) root cause en `tasks/tech-debt.md`
  - [x] A1.06: Backend: documentar H3 (test_get_brain) root cause en `tasks/tech-debt.md`
  - [x] A1.07: Verify: `rg "sqlite://" apps/` retorna 0 resultados — sin referencias residuales
  - [x] A1.08: Verify: `python -c "from database import engine; print(engine.url)"` muestra PostgreSQL URL
  - [x] A1.09: Verify: `GET /api/brains` retorna data real desde PostgreSQL

- [x] A2: Frontend Test Verification
  - [x] A2.01: Frontend: verificar que `pnpm test` (vitest) está configurado en `apps/web/package.json`
  - [x] A2.02: Frontend: ejecutar `pnpm test --reporter=verbose` desde `apps/web/`
  - [x] A2.03: Frontend: registrar resultado en `tasks/tech-debt.md` (N passed, M failed)
  - [x] A2.04: Frontend: por cada test fallando, categorizar: pre-existing / regresión / arreglable
  - [x] A2.05: Frontend: arreglar tests arreglables (< 2h cada uno)
  - [x] A2.06: Frontend: marcar tests no arreglables con `it.skip("reason: ...")` y documentar en tech-debt.md
  - [x] A2.07: Verify: `pnpm test` corre sin error fatal (aunque haya failures documentadas)

## TASK B: Observability Core

- [ ] B1: Structured Logging + Distributed Trace Pipeline
  - [x] B1.01: Rust: agregar `tracing` + `tracing-subscriber` a `rust_control_plane/Cargo.toml`
  - [x] B1.02: Rust: implementar middleware Axum que extrae `X-Trace-ID` del header y crea span
  - [x] B1.03: Rust: si no hay header, generar UUID v4 y propagarlo
  - [x] B1.04: Rust: propagar `trace_id` en metadata gRPC outgoing a Python
  - [x] B1.05: Python: `uv add structlog` en `apps/api/`
  - [x] B1.06: Python: configurar `structlog` con JSON processor
  - [x] B1.07: Python: implementar interceptor gRPC que extrae `trace_id` de metadata → contextvars
  - [x] B1.08: Python: bind `trace_id` automáticamente en todos los log calls
  - [x] B1.09: Frontend: implementar utility `getTraceId()` en `apps/web/src/lib/`
  - [x] B1.10: Frontend: agregar header `X-Trace-ID` en todos los `fetch()` calls
  - [x] B1.11: Tests: Rust unit test — request con `X-Trace-ID: test-abc` → span tiene `trace_id=test-abc`
  - [x] B1.12: Tests: Python unit test — gRPC metadata con `trace_id` → structlog emite `{"trace_id": "test-abc"}`
  - [ ] B1.13: Tests: integration — `POST /api/tasks/auto` con header → Python log contiene el ID
  - [ ] B1.14: Verify: `curl -H "X-Trace-ID: smoke-123" http://localhost:8001/api/tasks/auto -X POST` → log Python muestra smoke-123

- [ ] B2: WebSocket Hub
  - [ ] B2.01: Rust: implementar handler `GET /ws/events` con upgrade a WebSocket
  - [ ] B2.02: Rust: crear `tokio::sync::broadcast` channel (capacity 256) para fan-out
  - [ ] B2.03: Rust: definir `BrainStateEvent` struct con serde (trace_id, brain_id, status, timestamp)
  - [ ] B2.04: Rust: implementar endpoint `POST /internal/brain-event` para recibir eventos de Python
  - [ ] B2.05: Python: al despachar brain en `DynamicDispatchEngine`, POST a `http://rust:8002/internal/brain-event`
  - [ ] B2.06: Python: al completar brain, POST a mismo endpoint con status `completed`
  - [ ] B2.07: Frontend: implementar hook `useWebSocket(url)` con reconnect logic (max 3 intentos)
  - [ ] B2.08: Frontend: implementar Zustand store `wsEventsStore` con `Map<trace_id, BrainStateEvent[]>`
  - [ ] B2.09: Frontend: implementar componente `BrainStatusFeed`
  - [ ] B2.10: Tests: Rust unit test — broadcast channel (envío → recepción)
  - [ ] B2.11: Tests: Frontend unit test — `useWebSocket` con mock WS server, verify state update < 500ms
  - [ ] B2.12: Verify: `wscat -c ws://localhost:8002/ws/events` y ejecutar brain → recibir eventos JSON

- [ ] B3: Health Endpoints
  - [x] B3.01: Rust: implementar `GET /health` → `{"status": "ok", "service": "rust-control-plane"}`
  - [ ] B3.02: Python: verificar si `GET /health` existe. Si no, implementar con `{"status": "ok", "db": "postgresql"}`
  - [ ] B3.03: Frontend: implementar `GET /api/health` route que hace proxy a ambos servicios
  - [ ] B3.04: Tests: test que `/health` retorna 200 en Rust
  - [ ] B3.05: Tests: test que `/health` retorna 200 en Python con `db` field
  - [ ] B3.06: Verify: `curl localhost:8002/health` y `curl localhost:8001/health` → 200

## TASK C: Intelligent Orchestration

- [ ] C1: Central Agent Registry
  - [ ] C1.01: Python: crear migration Alembic para tabla `brain_registry` (brain_id, name, model_quality, model_balanced, model_budget, capabilities[], trigger_conditions[], enabled, created_at)
  - [ ] C1.02: Python: aplicar migration con `alembic upgrade head`
  - [ ] C1.03: Python: escribir seed script que inserta los 7 brains (leer capacidades de `.claude/agents/mm/`)
  - [ ] C1.04: Python: ejecutar seed script y verificar con `SELECT COUNT(*) FROM brain_registry` = 7
  - [ ] C1.05: Python: implementar `BrainRegistryRepository` con `get_all()`, `get_by_id()`, `get_matching(context)`
  - [ ] C1.06: Python: reemplazar config dict en `DynamicDispatchEngine` con query a `BrainRegistryRepository`
  - [ ] C1.07: Frontend: verificar que `GET /api/brains` retorna data de `brain_registry` (no hardcoded)
  - [ ] C1.08: Tests: unit test — `BrainRegistryRepository.get_all()` retorna 7 rows con fixture de test DB
  - [ ] C1.09: Tests: unit test — `DynamicDispatchEngine.dispatch(context)` llama `BrainRegistryRepository` (no dict)
  - [ ] C1.10: Verify: `SELECT COUNT(*) FROM brain_registry` = 7 en psql

- [ ] C2: Dynamic Dispatch + Model Profiles (Provider-Agnostic)
  - [ ] C2.01: Python: agregar sección `model_profiles` a `config.yml` (quality/balanced/budget) con formato `provider:model_id` — ej: `anthropic:claude-opus-4-6`, `openrouter:anthropic/claude-opus-4`, `z_ai:claude-3-7-sonnet`
  - [ ] C2.02: Python: agregar sección `providers` a `config.yml` con env vars de cada proveedor (ANTHROPIC_API_KEY, OPENROUTER_API_KEY, ZAI_API_KEY, base_url por proveedor)
  - [ ] C2.03: Python: `DynamicDispatchEngine` lee model profile del contexto y lo asigna al brain usando el proveedor configurado — NO hardcoded a Anthropic
  - [ ] C2.04: Python: dispatch result incluye `model` field con formato `provider:model_id`
  - [ ] C2.05: Python: WS event `BrainStateEvent` incluye `model` y `provider` fields
  - [ ] C2.06: Frontend: implementar dropdown de model profile en Command Center (quality/balanced/budget)
  - [ ] C2.07: Frontend: perfil elegido se envía en request body al despachar
  - [ ] C2.08: Frontend: `BrainStatusFeed` muestra el modelo + proveedor de cada brain ejecutándose
  - [ ] C2.09: Tests: unit test — `dispatch(context, profile="quality")` → brain usa `model_quality` del registry con su `provider`
  - [ ] C2.10: Tests: frontend test — cambiar dropdown → Zustand store actualiza → request incluye profile
  - [ ] C2.11: Verify: cambiar a "budget" en UI → ejecutar brain → WS event muestra `"model": "z_ai:claude-3-7-sonnet"` (no hardcoded Anthropic)
  - [ ] C2.12: JS: `mm-flow-context-monitor.js` — mover `BACKEND_LIMITS` a `.planning/.mm-flow/config.yml` (leer en runtime, no hardcoded)
  - [ ] C2.13: JS: al llegar al umbral crítico (95%) → escribir `.planning/BACKEND-SWITCH-REQUIRED.json` con `{current_backend, next_backend, reason: "token_depletion", timestamp}`
  - [ ] C2.14: Python: `complete-task-handler.py` al inicio lee `.planning/BACKEND-SWITCH-REQUIRED.json` — si existe: actualiza `ACTIVE_BACKEND` al próximo de la prioridad (`z_ai → openrouter → claude`), borra el archivo signal
  - [ ] C2.15: Python: `complete-task-handler.py` escribe `.planning/ACTIVE-BACKEND.json` con el backend activo — fuente de verdad para el hook JS y el handler
  - [ ] C2.16: JS: `mm-flow-context-monitor.js` lee `ACTIVE-BACKEND.json` para saber cuál backend trackear (no hardcoded)
  - [ ] C2.17: JS: `mm-flow-statusline.js` muestra el proveedor activo en la statusline cuando hay switch activo — ej: `│ v3.1 Task A1 [3/9] │ ⚡ openrouter`
  - [ ] C2.18: Tests: simular 95% de tokens en mock → verify `BACKEND-SWITCH-REQUIRED.json` creado con next_backend correcto
  - [ ] C2.19: Tests: `complete-task-handler.py` con `BACKEND-SWITCH-REQUIRED.json` presente → verify ACTIVE_BACKEND cambia + archivo borrado
  - [ ] C2.20: Verify: agotar tokens del backend primario → próximo `/mm:complete-task` usa automáticamente el siguiente proveedor sin intervención manual

- [ ] C3: Learning + Audit Pipeline
  - [ ] C3.01: Python: identificar el método correcto para el hook (StatelessCoordinator.complete_session o task_runner)
  - [ ] C3.02: Python: implementar hook que llama Brain #7 con output del brain ejecutado
  - [ ] C3.03: Python: Brain #7 response estructura: `quality_score` (float) + `insights[]` (strings)
  - [ ] C3.04: Python: llamar `ExperienceLogger.log_execution()` con output + quality_score + `model` field (qué modelo ejecutó)
  - [ ] C3.05: Python: flag `high_value` en custom_metadata si duración > 5min o score significativo
  - [ ] C3.06: Python: POST a Rust `/internal/brain-event` con tipo `session_evaluated` y score
  - [ ] C3.07: Frontend: escuchar WS event `session_evaluated`
  - [ ] C3.08: Frontend: badge en Command Center: "Última sesión: score 0.87"
  - [ ] C3.09: Tests: unit test — mock Brain #7 → verify `ExperienceLogger.log_execution()` llamado con quality_score
  - [ ] C3.10: Tests: integration test — complete session → `SELECT quality_score, model FROM experience_records ORDER BY created_at DESC LIMIT 1` IS NOT NULL
  - [ ] C3.11: Tests: frontend test — WS event `session_evaluated` → badge actualiza
  - [ ] C3.12: Verify: ejecutar cualquier brain → `uv run python -c "from experience.logger import ExperienceLogger; import asyncio; asyncio.run(ExperienceLogger().get_recent_by_brain('brain-01'))"` retorna record con quality_score
  - [ ] C3.13: Python: `complete-task-handler.py` al inicio de tarea → INSERT en `dev_sessions` (task_id, backend_used, tokens_estimated, tasks_total, started_at)
  - [ ] C3.14: Python: `complete-task-handler.py` al fin de tarea → UPDATE `dev_sessions` con tokens_consumed, tasks_completed, commit_hashes[], discoveries (texto de subtasks completados), ended_at
  - [ ] C3.15: Python: `task-executor` — por cada error de subtask → INSERT en `decisions` (decision_type="error_resolution", title=error summary, rationale=root_cause, chosen_option=solution_applied, confidence=0.7 default)
  - [ ] C3.16: Python: `task-executor` — al inicio de cada subtask → `brain_memory.py query --brain-id task-executor --limit 3` para recuperar patrones previos similares e incluirlos en el contexto
  - [ ] C3.17: Python: `task-executor` — al completar subtask con éxito → `brain_memory.py log` guardando qué funcionó (input=problema, output=solución, status=success)
  - [ ] C3.18: Tests: integration test — ejecutar task A1 → `SELECT * FROM dev_sessions ORDER BY started_at DESC LIMIT 1` tiene task_id + commit_hashes populated
  - [ ] C3.19: Tests: unit test — simular error en subtask → verify INSERT en `decisions` con decision_type="error_resolution"
  - [ ] C3.20: Verify: `SELECT COUNT(*) FROM dev_sessions` > 0 después de primer `/mm:complete-task`
  - [ ] C3.21: Python: `task-progress.json` incluye `started_at` + `completed_at` por cada subtask (para calcular duración real vs estimada)
  - [ ] C3.22: Python: `dev_sessions.metadata` incluye `context_budget_exits` (int) — cuántas veces task-executor salió al 75% y necesitó `--continue`
  - [ ] C3.23: Python: `dev_sessions.metadata` incluye `tokens_by_provider_model` (dict) — desglose `{"anthropic:claude-sonnet-4-6": N, "openrouter:claude-opus": N}` acumulado de `BACKEND-USAGE.json` — agnóstico al proveedor
  - [ ] C3.24: Python: `brain_consultations.metadata` incluye `gga_pass_first_attempt` (bool) — si el commit pasó GGA en el primer intento
  - [ ] C3.25: Python: `decisions` con `decision_type="error_pattern"` cuando el mismo root_cause aparece ≥ 2 veces — flag automático de deuda técnica recurrente
  - [ ] C3.26: Tests: unit test — dos errores con mismo root_cause → verify segundo INSERT tiene decision_type="error_pattern"
  - [ ] C3.27: Verify: después de 3 tasks ejecutadas → `SELECT SUM(tokens_consumed), backend_used FROM dev_sessions GROUP BY backend_used` muestra desglose real por backend

## TASK D: UI Evolution

- [ ] D1: Three-Column Orchestration Canvas
  - [ ] D1.01: Frontend: crear ruta `/orchestrate` en `apps/web/src/app/orchestrate/`
  - [ ] D1.02: Frontend: implementar layout de tres columnas (`[BrainList | OrchestrationCanvas | OutputPanel]`)
  - [ ] D1.03: Frontend: implementar `BrainList` component (consume `/api/brains` + `wsEventsStore`)
  - [ ] D1.04: Frontend: extender `NexusCanvas` existente para mostrar nodos con estado dinámico (no reescritura)
  - [ ] D1.05: Frontend: implementar `OutputPanel` (output estructurado + Brain #7 score + trace timeline)
  - [ ] D1.06: Frontend: responsive — en < 1280px colapsa a tabs
  - [ ] D1.07: Frontend: agregar link a `/orchestrate` en la nav principal
  - [ ] D1.08: Tests: component test — `OrchestrationCanvas` renderiza con data mockeada de 7 brains
  - [ ] D1.09: Tests: component test — `BrainList` actualiza estado cuando llega WS event
  - [ ] D1.10: Tests: component test — `OutputPanel` renderiza output estructurado
  - [ ] D1.11: Verify: navegar a `localhost:3000/orchestrate` → tres columnas visibles en 1440px

- [ ] D2: Real-Time Monitoring Panel + Progressive Streaming
  - [ ] D2.01: Frontend: implementar hook `useOrchestrationStream()` que consume `wsEventsStore`
  - [ ] D2.02: Frontend: implementar `StatusTimeline` component (eventos en orden cronológico)
  - [ ] D2.03: Frontend: integrar `StatusTimeline` en columna 2, debajo del React Flow DAG
  - [ ] D2.04: Frontend: iconos de estado (completado / ejecutando / error / pendiente)
  - [ ] D2.05: Frontend: auto-scroll al evento más reciente
  - [ ] D2.06: Tests: component test — `StatusTimeline` renderiza lista de eventos mockeados en orden correcto
  - [ ] D2.07: Tests: hook test — `useOrchestrationStream()` con mock store → retorna estado correcto
  - [ ] D2.08: Tests: interaction test — WS event llegado → timeline agrega evento en < 500ms
  - [ ] D2.09: Verify: ejecutar brain mientras se observa `/orchestrate` → StatusTimeline se actualiza en tiempo real

## Tracking
