# Performance Test Instructions — UOW-5 verification-review-recovery-v1

## Purpose

Validar que verification/review/recovery agregue overhead pequeño y bounded al
coordinador stateless.

## Performance Requirements

- **Selection Cost**: clasificación + selección deben ser locales, sin red
- **Harness Cost**: verification/review/recovery deben ser locales y baratos
- **Overhead Shape**: O(n) respecto al inventario local pequeño del MVP
- **Failure Mode**: degradación segura, no fan-out adicional

## Lightweight Validation Strategy

Este slice no requiere un harness de carga dedicado todavía. Validación mínima:

### 1. Measure Focused Test Runtime

```bash
cd apps/api
time UV_CACHE_DIR=/tmp/uv-cache uv run python -m pytest \
  tests/unit/test_runtime_contracts.py \
  tests/unit/test_runtime_contracts_verification.py \
  tests/unit/test_runtime_contracts_review.py \
  tests/unit/test_runtime_contracts_recovery.py \
  tests/unit/test_stateless_coordinator.py -q
```

### 2. Compare Against Future Regressions

- guardar el tiempo observado en notas de PR o commit
- vigilar crecimiento abrupto al expandir inventario/loops

### 3. Manual Micro-Checks

```bash
cd apps/api
UV_CACHE_DIR=/tmp/uv-cache uv run python - <<'PY'
from mastermind_cli.types.interfaces import Brief
from mastermind_cli.orchestrator.runtime_contracts import LoopSelector, CapabilityRegistry
selector = LoopSelector()
profile = selector.classify_task(Brief(problem_statement="Build a CRM for small businesses"), ["brain-01-product-strategy"])
caps = CapabilityRegistry().resolve_for_task(profile)
policy = selector.select_loop(profile, caps)
print(profile.complexity, policy.base_loop)
PY
```

```bash
cd apps/api
UV_CACHE_DIR=/tmp/uv-cache uv run python - <<'PY'
from mastermind_cli.orchestrator.runtime_contracts import (
    build_execution_envelope,
    VerificationHarness,
    ReviewHarness,
    RecoveryHarness,
)
envelope = build_execution_envelope(
    task_id="perf-check",
    task_profile={"task_type": "delivery", "complexity": "complex", "risk": "medium", "requires_verification": True, "requires_review": True},
    loop_policy={"base_loop": "plan_execute_verify", "max_iterations": 2, "review_depth": "standard"},
    capabilities=["planning", "implementation"],
    harnesses=["planner", "implementer"],
    brains=["brain-01-product-strategy"],
    artifacts=["artifact.md"],
    status="success",
    next_actions=[],
)
verification = VerificationHarness().verify(envelope, envelope.task_profile)
review = ReviewHarness().review(envelope, verification, envelope.task_profile)
recovery = RecoveryHarness().decide(envelope, "review_failed", review.review_verdict, envelope.loop_policy.max_iterations, 1)
print(verification.verification_verdict, review.review_verdict, recovery.action)
PY
```

## Interpretation

- si clasificación/selección requiere red o I/O nuevo: regresión
- si verification/review/recovery requiere red o I/O nuevo: regresión
- si el tiempo de suite enfocada crece fuertemente sin cambio funcional:
  investigar
