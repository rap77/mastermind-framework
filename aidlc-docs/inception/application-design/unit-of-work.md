# Units of Work

## UOW-1 — Governance Core

### Goal
Crear el borde determinista de policy enforcement antes del `Coordinator`.

### Includes
- `CoordinatorAdapter`
- `GovernanceInterceptor`
- `ScopePolicy`
- `RiskPolicy`
- `SecretPolicy`
- `ProductionWritePolicy`
- `MainBranchPolicy`

### Responsibility
Interceptar intenciones, decidir allow/deny/pause y garantizar audit trail.

## UOW-2 — Budget & Evidence Persistence

### Goal
Persistir consumo de tokens y evidencia append-only para sesiones y tasks.

### Includes
- `BudgetEnforcer`
- `EvidenceChainWriter`
- `ResumeCheckpointStore`
- formatos JSON Lines MVP

### Responsibility
Mantener continuidad, auditabilidad y datos para morning report/meta-loop.

## UOW-3 — Memory Eval Harness

### Goal
Medir retrieval sobre corpus estable con qrels sellados y baseline CI.

### Includes
- `EvalHarnessService`
- `QrelGenerationSupport`
- scorer offline
- baseline compare

### Responsibility
Detectar regresiones y establecer scorecards comparables.

## UOW-4 — Overnight Scheduler Integration

### Goal
Agregar modo nocturno cauteloso usando governance y budget como precondición.

### Includes
- `OvernightSupervisor`
- morning report
- checkpoint de reanudación
- integración con disponibilidad real de backends confirmados

### Responsibility
Ejecutar tareas secuenciales seguras durante runs largos sin intervención.

## UOW-5 — Core Runtime Contracts

### Goal
Formalizar los contratos runtime necesarios para que MasterMind evolucione a un
núcleo multi-harness y multi-loop seleccionable por tarea.

### Includes
- `HarnessRegistry`
- `LoopSelector`
- `EnvelopeContract`
- `ExecutionHarness`
- `VerificationHarness`
- `ReviewHarness`
- `RecoveryHarness`
- `CapabilityRegistry`

### Responsibility
Seleccionar el control mínimo suficiente, comunicar outcomes de forma tipada y
separar ejecución, verificación, review y recuperación.

## Code Organization Strategy

Como el sistema es brownfield y el módulo es multi-unit lógico dentro de `apps/api/mastermind_cli/orchestrator/`, la organización recomendada es:

- `orchestrator/governance/`
- `orchestrator/evaluation/`
- `orchestrator/scheduler/`
- `orchestrator/runtime_contracts/` o ubicación equivalente cercana al borde de
  `Coordinator`

Cada unidad mantiene su propio paquete, tests y contratos typed.
