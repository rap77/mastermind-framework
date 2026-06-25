# Integration Test Instructions — UOW-5 verification-review-recovery-v1

## Purpose

Verificar que verification/review/recovery convive con el runtime actual sin
romper orchestración stateless ni governance fail-closed.

## Test Scenarios

### Scenario 1: Verification / Review / Recovery → Stateless Coordinator
- **Description**: el coordinador sintetiza `ExecutionEnvelope` final usando
  verification, review y recovery cuando el task profile lo requiere.
- **Setup**: entorno `apps/api` con dev dependencies instaladas.
- **Test Steps**:
  1. ejecutar `tests/unit/test_stateless_coordinator.py`
  2. confirmar presencia de `runtime_task_profile`, `runtime_loop_policy`,
     `runtime_verification_outcome`, `runtime_review_outcome`,
     `runtime_recovery_decision`, `runtime_envelope`
  3. confirmar metadata en `message_log`
- **Expected Results**:
  - flow existente sigue funcionando
  - outcomes intermedios quedan expuestos
  - envelope final usa el verdict más restrictivo

### Scenario 2: Governance Block → Stateless Coordinator
- **Description**: governance deny debe seguir devolviendo `{}` sin side effects
  de runtime contracts.
- **Setup**: usar `BlockingGovernance` test double.
- **Test Steps**:
  1. ejecutar test `test_coordinator_blocks_when_governance_denies`
  2. verificar que no haya resultados ni envelope final
- **Expected Results**:
  - comportamiento fail-closed preservado

### Scenario 3: Failing Verification / Review → Bounded Recovery
- **Description**: una falla de verification o review debe disparar decisión de
  recovery bounded, no loop abierto.
- **Setup**: suites de recovery + coordinator.
- **Test Steps**:
  1. ejecutar `tests/unit/test_runtime_contracts_recovery.py`
  2. revisar `test_coordinator_records_recovery_for_failed_verification`
  3. revisar límite por `max_iterations`
- **Expected Results**:
  - `retry`, `patch`, `replan` o `escalate` salen determinísticamente
  - sin loop abierto

### Scenario 4: Existing Brain Execution Still Green
- **Description**: la nueva capa no debe romper Brain #1 y aliases RAG ya
  cubiertos.
- **Setup**: suite de `test_stateless_coordinator.py`
- **Test Steps**:
  1. correr suite completa enfocada
  2. revisar tests RAG alias y multi-user safety
- **Expected Results**:
  - todos verdes
  - sin regresión en paths previos

## Run Integration Validation

```bash
cd apps/api
UV_CACHE_DIR=/tmp/uv-cache uv run python -m pytest tests/unit/test_stateless_coordinator.py -q
UV_CACHE_DIR=/tmp/uv-cache uv run python -m pytest tests/unit/test_runtime_contracts_recovery.py -q
```

## Verify Service Interactions

- `LoopSelector` decide antes de `_resolve_waves()`
- `BrainEnvelope.transport_metadata` incorpora runtime contract context
- `build_execution_envelope()` corre después de `results.update(...)`
- `synthesize_execution_envelope()` resuelve el verdict final más restrictivo

## Cleanup

```bash
unset UV_CACHE_DIR
```
