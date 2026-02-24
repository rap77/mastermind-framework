# Evaluator Protocol — Protocolo de Evaluación del Cerebro #7

Este documento describe el protocolo completo de evaluación que el Cerebro #7 sigue para evaluar outputs de los cerebros 1-6.

---

## Overview

El protocolo de evaluación tiene **5 fases**:

1. **Intake** — Recibir y clasificar el input
2. **Evaluación** — Ejecutar checks y detectar problemas
3. **Scoring** — Calcular puntaje y determinar veredicto
4. **Veredicto** — Generar reporte con instrucciones
5. **Registro** — Guardar para aprendizaje futuro

---

## Fase 1: Intake

### Objetivo
Recibir el output, clasificarlo, y cargar la evaluation-matrix correcta.

### Pasos

```
┌─────────────────────────────────────────────────────────────┐
│  INPUT RECIBIDO                                              │
│  - source_brain: (ej: "01-product-strategy")                │
│  - output_type: (ej: "product-brief")                       │
│  - content: (el output a evaluar)                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │  Identificar tipo de   │
        │  output               │
        └────────┬───────────────┘
                 │
    ┌────────────┼────────────┬────────────┬────────────┐
    │            │            │            │            │
    ▼            ▼            ▼            ▼            ▼
product-brief ux-report  ui-design  frontend    backend
    │            │            │        implementation  architecture
    │            │            │            │            │
    ▼            ▼            ▼            ▼            ▼
¿Matrix      ¿Matrix      ¿Matrix      ¿Matrix      ¿Matrix
existe?      existe?      existe?      existe?      existe?
    │            │            │            │            │
    ├──NO──► ESCALATE      └───┐         └─────────┬─────┘
    │                           │                   │
   SÍ                          SÍ                  SÍ
    │                           │                   │
    └─────────────────┬─────────┴───────────────────┘
                      ▼
              Cargar matrix.yaml
                      │
                      ▼
              Verificar que el
              output está completo
                      │
                      ▼
              Continuar a Fase 2
```

### Checklist de Intake

- [ ] Output recibido tiene `source_brain` identificado
- [ ] Output tiene `output_type` identificable
- [ ] Evaluation-matrix existe para este `output_type`
- [ ] Output está completo (no está truncado)

### Decisiones en Intake

| Situación | Acción |
|-----------|--------|
| No existe matrix para output_type | ESCALATE pidiendo que se cree |
| Output está truncado/incompleto | SOLICITAR versión completa |
| No se puede identificar output_type | SOLICITAR aclaración |

---

## Fase 2: Evaluación

### Objetivo
Ejecutar cada check de la matrix y detectar problemas.

### Proceso por Check

```
┌─────────────────────────────────────────────────────────────┐
│  CHECK DE LA MATRIX                                          │
│  - id: "C1"                                                  │
│  - check: "¿Define claramente el problema?"                  │
│  - weight: 10                                                │
│  - fail_action: "REJECT"                                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │  Buscar evidencia en   │
        │  el output            │
        └────────┬───────────────┘
                 │
        ┌────────┴────────┐
        │                 │
     EVIDENCIA        NO EVIDENCIA
     ENCONTRADA        ENCONTRADA
        │                 │
        ▼                 ▼
     PASS              FAIL
        │                 │
        │         ┌──────┴──────┐
        │         │             │
        ▼         ▼             ▼
    Justificar  Explicar   Instrucciones
  específicamente  qué falta  ESPECÍFICAS
        │         │             │
        └────┬────┴──────┬──────┘
             ▼           ▼
    Verificar bias   Verificar
    catalog?        benchmarks?
```

### Ejecución de Checks

Por cada check en la matrix:

1. **Leer el criterio** — ¿Qué se está evaluando?
2. **Buscar evidencia** — ¿Dónde en el output está la respuesta?
3. **Determinar resultado** — PASS o FAIL
4. **Documentar**:
   - Si PASS: Justificación específica (cita del output)
   - Si FAIL: Qué falta + instrucción específica de corrección

