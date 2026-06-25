# Business Logic Model — UOW-5 verification-review-recovery-v1

## Purpose

Definir cómo el runtime stateless convierte el control seleccionado en loops
útiles de:

- `VerificationHarness`
- `ReviewHarness`
- `RecoveryHarness`

sin romper el principio de minimum sufficient control.

## Core Workflow

1. **Ejecución base**
   - `StatelessCoordinator` ejecuta el flow principal como hoy.
   - El resultado base produce artifacts y contexto suficiente para verificación.

2. **Verificación condicional**
   - Si `LoopPolicy.requires_verification = true`, el runtime invoca
     `VerificationHarness`.
   - El harness ejecuta checks determinísticos sobre:
     - artifacts presentes
     - shape del output
     - envelope inicial
     - criterios mínimos de aceptación
   - El output es un `VerificationOutcome`.

3. **Review condicional**
   - Si `LoopPolicy.requires_review = true`, el runtime invoca `ReviewHarness`.
   - El review MVP no depende de red ni de otro modelo.
   - El harness aplica una rubric local/adversarial mínima:
     - ¿hay artifacts suficientes?
     - ¿la verificación pasó?
     - ¿hay riesgos pendientes?
     - ¿el maker intenta autoaprobarse sin evidencia suficiente?
   - El output es un `ReviewOutcome`.

4. **Síntesis de outcome**
   - El runtime fusiona:
     - resultado base
     - verification outcome
     - review outcome
   - Se actualiza `ExecutionEnvelope` con evidencia, riesgos y next actions.

5. **Recovery condicional**
   - Si verification o review fallan, o si la ejecución base produce fallo,
     el runtime invoca `RecoveryHarness`.
   - Recovery no ejecuta trabajo por sí solo; decide el siguiente paso bounded.

6. **Decisión bounded**
   - `RecoveryHarness` solo puede devolver:
     - `retry`
     - `patch`
     - `replan`
     - `escalate`
     - `stop`
   - La decisión depende de:
     - failure class
     - retryability
     - attempt count
     - progreso observable

## Verification Logic

### Deterministic checks MVP

- artifacts no vacíos cuando la tarea lo exige
- envelope válido
- status coherente con verification/recovery fields
- acceptance criteria mínimas satisfechas

### Success boundary

`VerificationHarness` no decide rollout ni approval humana; solo decide si la
salida cumple checks mínimos suficientes.

## Review Logic

### Maker-checker MVP

El review MVP simula checker separado usando rubric independiente, no usando
más generación creativa ni network fresh-context obligatorio.

### Review questions implicit in rubric

- ¿hay evidencia suficiente?
- ¿hay riesgo pendiente no mitigado?
- ¿la verificación fue omitida cuando era requerida?
- ¿el envelope pide acciones antes de aceptar?

## Recovery Logic

### Recovery ladder

1. `retry`
   - si el fallo es transitorio o incompleto
2. `patch`
   - si la salida existe pero requiere corrección local acotada
3. `replan`
   - si el approach elegido no sirve
4. `escalate`
   - si el riesgo o la incertidumbre exceden el MVP
5. `stop`
   - si no hay progreso o seguir sería desperdicio

### No-progress detection

Hay no-progreso cuando:

- se repite misma failure class
- el attempt count supera el límite
- no cambia ni artifacts ni verification verdict útil

## Boundaries

- `VerificationHarness` valida; no repara
- `ReviewHarness` juzga evidencia/riesgo; no ejecuta
- `RecoveryHarness` decide siguiente paso; no hace auto-healing abierto
- `StatelessCoordinator` orquesta el orden; no redefine las reglas
