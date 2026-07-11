# Design — memory-layer-v1

## Architecture / Boundaries

El cambio introduce una capa nueva, separada de `project_state`:

- `project_state` sigue siendo runtime state canónico
- `memory_layer` se vuelve la memoria persistente reusable
- `retrieval` seguirá siendo una capability posterior encima de la memoria

### Boundary map

```text
Agents / Brains / UI
        │
        ▼
   MemoryService
        │
        ▼
    MemoryStore
   ├── EngramMemoryStore   (bridge temporal)
   └── PostgresMemoryStore (target propio)
```

## Technical Approach

### 1. Nuevo paquete

Crear:

- `apps/api/mastermind_cli/memory_layer/`

Archivos iniciales:

- `models.py`
- `contracts.py`
- `service.py`
- `store_engram.py`
- `store_postgres.py`

### 2. Modelos mínimos

- `MemoryItem`
- `MemorySearchResult`
- `MemoryContextBundle`

Todos con campos preparados para:

- `project_id`
- `brain_id`
- `niche`
- `visibility`
- `memory_type`
- `metadata`

### 3. Contrato inicial

Métodos mínimos:

- `save_item`
- `get_item`
- `search`
- `list_recent`
- `save_session_summary`
- `save_preference`

No incluir aún:

- graph traversal
- reranking
- query cache

### 4. Engram bridge

El adapter temporal traduce:

- save/search/context

pero el resto del sistema solo conoce `MemoryStore`.

### 5. Postgres store

Backend mínimo con tablas:

- `mm_memory_items`
- `mm_memory_preferences`
- `mm_memory_sessions`

### 6. Primeras superficies

Migrar primero:

- session summaries
- learnings / fixes / patterns
- preferences operativas

## Dependencies

- `project_state` solo como referencia de IDs y source refs
- Postgres actual del framework
- Engram únicamente como bridge temporal, no como contrato de dominio

## Validation Strategy

- tests unitarios del contrato de store
- tests de mapping Engram → modelos internos
- tests de integración Postgres save/get/search
- pruebas focalizadas sobre session summary / preference / learning flows

## Tradeoffs

- Se pospone retrieval híbrido para no mezclar ownership del dato con sofisticación de búsqueda.
- Se mantiene dualidad temporal con Engram para no romper continuidad.
- Se privilegia extensibilidad futura por niche sin sobrediseñar el slice actual.

## Context Notes

- Los docs canónicos 55–62 ya fijan arquitectura, taxonomía, roadmap y modularidad.
- El principio lego/comercializable aplica desde el diseño del contrato.
