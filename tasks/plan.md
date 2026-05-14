# MasterMind v3.1 — Implementation Plan

**Generado:** 2026-04-28
**Basado en:** tasks/SPEC.md
**Estrategia:** Vertical slicing estricto — cada task entrega test + frontend + backend juntos

---

## Dependency Graph

```
TASK-A (Foundation Integrity)
  ├── A1: PostgreSQL Migration Complete
  └── A2: Frontend Test Verification

       ↓ (A completo)

TASK-B (Observability Core)
  ├── B1: Structured Logging + Trace Pipeline
  ├── B2: WebSocket Hub
  └── B3: Health Endpoints

       ↓ (B completo — WS Hub activo)

TASK-C (Intelligent Orchestration)
  ├── C1: Central Agent Registry
  ├── C2: Dynamic Dispatch + Model Profiles
  └── C3: Brain #7 Post-Session Hook

       ↓ (B + C completos — Registry + WS activos)

TASK-D (UI Evolution)
  ├── D1: Three-Column Orchestration Canvas
  └── D2: Real-Time Monitoring Panel
```

**Parallelismo permitido:**
- A1 y A2 son paralelos entre sí
- B1 y B2 son paralelos entre sí (B3 es trivial, se hace con B1 o B2)
- C1 y C3 son paralelos entre sí (C2 depende de C1)
- D1 y D2 se planean juntos (mismo layout)

**Regla estricta:** Nunca avanzar al siguiente TASK si el anterior tiene acceptance criteria sin cumplir.

---

## TASK A: Foundation Integrity

**Gaps cerrados:** C1, E1, H2, H3
**Objetivo:** PostgreSQL como read-source en producción + tests de frontend verificados en ejecución. Eliminar la base inestable antes de construir observabilidad.
**Tiempo estimado:** 3-5 días

### A1: PostgreSQL Cleanup + Verification

**Qué:** PostgreSQL ya está corriendo con todas las tablas implementadas. Esta subtask audita el código para remover cualquier dual-write residual o fallback a SQLite, y verifica que la suite pasa 100% contra PostgreSQL.

**Backend (`apps/api/`):**
- Auditar `database.py`, `config.py` y cualquier módulo de configuración buscando referencias a dual-write, fallback SQLite o `sqlite://`
- Remover el código dual-write residual — PostgreSQL es la única DB
- `uv run pytest` — registrar resultado. Si hay failures nuevas por el cleanup, arreglarlas.
- Documentar en `tasks/tech-debt.md` los tests H2 (test_cors_configuration) y H3 (test_get_brain) con root cause

**Frontend (`apps/web/`):**
- Sin cambios de código. La auditoría es backend.

**Tests:**
- `uv run pytest` desde `apps/api/` — must pass con PostgreSQL como única fuente
- Smoke test: `GET /api/brains` retorna data real desde PostgreSQL
- Documentar: `SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public'` retorna N tablas implementadas

**Acceptance**:
- [x] `DATABASE_URL` apunta a PostgreSQL — verificado con `python -c "from database import engine; print(engine.url)"`
- [x] Sin referencias a `sqlite://` o dual-write en el código activo (`rg sqlite:// apps/` retorna 0 resultados)
- [x] `uv run pytest` de `apps/api/` pasa sin regresiones nuevas (puede haber failures pre-existentes documentadas)
- [x] H2 (test_cors_configuration) tiene root cause en `tasks/tech-debt.md`
- [x] H3 (test_get_brain) tiene root cause en `tasks/tech-debt.md`
- [x] `GET /api/brains` retorna data desde PostgreSQL (verificado con log/debug)

---

### A2: Frontend Test Verification

**Qué:** Ejecutar los 628 TypeScript tests y registrar resultado real. Esta subtask no agrega tests — ejecuta los que existen y documenta el estado real.

**Frontend (`apps/web/`):**
- Ejecutar `pnpm test` (o el comando de vitest configurado)
- Registrar: total tests, passed, failed
- Por cada test que falla: categorizar (pre-existing vs. regresión, arreglable en < 2h o no)
- Arreglar los que sean < 2h de fix
- Los demás: documentar en `tasks/tech-debt.md` con nombre + reason

**Backend:**
- Sin cambios. Si algún test falla por un endpoint que no existe, documentar — no inventar el endpoint.

**Tests:**
- `pnpm test --reporter=verbose` — output completo registrado
- Si vitest no está configurado: verificar `package.json` scripts y configurar si falta

**Acceptance**:
- [x] `pnpm test` ejecutado — no "no ejecutado"
- [x] Resultado documentado en `tasks/tech-debt.md`: N passed, M failed, lista de failures con categoría
- [x] Tests arreglables (< 2h) resueltos
- [x] Tests no arreglables documentados como issues o marcados `it.skip` con reason

