---
proposal_id: "PROP-003"
title: "Event-Driven Heartbeats con Webhooks/Integraciones"
status: "DEFERRED"
created_at: "2026-04-06"
last_updated: "2026-04-06"
brain_evaluations:
  - brain: "Brain #1 (Product Strategy)"
    verdict: "DEFERRED"
    confidence: 75%
  - brain: "Brain #5 (Backend Architecture)"
    verdict: "RECOMENDADO CON MODIFICACIONES"
    confidence: 80%
  - brain: "Brain #7 (Growth/Data - Meta-evaluator)"
    verdict: "DEFERRED"
    confidence: 85%
---

# PROP-003: Event-Driven Heartbeats con Webhooks/Integraciones

**Estado:** 🔴 **DEFERRED** — Requiere validación de problema ANTES de infraestructura

**Confianza:** 85%

---

## Resumen Ejecutivo

**Problema identificado:** Heartbeats actuales (en Paperclip) son schedules fijos pasivos (cada 4h, 8h) sin reacción a eventos externos.

**Solución propuesta:** Sistema event-driven que active heartbeats en respuesta a webhooks de terceros (Google, Stripe, N8N, CRM, ERP, bases de datos).

**Beneficiarios:** Empresa + usuarios finales (monitoreo externo + automatización de flujos).

**Valor declarado:** Agentes más PROACTIVOS — reaccionan en tiempo real.

---

## Evaluación de Brains

### Brain #1 (Product Strategy) — DEFERRED 🔴 (75% confianza)

#### ✅ Lo Bueno
- Problema real identificado — Latency de 4-8h puede ser leverage point crítico (Meadows)
- Alineado con arquetipo "Proactivo"
- Casos de uso concretos: Stripe, Google, N8N, CRM/ERP
- Complementa Knowledge Distillation (patterns pueden destilarse)

#### ⚠️ Lo Que Falta
- **Evidencia de bottleneck:** T1 baseline (210-270s) es processing time, no wall-clock time. ¿El dolor es "tardo 4 minutos" (heartbeats NO arreglan) o "tardo 4 horas" (heartbeats SÍ arreglan)?
- **Codebase verification:** NO existe implementación de heartbeats actualmente (grep confirmó 0 matches) — esto es net-new infrastructure
- **Target user mal definido:** Builder actual YA ve updates por WS. ¿Quién NO ve updates que necesita heartbeats?
- **Frequency/Severity NO medidos:** ¿1 evento/día? ¿100? Sin este dato, imposible calcular ROI
- **Duplicación con PROP-002-v2:** PROP-002 ya propone reportes ejecutivos que podrían requerir eventos reactivos

#### 🚨 Peligros
- **🚨 HIGH: Build Trap confirmado** — Construir infraestructura SIN validar que el dolor es real, frecuencia suficiente, outcome medible
- **🚨 HIGH: Scope explosion** — 6 integraciones (Google, Stripe, N8N, CRM, ERP, DB) = effort XL, no Medium
- **🚨 MEDIUM: Solved Problem** — WS infrastructure ya existe. ¿Qué gap específico llena webhook que WS no llena?
- **🚨 MEDIUM: Wrong metric** — "Agentes más proactivos" es vago. Se necesita "T1 reducido de X a Y"

#### 💭 Sugerencias
1. **Concierge MVP OBLIGATORIO** (1 semana): Manual trigger para 1 workflow, medir frecuencia + T1 + outcome
2. **Separar en 2 propuestas:** PROP-003-A (infraestructura) + PROP-003-B (integraciones específicas)
3. **Validar WS no ya resuelve:** Revisar logs de WS events
4. **Priorizar por Frequency × Impact:** Solo implementar Top 1 con frecuencia ≥5/día
5. **Empezar con UNA integración:** Stripe webhooks ONLY para MVP

---

### Brain #5 (Backend Architecture) — RECOMENDADO CON MODIFICACIONES (80% confianza)

#### ✅ Lo Bueno
- **Alineación con Stack Asíncrono** — `asyncio.TaskGroup` + `BackgroundTasks` ya validados
- **Rust Control Plane Integrado** — gRPC + Protobuf, 6.2x velocidad validada
- **Repository Pattern** — Ya implementado, solo extender para `webhook_events` table
- **Seguridad en Capas** — JWT + httpOnly cookies + HMAC verification

#### ⚠️ Lo Que Falta
- **Idempotency Keys — CRÍTICO:** Sin esto, reintentos de Stripe procesan mismo pago 2-3 veces
- **Circuit Breaker:** Necesario para llamadas a CRM/ERP (latencia de terceros)
- **Contract Testing:** Google/Stripe cambian schemas sin avisar
- **Dead Letter Queue:** ¿Qué pasa si Stripe manda webhook inválido? Hoy: se pierde

