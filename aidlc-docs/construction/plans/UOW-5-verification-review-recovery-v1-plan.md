# Plan — UOW-5 verification-review-recovery-v1

## Goal

Expandir UOW-5 sobre el seam ya creado para que `VerificationHarness`,
`ReviewHarness` y `RecoveryHarness` dejen de ser solo diseño y pasen a tener
implementación MVP consumible por el runtime stateless.

## Why Now

- `TaskProfile`, `LoopPolicy` y `ExecutionEnvelope` ya existen.
- El siguiente valor no está en más selección, sino en hacer útiles los loops.
- Sin verificación/review/recovery reales, maker-checker y bounded recovery
  siguen siendo mostly declarativos.

## Scope

- implementar seams ejecutables mínimos para:
  - `VerificationHarness`
  - `ReviewHarness`
  - `RecoveryHarness`
- extender `ExecutionEnvelope` / metadata solo si hace falta y sin romper shape
- integrar activación condicional desde `StatelessCoordinator`
- agregar tests unitarios e integración liviana

## Non-Goals

- no scheduler nocturno
- no persistence durable nueva
- no parity con coordinator legacy
- no reviewer basado en red/MCP obligatorio
- no auto-healing abierto

## Proposed Steps

- [ ] Step 1 — definir contrato MVP de `VerificationHarness`
      (checks determinísticos + acceptance verdict)
- [ ] Step 2 — definir contrato MVP de `ReviewHarness`
      (fresh-checker local / adversarial rubric mínima)
- [ ] Step 3 — definir contrato MVP de `RecoveryHarness`
      (`retry -> patch -> replan -> escalate/stop`)
- [ ] Step 4 — integrar activación desde `LoopPolicy`
- [ ] Step 5 — reflejar outcomes en `ExecutionEnvelope`
- [ ] Step 6 — agregar tests unitarios y focused integration tests
- [ ] Step 7 — documentar nuevo slice y actualizar Build & Test

## Acceptance Criteria

- tareas simples siguen evitando loops caros
- tareas con `requires_verification` producen verification outcome explícito
- tareas con `requires_review` producen review outcome explícito
- failures tienen `RecoveryDecision` bounded, no retry implícito infinito
- el flow stateless existente sigue verde

## Recommended Code Surface

- `apps/api/mastermind_cli/orchestrator/runtime_contracts/verification.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/review.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/recovery.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/models.py`
- `apps/api/mastermind_cli/orchestrator/stateless_coordinator.py`
- `apps/api/tests/unit/test_runtime_contracts_*.py`

## Status

Planning artifact only. No code started in this slice yet.
