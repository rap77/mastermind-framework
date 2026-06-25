# Application Design Summary — Multi-Harness Architecture

## Design Decision Summary

- MasterMind adoptará una **arquitectura multi-harness explícita**.
- MasterMind adoptará una **taxonomía multi-loop explícita**.
- Governance entra como **interceptor determinista** antes del `Coordinator`.
- La persistencia MVP de evidencia y budget será **JSON Lines append-only**.
- El eval harness se mantiene **desacoplado** como servicio/script offline.
- Overnight mode se implementa como **supervisor cauteloso** que consulta governance antes y después de cada tarea.
- El primer target no es un OS completo estilo ECC, pero sí dejar el núcleo
  listo para crecer hacia esa dirección.
- Rust queda fuera del primer slice funcional y solo absorberá hot paths medidos.

## Main Components

- `CoordinatorAdapter`
- `HarnessRegistry`
- `LoopSelector`
- `EnvelopeContract`
- `GovernanceInterceptor`
- `PolicySet`
- `BudgetEnforcer`
- `EvidenceChainWriter`
- `ExecutionHarness`
- `EvalHarnessService`
- `VerificationHarness`
- `ReviewHarness`
- `RecoveryHarness`
- `QrelGenerationSupport`
- `OvernightSupervisor`
- `ResumeCheckpointStore`
- `CapabilityRegistry`

## Service Layer

- Governance Service
- Loop Selection Service
- Capability Resolution Service
- Execution Service
- Evaluation Service
- Verification Service
- Review Service
- Recovery Service
- Meta-loop Analysis Service
- Overnight Execution Service
- Persistence Service

## Architectural Guarantees

- backward compatibility para callers actuales
- policy enforcement determinista
- audit trail reproducible
- selección del mínimo control suficiente por tarea
- maker-checker split para trabajo no trivial
- continuidad entre modelos/backends basada en checkpoint + memory
- extensión futura a PostgreSQL y Rust sin rediseño completo

## Canonical Harness Inventory

1. **Orchestrator Harness**
2. **Context & Memory Harness**
3. **Execution Harness**
4. **Verification Harness**
5. **Review Harness**
6. **Recovery Harness**
7. **Observability & Audit Harness**

## Canonical Loop Taxonomy

1. **Tool Loop**
2. **Goal Loop**
3. **Verification Loop**
4. **Reflection Loop**
5. **Recovery Loop**
6. **Review Loop**
7. **Heartbeat Loop**

## Compatibility Rule

Los harnesses y loops no son sinónimos:

- el **harness** define responsabilidad, capacidades y contrato
- el **loop** define control, iteración, validación, finalización y escalación

Una tarea puede ejecutar un harness con distintos loops según su complejidad y
riesgo.
