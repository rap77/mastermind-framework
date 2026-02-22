# Plantilla Estándar de Cerebro — MasterMind Framework

Esta plantilla define la estructura que debe seguir **cada cerebro** del framework. Es la receta para replicar el modelo a cualquier nicho.

---

## Estructura de Archivos por Cerebro

```
docs/{nicho}/{##-nombre-brain}/
├── README.md                    ← Índice del cerebro
├── brain-spec.yaml              ← Definición formal (5 capas, I/O, autoridad)
├── knowledge-map.md             ← Habilidades → Expertos → Fuentes
├── experts-directory.md         ← Fichas biográficas de expertos
├── master-sources.md            ← Índice de fuentes maestras
├── sources/                     ← Carpeta de fichas individuales
│   ├── FUENTE-001-titulo.md
│   ├── FUENTE-002-titulo.md
│   └── ...
├── use-cases.md                 ← Escenarios de activación
├── evaluation-criteria.md       ← Métricas de calidad del output
└── notebook-config.json         ← Mapeo técnico a NotebookLM
```

---

## Plantilla: README.md

```markdown
# Cerebro #{número} — {Nombre}

**Nicho:** {Desarrollo de Software | Marketing Digital | etc.}
**Nombre NotebookLM:** [CEREBRO] {Nombre} — {Nicho}
**Versión:** 1.0
**Última actualización:** {fecha}

## Rol en el Flujo

{Una oración clara de qué hace este cerebro y por qué es crítico.}

## Pregunta Central

> ¿{La pregunta fundamental que este cerebro responde}?

## Dependencias

- **Recibe input de:** Cerebro #{n} ({nombre})
- **Entrega output a:** Cerebro #{n} ({nombre})
- **Evaluado por:** Cerebro #7 (Growth & Data) en tiempo real

## Escenarios de Activación

El Orquestador invoca este cerebro cuando:

1. {Escenario 1}
2. {Escenario 2}
3. {Escenario 3}

## Estado del Conocimiento

| Métrica | Valor |
|---------|-------|
| Expertos registrados | {n} |
| Fuentes maestras cargadas | {n} |
| Habilidades cubiertas | {n}/{total} |
| Gaps identificados | {lista o "Ninguno"} |
```

---

## Plantilla: brain-spec.yaml

```yaml
brain:
  id: "brain-{nicho}-{numero}-{nombre}"
  name: "{Nombre del Cerebro}"
  niche: "{nicho}"
  order_in_flow: {numero}
  version: "1.0"

role:
  description: "{Descripción del rol en una oración}"
  central_question: "{La pregunta que responde}"

  # Esto es lo que separa un experto de un asistente
  can_reject: true
  can_request_info: true
  can_detect_incoherence: true
  can_say_no: true

five_layers:
  1_conceptual_base:
    description: "Principios fundamentales del dominio"
    content:
      - "{Principio 1}"
      - "{Principio 2}"
      - "{Principio 3}"

  2_operational_frameworks:
    description: "Métodos y herramientas prácticas"
    content:
      - "{Framework 1}"
      - "{Framework 2}"

  3_mental_models:
    description: "Formas de pensar y analizar"
    content:
      - "{Modelo 1}"
      - "{Modelo 2}"

  4_decision_criteria:
    description: "Cómo resolver trade-offs profesionales"
    content:
      - "{Trade-off 1: A vs B}"
      - "{Trade-off 2: C vs D}"

  5_feedback_mechanism:
    description: "Cómo mide y mejora su desempeño"
    metrics:
      - "{Métrica 1}"
      - "{Métrica 2}"

inputs:
  required:
    - field: "{nombre_campo}"
      type: "{string | object | array}"
      description: "{Qué es y por qué se necesita}"
  optional:
    - field: "{nombre_campo}"
      description: "{Para qué sirve}"

outputs:
  required:
    - field: "{nombre_campo}"
      type: "{tipo}"
      description: "{Qué contiene}"
  format: "markdown | yaml | json"

authority:
  can_reject_from: ["{brain_id}"]
  cannot_reject_from: ["{brain_id}"]
  veto_power_over: "{área específica}"

evaluation:
  evaluated_by: "brain-growth-data-007"
  criteria:
    - "{Criterio 1}"
    - "{Criterio 2}"
  max_iterations: 3
  escalation_on_failure: "orchestrator → human"

notebook:
  notebook_id: "{id del cuaderno NotebookLM}"
  source_count: {n}
  last_sync: "{fecha}"
```

