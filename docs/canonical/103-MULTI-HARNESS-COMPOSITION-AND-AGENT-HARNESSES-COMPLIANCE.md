# Multi-Harness Composition and Agent Harnesses Compliance

## 1. Propósito

Definir cómo MasterMind compone múltiples harnesses y skills adaptables por objetivo sin abandonar el estándar Agent Harnesses.

Este documento conecta:

- la biblioteca de harnesses de MasterMind
- el selector de harness + loop
- el runtime contract
- el Capability Registry
- el formato externo Agent Harnesses (`HARNESS.md`, routing files y leaf detectors)

## 2. Tesis central

> MasterMind no concatena prompts. MasterMind selecciona paquetes Agent Harness válidos, compone un RunBundle efímero válido y ejecuta sólo el contexto mínimo necesario.

La unidad base es un harness estándar. La ventaja de MasterMind es la composición dinámica.

## 3. Relación con canónicos existentes

Este documento extiende:

- `64-HARNESS-LIBRARY-AND-LOOP-TAXONOMY.md`
- `67-HARNESS-SELECTION-POLICY.md`
- `68-CAPABILITY-REGISTRY-SPEC.md`
- `69-CAPABILITY-REGISTRY-SCHEMA.md`
- `71-HARNESS-RUNTIME-CONTRACT.md`
- `73-HARNESS-SELECTOR-SERVICE.md`
- `90-HARNESS-ESCALATION-POLICY.md`

No reemplaza esos contratos. Añade la capa faltante: composición multi-harness y compliance con Agent Harnesses.

## 4. Modelo conceptual

```text
Objective
  -> ObjectiveProfile
  -> HarnessSelector
  -> HarnessCompositionPlan
  -> RunBundleComposer
  -> Agent Harness compliant RunBundle
  -> RunBundleStageExecutor
  -> HarnessCore execution envelope
```

## 5. Biblioteca de harnesses

La biblioteca vive conceptualmente en:

```text
.mm-flow/harness-library/
```

Estructura recomendada:

```text
.mm-flow/harness-library/
├── roles/
│   ├── product-strategist/
│   ├── ux-researcher/
│   ├── backend-architect/
│   └── qa-reviewer/
├── lifecycle/
│   ├── discovery/
│   ├── planning/
│   ├── implementation/
│   ├── verification/
│   └── archive/
├── verification/
│   ├── evidence-readiness/
│   ├── security-review/
│   └── regression-check/
├── recovery/
│   └── bounded-recovery/
├── shared-skills/
│   ├── memory-retrieval/
│   ├── codebase-scan/
│   └── notebooklm-query/
└── registry.yaml
```

## 6. Harness package estándar

Cada harness de biblioteca debe ser un paquete Agent Harness válido:

```text
product-strategist/
├── HARNESS.md
├── .leaf-detectors
├── skills/
│   ├── SKILLS.md
│   └── generate-prd/
│       └── SKILL.md
├── references/
│   └── REFERENCES.md
└── data/
    └── DATA.md
```

### 6.1 `HARNESS.md`

Debe incluir frontmatter mínimo:

```yaml
---
name: Product Strategist
description: Select this harness to turn product goals, evidence, and constraints into strategy artifacts.
---
```

El body debe ser corto y funcionar como mapa:

```md
You are the primary product strategy harness.

- `skills/` — product strategy capabilities (see SKILLS.md)
- `references/` — reusable strategy doctrine and examples (see REFERENCES.md)
- `data/` — schemas and local metadata used by this harness (see DATA.md)
```

### 6.2 `.leaf-detectors`

Todo harness con skills debe declarar:

```text
skill=SKILL.md
```

Esto evita que el loader recurse dentro de internals de skills (`scripts/`, `assets/`, `references/`).

### 6.3 Routing files

Cada directorio relevante debe tener routing file con frontmatter `description`:

```text
skills/SKILLS.md
references/REFERENCES.md
data/DATA.md
```

El routing file responde: “¿debo mirar aquí para esta tarea?”

## 7. Tipos de harness

### 7.1 Role Harness

Define identidad operativa primaria.

Ejemplos:

- Product Strategist
- UX Researcher
- Backend Architect
- QA Reviewer

Sólo un Role Harness puede ser primario por run.

### 7.2 Lifecycle Harness

Define fase de trabajo.

Ejemplos:

- Discovery
- Planning
- Implementation
- Verification
- Archive

Puede apoyar al Role Harness, pero no debe sobrescribir identidad.

### 7.3 Verification Harness

Añade checks, criterios y evidencia.

Ejemplos:

- Evidence Readiness
- Security Review
- Regression Check

### 7.4 Recovery Harness

Define retry, patch, replan, rollback o escalación.

### 7.5 Shared Skill Package

Contiene una skill atómica reutilizable por varios harnesses.

Debe seguir el formato Agent Skill:

```text
memory-retrieval/
├── SKILL.md
└── scripts/
```

### 7.6 Review Harness

Añade fresh-context o adversarial review sin sustituir verification ni approval.
Puede bloquear por findings según project policy, risk o segregation of duties.

