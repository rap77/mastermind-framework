## PHASE 20: pgvector Schema + LangSmith

- [ ] 20: pgvector Schema + LangSmith
  - [ ] 20.01: Backend: crear migration Alembic para tabla `brain_embeddings` con columnas: id UUID PK, brain_id TEXT, collection_type TEXT CHECK(IN 'domain_knowledge','project_memory'), source_ref TEXT, chunk_text TEXT, chunk_hash TEXT UNIQUE, embedding vector(768), created_at TIMESTAMPTZ
  - [ ] 20.02: Backend: crear HNSW index en columna `embedding` con `m=16, ef_construction=64` usando `vector_cosine_ops`
  - [ ] 20.03: Backend: ejecutar `alembic upgrade head` y verificar schema con `\d brain_embeddings`
  - [ ] 20.04: Tests: unit test — `SELECT to_regclass('public.brain_embeddings') IS NOT NULL` pasa
  - [ ] 20.05: Tests: unit test — HNSW index existe en `pg_indexes` para `brain_embeddings`
  - [ ] 20.06: Tests: unit test — INSERT de embedding dummy 768-dim → SELECT retorna sin error
  - [ ] 20.07: Verify: `SELECT column_name FROM information_schema.columns WHERE table_name='brain_embeddings'` retorna todas las columnas esperadas
  - [ ] 20.08: Backend: `uv add sentence-transformers` — mover de dev-deps a deps en `pyproject.toml`
  - [ ] 20.09: Backend: crear `apps/api/mastermind_cli/rag/__init__.py` con exports
  - [ ] 20.10: Backend: crear `apps/api/mastermind_cli/rag/embed.py` con `load_model()`, `encode(texts)`, `compute_hash(text)`
  - [ ] 20.11: Backend: crear `apps/api/mastermind_cli/rag/search.py` con `similarity_search(conn, brain_id, collection, query_text, limit=5)`
  - [ ] 20.12: Tests: unit test — `encode(["hello world"])` retorna lista de 768 floats
  - [ ] 20.13: Tests: unit test — `compute_hash("text")` retorna string hex de 64 chars
  - [ ] 20.14: Tests: integration — `similarity_search()` con fixture en DB de test retorna lista con chunk_text y score en [0.0, 1.0]
  - [ ] 20.15: Tests: edge case — `similarity_search()` con colección vacía retorna lista vacía sin crash
  - [ ] 20.16: Verify: `from mastermind_cli.rag import similarity_search` no levanta ImportError
  - [ ] 20.17: Backend: `uv add langsmith` — agregar a runtime deps en `pyproject.toml`
  - [ ] 20.18: Backend: agregar `LANGSMITH_API_KEY` y `LANGSMITH_PROJECT` a `.env.example`
  - [ ] 20.19: Backend: instrumentar `DynamicDispatchEngine.dispatch()` con `@traceable(name="brain_dispatch")` y metadata: brain_id, provider, model, profile
  - [ ] 20.20: Backend: crear `apps/api/mastermind_cli/rag/baseline.py` — lee últimos N records de ExperienceLogger para brain-01 sin rag_enabled, calcula quality_score mean y guarda en `tasks/rag-baseline.json`
  - [ ] 20.21: Tests: unit test — `@traceable` decorator no rompe dispatch con mock LangSmith client
  - [ ] 20.22: Tests: unit test — `baseline.py` calcula mean correctamente con fixture de 5 records
  - [ ] 20.23: Verify: `sentence-transformers` en `[project.dependencies]` de `pyproject.toml` (no en dev-dependencies)
  - [ ] 20.24: Verify: `langsmith` en `[project.dependencies]` de `pyproject.toml`
  - [ ] 20.25: Verify: `tasks/rag-baseline.json` existe con estructura correcta (sessions_evaluated, quality_score_mean, oec_target)

## PHASE 21: RAG Pilot — Brain #1 Only