### Detección de Sesgos

```
POR CADA CHECK:
├─ ¿Tiene asociado un bias_check?
│  ├─ SÍ → Buscar signals del sesgo en el output
│  │  ├─ ¿Signal detectada?
│  │  │  ├─ SÍ → Registrar bias con evidencia
│  │  │  └─ NO → Continuar
│  └─ NO → Continuar
└─ Siguiente check
```

### Comparación con Benchmarks

Si el output incluye métricas:

```
MÉTRICA ENCONTRADA:
├─ ¿Existe benchmark?
│  ├─ Sí → Comparar valor vs benchmark
│  │  ├─ Above "great" → Registrar como positivo
│  │  ├─ Within "good" → Registrar como aceptable
│  │  ├─ Below "good" → Registrar como warning
│  │  └─ Below "red_flag" → Registrar como problema
│  └─ No → Solicitar al cerebro que declare su baseline
└─ Siguiente métrica
```

---

## Fase 3: Scoring

### Objetivo
Calcular el puntaje total y determinar el veredicto.

### Cálculo del Score

```
SCORE_TOTAL = SUM(checks_pasados × weight) / SUM(total_weights) × 100

Ejemplo:
- 10 checks pasados de 15 totales
- Suma de weights de checks pasados = 95
- Suma de weights de checks totales = 138
- Score = 95 / 138 × 100 = 68.8%
```

### Score por Categoría

```
SCORE_COMPLETENESS = SUM(passed_completeness × weight) / SUM(total_completeness_weights)
SCORE_QUALITY = SUM(passed_quality × weight) / SUM(total_quality_weights)
SCORE_HONESTY = SUM(passed_honesty × weight) / SUM(total_honesty_weights)
SCORE_VIABILITY = SUM(passed_viability × weight) / SUM(total_viability_weights)
```

### Determinación del Veredicto

```
┌─────────────────────────────────────────────────────────────┐
│  CALCULAR SCORE TOTAL                                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
              ┌──────────────┐
              │ score >= 80? │
              └──────┬───────┘
                     │
            ┌────────┴────────┐
            │                 │
           SÍ                NO
            │                 │
            ▼                 ▼
       APPROVE      ┌──────────────────┐
                    │  score >= 60?    │
                    └──────┬───────────┘
                           │
                  ┌────────┴────────┐
                  │                 │
                 SÍ                NO
                  │                 │
                  ▼                 ▼
           CONDITIONAL         REJECT
                  │                 │
                  │         ┌───────┴────────┐
                  │         │                │
                  │         │      ¿3er rechazo
                  │         │      consecutivo?
                  │         │         │      │
                  │         │        SÍ     NO
                  │         │         │      │
                  │         └───┬─────┘      │
                  │             │            │
                  ▼             ▼            ▼
              Iterar      ESCALATE      REJECT
```

---

## Fase 4: Veredicto

### Objetivo
Generar el evaluation-report con el veredicto y instrucciones.

### Contenido del Reporte

```yaml
evaluation_id: "EVAL-{YYYY-MM-DD}-{NNN}"
timestamp: "2026-02-23T23:45:00Z"
evaluator: "brain-07-critical-evaluator"

# Input
source_brain: "01-product-strategy"
output_type: "product-brief"
output_file: "brief-taskflow-pro.md"
iteration: 1

# Scoring
verdict: "CONDITIONAL"  # APPROVE | CONDITIONAL | REJECT | ESCALATE
score_total: 68
scores_by_category:
  completeness: 70
  quality: 55
  intellectual_honesty: 75
  commercial_viability: 60

# Detail
passed_checks:
  - id: "C1"
    check: "¿Define claramente el problema?"
    justification: "Linea 15: 'El problema es que los product managers no
      pueden priorizar Features porque no tienen un framework claro'"

failed_checks:
  - id: "Q2"
    check: "¿Las métricas son outcomes?"
    failure_reason: "Incluye 'features lanzadas' como métrica de éxito"
    fix_instruction: "Reemplazar por 'D7 retention rate' o 'D7 activation rate'"

biases_detected:
  - bias_id: "BIAS-01"
    name: "Confirmation Bias"
    evidence: "Solo cita casos de éxito de discovery, no menciona
      proyectos donde discovery falló"

redirect_instructions:
  to_brain: "01-product-strategy"
  action: "REVISE"
  specific_fixes:
    - "Reemplazar métricas de output por outcomes"
    - "Incluir al menos 1 caso donde discovery falló y por qué"
  max_iterations: 3
```

