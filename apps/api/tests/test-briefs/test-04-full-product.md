# TEST-04: Full Product Flow - FitTrack Pro

> **Tipo de Test:** Full Product Flow (todos los cerebros)
> **Veredicto Esperado:** APPROVE en cada etapa
> **Cerebros Involucrados:** #1 → #2 → #3 → #4 → #5 → #6 → #7 (loop)
> **Propósito:** Validar que los 7 cerebros pueden trabajar juntos coherentemente
> **Complexity:** Alta (requiere outputs consistentes entre cerebros)

---

## Brief Inicial (para Brain #1)

### Producto Propuesto: FitTrack Pro

**Concepto:** Una app de fitness que usa IA para generar rutinas de ejercicio personalizadas basadas en:
- Objetivos del usuario (perder peso, ganar músculo, resistencia)
- Equipamiento disponible (gimnasio, casa, sin equipamiento)
- Tiempo disponible (10min, 30min, 60min)
- Historial de progreso

**Target audience:** Personas 25-40 años que quieren hacer ejercicio pero no tienen tiempo/capacidad para diseñar sus propias rutinas.

**Unique value prop:** "Como tener un personal trainer en tu pocket, pero fraction del costo."

**Monetización:** Freemium
- Gratis: 3 rutinas/semana
- Premium: $9.99/mes (rutinas ilimitadas + nutrition plans)

**Tech stack inicial:** React Native + Firebase

---

## Lo que debe validar cada cerebro:

### Brain #1: Product Strategy
**Output esperado:**
- ¿Es este problema real? (evidencia de demanda)
- ¿Está bien definido el target?
- ¿El modelo de negocio tiene sentido?
- ¿Cuáles son los riesgos?
- ¿Qué features son MUST vs NICE?

### Brain #2: UX Research
**Input:** Output del Brain #1
**Output esperado:**
- ¿Cómo validamos que este problema existe?
- ¿Qué entrevistas/hay que hacer?
- ¿Qué comportamientos observamos?
- ¿Insights cualitativos clave?
- User research plan

### Brain #3: UI Design
**Input:** Outputs de Brain #1 + #2
**Output esperado:**
- Design system apropiado para el target
- Key screens y su estructura
- Component library
- Responsive considerations
- Accessibility requirements

### Brain #4: Frontend
**Input:** Output del Brain #3
**Output esperado:**
- Tech stack recomendado (React vs alternatives)
- Architecture (component structure, state management)
- Performance considerations
- PWA vs Native decision
- Implementation roadmap

### Brain #5: Backend
**Input:** Outputs de Brain #1 + #4
**Output esperado:**
- API architecture (REST vs GraphQL vs tRPC)
- Database schema
- AI integration (cómo generar rutinas con IA)
- Auth strategy
- Infrastructure recommendations

### Brain #6: QA/DevOps
**Input:** Outputs de Brain #4 + #5
**Output esperado:**
- Testing strategy (unit, integration, e2e)
- CI/CD pipeline
- Monitoring y alerting
- Error tracking
- Deployment strategy

### Brain #7: Evaluator (en cada etapa)
**Valida:**
- Calidad del output de cada cerebro
- Consistencia entre outputs de diferentes cerebros
- Flags si hay contradicciones
- Aprueba/rechaza/condicional cada output

---

## Outputs Esperados del Framework

### Estructura de comunicación entre cerebros

```yaml
task_flow:
  TASK-001:
    from: "user"
    to: "brain-01"
    type: "request"
    content:
      brief: "FitTrack Pro initial brief"
      flow_type: "full_product"
      version: "1.0.0"

  TASK-002:
    from: "brain-01"
    to: "brain-07"
    type: "output"
    content:
      problem_validation: "APPROVED"
      target_segment: "25-40 y.o., busy professionals"
      must_have_features: ["AI routines", "progress tracking", "equipment filter"]
      nice_to_have: ["nutrition plans", "social features"]
      business_model: "Freemium validated"
      risks: ["Competition high", "AI costs unknown"]
      confidence: 0.75

  TASK-003:
    from: "brain-07"
    to: "brain-02"
    type: "approval"
    content:
      task_id: "TASK-002"
      veredict: "CONDITIONAL"
      score: 72
      feedback: ["Validar willingness to pay con experimento", "Analizar competencia profunda"]

  # ... continua con brain-02, brain-03, etc.
```

### Validaciones clave del Brain #7

