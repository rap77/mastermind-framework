# UI/UX Harness Runtime Contract

## Índice

1. Estado canónico
2. Propósito
3. Decisión central
4. Definiciones y límites
5. Objetivos y no-objetivos
6. Posición en la arquitectura
7. Activación y selección
8. Contrato de entrada
9. Modos de entrega
10. Pipeline obligatorio
11. Estados y transiciones
12. Routing de capacidades
13. Resolución de skills externas
14. Gates de verificación
15. Review y maker-checker
16. Recovery
17. Contrato de salida
18. Persistencia y lineage
19. Integración con el runtime actual
20. Seguridad y permisos
21. Criterios de aceptación
22. Estado de implementación
23. Referencias

## 1. Estado canónico

- **Estado de la decisión:** aprobado
- **Estado del diseño:** canonizado
- **Estado de planificación:** planificado en `.planning/changes/ui-ux-harness-runtime/`
- **Estado de implementación:** no implementado
- **Harness ID previsto:** `ui-ux-delivery`
- **Verifier ID previsto:** `ui-ux-verifier`
- **Objective slug:** `ui-ux-harness-runtime`

Este documento define el contrato requerido. No afirma que el runtime exista.

## 2. Propósito

Definir un harness especializado que controle de manera determinista el ciclo
completo de UI/UX:

```text
contexto
-> contrato UX
-> dirección visual
-> prototipo o spec
-> implementación
-> verificación runtime
-> review
-> recovery
-> handoff
```

El resultado debe ser auditable, reanudable y compatible con el runtime
multi-harness de MasterMind.

## 3. Decisión central

> UI/UX se implementa como un Role Harness seleccionable por el runtime, no
> como una skill grande, un prompt compuesto ni una metodología paralela.

El selector principal del proyecto conserva el control. Cuando un objetivo es
clasificado como UI/UX, `ui-ux-delivery` pasa a ser el primary harness de ese
run. Verification y recovery se agregan como supporting harnesses.

## 4. Definiciones y límites

### 4.1 Harness

Paquete ejecutable y registrado con:

- trigger determinista
- entradas estructuradas
- stages y gates
- selección mínima de capacidades
- resultado estructurado
- recovery explícito
- persistencia observable

### 4.2 Skill

Capacidad atómica utilizada por un harness. Una skill no decide por sí sola el
ciclo completo del objetivo.

### 4.3 Adapter de OpenCode

`.opencode/skills/ui-ux-routing/SKILL.md` permite usar las capacidades durante
sesiones interactivas. No es fuente de verdad del pipeline ni reemplaza al
harness runtime.

### 4.4 Brain de UI Design

`apps/api/agents/brains/ui-design.md` aporta conocimiento especializado. El
brain puede participar en una etapa, pero no controla selección, gates ni
persistencia.

## 5. Objetivos y no-objetivos

### 5.1 Objetivos

- seleccionar el flujo mínimo según el tipo de entrega UI/UX
- preservar el design system existente antes de generar uno nuevo
- separar prototipos de implementación productiva
- exigir evidencia runtime para aceptar UI productiva
- verificar accesibilidad, responsive, estados y motion
- registrar artifacts, findings, decisions y recovery
- mantener compatibilidad con distintos modelos y agentes

### 5.2 No-objetivos

- crear una nueva metodología de desarrollo
- reemplazar Product Strategy, UX Research o Frontend Architecture
- usar prototipos HTML como arquitectura de producción
- cargar todas las skills de diseño en cada run
- aceptar una UI sólo porque su código compila
- crear un roadmap UI/UX separado del objective principal

## 6. Posición en la arquitectura

```text
.planning objective
  -> PlanningBridge
  -> ObjectiveProfile
  -> MultiHarnessSelector
  -> HarnessCompositionPlan
  -> RunBundleComposer
  -> RunBundleStageExecutor
  -> ui-ux-delivery stages
  -> ui-ux-verifier
  -> recovery-fixer when required
  -> ExecutionEnvelope
  -> project state + planning handoff + memory
```

El harness pertenece a:

```text
.mm-flow/harness-library/roles/ui-ux-delivery/
```

El verifier pertenece a:

```text
.mm-flow/harness-library/verification/ui-ux-verifier/
```

