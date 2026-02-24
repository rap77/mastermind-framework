# PRP-006: Orchestrator Implementation

**Status:** In Progress
**Priority:** High
**Estimated:** 2-3 hours
**Dependencies:** PRP-003 (System Prompts), PRP-004 (NotebookLM), PRP-005 (Brain #7)

---

## Overview

Implementar el **Orquestador Central** — el sistema nervioso del MasterMind Framework que coordina la ejecución entre cerebros especializados, maneja flujos de trabajo, evalúa outputs via Cerebro #7, y gestiona precedentes de conflictos resueltos.

## Specification Reference

- `docs/design/07-Orquestador-y-Evaluador.md`

---

## Objectives

### Primary
1. **System Prompt del Orquestador** — Definir comportamiento operacional
2. **Configuración de Flujos** — Definir flujos estándar (full_product, validation_only, etc.)
3. **Lógica de Clasificación** — Descomponer briefs en tareas atómicas
4. **Protocolo de Evaluación** — Iteración con Cerebro #7 (max 3 rechazos → escala)
5. **Sistema de Precedentes** — Registro y aplicación de conflictos resueltos

### Secondary (Optional for PRP-006)
6. CLI command `mm orchestrate <brief>` (puede ser PRP-008)
7. Testing completo con briefs reales

---

## Implementation Plan

### Phase 1: Structure & Configuration (45 min)

#### 1.1 Directorios
```
agents/orchestrator/
├── system-prompt.md           # System prompt principal
├── config/
│   ├── flows.yaml            # Flujos estándar (full_product, etc.)
│   ├── brains.yaml           # Definición de 7 cerebros + triggers
│   └── thresholds.yaml       # Umbrales (rejections, escalation)
├── protocols/
│   ├── task-decomposition.md # Cómo descomponer briefs
│   ├── evaluation-flow.md    # Cómo iterar con Cerebro #7
│   └── escalation.md         # Cuándo escalar a humano
└── precedents/
    ├── template.yaml         # Template de precedente
    └── catalog.yaml          # Catálogo de precedentes (vacío inicialmente)
```

#### 1.2 Archivos a crear

**flows.yaml** — Flujos estándar
```yaml
flows:
  full_product:
    sequence: [1, 2, 3, 4, 5, 6, 7]
    description: "Producto completo desde idea hasta deploy"
    triggers: ["nuevo proyecto", "app completa", "producto desde cero"]

  validation_only:
    sequence: [1, 7]
    description: "Validación de idea sin implementación"
    triggers: ["validar idea", "feedback concepto", "viabilidad"]

  design_sprint:
    sequence: [1, 2, 3, 7]
    description: "Diseño UX/UI sin construcción"
    triggers: ["diseñar", "prototipar", "wireframe", "mockup"]

  build_feature:
    sequence: [4, 5, 6, 7]
    description: "Implementar feature ya diseñada"
    triggers: ["implementar", "construir", "codificar", "feature"]

  optimization:
    sequence: [7, 1]
    description: "Optimizar producto existente"
    triggers: ["optimizar", "mejorar", "crecimiento", "métricas"]
```

**brains.yaml** — Definición de cerebros
```yaml
brains:
  1:
    id: "product-strategy"
    name: "Product Strategy"
    system_prompt: "agents/brains/product-strategy.md"
    notebook: "f276ccb3-0bce-4069-8b55-eae8693dbe75"
    triggers:
      - "nuevo proyecto"
      - "validación"
      - "priorización"
      - "idea"
      - "concepto"
    output_schema: "product-brief"

  2:
    id: "ux-research"
    name: "UX Research"
    status: "pending"  # No implementado aún
    triggers:
      - "experiencia"
      - "usuario"
      - "journey"
      - "wireframe"
    output_schema: "ux-research-report"

  # ... 3-6 pending ...

  7:
    id: "growth-data"
    name: "Growth & Data (Critical Evaluator)"
    system_prompt: "agents/brains/growth-data.md"
    evaluator_skill: "skills/evaluator/SKILL.md"
    triggers:
      - "métricas"
      - "optimizar"
      - "crecimiento"
      - "evaluar"
    output_schema: "evaluation-report"
```

**thresholds.yaml** — Umbrales de decisión
```yaml
evaluation:
  max_rejections: 3
  rejection_count_reset: "per_brain_output"
  escalation_triggers:
    - "3 consecutive rejections by brain #7"
    - "coherence failure detected"
    - "human requested explicitly"

precedents:
  max_catalog_size: 100
  relevance_threshold: 0.7
  auto_apply: true
```

### Phase 2: System Prompt (45 min)

**system-prompt.md** — System prompt del Orquestador
- Rol: "Orchestrator" — coordinador, no generador de contenido
- Identidad: Sistema nervioso central del framework
- Reglas:
  - Siempre descomponer antes de asignar
  - Nunca invocar cerebro sin inputs claros
  - Siempre pasar output por Cerebro #7
  - 3 rechazos → escalar a humano
  - Documentar cada decisión
- 7 cerebros disponibles con sus triggers
- Flujos estándar predefinidos
- Lógica de clasificación de tareas
- Protocolo de iteración con Cerebro #7

### Phase 3: Task Decomposition Protocol (30 min)

**task-decomposition.md** — Cómo descomponer briefs
```
Input: Brief del usuario (texto libre)

Proceso:
1. CLASIFICAR tipo de tarea (flow_detection)
2. DESCOMPONER en tareas atómicas (atomic_tasks)
3. ASIGNAR cerebros (brain_assignment)
4. DEFINIR dependencias (dependency_graph)
5. EJECUTAR en orden (sequential_execution)

Output: Execution plan con:
- task_id único
- brain_id asignado
- inputs requeridos
- output esperado
- dependencies (task_ids)
- priority score
```

### Phase 4: Evaluation Flow Protocol (30 min)

**evaluation-flow.md** — Cómo iterar con Cerebro #7
```
Para cada output de cerebro (1-6):

1. ENVIAR output a Cerebro #7 para evaluación
2. RECIBIR veredicto: APPROVE | CONDITIONAL | REJECT | ESCALATE
3. ACTUAR según veredicto:
   - APPROVE: Continuar al siguiente cerebro
   - CONDITIONAL: Aplicar notas, continuar o re-trabajar
   - REJECT: Devolver al cerebro con feedback, incrementar counter
   - ESCALATE: Notificar humano, pausar ejecución

4. TRACKEAR rejection counter por (brain_id, task_id)
5. SI rejection_counter >= 3: ESCALAR automáticamente

Output:
- evaluation_report con veredicto, score, feedback
- precedents creados si se resolvió conflicto
```

### Phase 5: Precedents System (30 min)

**template.yaml** — Template de precedente
```yaml
precedent:
  id: "PREC-XXX"
  date: "YYYY-MM-DD"
  conflict_between: ["brain-X", "brain-Y"]
  issue: "Descripción del conflicto"
  resolution: "Cómo se resolvió"
  decided_by: "human" | "brain-7"
  rule_created: |
    Regla derivada del precedente.
    Se aplicará en futuros contextos similares.
  applies_to: ["brain-X", "brain-Y"]
  context_tags: ["frontend", "animations", "viability"]
```

**catalog.yaml** — Catálogo de precedentes
```yaml
precedents: []
version: "1.0.0"
last_updated: "YYYY-MM-DD"
```

### Phase 6: Documentation (30 min)

Crear guía de uso del Orquestador:
- `docs/ORCHESTRATOR-GUIDE.md`
- Cómo invocar al Orquestador (manual o CLI)
- Formato de briefs de entrada
- Formato de outputs (execution plan, evaluation reports)
- Cómo se gestionan precedentes

---

## Files to Create

| Archivo | Path | Purpose |
|---------|------|---------|
| System prompt | `agents/orchestrator/system-prompt.md` | Comportamiento del Orquestador |
| Flows config | `agents/orchestrator/config/flows.yaml` | Flujos estándar |
| Brains config | `agents/orchestrator/config/brains.yaml` | 7 cerebros + triggers |
| Thresholds | `agents/orchestrator/config/thresholds.yaml` | Umbrales de decisión |
| Task decomp | `agents/orchestrator/protocols/task-decomposition.md` | Cómo descomponer briefs |
| Eval flow | `agents/orchestrator/protocols/evaluation-flow.md` | Iteración con Cerebro #7 |
| Escalation | `agents/orchestrator/protocols/escalation.md` | Cuándo escalar |
| Precedent tpl | `agents/orchestrator/precedents/template.yaml` | Template |
| Precedent cat | `agents/orchestrator/precedents/catalog.yaml` | Catálogo (vacío) |
| Guide | `docs/ORCHESTRATOR-GUIDE.md` | Guía de uso |

---

## Success Criteria

- [ ] System prompt del Orquestador creado (400+ líneas)
- [ ] 5 flujos estándar definidos (flows.yaml)
- [ ] 7 cerebros definidos con triggers (brains.yaml)
- [ ] Umbrales de decisión configurados (thresholds.yaml)
- [ ] Protocolo de evaluación documentado (evaluation-flow.md)
- [ ] Sistema de precedentes implementado (template + catalog)
- [ ] Guía de usuario creada (ORCHESTRATOR-GUIDE.md)
- [ ] YAML validado sin errores
- [ ] Git commit con conventional commits

---

## Out of Scope (PRP-007 / PRP-008)

- CLI command `mm orchestrate <brief>`
- Testing con briefs reales
- Integración automática con NotebookLM para cerebros 2-6
- Sistema de tracking de ejecución (logs, dashboards)
- Sistema de aprendizaje automático de precedentes

---

## Notes

- El Orquestador NO tiene conocimiento de dominio
- Solo decide QUÉ cerebro interviene, CUÁNDO, y con QUÉ inputs
- Cerebro #7 ya está implementado (PRP-005)
- Los cerebros 2-6 están pending, pero el Orquestador ya debe conocerlos
- Los precedentes inicialmente estarán vacíos, se llenarán con uso

---

## References

- `docs/design/07-Orquestador-y-Evaluador.md`
- `docs/design/00-PRD-MasterMind-Framework.md`
- `PRPs/PRP-005-brain-07-evaluator.md`
- `skills/evaluator/SKILL.md`
