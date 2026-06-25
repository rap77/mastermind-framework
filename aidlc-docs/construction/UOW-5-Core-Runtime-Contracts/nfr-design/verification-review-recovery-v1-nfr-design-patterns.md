# NFR Design Patterns — UOW-5 verification-review-recovery-v1

## Purpose

Traducir los NFR de verification/review/recovery a patrones concretos para que
la slice agregue control real sin introducir loops abiertos, costo remoto
innecesario ni opacidad operacional.

## 1. Conditional Harness Activation

### Pattern
Activar verification/review/recovery solo cuando `LoopPolicy` u outcomes previos
lo exigen.

### Applies To
- NFR-P5.VR1
- NFR-M5.VR3

### Design Effect
- tareas simples no pagan costo adicional
- el costo crece solo con necesidad real de control

## 2. Local Deterministic Verification

### Pattern
`VerificationHarness` ejecuta checks locales, repetibles y sin red obligatoria.

### Applies To
- NFR-P5.VR2
- NFR-R5.VR1

### Design Effect
- mismo input produce mismo verdict
- la base de aceptación mínima no depende de backend externo

## 3. Rubric-Based Maker-Checker

### Pattern
`ReviewHarness` usa una rubric separada del flujo base para bloquear
autoaprobación silenciosa.

### Applies To
- NFR-S5.VR1
- NFR-R5.VR1

### Design Effect
- el maker-checker existe lógicamente desde el MVP
- review richer puede llegar después sin invalidar el contrato inicial

## 4. Recovery As Decision Engine

### Pattern
`RecoveryHarness` decide el siguiente paso bounded, pero no ejecuta
auto-healing abierto.

### Applies To
- NFR-S5.VR2
- NFR-R5.VR2
- NFR-R5.VR3

### Design Effect
- recovery sigue la ladder finita
- se separa decisión de acción
- el sistema corta no-progreso en vez de insistir

## 5. Restrictive Final Verdict Synthesis

### Pattern
El envelope final refleja el verdict más restrictivo entre ejecución,
verificación, review y recovery.

### Applies To
- NFR-O5.VR2
- NFR-S5.VR1

### Design Effect
- no existe `success` silencioso con review pendiente/fallido
- `next_actions` queda alineado al control real

## 6. Safe Local Degradation

### Pattern
Si un review richer no existe, degradar a rubric local o `escalate`, nunca a
omitir review requerida.

### Applies To
- NFR-A5.VR1
- NFR-S5.VR1

### Design Effect
- la ausencia de capacidad no hace más permisivo al sistema
- se preserva el control aun en modo MVP

## 7. Traceable Evidence Payloads

### Pattern
Cada harness deja outcomes compactos, legibles y serializables en el envelope.

### Applies To
- NFR-A5.VR2
- NFR-O5.VR1
- NFR-S5.VR3

### Design Effect
- handoff/reanudación futura no dependen de transcript narrativo
- la metadata sigue breve y sin fuga innecesaria

## 8. Isolated Harness Testing

### Pattern
Cada harness se prueba en aislamiento y luego mediante wiring focused en el
coordinator.

### Applies To
- NFR-M5.VR1
- NFR-M5.VR2
- NFR-M5.VR3

### Design Effect
- regressions se detectan cerca del seam real
- la slice crece sin romper el flow base