---

## TASK B: Observability Core

**Gaps cerrados:** D1, D2, D3, D4
**Objetivo:** Un `trace_id` propagado end-to-end visible desde la UI. WebSocket Hub emitiendo eventos de estado.
**Tiempo estimado:** 5-7 días
**Depende de:** TASK A completo

### B1: Structured Logging + Distributed Trace Pipeline

**Qué:** `trace_id` único por request, propagado desde Next.js hasta Python, visible en logs estructurados de todos los servicios.

**Backend (Rust — `rust_control_plane/`):**
- Agregar `tracing` + `tracing-subscriber` (JSON formatter) al `Cargo.toml`
- Middleware Axum: extrae `X-Trace-ID` del header HTTP, crea `tracing::Span` con el valor
- Si no hay header: generar UUID v4 y propagarlo
- Propagar `trace_id` en metadata gRPC outgoing hacia Python

**Backend (Python — `apps/api/`):**
- Agregar `structlog` a `pyproject.toml` via `uv add structlog`
- Configurar `structlog` con JSON processor + `trace_id` bound desde gRPC metadata
- Interceptor gRPC que extrae `trace_id` de metadata y lo hace disponible via contextvars
- Cada log call tiene `trace_id` automáticamente (no manual)

**Frontend (`apps/web/`):**
- Utility `getTraceId()` — genera o reutiliza `trace_id` por request
- Todos los `fetch()` en `apps/web/src/` incluyen header `X-Trace-ID: ${traceId}`
- API route middleware en Next.js: agrega `X-Trace-ID` en respuesta para correlación

**Tests:**
- Rust: unit test del middleware — request con `X-Trace-ID: test-abc` → span contiene `trace_id=test-abc`
- Python: test que `structlog` emite `{"trace_id": "test-abc"}` cuando gRPC metadata lo incluye
- Integration: `POST /api/tasks/auto` con header `X-Trace-ID: e2e-test-123` → verificar que Python log contiene ese ID

**Acceptance**:
- [x] `curl -H "X-Trace-ID: smoke-123" POST /api/tasks/auto` → Python structlog emite `trace_id=smoke-123`
- [x] Rust logs en formato JSON con `trace_id` field
- [x] Python logs en formato JSON con `trace_id` field
- [x] Tests de propagación pasan (Rust unit + Python unit + integration)

---

### B2: WebSocket Hub

**Qué:** Rust Axum WebSocket endpoint que emite eventos de estado de brain en tiempo real. Frontend conecta y recibe updates sin polling.

**Backend (Rust — `rust_control_plane/`):**
- Handler `GET /ws/events` — upgrade a WebSocket
- `tokio::sync::broadcast` channel (capacity: 256) para fan-out de eventos
- `BrainStateEvent` struct: `{ trace_id, brain_id, status: "starting"|"running"|"completed"|"error", timestamp, payload? }`
- Serialización a JSON con `serde_json`
- Python gRPC client notifica al Hub cuando cambia estado de brain (via HTTP POST a Rust `POST /internal/brain-event`)

**Backend (Python — `apps/api/`):**
- Cuando `DynamicDispatchEngine` despacha un brain: POST a Rust `POST /internal/brain-event` con `BrainStateEvent`
- Cuando el brain completa: idem con status `completed`

**Frontend (`apps/web/`):**
- Hook `useWebSocket(url)` — maneja connect/disconnect/reconnect
- Zustand store `wsEventsStore` — state: `Map<trace_id, BrainStateEvent[]>`
- Componente `BrainStatusFeed` — lista de eventos en tiempo real (sin polling)

**Tests:**
- Rust: unit test del broadcast channel (envío → recepción)
- Frontend: `useWebSocket` con mock WS server — verify que state se actualiza en < 500ms
- Integration: Python despacha brain → Rust recibe evento → frontend lo muestra

**Acceptance**:
- [x] `wscat -c ws://localhost:8002/ws/events` — conecta y recibe eventos JSON
- [x] Frontend `BrainStatusFeed` se actualiza en tiempo real al ejecutar brain
- [x] Reconecta automáticamente si el WS se cae (max 3 intentos con backoff)
- [x] Tests de WS pasan (Rust unit + frontend unit + integration)

---

### B3: Health Endpoints

**Qué:** Endpoints `/health` en todos los servicios. Trivial pero necesario para monitoring y Slice 4.

**Backend (Rust):** `GET /health` → `{"status": "ok", "service": "rust-control-plane", "version": "..."}`
**Backend (Python):** Verificar si existe y agregar si falta. `GET /health` → `{"status": "ok", "service": "fastapi", "db": "postgresql"}`
**Frontend:** `GET /api/health` → proxy a ambos servicios, retorna estado agregado

