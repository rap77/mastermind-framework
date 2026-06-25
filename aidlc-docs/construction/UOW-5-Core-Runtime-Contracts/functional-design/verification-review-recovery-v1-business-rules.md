# Business Rules — UOW-5 verification-review-recovery-v1

## Rule Group 1 — Verification

### BR-5.V1
Si `LoopPolicy.requires_verification = true`, debe existir outcome explícito de
verificación en el envelope final.

### BR-5.V2
La verificación MVP debe ser determinística y local; no debe depender de red
como precondición.

### BR-5.V3
Un artifact faltante en tarea que lo exige debe marcar verificación fallida.

## Rule Group 2 — Review

### BR-5.R1
Si `LoopPolicy.requires_review = true`, el maker no puede considerarse
aceptado solo con su propio output base.

### BR-5.R2
El review MVP puede ser local, pero debe usar rubric separada del flujo de
ejecución base.

### BR-5.R3
Si la verificación falló, el review no puede aprobar plenamente la tarea.

## Rule Group 3 — Recovery

### BR-5.RE1
Todo fallo elegible para recovery debe producir `RecoveryDecision` explícita.

### BR-5.RE2
La recovery ladder permitida es:
1. retry
2. patch
3. replan
4. escalate
5. stop

### BR-5.RE3
No se puede repetir indefinidamente la misma action sobre la misma failure
class.

### BR-5.RE4
Si el attempt count supera el límite del loop, recovery debe escalar o detener.

## Rule Group 4 — Envelope Final

### BR-5.E1
El envelope final debe reflejar outcomes de verification/review/recovery cuando
apliquen.

### BR-5.E2
`next_actions` debe ser consistente con el verdict más restrictivo disponible.

### BR-5.E3
Un review pendiente o fallido no debe traducirse a `success` silencioso.

## Rule Group 5 — Cost Control

### BR-5.C1
Tareas simples con `requires_verification = false` y `requires_review = false`
no deben pagar costo adicional de estos harnesses.

### BR-5.C2
El activation path de verification/review/recovery debe depender solo de
`LoopPolicy` y outcomes previos, no de heurística emergente posterior.
