# MasterMind v3.1 — Specification

**Generado:** 2026-04-28
**Brain consultations:** Brain #1 (Product Strategy) + Brain #7 (Growth/Data)
**Input:** 37 gaps de V31-GAPS.md, auditados desde fases 07-19

---

## Objetivo

v3.1 resuelve la deuda estructural acumulada en v3.0: tests de frontend nunca ejecutados, producción corriendo en SQLite, observabilidad completamente ausente (Phase 16 = 0%), y un sistema de dispatch que existe en código pero sigue siendo 100% manual en operación.

**No es un milestone de features nuevas.** Es el milestone que hace que lo construido en v3.0 funcione de verdad — con PostgreSQL como read-source, tests verdes, trazas cross-service visibles, y el motor de dispatch realmente disparando brains automáticamente.

El resultado medible: cualquier operación de brain se puede trazar desde Next.js → Rust → gRPC → Python, el sistema sabe qué brains tiene disponibles y los despacha solo, y el frontend está cubierto por tests ejecutados (no solo compilados).

---

## Contexto

- **v3.0 cerrado** — fases 13-19 completadas. Stack: Next.js 16 + FastAPI + Rust Axum + PostgreSQL (dual-write, no migrado)
- **DynamicDispatchEngine EXISTS** — `apps/api/mastermind_cli/mm_flow/dispatch_engine.py` (Phase 19). Dispatch sigue siendo 100% manual.
- **PostgreSQL dual-write EXISTS** — infraestructura completa. Read-source nunca se switcheó. Producción = SQLite.
- **628 TypeScript tests** — escritos en Phase 17. Compilación verificada. Ejecución NUNCA verificada.
- **Phase 16 (Observability) = 0%** — 7 planes definidos, ninguno ejecutado.
- **ExperienceLogger EXISTS** — 0 records. Brains no lo llaman. Sistema de aprendizaje no aprende.
- **Brain #7** — evalúa en planning (momentos 2+3). No evalúa post-sesión.
- **T1 baseline** — 210-270s. Target v3.1: sub-90s con learning activo.

---

## User Stories (priorizadas)

### Must Have (v3.1)

**US-01 — Foundation Integrity**
Como operador, quiero que el sistema corra con PostgreSQL como read-source y que todos los tests del frontend estén verificados en ejecución, para tener confianza real en la infraestructura antes de construir encima.
- **Acceptance:** `pnpm test` corre los 628 tests y pasan (o los que fallen están documentados como pre-existentes). `uv run pytest` pasa con PostgreSQL como read-source activo.

**US-02 — Cross-Service Tracing**
Como operador, cuando ejecuto un brain, quiero ver una traza completa Next.js → Rust → gRPC → Python en un panel de la UI, para poder debuggear sin SSH ni logs manuales.
- **Acceptance:** Un `trace_id` propagado desde el request original aparece en cada servicio. La UI muestra el span tree completo para cada ejecución de brain.

**US-03 — Real-time Brain Status**
Como operador, quiero ver en tiempo real el estado de cada brain (iniciando / ejecutando / completado / error) mientras una sesión corre, para no estar ciego durante ejecuciones largas.
- **Acceptance:** WebSocket Hub emite eventos de estado. El panel de la UI actualiza sin reload. T1 de "¿qué está pasando?" = 0s (visible sin preguntar).

**US-04 — Auto-dispatch de Brains**
Como operador, cuando inicio una sesión de planning, quiero que el sistema detecte el contexto (fase actual, gaps, momento) y despache los brains correctos automáticamente, sin que tenga que elegir manualmente cuál invocar.
- **Acceptance:** El Central Agent Registry tiene los 7 brains persistidos en PostgreSQL con capacidades y modelo asignado. El DynamicDispatchEngine los despacha según `config.yml`. Zero intervención manual en el happy path.

**US-05 — Brain #7 Post-Session Evaluation**
Como operador, después de cada sesión de brain, quiero que Brain #7 evalúe el output automáticamente y genere un score + aprendizaje, para que el sistema mejore sin que yo tenga que invocar Brain #7 manualmente.
- **Acceptance:** Hook post-sesión llama Brain #7. `ExperienceLogger` recibe el record con `quality_score`. El sistema tiene al menos 1 record por sesión ejecutada. T1 manual para evaluación = 0s.

