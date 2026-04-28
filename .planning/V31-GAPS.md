# MasterMind v3.1 — Gaps Identificados

**Generado:** 2026-04-28
**Fuentes auditadas:** MM-FLOW-COMPLETION-PLAN, ROADMAP v3.0, milestones v2.x,
V30_MILESTONE_VERIFICATION_SUMMARY, proposals PROP-001/002/003, phases 07/13/14/15/16/17/18/19

---

## A — Orchestration Engine (gaps del plan MM-Flow, nunca implementados)

| # | Gap | Descripción | Impacto |
|---|-----|-------------|---------|
| A1 | **Central Agent Registry** | Tabla en PostgreSQL con qué brains existen, capacidades, modelo asignado y cuándo aplican. Hoy son solo archivos `.md` — el sistema no "sabe" qué tiene disponible. | ALTO |
| A2 | **Dynamic Dispatch Engine** | Motor que lee estado actual (fase, gaps, contexto) y despacha brains correctos automáticamente según `config.yml`. Hoy el dispatch es 100% manual. | ALTO |
| A3 | **Model profiles por rol** | Triplets `quality / balanced / budget` para asignar modelos automáticamente: planning → Opus, ejecución → Sonnet, archiving → Haiku. GSD lo tiene, MM-Flow no. | MEDIO |
| A4 | **Nyquist auditing** | Validación real de cobertura antes de marcar fase completa — no "checkboxes en [x]" sino verificación activa de que los artefactos existen y funcionan. | MEDIO |
| A5 | **"Next X" queries automáticas** | El sistema debería decirte cuál es el próximo paso disponible sin que lo preguntes manualmente. | MEDIO |
| A6 | **Progressive status streaming** | Feedback visible mientras ejecuta: `Brain #1 ✅ → Brain #7 validando... → spec generada ✅`. Hoy el background agent es opaco. | BAJO |

---

## B — Knowledge Distillation (Phase 14, success criteria incompletos)

| # | Gap | Descripción | Impacto |
|---|-----|-------------|---------|
| B1 | **Auto-evaluación Brain #7 post-sesión** | Brain #7 debe evaluar outputs de otros brains DESPUÉS de cada sesión para auto-mejora. Requiere hook nuevo. Documentado en CORRECTED-ASSUMPTIONS.md. | ALTO |
| B2 | **Dashboard de patterns/insights/correlaciones** | Patrones recurrentes por brain, insights acumulados, correlaciones entre brains, delta-velocity trends. ExperienceLogger existe pero los brains no lo llaman. | MEDIO |

---

## C — Rust Control Plane (Phase 15, migration incompleta)

| # | Gap | Descripción | Impacto |
|---|-----|-------------|---------|
| C1 | **SQLite → PostgreSQL migration no completada** | Dual-write infrastructure completa pero la migración de read-source nunca se ejecutó. Producción sigue en SQLite. | ALTO |
| C2 | **JWT + RBAC migrado a Rust** | Auth en Python (jose) mientras Rust Control Plane corre — inconsistencia. CVE-2025-29927 mitigation pendiente en Axum middleware. | MEDIO |
| C3 | **Event sourcing `activity_log`** | Tabla inmutable para operaciones de brains con temporal queries nunca implementada. Audit trail y analytics de time-series imposibles. | MEDIO |

---

## D — Observability (Phase 16, 0% ejecutado)

Phase 16 completa quedó pendiente. Los 7 planes nunca se ejecutaron:

| # | Gap | Descripción | Impacto |
|---|-----|-------------|---------|
| D1 | **Structured logging** | Rust tracing + Python structlog cross-service. Cross-service debugging ciego hoy. | ALTO |
| D2 | **Distributed tracing** | trace_id propagation entre Next.js → Rust → gRPC → Python. | ALTO |
| D3 | **WebSocket Hub** | Real-time hub para streaming de eventos. Definido en Phase 16, nunca construido. | ALTO |
| D4 | **Health checks** | Health endpoints cross-service. | MEDIO |
| D5 | **Metrics exposure** | SLIs definidos pero sin validación. | MEDIO |
| D6 | **Load testing K6** | Scripts definidos, nunca ejecutados. No sabemos si WebSocket Hub aguanta 1000 conexiones. | MEDIO |
| D7 | **Ghost Mode buffer** | Buffer offline para WebSocket disconnections. | BAJO |

