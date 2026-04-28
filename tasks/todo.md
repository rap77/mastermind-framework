# MasterMind v3.1 — Checklist

**Generado:** 2026-04-28
**Total tasks:** 4 | **Total subtasks:** 9 | **Gaps cerrados:** 17/37

---

## TASK A: Foundation Integrity
*Gaps: C1, E1, H2, H3 — Estimado: 3-5 días*

### A1: PostgreSQL Cleanup + Verification
- [ ] Backend: auditar `database.py`, `config.py` buscando referencias a dual-write o `sqlite://`
- [ ] Backend: remover código dual-write residual — PostgreSQL ya está activo con todas las tablas
- [ ] Backend: ejecutar `uv run pytest` desde `apps/api/` y registrar resultado
- [ ] Backend: si hay failures nuevas por el cleanup, arreglarlas
- [ ] Backend: documentar H2 (test_cors_configuration) root cause en `tasks/tech-debt.md`
- [ ] Backend: documentar H3 (test_get_brain) root cause en `tasks/tech-debt.md`
- [ ] Verify: `rg "sqlite://" apps/` retorna 0 resultados — sin referencias residuales
- [ ] Verify: `python -c "from database import engine; print(engine.url)"` muestra PostgreSQL URL
- [ ] Verify: `GET /api/brains` retorna data real desde PostgreSQL

### A2: Frontend Test Verification
- [x] Frontend: verificar que `pnpm test` (vitest) está configurado en `apps/web/package.json`
- [x] Frontend: ejecutar `pnpm test --reporter=verbose` desde `apps/web/`
- [x] Frontend: registrar resultado en `tasks/tech-debt.md` (N passed, M failed)
- [x] Frontend: por cada test fallando, categorizar: pre-existing / regresión / arreglable
- [x] Frontend: arreglar tests arreglables (< 2h cada uno)
- [x] Frontend: marcar tests no arreglables con `it.skip("reason: ...")` y documentar en tech-debt.md
- [x] Verify: `pnpm test` corre sin error fatal (aunque haya failures documentadas)

---

## TASK B: Observability Core
*Gaps: D1, D2, D3, D4 — Estimado: 5-7 días — Depende de: TASK A*

### B1: Structured Logging + Distributed Trace Pipeline
- [ ] Rust: agregar `tracing` + `tracing-subscriber` a `rust_control_plane/Cargo.toml`
- [ ] Rust: implementar middleware Axum que extrae `X-Trace-ID` del header y crea span
- [ ] Rust: si no hay header, generar UUID v4 y propagarlo
- [ ] Rust: propagar `trace_id` en metadata gRPC outgoing a Python
- [ ] Python: `uv add structlog` en `apps/api/`
- [ ] Python: configurar `structlog` con JSON processor
- [ ] Python: implementar interceptor gRPC que extrae `trace_id` de metadata → contextvars
- [ ] Python: bind `trace_id` automáticamente en todos los log calls
- [ ] Frontend: implementar utility `getTraceId()` en `apps/web/src/lib/`
- [ ] Frontend: agregar header `X-Trace-ID` en todos los `fetch()` calls
- [ ] Tests: Rust unit test — request con `X-Trace-ID: test-abc` → span tiene `trace_id=test-abc`
- [ ] Tests: Python unit test — gRPC metadata con `trace_id` → structlog emite `{"trace_id": "test-abc"}`
- [ ] Tests: integration — `POST /api/tasks/auto` con header → Python log contiene el ID
- [ ] Verify: `curl -H "X-Trace-ID: smoke-123" http://localhost:8001/api/tasks/auto -X POST` → log Python muestra smoke-123

### B2: WebSocket Hub
- [ ] Rust: implementar handler `GET /ws/events` con upgrade a WebSocket
- [ ] Rust: crear `tokio::sync::broadcast` channel (capacity 256) para fan-out
- [ ] Rust: definir `BrainStateEvent` struct con serde (trace_id, brain_id, status, timestamp)
- [ ] Rust: implementar endpoint `POST /internal/brain-event` para recibir eventos de Python
- [ ] Python: al despachar brain en `DynamicDispatchEngine`, POST a `http://rust:8002/internal/brain-event`
- [ ] Python: al completar brain, POST a mismo endpoint con status `completed`
- [ ] Frontend: implementar hook `useWebSocket(url)` con reconnect logic (max 3 intentos)
- [ ] Frontend: implementar Zustand store `wsEventsStore` con `Map<trace_id, BrainStateEvent[]>`
- [ ] Frontend: implementar componente `BrainStatusFeed`
- [ ] Tests: Rust unit test — broadcast channel (envío → recepción)
- [ ] Tests: Frontend unit test — `useWebSocket` con mock WS server, verify state update < 500ms
- [ ] Verify: `wscat -c ws://localhost:8002/ws/events` y ejecutar brain → recibir eventos JSON