- [ ] 21: RAG Pilot — Brain #1 Only
  - [ ] 21.01: Backend: crear `apps/api/mastermind_cli/rag/context_builder.py` con clase `RAGContextBuilder`
  - [ ] 21.02: Backend: implementar `RAGContextBuilder.__init__(conn: asyncpg.Connection)`
  - [ ] 21.03: Backend: implementar `async RAGContextBuilder.build(brain_id: str, query: str) -> str` — top-5 domain_knowledge + top-3 project_memory
  - [ ] 21.04: Backend: formato del bloque — sección `[RETRIEVED CONTEXT]` con subsecciones `--- domain_knowledge (top-5) ---` y `--- project_memory (top-3) ---` con scores y source_ref
  - [ ] 21.05: Backend: si colección vacía → omitir esa subsección (no crash, no placeholder)
  - [ ] 21.06: Backend: si ambas colecciones vacías → retornar string vacío `""`
  - [ ] 21.07: Tests: unit test — `build()` con mock `similarity_search` retorna string con `[RETRIEVED CONTEXT]` y `[END RETRIEVED CONTEXT]`
  - [ ] 21.08: Tests: unit test — `build()` con ambas colecciones vacías retorna `""` (no bloque vacío)
  - [ ] 21.09: Tests: unit test — `build()` con solo domain_knowledge omite sección project_memory
  - [ ] 21.10: Tests: timing test — `build()` con fixture real tarda < 200ms (medido con `time.perf_counter`)
  - [ ] 21.11: Verify: `from mastermind_cli.rag.context_builder import RAGContextBuilder` no levanta ImportError
  - [ ] 21.12: Backend: identificar punto de construcción del system prompt para Brain #1 (DynamicDispatchEngine o brain agent runner)
  - [ ] 21.13: Backend: integrar `RAGContextBuilder.build()` antes de la llamada LLM de Brain #1 — append del bloque al system prompt si no vacío
  - [ ] 21.14: Backend: no agregar bloque vacío al system prompt si `rag_context == ""`
  - [ ] 21.15: Tests: unit test — mock `build()` retorna bloque → system prompt incluye `[RETRIEVED CONTEXT]`
  - [ ] 21.16: Tests: unit test — mock `build()` retorna `""` → system prompt NO incluye `[RETRIEVED CONTEXT]`
  - [ ] 21.17: Tests: integration — Brain #1 con colecciones vacías responde sin error, `rag_enabled=false` en custom_metadata
  - [ ] 21.18: Backend: pasar `rag_enabled: bool` como campo en `custom_metadata` al llamar `ExperienceLogger.log_execution()`
  - [ ] 21.19: Backend: `rag_enabled = rag_context != ""` — True solo si se recuperó contexto real
  - [ ] 21.20: Backend: LangSmith span de la sesión incluye `rag_enabled` en metadata
  - [ ] 21.21: Tests: unit test — `log_execution(custom_metadata={"rag_enabled": True})` → `SELECT custom_metadata->>'rag_enabled'` retorna `"true"`
  - [ ] 21.22: Tests: integration — ejecutar Brain #1 → `SELECT custom_metadata FROM experience_records ORDER BY created_at DESC LIMIT 1` tiene key `rag_enabled`
  - [ ] 21.23: Verify: Brain #1 llama `RAGContextBuilder.build()` antes de cada invocación LLM
  - [ ] 21.24: Verify: `experience_records.custom_metadata` tiene `rag_enabled` key después de sesión de Brain #1

## PHASE 21.5: RAG Evaluation Gate

