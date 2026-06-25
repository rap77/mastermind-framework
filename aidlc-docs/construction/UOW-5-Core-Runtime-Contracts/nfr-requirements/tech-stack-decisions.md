# Tech Stack Decisions — UOW-5 Core Runtime Contracts

## Decision Summary

UOW-5 se implementará primero en Python sobre el stack actual de
`apps/api/mastermind_cli/`, reutilizando seams existentes de orchestrator,
governance, budget, memory y mm-flow, sin introducir infraestructura externa en
el camino crítico del slice inicial.

## 1. Runtime Language

### Decision
Usar **Python** para el primer release de `HarnessRegistry`, `LoopSelector`,
`EnvelopeContract` y `CapabilityRegistry`.

### Rationale
- El runtime actual ya vive en Python.
- Minimiza fricción de integración.
- Evita introducir una nueva frontera de lenguaje antes de estabilizar el
  contrato.

## 2. Integration Pattern

### Decision
Integrar el slice como **runtime contracts cercanos al borde del Coordinator**
con adopción progresiva por constructor/composición.

### Rationale
- Permite encajar con governance y budget ya existentes.
- Reduce blast radius en el primer rollout.
- Mantiene backward compatibility.

## 3. Registry Model

### Decision
Usar **registros tipados en código/config local** para el MVP.

### Rationale
- La selección necesita determinismo fuerte.
- El inventario inicial será pequeño.
- Permite evolucionar a fuentes más dinámicas después sin diseñar de más ahora.

## 4. Envelope Model

### Decision
Definir `ExecutionEnvelope` como **schema interno estable** antes de expandir
worktrees, HUD o cross-harness parity.

### Rationale
- Sin contrato estable, cada harness inventará su propia salida.
- El envelope es prerequisito para verification, review, recovery y handoff.

## 5. Loop Selection Model

### Decision
Implementar `LoopSelector` como **policy engine determinista**, no como prompt.

### Rationale
- El tipo de control no debe decidirse por intuición variable del modelo.
- Permite pruebas y debugging repetibles.

## 6. Persistence Boundary

### Decision
Reutilizar persistence ya existente (JSONL / project state / memory artifacts)
en vez de crear un nuevo store dedicado en el primer slice.

### Rationale
- La prioridad ahora es el contrato, no otro sistema de almacenamiento.
- La continuidad ya tiene piezas disponibles para reuso.

## 7. Testing Stack

### Decision
Cubrir UOW-5 con pruebas unitarias y de integración dentro del stack Python
existente.

### Rationale
- Debe validarse selección de loops, validez de envelopes y decisiones de
  recovery sin dependencia de LLMs.
- El slice se beneficia del patrón ya usado por governance y budget.

## 8. Future Migration Boundary

### Decision
Diseñar el slice para futuras adapters/harnesses más ricos, pero sin implementar
todavía paridad cross-harness total, worktree runtime completo o operator HUD.

### Rationale
- El target state estilo ECC es norte, no requisito del MVP.
- El primer valor viene de contratos runtime sólidos y selection policy útil.
