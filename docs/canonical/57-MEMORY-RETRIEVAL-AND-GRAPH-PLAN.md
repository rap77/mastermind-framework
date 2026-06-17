# Memory Retrieval and Graph Plan

## 1. Propósito

Definir cómo MasterMind debe recuperar memoria útil con bajo costo de tokens y alta relevancia, combinando retrieval híbrido, scoping por fuente y relaciones de grafo.

---

## 2. Tesis central

> La memoria útil no se obtiene con vector-only search. MasterMind necesita retrieval híbrido y graph-aware para recuperar contexto correcto, explicable y reusable.

---

## 3. Roadmap de retrieval

### Fase 1 — Hybrid retrieval mínimo

- pgvector
- full-text / BM25
- RRF

### Fase 2 — Ranking enriquecido

- reranker opcional
- intent routing
- source boosts

### Fase 3 — Graph-aware retrieval

- relational recall
- graph traversal
- hub / adjacency signals

### Fase 4 — Retrieval efficiency

- semantic query cache
- adaptive return
- evidence contract
- gap analysis

---

## 4. Fuentes de retrieval

La búsqueda no debe ir contra un solo corpus.

Fuentes recomendadas:

- `project_memory`
- `knowledge_memory`
- `decision_memory`
- `incident_memory`
- `artifact_memory`
- `preference_memory`

Cada fuente puede tener:

- distinto chunking
- distinto weighting
- distinta política de freshness

---

## 5. Query intent mínimo

MasterMind debería clasificar consultas en:

- `entity`
- `temporal`
- `decision`
- `runtime`
- `pattern`
- `knowledge`

Eso permite ajustar:

- top-K
- boosts
- graph use
- reranker
- return shape

---

## 6. Graph plan

El grafo no debe centrarse en markdown pages, sino en entidades del dominio.

### Nodos mínimos

- project
- task
- task_run
- artifact
- checkpoint
- decision
- participant
- memory_item
- source_document
- niche_entity

### Relaciones mínimas

- `produced`
- `depends_on`
- `supports`
- `contradicts`
- `learned_from`
- `authored_by`
- `about`
- `used_in`
- `related_to`

---

## 7. Evidence contract

Cada resultado de retrieval debería poder explicar:

- `why_matched`
- `source_kind`
- `source_ref`
- `confidence_band`
- `freshness`
- `visibility_scope`

Esto ayuda a:

- agentes
- Brain #7
- auditoría
- UI de Strategy Vault / War Room

---

## 8. Gap analysis

El retrieval ideal no solo devuelve resultados.

También debe indicar:

- evidencia vieja
- contradicción entre items
- falta de cobertura
- ausencia de memoria para ese niche/brain/proyecto

---

## 9. Extensibilidad por niche

Cada niche puede registrar:

- tipos de entidad
- relaciones propias
- boosts específicos
- query intents dominantes

Ejemplos:

### Finanzas / inversiones

prioriza:

- temporal trajectories
- decision lineage
- risk relationships

### Marketing / digital

prioriza:

- campaign lineage
- channel performance learnings
- audience/entity links

---

## 10. Resultado esperado

Que MasterMind recupere menos texto bruto pero más contexto correcto:

- con menos tokens
- con mejor grounding
- con mejores explicaciones
- con menor repetición de errores

## Key Learnings:

1. El retrieval objetivo debe ser híbrido y multi-fuente, no solo vectorial.
2. El grafo debe modelar relaciones del dominio de MasterMind, no imitar literalmente el modelo de páginas de GBrain.
3. Evidence contract y gap analysis son partes de la calidad del retrieval, no extras opcionales.