## 8. ObjectiveProfile

El selector debe normalizar cada objetivo antes de elegir harnesses.

Campos conceptuales:

- `objective_id`
- `objective_text`
- `domain`
- `phase`
- `output_type`
- `complexity`
- `risk_level`
- `verifiability`
- `requires_write`
- `requires_fresh_context`
- `requires_memory`
- `requires_mcp`
- `requires_review`
- `requires_recovery`
- `evidence_readiness_gate`
- `evidence_readiness_score`

## 9. HarnessCompositionPlan

El selector no devuelve texto libre. Devuelve un plan estructurado.

Campos conceptuales:

- `plan_id`
- `objective_profile`
- `primary_harness`
- `supporting_harnesses`
- `selected_skills`
- `selected_references`
- `selected_loops`
- `precedence_policy`
- `context_budget`
- `validation_requirements`
- `rejected_candidates`
- `rationale`

Ejemplo:

```yaml
plan_id: run-product-discovery-001
primary_harness: roles/product-strategist
supporting_harnesses:
  - lifecycle/discovery
  - verification/evidence-readiness
  - verification/qa-review
selected_skills:
  - shared-skills/memory-retrieval
  - roles/product-strategist/skills/generate-prd
selected_references:
  - roles/product-strategist/references/strategy-doctrine.md
selected_loops:
  - goal-loop
  - verification-loop
precedence_policy:
  - project_policy
  - primary_harness
  - supporting_harnesses
  - selected_skills
  - selected_references
```

## 10. RunBundle

El composer materializa un bundle efímero por ejecución.

```text
.run-bundles/<run-id>/
├── HARNESS.md
├── .leaf-detectors
├── skills/
│   ├── SKILLS.md
│   ├── memory-retrieval -> ../../.mm-flow/harness-library/shared-skills/memory-retrieval
│   └── generate-prd -> ../../.mm-flow/harness-library/roles/product-strategist/skills/generate-prd
├── references/
│   └── REFERENCES.md
├── verification/
│   └── VERIFICATION.md
└── bundle.yaml
```

El RunBundle también debe ser un Agent Harness válido.

Cuando el harness declara stages, el bundle debe materializar además el stage
graph, policies, selected capabilities y content hash definidos en
`113-HARNESS-STAGE-EXECUTION-RUNTIME-CONTRACT.md`.

## 11. `bundle.yaml`

El bundle debe conservar lineage:

```yaml
bundle_id: run-product-discovery-001
objective_id: obj-001
primary_harness: roles/product-strategist
supporting_harnesses:
  - lifecycle/discovery
  - verification/evidence-readiness
source_harnesses:
  - id: product-strategist
    path: .mm-flow/harness-library/roles/product-strategist
  - id: evidence-readiness
    path: .mm-flow/harness-library/verification/evidence-readiness
selected_skills:
  - id: memory-retrieval
    source_path: .mm-flow/harness-library/shared-skills/memory-retrieval
  - id: generate-prd
    source_path: .mm-flow/harness-library/roles/product-strategist/skills/generate-prd
precedence:
  - project_policy
  - primary_harness
  - supporting_harnesses
  - selected_skills
  - selected_references
created_at: "<iso8601>"
stage_graph_ref: stages.yaml
content_hash: "<sha256>"
```

## 12. Precedencia

Para evitar conflicto multi-harness, el runtime aplica este orden:

```text
project policy
> primary harness
> supporting harnesses
> selected skills
> selected references
```

Reglas:

- Sólo un harness puede declarar la identidad primaria.
- Supporting harnesses no pueden sobrescribir rol, tono global o políticas del proyecto.
- Skills no pueden modificar políticas; sólo ejecutan capacidades atómicas.
- References no instruyen comportamiento salvo que el harness las active explícitamente.
- Si hay conflicto de seguridad, gana project policy.

## 13. Loader estándar

El cliente/runtime debe exponer una operación equivalente a:

```text
load_content(path: str) -> str
```

Comportamiento:

- Si `path` apunta a un directorio agrupador, devuelve su routing file.
- Si `path` apunta a una leaf, devuelve el archivo primario detectado por `.leaf-detectors`.
- Si `path` apunta a un archivo, devuelve el contenido del archivo.
- Si no hay routing file, devuelve listing mínimo del directorio.

## 14. Script execution

Scripts viven dentro de skills, no en raíz del harness:

```text
skills/<skill-id>/scripts/<script>
```

El runtime debe exponer una operación equivalente a:

```text
run_script(path: str, script: str, args: list[str]) -> str
```

Reglas:

- argumentos por stdin o CLI args
- output por stdout
- fallo por exit code no cero
- errores en stderr
- credenciales por variables de entorno, nunca hardcoded

## 15. Validación estructural

Cada harness individual debe validar:

```text
harnesses-ref validate .mm-flow/harness-library/roles/product-strategist
```

Cada bundle compuesto debe validar:

```text
harnesses-ref validate .run-bundles/<run-id>
```

