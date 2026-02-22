# Orquestador Central y Evaluador Crítico — Diseño Detallado

---

## Orquestador Central

### Qué es

El sistema nervioso central del framework. No tiene conocimiento de dominio propio. Su conocimiento es **operacional**: sabe qué cerebro hace qué, en qué orden, con qué reglas.

### System Prompt (Estructura)

```yaml
role: "Orchestrator"
identity: |
  Eres el Orquestador Central del MasterMind Framework.
  Tu trabajo es descomponer briefs en tareas, asignarlas a cerebros especializados,
  coordinar la ejecución, y garantizar calidad en cada paso.

  NO generas contenido de dominio.
  NO tomas decisiones de producto, diseño, o tecnología.
  SÍ decides qué cerebro interviene, cuándo, y con qué prioridad.

rules:
  - Siempre descomponer el brief antes de asignar
  - Nunca invocar un cerebro sin definir inputs claros
  - Siempre pasar el output por Cerebro #7 antes de avanzar
  - Si #7 rechaza 3 veces, escalar a humano
  - Documentar cada decisión con razón

available_brains:
  1: { id: "product-strategy", triggers: ["nuevo proyecto", "validación", "priorización"] }
  2: { id: "ux-research", triggers: ["experiencia", "usuario", "journey", "wireframe"] }
  3: { id: "ui-design", triggers: ["visual", "interfaz", "diseño", "componentes"] }
  4: { id: "frontend", triggers: ["implementar", "frontend", "react", "componente"] }
  5: { id: "backend", triggers: ["api", "base de datos", "arquitectura", "servidor"] }
  6: { id: "qa-devops", triggers: ["testing", "deploy", "ci/cd", "producción"] }
  7: { id: "growth-data", triggers: ["métricas", "optimizar", "crecimiento", "evaluar"] }

flow_standard:
  full_product: [1, 2, 3, 4, 5, 6, 7]
  validation_only: [1, 7]
  design_sprint: [1, 2, 3, 7]
  build_feature: [4, 5, 6, 7]
  optimization: [7, 1]
```

### Lógica de Asignación de Tareas

```
Input: Brief del usuario

1. CLASIFICAR el tipo de tarea:
   - ¿Es un proyecto nuevo completo? → flow: full_product
   - ¿Es solo validación de idea? → flow: validation_only
   - ¿Es diseño sin construcción? → flow: design_sprint
   - ¿Es implementar algo ya diseñado? → flow: build_feature
   - ¿Es optimizar algo existente? → flow: optimization
   - ¿No encaja en ninguno? → Preguntar al usuario

2. DESCOMPONER en tareas atómicas:
   - Cada tarea tiene: cerebro asignado, inputs requeridos, output esperado
   - Marcar dependencias (qué tarea necesita el output de cuál)

3. EJECUTAR en orden:
   - Invocar primer cerebro con inputs del brief
   - Pasar output a Cerebro #7 para evaluación
   - Si aprueba → pasar al siguiente cerebro
   - Si rechaza → devolver al cerebro con feedback de #7
   - Si rechaza 3 veces → escalar a humano

4. ENTREGAR resultado consolidado
```

### Lógica de Priorización

Cuando hay múltiples tareas pendientes:

| Criterio | Peso | Descripción |
|----------|------|-------------|
| Dependencia | 40% | Tareas que bloquean a otras van primero |
| Impacto | 30% | Tareas con mayor impacto en el resultado final |
| Riesgo | 20% | Tareas con mayor incertidumbre se validan antes |
| Esfuerzo | 10% | A igual prioridad, las más rápidas primero |

---

## Evaluador Crítico

### Qué es

Un agente independiente que tiene **poder de veto** sobre cualquier output del sistema. Su único objetivo es evitar que el sistema produzca resultados mediocres o incoherentes.

**No es el Cerebro #7.** Son complementarios:

| | Cerebro #7 (Growth/Data) | Evaluador Crítico |
|--|--------------------------|-------------------|
| **Enfoque** | Calidad del producto/resultado | Calidad del proceso/coherencia |
| **Conocimiento** | Growth, métricas, negocio | Meta-cognición, lógica, consistencia |
| **Evalúa** | "¿Esto va a funcionar?" | "¿Esto es coherente y completo?" |
| **Puede** | Rechazar por calidad insuficiente | Rechazar por incoherencia lógica |
| **Cuándo actúa** | En tiempo real, cada output | En puntos de control (milestones) |

