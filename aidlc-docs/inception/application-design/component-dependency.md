# Component Dependency

## Dependency Matrix

| Component | Depends On | Why |
|---|---|---|
| CoordinatorAdapter | HarnessRegistry, LoopSelector, GovernanceInterceptor, Coordinator | Selección y control antes de ejecutar |
| HarnessRegistry | static config / typed models | Fuente de verdad de harnesses |
| LoopSelector | task classification, CapabilityRegistry | Elegir control mínimo suficiente |
| EnvelopeContract | typed schemas | Unificar handoff entre componentes |
| GovernanceInterceptor | PolicySet, BudgetEnforcer, EvidenceChainWriter | Evaluación y trazabilidad |
| PolicySet | TaskContext, Intention | Decisiones determinísticas |
| BudgetEnforcer | EvidenceChainWriter, BudgetContext | Persistencia de consumo |
| ExecutionHarness | CapabilityRegistry, Persistence Service | Ejecutar y persistir artifacts |
| VerificationHarness | ExecutionHarness outputs, acceptance criteria | Validar estado logrado |
| ReviewHarness | ExecutionHarness outputs, summary context | Maker-checker split |
| RecoveryHarness | VerificationHarness, ReviewHarness, LoopSelector | Retry/patch/replan/escalate |
| EvalHarnessService | QrelGenerationSupport, corpus loader, baseline store | Medición offline |
| CapabilityRegistry | harness metadata, skill inventory, MCP inventory, verifier metadata | Selección dinámica |
| OvernightSupervisor | GovernanceInterceptor, ResumeCheckpointStore, backend health provider, LoopSelector | Loop nocturno cauteloso |
| Meta-loop Analysis Service | EvidenceChainWriter, EvalHarnessService outputs | Aprendizaje de reglas |

## Communication Pattern

- `CoordinatorAdapter -> LoopSelector`: synchronous policy selection
- `CoordinatorAdapter -> CapabilityRegistry`: contextual capability resolution
- `CoordinatorAdapter -> GovernanceInterceptor`: synchronous pre-check
- `GovernanceInterceptor -> EvidenceChainWriter`: append-only write
- `GovernanceInterceptor -> Coordinator/ExecutionService`: conditional delegation
- `ExecutionService -> VerificationHarness`: deterministic validation
- `ExecutionService -> ReviewHarness`: maker-checker review when required
- `VerificationHarness/ReviewHarness -> RecoveryHarness`: failure routing
- `OvernightSupervisor -> GovernanceInterceptor`: per-task gating
- `EvalHarnessService -> baseline store`: compare + report
- `Meta-loop -> regression runner`: post-analysis validation

## Data Flow

1. El caller invoca `CoordinatorAdapter`.
2. Se construye una `Intention`.
3. `LoopSelector` decide loop policy.
4. `CapabilityRegistry` resuelve harnesses/capabilities mínimas útiles.
5. `GovernanceInterceptor` consulta scope/risk/secret/budget.
6. Se registra evidencia.
7. Si el veredicto es `allow`, se delega al `Coordinator` o `ExecutionService`.
8. `VerificationHarness` y/o `ReviewHarness` validan el outcome.
9. `RecoveryHarness` decide retry/patch/replan/escalate si falla.
10. `BudgetEnforcer.post_call` registra consumo real.
11. `OvernightSupervisor` toma snapshots y checkpoints.