- [ ] 21.5: RAG Evaluation Gate (HARD GATE — no continuar sin pasar)
  - [ ] 21.5.01: Backend: crear `apps/api/mastermind_cli/rag/evaluate.py` con función `run_ab_test(brief, pairs=5) -> ABTestResult`
  - [ ] 21.5.02: Backend: `ABTestResult` dataclass — rag_scores: list[float], cold_scores: list[float], delta_mean: float, delta_std: float, passes_oec: bool
  - [ ] 21.5.03: Backend: `passes_oec = delta_mean >= 0.08` (8pp en escala 0–1 = 8 puntos en escala 0–100)
  - [ ] 21.5.04: Backend: `run_ab_test()` ejecuta mismo brief con RAG-enabled y cold para cada par, evalúa con Brain #7 automático
  - [ ] 21.5.05: Backend: guardar resultado en `tasks/rag-evaluation-results.json` con estructura: {rag_scores, cold_scores, delta_mean, delta_std, passes_oec, pairs_evaluated, measured_at}
  - [ ] 21.5.06: Tests: unit test — `delta_mean = 0.09` → `passes_oec = True`
  - [ ] 21.5.07: Tests: unit test — `delta_mean = 0.07` → `passes_oec = False`
  - [ ] 21.5.08: Tests: unit test — `run_ab_test()` con mock brain + mock Brain #7 → `ABTestResult` con campos correctos
  - [ ] 21.5.09: Tests: edge case — N=1 par → `ABTestResult` válido sin crash
  - [ ] 21.5.10: Backend: crear `tasks/rag-eval-pairs.json` con 10 pares etiquetados para Brain #1 domain_knowledge — estructura: [{query, relevant_chunk_refs: [str]}]
  - [ ] 21.5.11: Backend: crear `apps/api/mastermind_cli/rag/recall_eval.py` con función `evaluate_recall(brain_id, collection, eval_pairs_path, limit=5) -> RecallResult`
  - [ ] 21.5.12: Backend: `RecallResult` — recall_at_5: float, passes_sli: bool, hits: int, total: int
  - [ ] 21.5.13: Backend: `passes_sli = recall_at_5 >= 0.70`
  - [ ] 21.5.14: Backend: guardar en `tasks/rag-recall-results.json`
  - [ ] 21.5.15: Tests: unit test — 7 de 10 pares con hit → `recall_at_5 = 0.70`, `passes_sli = True`
  - [ ] 21.5.16: Tests: unit test — 6 de 10 pares con hit → `recall_at_5 = 0.60`, `passes_sli = False`
  - [ ] 21.5.17: Tests: unit test — corpus vacío → `recall_at_5 = 0.0`, `passes_sli = False` sin crash
  - [ ] 21.5.18: Verify: ejecutar `run_ab_test()` con 5 pares reales — `tasks/rag-evaluation-results.json` creado
  - [ ] 21.5.19: Verify: ejecutar `evaluate_recall()` — `tasks/rag-recall-results.json` creado
  - [ ] 21.5.20: Verify: LangSmith traces muestran retrieval P99 < 200ms para Brain #1 (o timing logs si LangSmith no disponible)
  - [ ] 21.5.21: Verify: sample manual de chunks recuperados — no incluyen respuestas previas del mismo brain (self-similarity < 0.85)
  - [ ] 21.5.22: Crear `tasks/gate-21.5-result.md` con Status PASS o FAIL y evidencia de cada criterio (OEC, SLI-1, latency, contamination)
  - [ ] 21.5.23: GATE CHECK: `passes_oec: true` en `rag-evaluation-results.json`
  - [ ] 21.5.24: GATE CHECK: `passes_sli: true` en `rag-recall-results.json`
  - [ ] 21.5.25: GATE CHECK: `Status: PASS` en `tasks/gate-21.5-result.md` — SI FAIL: STOP, diagnosticar antes de continuar

## PHASE 22: Knowledge Ingestion (Manual One-Shot)

- [ ] 22: Knowledge Ingestion (Manual One-Shot)
  - [ ] 22.01: Backend: crear `apps/api/mastermind_cli/rag/ingest.py` CLI con argumentos `--brain-id`, `--collection`, `--source-dir`
  - [ ] 22.02: Backend: implementar chunking strategy para `domain_knowledge` — split por sección H2 (regex `^## `), overlap 128 tokens, máximo 512 tokens por chunk
  - [ ] 22.03: Backend: implementar chunking strategy para `project_memory` — split por bullet point (`^- ` o `^  - `), sin overlap
  - [ ] 22.04: Backend: `chunk_hash = SHA256(brain_id + collection + chunk_text)` — `INSERT ... ON CONFLICT (chunk_hash) DO NOTHING` para idempotencia
  - [ ] 22.05: Backend: embed en batch (no uno por uno) usando `EmbeddingService.encode()`
  - [ ] 22.06: Backend: reporte al finalizar: `brain-01 / domain_knowledge: N chunks ingested (M skipped — duplicates)`
  - [ ] 22.07: Tests: unit test — `chunk_by_h2(text)` con 3 secciones H2 → retorna 3 chunks
  - [ ] 22.08: Tests: unit test — `chunk_by_bullets(text)` con 5 bullets → retorna 5 chunks
  - [ ] 22.09: Tests: unit test — re-run ingest con mismo contenido → `COUNT(*)` no cambia (idempotencia verificada)
  - [ ] 22.10: Tests: unit test — directorio vacío → retorna `{chunks_ingested: 0, skipped: 0}` sin error
  - [ ] 22.11: Verify: `ingest.py` corre sin error con `--help` y con directorio de test
  - [ ] 22.12: Ejecutar: `uv run python -m mastermind_cli.rag.ingest --brain-id brain-01 --collection domain_knowledge --source-dir docs/software-development/sources/`
  - [ ] 22.13: Ejecutar: `uv run python -m mastermind_cli.rag.ingest --brain-id brain-01 --collection project_memory --source-dir .planning/` (BRAIN-FEED-01 o fallback a BRAIN-FEED.md)
  - [ ] 22.14: Ejecutar: ingest domain_knowledge para brains 02–07 (1 comando por brain, fuente filtrada por skills_covered si aplica)
  - [ ] 22.15: Ejecutar: ingest project_memory para brains 02–07 (BRAIN-FEED-NN-domain.md respectivo o fallback a BRAIN-FEED.md)
  - [ ] 22.16: Verify: `SELECT brain_id, collection_type, COUNT(*) FROM brain_embeddings GROUP BY 1, 2 ORDER BY 1, 2` retorna 14 filas con chunks > 0
  - [ ] 22.17: Verify: `SELECT COUNT(*) FROM brain_embeddings` > 0
  - [ ] 22.18: Crear `tasks/ingestion-report.md` con: chunks por brain+collection, fecha, notas de fallbacks (si algún BRAIN-FEED-NN no existía)