### Veredicto APPROVE

```
┌─────────────────────────────────────────────────────────────┐
│  APPROVE — score >= 80                                      │
│                                                             │
│  Acción: Output pasa al siguiente cerebro o fase            │
│  Registro: Guardar en logs/evaluations/ como precedente     │
│  positivo                                                   │
└─────────────────────────────────────────────────────────────┘
```

### Veredicto CONDITIONAL

```
┌─────────────────────────────────────────────────────────────┐
│  CONDITIONAL — score 60-79                                  │
│                                                             │
│  Acción: Devolver al cerebro original con:                  │
│  - Lista de checks fallidos                                │
│  - Instrucciones ESPECÍFICAS de corrección                  │
│  - Iteration count + 1                                     │
│                                                             │
│  Si iteration > 3 → ESCALATE al humano                      │
└─────────────────────────────────────────────────────────────┘
```

### Veredicto REJECT

```
┌─────────────────────────────────────────────────────────────┐
│  REJECT — score < 60                                        │
│                                                             │
│  Acción: Devolver al cerebro original con:                  │
│  - Explicación de problemas fundamentales                   │
│  - Recomendación: REDO o REVISE                            │
│  - Instrucciones específicas                               │
│  - Iteration count + 1                                     │
│                                                             │
│  Si iteration > 3 → ESCALATE al humano                      │
└─────────────────────────────────────────────────────────────┘
```

### Veredicto ESCALATE

```
┌─────────────────────────────────────────────────────────────┐
│  ESCALATE — 3er rechazo o situación sin resolver            │
│                                                             │
│  Acción: Generar escalation-report.yaml con:                │
│  - Historial de iteraciones                                │
│  - Checks fallidos recurrentes                             │
│  - Recomendación del evaluador                             │
│  - Contexto completo para decisión humana                   │
│                                                             │
│  Registro: Guardar en logs/precedents/                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Fase 5: Registro

### Objetivo
Guardar el reporte y aprender para futuras evaluaciones.

### Archivos Generados

```
logs/
├── evaluations/
│   └── EVAL-2026-02-23-001.yaml  # Reporte de evaluación
└── precedents/
    └── PREC-001-vanity-metrics.yaml  # Precedente (si hay conflicto resuelto)
```

### Precedentes

Un precedente se crea cuando:

1. El humano resuelve un conflicto entre cerebros
2. El evaluador identifica un patrón recurrente
3. Se establece una nueva regla de evaluación

Estructura de precedente:

```yaml
precedent_id: "PREC-001"
date: "2026-02-23"
conflict:
  brain_a: "01-product-strategy"
  brain_b: "07-evaluator"
  issue: "Strategy propuso 'usuarios registrados' como KR. Evaluator rechazó por ser vanity metric."
resolution:
  decided_by: "human"
  decision: "Evaluator tenía razón. KR debe ser 'usuarios activos D7' no 'registrados'."
  rule: "Nunca aceptar métricas de registro/descarga como Key Results. Siempre exigir métricas de activación o retención."
applied_in_future:
  - "EVAL-2026-03-20-003"
  - "EVAL-2026-04-02-001"
