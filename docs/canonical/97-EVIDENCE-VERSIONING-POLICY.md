# Evidence Versioning Policy

## 1. Propósito

Definir cómo versiona MasterMind la evidencia para conservar historia, comparar cambios y evitar pérdida de aprendizaje.

## 2. Tesis central

Toda evidencia útil debe poder referenciar una versión concreta, no solo una fuente genérica.

## 3. Qué se versiona

- fuente original
- snapshot de la fuente
- extracto canónico
- bloques canónicos
- decisiones derivadas
- preguntas y respuestas

## 4. Identificadores mínimos

Cada versión debe poder responder:

- qué es
- de dónde salió
- cuándo se capturó
- qué cambió respecto a la versión anterior
- qué decisión afectó

## 5. Versioning rules

- no sobrescribir versiones previas
- no reutilizar un identificador para contenido distinto
- no perder el vínculo entre snapshot y bloques
- no convertir un delta en una versión nueva sin razón

## 6. Version states

- `current`
- `superseded`
- `archived`
- `deprecated`
- `retracted`

## 7. No-goals

- no versionar texto bruto sin utilidad
- no tratar una versión nueva como reemplazo automático
- no eliminar historia por limpieza estética
