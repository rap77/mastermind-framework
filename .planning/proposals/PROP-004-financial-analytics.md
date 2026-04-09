---
proposal_id: "PROP-004"
title: "Analytics Financiero por Agente y Proyecto"
status: "DEFERRED"
created_at: "2026-04-06"
last_updated: "2026-04-06"
brain_evaluations:
  - brain: "Brain #1 (Product Strategy)"
    verdict: "DEFERRED"
    confidence: 85%
  - brain: "Brain #7 (Growth/Data - Domain)"
    verdict: "APPROVED_WITH_CONDITIONS"
    confidence: 80%
  - brain: "Brain #7 (Growth/Data - Meta-evaluator)"
    verdict: "DEFERRED"
    confidence: 90%
---

# PROP-004: Analytics Financiero por Agente y Proyecto

**Estado:** 🔴 **DEFERRED** — Prematuro sin revenue model ni paying customers

**Confianza:** 90%

---

## Resumen Ejecutivo

**Problema identificado:** Observabilidad limitada — hay audit log pero NO dashboards profundos de:
- Costo por tarea
- ROI por agente
- Tiempo a completar

**Solución propuesta:** Dashboard de analytics financiero real con métricas por agente y proyecto.

**Valor declarado:** Visibilidad económica del sistema — saber qué agentes generan valor vs costo.

---

## Evaluación de Brains

### Brain #1 (Product Strategy) — DEFERRED 🔴 (85% confianza)

#### ✅ Lo Bueno
- **Sistema de logging listo:** `ExperienceRecord` tiene `duration_ms`, `brain_id`, `custom_metadata` extensible
- **Outcome metrics YA definidas:** Delta-T1, Knowledge Yield, Planning Accuracy (Phase 14 complete)
- **Preparación para futuro multi-tenant:** Si v3.0 evoluciona a plataforma multi-usuario, tener costos permitirá billing

#### ⚠️ Lo Que Falta
- **Modelo de costos:** No hay precios por tokens, tiempo de ejecución, storage. Builder corre todo localmente — no hay factura externa.
- **Acción clara:** Si supiéramos "Brain #1 cuesta $0.15", ¿qué haríamos diferente? ¿Prompts más cortos? Ya optimizamos por velocidad.
- **Contexto de viabilidad:** No hay paying customers, no hay pricing model, Phase 5 (Marketplace) DEFERRED

#### 🚨 Peligros
- **Value Risk ALTO:** El único usuario hoy es el builder. Su recurso escaso es tiempo, no costo de Claude API. Delta-T1 ya mide eso.
- **Viability Risk ALTO:** Sin revenue model, no hay "ROI" para calcular. Es como medir eficiencia de un negocio que no factura.
- **Usability Risk MEDIO:** Dashboard financiero requiere interpretación. ¿Qué significa "costo por tarea = $0.12"?

#### 💭 Sugerencias
1. **Diferir a Phase 15+** — Solo cuando haya ≥1 paying customer O pricing model definido
2. **Telemetry primero** — Implementar como recolección de datos (no dashboard completo)
3. **Alinear con TOP 3 outcomes** — Conectar métricas financieras con Delta-T1, Knowledge Yield, Planning Accuracy

---

### Brain #7 (Growth/Data - Domain) — APPROVED_WITH_CONDITIONS 🟡 (80% confianza)

#### ✅ Lo Bueno
- **duration_ms YA capturado** — Proxy de compute time
- **quality_score YA calculado** — Proxy de valor (Hormozi value equation)
- **custom_metadata JSONB** — Permite agregar cost metrics SIN migración de schema

#### ⚠️ Lo Que Falta
- **Capturar tokens:** `prompt_tokens`, `completion_tokens` en cada ejecución
- **Capturar model_id** — Para aplicar pricing correcto
- **Calcular roi_score asincrónicamente** — NO en hot path de ejecución

