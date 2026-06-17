# Memory Layer Phase 1–2 Technical Plan

## 1. Propósito

Bajar la visión de la Memory Layer al primer corte técnico ejecutable: abstracción de contrato y backend Postgres mínimo.

---

## 2. Alcance

Este plan cubre únicamente:

- **Phase 1** — `MemoryStore` abstraction
- **Phase 2** — `PostgresMemoryStore` mínimo viable

No cubre todavía:

- graph retrieval
- reranking
- eval harness completo
- cutover total de Engram

---

## 3. Objetivo del corte

Lograr que MasterMind pueda:

1. guardar memoria a través de un contrato propio
2. implementar ese contrato sobre Postgres
3. seguir soportando bridge temporal hacia Engram
4. empezar a persistir learnings y summaries sin depender del proveedor externo

---

## 4. Entregables técnicos

## A. Contrato de dominio

Crear un paquete nuevo tipo:

- `apps/api/mastermind_cli/memory_layer/`

Submódulos iniciales:

- `contracts.py`
- `models.py`
- `store_engram.py`
- `store_postgres.py`
- `service.py`

---

## B. Modelos mínimos

### `MemoryItem`

Campos sugeridos:

- `memory_id`
- `memory_type`
- `title`
- `content`
- `project_id`
- `brain_id`
- `niche`
- `visibility`
- `source_kind`
- `source_ref`
- `tags`
- `metadata`
- `created_at`
- `updated_at`

### `MemorySearchResult`

- `memory_id`
- `title`
- `snippet`
- `score`
- `memory_type`
- `project_id`
- `brain_id`
- `why_matched`
- `source_ref`

### `MemoryContextBundle`

- `items`
- `summary`
- `open_gaps`
- `applied_scopes`

---

## C. Contrato `MemoryStore`

Métodos mínimos:

- `save_item(item)`
- `get_item(memory_id)`
- `search(query, scope, limit)`
- `save_session_summary(...)`
- `save_preference(...)`
- `list_recent(project_id, limit)`

### Nota

No meter desde el principio:

- graph traversal
- complex ranking
- batch remediation

Eso viene después.

---

## 5. Engram bridge de transición

## Objetivo

Encapsular Engram detrás del contrato, no usarlo directo.

### `EngramMemoryStore`

Debe mapear:

- save summary
- save observation
- search context

### Regla

Fuera de este adapter:

- nadie llama `mem_save`
- nadie llama `mem_search`
- nadie conoce la forma Engram

---

## 6. Postgres store mínimo

## Tabla principal

### `mm_memory_items`

Campos recomendados:

- `memory_id UUID PK`
- `memory_type TEXT NOT NULL`
- `title TEXT NOT NULL`
- `content TEXT NOT NULL`
- `project_id TEXT NULL`
- `brain_id TEXT NULL`
- `niche TEXT NULL`
- `visibility TEXT NOT NULL`
- `source_kind TEXT NULL`
- `source_ref TEXT NULL`
- `tags JSONB NOT NULL DEFAULT '[]'::jsonb`
- `metadata JSONB NOT NULL DEFAULT '{}'::jsonb`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`

## Tabla secundaria

### `mm_memory_preferences`

Para no mezclar preferencias operativas con cualquier otro memory item.

Campos:

- `preference_id UUID PK`
- `project_id TEXT NULL`
- `scope TEXT NOT NULL`
- `key TEXT NOT NULL`
- `value JSONB NOT NULL`
- `created_at TIMESTAMPTZ NOT NULL`
- `updated_at TIMESTAMPTZ NOT NULL`

## Tabla de sesiones

### `mm_memory_sessions`

Para resúmenes y continuidad.

Campos:

- `session_id TEXT PK`
- `project_id TEXT NULL`
- `summary TEXT NOT NULL`
- `metadata JSONB NOT NULL DEFAULT '{}'::jsonb`
- `created_at TIMESTAMPTZ NOT NULL`

---

## 7. Índices mínimos

Para el slice inicial:

- `(project_id, created_at DESC)`
- `(memory_type, created_at DESC)`
- `(brain_id, created_at DESC)`
- GIN en `tags`
- GIN/FTS sobre `title + content` si se decide meter lexical search ya

### Nota

pgvector puede esperar al siguiente slice si hace falta reducir riesgo.

---

## 8. Servicio de aplicación

Crear un `MemoryService` encima del store para:

- normalizar inputs
- decidir routing básico por tipo
- ocultar detalles de implementación

### Ejemplos

- `record_session_summary(...)`
- `record_lesson(...)`
- `record_fix(...)`
- `record_preference(...)`
- `fetch_project_context(...)`

---

## 9. Primeras superficies a migrar

## Slice A

Session summaries

## Slice B

Learned / fixes / patterns

## Slice C

Preferences operativas

### Razón

Son de bajo riesgo y alto valor.

---

## 10. Integración con lo actual

### Con `project_state`

No compartir tablas.

Sí compartir:

- `project_id`
- `task_id` como `source_ref`
- `artifact_id` como `source_ref`

### Con RAG futuro

La Phase 1–2 no debe obligar aún a embeddings, pero sí dejar:

- `memory_type`
- `niche`
- `visibility`
- `project_id`

como campos que luego faciliten retrieval híbrido.

---

## 11. Verificación

## Acceptance mínima Phase 1

1. existe `MemoryStore`
2. existe `EngramMemoryStore`
3. los flujos nuevos llaman contrato propio

## Acceptance mínima Phase 2

1. existe `PostgresMemoryStore`
2. se puede guardar y leer `MemoryItem`
3. se puede guardar y leer `session_summary`
4. se puede guardar y leer `preference`
5. tests del contrato pasan para ambos stores

---

## 12. Tests sugeridos

### Unit

- contract tests para store
- mapping tests Engram ↔ models internos
- validation tests de taxonomía mínima

### Integration

- save/get/search sobre Postgres
- dual-write opcional
- recent-by-project

---

## 13. Riesgos del slice

### Riesgo 1

Sobrediseñar el contrato.

### Mitigación

Mantenerlo pequeño y cubrir solo casos activos.

### Riesgo 2

Meter retrieval complejo demasiado pronto.

### Mitigación

Postergar hybrid retrieval al siguiente slice.

### Riesgo 3

Acoplar el contrato a software-development.

### Mitigación

Usar `memory_type`, `niche`, `visibility` y `metadata` desde el día 1.

---

## 14. Resultado esperado

Al cerrar este slice, MasterMind ya no dependerá conceptualmente de Engram para definir su memoria, aunque todavía pueda usarlo como bridge temporal.

## Key Learnings:

1. El primer corte técnico correcto es contrato + store mínimo, no retrieval sofisticado.
2. Session summaries, learnings y preferences son la mejor superficie inicial para migrar.
3. El contrato debe ser pequeño pero ya preparado para niches y modularidad futura.
