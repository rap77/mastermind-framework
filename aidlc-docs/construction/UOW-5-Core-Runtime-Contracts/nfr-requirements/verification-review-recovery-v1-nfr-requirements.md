# NFR Requirements — UOW-5 verification-review-recovery-v1

## Purpose

Definir las cualidades operativas mínimas para que `VerificationHarness`,
`ReviewHarness` y `RecoveryHarness` vuelvan útil el runtime sin convertirlo en
un sistema caro, opaco o recursivo.

## 1. Performance

### NFR-P5.VR1 — Overhead pequeño
- Verification/review/recovery deben agregar overhead pequeño frente a la
  ejecución base.
- El camino simple no debe invocar estos harnesses cuando `LoopPolicy` no lo exige.

### NFR-P5.VR2 — Coste local
- La primera implementación debe operar localmente, sin llamadas remotas
  obligatorias.
- El maker-checker MVP no debe requerir MCP/network para cada tarea.

## 2. Security

### NFR-S5.VR1 — No autoaprobación silenciosa
- Si `requires_review = true`, el resultado no puede presentarse como éxito
  pleno sin `ReviewOutcome`.

### NFR-S5.VR2 — Recovery bounded
- Recovery debe respetar una ladder finita y explicitada.
- No puede ejecutar retries infinitos ni patching autónomo abierto.

### NFR-S5.VR3 — Sin fuga en metadata
- Verification/review/recovery no deben introducir secretos innecesarios en
  envelope o transport metadata.

## 3. Availability and Continuity

### NFR-A5.VR1 — Degradación local segura
- Si review richer no está disponible, el MVP debe degradar a rubric local o a
  escalate, no a omitir review requerida.

### NFR-A5.VR2 — Continuidad resumible
- Los outcomes de verification/review/recovery deben poder resumirse en el
  envelope para handoff y reanudación futura.

## 4. Reliability and Determinism

### NFR-R5.VR1 — Verdicts repetibles
- Dado el mismo envelope base y la misma rubric/check set, verification y
  review deben producir el mismo verdict.

### NFR-R5.VR2 — Failure classification estable
- `FailureRecord` debe clasificar fallos de forma estable para que recovery no
  cambie de rama arbitrariamente.

### NFR-R5.VR3 — No-progress detection obligatoria
- Recovery debe reconocer repetición de failure class + attempts y cortar el
  loop con `escalate` o `stop`.

## 5. Maintainability and Testability

### NFR-M5.VR1 — Harnesses pequeños y aislables
- Verification/review/recovery deben implementarse como componentes pequeños,
  testeables en aislamiento.

### NFR-M5.VR2 — Cobertura dirigida
- Deben existir tests unitarios para:
  - verification pass/fail
  - review approval/block
  - recovery ladder selection
  - no-progress detection

### NFR-M5.VR3 — Integración incremental
- La slice debe integrarse en `StatelessCoordinator` sin romper tests
  existentes del flow base.

## 6. Operability

### NFR-O5.VR1 — Evidence legible
- `VerificationOutcome`, `ReviewOutcome` y `RecoveryDecision` deben dejar
  razones breves y trazables.

### NFR-O5.VR2 — Next action explícita
- El envelope final debe exponer `next_actions` consistentes con el verdict más
  restrictivo.

## 7. Success Thresholds

- tasks simples siguen sin pagar verification/review/recovery extra
- tasks con `requires_verification` dejan outcome explícito
- tasks con `requires_review` dejan outcome explícito
- failures elegibles producen `RecoveryDecision` bounded
- la suite focused del coordinator sigue verde
