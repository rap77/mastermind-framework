# Postgres Hybrid Data Model

## 1. Propósito

Definir el modelo de datos recomendado para MasterMind usando Postgres como base principal, combinando estructura relacional, JSONB y pgvector.

---

## 2. Tesis central

> MasterMind necesita un modelo híbrido: relacional para estructura crítica, JSONB para flexibilidad operativa, y pgvector para recuperación semántica.

---

## 3. Por qué no todo relacional

Porque el sistema necesita almacenar:

- metadata variable por proyecto
- payloads de eventos
- snapshots de checkpoints
- config por adapter
- doctrine projections
- context projections

Eso encaja mejor en JSONB.

---

## 4. Por qué no todo JSON

Porque el sistema también necesita:

- dependencias entre tareas
- joins limpios
- agregaciones de costo/tiempo
- scheduling
- ownership
- versionado y lineage
- dashboards analíticos

Eso encaja mejor en un core relacional.

---

## 5. Recomendación

### A. Relational Core

Para entidades con identidad fuerte y relaciones claras.

### B. JSONB Edge Layer

Para metadata flexible, payloads y snapshots.

### C. Vector Layer

Para retrieval semántico sobre artefactos, decisiones y checkpoints.

### D. Projection Layer

Para exponer JSON limpio y contextual a agentes y UIs.

---

## 6. Entidades del core relacional

### Project domain
- `projects`
- `project_adapters`
- `project_participants`

### Artifact domain
- `artifacts`
- `artifact_versions`
- `artifact_links`

### Planning / execution domain
- `tasks`
- `task_dependencies`
- `task_runs`
- `task_time_events`
- `task_estimates`
- `task_metrics`

### Decision domain
- `decision_records`
- `decision_positions`
- `decision_artifact_links`

### Runtime domain
- `backend_sessions`
- `availability_states`
- `run_policies`
- `scheduler_events`

### Continuity domain
- `checkpoints`
- `checkpoint_artifact_links`

### Telemetry domain
- `token_usage_events`
- `quality_events`

### Doctrine domain
- `doctrine_documents`
- `policy_rules`
- `methodology_profiles`
- `phase_gates`
- `enforcement_results`

---

## 7. Uso recomendado de JSONB

### JSONB en `artifacts`
Para metadata variable:

- tags
- niche
- source refs
- review status

### JSONB en `checkpoints`
Para snapshot estructurado de reanudación:

- context summary
- next step
- open questions
- constraints

### JSONB en `scheduler_events`
Para payloads específicos de runtime:

- raw provider hints
- reset evidence
- switch notes

### JSONB en `policy_rules`
Para condiciones complejas:

- applies_to_phase
- applies_to_task_type
- applies_to_brain

### JSONB en `token_usage_events`
Para provider-specific fields:

- cache info
- request ids
- pricing snapshot

---

## 8. Uso recomendado de pgvector

### Artefactos
- specs
- decisions
- validations
- reports

### Checkpoints
- context summaries
- next-step summaries

### Optional
- doctrine docs
- task summaries

---

## 9. Principios de diseño

1. La verdad estructural va en tablas.
2. La flexibilidad va en JSONB.
3. La similitud semántica va en pgvector.
4. Los agentes no consultan la base cruda; consumen proyecciones.

---

## 10. Ejemplo de patrón híbrido

### `tasks`
Campos relacionales:
- `task_id`
- `project_id`
- `title`
- `status`
- `owner_id`
- `priority`

Campos JSONB:
- `metadata`
- `constraints`
- `completion_criteria`

### `checkpoints`
Campos relacionales:
- `checkpoint_id`
- `project_id`
- `task_id`
- `created_at`

Campos JSONB:
- `resume_state`
- `context_summary`
- `open_questions`

---

## 11. Beneficios del modelo híbrido

- mejor analytics
- mejor scheduling
- mejor colaboración humana
- retrieval semántico útil
- contexto JSON limpio para modelos
- menos dependencia de archivos sueltos

---

## 12. Riesgos si se diseña mal

### Riesgo 1
Poner demasiada estructura crítica dentro de JSONB.

### Riesgo 2
Intentar modelar toda variabilidad con tablas rígidas.

### Riesgo 3
Usar pgvector como sustituto de relaciones normales.

### Riesgo 4
Hacer que agentes dependan de consultas SQL crudas.

---

## 13. Regla práctica

> Relacional para identidad y relaciones; JSONB para flexibilidad; vector para recuperación; proyecciones para consumo de agentes.

---

## 14. Próximos artefactos recomendados

1. `28-CONTEXT-PROJECTION-STRATEGY.md`
2. `29-INITIAL-POSTGRES-SCHEMA-SLICE.md`
3. `30-DASHBOARD-INFORMATION-ARCHITECTURE.md`

## Key Learnings:

1. El modelo correcto para MasterMind no es SQL puro ni JSON puro, sino híbrido.
2. Los modelos pueden seguir trabajando con JSON si la capa de proyección hace su trabajo.
3. El valor del diseño híbrido está en separar almacenamiento, retrieval y consumo agente.
