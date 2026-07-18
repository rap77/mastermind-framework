# Design — ui-ux-harness-runtime

## Architecture / Boundaries

El objective extiende el runtime multi-harness existente. No crea un runtime
paralelo.

```text
PlanningBridge
  -> UI/UX profile classification
  -> MultiHarnessSelector
  -> RunBundleComposer
  -> RunBundleStageExecutor
  -> UI/UX stage runner
  -> UI/UX verifier
  -> recovery when required
  -> ExecutionEnvelope
  -> project state + planning + memory
```

Boundaries:

- planning conserva objective, scope y task state
- harness library define packages y capability routing
- orchestrator ejecuta stages y produce envelopes
- project state persiste estructura y lineage
- memory conserva decisions, learnings y checkpoints
- browser tooling aporta evidencia, no autoridad de negocio
- skills externas no pueden sobrescribir project policy

## Technical Approach

### 1. Profile contract

Extender `ObjectiveProfile` con un `delivery_mode` opcional y normalizar UI/UX
como `domain: ui-ux`. Mantener compatibilidad para perfiles existentes.

Valores UI/UX:

| Phase | Output type | Delivery mode |
| --- | --- | --- |
| planning | `ui-spec` | `design-system` |
| implementation | `prototype` | `prototype` |
| implementation | `ui-artifact` | `production-implementation` |
| verification | `ui-verdict` | `review` |
| verification | `motion-plan` | `motion-audit` |

La inferencia debe vivir en una función pura y testeable. Señales explícitas de
planning tienen prioridad sobre texto libre.

### 2. Harness packages

Crear:

```text
.mm-flow/harness-library/roles/ui-ux-delivery/
  HARNESS.md
  .leaf-detectors

.mm-flow/harness-library/verification/ui-ux-verifier/
  HARNESS.md
  .leaf-detectors

.mm-flow/harness-library/references/ui-ux-delivery.md
.mm-flow/harness-library/references/ui-ux-verification.md
```

`ui-ux-delivery` es primary role. `ui-ux-verifier` es supporting verification.
`recovery-fixer` sigue siendo recovery compartido.

### 3. Conditional skill routing

Agregar al catalog un contrato genérico de `skill_routes`:

```yaml
skill_routes:
  - when:
      delivery_modes: [production-implementation]
    skills: [frontend-design, web-design-guidelines]
  - when:
      delivery_modes: [prototype]
    skills: [huashu-design]
```

El selector resuelve baseline skills más conditional skills preservando orden y
eliminando duplicados.

### 4. Installed skill resolver

Introducir un resolver independiente del selector:

```text
skill ID
-> configured roots
-> project override
-> global candidates
-> metadata validation
-> content hash
-> resolved source
```

No modificar skills globales compartidas. Project policy neutraliza assumptions
incompatibles, como el supuesto React Native presente en la copia instalada de
`ui-ux-pro-max`.

### 5. RunBundle stage execution

Consumir `run-bundle-stage-executor` desde
`harness-stage-execution-runtime`. UI/UX materializa sus stage definitions,
capabilities y gates; no implementa scheduling, checkpoint ni recovery routing
genéricos.

Contrato mínimo:

```python
execute(bundle, request, context) -> HarnessStageRunResult
```

No basta con adjuntar `multi_harness_result` al resultado final.

### 6. Stage runner

Stages canónicos:

1. intake
2. context_projection
3. ux_contract
4. design_direction
5. prototype_or_spec
6. production_implementation
7. runtime_verification
8. independent_review
9. recovery
10. handoff_persistence

Cada stage devuelve:

- status
- summary
- artifacts
- evidence
- risks
- next action
- skip reason cuando aplica

### 7. Verification

`ui-ux-verifier` resuelve checks por delivery mode y herramientas disponibles.

Checks obligatorios de producción:

- responsive desktop/mobile
- keyboard/focus
- semantics/labels
- console errors
- edge states
- overflow/content extremes
- reduced motion cuando aplica
- acceptance criteria

La ausencia de browser tooling produce `warning` o `blocked` según criterio, no
un pass falso.

### 8. Review

Maker-checker se activa por:

- risk high/critical
- navegación primaria
- tokens globales
- accessibility crítica
- motion significativo
- acceptance subjetiva

