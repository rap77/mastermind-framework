# Unit Test Execution — UOW-5 verification-review-recovery-v1

## Run Unit Tests

### 1. Execute Focused UOW-5 Tests

```bash
cd apps/api
UV_CACHE_DIR=/tmp/uv-cache uv run python -m pytest \
  tests/unit/test_runtime_contracts.py \
  tests/unit/test_runtime_contracts_verification.py \
  tests/unit/test_runtime_contracts_review.py \
  tests/unit/test_runtime_contracts_recovery.py \
  tests/unit/test_stateless_coordinator.py -q
```

### 2. Expected Results

- **Expected**: `36 passed`
- **Critical Assertions**:
  - `LoopSelector` clasifica tareas y elige control mínimo suficiente
  - `CapabilityRegistry` / `HarnessRegistry` filtran determinísticamente
  - `ExecutionEnvelope` valida shape estable
  - `VerificationHarness` falla en artifacts faltantes o payload incompleto
  - `ReviewHarness` aplica maker-checker local y bloquea cuando verification falla
  - `RecoveryHarness` decide retry/patch/replan/escalate de forma bounded
  - `StatelessCoordinator` expone `runtime_task_profile`,
    `runtime_loop_policy`, `runtime_envelope`,
    `runtime_verification_outcome`, `runtime_review_outcome`,
    `runtime_recovery_decision`
  - `message_log[*].transport_metadata["runtime_contracts"]` queda poblado

### 3. Optional Narrow Test Loops

```bash
cd apps/api
UV_CACHE_DIR=/tmp/uv-cache uv run python -m pytest tests/unit/test_runtime_contracts.py -q
UV_CACHE_DIR=/tmp/uv-cache uv run python -m pytest tests/unit/test_runtime_contracts_verification.py -q
UV_CACHE_DIR=/tmp/uv-cache uv run python -m pytest tests/unit/test_runtime_contracts_review.py -q
UV_CACHE_DIR=/tmp/uv-cache uv run python -m pytest tests/unit/test_runtime_contracts_recovery.py -q
UV_CACHE_DIR=/tmp/uv-cache uv run python -m pytest tests/unit/test_stateless_coordinator.py -q
```

### 4. Review Test Results

- **Coverage Target**: foco funcional sobre runtime contracts y coordinator seam
- **Relevant Files**:
  - `tests/unit/test_runtime_contracts.py`
  - `tests/unit/test_runtime_contracts_verification.py`
  - `tests/unit/test_runtime_contracts_review.py`
  - `tests/unit/test_runtime_contracts_recovery.py`
  - `tests/unit/test_stateless_coordinator.py`

### 5. Fix Failing Tests

Si fallan:
1. revisar mismatch entre clasificación esperada y heurística actual
2. revisar `transport_metadata["runtime_contracts"]`
3. revisar validez de `ExecutionEnvelope`
4. revisar gates de verification/review y decisión de recovery
5. reejecutar hasta volver a verde
