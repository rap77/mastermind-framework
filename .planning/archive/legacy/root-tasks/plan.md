# MasterMind v3.2 — Implementation Plan

**Generado:** 2026-05-14
**Basado en:** tasks/SPEC.md
**Estrategia:** Vertical slicing estricto — cada task entrega test + implementación juntos

---

## Dependency Graph

```
PHASE 20 (pgvector Schema + LangSmith)
  ├── 20A: brain_embeddings table + HNSW index
  ├── 20B: EmbeddingService (asyncpg utilities)
  └── 20C: LangSmith instrumentation + OEC baseline

       ↓ (Phase 20 completo)

PHASE 21 (RAG Pilot — Brain #1 Only)
  ├── 21A: RAGContextBuilder
  ├── 21B: Brain #1 integration (domain_knowledge + project_memory)
  └── 21C: ExperienceLogger rag_enabled flag

       ↓ (Phase 21 completo)

PHASE 21.5 (RAG Evaluation Gate) ← HARD GATE
  ├── 21.5A: A/B test framework (RAG vs cold)
  ├── 21.5B: Recall@5 offline evaluation
  └── 21.5C: Gate decision (PASS → Phase 22, FAIL → STOP)

       ↓ (Gate PASSED)

PHASE 22 (Knowledge Ingestion — Manual One-Shot)
  ├── 22A: Chunking logic + ingest.py
  └── 22B: Execute ingestion para los 7 brains × 2 collections

       ↓ (Phase 22 completo)

PHASE 23 (RAG Scale-Out — Brains 2–7)
  ├── 23A: Replicar RAG integration a Brains 2–7
  └── 23B: Recall@5 + OEC validation para todos los brains
```

**Parallelismo permitido:**
- 20A y 20C son paralelos entre sí (20B depende de 20A)
- 22A y 22B son secuenciales (22B necesita 22A)
- 23A para cada brain es independiente entre sí

**Regla estricta:** Phase 21.5 bloquea Phase 22. Si el gate no pasa, STOP y diagnosticar retrieval.

---

## PHASE 20: pgvector Schema + LangSmith Foundation

**Objetivo:** Schema de embeddings listo, utilities de asyncpg funcionando, LangSmith instrumentado. OEC baseline registrado.
**Tiempo estimado:** 3-4 días
**Depende de:** Nada (primera fase de v3.2)
**Entregable mínimo:** `similarity_search()` retorna resultados, LangSmith muestra trazas de DynamicDispatchEngine

### 20A: brain_embeddings Table + HNSW Index

**Qué:** Tabla `brain_embeddings` en PostgreSQL con columna `vector`, particionada por `brain_id` y `collection_type`. HNSW index para búsqueda eficiente.

**Backend (`apps/api/`):**
- Migration Alembic: tabla `brain_embeddings` con columnas: `id UUID PK`, `brain_id TEXT NOT NULL`, `collection_type TEXT CHECK(collection_type IN ('domain_knowledge','project_memory'))`, `source_ref TEXT`, `chunk_text TEXT NOT NULL`, `chunk_hash TEXT UNIQUE`, `embedding vector(768)`, `created_at TIMESTAMPTZ DEFAULT now()`
- HNSW index: `CREATE INDEX ON brain_embeddings USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)`
- Ejecutar `alembic upgrade head`

**Nota sobre dimensiones:** `all-MiniLM-L6-v2` produce 384d, `all-mpnet-base-v2` produce 768d. Usar `vector(768)` con `all-mpnet-base-v2`. Si se cambia el modelo, ajustar la dimensión en migration (breaking change).

**Tests:**
- Unit: verificar que `CREATE TABLE brain_embeddings` existe en schema test (`SELECT to_regclass('public.brain_embeddings') IS NOT NULL`)
- Unit: verificar que el HNSW index existe (`SELECT indexname FROM pg_indexes WHERE tablename='brain_embeddings' AND indexdef LIKE '%hnsw%'`)
- Unit: INSERT de un embedding dummy (768 zeros) → SELECT retorna sin error

**Acceptance:**
- [ ] `SELECT column_name, data_type FROM information_schema.columns WHERE table_name='brain_embeddings'` retorna todas las columnas esperadas
- [ ] `SELECT indexname FROM pg_indexes WHERE tablename='brain_embeddings'` incluye el HNSW index
- [ ] `chunk_hash` tiene UNIQUE constraint — idempotencia garantizada
- [ ] Tests de migration pasan

