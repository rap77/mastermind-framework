# Artifact Versioning and Lineage

## 1. Propósito

Definir cómo MasterMind versiona artefactos y preserva lineage entre specs, tareas, decisiones, revisiones, checkpoints y outputs.

---

## 2. Qué resuelve

- saber qué cambió y por qué
- relacionar tareas con specs y decisiones
- reconstruir causalidad
- mejorar auditoría y replay

---

## 3. Qué debe versionarse

- specs
- plans
- tasks
- doctrine docs
- decision records
- validations
- reports
- context summaries críticos

---

## 4. Qué debe modelar el lineage

- esta tarea salió de qué spec
- esta decisión impactó qué tareas
- este output vino de qué run
- este checkpoint usó qué artefactos
- esta revisión aprobó o rechazó qué versión

---

## 5. Principios

1. Versionado y lineage no son lo mismo.
2. Todo artefacto crítico debe ser trazable a sus causas.
3. Las relaciones deben ser consultables y visualizables.
4. El lineage debe servir tanto para auditoría como para contexto.

---

## 6. Entidades sugeridas

- `artifact_versions`
- `artifact_links`
- `decision_artifact_links`
- `task_artifact_links`
- `checkpoint_artifact_links`

## Key Learnings:

1. Sin lineage, el proyecto tiene historial pero no causalidad.
2. Specs, tareas y decisiones deben quedar conectadas explícitamente.
3. El versionado de artefactos es base para replay, auditoría y mejores proyecciones de contexto.
