# Roadmap: MasterMind v3.2

**Milestone:** RAG per agent + pgvector + LangSmith observability
**Defined:** 2026-05-14
**Phase Start:** 20 (v3.1 ended at D2)
**Brain validation:** Brain #1 (Product) + Brain #7 (Evaluator) — APPROVED_WITH_CONDITIONS

---

## Brain Validation Summary

**Brain #1 key corrections:**
- pgvector ya está activo (migration 001) — Phase 20 es schema only, no infraestructura
- LangSmith corre en paralelo con Phase 20 (no después de ingestion)
- Phase 3 auto-update reducida a script manual one-shot
- Phase 2.5 (RAG evaluation gate) es OBLIGATORIA antes de escalar de 1 a 7 brains
- sentence-transformers necesita promoverse de dev-deps a runtime deps
- Cross-brain learning → v3.3 (no validado aún)

**Brain #7 critical constraints:**
- OEC: quality_score delta >= +8pp (RAG vs cold context) — medido con ExperienceLogger + Brain #7 evaluator
- SLI-1: Recall@5 >= 0.70 para cada brain (70 pares etiquetados)
- Dos colecciones con estrategias distintas: `project_memory` (BRAIN-FEED logs) ≠ `domain_knowledge` (docs/sources/ libros)
- Knowledge Contamination Loop: no ingestar logs operacionales como conocimiento experto
- Phase 5 hard gate: OEC + SLI-1 confirmados en 5/7 brains antes de escalar

---

## Phases

### Phase 20: pgvector Schema + LangSmith Foundation (paralelo)

**Goal:** Embeddings table, vector index, asyncpg utilities, LangSmith instrumentation — todo en una fase paralela. pgvector ya live.

**Depends on:** Nothing (first phase of v3.2)

**Requirements:** RAG-01, LSMITH-01

**Success Criteria:**

1. Tabla `brain_embeddings` creada con columna `embedding vector(1536)`, HNSW index, particionada por `brain_id` y `collection_type` (domain_knowledge | project_memory)
2. `sentence-transformers` promovido de dev-deps a runtime deps en `apps/api/pyproject.toml`
3. Utility function `similarity_search(brain_id, collection, query_text, limit=5)` retorna top-K chunks con score
4. LangSmith SDK instalado en runtime deps, `LANGSMITH_API_KEY` en `.env.example`
5. `DynamicDispatchEngine` instrumentado con LangSmith callbacks — latencia, tokens, costo visible por provider (anthropic / openrouter / z_ai)
6. OEC definido y registrado: `quality_score` baseline medido en Brain #1 sin RAG (mínimo 5 sesiones)

---

### Phase 21: RAG Pilot — Brain #1 Only

**Goal:** Un solo brain con RAG funcional, recuperando contexto de sus dos colecciones antes de responder.

**Depends on:** Phase 20 (schema + utilities)

**Requirements:** RAG-02

**Success Criteria:**

1. Brain #1 (Product Strategy) consulta `domain_knowledge` collection antes de cada respuesta — top-5 chunks del corpus de libros (`docs/software-development/sources/`)
2. Brain #1 consulta `project_memory` collection — top-3 chunks de su BRAIN-FEED operacional reciente
3. Contexto recuperado se inyecta en el system prompt del brain con sección `[RETRIEVED CONTEXT]` explícita
4. Retrieval latency P99 < 200ms (medido con LangSmith traces)
5. `ExperienceLogger` registra `rag_enabled: true` en `custom_metadata` de la sesión

---

### Phase 21.5: RAG Evaluation Gate

**Goal:** Validar que el RAG mejora calidad antes de escalar a los 7 brains.

