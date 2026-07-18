# 50. Project Control Plane Schema and Router

## 1. Propósito

Definir el esquema mínimo del control plane de proyecto y el contrato del router
de metodologías que decide cómo avanzar un objetivo.

---

## 2. Tesis central

> MasterMind should expose a project control plane: markdown remains canonical
> for human-authored artifacts, Postgres stores the structured registry and
> lineage, and the router selects the smallest safe methodology route.

---

## 3. Qué existe hoy

El slice `project_state` ya cubre buena parte de la base relacional:

- `ps_projects`
- `ps_tasks`
- `ps_task_dependencies`
- `ps_task_runs`
- `ps_checkpoints`
- `ps_decision_records`
- `ps_token_usage_events`
- `ps_artifact_versions`
- `ps_artifact_links`
- `ps_objective_documents`
- `ps_objective_events`
- `ps_objective_projection`
- `ps_objective_sync_state`

Eso ya permite armar una superficie de control plane sin crear un modelo nuevo
desde cero.

---

## 4. Esquema mínimo del control plane

### A. Project registry

Entidad principal:

- `ps_projects`

Responsabilidad:

- identidad del proyecto
- estado general
- adapter asociado
- metadata flexible

### B. Artifact registry

Entidades:

- `ps_artifact_versions`
- `ps_artifact_links`

Responsabilidad:

- versionado inmutable
- lineage causal entre versiones
- trazabilidad de specs, plans, tasks, decisions y checkpoints

### C. Planning projection

Entidades:

- `ps_objective_documents`
- `ps_objective_events`
- `ps_objective_projection`
- `ps_objective_sync_state`

Responsabilidad:

- reflejar el estado file-backed de `.planning`
- mantener un snapshot consultable del objective activo
- sincronizar surface state sin mezclar runtime con docs

### D. Execution read-side

Entidades:

- `ps_tasks`
- `ps_task_dependencies`
- `ps_task_runs`
- `ps_checkpoints`
- `ps_decision_records`
- `ps_token_usage_events`

Responsabilidad:

- progreso
- dependencias
- continuidad
- decisiones
- costos/telemetría

---

## 5. Campos que no deben faltar

El control plane necesita, como mínimo:

- `project_id`
- `artifact_id` / `version_id`
- `task_id`
- `decision_id`
- `checkpoint_id`
- `objective_slug`
- `created_at` / `updated_at`
- `metadata` o `payload` JSONB donde el shape sea variable

---

## 6. Router de metodologías

El router no elige “frameworks”; elige una ruta de trabajo.

### Entrada

- intención del usuario
- madurez del proyecto
- complejidad de la tarea
- restricciones activas
- políticas aplicables

### Salida

- harness principal
- loops internos
- policies activas
- proyección a actualizar
- verificación esperada

### Regla base

Seleccionar el camino mínimo que cumpla el objetivo de forma segura.

---

## 7. Router boundaries

### A. Harnesses

El router puede seleccionar:

- Discovery
- Onboarding
- AI-DLC
- SDD
- TDD
- Execution
- Verification
- Recovery

### B. Loops

El router puede activar:

- tool loop
- verify loop
- review loop
- recovery loop
- refactor loop

### C. Policies

Las policies pueden restringir cualquier ruta:

- Clean Code
- Security
- Architecture
- Naming
- Testing Discipline

---

## 8. Responsibilities split

### Project control plane

- persiste estado estructurado
- expone proyecciones
- conserva lineage
- permite navegación y auditabilidad

### Methodology router

- decide la ruta
- no ejecuta trabajo de dominio
- no reemplaza al planner
- no reemplaza al runtime

### Markdown docs

- siguen siendo la fuente canónica para artefactos humanos
- no se reemplazan por filas sueltas en BD

---

## 9. Minimal acceptance criteria

El diseño está bien si:

- el project overview puede construirse desde `project_state`
- specs/tasks/decisions/checkpoints quedan conectados por lineage
- `.planning` puede proyectarse sin romper el runtime
- el router puede elegir una ruta mínima y auditable

---

## 10. Next implementation slice

1. formalizar `ProjectOverview` como entrada principal del control plane
2. completar el esquema de artifact lineage para specs y decisions
3. conectar `ObjectiveProjectionState` con el router de metodologías
4. definir la UI de lectura tipo Obsidian sobre el grafo de artefactos

## Key Learnings:

1. `project_state` ya tiene la mayoría de las tablas base para el control plane.
2. El router de metodologías es una capa de decisión, no una nueva metodología.
3. La separación correcta es: markdown canónico, Postgres estructural, grafo/retrieval como acceso.