---

### 20B: EmbeddingService — asyncpg Utilities

**Qué:** Módulo `apps/api/mastermind_cli/rag/` con tres archivos: `embed.py`, `search.py`, `__init__.py`. sentence-transformers promovido a runtime dep.

**Backend (`apps/api/`):**
- `uv add sentence-transformers` — mover de dev-deps a deps en `pyproject.toml`
- `apps/api/mastermind_cli/rag/embed.py`:
  - `load_model(model_name="sentence-transformers/all-mpnet-base-v2") → SentenceTransformer`
  - `encode(texts: list[str]) → list[list[float]]` — batch encoding
  - `compute_hash(text: str) → str` — SHA256 para deduplicación
- `apps/api/mastermind_cli/rag/search.py`:
  - `similarity_search(conn, brain_id: str, collection: str, query_text: str, limit: int = 5) -> list[dict]` — query asyncpg con operador `<=>`, retorna `[{chunk_text, score, source_ref}]`
- `apps/api/mastermind_cli/rag/__init__.py` — exports

**Tests:**
- Unit: `encode(["hello world"])` retorna lista de 768 floats (shape check)
- Unit: `compute_hash("text")` retorna string hex de 64 chars
- Integration: `similarity_search(conn, "brain-01", "domain_knowledge", "product strategy", limit=3)` con datos de fixture → retorna lista con `chunk_text` y `score` en [0.0, 1.0]
- Edge: `similarity_search()` con colección vacía → retorna lista vacía (no crash)

**Acceptance:**
- [ ] `sentence-transformers` en `[project.dependencies]` de `pyproject.toml` (no en `[tool.uv.dev-dependencies]`)
- [ ] `from mastermind_cli.rag import similarity_search` no levanta ImportError
- [ ] `similarity_search()` con fixture retorna resultados ordenados por score desc
- [ ] Tests de search pasan

---

### 20C: LangSmith Instrumentation + OEC Baseline

**Qué:** LangSmith SDK instalado. `DynamicDispatchEngine` instrumentado con `@traceable`. OEC baseline: medir quality_score de Brain #1 en 5 sesiones sin RAG.

**Backend (`apps/api/`):**
- `uv add langsmith` — agregar a runtime deps
- `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT` en `.env.example`
- Instrumentar `DynamicDispatchEngine.dispatch()` con `@traceable(name="brain_dispatch")`
- Span metadata: `brain_id`, `provider`, `model`, `profile`
- `apps/api/mastermind_cli/rag/baseline.py`: script que lee los últimos N records de `ExperienceLogger` para `brain-01` sin `rag_enabled` y calcula quality_score promedio → guarda en `tasks/rag-baseline.json`

**Estructura de `tasks/rag-baseline.json`:**
```json
{
  "brain_id": "brain-01",
  "rag_enabled": false,
  "sessions_evaluated": 5,
  "quality_score_mean": 0.0,
  "quality_score_std": 0.0,
  "measured_at": "2026-05-14T00:00:00Z",
  "oec_target": "mean + 0.08"
}
```

**Tests:**
- Unit: `@traceable` decorator no rompe el dispatch normal (mock LangSmith client)
- Unit: `baseline.py` calcula mean correctamente con fixture de 5 records
- Smoke: `LANGSMITH_API_KEY=test python -c "from langsmith import traceable; print('ok')"` no levanta error

**Acceptance:**
- [ ] `langsmith` en `[project.dependencies]` de `pyproject.toml`
- [ ] `LANGSMITH_API_KEY` en `.env.example`
- [ ] `DynamicDispatchEngine.dispatch()` tiene `@traceable` decorator
- [ ] `tasks/rag-baseline.json` existe con `sessions_evaluated >= 5` (puede ser 0.0 si no hay sesiones previas — el campo documenta el baseline)
- [ ] Tests de LangSmith pasan

---

## PHASE 21: RAG Pilot — Brain #1 Only

**Objetivo:** Brain #1 recupera contexto de sus dos colecciones antes de cada respuesta. Latencia P99 < 200ms.
**Tiempo estimado:** 3-4 días
**Depende de:** Phase 20 (schema + EmbeddingService)

### 21A: RAGContextBuilder

**Qué:** Módulo `apps/api/mastermind_cli/rag/context_builder.py` que orquesta el retrieval y construye el bloque `[RETRIEVED CONTEXT]`.

