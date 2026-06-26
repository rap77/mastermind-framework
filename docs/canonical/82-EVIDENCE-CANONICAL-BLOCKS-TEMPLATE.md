# Evidence Canonical Blocks Template

## 1. Propósito

Definir la plantilla estándar que MasterMind usa para convertir evidencia cruda en bloques canónicos reutilizables.

## 2. Tesis central

Toda fuente útil debe poder resumirse en bloques pequeños, comparables y versionables.

## 3. Uso

Usar esta plantilla para:

- repositorios
- páginas de producto
- libros
- docs técnicas
- sistemas existentes
- entrevistas y transcripciones

## 4. Bloques canónicos

### 4.1 Source Summary

- qué es la fuente
- qué problema resuelve
- qué tan confiable es
- qué parte importa para MasterMind

### 4.2 Capability Blocks

- nombre de la capability
- descripción corta
- valor para MasterMind
- evidencia de respaldo
- nivel de confianza

### 4.3 Pattern Blocks

- patrón observado
- contexto donde aplica
- beneficio
- costo
- restricciones

### 4.4 Anti-pattern Blocks

- anti-pattern
- por qué evitarlo
- severidad
- alternativa recomendada

### 4.5 Constraint Blocks

- limitación técnica
- limitación operativa
- limitación de seguridad
- limitación de tokens/contexto

### 4.6 Gap Blocks

- información faltante
- impacto del gap
- pregunta necesaria
- severidad

### 4.7 Decision Blocks

- decisión tomada
- estado de adopción
- razón
- fuente exacta
- efecto sobre MasterMind

## 5. Campos mínimos por bloque

Cada bloque debe tener, como mínimo:

- `title`
- `type`
- `summary`
- `source_ref`
- `confidence`
- `impact`

## 6. Regla de compresión

Si una fuente es larga, el sistema debe preferir varios bloques pequeños antes que un único resumen monolítico.

## 7. Regla de trazabilidad

Cada bloque debe apuntar a una evidencia concreta:

- URL
- path
- commit
- snapshot
- cita
- extracto

## 8. Token policy

- resumen primero
- metadata primero
- bloques cortos
- top-k
- no duplicar texto

## 9. No-goals

- no guardar evidencia cruda como si fuera canonical
- no crear bloques sin source_ref
- no mezclar gaps con decisiones
- no escribir párrafos largos si un bloque corto basta