**US-06 — Health Baseline**
Como operador, quiero que los 2 tests pre-existentes que fallan (test_cors_configuration, test_get_brain) estén documentados con root cause, para tener una suite limpia o conocer exactamente qué está roto y por qué.
- **Acceptance:** Ambos tests tienen un issue documentado en tasks/tech-debt.md con root cause. Si se pueden arreglar en < 1h, se arreglan. Si no, se marcan como `@pytest.mark.xfail` con reason.

### Should Have (v3.1)

**US-07 — Structured Logging**
Como operador, quiero que todos los servicios (Rust + Python) emitan logs estructurados con el mismo `trace_id`, para poder hacer `grep trace_id=XYZ` y ver toda la historia de una operación.

**US-08 — Model Profiles**
Como operador, quiero que las operaciones de planning usen Opus automáticamente y las de archiving usen Haiku, sin tener que especificarlo en cada invocación.

**US-09 — Nyquist Auditing**
Como operador, cuando marco una fase como completa, quiero que el sistema verifique activamente que los artefactos existen y funcionan (no solo checkboxes), para no acumular deuda de fases "completadas" que en realidad tienen gaps.

**US-10 — Three-Column Layout**
Como operador, quiero ver el orchestration canvas con la lista de brains, el canvas de ejecución actual, y los outputs estructurados en tres columnas, para tener toda la información sin cambiar de pantalla.

### Could Have (v3.2)