**Backend (`apps/api/`):**
- `RAGContextBuilder`:
  - `__init__(conn: asyncpg.Connection)`
  - `async build(brain_id: str, query: str) -> str` — llama `similarity_search` para ambas colecciones, ensambla el bloque
- Formato del bloque inyectado:
  ```
  [RETRIEVED CONTEXT]
  --- domain_knowledge (top-5) ---
  [chunk_text] (score: 0.87, source: FUENTE-001)
  ...
  --- project_memory (top-3) ---
  [chunk_text] (score: 0.79, source: BRAIN-FEED-01)
  ...
  [END RETRIEVED CONTEXT]
  ```
- Si una colección está vacía: omitir esa sección del bloque (no crash, no placeholder)

**Tests:**
- Unit: `build("brain-01", "product strategy")` con mock `similarity_search` → retorna string que contiene `[RETRIEVED CONTEXT]` y `[END RETRIEVED CONTEXT]`
- Unit: `build()` con ambas colecciones vacías → retorna string vacío (no bloque vacío que contamina el prompt)
- Unit: `build()` con solo domain_knowledge → omite sección project_memory
- Timing: `build()` con fixture real → latencia < 200ms (medida con `time.perf_counter`)

**Acceptance:**
- [ ] `from mastermind_cli.rag.context_builder import RAGContextBuilder` no levanta ImportError
- [ ] `build()` retorna bloque con secciones correctas cuando hay datos
- [ ] `build()` retorna `""` cuando ambas colecciones están vacías
- [ ] Tests de context_builder pasan

---

### 21B: Brain #1 Integration

**Qué:** Integrar `RAGContextBuilder` en el path de ejecución de Brain #1. El contexto recuperado se inyecta en el system prompt antes de la llamada LLM.

**Backend (`apps/api/`):**
- Identificar dónde se construye el system prompt de Brain #1 (probablemente en `DynamicDispatchEngine` o en el brain agent runner)
- Antes de la llamada LLM: `rag_context = await rag_builder.build(brain_id="brain-01", query=user_brief)`
- Si `rag_context` no está vacío: append al system prompt como bloque `[RETRIEVED CONTEXT]`
- Flag en el request context: `rag_enabled = rag_context != ""`

**Tests:**
- Unit: mock `RAGContextBuilder.build()` → verify que system prompt incluye el bloque cuando `rag_context != ""`
- Unit: mock `RAGContextBuilder.build()` retorna `""` → system prompt NO incluye `[RETRIEVED CONTEXT]` (no bloque vacío)
- Integration: ejecutar Brain #1 con colecciones vacías (pre-ingestion) → responde sin error, `rag_enabled=false`

**Acceptance:**
- [ ] Brain #1 llama `RAGContextBuilder.build()` antes de cada invocación LLM
- [ ] System prompt de Brain #1 incluye `[RETRIEVED CONTEXT]` cuando hay chunks recuperados
- [ ] Brain #1 responde sin error cuando colecciones están vacías (pre-ingestion path)
- [ ] Tests de integración pasan

---

### 21C: ExperienceLogger rag_enabled Flag

**Qué:** El `ExperienceLogger` registra `rag_enabled: true/false` en `custom_metadata` de cada sesión de Brain #1.

**Backend (`apps/api/`):**
- Pasar `rag_enabled` como campo en `custom_metadata` al llamar `ExperienceLogger.log_execution()`
- Verificar que `experience_records.custom_metadata` es JSONB (ya debería serlo desde v3.1)
- LangSmith span de la sesión incluye `rag_enabled` en metadata

**Tests:**
- Unit: `log_execution(custom_metadata={"rag_enabled": True})` → verify `SELECT custom_metadata->>'rag_enabled' FROM experience_records` retorna `"true"`
- Integration: ejecutar Brain #1 → `SELECT custom_metadata FROM experience_records ORDER BY created_at DESC LIMIT 1` tiene `rag_enabled` key

**Acceptance:**
- [ ] `experience_records.custom_metadata` tiene `rag_enabled` key después de cada sesión de Brain #1
- [ ] Tests del flag pasan

---

## PHASE 21.5: RAG Evaluation Gate