Review source y runtime evidence permanecen separados.

### 9. Recovery

Usar el recovery ladder existente:

- retry local una vez
- patch acotado
- replan estructural
- escalate por ambigüedad
- blocked por capability ausente

### 10. Persistence

Persistir:

- composition plan
- selected skill source/hash
- stage transitions
- artifacts y links
- verification evidence
- review findings
- recovery decision
- checkpoint y next action

No persistir secretos ni payloads de browser sensibles.

## Dependencies

- `docs/canonical/22-ENGINEERING-DOCTRINE-LAYER.md`
- `docs/canonical/67-HARNESS-SELECTION-POLICY.md`
- `docs/canonical/71-HARNESS-RUNTIME-CONTRACT.md`
- `docs/canonical/103-MULTI-HARNESS-COMPOSITION-AND-AGENT-HARNESSES-COMPLIANCE.md`
- `docs/canonical/110-UI-UX-HARNESS-RUNTIME-CONTRACT.md`
- `docs/canonical/113-HARNESS-STAGE-EXECUTION-RUNTIME-CONTRACT.md`
- existing `MultiHarnessPipeline`, `HarnessCore` and `HarnessRunExecutor`
- existing project-state artifact/checkpoint/memory adapters

Roadmap dependencies:

- `engineering-doctrine-layer`
- `artifact-versioning-and-lineage`
- `harness-stage-execution-runtime`

Las dos primeras están completadas. La foundation de stage execution permanece
planificada y debe completarse antes de activar UI/UX.

## Validation Strategy

### Unit

- profile classification
- conditional skill selection
- installed skill resolution
- stage transition rules
- UI verifier check resolution
- recovery decisions

### Behavioral routing

- design system positive case
- prototype positive case
- production UI positive case
- review and motion positive cases
- backend and incidental-text negative cases

### Integration

- planning request -> bundle -> stage execution -> envelope
- missing skill -> explicit blocked result
- failed UI check -> recovery decision
- passed run -> persisted checkpoint and lineage

### Regression

- existing product/software harness routing remains unchanged
- existing harness executor tests remain green
- generic acceptance/recovery paths remain compatible

### Commands

- `cd apps/api && uv run pytest -q tests/unit/test_multi_harness_selector.py`
- `cd apps/api && uv run pytest -q tests/unit/test_harness_run_executor.py`
- `cd apps/api && uv run pytest -q tests/unit/test_ui_ux_harness.py`
- `cd apps/api && uv run pytest -q tests/integration/test_ui_ux_harness_runtime.py`
- `cd apps/api && uv run ruff check mastermind_cli tests`

No build command forma parte de este objective bajo la política actual.

## Important Tradeoffs

### One role harness vs. many UI roles

Se elige un Role Harness con delivery modes para evitar fragmentar selection.
Si los modes divergen demasiado, podrán separarse con evidencia posterior.

### External skills vs. vendoring

Se elige resolver por ID y hash. Vendoring evitaría missing dependencies, pero
duplicaría contenido, licencias y actualización.

### Browser verification required vs. universally available

Se exige evidencia para producción, pero se modela tooling unavailable como un
estado explícito. No se falsifica aprobación.

### Shared runtime dependency

Bundle-to-execution wiring es genérico y beneficia otros harnesses. Se extrae a
un objective foundation para evitar que UI/UX sea dueño accidental del runtime.

## Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| keyword false positives | high | explicit profile signals plus negative routing cases |
| skill prompt conflicts | high | precedence and project policy enforcement |
| missing global skill | medium | InstalledSkillResolver fails loudly |
| context bloat | medium | conditional skill routes and budget assertions |
| fake verification pass | high | unperformed checks never pass |
| UI-specific coupling in core | high | generic stage/result interfaces |
| non-deterministic visual judgment | medium | separate deterministic checks from maker-checker review |

## Context Notes

- `.opencode/skills/ui-ux-routing/` is an interactive adapter only.
- `docs/canonical/decision-records/DR-009-UI-UX-AS-RUNTIME-HARNESS.md`
  records the architectural decision.
- This objective is planned but not active; `multi-channel-gateway` remains the
  current active objective until explicit activation.
