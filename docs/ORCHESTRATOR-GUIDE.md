# Orchestrator Guide

**MasterMind Framework** — Guía de uso del Orquestador Central

---

## Overview

El **Orquestador Central** es el sistema nervioso del MasterMind Framework. No genera contenido de dominio, sino que coordina los cerebros especializados para producir resultados de calidad.

**Lo que hace:**
- Descompone briefs del usuario en tareas atómicas
- Asigna tareas a los cerebros apropiados
- Coordina la ejecución en el orden correcto
- Garantiza calidad mediante Cerebro #7
- Gestiona precedentes de conflictos resueltos

**Lo que NO hace:**
- No genera estrategia de producto (Cerebro #1)
- No diseña UX/UI (Cerebros #2-3)
- No escribe código (Cerebros #4-5)
- No hace QA/Deploy (Cerebro #6)

---

## Estructura de Archivos

```
agents/orchestrator/
├── system-prompt.md           # System prompt del Orquestador
├── config/
│   ├── flows.yaml            # Flujos estándar (full_product, etc.)
│   ├── brains.yaml           # Definición de 7 cerebros + triggers
│   └── thresholds.yaml       # Umbrales (rejections, escalation)
├── protocols/
│   ├── task-decomposition.md # Cómo descomponer briefs
│   ├── evaluation-flow.md    # Iteración con Cerebro #7
│   └── escalation.md         # Cuándo escalar a humano
└── precedents/
    ├── template.yaml         # Template de precedente
    └── catalog.yaml          # Catálogo de precedentes
```

---

## Los 7 Cerebros

| # | ID | Nombre | Estado | Triggers |
|---|----|----|--------|----------|
| 1 | `product-strategy` | Product Strategy | ✅ Activo | nuevo proyecto, idea, concepto |
| 2 | `ux-research` | UX Research | ⏳ Pendiente | experiencia, usuario, journey |
| 3 | `ui-design` | UI Design | ⏳ Pendiente | visual, interfaz, diseño |
| 4 | `frontend` | Frontend Dev | ⏳ Pendiente | implementar, react, componente |
| 5 | `backend` | Backend Dev | ⏳ Pendiente | api, base de datos, arquitectura |
| 6 | `qa-devops` | QA & DevOps | ⏳ Pendiente | testing, deploy, ci/cd |
| 7 | `growth-data` | Growth & Data | ✅ Activo | métricas, optimizar, evaluar |

**Nota:** Solo Cerebros #1 y #7 están implementados. Los demás están definidos para futura implementación.

---

## Flujos Estándar

### `full_product` — Producto Completo
```
Brief → [1] → [7] → [2] → [7] → [3] → [7] → [4] → [7] → [5] → [7] → [6] → [7] → Resultado
```
Para: Nuevo producto completo desde idea hasta producción.

### `validation_only` — Validación de Idea
```
Brief → [1] → [7] → Resultado
```
Para: Validar idea sin implementar.

### `design_sprint` — Diseño Sin Construcción
```
Brief → [1] → [7] → [2] → [7] → [3] → [7] → Resultado
```
Para: Diseño UX/UI completo.

### `build_feature` — Implementar Feature
```
Brief → [4] → [7] → [5] → [7] → [6] → [7] → Resultado
```
Para: Implementar feature ya diseñada.

### `optimization` — Optimizar Producto
```
Brief + métricas → [7] → [1] → Resultado
```
Para: Optimizar basado en métricas.

---

## Cómo Usar el Orquestador

### Opción 1: Manual (Actual)

1. **Leer el brief del usuario**
2. **Clasificar el tipo de trabajo** → seleccionar flujo
3. **Crear execution plan** con tareas atómicas
4. **Ejecutar tareas secuencialmente**:
   - Invocar cerebro con inputs claros
   - Enviar output a Cerebro #7
   - Manejar veredicto (APPROVE/CONDITIONAL/REJECT/ESCALATE)
   - Continuar o re-trabajar según veredicto
5. **Entregar resultado consolidado**

### Opción 2: CLI Command (Futuro - PRP-008)

```bash
# Ejecutar orquestador con brief
mm orchestrate "Quiero crear una app para encontrar compañeros de viaje"

# Especificar flujo explícitamente
mm orchestrate "Validar idea de app de viajes" --flow validation_only

# Usar archivo de brief
mm orchestrate --file brief.md
```

---

## Formato de Briefs

### Brief Mínimo

```
"Quiero crear una app para encontrar compañeros de viaje en Chile"
```

### Brief Estructurado (Recomendado)

```yaml
brief:
  idea: "App para encontrar compañeros de viaje en Chile"
  target: "Viajeros solitarios que quieren compañía"
  key_features:
    - "Match por ruta y fechas"
    - "Perfil con intereses"
    - "Chat integrado"
  constraints:
    - "MVP, lean startup"
    - "Mercado chileno"
  timeline: "3-6 meses para MVP"
```

---

## Output del Orquestador

### Execution Plan (Después de Descomposición)

```yaml
execution_plan:
  plan_id: "PLAN-001"
  flow_type: "full_product"
  brief: "App para encontrar compañeros de viaje"
  tasks:
    - task_id: "TASK-001"
      brain_id: 1
      title: "Definir estrategia de producto"
      dependencies: []
      priority: 10
    - task_id: "TASK-002"
      brain_id: 2
      title: "Investigación UX"
      dependencies: ["TASK-001"]
      priority: 9
  estimated_duration: "3-4 hours"
```

### Final Deliverable (Después de Ejecución)

```yaml
execution_report:
  plan_id: "PLAN-001"
  status: "completed"
  tasks_completed: 7
  tasks_total: 7
  outputs:
    TASK-001: "product-brief-001.yaml"
    TASK-002: "ux-research-001.yaml"
    # ...
  evaluations:
    TASK-001:
      veredict: "APPROVE"
      score: 87
    TASK-002:
      veredict: "CONDITIONAL"
      score: 72
      notes: "Agregar más detalle en persona"
  final_deliverable: |
    # Resumen consolidado para el usuario
    ...
```

---

## Protocolo de Evaluación (Cerebro #7)

### Veredictos Posibles

| Veredicto | Score | Acción |
|-----------|-------|--------|
| **APPROVE** | ≥80 | Continuar al siguiente cerebro |
| **CONDITIONAL** | 60-79 | Aplicar notas y continuar/re-trabajar |
| **REJECT** | <60 | Devolver al cerebro con feedback |
| **ESCALATE** | - | Escalar a humano |

### Regla de 3 Rechazos

```
1er rechazo → Devolver con feedback, contador = 1
2do rechazo → Devolver con feedback + precedentes, contador = 2
3er rechazo → ESCALAR a humano inmediatamente
```

---

## Sistema de Precedentes

Los precedentes son reglas aprendidas de conflictos resueltos.

### Ejemplo de Precedente

```yaml
precedent:
  id: "PREC-001"
  date: "2026-02-24"
  issue: "Brain #1 repeatedly omits competitive analysis"
  resolution: "Human requested explicit competitive section"
  decided_by: "human"
  rule_created: "Always include competitive analysis in product briefs"
  applies_to: ["brain-1"]
  context_tags: ["product-strategy", "competition"]
  occurrences: 1
```

### Cómo se Aplican los Precedentes

1. Antes de invocar un cerebro, el Orquestador busca precedentes relevantes
2. Filtra por `applies_to` y `context_tags`
3. Incluye precedentes como contexto adicional
4. Después de la ejecución, Cerebro #7 verifica que se respetaran

---

## Escalación a Humano

### Cuándo Escalar

- 3 rechazos consecutivos del mismo output
- Fallo de coherencia (output contradice outputs previos)
- Dominio desconocido fuera de experiencia
- Issue crítico (seguridad, legal, ético)
- Timeout de cerebro sin respuesta
- Usuario lo solicita explícitamente

### Reporte de Escalación

```yaml
escalation_report:
  escalation_id: "ESC-001"
  severity: "high"
  trigger: "third_rejection"
  attempts: 3
  recommendation: "Revisar brief con usuario para claridad"
  action_required: "guidance"
```

---

## Configuración

### Umbrales de Evaluación (thresholds.yaml)

```yaml
evaluation:
  max_rejections: 3
  approval_threshold: 80
  conditional_threshold: 60
  rejection_threshold: 60
```

### Flujos Personalizables (flows.yaml)

Para agregar un nuevo flujo estándar:

```yaml
flows:
  custom_flow:
    sequence: [1, 7]
    description: "Mi flujo personalizado"
    triggers: ["trigger1", "trigger2"]
```

---

## Validación

### Validar YAMLs

```bash
# Validar flows.yaml
python3 -c "import yaml; yaml.safe_load(open('agents/orchestrator/config/flows.yaml'))"

# Validar brains.yaml
python3 -c "import yaml; yaml.safe_load(open('agents/orchestrator/config/brains.yaml'))"

# Validar thresholds.yaml
python3 -c "import yaml; yaml.safe_load(open('agents/orchestrator/config/thresholds.yaml'))"
```

### Verificar Estructura

```bash
# Listar archivos del orquestador
ls -la agents/orchestrator/

# Verificar precedents
ls -la agents/orchestrator/precedents/
```

---

## Logs y Checkpoints

### Logs de Ejecución

```
logs/execution/
├── 2026-02-24_plan-001_execution.log
├── 2026-02-24_plan-002_execution.log
└── ...
```

### Logs de Evaluaciones

```
logs/evaluations/
├── eval-001.yaml
├── eval-002.yaml
└── ...
```

### Checkpoints (para resume)

```
logs/checkpoints/
├── plan-001_checkpoint.yaml
├── plan-002_checkpoint.yaml
└── ...
```

---

## Ejemplos de Uso

### Ejemplo 1: Validación de Idea

**Input:**
```
"Es buena idea una app de walking para perros?"
```

**Orquestador:**
1. Clasifica: `validation_only`
2. Execution plan: TASK-001 (Brain #1) → TASK-002 (Brain #7)
3. Invoca Brain #1 con brief
4. Envía output a Brain #7
5. Entrega evaluation report al usuario

### Ejemplo 2: Producto Completo

**Input:**
```
"Quiero crear una marketplace freelance para desarrolladores latam"
```

**Orquestador:**
1. Clasifica: `full_product`
2. Execution plan: 7 tareas (Brains 1→2→3→4→5→6→7)
3. Ejecuta secuencialmente con evaluaciones
4. Entrega deliverable consolidado

---

## Troubleshooting

| Problema | Solución |
|----------|----------|
| Brief demasiado vague | Hacer preguntas de clarificación |
| Output no pasa evaluación | Revisar feedback de Cerebro #7 |
| 3 rechazos consecutivos | Escalar a humano |
| YAML syntax error | Validar archivos con python3 yaml |
| Precedente no se aplica | Verificar `applies_to` y `context_tags` |

---

## Referencias

- `docs/design/07-Orquestador-y-Evaluador.md` — Especificación completa
- `docs/design/00-PRD-MasterMind-Framework.md` — PRD del framework
- `PRPs/PRP-006-orchestrator.md` — PRP de implementación
- `skills/evaluator/SKILL.md` — Sistema del Cerebro #7

---

**Versión:** 1.0.0
**Última actualización:** 2026-02-24
