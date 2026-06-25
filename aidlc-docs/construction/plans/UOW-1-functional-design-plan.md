# Functional Design Plan — UOW-1 Governance Core

## Scope

Diseñar la lógica de negocio detallada del borde de governance que intercepta intenciones antes del `Coordinator`.

## Plan

- [x] Analizar el contexto de UOW-1 y su boundary con `Coordinator`
- [x] Modelar las entidades de dominio necesarias para intención, contexto, veredicto y eventos
- [x] Definir el flujo de evaluación de policies y resolución de veredictos
- [x] Definir reglas de negocio para scope, riesgo, secretos, writes a producción y main branch
- [x] Definir reglas de data flow, auditabilidad y escenarios de error
- [x] Validar coherencia con backward compatibility y determinismo

## Clarification Status

No se agregaron preguntas `[Answer]:` en esta corrida porque los artefactos de inception ya fijaron:

- patrón interceptor
- formato de veredicto
- límites de scope/riesgo
- responsabilidad de audit trail
- compatibilidad con `Coordinator.orchestrate()`
