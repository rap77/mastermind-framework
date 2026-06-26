# Harness Runtime Contract

## 1. Propósito

Definir el contrato común que todo harness de MasterMind debe cumplir para que el orquestador pueda ejecutarlo, verificarlo, recuperarlo y archivarlo de forma uniforme.

## 2. Tesis central

> Si todos los harnesses hablan el mismo contrato, el orquestador puede cambiar de workflow sin cambiar de mentalidad.

## 3. Contract shape

Todo harness debe aceptar una request estructurada y devolver un envelope estructurado.

### 3.1 Harness Request

Campos conceptuales:

- `request_id`
- `harness_key`
- `objective`
- `scope`
- `project_id`
- `phase_id`
- `brain_id`
- `loop_hint`
- `context_refs`
- `constraints`
- `token_budget`
- `risk_level`
- `approval_state`
- `memory_hints`
- `source_refs`

### 3.2 Harness Envelope

Campos conceptuales:

- `status`
- `summary`
- `artifacts`
- `risks`
- `next_actions`
- `verification`
- `recovery`
- `memory_writes`
- `registry_updates`
- `source_updates`
- `token_usage`
- `elapsed_ms`

## 4. Status model

Valores mínimos:

- `success`
- `partial`
- `blocked`
- `needs_review`
- `needs_recovery`
- `failed`
- `archived`

## 5. Artifact model

Cada harness debe poder devolver referencias a artefactos, no solo texto.

### Artifact fields

- `artifact_id`
- `artifact_type`
- `title`
- `location`
- `summary`
- `source_ref`
- `version`
- `created_at`

## 6. Verification model

El envelope debe incluir una verificación explícita:

- qué se verificó
- cómo se verificó
- qué pasó
- qué faltó
- si requiere checker separado

## 7. Recovery model

El envelope debe incluir recuperación explícita cuando aplique:

- retry suggestion
- rollback suggestion
- replan suggestion
- escalation suggestion

## 8. Memory writes

Todo harness debe declarar qué escribe en memoria:

- decision
- learning
- preference
- checkpoint
- source adoption
- summary

## 9. Registry updates

Todo harness debe declarar si actualiza:

- capability registry
- harness usage stats
- loop selection history
- policy state

## 10. Source updates

Todo harness debe declarar si agrega:

- source snapshot
- delta notes
- adoption decision
- anti-pattern note

## 11. Token rules

El harness debe respetar:

- token_budget de entrada
- token_budget de salida
- summary-first output
- top-k context projection

## 12. MCP rules

Si un harness usa MCP:

- debe declarar qué server/tool consume
- debe declarar si es read-only o write-enabled
- debe pasar por policy check

## 13. Loop compatibility

El harness debe declarar qué loops soporta:

- Tool Loop
- Goal Loop
- Verification Loop
- Reflection Loop
- Recovery Loop
- Review Loop
- Heartbeat Loop

## 14. Execution phases

Un harness puede pasar por estas fases:

1. intake
2. context projection
3. execution
4. verification
5. recovery or review if needed
6. archive

## 15. Selection interoperability

El selector de harness debe poder leer:

- status
- risks
- token usage
- elapsed time
- verification outcome

## 16. No-goals

- no devolver solo prosa libre
- no omitir verification/recovery cuando aplican
- no mutar memoria sin declararlo
- no esconder uso de MCP
- no esconder costos

## 17. Relación con los demás docs

- `63-MASTERMIND-CORE-ARCHITECTURE.md`
- `64-HARNESS-LIBRARY-AND-LOOP-TAXONOMY.md`
- `65-MEMORY-AND-CONTEXT-ARCHITECTURE.md`
- `67-HARNESS-SELECTION-POLICY.md`
- `68-CAPABILITY-REGISTRY-SPEC.md`
- `70-MEMORY-SCHEMA.md`
