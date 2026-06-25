# Security Test Instructions — UOW-5 verification-review-recovery-v1

## Purpose

Verificar que el slice preserve bounded control, maker-checker foundations,
restrictive final verdict synthesis y fail-closed behavior.

## Security Checks

### 1. Governance Precedence Still Holds

```bash
cd apps/api
UV_CACHE_DIR=/tmp/uv-cache uv run python -m pytest \
  tests/unit/test_stateless_coordinator.py::test_coordinator_blocks_when_governance_denies -q
```

**Expected**:
- resultado vacío
- sin ejecución de brains
- sin continuación permisiva

### 2. No Open Loop Defaults

Revisar en código:
- `max_iterations=1` para camino simple
- `max_iterations` bounded para caminos medios/complejos
- no loops sin límite explícito

Archivos:
- `mastermind_cli/orchestrator/runtime_contracts/loop_selector.py`

### 3. Envelope Contract Validation

```bash
cd apps/api
UV_CACHE_DIR=/tmp/uv-cache uv run python -m pytest \
  tests/unit/test_runtime_contracts.py::test_execution_envelope_validates_success_shape \
  tests/unit/test_runtime_contracts.py::test_synthesize_execution_envelope_uses_most_restrictive_verdict -q
```

**Expected**:
- envelope válido
- verdict final más restrictivo cuando verification/review/recovery discrepan
- shape estructurado disponible para decisiones futuras

### 4. Maker-Checker Review Gate

```bash
cd apps/api
UV_CACHE_DIR=/tmp/uv-cache uv run python -m pytest \
  tests/unit/test_runtime_contracts_review.py::test_review_harness_blocks_when_verification_failed -q
```

**Expected**:
- review no aprueba si verification ya falló
- no promoción accidental de un verdict fallido

### 5. Static Lint Check

```bash
rtk ruff check apps/api/mastermind_cli/orchestrator/runtime_contracts \
  apps/api/mastermind_cli/orchestrator/stateless_coordinator.py \
  apps/api/tests/unit/test_runtime_contracts.py \
  apps/api/tests/unit/test_runtime_contracts_verification.py \
  apps/api/tests/unit/test_runtime_contracts_review.py \
  apps/api/tests/unit/test_runtime_contracts_recovery.py \
  apps/api/tests/unit/test_stateless_coordinator.py
```

## Review Focus

- no network obligatorio agregado por default
- no write path nuevo
- no bypass de governance
- no verdict final permisivo si algún harness falla
- metadata runtime no debe incluir secretos