| Checkpoint | Qué valida | Score mínimo |
|------------|------------|--------------|
| **CP1: Product Brief** | Problema real, target claro, métricas | ≥70 |
| **CP2: UX Research** | Insights de usuarios reales, no asumptions | ≥70 |
| **CP3: UI Design** | Consistente con research, accesible | ≥70 |
| **CP4: Frontend** | Tech stack justificado, architecture sólida | ≥70 |
| **CP5: Backend** | APIs diseñadas, escalabilidad considerada | ≥70 |
| **CP6: QA/DevOps** | Testing coverage, CI/CD definido | ≥70 |
| **CP7: Integration** | Consistencia entre todos los outputs | ≥75 |

---

## Casos de Test para Brain #7

### Test 7.1: Consistencia de Tech Stack

**Escenario:** Brain #4 recomienda React Native, pero Brain #5 asume web-first

**Validación esperada:**
- Brain #7 debe detectar la inconsistencia
- Pedir aclaración a Brain #4 o #5
- No aprobar hasta que se resuelva

### Test 7.2: Completeness de Features

**Escenario:** Brain #3 diseña UI para "social features" que no fueron aprobadas por Brain #1

**Validación esperada:**
- Brain #7 debe detectar que se están diseñando features no aprobadas
- Rechazar output de Brain #3 o pedir revisión

### Test 7.3: Feasibility Check

**Escenario:** Brain #5 propone architecture que requiere equipo de 5 personas, pero el brief asume equipo de 1-2

**Validación esperada:**
- Brain #7 debe detectar mismatch de recursos
- Pedir a Brain #5 que ajuste a recursos disponibles

---

## Métricas de Éxito del Test

| Métrica | Valor esperado | Cómo medir |
|---------|----------------|------------|
| **Outputs aprobados** | 6/6 cerebros | Count de approvals de Brain #7 |
| **Consistency score** | ≥80% | % de outputs sin contradicciones |
| **Iteration rounds** | ≤2 por cerebro | Promedio de idas/vueltas |
| **Total time** | <30 min | Tiempo total de ejecución |
| **Final approval** | APPROVE | Veredicto final de Brain #7 |

---

## Documentación de Resultados

### Template de reporte

```markdown
## TEST-04 Results: FitTrack Pro

### Execution Summary
- **Date:** 2026-02-28
- **Framework version:** 0.6.0
- **Test duration:** 23 min
- **Final veredict:** APPROVE (78)

### Brain Outputs

| Brain | Score | Veredicto | Iterations |
|-------|-------|-----------|------------|
| #1 Product Strategy | 72 | CONDITIONAL | 2 |
| #2 UX Research | 81 | APPROVE | 1 |
| #3 UI Design | 76 | APPROVE | 1 |
| #4 Frontend | 74 | APPROVE | 1 |
| #5 Backend | 71 | APPROVE | 1 |
| #6 QA/DevOps | 83 | APPROVE | 1 |

### Issues Detected by Brain #7

1. **Issue 1:** Brain #3 diseñó features no aprobadas por Brain #1
   - **Resolución:** Brain #3 revisó y eliminó social features
   - **Tiempo de resolución:** 3 min

2. **Issue 2:** Inconsistencia tech stack entre Brain #4 y #5
   - **Resolución:** Brain #5 ajustó architecture para React Native
   - **Tiempo de resolución:** 5 min

### Final Output Summary

El framework generó:
- ✅ Product requirements document
- ✅ User research plan
- ✅ UI design system
- ✅ Frontend architecture
- ✅ Backend API spec
- ✅ QA testing strategy
- ✅ CI/CD pipeline

**Validation:** Framework completo funciona coherentemente.

### Recommendations

1. Agregar checkpoint intermedio después de Brain #3 para detectar inconsistencias más temprano
2. Crear template standard de outputs para reducir variabilidad
3. Mejorar comunicación entre Brain #4 y #5 sobre tech stack
```

---

**NOTA PARA EL EVALUADOR:**

Este test es el **más comprehensivo** del suite. Valida:

1. **Flow completo:** Los 7 cerebros en secuencia
2. **Comunicación inter-cerebro:** YAML structure con from/to/type
3. **Brain #7 como meta-evaluador:** Valida cada output + consistencia global
4. **Detección de inconsistencias:** 3 casos de test específicos
5. **Métricas cuantificables:** Para medir performance del framework

**Si este test pasa, el framework está listo para producción.**