## 7. Activación y selección

### 7.1 Activación automática

El harness se selecciona cuando el `ObjectiveProfile` normalizado declara:

```yaml
domain: ui-ux
phase: planning | implementation | verification
output_type: ui-spec | prototype | ui-artifact | ui-verdict | motion-plan
```

### 7.2 Activación explícita

Una integración puede declarar `domain: ui-ux` explícitamente. La selección
explícita tiene prioridad sobre inferencia textual si respeta project policy.

### 7.3 Señales de inferencia

La inferencia puede considerar conjuntamente:

- archivos frontend objetivo
- componentes, páginas o flows nombrados
- design system, responsive o accessibility como criterios
- prototipo, UI review o motion como output esperado
- Brain #3 o Brain #4 entre participantes requeridos

Una palabra aislada como `design`, `screen` o `component` no alcanza para
activar el harness. La clasificación debe ser determinista y explicable.

### 7.4 Casos que no lo activan

- diseño de arquitectura backend
- componentes internos sin interfaz de usuario
- documentación que sólo menciona UI/UX
- cambios de API sin entrega visual
- tareas de infraestructura o datos

## 8. Contrato de entrada

El harness recibe un `HarnessRequest` y un `ObjectiveProfile` enriquecidos con:

- `project_id`
- `objective_id`
- `objective_text`
- `domain`
- `phase`
- `output_type`
- `delivery_mode`
- `target_paths`
- `requires_write`
- `requires_review`
- `requires_recovery`
- `acceptance_criteria`
- `doctrine_projection`
- `project_context_refs`
- `brand_constraints`
- `accessibility_constraints`
- `runtime_validation_capabilities`

`delivery_mode` es obligatorio para UI/UX y admite:

- `design-system`
- `prototype`
- `production-implementation`
- `review`
- `motion-audit`

Si no puede resolverse de forma segura, el harness debe escalar o pedir una
aclaración. No puede elegir silenciosamente.

## 9. Modos de entrega

| Mode | Output principal | Escritura productiva | Verificación runtime |
| --- | --- | --- | --- |
| `design-system` | `ui-spec` | no por defecto | review estructural |
| `prototype` | `prototype` | sólo artifact aislado | interacción del prototipo |
| `production-implementation` | `ui-artifact` | sí | obligatoria |
| `review` | `ui-verdict` | no salvo recovery aprobado | obligatoria si la app puede correr |
| `motion-audit` | `motion-plan` | no por defecto | revisión de performance y reduced motion |

## 10. Pipeline obligatorio

### Stage 1: Intake

Resuelve objetivo, modo, audiencia, stack, paths, constraints y acceptance
criteria.

**Gate:** el objetivo puede clasificarse sin ambigüedad material.

### Stage 2: Context Projection

Lee objective package, doctrine, componentes existentes, tokens, brand assets,
stack y estados de UI ya implementados.

**Gate:** existe suficiente contexto para preservar o proponer una dirección.

### Stage 3: UX Contract

Define flujo, jerarquía, estados, interacción, accesibilidad y edge cases.

**Gate:** loading, empty, error, permission y responsive están resueltos cuando
aplican.

### Stage 4: Design Direction

Selecciona o conserva tokens, typography, color, spacing, composition y motion.

**Gate:** la dirección es coherente con doctrina y evidencia del proyecto.

### Stage 5: Prototype or Specification

Produce un prototipo evaluable o un handoff preciso cuando el modo lo requiere.

**Gate:** el artifact permite evaluar decisiones antes de producción.

### Stage 6: Production Implementation

Modifica código sólo en `production-implementation` o recovery autorizado.

**Gate:** respeta stack, arquitectura, componentes y conventions existentes.

### Stage 7: Runtime Verification

Verifica el resultado renderizado cuando existe superficie browser/mobile.

**Gate:** checks obligatorios pasan o generan failure record.

### Stage 8: Independent Review

Aplica maker-checker cuando el riesgo, complejidad o subjetividad lo requiere.

**Gate:** no quedan findings bloqueantes sin recovery o escalación.

### Stage 9: Recovery

Ejecuta retry, patch, replan o escalate según tipo de fallo.