#### 🚨 Peligros
- **SPOF en Single-Host** — `asyncio.create_task()` se pierde si proceso reinicia. Mitigación: write-ahead log
- **Bloqueo del Event Loop** — ERP devuelve JSON de 5MB → parseo bloquea. Mitigación: `asyncio.to_thread()`
- **Broken Access Control** — `webhook.user_id` spoofeable sin HMAC verification
- **Inconsistencia Rust↔Python** — Race condition posible. Mitigación: gRPC con `accepted_at_unix_ms`

#### 💭 Sugerencias

**Patrón Arquitectónico Recomendado:**
```
Webhook (Stripe/Google)
    ↓
Rust (Axum) - Receiver [valida HMAC, devuelve 202]
    ↓
asyncio.Queue (in-memory, backpressure incluido)
    ↓
Python (FastAPI) - Worker [procesa, llama CRM/ERP]
    ↓
PostgreSQL - persistencia
```

**Stack Split:**
| Componente | Lenguaje | Justificación |
|-----------|----------|---------------|
| Webhook Receiver | Rust (Axum) | Baja latencia, valida HMAC rápido |
| Integración CRM/ERP | Python (FastAPI) | SDKs maduros |
| Heartbeat Dispatcher | Rust (Axum) | Control Plane ya en Rust |

**Implementación Priorities:**
- **Phase 1 (MVP - 2 semanas):** webhook_events table, Rust receiver, Python worker, Idempotency keys
- **Phase 2 (Robustez - 1 semana):** Circuit Breaker, Contract testing, Dead Letter Queue
- **Phase 3 (Observabilidad - 1 semana):** Métricas latency, dashboard, alertas

---

### Brain #7 (Growth/Data - Meta-evaluator) — DEFERRED 🔴 (85% confianza)

#### Veredicto Final

**DEFERRED** — No REJECTED porque el problema puede ser real. Pero no APPROVED porque:

1. **Evidencia insuficiente:** NO existe heartbeats en codebase (verificado) y NO hay evidencia de bottleneck. Build Trap clásico.
2. **Target user ambiguity:** Builder (hoy) vs. external users (futuro) — proposal no lo aclara.
3. **Scope explosion:** 6 integraciones sin priorización.
4. **Validación de WS faltante:** Ningún cerebro verificó que `wsDispatcher.ts` NO ya resuelve el 80% del caso.
5. **Feedback loops no nombrados:** Proactividad Fallida → Confiabilidad colapsa. WYSIATI → Asumir proactividad = solución.

#### Tensiones Identificadas

**TENSIÓN #1: Velocidad de Aprendizaje vs. Robustez Técnica**
- Brain #1: "Concierge MVP 1 semana"
- Brain #5: "MVP 2 semanas + robustez 1 semana = 3 semanas"
- **Ganador:** Brain #1 — Sunk Cost dicta validar antes de invertir

**TENSIÓN #2: Alcance de Integraciones**
- Brain #1: "Scope explosion — separar en 2 propuestas"
- Brain #5: "Stack split: 6 integraciones"
- **Ganador:** Brain #1 — Tabla Frequency × Impact es crítica

**TENSIÓN #3: Validación de WebSocket Existente**
- Brain #1: "WS ya soluciona para builder — validar"
- Brain #5: No menciona validación
- **Ganador:** Brain #1 — wsDispatcher.ts ya existe, verificar gap real

#### Feedback Loops Sistémicos Identificados

1. **Negative Noise Loop:** Proactividad → Aumento ruido/señal → Confiabilidad colapsa → Builder desactiva
2. **Feature-Positive Effect:** Asumir proactividad = valor → Construir integraciones → Medir output → NO medir outcome → Sistema productivo pero sin valor
3. **Action Bias Loop:** Se ve "Agents no son proactivos" → Se asume "Necesitamos webhooks" → NO se pregunta "¿El problema es activación o lógica?"

#### Condiciones CRÍTICAS para Aprobar

**Condición #1: Concierge MVP (BLOCKER)**
- 1 semana de heartbeats MANUALES
- Criterio: ≥5 heartbeats/semana + ≥30s T1 reduction
- Si T1 < 30s → REJECTED

**Condición #2: Validación de WebSocket Existente (BLOCKER)**
- Verificar que `wsDispatcher.ts` NO ya permite activación proactiva
- Documentar gap específico que llena webhook

