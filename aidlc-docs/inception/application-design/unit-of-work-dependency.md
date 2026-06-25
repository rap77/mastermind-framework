# Unit of Work Dependency

## Dependency Matrix

| Unit | Depends On | Reason |
|---|---|---|
| UOW-1 Governance Core | none | Base para todo el harness |
| UOW-2 Budget & Evidence Persistence | UOW-1 | Budget gates y evidencia se disparan desde governance |
| UOW-3 Memory Eval Harness | UOW-2 (optional shared persistence patterns) | Puede vivir casi desacoplado, pero reutiliza conventions de scorecard/audit |
| UOW-4 Overnight Scheduler Integration | UOW-1, UOW-2 | Necesita gating, budget, checkpoints y audit |
| UOW-5 Core Runtime Contracts | UOW-1, UOW-2, UOW-3 (partial reuse) | Necesita governance/budget ya existentes y reutiliza conventions de eval/memory para envelopes, selection y continuity |

## Recommended Build Order

1. UOW-1
2. UOW-2
3. UOW-3
4. UOW-4
5. UOW-5

## Coupling Notes

- UOW-3 debe mantenerse lo más desacoplada posible del runtime de ejecución.
- UOW-4 depende de UOW-1 y UOW-2, pero no debe conocer detalles internos del scorer.
- UOW-5 se apoya en slices previas, pero debe introducir contratos runtime
  reutilizables sin reescribir governance/budget existentes.
