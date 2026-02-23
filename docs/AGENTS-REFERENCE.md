# MasterMind Framework - Agentes Reference

Guía de referencia para todos los agentes del MasterMind Framework.

---

## Arquitectura de Agentes

```
agents/
├── orchestrator/
│   ├── system-prompt.md         # Orquestador Central
│   └── flow-definitions.yaml    # Flujos disponibles
├── evaluator/
│   ├── system-prompt.md         # Cerebro #7: Growth + Evaluación
│   └── evaluation-checklist.yaml # Criterios de evaluación
└── brains/
    ├── product-strategy.md      # Cerebro #1: Product Strategy
    ├── ux-research.md           # Cerebro #2 (futuro)
    ├── ui-design.md             # Cerebro #3 (futuro)
    ├── frontend.md              # Cerebro #4 (futuro)
    ├── backend.md               # Cerebro #5 (futuro)
    ├── qa-devops.md             # Cerebro #6 (futuro)
    └── growth-data.md           # Cerebro #7 (mismo que evaluator)
```

---

## 1. Orquestador Central

**Archivo:** `agents/orchestrator/system-prompt.md`

**Rol:** Meta-cerebro coordinador que recibe briefs del usuario y orquesta los cerebros especializados.

**Responsabilidades:**
- Parsear el input del usuario en structured format
- Clasificar el tipo de tarea requerida
- Seleccionar qué cerebros involucrar
- Orquestar la ejecución en orden correcto
- Consolidar outputs en deliverable accionable

**Cerebros Disponibles (MVP):**
| # | Cerebro | Experties |
|---|---------|-----------|
| 1 | Product Strategy | Define QUÉ y POR QUÉ construir |
| 7 | Growth & Data | Métricas, evaluación, optimización |

**Flujos Disponibles:**
| Flujo | Cerebros | Descripción |
|-------|----------|-------------|
| `full_product` | 1→2→3→4→5→6→7 | Desarrollo completo de producto |
| `validation_only` | 1→7 | Validación rápida de idea |
| `product_strategy` | 1 | Estrategia solamente |

**Output Format:**
```json
{
  "orchestrator": "central",
  "task_id": "UUID",
  "brief_summary": "one sentence",
  "selected_flow": "flow_name",
  "brains_involved": ["brain-1", "brain-7"],
  "status": "in_progress|completed|blocked",
  "outputs": {...}
}
```

---

## 2. Cerebro #7: Growth & Data + Real-time Evaluator

**Archivo:** `agents/evaluator/system-prompt.md`

**Rol:** Meta-cerebro evolutivo que combina Data Science, Growth Hacking y Evaluación de Calidad. Es el ÚNICO cerebro que ve TODOS los outputs del sistema.

**Responsabilidades:**

### 2.1 Evaluador (Tiempo Real)
- Evalúa outputs de todos los demás cerebros
- Tiene poder de VETO sobre cualquier output
- Puede: APPROVE, REJECT, o REQUEST REVISION

**Criterios de Evaluación:**
- Completitud: ¿Responde al brief?
- Calidad: ¿Es accionable? ¿Específico? ¿Basado en evidencia?
- Consistencia: ¿Hay contradicciones?
- Riesgo: ¿Qué podría salir mal?

### 2.2 Growth (Optimización)
- Busca oportunidades de optimización
- Identifica feedback loops a fortalecer
- Detecta patrones que llevan al éxito

### 2.3 Data (Learning)
- Acumula qué briefs llevan a outcomes exitosos
- Rastrea qué combinaciones de cerebros funcionan mejor
- Identifica patrones de falla comunes

**Regla Crítica:** Después de 3 rechazos del mismo output → ESCALAR a humano.

**Output Format:**
```json
{
  "evaluator": "brain-7",
  "evaluation": "approve|reject|request_revision",
  "confidence": 0.0-1.0,
  "criteria_met": ["criterion1", "criterion2"],
  "criteria_missing": ["criterion3"],
  "feedback": "specific constructive feedback",
  "metrics_to_track": ["metric1", "metric2"]
}
```

---

## 3. Cerebro #1: Product Strategy

**Archivo:** `agents/brains/product-strategy.md`

**Rol:** Define QUÉ construir y POR QUÉ. Si falla, todo el proyecto nace mal.