**Tests:** Test que `/health` retorna 200 en cada servicio.

**Acceptance**:
- [x] `curl localhost:8002/health` → 200 JSON
- [x] `curl localhost:8001/health` → 200 JSON con `"db": "postgresql"`
- [x] `curl localhost:3000/api/health` → 200 JSON con estado agregado

---

## TASK C: Intelligent Orchestration

**Gaps cerrados:** A1, A2, B1, A3
**Objetivo:** Sistema que sabe qué brains tiene (Registry) y los despacha automáticamente (Engine). Brain #7 evalúa post-sesión. ExperienceLogger con records reales.
**Tiempo estimado:** 5-7 días
**Depende de:** TASK A (PostgreSQL activo) + TASK B (WS Hub para notificaciones de estado)

### C1: Central Agent Registry

**Qué:** Tabla `brain_registry` en PostgreSQL con los 7 brains, sus capacidades, modelo asignado y triggers de dispatch. El `DynamicDispatchEngine` la usa como fuente de verdad (hoy usa un dict hardcodeado).

**Backend (Python — `apps/api/`):**
- Migration Alembic: tabla `brain_registry` con columnas `brain_id, name, model_quality, model_balanced, model_budget, capabilities[], trigger_conditions[], enabled, created_at`
- Seed script: 7 rows con data de los brain bundles actuales (leer de `.claude/agents/mm/`)
- `BrainRegistryRepository` — CRUD básico: `get_all()`, `get_by_id()`, `get_matching(context)`
- `DynamicDispatchEngine.dispatch()`: reemplazar config dict con query a `BrainRegistryRepository`

**Frontend (`apps/web/`):**
- Verificar que `GET /api/brains` retorna data de `brain_registry` (no de config hardcodeado)
- Si retorna hardcoded: actualizar para leer desde la fuente correcta

**Tests:**
- Unit: `BrainRegistryRepository.get_all()` retorna 7 rows (fixture de PostgreSQL de test)
- Unit: `DynamicDispatchEngine.dispatch(context)` usa registry, no dict — mock registry, verify query
- Integration: POST session → dispatch usa `brain_registry` → brain ejecutado es el correcto

**Acceptance**:
- [x] `SELECT COUNT(*) FROM brain_registry` = 7
- [x] `DynamicDispatchEngine` no tiene ningún dict hardcodeado de brains en su código fuente
- [x] `GET /api/brains` retorna data de `brain_registry` PostgreSQL
- [x] Tests de registry pasan

---

### C2: Dynamic Dispatch + Model Profiles

**Qué:** Model profiles `quality/balanced/budget` configurados en `config.yml` y usados en el dispatch automáticamente.

**Backend (Python — `apps/api/`):**
- `config.yml`: sección `model_profiles` con triplets por rol (planning → Opus, execution → Sonnet, archiving → Haiku)
- `DynamicDispatchEngine`: leer model profile del contexto de la sesión y asignarlo al brain despachado
- `dispatch()` result incluye el modelo elegido — visible en el response y en el WS event

**Frontend (`apps/web/`):**
- Selector de model profile en Command Center: dropdown `quality / balanced / budget`
- El perfil elegido se envía en el request body al despachar
- El perfil activo visible en el `BrainStatusFeed` para cada brain ejecutándose

**Tests:**
- Unit: `dispatch(context, profile="quality")` → brain usa `model_quality` del registry
- Frontend: cambiar profile en dropdown → verify que Zustand store actualiza y el request siguiente lo incluye

**Acceptance**:
- [x] `config.yml` tiene sección `model_profiles` con 3 perfiles definidos
- [x] Cambiar el profile en la UI → la siguiente invocación de brain usa el modelo correcto
- [x] WS event incluye `model` field: `{"brain_id": "brain-01", "model": "claude-opus-4", ...}`

---

### C3: Brain #7 Post-Session Hook

**Qué:** Al cierre de cualquier sesión de brain, Brain #7 evalúa el output automáticamente y `ExperienceLogger` registra el resultado. T1 manual para evaluación = 0s.

**Backend (Python — `apps/api/`):**
- Hook en `StatelessCoordinator.complete_session()` (o en `task_runner.py`) — llama Brain #7 con output del brain ejecutado
- Brain #7 retorna `quality_score` (0.0-1.0) + `insights[]`
- `ExperienceLogger.log_execution()` llamado con el output + `quality_score`
- `high_value` flag en `custom_metadata`: True si duración > 5min O quality_score cambió significativamente

