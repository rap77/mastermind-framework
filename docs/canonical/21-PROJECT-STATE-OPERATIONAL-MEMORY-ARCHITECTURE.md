# Project State & Operational Memory Architecture

## 1. Propósito

Definir la capa canónica donde MasterMind guarda el estado operativo real de cada proyecto, sus artefactos, tareas, decisiones, checkpoints y memoria recuperable.

---

## 2. Tesis central

> MasterMind no debe depender del contexto efímero de cada proveedor para saber en qué estado está un proyecto; debe poseer ese estado en su propia capa estructurada.

---

## 3. Qué resuelve

- continuidad entre runs y modelos
- menor dependencia de historiales largos
- trazabilidad de tareas, decisiones y checkpoints
- base para dashboards, estimaciones y colaboración humana
- base para proyecciones de contexto en tiempo real

---

## 4. Componentes

### A. Artifact Store
Guarda specs, tasks, plans, reviews, validations y reports en markdown con metadata estructurada.

### B. Execution State Store
Guarda tarea actual, run actual, actor actual, estado, bloqueo, próximo paso y checkpoint vigente.

### C. Decision Store
Guarda decisiones, posiciones por brain, objeciones, vetos y outcomes.

### D. Checkpoint & Resume Store
Guarda checkpoints estructurados y el estado mínimo de reanudación.

### E. Semantic Retrieval Store
Usa embeddings para recuperar artefactos, decisiones y checkpoints relevantes.

### F. Context Projection Layer
Construye contexto JSON limpio para agentes desde el estado estructurado.

---

## 5. Principios

1. El proyecto tiene una fuente de verdad propia.
2. El contexto de tarea se proyecta desde estado estructurado.
3. El markdown sigue siendo artefacto humano principal.
4. JSONB y pgvector complementan, no sustituyen, la estructura base.

---

## 6. Entidades mínimas

- `projects`
- `artifacts`
- `tasks`
- `task_dependencies`
- `task_runs`
- `decision_records`
- `checkpoints`
- `artifact_embeddings`

---

## 7. Resultado esperado

Permitir que MasterMind responda rápidamente:

- qué se está haciendo
- por quién
- con qué contexto
- por qué está bloqueado
- qué sigue
- qué decisiones condicionan el trabajo actual

## Key Learnings:

1. El estado del proyecto debe vivir fuera del contexto efímero del proveedor.
2. Artefactos, estado y checkpoints deben modelarse como una sola capa operativa.
3. La proyección de contexto debe salir de esta capa, no del caos del filesystem.