**Objetivo:** Validar que RAG mejora calidad antes de escalar. Gate obligatorio.
**Tiempo estimado:** 2-3 días
**Depende de:** Phase 21 (RAG on Brain #1)
**HARD GATE:** Si no pasa, STOP. No avanzar a Phase 22.

### 21.5A: A/B Test Framework

**Qué:** Script que ejecuta el mismo brief con Brain #1 RAG-enabled y Brain #1 cold (sin RAG), captura los outputs, y solicita evaluación de Brain #7 para ambos.

**Backend (`apps/api/`):**
- `apps/api/mastermind_cli/rag/evaluate.py`:
  - `run_ab_test(brief: str, pairs: int = 5) -> ABTestResult`
  - Para cada par: ejecutar con RAG → evaluar → ejecutar cold → evaluar
  - `ABTestResult`: `{rag_scores: [float], cold_scores: [float], delta_mean: float, delta_std: float, passes_oec: bool}`
- Guardar resultado en `tasks/rag-evaluation-results.json`
- Script CLI: `uv run python -m mastermind_cli.rag.evaluate --pairs 5 --brief "Define product strategy for..."`

**Tests:**
- Unit: `ABTestResult.passes_oec` = True si `delta_mean >= 0.08` (8pp en escala 0–1)
- Unit: `run_ab_test()` con mock brain + mock evaluator → `ABTestResult` con campos correctos
- Edge: solo 1 par → `ABTestResult` válido (no crash con N=1)

**Acceptance:**
- [ ] `evaluate.py` ejecuta sin error con brains mock
- [ ] `tasks/rag-evaluation-results.json` creado después de `run_ab_test()`
- [ ] `passes_oec` = True si delta >= 8pp — False si no
- [ ] Tests de A/B framework pasan

---

### 21.5B: Recall@5 Offline Evaluation

**Qué:** Script que mide Recall@5 en un conjunto de 10 pares etiquetados manualmente para Brain #1 domain_knowledge.

**Backend (`apps/api/`):**
- `apps/api/mastermind_cli/rag/recall_eval.py`:
  - Lee `tasks/rag-eval-pairs.json` — lista de 10 `{query, relevant_chunk_refs: [str]}` pares etiquetados
  - Para cada par: llama `similarity_search(brain_id, "domain_knowledge", query, limit=5)` → verifica si algún chunk relevante aparece en top-5
  - Calcula Recall@5 = `hits / total_queries`
  - Guarda en `tasks/rag-recall-results.json`: `{recall_at_5: float, passes_sli: bool, hits: int, total: int}`
- Crear `tasks/rag-eval-pairs.json` con 10 pares de muestra (pueden ser placeholders iniciales, se populan durante la fase)

**Tests:**
- Unit: 7 de 10 pares con hit → `recall_at_5 = 0.70`, `passes_sli = True`
- Unit: 6 de 10 pares con hit → `recall_at_5 = 0.60`, `passes_sli = False`
- Unit: corpus vacío → Recall@5 = 0.0, `passes_sli = False` (no crash)

**Acceptance:**
- [ ] `tasks/rag-eval-pairs.json` existe con al menos 10 pares
- [ ] `recall_eval.py` calcula Recall@5 correctamente
- [ ] `tasks/rag-recall-results.json` creado con `recall_at_5` y `passes_sli`
- [ ] Tests de recall pasan

---

### 21.5C: Gate Decision

**Qué:** Verificar que OEC y SLI-1 están cumplidos. Documentar resultado en `tasks/gate-21.5-result.md`. Si no pasa: diagnóstico.

**Artefactos necesarios:**
- `tasks/rag-evaluation-results.json` con `passes_oec: true`
- `tasks/rag-recall-results.json` con `passes_sli: true`
- Latency: LangSmith dashboard muestra P99 < 200ms para retrieval
- Zero contamination: verificar manualmente en sample de chunks recuperados

**`tasks/gate-21.5-result.md` estructura:**
```markdown
# RAG Evaluation Gate — Phase 21.5

**Date:** YYYY-MM-DD
**Status:** PASS | FAIL

## OEC
- quality_score delta: X.X pp (target: >= 8pp)
- Pairs evaluated: N
- Result: PASS | FAIL

## SLI-1: Recall@5
- Score: X.XX (target: >= 0.70)
- Result: PASS | FAIL

## SLI-3: Latency P99
- Retrieval P99: Xms (target: < 200ms)
- Result: PASS | FAIL

## SLI-5: Zero Contamination
- Self-similarity check: PASS | FAIL

## Conclusion
[PASS: Proceed to Phase 22] | [FAIL: Diagnose and fix before continuing]
```

**Acceptance:**
- [ ] `tasks/gate-21.5-result.md` existe y tiene `Status: PASS`
- [ ] `passes_oec: true` en `rag-evaluation-results.json`
- [ ] `passes_sli: true` en `rag-recall-results.json`
- [ ] Latency verificada en LangSmith (o via timing logs si LangSmith no disponible)
- [ ] **Si FAIL: STOP — no continuar a Phase 22**

---

## PHASE 22: Knowledge Ingestion (Manual One-Shot)

**Objetivo:** Cargar el corpus de conocimiento en el vector store de los 7 brains.
**Tiempo estimado:** 2-3 días
**Depende de:** Phase 21.5 con gate PASSED

### 22A: Ingest Script + Chunking Logic

**Qué:** Script `apps/api/mastermind_cli/rag/ingest.py` — idempotent, configurable, reporta N chunks por brain.

**Backend (`apps/api/`):**
- `ingest.py` CLI:
  ```
  uv run python -m mastermind_cli.rag.ingest \
    --brain-id brain-01 \
    --collection domain_knowledge \
    --source-dir docs/software-development/sources/
  ```
- Chunking strategy:
  - `domain_knowledge`: split por sección H2 (regex `^## `), overlap de 128 tokens entre chunks. Tamaño máximo: 512 tokens.
  - `project_memory`: split por bullet point (`^- ` o `^  - `). Sin overlap (bullets son atómicos).
- Por chunk: calcular `chunk_hash = SHA256(brain_id + collection + chunk_text)` — `ON CONFLICT (chunk_hash) DO NOTHING` para idempotencia
- Embed con `EmbeddingService.encode()` en batch (no uno por uno)
- Reporte al finalizar: `brain-01 / domain_knowledge: 142 chunks ingested (3 skipped — duplicates)`

**Tests:**
- Unit: `chunk_by_h2(text)` con documento de 3 secciones H2 → retorna 3 chunks
- Unit: `chunk_by_bullets(text)` con 5 bullets → retorna 5 chunks
- Unit: re-run de ingest con mismo contenido → `SELECT COUNT(*)` no cambia (idempotencia)
- Unit: `ingest()` con directorio vacío → retorna `{chunks_ingested: 0, skipped: 0}` sin error

**Acceptance:**
- [ ] `ingest.py` corre sin error desde CLI
- [ ] Re-run idempotente: `COUNT(*)` igual antes y después de segunda ejecución
- [ ] Chunks ingested reportados al finalizar
- [ ] Tests de chunking e idempotencia pasan

---

### 22B: Execute Ingestion — 7 Brains × 2 Collections

**Qué:** Ejecutar el script de ingestion para todos los brains y sus colecciones. Verificar con query SQL.

**Brains y fuentes:**

| Brain | domain_knowledge source | project_memory source |
|-------|------------------------|-----------------------|
| brain-01 | `docs/software-development/sources/` (10 FUENTE-*.md) | `.planning/BRAIN-FEED-01-product.md` |
| brain-02 | `docs/software-development/sources/` (filtrado por skills_covered) | `.planning/BRAIN-FEED-02-ux.md` |
| brain-03 | `docs/software-development/sources/` (filtrado) | `.planning/BRAIN-FEED-03-ui.md` |
| brain-04 | `docs/software-development/sources/` (filtrado) | `.planning/BRAIN-FEED-04-frontend.md` |
| brain-05 | `docs/software-development/sources/` (filtrado) | `.planning/BRAIN-FEED-05-backend.md` |
| brain-06 | `docs/software-development/sources/` (filtrado) | `.planning/BRAIN-FEED-06-qa.md` |
| brain-07 | `docs/software-development/sources/` (filtrado) | `.planning/BRAIN-FEED-07-growth.md` (o `.planning/BRAIN-FEED.md` global) |

**Nota:** Si un BRAIN-FEED-NN-domain.md no existe para un brain, usar el BRAIN-FEED.md global para project_memory. Documentar en el reporte.

**Verificación final:**
```sql
SELECT brain_id, collection_type, COUNT(*) as chunks
FROM brain_embeddings
GROUP BY brain_id, collection_type
ORDER BY brain_id, collection_type;
```
Debe retornar 14 filas (7 brains × 2 collections), con `chunks > 0`.

**Acceptance:**
- [ ] `SELECT COUNT(*) FROM brain_embeddings` > 0
- [ ] Query GROUP BY retorna 14 filas con `chunks > 0` en cada fila
- [ ] Todos los 7 brains tienen entries para ambas collections
- [ ] Reporte de ingestion guardado en `tasks/ingestion-report.md`

---

## PHASE 23: RAG Scale-Out — Brains 2–7

**Objetivo:** Los 6 brains restantes con RAG funcional, validados con Recall@5 >= 0.70 cada uno.
**Tiempo estimado:** 4-5 días
**Depende de:** Phase 22 (ingestion completa)

### 23A: RAG Integration — Brains 2–7

**Qué:** Replicar el mismo patrón de Brain #1 a los 6 brains restantes. No es reescritura — es parametrización del mismo código.

**Backend (`apps/api/`):**
- `RAGContextBuilder.build(brain_id, query)` ya acepta cualquier `brain_id` — verificar que el routing es correcto para cada brain
- Activar `rag_enabled` en los agent configs de Brains 2–7 (mismo flag que Brain #1)
- Para cada brain: ejecutar una sesión de test → verificar `rag_enabled=true` en `experience_records`
- Los 6 brains deben seguir el mismo patrón: top-5 domain_knowledge + top-3 project_memory

**Tests:**
- Integration (por cada brain 2–7): `build(brain_id="brain-02", query="UX research...")` → retorna bloque con chunks (asumiendo colección populated)
- Integration: sesión de Brain #2 → `custom_metadata->>'rag_enabled' = 'true'` en experience_records

**Acceptance:**
- [ ] Los 7 brains tienen `rag_enabled: true` en sus agent configs
- [ ] `experience_records` de cada brain tiene `rag_enabled=true` después de una sesión de test
- [ ] Tests de integración pasan para los 6 brains nuevos

---

### 23B: Recall@5 + OEC Validation — Todos los Brains

**Qué:** Medir Recall@5 para los 6 brains nuevos. OEC confirmado en promedio de los 7. LangSmith dashboard operativo.

**Artefactos:**
- `tasks/rag-eval-pairs.json` extendido con 10 pares por brain (#2–#7) — total 70 pares
- `recall_eval.py` extendido para evaluar múltiples brains en batch
- `tasks/rag-recall-results-all.json`: Recall@5 por brain, avg total

**Criterios de scale-out:**
- Recall@5 >= 0.70 en TODOS los 7 brains (hard requirement)
- Si algún brain no alcanza 0.70: diagnosticar chunking o modelo de embeddings para esa colección específica — no bloquear los brains que sí pasaron

**LangSmith:**
- Dashboard muestra trazas de todos los providers activos
- Desglose de costo por brain visible
- Latency por brain documentada

**Verificación final:**
```sql
SELECT
  e.brain_id,
  COUNT(*) AS sessions_with_rag,
  AVG((e.quality_score)::float) AS avg_quality_score
FROM experience_records e
WHERE e.custom_metadata->>'rag_enabled' = 'true'
GROUP BY e.brain_id
ORDER BY e.brain_id;
```

**Acceptance:**
- [ ] Recall@5 >= 0.70 en los 7 brains
- [ ] OEC: quality_score delta >= +8pp en promedio de los 7 brains vs baseline cold
- [ ] Latency guardrail: ningún brain supera baseline + 500ms en P99
- [ ] LangSmith dashboard muestra trazas de todos los providers con desglose de costo
- [ ] `tasks/rag-recall-results-all.json` documenta Recall@5 por brain
- [ ] Tests de validación pasan

---

## Notas de Ejecución

### TDD estricto
Cada subtask comienza con tests RED. Implementación viene después. No hay "agrego tests al final."

### Vertical slice estricto
Nunca cerrar una subtask con solo un lado completo. Tests + implementación juntos.

### Gate Phase 21.5 es bloqueante
No continuar a Phase 22 si el gate no pasa. Documentar en `tasks/gate-21.5-result.md` el diagnóstico.

### Idempotencia del ingest script
Diseñado para re-runs seguros. `chunk_hash` garantiza que re-correr el script no duplica datos.

### Knowledge Contamination Loop — invariante
`project_memory` = logs operacionales de BRAIN-FEED. `domain_knowledge` = libros destilados de docs/. Nunca mezclar.

### Orden de commits
Un commit por subtask completada. Mensaje: `feat(v3.2/[phase-id]): [descripción]`. Ejemplo: `feat(v3.2/20A): add brain_embeddings migration with HNSW index`.