```

---

## Ejemplo Completo de Evaluación

### Input

```
SOURCE_BRAIN: 01-product-strategy
OUTPUT_TYPE: product-brief
CONTENT: |
  # TaskFlow Pro — Product Brief

  ## Problema
  Los product managers en startups no pueden priorizar features porque
  no tienen un framework claro de priorización.

  ## Audiencia
  Product managers en startups etapa seed, con 1-3 años de experiencia,
  en empresas B2B SaaS.

  ## Métricas de Éxito
  - OKR1: Lanzar MVP en Q2 2026
  - OKR2: Alcanzar 1,000 usuarios registrados
  - OKR3: Lanzar 5 features clave

  ## Riesgos de Discovery
  - Valor: ¿Realmente necesitan un framework o solo necesitan tiempo?
  - Usabilidad: ¿La interfaz será suficientemente simple?
  - Factibilidad: ¿Podemos construir el MVP en 3 meses?
  - Viabilidad: ¿Podremos monetizar?

  ## Evidencia
  Entrevistamos a 5 PMs y todos reportaron el mismo problema.
  "Es un dolor real," dijo uno de ellos.
```

### Ejecución de Evaluación

```
FASE 1: INTAKE
- source_brain: 01-product-strategy ✓
- output_type: product-brief ✓
- Matrix: evaluation-matrices/product-brief.yaml ✓
- Output completo: ✓

FASE 2: EVALUACIÓN

Check C1 (weight 10): ¿Define claramente el problema?
  Evidencia: "Los product managers en startups no pueden priorizar
  features porque no tienen un framework claro de priorización"
  Resultado: PASS ✓

Check C2 (weight 8): ¿Identifica persona específica?
  Evidencia: "Product managers en startups etapa seed, con 1-3 años
  de experiencia, en empresas B2B SaaS"
  Resultado: PASS ✓

Check C3 (weight 9): ¿Tiene métricas OKR con Key Results numéricos?
  Evidencia: "OKR2: Alcanzar 1,000 usuarios registrados"
  Resultado: PASS ✓ (pero ve Q2)

Check C4 (weight 10): ¿Evaluó los 4 riesgos de discovery?
  Evidencia: Lista los 4 riesgos
  Resultado: PASS ✓

Check Q2 (weight 8): ¿Las métricas son outcomes?
  Evidencia: "1,000 usuarios registrados" → es OUTPUT, no OUTCOME
  Resultado: FAIL ✗
  Fix: Reemplazar por "D7 activation rate >35%"

Check H1 (weight 8): ¿Reconoce lo que NO sabe?
  Evidencia: No hay sección de "Lo que no sabemos"
  Resultado: FAIL ✗
  Fix: Agregar sección con suposiciones no validadas

Check H3 (weight 8): ¿Incluye análisis de fallo?
  Evidencia: No hay pre-mortem o inversión
  Resultado: FAIL ✗
  Fix: Aplicar inversión de Munger: "¿Por qué esto fallaría?"

Check V1 (weight 9): ¿Hay evidencia de demanda?
  Evidencia: "Entrevistamos a 5 PMs"
  Resultado: PASS ✓

BIAS CHECK:
- BIAS-01 (Confirmation Bias): Solo mencione opinión positiva
  Evidence: '"Es un dolor real," dijo uno de ellos' — sin contra-evidencia
  Resultado: BIAS DETECTED ⚠

FASE 3: SCORING
Puntos obtenidos: C1(10) + C2(8) + C3(9) + C4(10) + Q2(0) + H1(0) + H3(0) + V1(9) = 46
Total posible: 138
Score: 46 / 138 × 100 = 33.3%

FASE 4: VEREDICTO
Score: 33.3% → REJECT
```

### Output del Evaluador

```
VEREDICTO: REJECT
SCORE: 33/100 (33%)

RESUMEN: El product-brief tiene problemas fundamentales. Aunque define el
problema y la audiencia, las métricas son outputs no outcomes, no hay
reconocimiento de lo que no se sabe, falta análisis de fallo, y hay
confirmation bias evidente (solo opiniones positivas).

CHECKS PASADOS (4/12):
- C1: Problema claramente definido ✓
- C2: Persona específica (PMs en startups seed, B2B SaaS, 1-3 años exp) ✓
- C3: OKRs definidos (aunque necesitan corrección) ✓
- C4: 4 riesgos de discovery evaluados ✓
- V1: Evidencia de demanda (5 entrevistas) ✓

