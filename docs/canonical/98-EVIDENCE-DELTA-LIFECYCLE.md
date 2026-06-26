# Evidence Delta Lifecycle

## 1. Propósito

Definir el ciclo de vida de un delta de evidencia desde su detección hasta su archivado.

## 2. Tesis central

Un delta solo vale si produce una comparación útil y una decisión trazable.

## 3. Lifecycle stages

### 3.1 Detected

Se detectó cambio entre snapshots o fuentes.

### 3.2 Classified

Se clasificó el tipo de delta: funcional, estructural, de datos, NFR o de decisión.

### 3.3 Assessed

Se midió impacto, riesgo y confianza.

### 3.4 Decided

Se eligió adoptar, adaptar, rechazar o posponer.

### 3.5 Canonized

Se actualizó el bloque canónico o la spec correspondiente.

### 3.6 Archived

Se guardó la línea de tiempo completa.

## 4. Delta record fields

- delta_id
- from_version
- to_version
- delta_type
- summary
- impact
- risk
- confidence
- decision
- source_refs

## 5. Rules

- no delta sin comparación
- no decisión sin impacto
- no canonización sin trazabilidad
- no archivado sin referencia a versiones

## 6. No-goals

- no borrar deltas antiguos
- no fusionar deltas distintos sin justificación
- no perder el “por qué” del cambio