Errores bloquean activación. Warnings se registran y se corrigen según severidad.

## 16. Validación behavioral

Mantener un set versionado de 10 a 20 prompts por harness o familia.

Ubicación canónica por defecto:

```text
.mm-flow/harness-library/routing-cases.yaml
```

Ejecución:

```bash
uv run --no-sync python -m mastermind_cli.mm_flow.cli harness-routing-check
```

Cada caso declara:

- prompt
- expected primary harness
- expected supporting harnesses
- expected skills
- forbidden skills
- expected references
- max context budget

Ejemplo:

```yaml
- case_id: product-prd-from-evidence
  prompt: "Crea un PRD para este objetivo usando evidencia existente"
  expected_primary_harness: roles/product-strategist
  expected_supporting_harnesses:
    - verification/evidence-readiness
  expected_skills:
    - shared-skills/memory-retrieval
    - roles/product-strategist/skills/generate-prd
  forbidden_skills:
    - shared-skills/code-edit
  max_harness_body_tokens: 600
```

## 17. Buenas prácticas obligatorias

### 17.1 Context budget

- `HARNESS.md` ideal: menos de 300 tokens.
- `HARNESS.md` aceptable para harness complejo: 300 a 600 tokens.
- Más de 600 tokens exige routing files y extracción a references.

### 17.2 Skills atómicas

Cada skill debe hacer una sola cosa.

Bueno:

```text
skills/generate-prd/
skills/check-evidence-readiness/
skills/query-memory/
```

Malo:

```text
skills/product-everything/
```

### 17.3 Cross-skill knowledge

Conocimiento usado por varias skills vive en `references/` del harness o en shared references, no duplicado dentro de cada skill.

### 17.4 Descriptions accionables

Descriptions deben responder “cuándo mirar aquí”.

Bueno:

```yaml
description: Generate a PRD from an objective, evidence notes, and acceptance constraints.
```

Malo:

```yaml
description: PRD skill.
```

## 18. Observabilidad

Cada selección y composición debe registrar:

- objective profile
- candidates considered
- selected primary harness
- selected supporting harnesses
- selected skills
- rejected alternatives
- validation result
- bundle path
- context budget estimate
- final execution envelope
- stage decisions, evidence, approvals y checkpoint refs

## 19. Failure modes

### 19.1 No primary harness

Status: `blocked`.

Acción: pedir discovery o crear harness faltante.

### 19.2 Multiple primary harnesses

Status: `failed`.

Acción: resolver conflicto de rol antes de ejecutar.

### 19.3 Missing skill leaf detector

Status: `failed`.

Acción: agregar `.leaf-detectors` con `skill=SKILL.md`.

### 19.4 Routing ambiguity

Status: `needs_review`.

Acción: ajustar `description` o routing file.

### 19.5 Bundle validation failure

Status: `failed`.

Acción: no ejecutar; reparar bundle o seleccionar alternativa.

## 20. Implementación mínima recomendada

### Slice 1 — Modelos

Agregar modelos tipados:

- `ObjectiveProfile`
- `HarnessPackage`
- `SkillPackage`
- `HarnessCompositionPlan`
- `RunBundle`

### Slice 2 — Catálogo filesystem

Agregar `FileSystemHarnessCatalog`:

- lee `registry.yaml`
- descubre `HARNESS.md`
- lee descriptions
- valida `.leaf-detectors`
- expone candidatos al selector

### Slice 3 — Selector multi-harness

Extender el selector actual para devolver `HarnessCompositionPlan`.

### Slice 4 — Composer

Agregar `RunBundleComposer`:

- crea `.run-bundles/<run-id>/`
- genera `HARNESS.md` compuesto
- genera `.leaf-detectors`
- enlaza o copia skills seleccionadas
- escribe `bundle.yaml`

### Slice 5 — Validación

Agregar tests para:

- harness individual válido
- bundle compuesto válido
- routing esperado
- precedencia
- failure modes

### Slice 6 — Stage execution

Implementar `RunBundleStageExecutor` como foundation compartida:

- valida y ejecuta el stage graph
- invoca sólo capabilities seleccionadas
- registra evidence, approvals y checkpoints
- enruta review/recovery y safe replanning
- mantiene domain semantics fuera del executor

## 21. Exit criteria

La arquitectura multi-harness está lista cuando:

- el selector produce un `HarnessCompositionPlan` determinístico
- el composer produce un RunBundle validable
- el runtime puede ejecutar desde ese bundle
- cada bundle preserva lineage
- los tests de routing pasan
- no se carga contexto fuera del plan seleccionado

La ejecución detallada se rige por
`113-HARNESS-STAGE-EXECUTION-RUNTIME-CONTRACT.md`.

## 22. No-goals

- no cargar toda la biblioteca en cada run
- no permitir múltiples identidades primarias
- no mezclar instrucciones por concatenación libre
- no convertir supporting harnesses en roles ocultos
- no ejecutar bundles que fallen validación estructural
- no duplicar knowledge compartido dentro de cada skill
