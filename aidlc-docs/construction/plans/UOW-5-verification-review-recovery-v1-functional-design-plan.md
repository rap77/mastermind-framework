# Functional Design Plan — UOW-5 verification-review-recovery-v1

## Scope

Diseñar la lógica funcional mínima para volver ejecutables los seams de
`VerificationHarness`, `ReviewHarness` y `RecoveryHarness` sobre el runtime
stateless ya implementado.

## Plan

- [x] Aterrizar el workflow lógico entre ejecución, verificación, review y recovery
- [x] Definir entidades adicionales requeridas para verdicts, rubrics y decisiones bounded
- [x] Definir reglas de negocio para activación condicional desde `LoopPolicy`
- [x] Delimitar qué significa maker-checker MVP sin fresh-context remoto obligatorio
- [x] Delimitar qué significa recovery bounded MVP sin auto-healing abierto

## Clarification Status

No se agregaron preguntas `[Answer]:` en esta corrida porque ya quedó fijado
por artifacts previos y decisiones del usuario que:

- tareas simples deben seguir evitando loops caros
- maker-checker debe existir, pero primero con implementación mínima
- recovery debe ser bounded, no autónomo ni infinito
- la slice debe crecer sobre el seam stateless actual, sin abrir scope lateral