### B3: Health Endpoints
- [ ] Rust: implementar `GET /health` → `{"status": "ok", "service": "rust-control-plane"}`
- [ ] Python: verificar si `GET /health` existe. Si no, implementar con `{"status": "ok", "db": "postgresql"}`
- [ ] Frontend: implementar `GET /api/health` route que hace proxy a ambos servicios
- [ ] Tests: test que `/health` retorna 200 en Rust
- [ ] Tests: test que `/health` retorna 200 en Python con `db` field
- [ ] Verify: `curl localhost:8002/health` y `curl localhost:8001/health` → 200

---

## TASK C: Intelligent Orchestration
*Gaps: A1, A2, B1, A3 — Estimado: 5-7 días — Depende de: TASK A + TASK B*

### C1: Central Agent Registry
- [ ] Python: crear migration Alembic para tabla `brain_registry` (brain_id, name, model_quality, model_balanced, model_budget, capabilities[], trigger_conditions[], enabled, created_at)
- [ ] Python: aplicar migration con `alembic upgrade head`
- [ ] Python: escribir seed script que inserta los 7 brains (leer capacidades de `.claude/agents/mm/`)
- [ ] Python: ejecutar seed script y verificar con `SELECT COUNT(*) FROM brain_registry` = 7
- [ ] Python: implementar `BrainRegistryRepository` con `get_all()`, `get_by_id()`, `get_matching(context)`
- [ ] Python: reemplazar config dict en `DynamicDispatchEngine` con query a `BrainRegistryRepository`
- [ ] Frontend: verificar que `GET /api/brains` retorna data de `brain_registry` (no hardcoded)
- [ ] Tests: unit test — `BrainRegistryRepository.get_all()` retorna 7 rows con fixture de test DB
- [ ] Tests: unit test — `DynamicDispatchEngine.dispatch(context)` llama `BrainRegistryRepository` (no dict)
- [ ] Verify: `SELECT COUNT(*) FROM brain_registry` = 7 en psql

### C2: Dynamic Dispatch + Model Profiles (Provider-Agnostic)

**Model profiles**
- [ ] Python: agregar sección `model_profiles` a `config.yml` (quality/balanced/budget) con formato `provider:model_id` — ej: `anthropic:claude-opus-4-6`, `openrouter:anthropic/claude-opus-4`, `z_ai:claude-3-7-sonnet`
- [ ] Python: agregar sección `providers` a `config.yml` con env vars de cada proveedor (ANTHROPIC_API_KEY, OPENROUTER_API_KEY, ZAI_API_KEY, base_url por proveedor)
- [ ] Python: `DynamicDispatchEngine` lee model profile del contexto y lo asigna al brain usando el proveedor configurado — NO hardcoded a Anthropic
- [ ] Python: dispatch result incluye `model` field con formato `provider:model_id`
- [ ] Python: WS event `BrainStateEvent` incluye `model` y `provider` fields
- [ ] Frontend: implementar dropdown de model profile en Command Center (quality/balanced/budget)
- [ ] Frontend: perfil elegido se envía en request body al despachar
- [ ] Frontend: `BrainStatusFeed` muestra el modelo + proveedor de cada brain ejecutándose
- [ ] Tests: unit test — `dispatch(context, profile="quality")` → brain usa `model_quality` del registry con su `provider`
- [ ] Tests: frontend test — cambiar dropdown → Zustand store actualiza → request incluye profile
- [ ] Verify: cambiar a "budget" en UI → ejecutar brain → WS event muestra `"model": "z_ai:claude-3-7-sonnet"` (no hardcoded Anthropic)