- **F1/F2/F3** — WhatsApp / Instagram / Email real APIs (requieren concierge MVP primero — Brian #1 veto)
- **G1** — PROP-001 Onboarding Visual (desbloqueado pero no crítico)
- **G2** — PROP-002-v2 Multi-Channel Orchestrator UI (aprobación condicional 65%, requiere concierge)
- **G3** — PROP-003 Event-Driven Heartbeats (Build Trap — 1 semana concierge primero)
- **E4** — WCAG 2.1 AA (nivel A suficiente para v3.1)
- **E5** — Storybook (diferido a v3.2)
- **A5** — "Next X" queries automáticas
- **A6** — Progressive status streaming (nice to have, detrás de D3)
- **C3** — Event sourcing `activity_log` (diferido, infraestructura de C1/C2 primero)
- **D6** — K6 load testing (diferido — WebSocket Hub debe existir primero)
- **D7** — Ghost Mode buffer (diferido)

---

## Arquitectura v3.1

### Qué cambia respecto a v3.0

| Componente | v3.0 | v3.1 |
|-----------|------|------|
| DB Read-Source | PostgreSQL (dual-write residual) | PostgreSQL exclusivo (sin dual-write) |
| Dispatch | Manual (100%) | Automático vía Registry + DynamicDispatchEngine |
| Observabilidad | Ninguna | Structured logs + distributed traces + WebSocket Hub |
| Frontend tests | Compilados (no ejecutados) | Ejecutados y verdes |
| Brain #7 trigger | Sólo planning | Planning + post-sesión automático |
| Cross-service debugging | SSH + logs manuales | Trace UI en Next.js |

### Nuevos componentes v3.1

- **Central Agent Registry** — Tabla PostgreSQL `brain_registry` con capacidades, modelo y triggers por brain
- **WebSocket Hub** — Rust Axum + tokio-tungstenite, emite eventos de estado en tiempo real
- **Distributed Trace Pipeline** — `trace_id` propagado: Next.js header → Rust middleware → gRPC metadata → Python structlog
- **Post-Session Hook** — Llama Brain #7 automáticamente al cierre de sesión (modify `StatelessCoordinator` o cron job)
- **Orchestration Canvas v2** — Three-column layout en Next.js con panel de monitoring en tiempo real

---

## Vertical Slices (fases propuestas)

### Slice 1: Foundation Integrity (C1 + E1 + H2/H3)

**Objetivo:** Eliminar el riesgo estructural más alto — verificar que PostgreSQL es el único read-source (sin código dual-write residual) y que los tests de frontend están ejecutados y verdes.

**Backend:**
- Auditar el código y remover cualquier referencia a dual-write o fallback a SQLite — PostgreSQL ya está corriendo con todas las tablas implementadas
- Documentar/arreglar H2 (test_cors_configuration) y H3 (test_get_brain)

**Frontend:**
- Ejecutar los 628 TypeScript tests (`pnpm test`) y registrar resultado
- Arreglar los que fallen si son < 2h de fix cada uno; los demás → issue documentado

**Tests:**
- `uv run pytest` con PostgreSQL read-source = 0 failures nuevas
- `pnpm test` ejecutado y con resultado documentado (pass count + failures conocidas)

**Acceptance:**
- [ ] `DATABASE_URL` apunta a PostgreSQL en todos los entornos
- [ ] `uv run pytest` pasa sin regresiones nuevas
- [ ] `pnpm test` reporta resultado (pass/fail) — NO "no ejecutado"
- [ ] H2 y H3 tienen root cause documentado en tasks/tech-debt.md

**Por qué primero:** Brain #7 — sin esto, cualquier cosa construida encima tiene base incierta. C1 sin resolver es un riesgo de corrupción de datos cuando la observabilidad empiece a escribir.

---

### Slice 2: Observability Core (D1 + D2 + D3 + D4)

**Objetivo:** Cross-service debugging visible desde la UI. Un `trace_id` que viaja de Next.js a Python.

**Backend (Rust):**
- `tracing` crate + `tracing-subscriber` con JSON formatter
- Middleware Axum que extrae `X-Trace-ID` del header y lo propaga como `tracing::Span`
- WebSocket Hub: Axum handler `/ws/events`, tokio broadcast channel, emite `BrainStateEvent`
- Health endpoints: `/health` en cada servicio

**Backend (Python):**
- `structlog` con `trace_id` bound desde gRPC metadata
- Post interceptor que inyecta `trace_id` en cada log line

**Frontend (Next.js):**
- `X-Trace-ID` header en todos los fetches desde `apps/web/`
- Panel de monitoring: WebSocket listener + Zustand store de eventos
- Trace viewer: muestra span tree por `trace_id`

**Tests:**
- Rust: unit test del middleware (trace propagation)
- Python: test que verifica que structlog emite `trace_id`
- Frontend: test del WebSocket store (mock WS, verify state updates)
- E2E: `POST /api/tasks/auto` → verificar que `trace_id` llega a Python structlog

**Acceptance:**
- [ ] `curl -H "X-Trace-ID: test-123" POST /api/tasks/auto` → Python log contiene `trace_id=test-123`
- [ ] WebSocket en `ws://localhost:8002/ws/events` emite eventos al ejecutar brain
- [ ] UI panel muestra estado en tiempo real sin reload
- [ ] Todos los servicios tienen `/health` endpoint respondiendo 200

---

### Slice 3: Intelligent Orchestration (A1 + A2 + B1 + A3)

**Objetivo:** El sistema sabe qué brains tiene y los despacha automáticamente. Brain #7 evalúa post-sesión sin intervención manual.

**Backend (Python):**
- Tabla `brain_registry` en PostgreSQL (brain_id, name, model, capabilities[], triggers[])
- Seed con los 7 brains actuales
- `DynamicDispatchEngine` ya existe — conectarlo a `brain_registry` como fuente de verdad (hoy usa config dict estático)
- Model profiles: `config.yml` con triplets `quality/balanced/budget` por rol
- Post-session hook en `StatelessCoordinator`: al cierre de sesión, llama Brain #7 con output del brain ejecutado
- `ExperienceLogger.log_execution()` llamado desde el hook (hoy = 0 records)

**Frontend (Next.js):**
- Panel de brains disponibles: consume `/api/brains` (ya existe) + muestra estado desde WebSocket
- Model profile selector: dropdown en Command Center (quality/balanced/budget)

**Tests:**
- Unit: `DynamicDispatchEngine` con `brain_registry` como fuente (no config dict)
- Integration: POST session → verify Brain #7 hook se ejecuta → verify ExperienceLogger record creado
- Frontend: test del model profile selector (Zustand store update)

**Acceptance:**
- [ ] `SELECT * FROM brain_registry` retorna 7 rows con capacidades correctas
- [ ] `DynamicDispatchEngine.dispatch()` usa `brain_registry`, no config dict hardcodeado
- [ ] Después de cualquier sesión de brain: `ExperienceLogger.get_recent_by_brain()` retorna >= 1 record
- [ ] Brain #7 score aparece en el record (`quality_score IS NOT NULL`)
- [ ] Model profile elegido en UI se usa en la invocación del brain

---

### Slice 4: UI Evolution (E2 + E3 + A6 + US-10)

**Objetivo:** Three-column orchestration canvas con monitoring en tiempo real. El operador ve todo sin cambiar de pantalla.

**Frontend (Next.js):**
- Three-column layout en `/command-center` o nueva ruta `/orchestrate`
- Columna 1: Brain list (disponibles, estado, model profile)
- Columna 2: Canvas de ejecución actual (React Flow DAG, extender The Nexus)
- Columna 3: Output estructurado del brain activo + trace timeline
- Real-time agent monitoring panel: consume WebSocket Hub del Slice 2
- Progressive status streaming: `Brain #1 ✅ → Brain #7 validando...` visible en columna 2

**Backend:**
- No backend nuevo — consume WebSocket Hub (Slice 2) y `brain_registry` (Slice 3)

**Tests:**
- Component tests: ThreeColumnLayout, BrainStatusPanel, TraceTimeline
- Integration: WebSocket mock → UI updates en tiempo real (verified)

**Acceptance:**
- [ ] Three-column layout renderiza en desktop (>1280px) sin overflow
- [ ] Brain status se actualiza en tiempo real desde WebSocket (< 500ms latency)
- [ ] Progressive status messages visibles durante ejecución (no spinner opaco)
- [ ] Output estructurado renderiza correctamente para todos los brain types

---

## Testing Strategy

| Slice | Unit | Integration | E2E |
|-------|------|-------------|-----|
| 1 — Foundation | `pnpm test` run, pytest baseline | DB connection via PostgreSQL | Smoke test: app arranca con PG |
| 2 — Observability | Rust middleware, Python structlog | trace_id end-to-end | POST /api/tasks/auto → trace visible |
| 3 — Orchestration | DynamicDispatchEngine, post-hook | Session → ExperienceLogger record | Full brain dispatch cycle |
| 4 — UI Evolution | Component tests | WS mock → state update | Three-column layout render |

**TDD obligatorio en todos los slices.** Cada subtask: tests RED primero, implementación GREEN, refactor si necesario.

---

## Acceptance Criteria para "v3.1 Complete"

### Infraestructura
- [ ] PostgreSQL es el único read-source — código dual-write residual removido y tests pasan sin fallback a SQLite
- [ ] `pnpm test` ejecutado — resultado documentado (pass count + failures conocidas)
- [ ] `uv run pytest` sin regresiones nuevas post-migración
- [ ] H2 y H3 tienen root cause documentado o están marcados `xfail`

### Observabilidad
- [ ] `X-Trace-ID` propagado end-to-end: Next.js → Rust → gRPC → Python
- [ ] WebSocket Hub activo en `/ws/events`
- [ ] UI panel de monitoring actualiza en tiempo real (< 500ms)
- [ ] Health endpoints activos en todos los servicios

### Orquestación
- [ ] `brain_registry` tiene 7 rows en PostgreSQL
- [ ] `DynamicDispatchEngine` usa `brain_registry` (no config dict hardcodeado)
- [ ] Después de cada sesión: `ExperienceLogger` tiene record con `quality_score`
- [ ] Model profiles configurados y usados en despacho

### UI
- [ ] Three-column orchestration canvas operativo
- [ ] Progressive status streaming visible durante ejecución de brains

---

## Out of Scope v3.1

Los siguientes items quedan para v3.2 o posteriores:

- **F1/F2/F3** — Channel integrations reales (WhatsApp/Instagram/Email). Requieren concierge MVP de validación primero. Brain #1 veto hasta entonces.
- **G1/G2/G3** — Proposals PROP-001/002/003. G1 desbloqueada pero no crítica. G2/G3 necesitan concierge.
- **C3** — Event sourcing `activity_log` (infraestructura de C1 primero, C3 después).
- **D6/D7** — K6 load testing y Ghost Mode buffer (después de WS Hub estable).
- **E4/E5** — WCAG AA y Storybook.
- **A5** — "Next X" queries automáticas.
- **H1** — 9 tech debt items de v2.1 (scope desconocido, necesitan audit separado).
- **C2** — JWT + RBAC en Rust (auth en Python funciona, migración puede esperar C1 estable).
- **Multi-tenant / Marketplace** — sin paying customers validados, Build Trap garantizado.
