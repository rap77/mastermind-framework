# Multi-Harness & Loop Engineering Synthesis

## Goal

Preservar la investigación sobre **ECC**, **gentle-ai** y los notebooks de
NotebookLM para que la evolución de MasterMind hacia un sistema agnóstico,
multi-harness, multi-loop y con memoria persistente quede explícita dentro de
AI-DLC.

## Source Inputs

- ECC (`/tmp/ECC`)
- gentle-ai (`/tmp/gentle-ai`)
- NotebookLM:
  - `Ingeniería de Arneses de IA: Arquitectura y Sistemas Agnósticos`
  - `Ingeniería de Loops de IA: Feedback Loops, Control Loops y Sistemas Iterativos`
- Estado actual del repo:
  - `apps/api/mastermind_cli/*`
  - `tools/mastermind-cli/mastermind_cli/*`
  - `aidlc-docs/*`

## Research Summary

### 1. Principio rector

MasterMind debe operar con la regla:

> **probabilístico por dentro, determinístico en los bordes**

La IA puede razonar, proponer y explorar; el runtime debe imponer contratos
explícitos para scope, validación, finalización, recuperación, auditabilidad y
continuidad.

### 2. Qué sí tomar de ECC

- visión de **harness operating system** como norte de largo plazo
- session/worktree state exportable
- contracts de sesión/worker y payloads de status
- auditabilidad, readiness, risk posture
- mejora continua separada en:
  - observación
  - propuesta
  - verificación
  - promoción
  - rollback

### 3. Qué sí tomar de gentle-ai

- orquestador delgado: coordina, no “hace todo”
- separación por fases / modos de trabajo
- skill registry indexado por path exacto
- delegación basada en umbrales reales de complejidad
- memoria persistente como parte del runtime, no como accesorio

### 4. Qué no copiar todavía

- OS completo multi-superficie tipo ECC
- capa comercial / billing / GitHub App
- explosión de skills/commands/adapters prematura
- paridad cross-harness agresiva antes de cerrar el core
- automejora write-enabled sin verificador fuerte
- SDD completo como default universal para cualquier tarea

## Architectural Direction

### Now

Fortalecer el núcleo para soportar:

- multi-harness explícito
- multi-loop explícito
- envelope contract único
- maker-checker split
- recovery bounded
- capability registry

### Next

Construir:

- selección dinámica de harness/loop según tarea
- snapshots de work item / run state
- continuidad entre modelos/harnesses al agotarse créditos
- verificadores especializados por tipo de outcome

### Later

Expandir hacia:

- adapters cross-harness más amplios
- runtime de worktrees/sesiones más rico
- status payloads/HUD
- loop scheduling autónomo más amplio

### North Star

MasterMind debe llegar a ser un **operator system agnóstico al modelo/harness**
que:

- no pierde memoria ni contexto útil
- mantiene continuidad entre sesiones y proveedores
- selecciona el mínimo control suficiente por tarea
- aprende de su experiencia sin degradar seguridad ni auditabilidad

## Canonical Harness Inventory

1. **Orchestrator Harness**
2. **Context & Memory Harness**
3. **Execution Harness**
4. **Verification Harness**
5. **Review Harness**
6. **Recovery Harness**
7. **Observability & Audit Harness**

## Canonical Loop Taxonomy

1. **Tool Loop** — tareas simples y determinísticas
2. **Goal Loop** — iteración hasta condición verificable
3. **Verification Loop** — validación externa del estado logrado
4. **Reflection Loop** — crítica y refinamiento cuando la calidad no basta
5. **Recovery Loop** — retry/patch/replan/escalate
6. **Review Loop** — maker-checker / adversarial review
7. **Heartbeat Loop** — monitoreo o automation recurrente

## Critical Design Rules

1. El **maker no se verifica a sí mismo**.
2. No todo requiere el mismo loop.
3. No todo requiere multi-agent.
4. Los loops deben tener:
   - criterio de validación
   - criterio de aceptación
   - criterio de finalización
   - criterio de escalación
5. La selección debe ser por **minimum sufficient control**.
6. Las mejoras aprendidas deben empezar como:
   - observación persistida
   - propuesta
   - verificación
   - promoción manual o gated

## Capability Registry Direction

MasterMind no debe limitarse a un inventario pasivo de skills o MCPs. Debe
evolucionar hacia un **Capability Registry** que indexe:

- harnesses
- loops
- brains
- skills
- MCPs
- commands
- verificadores
- políticas de recovery

Con metadatos como:

- objetivo
- costo
- riesgo
- prerequisitos
- compatibilidad por harness
- compatibilidad por modelo/proveedor
- necesidad de fresh context
- necesidad de checker separado
- criterios de “cuándo usar” / “cuándo no usar”

## Recommended First Slices

### Slice 1

- Envelope Contract único
- Loop Selection Policy

### Slice 2

- Verification Harness
- Maker-Checker Split

### Slice 3

- Recovery Harness
- Circuit Breakers

### Slice 4

- Capability Registry inicial
- Dynamic capability selection

## Open Questions

1. ¿Qué harnesses serán obligatorios en el primer release del nuevo núcleo?
2. ¿Qué señales decidirán cambio de modelo/backend por agotamiento de créditos?
3. ¿Cuál es el contrato mínimo exportable de estado de ejecución?
4. ¿Qué parte del capability registry debe vivir en código tipado vs config?
5. ¿Qué mejoras de experiencia pueden auto-promoverse y cuáles siempre exigen aprobación humana?