---

## Plantilla: knowledge-map.md

```markdown
# Mapa de Conocimiento — Cerebro #{número} {Nombre}

## Habilidades Requeridas (sin GAP)

| # | Habilidad | Nivel Requerido | Experto(s) Asignado(s) | Fuente(s) Maestra(s) | Estado |
|---|-----------|----------------|----------------------|---------------------|--------|
| H1 | {Habilidad} | Experto | {Nombre} | FUENTE-001 | ✅ Cubierta |
| H2 | {Habilidad} | Avanzado | {Nombre} | FUENTE-002, FUENTE-003 | ✅ Cubierta |
| H3 | {Habilidad} | Experto | — | — | ❌ GAP |

## Análisis de Gaps

### Gaps Identificados

| Habilidad | Razón del Gap | Plan de Cierre | Prioridad |
|-----------|--------------|----------------|-----------|
| {Habilidad} | {No se encontró experto adecuado / Fuente no disponible} | {Acción} | Alta |

### Habilidades Transversales (necesita entender de otros cerebros)

- Debe entender: {área del Cerebro X}
- Debe entender: {área del Cerebro Y}
- Razón: {por qué es necesario para no tener gap}
```

---

## Plantilla: experts-directory.md

```markdown
# Directorio de Expertos — Cerebro #{número} {Nombre}

## Criterios de Selección Aplicados

Ver documento completo: `02-Metodo-Seleccion-Expertos.md`

Resumen: Cada experto fue seleccionado cumpliendo mínimo 4 de 6 criterios obligatorios.

---

## EXP-001: {Nombre Completo}

**Especialidad:** {Área principal}
**Relevancia para este cerebro:** {Qué habilidades cubre}
**Credenciales:**
- {Cargo, empresa, logro}
- {Publicaciones, conferencias}
- {Años de experiencia, clientes notables}

**Justificación de selección:**
{Por qué esta persona y no otra. Qué aporta que es único.}

**Fuentes maestras asociadas:**
- FUENTE-001: {Título del libro}
- FUENTE-002: {Título del video/curso}

**Cuándo usar este experto:**
- Cuando se necesite: {situación 1}
- Cuando se necesite: {situación 2}

**Cuándo NO usar este experto:**
- {Limitación 1}
- {Limitación 2}

---

## EXP-002: {Siguiente experto...}
```

---

## Plantilla: evaluation-criteria.md

```markdown
# Criterios de Evaluación — Cerebro #{número} {Nombre}

## Evaluación por el Cerebro #7 (en tiempo real)

Cada output de este cerebro es evaluado automáticamente contra:

| Criterio | Peso | Descripción | Aprueba si... |
|----------|------|-------------|---------------|
| Coherencia | 25% | ¿Es consistente con inputs? | No contradice información recibida |
| Completitud | 25% | ¿Cubre todos los aspectos? | Todos los campos required están llenos |
| Calidad profesional | 25% | ¿Un experto humano lo aprobaría? | Sigue frameworks de las fuentes maestras |
| Viabilidad | 15% | ¿Es implementable? | Considera recursos y restricciones reales |
| Alineación | 10% | ¿Contribuye al objetivo? | Responde la pregunta central del brief |

## Reglas de Iteración

- **Score < 60%:** Rechazo automático con feedback detallado
- **Score 60-80%:** Aprobación condicional, sugerencias de mejora
- **Score > 80%:** Aprobación completa
- **Máximo 3 iteraciones** antes de escalamiento humano

## Señales de Alerta (Red Flags)

El Cerebro #7 escala inmediatamente si detecta:

1. Output contradice outputs previos de otros cerebros
2. Se hacen suposiciones no declaradas
3. Se omiten dependencias críticas
4. El nivel de detalle es insuficiente para el siguiente cerebro
5. Se detecta "alucinación" (información sin respaldo en fuentes maestras)
```