---

## E — UI Evolution (Phase 17, tests sin verificar)

| # | Gap | Descripción | Impacto |
|---|-----|-------------|---------|
| E1 | **Frontend tests sin verificar** | 628 TypeScript tests escritos pero `execution not verified` (solo compilación verificada). | ALTO |
| E2 | **Three-column layout + orchestration canvas** | UI completa prometida en Phase 17, 0 planes ejecutados. | MEDIO |
| E3 | **Real-time agent monitoring panel** | Panel de monitoreo de agentes en tiempo real con WebSocket. | MEDIO |
| E4 | **WCAG 2.1 AA** | Solo nivel A implementado. AA deferido explícitamente a v3.1. | BAJO |
| E5 | **Storybook** | Deferido explícitamente a v3.1. | BAJO |

---

## F — Multi-channel Gateway (Phase 18, integraciones reales pendientes)

| # | Gap | Descripción | Impacto |
|---|-----|-------------|---------|
| F1 | **WhatsApp Business API real** | Hoy solo LocalStorage-first. Integración real con API deferred. | MEDIO |
| F2 | **Instagram Graph API real** | Mismo — mock/stub, no real. | MEDIO |
| F3 | **Email IMAP/SMTP real** | Mismo — server-side sync deferred. | MEDIO |
| F4 | **Queue depth monitoring** | Wave 1 deferred (18-08). | BAJO |
| F5 | **gRPC bridge + AI worker** | Wave 2 deferred (18-09). | BAJO |
| F6 | **DLQ API endpoints + Channel Router** | Wave 3 deferred (18-10). | BAJO |

---

## G — Propuestas Aprobadas No Ejecutadas

| # | Propuesta | Descripción | Estado |
|---|-----------|-------------|--------|
| G1 | **PROP-001: Onboarding Visual** | UI de onboarding para nuevos usuarios de MasterMind. Aprobada con condiciones (resueltas en 2026-04-06). No ejecutada — estaba blocked en Phase 15. | Desbloqueada |
| G2 | **PROP-002-v2: Multi-Channel Orchestrator UI** | Interface unificada para orquestar canales. Aprobación condicional (65%). Requiere concierge MVP de validación primero. | Conditional |
| G3 | **PROP-003: Event-Driven Heartbeats** | Sistema de heartbeats para brains. Deferido como Build Trap — requiere 1 semana de concierge MVP antes de código. | Deferido |

---

## H — Deuda Técnica Documentada

| # | Deuda | Fuente | Impacto |
|---|-------|--------|---------|
| H1 | **9 tech debt items desde v2.1** | `.planning/RETROSPECTIVE.md` — compounded 3 milestones, sin detalle listado | Desconocido |
| H2 | **test_cors_configuration FAILING** | Phase 07, pre-existente, nunca cerrado | BAJO |
| H3 | **test_get_brain FAILING** | Phase 07, pre-existente, nunca cerrado | BAJO |

---

## Priorización sugerida para v3.1

```
CRÍTICO (desbloquean todo lo demás):
  C1 — SQLite → PostgreSQL migration completar
  D1/D2 — Structured logging + distributed tracing
  A1/A2 — Agent Registry + Dynamic Dispatch

ALTO (completan fases incompletas):
  B1 — Auto-evaluación Brain #7
  D3 — WebSocket Hub
  E1 — Verificar frontend tests
  A3 — Model profiles

MEDIO (mejoran el producto):
  C2/C3 — JWT Rust + event sourcing
  E2/E3 — UI evolution
  F1/F2/F3 — Channel integrations reales
  B2 — Dashboard

BAJO (polish y deuda):
  A4/A5/A6 — Nyquist, Next X, streaming
  G1 — PROP-001 onboarding
  H2/H3 — Tests pre-existentes
  E4/E5 — WCAG AA + Storybook
```

---

**Total gaps identificados: 37**
(6 orchestration + 2 knowledge + 3 rust + 7 observability + 5 UI + 6 channels + 3 proposals + 3 tech debt + 2 tests)
