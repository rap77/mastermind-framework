# Tech Stack Decisions — UOW-5 verification-review-recovery-v1

## Decision Summary

La slice `verification-review-recovery-v1` seguirá en Python sobre
`apps/api/mastermind_cli/orchestrator/runtime_contracts/`, reutilizando el seam
stateless existente y sin introducir dependencias remotas nuevas.

## 1. Harness Implementation Model

### Decision
Implementar `VerificationHarness`, `ReviewHarness` y `RecoveryHarness` como
módulos locales pequeños dentro de `runtime_contracts/`.

### Rationale
- preserva determinismo
- baja fricción de integración
- facilita tests aislados

## 2. Review Model

### Decision
Usar **rubric local deterministic review** para el MVP.

### Rationale
- cumple maker-checker lógico sin depender todavía de otro backend/modelo
- evita costo y fragilidad remota temprana

## 3. Recovery Model

### Decision
Representar recovery como **decision engine**, no como executor autónomo.

### Rationale
- bounded control primero
- evita loops auto-healing prematuros

## 4. Envelope Evolution

### Decision
Extender el envelope solo con payloads compatibles, sin romper shape base.

### Rationale
- protege backward compatibility
- evita que cada harness reinvente contrato

## 5. Testing Stack

### Decision
Cubrir la slice con pytest focused + lint local.

### Rationale
- suficiente para validar verdicts y wiring
- consistente con el patrón ya usado en UOW-5 v1
