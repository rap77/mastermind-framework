# Memory and Context Architecture

## 1. Propósito

Definir cómo MasterMind guarda, recupera y proyecta memoria para sostener continuidad con el menor consumo posible de tokens.

## 2. Objetivo principal

Mantener el contexto útil disponible sin inundar al modelo con historial innecesario.

## 3. Principio rector

> La memoria no debe ser “todo lo que pasó”. Debe ser “lo que sigue siendo útil para decidir mejor la próxima acción”.

## 4. Capas de memoria

### 4.1 Operational State

Estado corto y mutable de ejecución.

Contiene:

- sesión activa
- fase activa
- objective / goal activo
- checkpoints recientes
- tareas en curso
- flags de approval / recovery
- backend/modelo actual

### 4.2 Durable Memory

Hechos estables y reutilizables.

Contiene:

- decisiones cerradas
- aprendizajes
- preferencias del usuario
- patterns reutilizados
- fallos corregidos
- outcomes relevantes
- summaries canonizados

### 4.3 Semantic Memory

Recuperación basada en similitud.

Contiene:

- fragments vectorizados
- summaries recuperables
- relaciones semánticas entre artefactos
- consultas pasadas con valor repetible

### 4.4 Cold Archive

Material de referencia de bajo acceso.

Contiene:

- logs largos
- transcripts completos
- artefactos antiguos
- diffs históricos
- reports previos

## 5. Backend base

### 5.1 Postgres como source of truth

Postgres será la fuente principal para:

- estado operativo
- memoria durable
- indexación de artefactos
- historial de decisiones
- checkpoints
- source registry

### 5.2 pgvector como retrieval layer

pgvector u otra extensión vectorial se usará para recuperar:

- decisiones parecidas
- fuentes relacionadas
- patterns reutilizables
- artefactos de contexto
- memories que refuercen una acción

### 5.3 Grafo derivado opcional

Un grafo puede usarse como índice de relaciones entre:

- fuentes
- decisiones
- harnesses
- brains
- artefactos
- checkpoints

El grafo no tiene que ser la fuente primaria desde el día uno; puede nacer como vista derivada sobre Postgres.

## 6. Modelo lógico mínimo

### 6.1 Tabla de estado de sesión

Campos conceptuales:

- `session_id`
- `project_id`
- `phase_id`
- `objective_id`
- `status`
- `current_harness`
- `current_loop`
- `checkpoint_ref`
- `updated_at`

### 6.2 Tabla de memoria durable

Campos conceptuales:

- `memory_id`
- `memory_type`
- `title`
- `content`
- `project_id`
- `brain_id`
- `niche`
- `source_kind`
- `source_ref`
- `importance`
- `trust_level`
- `tags`
- `summary`
- `embedding`
- `created_at`
- `updated_at`

### 6.3 Tabla de retrieval chunks

Campos conceptuales:

- `chunk_id`
- `memory_id`
- `chunk_text`
- `chunk_summary`
- `chunk_embedding`
- `metadata`

### 6.4 Tabla de checkpoints

Campos conceptuales:

- `checkpoint_id`
- `session_id`
- `project_id`
- `state_blob`
- `summary`
- `created_at`

## 7. Política de escritura

Escribir en memoria solo cuando el material tenga valor durable.

Reglas:

1. Guardar estado operativo corto siempre que cambie.
2. Guardar memoria durable solo en eventos de valor:
   - decisión
   - aprendizaje
   - fix
   - preference
   - source adoption
   - architecture change
3. Generar summary antes de persistir texto largo.
4. Separar raw artifact de memory fragment.
5. Registrar source_ref para volver al origen si hace falta.

## 8. Política de lectura

Cada lectura de contexto debe seguir este orden:

1. metadata filter
2. recency filter
3. trust filter
4. importance filter
5. semantic retrieval
6. summary-first projection
7. top-k fragments

## 9. Política de proyección de contexto

1. Filtrar por metadata.
2. Rankear por relevancia y recencia.
3. Resumir antes de expandir.
4. Inyectar solo top-k fragmentos.
5. No volver a cargar lo ya canonizado en el mismo ciclo.
6. Priorizar contexto que reduzca preguntas repetidas.

## 10. Tokens: principios

- Preferir resúmenes cortos a dumps largos.
- Guardar texto crudo solo cuando sea recuperable por referencia.
- Reusar summaries y canonical docs.
- Evitar duplicar el mismo contexto en varias capas.
- Meter primero contexto canónico; meter detalle solo si el loop lo exige.

## 11. Integración con Engram y AI-DLC state

Engram y AI-DLC state quedan como ayudas auxiliares de workflow o desarrollo.
La memoria principal del producto será Postgres.

## 12. Retrieval policy

Cada query debe considerar:

- proyecto
- fase
- tipo de memoria
- importancia
- recencia
- source trust
- necesidad de checker separado
- necesidad de vector retrieval
- necesidad de grafo

## 13. No-goals

- no guardar todo el chat como memoria durable
- no duplicar raw logs en varios sitios
- no usar grafo como source of truth inicial
- no meter summaries gigantes al prompt por defecto

## 14. Futuro

Si el grafo demuestra valor real, puede materializarse como BD dedicada.
Si no, basta como vista derivada sobre Postgres.
