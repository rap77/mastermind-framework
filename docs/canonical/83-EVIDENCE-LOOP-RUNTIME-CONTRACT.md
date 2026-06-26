# Evidence Loop Runtime Contract

## 1. Propósito

Definir el contrato de ejecución del loop que ingiere evidencia, detecta gaps, hace entrevistas al usuario, verifica readiness y entrega el handoff a especificación.

## 2. Tesis central

El loop debe ser explícito, repetible y auditable. Cada paso produce una salida pequeña y verificable.

## 3. Estados del loop

- `idle`
- `intaking`
- `canonizing`
- `detecting_gaps`
- `clarifying`
- `verifying`
- `ready`
- `blocked`
- `archived`

## 4. Entrada mínima

```text
objective
source_refs
current_snapshot
known_constraints
confidence_threshold
token_budget
user_context
existing_canon
```

## 5. Salida mínima

```text
status
summary
canonical_blocks
gaps
questions
answers
readiness_verdict
readiness_score
readiness_gate
risks
next_actions
memory_writes
registry_updates
source_updates
token_usage
elapsed_ms
```

## 6. Flujo de ejecución

### 6.1 Intake

Capturar o referenciar la evidencia.

### 6.2 Canonize

Extraer bloques canónicos pequeños y trazables.

### 6.3 Detect gaps

Comparar cobertura contra lo necesario para especificar.

### 6.4 Clarify

Si faltan datos, preguntar al usuario.

### 6.5 Verify readiness

Decidir si ya se puede pasar a especificación usando verdict + score + gate.

### 6.6 Archive

Persistir decisión, deltas y aprendizajes.

## 7. Reglas de transición

- no pasar a `verifying` si quedan gaps críticos sin resolver
- no pasar a `ready` si faltan fuentes o respuestas esenciales
- no pasar a `blocked` salvo que no haya forma razonable de avanzar
- no pasar a `archived` sin trazabilidad durable

## 8. Observabilidad

Cada ciclo debe registrar:

- fuente usada
- bloques creados
- gaps abiertos/cerrados
- preguntas emitidas
- respuestas recibidas
- estado final

## 9. Relación con otros harnesses

Este contrato conecta:

- Evidence Intake Harness
- Gap Detection Loop
- Spec Readiness Verification Harness
- AI-DLC Discovery/Requirements

## 10. No-goals

- no ejecutar sin estado explícito
- no ocultar preguntas dentro de notas vagas
- no mezclar output de canon con output de spec