## PHASE 23: RAG Scale-Out — Brains 2–7

- [ ] 23: RAG Scale-Out — Brains 2–7
  - [ ] 23.01: Backend: verificar que `RAGContextBuilder.build(brain_id, query)` ya acepta cualquier brain_id sin cambios de código
  - [ ] 23.02: Backend: activar `rag_enabled: true` en agent config de Brain #2 (UX Research)
  - [ ] 23.03: Backend: activar `rag_enabled: true` en agent config de Brain #3 (UI Design)
  - [ ] 23.04: Backend: activar `rag_enabled: true` en agent config de Brain #4 (Frontend)
  - [ ] 23.05: Backend: activar `rag_enabled: true` en agent config de Brain #5 (Backend)
  - [ ] 23.06: Backend: activar `rag_enabled: true` en agent config de Brain #6 (QA/DevOps)
  - [ ] 23.07: Backend: activar `rag_enabled: true` en agent config de Brain #7 (Growth/Data)
  - [ ] 23.08: Tests: integration — `build(brain_id="brain-02", query="UX research...")` con colecciones populadas retorna bloque con chunks
  - [ ] 23.09: Tests: integration — sesión de Brain #2 → `custom_metadata->>'rag_enabled' = 'true'` en experience_records
  - [ ] 23.10: Tests: integration — sesión de Brain #3 → `custom_metadata->>'rag_enabled' = 'true'` en experience_records
  - [ ] 23.11: Tests: integration — sesión de Brain #4 → `custom_metadata->>'rag_enabled' = 'true'` en experience_records
  - [ ] 23.12: Tests: integration — sesión de Brain #5 → `custom_metadata->>'rag_enabled' = 'true'` en experience_records
  - [ ] 23.13: Tests: integration — sesión de Brain #6 → `custom_metadata->>'rag_enabled' = 'true'` en experience_records
  - [ ] 23.14: Backend: extender `tasks/rag-eval-pairs.json` con 10 pares para cada brain #2–#7 (total 70 pares)
  - [ ] 23.15: Backend: extender `recall_eval.py` para evaluar múltiples brains en batch — argumento `--all-brains`
  - [ ] 23.16: Ejecutar: `recall_eval.py --all-brains` → guardar resultado en `tasks/rag-recall-results-all.json`
  - [ ] 23.17: Tests: unit test — `evaluate_recall()` con batch de 7 brains → retorna dict brain_id → RecallResult
  - [ ] 23.18: Verify: `SELECT brain_id, AVG((quality_score)::float) FROM experience_records WHERE custom_metadata->>'rag_enabled'='true' GROUP BY brain_id` retorna 7 filas
  - [ ] 23.19: Verify: Recall@5 >= 0.70 en `rag-recall-results-all.json` para todos los 7 brains
  - [ ] 23.20: Verify: OEC cumplido — quality_score delta >= +8pp en promedio de los 7 brains (comparar con `tasks/rag-baseline.json`)
  - [ ] 23.21: Verify: LangSmith dashboard muestra trazas de todos los providers activos con desglose de costo por brain
  - [ ] 23.22: Verify: ningún brain supera baseline + 500ms en P99 (LangSmith latency report)
  - [ ] 23.23: Documentar resultado final en `tasks/v3.2-completion-report.md` con: Recall@5 por brain, OEC delta, latency P99 por brain, LangSmith dashboard URL
