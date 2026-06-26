# Source Registry and Delta Protocol

## 1. Propósito

Evitar que el conocimiento aprendido de Hermes, ECC, gentle-ai u otras fuentes se pierda con nuevas actualizaciones.

## 2. Idea central

Cada fuente externa debe tratarse como un activo versionado, no como una referencia informal.

## 3. Source Registry

Cada fuente externa debe registrarse con:

- `source_id`
- nombre
- URL o path
- repo / package / doc type
- snapshot / commit hash / tag
- fecha de captura
- propósito
- estado de adopción
- nivel de confianza
- nivel de cambio esperado
- propietario o responsable
- riesgos
- decisiones derivadas

## 4. Estados de adopción

### 4.1 Candidate

Fuente observada pero no adoptada.

### 4.2 Adopted

Patrón o feature ya incorporado a MasterMind.

### 4.3 Adapted

Patrón útil, pero modificado para MasterMind.

### 4.4 Rejected

Patrón descartado por costo, complejidad, seguridad o desalineación.

### 4.5 Deprecated

Fuente o patrón antes útil que dejó de ser recomendable.

## 5. Artefactos por fuente

### 5.1 Summary

Qué es la fuente y qué aporta.

### 5.2 Capabilities

Qué capacidades, hooks o patrones ofrece.

### 5.3 Anti-patterns

Qué no conviene copiar.

### 5.4 Adoption Plan

Qué se adopta, adapta o descarta.

### 5.5 Delta Notes

Qué cambió desde la snapshot anterior.

### 5.6 Decision Record

Por qué se tomó cada decisión relevante.

## 6. Delta protocol

Ante una actualización de una fuente:

1. tomar snapshot nueva
2. registrar hash/tag/version
3. comparar contra la snapshot previa
4. revisar capacidades y anti-patterns
5. revisar si cambió riesgo/costo/compatibilidad
6. actualizar la síntesis canónica
7. actualizar registry y memory
8. ajustar specs o docs si cambia la decisión

## 7. Cómo se compara una fuente

La comparación debe responder:

- ¿qué capacidad nueva apareció?
- ¿qué capacidad cambió?
- ¿qué riesgo nuevo introdujo?
- ¿qué patrón dejó de ser recomendable?
- ¿qué parte sigue siendo útil para MasterMind?
- ¿qué parte ya quedó absorbida por el core?

## 8. Criterio de no-pérdida

Nada importante queda solo en el chat.
Toda decisión durable se materializa en:

- doc canónico
- decision record
- source registry
- memoria persistente
- delta notes

## 9. Uso con AI-DLC

El source registry se integra en discovery y research para que cada fuente externa pueda recorrerse, compararse, versionarse y re-evaluarse.

## 10. Flujo operativo recomendado

1. Capturar fuente
2. Sintetizar capacidades y anti-patterns
3. Elegir estado de adopción
4. Registrar delta frente a la snapshot previa
5. Actualizar docs canónicos si hace falta
6. Guardar memoria durable
7. Planificar la siguiente revisión

## 11. Reglas de actualización

- No sobrescribir análisis previo sin delta explícito.
- No reemplazar “adopted” por “candidate” sin razón.
- No perder snapshots antiguas si todavía justifican una decisión.
- No copiar una feature solo porque es popular.
- No re-evaluar sin comparar contra la versión anterior.