**Frontend (`apps/web/`):**
- WS event de tipo `session_evaluated` emitido por Hub después de que Brain #7 completa
- Badge en Command Center: "Última sesión: score 0.87" (usa el record más reciente de `/api/experiences`)

**Tests:**
- Unit: mock Brain #7 response → verify `ExperienceLogger.log_execution()` llamado con quality_score correcto
- Integration: complete session → verify `SELECT * FROM experience_records WHERE brain_id=X ORDER BY created_at DESC LIMIT 1` tiene quality_score
- Frontend: WS event `session_evaluated` → verify badge actualiza

**Acceptance**:
- [x] Después de cualquier sesión de brain: `ExperienceLogger.get_recent_by_brain(brain_id)` retorna >= 1 record
- [x] Record tiene `quality_score IS NOT NULL`
- [x] Badge en Command Center muestra score de última sesión
- [x] Tests del hook pasan (unit + integration)

---

## TASK D: UI Evolution

**Gaps cerrados:** E2, E3, A6
**Objetivo:** Three-column orchestration canvas. El operador ve todo sin cambiar de pantalla. Real-time monitoring integrado.
**Tiempo estimado:** 4-6 días
**Depende de:** TASK B (WS Hub) + TASK C (Registry + Dispatch para data real)

### D1: Three-Column Orchestration Canvas

**Qué:** Nueva ruta `/orchestrate` con layout de tres columnas. Extiende The Nexus (React Flow DAG existente) — no lo reemplaza.

**Frontend (`apps/web/`):**
- Ruta `/orchestrate` con layout: `[BrainList | OrchestrationCanvas | OutputPanel]`
- Columna 1 `BrainList`: consume `GET /api/brains` + WS events para estado en tiempo real
- Columna 2 `OrchestrationCanvas`: extender `NexusCanvas` existente (React Flow) con nodos de estado dinámico
- Columna 3 `OutputPanel`: output estructurado del brain activo + score de Brain #7 + trace timeline
- Responsive: en < 1280px colapsa a tabs

**Backend:**
- Sin cambios de backend — consume APIs existentes (`/api/brains`, `/ws/events`, `/api/experiences`)

**Tests:**
- Component: `OrchestrationCanvas` renderiza con data mockeada de 7 brains
- Component: `BrainList` actualiza estado cuando llega WS event
- Component: `OutputPanel` renderiza output estructurado correctamente
- E2E (Playwright si disponible): navegar a `/orchestrate` → verificar tres columnas visibles

**Acceptance**:
- [x] `/orchestrate` renderiza con tres columnas en 1440px
- [x] `BrainList` muestra los 7 brains con estado (idle/running/completed)
- [x] `OrchestrationCanvas` extiende NexusCanvas existente (no reescritura)
- [x] `OutputPanel` muestra output del último brain ejecutado
- [x] Responsive: < 1280px muestra tabs, no overflow

---

### D2: Real-Time Monitoring Panel + Progressive Streaming

**Qué:** Panel de monitoring integrado en la columna 2. Progressive status streaming visible durante ejecución. Elimina la opacidad del background agent.

**Frontend (`apps/web/`):**
- `useOrchestrationStream()` hook: consume `wsEventsStore` y emite estado progresivo
- `StatusTimeline` component: lista de eventos en orden cronológico con iconos de estado
- Integrado en columna 2 del canvas: debajo del React Flow DAG
- Estados visibles: completado, ejecutando, error, pendiente
- Auto-scroll al evento más reciente

**Backend:**
- Sin cambios — WS Hub (B2) ya emite los eventos necesarios

**Tests:**
- Component: `StatusTimeline` renderiza lista de eventos mockeados en orden correcto
- Hook: `useOrchestrationStream()` — mock WS store → verify que el hook retorna estado correcto
- Interaction: completar un brain → verify que timeline agrega el evento en < 500ms

**Acceptance**:
- [ ] Durante ejecución de brain: `StatusTimeline` muestra progreso sin reload
- [ ] Eventos en orden cronológico con timestamp
- [ ] Auto-scroll al evento más reciente
- [ ] Error states visibles (no spinner eterno)

---

## Notas de Ejecución

### TDD estricto
Cada subtask comienza con tests RED. Implementación viene después. No hay "agrego tests al final."

### Vertical slice estricto
Nunca cerrar una subtask con solo backend o solo frontend completo. Los tres tienen que estar done juntos.

### Verificación de acceptance criteria
Antes de marcar cualquier subtask como done, correr `/mm:verify-criteria [task-id]` para verificar cada checkbox de Acceptance.

### Orden de commits
Un commit por subtask completada. Mensaje: `feat(v3.1/[task-id]): [descripción]`. Ejemplo: `feat(v3.1/A1): complete PostgreSQL migration + document H2/H3 root cause`.