**Depends on:** Phase 21 (RAG on Brain #1)

**Requirements:** RAG-EVAL-01

**Success Criteria (HARD GATE — no continuar sin cumplir):**

1. A/B test: mismo brief ejecutado con Brain #1 RAG-habilitado vs Brain #1 cold (sin RAG) — mínimo 5 pares
2. `quality_score` delta (Brain #7 evaluator): RAG-enabled >= cold + 8 puntos (escala 0–100)
3. Recall@5 offline: >= 0.70 en 10 pares etiquetados manualmente para Brain #1's domain_knowledge collection
4. P99 latency total (RAG + LLM): < baseline + 500ms
5. Zero knowledge contamination: retrieved chunks no incluyen respuestas previas del mismo brain (self-similarity < 0.85)

**Si algún criterio no se cumple:** STOP — diagnosticar retrieval antes de continuar.

---

### Phase 22: Knowledge Ingestion (Manual)

**Goal:** Cargar el corpus de conocimiento en cada brain's vector store.

**Depends on:** Phase 21.5 (gate passed)

**Requirements:** RAG-03

**Success Criteria:**

1. Script `apps/api/mastermind_cli/rag/ingest.py` — idempotent upsert, chunking configurable, reporta N chunks por brain
2. `domain_knowledge` collection de los 7 brains cargada desde `docs/software-development/sources/` (10 archivos FUENTE-*.md)
3. `project_memory` collection de los 7 brains cargada desde sus respectivos `BRAIN-FEED-NN-domain.md`
4. Sin auto-update, sin file watcher — script one-shot manual
5. `SELECT brain_id, collection_type, COUNT(*) FROM brain_embeddings GROUP BY 1, 2` retorna 14 filas (7 brains × 2 collections), con conteos > 0

---

### Phase 23: RAG Scale-Out — Brains 2–7

**Goal:** Extender RAG a los 6 brains restantes, usando el mismo patrón validado en Brain #1.

**Depends on:** Phase 22 (all brains ingested)

**Requirements:** RAG-04

**Success Criteria:**

1. Los 7 brains con `rag_enabled: true` en sus agent configs
2. Recall@5 >= 0.70 en los 7 brains (70 pares etiquetados, 10 por brain)
3. OEC cumplido: quality_score delta >= +8pp en promedio de los 7 brains vs baseline cold
4. Latency guardrail: ningún brain supera baseline + 500ms en P99
5. LangSmith dashboard muestra trazas de todos los providers activos con desglose de costo por brain

---

## Progress

| Phase | Name | Status | Completed |
|-------|------|--------|-----------|
| 20 | pgvector Schema + LangSmith | ⏳ Pending | — |
| 21 | RAG Pilot — Brain #1 | ⏳ Pending | — |
| 21.5 | RAG Evaluation Gate | ⏳ Pending | — |
| 22 | Knowledge Ingestion | ⏳ Pending | — |
| 23 | RAG Scale-Out | ⏳ Pending | — |

**Overall Progress:** 0/5 phases delivered

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| RAG-01 (schema + utilities) | Phase 20 | ⏳ |
| LSMITH-01 (LangSmith instrumentation) | Phase 20 | ⏳ |
| RAG-02 (Brain #1 RAG) | Phase 21 | ⏳ |
| RAG-EVAL-01 (evaluation gate) | Phase 21.5 | ⏳ |
| RAG-03 (ingestion script) | Phase 22 | ⏳ |
| RAG-04 (scale-out 7 brains) | Phase 23 | ⏳ |

---

## Key Constraints

1. **pgvector ya activo** — `CREATE EXTENSION vector` está en migration 001. Phase 20 es schema only.
2. **Dos colecciones con estrategias distintas** — `domain_knowledge` (libros destilados) ≠ `project_memory` (BRAIN-FEED logs). Estrategias de chunking y pesos de retrieval distintos.
3. **OEC antes de escalar** — quality_score +8pp en Brain #1 es precondición de Phase 22.
4. **LangSmith = observabilidad only** — no reemplaza DynamicDispatchEngine ni ExperienceLogger.
5. **Cross-brain learning → v3.3** — solo si OEC + SLI-1 confirmados en 5/7 brains al final de v3.2.
6. **Sin LangChain, sin LangGraph** — asyncpg + pgvector directamente.

---

## Deferred to v3.3

- **Phase 24: Cross-brain learning** — pattern propagation via BRAIN-FEED (conditional on v3.2 OEC confirmed)
- **Ingestion auto-update pipeline** — solo si manual re-runs become documented bottleneck
- **Template Marketplace** — conditional on 3 LATAM SME interviews + 1 LOI

---
*Roadmap created: 2026-05-14*
*Brain validation: Brain #1 APPROVED | Brain #7 APPROVED_WITH_CONDITIONS*
