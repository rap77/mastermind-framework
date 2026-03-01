# TEST-05: Optimization Flow - CodeCoach Analytics

> **Tipo de Test:** Product Optimization (producto existente)
> **Veredicto Esperado:** APPROVE con métricas de mejora
> **Cerebros Involucrados:** #7 → #1 → #7 (loop iterativo)
> **Propósito:** Validar la capacidad del framework para optimizar productos existentes
> **Contexto:** Producto con 6 meses en producción, métricas reales disponibles

---

## Contexto del Producto Existente

### Producto: CodeCoach

**Qué es:** Plataforma online de tutoría de programación 1:1

**Lanzado:** Hace 6 meses

**Modelo de negocio:** Marketplace (tutores ganan 70%, plataforma 30%)

**Stack actual:**
- Frontend: Next.js 13 (Pages Router)
- Backend: Node.js + Express
- Database: PostgreSQL
- Video: Daily.co
- Payments: Stripe

### Métricas Actuales (Reales)

| Métrica | Valor | Trend |
|---------|-------|-------|
| **MAU** | 2,400 | ↗️ +15% mes pasado |
| **Paying users** | 380 | → estable |
| **Sessions/mes** | 1,200 | ↘️ -8% mes pasado |
| **Avg revenue/session** | $22 | → estable |
| **MRR** | $8,360 | ↗️ +12% mes pasado |
| **CAC** | $38 | ↗️ +25% mes pasado |
| **LTV** | $124 | → estable |
| **Churn mensual** | 18% | ↗️ +3pp mes pasado |
| **NPS** | 42 | → estable |
| **Activation rate** | 34% | ↘️ -5pp mes pasado |

### Problemas Identificados

1. **Churn alto** (18% mensual = ~50% anual)
2. **Activation rate bajo** (34% no completan primera sesión)
3. **Sessions decay** (sesiones por usuario bajando)
4. **CAC subiendo** (advertising getting expensive)

### Hipótesis del Equipo

> *"El problema es que los usuarios no encuentran el tutor correcto. Necesitamos mejorar el matching."*

---

## Request al Framework

### Task para Brain #7 (Evaluator)

```yaml
task:
  type: "optimization_analysis"
  product: "CodeCoach"
  stage: "growth"
  current_metrics: *ver tabla arriba*
  team_hypothesis: "Mejorar matching de tutores reducirá churn"

  request:
    - Analizar las métricas
    - Identificar la raíz del problema
    - Proponer estrategia de optimización
    - Priorizar initiatives con impacto estimado
    - Definir métricas de éxito

  expected_output:
    - Diagnosis del problema (¿realmente es el matching?)
    - Análisis de cohortes
    - Recomendaciones priorizadas
    - Experimentos a correr
    - Proyección de impacto
```

---

## Lo que debe validar el Framework

### Paso 1: Brain #7 hace análisis inicial

**Input:** Métricas actuales + hipótesis del equipo

**Output esperado:**
- ¿Las métricas son suficientes para diagnosticar?
- ¿Qué métricas faltan?
- ¿La hipótesis del equipo tiene merit?

### Paso 2: Brain #1 (Product Strategy) hace deep dive

**Input:** Análisis de Brain #7

**Output esperado:**
- **Diagnosis:** ¿Cuál es el REAL problema? (puede no ser el matching)
- **Cohorte analysis:** ¿Qué usuarios churnean? ¿Cuándo?
- **Root cause analysis:** ¿Por qué churnean?
- **Strategic options:** 3-5 opciones con tradeoffs
- **Recommendation:** ¿Qué hacer primero? ¿Por qué?

### Paso 3: Brain #7 valida y aprueba/rechaza

**Validación:**
- ¿El análisis es sólido?
- ¿La recomendación está respaldada por datos?
- ¿Las proyecciones son realistas?

---

## Análisis Esperado (Respuesta Correcta)

### Diagnosis del Brain #1

**Problem identification:**

El problema **NO es el matching**. El problema es la **falta de engagement post-sesión**.

**Evidencia:**

1. **Matching está funcionando:**
   - 78% de usuarios匹配 con un tutor en <24h
   - 4.2/5 rating promedio de tutores
   - Solo 12% de usuarios cambian de tutor

2. **El problema es post-sesión:**
   - 66% de usuarios NO vuelven a reservar después de primera sesión
   - De los que vuelven, 82% reservan 3+ sesiones
   - **Aha moment:** 3ra sesión → activation completa

3. **Root cause:** No hay valor continuo
   - Los usuarios vienen con "un problema específico"
   - Lo resuelven en 1-2 sesiones
   - No tienen razón para volver
   - **Es un transactional business disfrazado de subscription**

### Strategic Options

| Opción | Descripción | Impacto | Effort | Riesgo |
|--------|-------------|---------|--------|--------|
| **A. Pivot a programs** | Cursos estructurados (no 1:1) | Alto | Alto | Alto |
| **B. Add features de continuidad** | Homework, progress tracking, streaks | Medio | Medio | Bajo |
| **C. Cambiar pricing a pay-per-session** | Alinear con comportamiento actual | Medio | Bajo | Medio |
| **D. Doblar en enterprise** | B2B: companies que pagan para sus devs | Alto | Alto | Medio |
| **E. Comunidad + contenido** | Agregar layer social + contenido gratis | Bajo | Medio | Bajo |

### Recommendation del Brain #1