CHECKS FALLIDOS CRÍTICOS:
- Q2: Métricas son outputs, no outcomes
  PROBLEMA: "1,000 usuarios registrados" no indica que el producto genera
  valor. Pueden registrarse y nunca volver.
  FIX: Reemplazar por outcomes como:
  - "D7 activation rate >35%"
  - "D30 retention rate >15%"
  - "DAU/MAU >20%"

- H1: No reconoce lo que NO sabe
  PROBLEMA: El brief presenta certeza total sin reconocer suposiciones.
  FIX: Agregar sección "Lo que no sabemos" con:
  - No sabemos si PMs usarán el framework consistentemente
  - No sabemos si el problema es de falta de framework o de falta de tiempo
  - No sabemos si están dispuestos a pagar por esto

- H3: Sin análisis de fallo (pre-mortem)
  PROBLEMA: Solo piensa en éxito, nunca en fracaso.
  FIX: Aplicar inversión de Munger: "¿Qué tendría que ser verdad para que
  esto falle?" Considerar:
  - PMs no adopten el framework por "too much process"
  - La competencia (RICE, ICE, etc.) sea suficiente
  - El framework sea teórico y no práctico

SESGOS DETECTADOS:
- BIAS-01 (Confirmation Bias): Solo cita opinión positiva ("Es un dolor
  real"), sin incluir contra-evidencia o PMs que NO reportaron el problema
  QUESTION: ¿Qué dijeron los PMs que NO consideran este un problema? ¿Por qué?

REDIRECT INSTRUCTIONS:
TO BRAIN: 01-product-strategy
ACTION: REVISE
SPECIFIC FIXES:
1. Reemplazar métricas de output (registrados, features) por outcomes
   (retención, activación, engagement)
2. Agregar sección "Lo que no sabemos" reconociendo suposiciones
3. Aplicar inversión de Munger: análisis de cómo esto podría fallar
4. Incluir contra-evidencia: PMs entrevistados que NO reportaron el problema
5. Considerar: ¿es un framework lo que necesitan o es otra cosa?
MAX ITERATIONS: 3
```

---

## Debugging del Protocolo

### Problema: Evaluaciones inconsistentes

**Síntoma**: Mismo output tipo recibe diferentes veredictos en diferentes evaluaciones.

**Causa probable**: Checks sin criterios claros de PASS/FAIL.

**Solución**: Refinar la evaluation-matrix con ejemplos específicos de qué constituye PASS.

### Problema: Demasiados ESCALATEs

**Síntoma**: Muchas evaluaciones terminan en ESCALATE.

**Causa probable**: Evaluation-matrix incompleta o falta de precedentes.

**Solución**: 1) Crear las matrices faltantes, 2) Documentar precedentes de situaciones similares.

### Problema: Sesgos no detectados

**Síntoma**: Outputs con confirmation bias evidente pasan la evaluación.

**Causa probable**: Bias-check no asociado a los checks relevantes.

**Solución**: Revisar bias-catalog.yaml y asociar bias_check a checks donde sea relevante.

---

## Métricas del Evaluador

El propio evaluador debe medir su desempeño:

| Métrica | Fórmula | Target |
|---------|---------|--------|
| APPROVE rate | APROBADOS / TOTALES | 30-50% |
| CONDITIONAL rate | CONDITIONALES / TOTALES | 30-40% |
| REJECT rate | RECHAZADOS / TOTALES | 10-30% |
| ESCALATE rate | ESCALADOS / TOTALES | <5% |
| Avg iterations por output | SUM(iterations) / TOTALES | <2 |
| Bias detection rate | outputs_con_bias / TOTALES | 20-40% |

Si APPROVE rate > 70%, el evaluador está siendo muy blando.
Si REJECT rate > 50%, el evaluador está siendo muy duro.

---

**Versión**: 1.0.0
**Última actualización**: 2026-02-23
