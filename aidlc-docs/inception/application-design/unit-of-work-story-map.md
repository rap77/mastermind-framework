# Unit of Work Story Map

## Story / Requirement Mapping

| Requirement | Unit |
|---|---|
| FR-1 Governance interceptor previo al Coordinator | UOW-1 |
| FR-2 Policy gate SAL determinístico | UOW-1 |
| FR-3 Budget enforcement por tarea y sesión | UOW-2 |
| FR-4 Persistencia durable de consumo y evidencia | UOW-2 |
| FR-5 Memory Eval Harness v1 | UOW-3 |
| FR-6 Overnight Mode cauteloso | UOW-4 |
| FR-7 Meta-loop controlado | UOW-3 / UOW-2 |
| FR-8 Registration/backward compatibility | UOW-1 |
| FR-9 Overnight resume protocol | UOW-4 / UOW-2 |
| FR-10 Rust boundary | Cross-cutting constraint |
| FR-11 Multi-harness core explícito | UOW-5 |
| FR-12 Multi-loop explícito | UOW-5 |
| FR-13 Loop selection policy | UOW-5 |
| FR-14 Envelope contract único | UOW-5 |
| FR-15 Maker-checker split | UOW-5 |
| FR-16 Capability registry | UOW-5 |
| FR-17 Continuidad cross-model / cross-harness | UOW-5 / UOW-2 / UOW-4 |
| FR-18 Foundations for learning loop | UOW-5 / UOW-2 / UOW-3 |

## Incremental Delivery Map

### Slice 1
- UOW-1 Governance Core

### Slice 2
- UOW-2 Budget & Evidence Persistence

### Slice 3
- UOW-3 Memory Eval Harness

### Slice 4
- UOW-4 Overnight Scheduler Integration

### Slice 5
- UOW-5 Core Runtime Contracts
