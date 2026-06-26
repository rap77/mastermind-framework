# Spec Archive and Lineage

## 1. Propósito

Preservar cada especificación generada junto con su línea de evidencia, decisiones y deltas para futuras actualizaciones.

## 2. Tesis central

Una spec útil no termina cuando se escribe. Debe poder revisarse, versionarse y compararse con su origen.

## 3. Qué se archiva

Archivar:

- spec final
- canonical blocks usados
- gaps cerrados
- preguntas y respuestas
- source refs
- decision trail
- token usage

## 4. Línea de lineage

Cada spec debe poder responder:

- de qué evidencia salió
- qué gaps la moldearon
- qué respuestas del usuario cambiaron la dirección
- qué decisiones se adoptaron o rechazaron

## 5. Reglas de archivado

- no guardar solo el documento final
- no borrar el contexto de origen
- no mezclar versiones distintas sin delta
- no perder la relación con la fuente exacta

## 6. Actualizaciones futuras

Si cambia una fuente o una decisión:

- crear nueva snapshot
- reevaluar gaps
- regenerar o patchear la spec
- dejar claro qué cambió y por qué

## 7. Relación con otros componentes

Este artefacto conecta:

- source registry
- memory layer
- spec generation harness
- AI-DLC archive

## 8. No-goals

- no archivar solo por cumplimiento
- no perder trazabilidad al refactorizar
- no sobrescribir historia sin delta explícito
