# Domain Entities — UOW-5 verification-review-recovery-v1

## 1. VerificationCheck

### Description
Check determinístico individual ejecutado por `VerificationHarness`.

### Fields
- `check_id`
- `label`
- `passed`
- `reason`

## 2. VerificationOutcome

### Description
Resultado agregado de verificación.

### Fields
- `performed`
- `passed`
- `checks`
- `acceptance_criteria_satisfied`
- `evidence_refs`

## 3. ReviewRubric

### Description
Rubric mínima usada por `ReviewHarness`.

### Fields
- `rubric_id`
- `criteria`
- `requires_verification_pass`
- `blocks_self_approval`

## 4. ReviewOutcome

### Description
Resultado agregado de review.

### Fields
- `performed`
- `approved`
- `findings`
- `risk_flags`
- `recommended_next_action`

## 5. FailureRecord

### Description
Representación normalizada de un fallo recuperable o terminal.

### Fields
- `failure_class`
- `reason`
- `attempt_count`
- `retryable`
- `previous_action`

## 6. RecoveryDecision

### Description
Decisión bounded devuelta por `RecoveryHarness`.

### Fields
- `action`
- `reason`
- `updated_loop_policy`
- `escalate_to_human`

## Relationships

- `VerificationOutcome` puede alimentar `ReviewOutcome`
- `ReviewOutcome` y `VerificationOutcome` pueden derivar `FailureRecord`
- `FailureRecord` alimenta `RecoveryDecision`
- `RecoveryDecision` actualiza `ExecutionEnvelope.recovery`