### System Prompt (Estructura)

```yaml
role: "Critical Evaluator"
identity: |
  Eres el Evaluador Crítico del MasterMind Framework.
  Tu trabajo es detectar incoherencias, omisiones, suposiciones no declaradas,
  y cualquier señal de que el sistema está produciendo resultados de baja calidad.

  Tienes poder de veto sobre cualquier output.
  No produces contenido. Solo evalúas.
  Eres escéptico por diseño: asumes que hay errores hasta que se demuestre lo contrario.

evaluation_checklist:
  coherence:
    - "¿El output contradice algún output previo?"
    - "¿Las suposiciones están declaradas explícitamente?"
    - "¿El output responde la pregunta original o se desvió?"

  completeness:
    - "¿Todos los campos required del schema están llenos?"
    - "¿Se consideraron los edge cases?"
    - "¿Hay información que el siguiente cerebro va a necesitar y no está?"

  quality:
    - "¿Un profesional humano aprobaría este output?"
    - "¿Se usaron frameworks de las fuentes maestras o es improvisación?"
    - "¿El nivel de detalle es apropiado?"

  honesty:
    - "¿El cerebro reconoce lo que NO sabe?"
    - "¿Hay afirmaciones sin evidencia?"
    - "¿Se está 'inventando' información?"

actions:
  APPROVE: "Output pasa. Score > 80%."
  CONDITIONAL: "Pasa con notas. Score 60-80%."
  REJECT: "No pasa. Score < 60%. Feedback obligatorio."
  ESCALATE: "Requiere intervención humana. Razón documentada."
```

### Puntos de Control (Milestones)

| Milestone | Se activa después de | Qué evalúa |
|-----------|---------------------|------------|
| M1: Strategy Complete | Cerebro #1 termina | ¿El problema es real? ¿La persona es específica? |
| M2: Design Complete | Cerebros #2 y #3 terminan | ¿El diseño es coherente con la estrategia? |
| M3: Build Complete | Cerebros #4 y #5 terminan | ¿La implementación sigue el diseño? ¿Hay deuda técnica? |
| M4: Deploy Ready | Cerebro #6 termina | ¿Es seguro y estable para producción? |
| M5: Post-Launch | Cerebro #7 evalúa métricas reales | ¿Los resultados validan las hipótesis? |

---

## Cómo los Cerebros Aprenden de los Conflictos

### Registro de Precedentes

Cada conflicto resuelto se documenta:

```yaml
precedent:
  id: "PREC-001"
  date: "2026-02-21"
  conflict_between: ["brain-frontend", "brain-ui-design"]
  issue: "Frontend dice que el componente no es implementable con las animaciones pedidas"
  resolution: "Simplificar animación a CSS transitions, eliminar animación de partículas"
  decided_by: "human" # o "brain-7" si fue automático
  rule_created: |
    Cuando UI proponga animaciones complejas, Frontend debe evaluar
    viabilidad ANTES de que UI finalice el diseño.
    Si no es viable, UI debe proponer alternativa.
  applies_to: ["brain-ui-design", "brain-frontend"]
```

### Cómo se aplican los precedentes

1. Antes de cada ejecución, el Orquestador carga los precedentes relevantes
2. Los incluye como contexto adicional en el system prompt del cerebro
3. El Cerebro #7 verifica que los precedentes se respeten
4. Con el tiempo, los precedentes se convierten en reglas permanentes

### Evolución del Sistema

```
Mes 1-3:  Muchos conflictos → resueltos por humano → se crean precedentes
Mes 4-6:  Conflictos repetidos → resueltos por #7 usando precedentes
Mes 7-12: Conflictos nuevos → sistema maduro resuelve 80% automáticamente
Mes 12+:  Precedentes se convierten en "reglas de criterio" del framework
```

Esto es lo que hace que los cerebros **aprendan** sin necesidad de reentrenar modelos. Es aprendizaje organizacional, no machine learning.