#### 🚨 Peligros
- **Goodhart's Law:** Si "bajo costo" se vuelve target, deja de ser buena métrica. Optimizar para barato ≠ efectivo.
- **Sunk Cost Fallacy:** Resistirse a apagar agente caro PERO con ROI < 1.0
- **Overhead Cascade:** Medir costo puede aumentar T1 → profecía autocumplida (agentes se ven "más caros" porque medirlos los hace lentos)

#### 💭 Sugerencias

**ROI Score (Hormozi adaptado):**
```
ROI = (quality_score × Perceived_Likelihood) / (Financial_Cost + duration_ms)
```

**Thresholds:**
- `ROI ≥ 4.0` → Altamente rentable (template candidate)
- `ROI ≥ 1.0` → Rentable (aceptar)
- `ROI < 1.0` → "Dead offer" (rechazar o refactorizar)

**Implementación:**
1. Agregar `token_usage: {prompt, completion}` a `custom_metadata`
2. Crear tabla `model_pricing` con `{model_id, cost_per_1k_tokens}`
3. Background job que calcule `roi_score` asincrónicamente
4. Endpoint `/api/financial-analytics` que agregue por brain_id

---

### Brain #7 (Growth/Data - Meta-evaluator) — DEFERRED 🔴 (90% confianza)

#### Veredicto Final

**DEFERRED** — La propuesta es técnicamente factible PERO estratégicamente prematura.

**Razón:** El sistema está en etapa de **"Empathy" o "Stickiness"** (validar valor), no de **"Revenue"** (optimizar costos). Intentar optimizar ROI antes de validar Product-Market Fit = invertir prioridades.

#### Tensiones Identificadas

**TENSIÓN #1: Value vs. Infrastructure**
- Brain #1: "DEFERRED — no hay paying customers, Value Risk alto"
- Brain #7 (domain): "APPROVED_WITH_CONDITIONS — datos técnicos disponibles"
- **Ganador:** Brain #1 — La pregunta "¿podemos medir?" ≠ "¿debemos medir?"

**TENSIÓN #2: ROI Score Definition**
- Brain #7 (domain): "Calcular ROI Score = (quality × Likelihood) / (Financial_Cost + Time_Delay)"
- **Problema:** Sin revenue ni pricing model, el "R" en ROI es ZERO
- **Ganador:** Brain #1 — Diferir hasta que exista revenue model

**TENSIÓN #3: Dashboard vs. Telemetry**
- Brain #1: "Implementar como 'Telemetry' primero (no dashboard completo)"
- Brain #7 (domain): Aprobó con condiciones
- **Ganador:** Brain #1 — Telemetry silenciosa NO tiene riesgo de Goodhart's Law

#### Feedback Loops Sistémicos Identificados

**1. Goodhart's Law Death Spiral:**
Dashboard muestra "Agente A = $0.50, Agente B = $0.10" → Usuario selecciona Agente B siempre → Knowledge Yield baja → Delta-T1 sube → Sistema más barato PERO más inútil.

**2. Overhead Cascade:**
Tracking de tokens → +1-2 API calls → T1 aumenta 50-100ms → Feature que debería "optimizar costos" termina COSTANDO más dinero.

**3. Lollapalooza Effect (Munger):**
"Super-respuesta a Incentivos" (optimizar costo) + "Evitación de Inconsistencia" = degradación irreversible de la inteligencia del sistema.

---

## Condiciones CRÍTICAS para Aprobar (Futuro)

### Condición #1: Market Hunger Signal (BLOCKER estratégico)
- Señal: ≥5 preguntas espontáneas/semana sobre costos
- Medición: SLI-1 (The Mom Test) — contar preguntas en Slack/Discord/GitHub issues
- Si <1/semana → **DEFERRED**

### Condición #2: Revenue Model Existence (BLOCKER estratégico)
- Pricing model definido + al menos 1 paying customer
- Sin revenue, ROI es conceptual, no real