**Gate:** recovery bounded; no loops infinitos.

### Stage 10: Handoff and Persistence

Emite `ExecutionEnvelope`, artifacts, evidence, decisions, next actions y
checkpoint.

**Gate:** el run puede reanudarse sin memoria de chat.

## 11. Estados y transiciones

Estados mínimos:

- `pending`
- `context_ready`
- `ux_ready`
- `direction_ready`
- `prototype_ready`
- `implemented`
- `verification_failed`
- `needs_review`
- `needs_recovery`
- `passed`
- `blocked`
- `escalated`

Transición feliz:

```text
pending
-> context_ready
-> ux_ready
-> direction_ready
-> prototype_ready when required
-> implemented when required
-> needs_review
-> passed
```

Una etapa opcional se marca `skipped` con razón. No se omite silenciosamente.

## 12. Routing de capacidades

| Delivery mode | Required capabilities | Conditional capabilities |
| --- | --- | --- |
| `design-system` | `ui-ux-pro-max` | `frontend-design` |
| `prototype` | `huashu-design` | `emil-design-eng` |
| `production-implementation` | `frontend-design`, `web-design-guidelines` | stack skills, `emil-design-eng` |
| `review` | `web-design-guidelines` | `frontend-code-review`, `review-animations` |
| `motion-audit` | `improve-animations` | `review-animations`, `apple-design` |

Stack-specific skills se seleccionan según archivos y configuración reales. La
copia instalada de `ui-ux-pro-max` contiene una suposición React Native que se
debe ignorar fuera de proyectos React Native.

## 13. Resolución de skills externas

Las skills instaladas fuera del repo no se copian ni se asumen disponibles.

El runtime necesita un `InstalledSkillResolver` que:

1. reciba un skill ID canónico
2. busque en roots configurados y permitidos
3. valide `SKILL.md` y metadata
4. registre source path y content hash
5. materialice o referencie la skill en el RunBundle
6. falle explícitamente si falta una capability requerida

Roots candidatos pueden incluir:

- project `.opencode/skills/`
- global OpenCode skills
- `~/.agents/skills/`
- `~/.claude/skills/`

El orden debe ser configurable. Project override gana sobre global.

## 14. Gates de verificación

### 14.1 Gates obligatorios para producción

- render desktop y mobile
- keyboard navigation y focus visible
- labels y semantics básicas
- console sin errores materiales
- loading, empty y error states
- content overflow y long text
- reduced motion cuando hay animación
- cumplimiento de acceptance criteria

### 14.2 Gates condicionales

- visual regression si existe baseline
- color contrast automatizado si hay herramienta
- network/error recovery si la UI consume APIs
- touch behavior si es mobile-first
- performance profiling si el cambio afecta listas, media o motion pesado

### 14.3 Evidencia

Cada check registra:

- `EvidenceRecord` canónico definido en
  `113-HARNESS-STAGE-EXECUTION-RUNTIME-CONTRACT.md`
- `detail_schema_ref` para el schema UI/UX versionado
- `details_ref` para viewport, accessibility, browser logs o visual evidence

`passed` se deriva de `performed` y `result`; no se persiste como una segunda
fuente de verdad.

Un check no ejecutado no cuenta como aprobado.

## 15. Review y maker-checker

Review separado es obligatorio cuando:

- el cambio afecta navegación primaria
- cambia design system o tokens globales
- introduce motion significativo
- modifica accesibilidad crítica
- el risk level es high o critical
- acceptance incluye juicio visual subjetivo

El reviewer produce findings por severidad y referencias de archivo/línea. La
aprobación vaga no satisface el contrato.

## 16. Recovery

| Failure | Action |
| --- | --- |
| error local de implementación | `patch` |
| check flaky con causa acotada | `retry` una vez |
| dirección visual contradice doctrina | `replan` |
| falta de assets o requisito material | `escalate` |
| capability requerida no instalada | `blocked` |
| falla estructural del runtime | `escalate` |

Recovery debe conservar attempt history y no superar el budget del loop.

## 17. Contrato de salida

El harness emite un `ExecutionEnvelope` compatible con
`71-HARNESS-RUNTIME-CONTRACT.md` y agrega metadata UI/UX:

