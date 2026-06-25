# Logical Components — UOW-5 verification-review-recovery-v1

## Purpose

Definir los componentes lógicos mínimos para materializar verification, review
y recovery sobre el runtime stateless actual.

## 1. VerificationHarness

### Responsibility
Ejecutar checks determinísticos sobre artifacts, envelope base y criterios
mínimos de aceptación.

### Inputs
- base execution envelope
- acceptance hints
- selected verifier capabilities

### Outputs
- `VerificationOutcome`

## 2. VerificationCheckSet

### Responsibility
Agrupar los checks concretos que se aplican en el MVP.

### Inputs
- task profile
- base envelope

### Outputs
- list de `VerificationCheck`

## 3. ReviewHarness

### Responsibility
Aplicar rubric de maker-checker local sobre evidencia ya disponible.

### Inputs
- base envelope
- verification outcome
- review rubric

### Outputs
- `ReviewOutcome`

## 4. ReviewRubricResolver

### Responsibility
Resolver la rubric mínima apropiada según `TaskProfile` y `LoopPolicy`.

### Inputs
- task profile
- loop policy

### Outputs
- `ReviewRubric`

## 5. FailureClassifier

### Responsibility
Normalizar fallos de ejecución/verificación/review a `FailureRecord`.

### Inputs
- base envelope
- verification outcome
- review outcome
- previous recovery state

### Outputs
- `FailureRecord | None`

## 6. RecoveryHarness

### Responsibility
Decidir la siguiente acción bounded.

### Inputs
- failure record
- loop policy

### Outputs
- `RecoveryDecision`

## 7. FinalEnvelopeSynthesizer

### Responsibility
Fusionar execution + verification + review + recovery en un envelope final
consistente.

### Inputs
- base envelope
- verification outcome
- review outcome
- recovery decision

### Outputs
- final `ExecutionEnvelope`

## 8. RuntimeControlOrchestrator

### Responsibility
Coordinar el orden:
1. verification
2. review
3. failure classification
4. recovery
5. final envelope synthesis

### Inputs
- task profile
- loop policy
- base envelope

### Outputs
- final envelope

## MVP Boundary

- sin servicios remotos obligatorios
- sin executor autónomo de recovery
- sin reviewer LLM mandatory
- sí con decision logic explícita y outcomes tipados