### Condición #3: TOP 3 Outcomes Estables (BLOCKER de prioridad)
- Delta-T1 <90s sostenido por 2 semanas
- Knowledge Yield >30%
- Planning Accuracy >0.75
- Solo cuando outcomes core están estabilizados, optimizar costos tiene sentido

### Condición #4: Telemetry-First Implementation (BLOCKER técnico)
- Capturar `prompt_tokens`, `completion_tokens`, `model_id` en `custom_metadata`
- **NO** exponer dashboard, **NO** calcular ROI Score
- Solo escribir datos para construcción de "Inside View" histórica

### Condición #5: T1 Overhead Guardrail (BLOCKER técnico)
- Verificar que tracking overhead no aumenta Delta-T1 más de 1-2%
- Si >5% → feature se auto-invalida

---

## Roadmap Sugerido

### Fase 0: Telemetría Silenciosa (1 semana) — **PUEDE empezar AHORA**
- Agregar `prompt_tokens`, `completion_tokens`, `model_id` a `custom_metadata`
- NO dashboard, NO ROI Score
- Construir "Inside View" histórica

### Fase 1: Detección de Market Hunger (ongoing) — **CRÍTICO**
- Medir SLI-1 (preguntas espontáneas sobre costos)
- Medir SLI-2 (proxy de desperdicio: 20% ejecuciones consumen 80% tokens?)
- Si SLI-1 <1/semana Y SLI-2 <30% → continuar Fase 0

### Fase 2: Dashboard + ROI Score (Phase 15+ o cuando trigger)
- SI paying customers existen Y Market Hunger ≥5/semana → construir dashboard
- Calcular ROI Score con guardrails (Goodhart's Law, T1 Overhead <2%)

---

## Métricas de Detección Temprana (SLI/OKRs)

| SLI/OKR | Qué mide | Target | ¿Qué indica si falla? |
|---------|----------|--------|----------------------|
| **SLI-1: Market Hunger** | Preguntas espontáneas/semana sobre costos | ≥5/semana | Problema no existe, DEFERRED |
| **SLI-2: Proxy de Desperdicio** | % de ejecuciones que consumen 80% tokens sin mejorar Knowledge Yield | <30% | Ineficiencia sistémica justifica control |
| **SLI-3: T1 Overhead Guardrail** | Aumento de Delta-T1 por tracking overhead | <1-2% | Feature se auto-invalida |
| **OKR-1: Signal-to-Noise Ratio** | % de decisiones de agente cambiadas por dashboard de costos | ≥40% | Dashboard es ruido, no signal |

---

## Riesgo si se Ignora

Construir dashboard financiero AHORA = **sunk cost en UI + backend complexity + risk de Goodhart's Law + overhead en T1**

La asimetría de riesgo es enorme:
- **Costo de esperar:** Telemetría silenciosa (1 semana) + medir SLI-1 (ongoing)
- **Costo de avanzar prematuro:** Sunk cost + risk de Goodhart's Law + overhead + oportunidad perdida en Delta-T1

---

## Archivos Clave Existentes

- `apps/api/mastermind_cli/orchestration/analytics_service.py` — AnalyticsService con P50/P90 latency
- `apps/api/mastermind_cli/models.py` — ExperienceRecord con custom_metadata JSONB
- `.planning/BRAIN-FEED-01-product.md` — Delta-T1, Knowledge Yield, Planning Accuracy definidos

---

## Next Action

**Opción A:** Ejecutar Fase 0 (Telemetría Silenciosa) — PUEDE empezar AHORA
- Agregar tracking de tokens a `custom_metadata`
- NO dashboard, NO ROI Score
- Construir "Inside View" histórica

**Opción B:** Esperar trigger (Market Hunger + Revenue Model)
- Medir SLI-1 (preguntas espontáneas sobre costos)
- Implementar dashboard solo cuando ≥5/semana + paying customer

---

*Created: 2026-04-06*
*Status: DEFERRED — Prematuro sin revenue model ni paying customers*
*Next review: When Market Hunger ≥5/semana OR paying customer exists*