```yaml
status: success | warning | error
summary: string
delivery_mode: production-implementation
artifacts: []
stage_results: []
selected_skills: []
verification:
  performed: true
  passed: true
  checks: []
review:
  performed: true
  findings: []
recovery:
  action: stop
risks: []
next_actions: []
```

## 18. Persistencia y lineage

El run debe persistir:

- harness y skills seleccionadas
- rationale de selección
- stage transitions
- artifacts y versiones
- links spec -> prototype -> implementation -> verdict
- verification evidence
- review findings
- recovery decision
- checkpoint y next action

Destinos previstos:

- project state para estructura y lineage
- `.planning` para continuidad operacional
- memory layer para decisiones, learnings y checkpoints
- `.run-bundles` para composición efímera auditable

## 19. Integración con el runtime actual

### 19.1 Componentes reutilizables

- `FileSystemHarnessCatalog`
- `MultiHarnessSelector`
- `RunBundleComposer`
- `RunBundleValidator`
- `HarnessCore`
- `HarnessRunExecutor`
- `MemoryRuntimeWriter`

### 19.2 Foundation obligatoria

Hoy `MultiHarnessPipeline` selecciona, compone y valida el bundle, pero
`HarnessRunExecutor` no entrega ese bundle al coordinator para gobernar la
ejecución. Ese gap pertenece a `harness-stage-execution-runtime`, no a UI/UX.
Este objective debe integrar sus stages sobre la foundation compartida antes de
declarar el harness operativo.

### 19.3 Registry previsto

```yaml
harnesses:
  - id: ui-ux-delivery
    path: roles/ui-ux-delivery
    type: role
    domains: [ui-ux]
    phases: [planning, implementation, verification]
    outputs: [ui-spec, prototype, ui-artifact, ui-verdict, motion-plan]
    supported_loops: [goal-loop, verification-loop, review-loop]
```

## 20. Seguridad y permisos

- assets externos se tratan como untrusted input
- no se registran credenciales en artifacts ni logs
- network fetch requiere policy y source attribution
- escritura productiva requiere `requires_write=true`
- prototipos no reciben acceso backend por defecto
- exports y scripts respetan límites del workspace
- browser automation no puede aprobar acciones destructivas reales

## 21. Criterios de aceptación

El harness está implementado sólo si:

- el selector elige `ui-ux-delivery` para routing cases positivos
- no lo elige para casos backend negativos
- el RunBundle gobierna la ejecución real
- las skills requeridas se resuelven con lineage o fallan explícitamente
- los stages producen estados y evidencia
- producción exige UI verification
- review y recovery son observables
- el envelope se persiste y puede reanudarse
- tests unitarios, integración y behavioral routing pasan

## 22. Estado de implementación

### Disponible hoy

- skills externas instaladas
- runtime genérico de selección/composición
- generic verification/recovery primitives
- UI doctrine y UI Design brain
- adapter interactivo `ui-ux-routing`

### Pendiente

- package `ui-ux-delivery`
- package `ui-ux-verifier`
- ObjectiveProfile UI/UX
- InstalledSkillResolver
- routing condicional por delivery mode
- integración con `run-bundle-stage-executor`
- stage state machine
- UI verification evidence
- persistence integration
- behavioral and integration tests

## 23. Referencias

- `docs/canonical/22-ENGINEERING-DOCTRINE-LAYER.md`
- `docs/canonical/67-HARNESS-SELECTION-POLICY.md`
- `docs/canonical/71-HARNESS-RUNTIME-CONTRACT.md`
- `docs/canonical/103-MULTI-HARNESS-COMPOSITION-AND-AGENT-HARNESSES-COMPLIANCE.md`
- `docs/canonical/113-HARNESS-STAGE-EXECUTION-RUNTIME-CONTRACT.md`
- `docs/canonical/decision-records/DR-009-UI-UX-AS-RUNTIME-HARNESS.md`
- `.planning/changes/ui-ux-harness-runtime/`

## Key Learnings:

1. Una skill enruta conocimiento; un harness controla ejecución y evidencia.
2. La UI productiva no está terminada hasta verificar el resultado renderizado.
3. UI/UX consume el stage executor compartido; no implementa un runtime paralelo.
