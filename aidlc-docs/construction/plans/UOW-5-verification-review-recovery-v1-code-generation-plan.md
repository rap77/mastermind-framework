# Code Generation Plan — UOW-5 verification-review-recovery-v1

## Unit Context

- **Unit**: UOW-5 Core Runtime Contracts
- **Slice**: `verification-review-recovery-v1`
- **Stories / Requirements**:
  - FR-15 Maker-checker split
  - FR-17 Continuidad cross-model / cross-harness (foundation only)
  - FR-18 Foundations for learning loop (foundation only)
  - BR-5.V* verification explícita
  - BR-5.R* review explícito
  - BR-5.RE* recovery bounded
- **Dependencies**:
  - `envelope-contract-loop-selector-v1` ya implementado
  - `StatelessCoordinator` ya expone `runtime_task_profile`, `runtime_loop_policy`
    y `runtime_envelope`
  - envelope shape base ya existe y no debe romperse
- **Service Boundary**:
  - todo entra en `apps/api/mastermind_cli/orchestrator/runtime_contracts/`
  - integración mínima y incremental en `StatelessCoordinator`
- **Database Ownership**:
  - ninguna entidad persistida nueva
  - todo en memoria y resumible vía envelope

## Exact Code Paths

- `apps/api/mastermind_cli/orchestrator/runtime_contracts/models.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/__init__.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/verification.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/review.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/recovery.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/envelope.py`
- `apps/api/mastermind_cli/orchestrator/stateless_coordinator.py`
- `apps/api/tests/unit/test_runtime_contracts_verification.py`
- `apps/api/tests/unit/test_runtime_contracts_review.py`
- `apps/api/tests/unit/test_runtime_contracts_recovery.py`
- `apps/api/tests/unit/test_stateless_coordinator.py`
- `aidlc-docs/construction/UOW-5-Core-Runtime-Contracts/code/verification-review-recovery-v1-summary.md`

## Generation Strategy

- implementar harnesses locales pequeños
- extender modelos sin romper contratos existentes
- integrar orchestration en `StatelessCoordinator` por etapas
- probar en aislamiento primero, luego wiring focused

## Plan

- [x] Step 1 — Extender `models.py` con entidades mínimas para
      `VerificationCheck`, `VerificationOutcome`, `ReviewRubric`,
      `ReviewOutcome`, `FailureRecord` y `RecoveryDecision`
- [x] Step 2 — Implementar `verification.py` con `VerificationHarness`
      determinístico y set mínimo de checks locales
- [x] Step 3 — Implementar `review.py` con `ReviewRubricResolver` y
      `ReviewHarness` local rubric-driven
- [x] Step 4 — Implementar `recovery.py` con `FailureClassifier` y
      `RecoveryHarness` como decision engine bounded
- [x] Step 5 — Extender `envelope.py` para sintetizar envelope final con
      verdict más restrictivo y next actions consistentes
- [x] Step 6 — Exportar nuevos contratos/harnesses desde `__init__.py`
      preservando backward compatibility
- [x] Step 7 — Integrar la secuencia verification -> review -> recovery ->
      final envelope en `StatelessCoordinator` solo cuando `LoopPolicy` lo active
- [x] Step 8 — Agregar tests unitarios aislados para verification/review/recovery
      y ajustar tests del coordinator para cubrir el wiring
- [x] Step 9 — Crear resumen markdown del slice implementado en
      `aidlc-docs/construction/UOW-5-Core-Runtime-Contracts/code/`

## Traceability

- **verification** → Steps 1, 2, 5, 7, 8
- **review** → Steps 1, 3, 5, 7, 8
- **recovery** → Steps 1, 4, 5, 7, 8
- **envelope final restrictivo** → Steps 5, 7, 8
- **adopción incremental** → Steps 6, 7, 8, 9

## Explicit Non-Goals For This Slice

- no reviewer remoto obligatorio
- no auto-healing executor
- no persistence durable nueva
- no paridad con coordinator legacy
- no scheduler ni overnight mode
- no dynamic capability registry expansion

## Plan Status

Este plan es la fuente de verdad para Code Generation de
`verification-review-recovery-v1`.