**Auto-switch de backend por agotamiento de tokens**
- [ ] JS: `mm-flow-context-monitor.js` — mover `BACKEND_LIMITS` a `.planning/.mm-flow/config.yml` (leer en runtime, no hardcoded)
- [ ] JS: al llegar al umbral crítico (95%) → escribir `.planning/BACKEND-SWITCH-REQUIRED.json` con `{current_backend, next_backend, reason: "token_depletion", timestamp}`
- [ ] Python: `complete-task-handler.py` al inicio lee `.planning/BACKEND-SWITCH-REQUIRED.json` — si existe: actualiza `ACTIVE_BACKEND` al próximo de la prioridad (`z_ai → openrouter → claude`), borra el archivo signal
- [ ] Python: `complete-task-handler.py` escribe `.planning/ACTIVE-BACKEND.json` con el backend activo — fuente de verdad para el hook JS y el handler
- [ ] JS: `mm-flow-context-monitor.js` lee `ACTIVE-BACKEND.json` para saber cuál backend trackear (no hardcoded)
- [ ] JS: `mm-flow-statusline.js` muestra el proveedor activo en la statusline cuando hay switch activo — ej: `│ v3.1 Task A1 [3/9] │ ⚡ openrouter`
- [ ] Tests: simular 95% de tokens en mock → verify `BACKEND-SWITCH-REQUIRED.json` creado con next_backend correcto
- [ ] Tests: `complete-task-handler.py` con `BACKEND-SWITCH-REQUIRED.json` presente → verify ACTIVE_BACKEND cambia + archivo borrado
- [ ] Verify: agotar tokens del backend primario → próximo `/mm:complete-task` usa automáticamente el siguiente proveedor sin intervención manual

### C3: Learning + Audit Pipeline
*Antes: "Brain #7 Post-Session Hook" — expandido para cubrir el flujo completo de aprendizaje*

**Brain #7 quality scoring (brain sessions)**
- [ ] Python: identificar el método correcto para el hook (StatelessCoordinator.complete_session o task_runner)
- [ ] Python: implementar hook que llama Brain #7 con output del brain ejecutado
- [ ] Python: Brain #7 response estructura: `quality_score` (float) + `insights[]` (strings)
- [ ] Python: llamar `ExperienceLogger.log_execution()` con output + quality_score + `model` field (qué modelo ejecutó)
- [ ] Python: flag `high_value` en custom_metadata si duración > 5min o score significativo
- [ ] Python: POST a Rust `/internal/brain-event` con tipo `session_evaluated` y score
- [ ] Frontend: escuchar WS event `session_evaluated`
- [ ] Frontend: badge en Command Center: "Última sesión: score 0.87"
- [ ] Tests: unit test — mock Brain #7 → verify `ExperienceLogger.log_execution()` llamado con quality_score
- [ ] Tests: integration test — complete session → `SELECT quality_score, model FROM experience_records ORDER BY created_at DESC LIMIT 1` IS NOT NULL
- [ ] Tests: frontend test — WS event `session_evaluated` → badge actualiza
- [ ] Verify: ejecutar cualquier brain → `uv run python -c "from experience.logger import ExperienceLogger; import asyncio; asyncio.run(ExperienceLogger().get_recent_by_brain('brain-01'))"` retorna record con quality_score

**Task Execution Audit (flujo /mm:complete-task)**
- [ ] Python: `complete-task-handler.py` al inicio de tarea → INSERT en `dev_sessions` (task_id, backend_used, tokens_estimated, tasks_total, started_at)
- [ ] Python: `complete-task-handler.py` al fin de tarea → UPDATE `dev_sessions` con tokens_consumed, tasks_completed, commit_hashes[], discoveries (texto de subtasks completados), ended_at
- [ ] Python: `task-executor` — por cada error de subtask → INSERT en `decisions` (decision_type="error_resolution", title=error summary, rationale=root_cause, chosen_option=solution_applied, confidence=0.7 default)
- [ ] Python: `task-executor` — al inicio de cada subtask → `brain_memory.py query --brain-id task-executor --limit 3` para recuperar patrones previos similares e incluirlos en el contexto
- [ ] Python: `task-executor` — al completar subtask con éxito → `brain_memory.py log` guardando qué funcionó (input=problema, output=solución, status=success)
- [ ] Tests: integration test — ejecutar task A1 → `SELECT * FROM dev_sessions ORDER BY started_at DESC LIMIT 1` tiene task_id + commit_hashes populated
- [ ] Tests: unit test — simular error en subtask → verify INSERT en `decisions` con decision_type="error_resolution"
- [ ] Verify: `SELECT COUNT(*) FROM dev_sessions` > 0 después de primer `/mm:complete-task`

