# AI-DLC Harness Spec

## 1. Propósito

Definir AI-DLC como un harness formal de MasterMind para discovery, requirements, design, construction, verification y archive.

## 2. Tesis central

> AI-DLC no es la arquitectura total de MasterMind. Es un harness potente para estructurar trabajo cuando el objetivo requiere trazabilidad, faseamiento y cierre verificable.

## 3. Alcance

AI-DLC debe poder usarse cuando:

- hay que descubrir contexto
- hay que analizar requisitos
- hay que diseñar el enfoque
- hay que ejecutar construcción por slices
- hay que verificar resultados
- hay que archivar el aprendizaje

AI-DLC no debe usarse por default cuando:

- la tarea es trivial
- el cambio es aislado
- un Tool Loop basta
- el overhead del harness supera el beneficio

## 4. Fases del harness

### 4.1 Discovery

Objetivo:

- entender problema
- entender restricciones
- entender contexto

Salidas:

- summary
- open questions
- scope boundary
- source candidates

### 4.2 Requirements

Objetivo:

- convertir contexto en requisitos claros
- separar lo esencial de lo opcional

Salidas:

- functional requirements
- non-functional requirements
- constraints
- success criteria

### 4.3 Design

Objetivo:

- convertir requisitos en arquitectura y contratos

Salidas:

- component map
- harness mapping
- loop mapping
- registry impacts
- memory impacts

### 4.4 Construction

Objetivo:

- implementar slices
- mantener el alcance controlado

Salidas:

- code changes
- tests
- commit-ready artifacts
- notes for recovery/review

### 4.5 Verification

Objetivo:

- comprobar que el trabajo cumple lo prometido

Salidas:

- pass/fail verdict
- evidence
- gaps
- rework recommendations

### 4.6 Archive

Objetivo:

- preservar el resultado para reuso futuro

Salidas:

- canonical doc updates
- memory writes
- source deltas
- lessons learned

## 5. AI-DLC inputs

El harness debe aceptar:

- objective
- project_id
- scope
- phase
- budget
- approval state
- source refs
- memory hints
- constraints
- current artifacts

## 6. AI-DLC outputs

El harness debe devolver:

- status
- summary
- artifacts
- risks
- next_actions
- verification
- recovery
- memory_writes
- registry_updates
- source_updates

## 7. Loop mapping

AI-DLC puede usar:

- Discovery Loop
- Goal Loop
- Verification Loop
- Reflection Loop
- Review Loop
- Recovery Loop

## 8. Sub-harness behavior

AI-DLC puede delegar a sub-harnesses internos:

- Discovery Harness
- Research Harness
- Design Harness
- Implementation Harness
- Verification Harness
- Archive Harness

## 9. Selection criteria

El selector debe elegir AI-DLC cuando:

- el trabajo tiene varias fases
- la trazabilidad importa
- hay necesidad de documentar decisiones
- se requiere una transición clara de discovery a build
- hay múltiples dependencias o slices

## 10. Memory behavior

AI-DLC debe guardar:

- decisions
- requirements
- summaries
- checkpoints
- source deltas
- final archive notes

## 11. Registry behavior

AI-DLC debe registrar:

- harness usage
- loop usage
- capability usage
- selected brain(s)
- outcome

## 12. Source behavior

Si AI-DLC usa fuentes externas, debe registrar:

- source refs
- snapshot refs
- adoption decisions
- anti-pattern notes

## 13. Token policy

AI-DLC debe operar con:

- summary-first prompts
- top-k retrieval
- small context bundles
- explicit stop points

## 14. Failure modes

- si falta contexto, volver a Discovery
- si no hay requisitos claros, pausar
- si la verificación falla, activar Recovery
- si el trabajo queda ambiguo, pedir más información

## 15. No-goals

- no convertir AI-DLC en único workflow obligatorio
- no saltar fases sin razón
- no guardar todo el output crudo como memoria durable
- no sustituir el selector con preferencias manuales

## 16. Relación con los demás docs

- `63-MASTERMIND-CORE-ARCHITECTURE.md`
- `64-HARNESS-LIBRARY-AND-LOOP-TAXONOMY.md`
- `67-HARNESS-SELECTION-POLICY.md`
- `71-HARNESS-RUNTIME-CONTRACT.md`
- `73-HARNESS-SELECTOR-SERVICE.md`