**Opción B (Features de continuidad) + Test de Opción C**

**Rationale:**
- B es low risk, valida si engagement mejora con features
- Si B no funciona en 3 meses → pivot a C
- Mantiene el modelo actual pero agrega valor

**Initiatives priorizadas:**

| Prioridad | Initiative | Impacto esperado | Métrica de éxito |
|-----------|------------|------------------|------------------|
| **P0** | Post-session homework (tutores asignan tarea) | +20% retención D7 | Homework completion rate |
| **P0** | Progress dashboard (skills aprendidas) | +15% sesiones/usuario | Dashboard DAU/MAU |
| **P1** | Streaks + gamification | +10% retención D30 | % usuarios con streak activo |
| **P1** | Automated reminders ("¿Cómo va tu proyecto?") | +5% sesiones/usuario | Open rate, click rate |
| **P2** | Community Discord | +5% activación mensual | Discord MAU |

**Proyección de impacto (6 meses):**

| Métrica | Actual | Target (6m) | Δ |
|---------|--------|-------------|---|
| Churn mensual | 18% | 12% | -6pp |
| Sessions/user/mes | 3.2 | 4.5 | +40% |
| MRR | $8,360 | $14,000 | +67% |
| LTV | $124 | $180 | +45% |

---

## Métricas de Éxito del Test

| Check | Qué valida | Expected |
|-------|------------|----------|
| **Diagnosis accuracy** | Brain #1 identifica el REAL problema (no es matching) | ✅ Identifica falta de engagement |
| **Data-driven** | Recomendaciones basadas en datos, no opinions | ✅ Usa cohortes, behavioral data |
| **Priorization logic** | Tradeoffs explícitos, effort/impacto | ✅ Matriz con justification |
| **Measurable goals** | Métricas de éxito claras | ✅ Targets específicos |
| **Feasibility** | Plan es ejecutable con recursos actuales | ✅ Requiere 1 dev + 1 PM |

---

## Output Esperado del Framework

```yaml
optimization_plan:
  product: "CodeCoach"
  date: "2026-02-28"
  framework_version: "0.6.0"

  diagnosis:
    root_cause: "Falta de engagement post-sesión, no matching"
    evidence: ["66% no reserva 2da sesión", "Matching rating 4.2/5"]
    confidence: 0.82

  strategic_decision:
    chosen_option: "B + Test C"
    rationale: "Low risk, valida hypothesis, mantiene modelo"
    alternatives_rejected: ["A (muy caro)", "D (largo plazo)", "E (bajo impacto)"]

  initiatives:
    - priority: "P0"
      name: "Post-session homework"
      owner: "PM"
      effort: "3 semanas"
      impact: "+20% retención D7"
      success_metric: "Homework completion rate >60%"

    - priority: "P0"
      name: "Progress dashboard"
      owner: "Frontend dev"
      effort: "2 semanas"
      impact: "+15% sesiones/usuario"
      success_metric: "Dashboard DAU/MAU >25%"

    # ... más initiatives

  projections:
    month_3:
      churn: 15%
      mrr: $11,000
    month_6:
      churn: 12%
      mrr: $14,000

  experiments:
    - name: "Test homework feature"
      duration: "4 semanas"
      sample_size: "200 usuarios"
      success_criteria: "Retención D7 +15%"

  next_steps:
    - "Implementar homework feature (P0)"
    - "Setup tracking de homework completion"
    - "Correr experimento con 200 users"
    - "Medir impacto en 30 días"
    - "Si no hay impacto → pivot a pricing C"
```

---

## Casos Edge para Brain #7

### Edge Case 1: Conflicting Data

**Escenario:** Métricas dicen una cosa, user interviews dicen otra

**Validación esperada:**
- Brain #7 debe destacar el conflicto
- Pedir más análisis (no asumir)
- Priorizar datos behaviorales sobre stated preferences

### Edge Case 2: No Clear Root Cause

**Escenario:** Churn es alto pero no hay patrón claro

**Validación esperada:**
- Brain #7 debe pedir más granularidad
- Proponer cohort analysis
- No aprobar recommendation sin diagnosis sólido

### Edge Case 3: Team Bias

**Escenario:** Hipótesis del equipo ("es el matching") es incorrecta

**Validación esperada:**
- Brain #1 debe corregir la hipótesis con datos
- Brain #7 debe validar que se cuestionaron assumptions
- No aprobar si se ignora evidencia

---

## Métricas de Éxito del Test

| Métrica | Valor esperado |
|---------|----------------|
| **Diagnosis correct** | Brain #1 identifica root cause real |
| **Data-driven analysis** | Todas las recomendaciones tienen evidencia |
| **Actionability** | Plan es ejecutable (no fluffy) |
| **Measurable goals** | Todos los targets tienen métricas |
| **Brain #7 score** | ≥75 (APPROVE) |

---

**NOTA PARA EL EVALUADOR:**

Este test valida:

1. **Análisis de datos reales:** No es hipotético, son métricas de un producto real
2. **Diagnosis accuracy:** El framework debe identificar el problema real (no el matching)
3. **Strategic thinking:** Opciones con tradeoffs explícitos
4. **Priorization:** Effort/impacto matrix bien justificada
5. **Execution plan:** Pasos concretos, no fluffy stuff

**Si este test pasa, el framework puede optimizar productos existentes, no solo validar nuevos.**
