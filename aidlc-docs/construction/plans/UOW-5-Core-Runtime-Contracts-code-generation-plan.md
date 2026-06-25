# Code Generation Plan — UOW-5 Core Runtime Contracts

## Unit Context

- **Unit**: UOW-5 Core Runtime Contracts
- **Slice**: `envelope-contract-loop-selector-v1`
- **Stories / Requirements**:
  - FR-11 Multi-harness core explícito
  - FR-12 Multi-loop explícito
  - FR-13 Loop selection policy
  - FR-14 Envelope contract único
  - FR-15 Maker-checker split
  - FR-16 Capability registry
  - FR-17 Continuidad cross-model / cross-harness (foundation only)
  - FR-18 Foundations for learning loop (foundation only)
- **Dependencies**:
  - UOW-1 governance already available in `apps/api/mastermind_cli/orchestrator/governance/`
  - UOW-2 persistence conventions available for future continuity hooks
  - UOW-3 eval seams must remain untouched
- **Service Boundary**:
  - El slice entra cerca del borde del coordinador stateless actual.
  - No debe romper flows existentes ni agregar infraestructura remota.
- **Database Ownership**:
  - Ninguna entidad nueva persistida en este slice.
  - Solo contratos runtime en memoria + seams listos para persistencia futura.

## Exact Code Paths

- `apps/api/mastermind_cli/orchestrator/runtime_contracts/__init__.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/models.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/capability_registry.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/harness_registry.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/loop_selector.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/envelope.py`
- `apps/api/mastermind_cli/orchestrator/stateless_coordinator.py`
- `apps/api/mastermind_cli/orchestrator/__init__.py`
- `apps/api/tests/unit/test_runtime_contracts.py`
- `apps/api/tests/unit/test_stateless_coordinator_runtime_contracts.py`
- `aidlc-docs/construction/UOW-5-Core-Runtime-Contracts/code/envelope-contract-loop-selector-v1-summary.md`

## Generation Strategy

- Implementar primero contratos puros y deterministas.
- Integrar luego en `StatelessCoordinator` con adopción mínima.
- Verificar con tests unitarios del selector, envelope y wiring del coordinador.
- Diferir recovery/review ricos y persistence durable a slices posteriores.

## Plan

- [x] Step 1 — Crear paquete `runtime_contracts/` con modelos typed para
      `TaskProfile`, `LoopPolicy`, `CapabilityDefinition`, `CapabilitySet`,
      `ExecutionEnvelope`, `VerificationPayload` y `RecoveryPayload`
- [x] Step 2 — Implementar `CapabilityRegistry` y `HarnessRegistry` con
      inventario local estático, filtrado determinista por compatibilidad,
      costo, riesgo y `requires_checker`
- [x] Step 3 — Implementar `LoopSelector` con política de minimum sufficient
      control para clasificar tareas simples / medias / complejas y elegir
      `single-pass`, `execute+verify-light` o composición con review flag
- [x] Step 4 — Implementar utilidades de `EnvelopeContract` para construir y
      validar `ExecutionEnvelope` con shape estable y razones estructuradas
- [x] Step 5 — Integrar los runtime contracts en
      `apps/api/mastermind_cli/orchestrator/stateless_coordinator.py` de forma
      no disruptiva: clasificar la tarea antes de ejecutar, resolver
      capabilities, seleccionar loop y anexar envelope/resumen estructurado al
      resultado del flow
- [x] Step 6 — Exportar los nuevos contratos desde
      `apps/api/mastermind_cli/orchestrator/__init__.py` y mantener backward
      compatibility para callers que no conocen aún el nuevo package
- [x] Step 7 — Agregar pruebas unitarias para clasificación de `TaskProfile`,
      selección de `LoopPolicy`, validación de `ExecutionEnvelope` y filtrado
      de registries
- [x] Step 8 — Agregar pruebas de integración liviana para verificar que
      `StatelessCoordinator` usa los runtime contracts sin romper el flujo
      actual ni el comportamiento fail-closed de governance
- [x] Step 9 — Crear resumen markdown del slice implementado en
      `aidlc-docs/construction/UOW-5-Core-Runtime-Contracts/code/` con paths
      modificados/creados, contratos expuestos y límites explícitos del MVP

## Traceability

- **FR-11 / FR-16** → Steps 1, 2, 6, 7
- **FR-12 / FR-13** → Steps 1, 3, 5, 7, 8
- **FR-14** → Steps 1, 4, 5, 7
- **FR-15** → Steps 2, 3, 5, 8
- **FR-17 / FR-18 foundations** → Steps 1, 4, 5, 9

## Explicit Non-Goals For This Slice

- No operator HUD
- No scheduler nocturno
- No recovery ladder completa ejecutable end-to-end
- No persistence store nuevo
- No paridad cross-harness total
- No integración obligatoria con el coordinator legacy de `tools/mastermind-cli`

## Plan Status

Este plan es la fuente de verdad para Code Generation de
`envelope-contract-loop-selector-v1`.
