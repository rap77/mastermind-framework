# Memory Retrieval Service

## 1. Propósito

Definir el servicio que recupera contexto útil desde la Memory Layer con el menor costo posible de tokens.

## 2. Tesis central

> La mejor recuperación no es la que trae más contexto, sino la que trae el contexto mínimo suficiente y confiable.

## 3. Responsabilidad

El servicio debe:

- buscar memoria por metadata
- buscar por texto
- buscar por embeddings
- combinar resultados
- rankear por relevancia, recencia e importancia
- proyectar contexto resumido
- devolver referencias útiles para el selector y el harness

## 4. Inputs

### 4.1 MemoryQueryRequest

- `query_id`
- `project_id`
- `objective_id`
- `session_id`
- `brain_id`
- `phase_id`
- `query_text`
- `memory_types`
- `niche_scope`
- `tags`
- `min_trust_level`
- `min_importance`
- `top_k`
- `token_budget`
- `need_checkpoints`
- `need_decisions`
- `need_preferences`
- `need_source_summaries`

### 4.2 MemoryProjectionRequest

- `query_id`
- `target_context_type`
- `max_items`
- `max_tokens`
- `summary_first`
- `allow_chunks`
- `allow_archive`

## 5. Outputs

### 5.1 MemorySearchResult

- `memory_id`
- `memory_key`
- `title`
- `snippet`
- `summary`
- `score`
- `memory_type`
- `source_ref`
- `why_matched`

### 5.2 MemoryProjectionResult

- `projected_context`
- `selected_items`
- `summary`
- `reasoning`
- `token_estimate`
- `truncated`

## 6. Retrieval pipeline

### Step 1 — Normalize query

Limpia ruido y extrae señales:

- objective
- niche
- brain
- phase
- desired artifact

### Step 2 — Metadata filter

Filtra por:

- project_id
- brain_id
- phase_id
- memory_type
- niche_scope
- trust_level
- importance

### Step 3 — Text / keyword search

Buscar coincidencias literales cuando la consulta lo justifique.

### Step 4 — Vector search

Buscar similitud semántica sobre chunks o summaries.

### Step 5 — Merge and rank

Combinar resultados y rankear por:

- relevance
- recency
- importance
- trust
- source quality
- cost to project into context

### Step 6 — Project context

Producir un bundle mínimo suficiente para el siguiente paso del workflow.

## 7. Ranking rules

- Preferir summaries sobre chunks largos.
- Preferir memorias con mejor source_ref.
- Preferir memorias recientes si la tarea es operativa.
- Preferir memorias antiguas pero estables si la tarea es doctrinal.
- Bajar score si la memoria requiere demasiado contexto adicional.

## 8. Token minimization rules

- top_k pequeño por defecto
- summary-first projection
- expandir solo bajo necesidad explícita
- no incluir archive completo si un resumen basta
- no repetir la misma decisión en múltiples fragmentos

## 9. Context types

El servicio debe poder proyectar contextos distintos:

- operational context
- decision context
- source context
- harness context
- recovery context
- architecture context

## 10. Checkpoint integration

El servicio debe poder traer:

- último checkpoint
- summary del checkpoint
- next_step
- recovery notes

## 11. Decision integration

El servicio debe poder traer:

- decisiones relevantes
- rationale
- superseded decisions
- linked decisions

## 12. Preference integration

El servicio debe poder traer:

- preferencias del usuario
- preferencias de proyecto
- preferencias de brain
- restricciones persistentes

## 13. Source summary integration

Si la query toca fuentes externas, el servicio debe traer:

- source summary
- delta notes
- capabilities
- anti-patterns

## 14. Failure modes

Si no hay suficientes resultados:

- devolver `needs_more_context`
- sugerir queries alternativas
- sugerir discovery o source lookup

## 15. No-goals

- no traer todo por si acaso
- no mezclar memoria durable con runtime state
- no devolver chunks sin ranking
- no ignorar token budget
- no usar vector search sin metadata filter

## 16. Relación con los demás docs

- `65-MEMORY-AND-CONTEXT-ARCHITECTURE.md`
- `70-MEMORY-SCHEMA.md`
- `73-HARNESS-SELECTOR-SERVICE.md`
- `75-MEMORY-RETRIEVAL-SERVICE.md`