**Condición #3: Target User Clarity (BLOCKER)**
- Definir explícitamente: ¿Builder (hoy) o external users (futuro)?
- Si Builder → Concierge MVP suficiente. Si external → re-evaluar todo

**Condición #4: Tabla Frequency × Impact (BLOCKER)**
- Priorizar 6 integraciones por (Frequency × Impact)
- Seleccionar TOP 1 para MVP. Las otras 5 DEFERRED.

**Condición #5: Idempotency Keys + Circuit Breaker (BLOCKER técnico)**
- Diseñar cómo evitar duplicados y cascade failures
- Diagrama: qué pasa si Stripe dispara 1000 eventos/segundo

---

## Roadmap Recomendado

### Fase 0: Evidencia (1 semana) — **BLOCKER para todo lo demás**
1. Concierge MVP: 5 heartbeats manuales + medir T1
2. Auditoría WS: Verificar gap real
3. Definir target user + Tabla Freq × Impact

**Gate:** Si T1 < 30s reduction o WS ya resuelve → **STOP**. Proposal REJECTED.

### Fase 1: Diseño (1 semana) — Solo si Fase 0 pasa
1. Diseño de Idempotency Keys
2. Diseño de Circuit Breaker + DLQ
3. Selección TOP 1 integración
4. Diagrama de arquitectura Rust/Python split

**Gate:** Sin diseño de robustez → **STOP**. No escribir código.

### Fase 2: MVP Técnico (2 semanas) — Solo si Fase 1 pasa
1. Webhook Receiver en Rust (TOP 1 integración solo)
2. Heartbeat Dispatcher en Rust
3. Integración Python (solo si TOP 1 lo requiere)
4. Tests de idempotencia + circuit breaker

**Gate:** Signal-to-Noise Ratio < 40% → **STOP**. Sistema creando ruido.

### Fase 3: Medición Sistémica (1 semana) — **CRÍTICO**
1. SLI-1: Signal-to-Noise Ratio ≥40%
2. SLI-2: Systemic Latency Delta <50ms
3. OKR: T1 reduction ≥30s sostenido por 2 semanas
4. Friction-to-Benefit Ratio <1.0

**Gate:** Si cualquier SLI falla → **PIVOT** o **KILL**.

---

## Métricas de Detección Temprana (SLI/OKRs)

| SLI/OKR | Qué mide | Target | ¿Qué indica si falla? |
|---------|----------|--------|----------------------|
| **SLI-1: Signal-to-Noise Ratio** | % de heartbeats NO revertidos por Builder | ≥40% | Sistema creando ruido |
| **SLI-2: Systemic Latency Delta** | Aumento de latencia WS durante webhook bursts | <50ms | Proactividad rompiendo experiencia manual |
| **SLI-3: Idempotency Violation Rate** | % de heartbeats duplicados no detectados | 0% | Gap técnico de Brain #5 materializado |
| **OKR-1: T1 Reduction Sostenido** | T1 baseline vs. T1 con heartbeats | ≥30s por 2 semanas | Feature-Positive Effect |
| **OKR-2: Treatment Exposure Rate** | % de eventos externos que activaron flujo real | ≥60% | Infraestructura construida, problema inexistente |
| **OKR-3: Friction-to-Benefit Ratio** | (Tiempo configuración) / (T1 ahorrado/semana) | <1.0 | Valor percibido < costo mantenimiento |

---

## Archivos Clave Existentes a Reutilizar

- `/home/rpadron/proy/mastermind/apps/api/mastermind_cli/orchestrator/task_executor.py` — patrón TaskGroup + semaphores
- `/home/rpadron/proy/mastermind/apps/api/mastermind_cli/api/routes/tasks.py` — BackgroundTasks injection pattern
- `/home/rpadron/proy/mastermind/apps/web/src/stores/wsDispatcher.ts` — WS infrastructure (validar si ya resuelve)
- `/home/rpadron/proy/mastermind/.planning/BRAIN-FEED-05-backend.md` — reglas de seguridad + repository pattern

---

## Next Action

**Ejecutar Fase 0: Evidencia (1 semana)** antes de cualquier línea de código.

1. Elegir UN workflow donde latency de 4-8h SEA un dolor verificado
2. Implementar manual trigger (botón "Check Now")
3. Medir: frecuencia + T1 reduction + outcome impact

**Si T1 < 30s reduction o WS ya resuelve:** Proposal REJECTED. No hay segunda ronda.

---

*Created: 2026-04-06*
*Status: DEFERRED — Pending Concierge MVP validation*
*Next review: After Fase 0 completion*
