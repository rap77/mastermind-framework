# Memory Schema

## 1. Propósito

Bajar la Memory Layer a un esquema persistible en Postgres para sostener continuidad, contexto y aprendizaje con el menor consumo posible de tokens.

## 2. Tesis central

La memoria debe ser estructurada, versionada y recuperable por metadata antes que por texto libre.

## 3. Entidades principales

### 3.1 operational_state

Estado corto y mutable del sistema.

Campos sugeridos:

- `session_id`
- `project_id`
- `phase_id`
- `objective_id`
- `status`
- `current_harness`
- `current_loop`
- `current_brain`
- `checkpoint_ref`
- `backend_ref`
- `model_ref`
- `updated_at`

### 3.2 memory_items

Memoria durable de alto valor.

Campos sugeridos:

- `memory_id`
- `memory_key`
- `memory_type`
- `title`
- `content`
- `summary`
- `project_id`
- `brain_id`
- `niche_scope`
- `source_kind`
- `source_ref`
- `importance`
- `trust_level`
- `visibility`
- `tags`
- `state`
- `version`
- `created_at`
- `updated_at`

### 3.3 memory_chunks

Fragmentos recuperables para búsqueda semántica.

Campos sugeridos:

- `chunk_id`
- `memory_id`
- `chunk_index`
- `chunk_text`
- `chunk_summary`
- `metadata`
- `created_at`

### 3.4 memory_embeddings

Vectores de búsqueda semántica.

Campos sugeridos:

- `embedding_id`
- `chunk_id`
- `embedding_model`
- `embedding_vector`
- `dimensionality`
- `created_at`

### 3.5 memory_links

Relaciones entre memorias.

Campos sugeridos:

- `link_id`
- `from_memory_id`
- `to_memory_id`
- `relation_type`
- `reason`
- `strength`
- `created_at`

Relation types:

- `supports`
- `derived_from`
- `contradicts`
- `supersedes`
- `references`
- `related_to`

### 3.6 memory_checkpoints

Snapshots de estado reanudable.

Campos sugeridos:

- `checkpoint_id`
- `session_id`
- `project_id`
- `state_blob`
- `summary`
- `next_step`
- `created_at`

### 3.7 memory_usage_events

Eventos de lectura/escritura para aprendizaje del sistema.

Campos sugeridos:

- `event_id`
- `session_id`
- `project_id`
- `memory_id`
- `event_type`
- `query_ref`
- `result_count`
- `selected_count`
- `outcome`
- `created_at`

## 4. Índices recomendados

- `memory_key` unique
- `project_id`
- `brain_id`
- `memory_type`
- `state`
- `importance`
- `trust_level`
- `created_at`
- `memory_links(from_memory_id, relation_type)`
- `memory_links(to_memory_id, relation_type)`
- vector index sobre `memory_embeddings.embedding_vector`

## 5. Operaciones mínimas

### 5.1 Save memory item

Crear o versionar memoria durable.

### 5.2 Update memory item

Actualizar contenido, summary o metadata sin perder historial.

### 5.3 Chunk memory

Dividir un item largo en chunks recuperables.

### 5.4 Embed chunk

Generar vector para búsqueda semántica.

### 5.5 Link memory

Relacionar memorias entre sí.

### 5.6 Save checkpoint

Persistir estado reanudable.

### 5.7 Query memory

Buscar por metadata, texto o embeddings.

### 5.8 Record memory usage

Guardar cómo se usó la memoria y qué resultado tuvo.

## 6. Retrieval rules

La consulta debe seguir este orden:

1. metadata filter
2. scope filter
3. recency filter
4. trust filter
5. importance filter
6. semantic search
7. ranking
8. top-k projection

## 7. Token minimization rules

- guardar summary antes de guardar texto largo
- fragmentar solo cuando el item sea recuperable
- usar top-k pequeño por defecto
- no inyectar chunks si un summary basta
- no duplicar el mismo contenido en múltiples entidades

## 8. Integración con capability registry

La memoria debe poder alimentar:

- memory projections
- usage history
- adoption decisions
- selector hints

## 9. Integración con source registry

Cada memory item debe poder rastrearse a:

- fuente externa
- decisión interna
- artefacto canónico
- commit / issue / PR

## 10. Integración con harnesses

La Memory Layer debe servir a:

- Discovery Harness
- Research Harness
- AI-DLC Harness
- Review Harness
- Recovery Harness
- Archive Harness

## 11. No-goals

- no guardar todo como memoria durable
- no usar embeddings sin metadata
- no mezclar runtime state con long-term memory
- no tratar checkpoints como logs planos