**Métricas de ejecución**
- [ ] Python: `task-progress.json` incluye `started_at` + `completed_at` por cada subtask (para calcular duración real vs estimada)
- [ ] Python: `dev_sessions.metadata` incluye `context_budget_exits` (int) — cuántas veces task-executor salió al 75% y necesitó `--continue`
- [ ] Python: `dev_sessions.metadata` incluye `tokens_by_provider_model` (dict) — desglose `{"anthropic:claude-sonnet-4-6": N, "openrouter:claude-opus": N}` acumulado de `BACKEND-USAGE.json` — agnóstico al proveedor
- [ ] Python: `brain_consultations.metadata` incluye `gga_pass_first_attempt` (bool) — si el commit pasó GGA en el primer intento
- [ ] Python: `decisions` con `decision_type="error_pattern"` cuando el mismo root_cause aparece ≥ 2 veces — flag automático de deuda técnica recurrente
- [ ] Tests: unit test — dos errores con mismo root_cause → verify segundo INSERT tiene decision_type="error_pattern"
- [ ] Verify: después de 3 tasks ejecutadas → `SELECT SUM(tokens_consumed), backend_used FROM dev_sessions GROUP BY backend_used` muestra desglose real por backend

---

## TASK D: UI Evolution
*Gaps: E2, E3, A6 — Estimado: 4-6 días — Depende de: TASK B + TASK C*

### D1: Three-Column Orchestration Canvas
- [ ] Frontend: crear ruta `/orchestrate` en `apps/web/src/app/orchestrate/`
- [ ] Frontend: implementar layout de tres columnas (`[BrainList | OrchestrationCanvas | OutputPanel]`)
- [ ] Frontend: implementar `BrainList` component (consume `/api/brains` + `wsEventsStore`)
- [ ] Frontend: extender `NexusCanvas` existente para mostrar nodos con estado dinámico (no reescritura)
- [ ] Frontend: implementar `OutputPanel` (output estructurado + Brain #7 score + trace timeline)
- [ ] Frontend: responsive — en < 1280px colapsa a tabs
- [ ] Frontend: agregar link a `/orchestrate` en la nav principal
- [ ] Tests: component test — `OrchestrationCanvas` renderiza con data mockeada de 7 brains
- [ ] Tests: component test — `BrainList` actualiza estado cuando llega WS event
- [ ] Tests: component test — `OutputPanel` renderiza output estructurado
- [ ] Verify: navegar a `localhost:3000/orchestrate` → tres columnas visibles en 1440px

### D2: Real-Time Monitoring Panel + Progressive Streaming
- [ ] Frontend: implementar hook `useOrchestrationStream()` que consume `wsEventsStore`
- [ ] Frontend: implementar `StatusTimeline` component (eventos en orden cronológico)
- [ ] Frontend: integrar `StatusTimeline` en columna 2, debajo del React Flow DAG
- [ ] Frontend: iconos de estado (completado / ejecutando / error / pendiente)
- [ ] Frontend: auto-scroll al evento más reciente
- [ ] Tests: component test — `StatusTimeline` renderiza lista de eventos mockeados en orden correcto
- [ ] Tests: hook test — `useOrchestrationStream()` con mock store → retorna estado correcto
- [ ] Tests: interaction test — WS event llegado → timeline agrega evento en < 500ms
- [ ] Verify: ejecutar brain mientras se observa `/orchestrate` → StatusTimeline se actualiza en tiempo real

---

## Tracking

| Task | Estado | Subtasks Done | Acceptance |
|------|--------|---------------|------------|
| A — Foundation | Pendiente | 0/2 | 0/12 |
| B — Observability | Pendiente (bloquea A) | 0/3 | 0/10 |
| C — Orchestration | Pendiente (bloquea A+B) | 0/3 | 0/40 |
| D — UI Evolution | Pendiente (bloquea B+C) | 0/2 | 0/9 |
