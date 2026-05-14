# MasterMind v3.2 — Specification

**Generado:** 2026-05-14
**Brain consultations:** Brain #1 (Product Strategy) + Brain #7 (Growth/Data)
**Input:** ROADMAP-v3.2.md + BRAIN-FEED.md constraints + v3.1 ExperienceLogger baseline

---

## Objetivo

v3.2 introduce RAG per agent con pgvector + observabilidad LLM con LangSmith. Cada uno de los 7 brains tendrá su propio vector store particionado con dos colecciones distintas: `domain_knowledge` (libros destilados de `docs/`) y `project_memory` (BRAIN-FEED logs operacionales).

**No es un pivot de arquitectura.** Es el milestone que agrega memoria vectorial a los brains existentes, con un gate de evaluación obligatorio antes de escalar de 1 a 7 brains.

El resultado medible: Brain #1 con RAG produce un quality_score (evaluado por Brain #7) al menos +8 puntos por encima del cold baseline, con Recall@5 >= 0.70. Todos los brains instrumentados en LangSmith para visibilidad de costo/latencia por provider.

---

## Contexto

- **v3.1 cerrado** — Fases A–D completadas. Stack activo: Next.js 16 + FastAPI + Rust Axum + PostgreSQL 16.
- **pgvector YA ACTIVO** — `CREATE EXTENSION vector` está en migration 001. Phase 20 es schema only, no infraestructura.
- **ExperienceLogger EXISTS** — Registra quality_score post-sesión. Brain #7 evalúa automáticamente (hook C3). Baseline = 5 sesiones sin RAG necesarias.
- **DynamicDispatchEngine EXISTS** — `apps/api/mastermind_cli/mm_flow/dispatch_engine.py`. Es el punto de inyección para LangSmith callbacks.
- **asyncpg como driver** — No ORM, no LangChain, no LangGraph. Queries directas a pgvector.
- **sentence-transformers** — Librería para embeddings. Actualmente en dev-deps; debe promoverse a runtime.
- **BRAIN-FEED docs/** — `docs/software-development/sources/` contiene 10 archivos `FUENTE-*.md` (corpus de domain_knowledge para Brain #1 y otros).

---

## Problem Statement

Los brains responden con conocimiento de entrenamiento del modelo base. No tienen acceso a:
1. El corpus de libros destilados (`docs/software-development/sources/`) al momento de responder
2. El historial operacional del propio brain (BRAIN-FEED logs de sesiones pasadas)

Esto crea dos brechas:
- **Conocimiento perdido**: Los 10 libros destilados en `docs/` existen pero no se inyectan en el contexto.
- **Aprendizaje perdido**: Cada sesión empieza desde cero; patrones de sesiones anteriores no se recuperan.

La solución es RAG con pgvector: dos colecciones por brain, embeddings pre-generados, retrieval en < 200ms, contexto inyectado automáticamente en el system prompt.

---

## Solution Architecture

### Componentes nuevos

```
brain_embeddings (PostgreSQL/pgvector)
  ├── brain_id: text
  ├── collection_type: domain_knowledge | project_memory
  ├── chunk_text: text
  ├── embedding: vector(1536)
  └── HNSW index on embedding (m=16, ef_construction=64)

EmbeddingService (apps/api/mastermind_cli/rag/)
  ├── embed.py      — sentence-transformers encode + asyncpg upsert
  ├── search.py     — similarity_search(brain_id, collection, query, limit=5)
  └── ingest.py     — idempotent ingest script (one-shot manual)

RAGContextBuilder (apps/api/mastermind_cli/rag/context_builder.py)
  ├── build(brain_id, user_query) → str
  ├── domain_knowledge: top-5 chunks
  └── project_memory: top-3 chunks
```

### RAG Query Path

```
User brief → DynamicDispatchEngine
    ↓
RAGContextBuilder.build(brain_id, brief)
    ├── similarity_search(brain_id, "domain_knowledge", brief, limit=5) [asyncpg]
    └── similarity_search(brain_id, "project_memory", brief, limit=3) [asyncpg]
    ↓
[RETRIEVED CONTEXT] block inyectado en system prompt del brain
    ↓
Brain responds con contexto aumentado
    ↓
ExperienceLogger registra rag_enabled=true en custom_metadata
    ↓
Brain #7 evalúa quality_score → comparar con cold baseline
```

### Colecciones: estrategias distintas

| Collection | Fuente | Chunking | Peso retrieval | Propósito |
|------------|--------|----------|----------------|-----------|
| `domain_knowledge` | `docs/software-development/sources/FUENTE-*.md` | Por sección H2 + overlap 128 tokens | Mayor peso (fundamentos) | Contexto de libros destilados |
| `project_memory` | `.planning/BRAIN-FEED-NN-domain.md` | Por bullet point (learnings) | Menor peso (experiencias) | Patrones y aprendizajes operacionales |

**Invariante Brain #7:** Estas dos colecciones NO deben cruzarse. `project_memory` contiene logs operacionales, no conocimiento experto. Ingestar uno como el otro es Knowledge Contamination Loop.

### LangSmith Integration Points

LangSmith es observabilidad pura — no modifica el dispatch ni el routing. Puntos de instrumentación:

1. `DynamicDispatchEngine.dispatch()` — callback al inicio de cada llamada LLM
2. Resultado de Brain #7 evaluación — trace separado con quality_score
3. RAG retrieval — span con latency y chunk count

```python
# Patrón de instrumentación (DynamicDispatchEngine)
from langsmith import traceable

@traceable(name="brain_dispatch", metadata={"provider": provider})
async def dispatch(self, context: BrainContext) -> DispatchResult:
    ...
```

---

## Requirements

### Functional

| ID | Descripción | Phase |
|----|-------------|-------|
| RAG-01 | Tabla `brain_embeddings` con HNSW index, particionada por brain_id + collection_type | 20 |
| RAG-01b | `similarity_search(brain_id, collection, query, limit)` asyncpg utility | 20 |
| LSMITH-01 | LangSmith SDK instalado, `DynamicDispatchEngine` instrumentado | 20 |
| LSMITH-01b | OEC baseline medido: quality_score promedio de Brain #1 sin RAG (≥ 5 sesiones) | 20 |
| RAG-02 | Brain #1 recupera top-5 domain_knowledge + top-3 project_memory antes de responder | 21 |
| RAG-02b | Contexto inyectado en system prompt bajo sección `[RETRIEVED CONTEXT]` explícita | 21 |
| RAG-02c | `ExperienceLogger` registra `rag_enabled: true` en custom_metadata | 21 |
| RAG-EVAL-01 | A/B test Brain #1 RAG vs cold — mínimo 5 pares evaluados por Brain #7 | 21.5 |
| RAG-EVAL-01b | quality_score delta >= +8pp (HARD GATE) | 21.5 |
| RAG-EVAL-01c | Recall@5 >= 0.70 en 10 pares etiquetados para domain_knowledge de Brain #1 | 21.5 |
| RAG-03 | Script `ingest.py` idempotent — carga las 2 colecciones de los 7 brains one-shot | 22 |
| RAG-04 | Los 7 brains con `rag_enabled: true` en sus agent configs | 23 |
| RAG-04b | Recall@5 >= 0.70 en todos los 7 brains (70 pares etiquetados) | 23 |

### Non-Functional

| ID | Descripción | Medición |
|----|-------------|----------|
| NFR-01 | Retrieval latency P99 < 200ms | LangSmith traces |
| NFR-02 | Latency total (RAG + LLM) < baseline + 500ms en P99 | LangSmith |
| NFR-03 | Zero knowledge contamination: self-similarity retrieved vs previous responses < 0.85 | Script de validación |
| NFR-04 | Ingest script idempotent: re-run no duplica chunks (ON CONFLICT DO NOTHING o hash check) | `SELECT COUNT(*) FROM brain_embeddings` antes/después de re-run |
| NFR-05 | sentence-transformers en runtime deps (no dev-deps) | `pyproject.toml` |

---

## Tech Decisions

### asyncpg directo (no LangChain, no LangGraph)

**Decisión:** Queries pgvector via asyncpg con operador `<=>` (cosine similarity). No LangChain, no LangGraph.

**Razones:**
- Stack ya usa asyncpg como driver primario (Phase 19 decisión locked)
- LangChain agrega 15+ deps, compatibility friction con Pydantic v2 strict mode
- pgvector queries son triviales: `ORDER BY embedding <=> $1 LIMIT $2`
- BRAIN-FEED anti-patrón: no agregar dependencias sin justificación de complejidad

### sentence-transformers para embeddings

**Modelo elegido:** `all-MiniLM-L6-v2` (384d → proyectado a 1536 via padding o usar `all-mpnet-base-v2` directamente en 768d)

**Nota:** El schema usa `vector(1536)` (dimensión de OpenAI ada-002) para compatibilidad futura. Si sentence-transformers produce 768d, usar `vector(768)` directamente — ajustar schema a la dimensión real del modelo elegido.

**Razones:**
- sentence-transformers ya está en dev-deps — solo promover
- No depende de API externa para embeddings (sin costo por token, sin latency de red)
- Suficiente para corpus de 10 libros destilados (~3000 chunks estimados)

### LangSmith como observabilidad pura

**Decisión:** LangSmith no modifica el dispatch, el routing, ni la lógica de brains. Es decorador puro (`@traceable`).

**Razones:**
- Brain #7 constraint: LangSmith = observabilidad only
- `DynamicDispatchEngine` ya tiene su lógica probada — no tocarla más allá del decorator
- El costo/latencia por provider ya es visible en logs estructurados (v3.1) — LangSmith agrega dashboard UI

---

## Success Criteria (OEC + SLIs)

### OEC (Overall Evaluation Criterion)

**quality_score delta >= +8pp**

- Medición: Brain #1 con RAG vs Brain #1 cold (mismo brief)
- Evaluador: Brain #7 (automático via post-session hook)
- Mínimo: 5 pares de comparación en Phase 21.5
- Escala: 0–100 (heredada de ExperienceLogger.quality_score)

### SLIs

| SLI | Target | Medición | Phase |
|-----|--------|----------|-------|
| SLI-1: Recall@5 Brain #1 | >= 0.70 | 10 pares etiquetados manualmente | 21.5 |
| SLI-2: Recall@5 Brains 2–7 | >= 0.70 cada uno | 10 pares × 6 brains | 23 |
| SLI-3: Retrieval latency P99 | < 200ms | LangSmith spans | 21 |
| SLI-4: Total latency P99 | < baseline + 500ms | LangSmith | 21.5 |
| SLI-5: Zero contamination | self-sim < 0.85 | validation script | 21.5 |

### Hard Gate (Phase 21.5)

Si OEC o SLI-1 no se cumplen: STOP. No avanzar a Phase 22 (ingestion ni scale-out).
Diagnosticar retrieval antes de continuar: chunk size, overlap, modelo de embeddings, index params.

---

## Scope

### En v3.2

- pgvector schema (brain_embeddings, HNSW index)
- sentence-transformers embeddings (runtime dep)
- RAG en Brain #1 únicamente (Phase 21)
- Evaluation gate A/B (Phase 21.5) — obligatoria
- Ingestion script one-shot manual para los 7 brains (Phase 22)
- RAG scale-out a Brains 2–7 (Phase 23) — condicional a gate
- LangSmith instrumentation en DynamicDispatchEngine

### Fuera de v3.2 (→ v3.3)

- **Phase 24: Cross-brain learning** — propagación de patrones vía BRAIN-FEED entre brains. Solo después de OEC confirmado en 5/7 brains.
- **Ingestion auto-update pipeline** — file watcher o cron. Solo si re-runs manuales se documentan como bottleneck.
- **Template Marketplace** — condicional a 3 entrevistas LATAM SME + 1 LOI.
- **Embeddings via API externa** — OpenAI ada-002 o similar. Solo si sentence-transformers prueba insuficiente (NFR-01 no cumplido).

---

## Arquitectura v3.2 vs v3.1

| Componente | v3.1 | v3.2 |
|-----------|------|------|
| Contexto brain | Solo system prompt estático | System prompt + [RETRIEVED CONTEXT] inyectado |
| Memoria brain | ExperienceLogger (structured records) | ExperienceLogger + pgvector similarity search |
| Observabilidad LLM | Structured logs (structlog) | Structured logs + LangSmith dashboard |
| Ingestion | N/A | Script one-shot manual (`ingest.py`) |
| Evaluation | quality_score post-sesión (Brain #7) | A/B quality_score: RAG vs cold baseline |
| Scale | 0 brains con RAG | 7 brains con RAG (condicional a gate) |

---

## Out of Scope v3.2

- WhatsApp / Instagram / Email real APIs (requieren concierge MVP — Brain #1 veto)
- PROP-001/002/003 (proposals desbloqueadas pero no críticas para v3.2)
- WCAG AA, Storybook (deferred)
- K6 load testing (después de RAG estable)
- Multi-tenant / Marketplace (sin paying customers validados)
- Cambios al WebSocket Hub (v3.1 feature — no tocar)
- Cambios al Three-Column Canvas (v3.1 feature — no tocar)