**Conocimiento Destilado de Expertos:**
| Experto | Contribución |
|---------|--------------|
| Marty Cagan | Product discovery, equipos empoderados, 4 riesgos |
| Teresa Torres | Opportunity Solution Tree, Continuous Discovery |
| Melissa Perri | Outcomes over outputs, Product Kata |
| Eric Ries | Build-Measure-Learn, MVP, Pivot |
| John Doerr | OKRs (Objectives and Key Results) |
| Donella Meadows | Thinking in Systems, pensamiento sistémico |

**Frameworks Principales:**
- **4 Discovery Risks** (Cagan): Value, Usability, Feasibility, Viability
- **Opportunity Solution Tree** (Torres): Outcome → Opportunities → Solutions
- **Product Kata** (Perri): Vision → Current State → Obstacle → Experiment
- **Build-Measure-Learn** (Ries): MVP → Measure → Pivot
- **OKRs** (Doerr): Objectives + Key Results

**Responsabilidades:**
- Definir problema validado con evidencia
- Definir persona objetivo
- Proponer value proposition clara
- Definir métricas de éxito (OKRs)
- Priorizar features (RICE/MoSCoW)
- Identificar los 4 riesgos de discovery
- Recomendar: BUILD, DON'T BUILD, o PIVOT

**Output Format:**
```json
{
  "brain": "product-strategy",
  "task_id": "UUID",
  "validated_problem": {
    "statement": "clear problem statement",
    "evidence": ["source1", "source2"]
  },
  "target_persona": {
    "name": "persona name",
    "needs": ["need1", "need2"],
    "pains": ["pain1", "pain2"]
  },
  "value_proposition": "one clear sentence",
  "success_metrics": [
    {"metric": "name", "target": "value", "timeline": "date"}
  ],
  "prioritized_features": [
    {"feature": "name", "rice_score": 100, "rationale": "why"}
  ],
  "risks": [
    {"type": "value|usability|feasibility|viability", "risk": "description", "mitigation": "plan"}
  ],
  "recommendation": "BUILD|DON'T BUILD|PIVOT",
  "confidence": 0.0-1.0
}
```

---

## YAML Configs

### flow-definitions.yaml

Define los flujos disponibles para orquestación.

```yaml
flows:
  full_product:
    name: "Complete Product Development"
    brains: [1, 2, 3, 4, 5, 6, 7]
    description: "From idea to deployed product"

  validation_only:
    name: "Quick Validation"
    brains: [1, 7]
    description: "Validate idea without building"

  product_strategy:
    name: "Product Strategy Only"
    brains: [1]
    description: "Define strategy, defer execution"
```

### evaluation-checklist.yaml

Define los criterios de evaluación del Cerebro #7.

```yaml
criteria:
  brief_addressed:
    description: "Output directly addresses the brief"
    weight: critical

  evidence_provided:
    description: "Claims are supported by evidence"
    weight: high

  actionability:
    description: "Next steps are specific and actionable"
    weight: high

  specificity:
    description: "Output is specific, not generic"
    weight: medium

  risk_acknowledged:
    description: "Risks and limitations are acknowledged"
    weight: medium

  metrics_defined:
    description: "Success metrics are proposed where applicable"
    weight: low

escalation:
  max_rejections: 3
  action: "escalate_to_human"
```

---

## Reglas de Uso

1. **Idioma:** Los system prompts están en inglés (mejor performance con LLMs) pero responden en el idioma del input del usuario.

2. **Output Dual:** JSON para procesamiento automático + Markdown para humanos.

3. **Evaluador como Filtro:** Todo output pasa por #7. Si rechaza 3 veces, escala a humano.

4. **Orquestador Minimal:** Para MVP, solo coordina #1 y #7. Los demás cerebros se agregan en fases futuras.

---

## Próximos Cerebros (Futuro)

| # | Cerebro | Estado |
|---|---------|--------|
| 2 | UX Research | Pendiente |
| 3 | UI Design | Pendiente |
| 4 | Frontend | Pendiente |
| 5 | Backend | Pendiente |
| 6 | QA/DevOps | Pendiente |

---

## Referencias

- **PRD Principal:** `docs/design/00-PRD-MasterMind-Framework.md`
- **Orquestador Specs:** `docs/design/07-Orquestador-y-Evaluador.md`
- **Cerebro #1 Specs:** `docs/design/05-Cerebro-01-Product-Strategy.md`
- **Cerebro #7 Specs:** `docs/design/06-Cerebros-02-a-07-Specs.md`
