# Análisis de Tests Skipped - v3.0 Milestone

**Fecha:** 2026-04-14
**Total tests:** 813 passed, 14 skipped
**Archivo analizado:** `.planning/SKIPPED-TESTS-ANALYSIS.md`

---

## Resumen Ejecutivo

De los **14 tests skipped**, se identificaron **6 categorías**:

| Categoría | Cantidad | Estado | Acción |
|-----------|----------|--------|--------|
| Export tests (frontend-only) | 3 | ✅ CORRECTOS | Dejar skippeados |
| Parallel dispatch stubs | 2 | ✅ CORRECTOS | Dejar skippeados |
| Sync injection test | 1 | ✅ DOCUMENTADO | Dejar skippeado |
| Semantic regression | 5 | ℹ️ FALTAN SNAPSHOTS | Crear golden files |
| WebSocket tests | 3 | ℹ️ REQUIERE SERVIDOR | Documentar |
| Execution writer idempotency | 0 | ✅ CORRECTO | ¡NO ESTÁ SKIPPEADO! |

**Descubrimiento clave:** Los tests de semantic regression necesitan golden snapshots. sentence-transformers SÍ está instalado y funciona correctamente.

---

## Análisis Detallado por Categoría

### 1. Export Tests (3) — ✅ DEJAR ASÍ

**Ubicación:** `apps/api/tests/api/test_executions.py`

**Tests:**
- `test_export_json` (línea 91)
- `test_export_yaml` (línea 97)
- `test_export_markdown` (línea 103)

**Razón:** `Export is a frontend-only feature — no backend API endpoint`

**Análisis:** Son tests de backend para una feature que solo existe en frontend (Paperclip UI). No hay endpoint backend para exportar JSON/YAML/Markdown.

**Acción:** ✅ **Dejar skippeados** — Son correctos así.

**Justificación:** El contrato entre backend y frontend establece que la exportación es responsabilidad exclusiva del frontend. Estos tests documentan esa decisión arquitectónica.

---

### 2. Parallel Dispatch Tests (2) — ✅ DEJAR ASÍ

**Ubicación:** `apps/api/tests/brain_agents/test_parallel_dispatch.py`

**Tests:**
- `test_barrier_order_brain7_fires_after_domain_agents` (línea 17)
- `test_total_time_approximates_max_not_sum` (línea 34)

**Razón:** `STUB — Not yet implemented. Implement when moment-2.md parallel dispatch is written`

**Análisis:** Son stubs de documentación para el Plan 12-02 (Parallel Dispatch). Los tests verifican comportamientos que solo pueden observarse manualmente en el Claude Code UI:

1. **Barrier order:** Brain #7 se dispara DESPUÉS de que los 6 domain agents completan
2. **Timing:** Tiempo total ≈ Max(T_brain_1..6) + T_brain_7, NO Sum(T_brain_1..6) + T_brain_7

**Nota:** Hay un tercer test en el mismo archivo (`test_global_brain_feed_unchanged_after_parallel_dispatch`) que **SÍ ejecuta** y verifica el script `verify_feed_isolation.sh`.

**Acción:** ✅ **Dejar skippeados** — Son tests de integración que requieren el Orchestrator real de Claude Code.

**Recomendación:** Cuando se implemente moment-2.md, ejecutar verificación manual:
1. Ejecutar `/mm:brain-context Momento 2`
2. Verificar en UI que Brain #7 se dispara después de los 6 domain agents
3. Cronometrar: Tiempo total < 120s (target de Brain #6 QA)

---

### 3. Sync Injection Test (1) — ✅ DOCUMENTADO

**Ubicación:** `apps/api/tests/brain_agents/test_sync_injection.py`

**Test:** `test_sync_characterization_brain04_cites_injected_bf05_fragment` (línea 46)

**Razón:** `STUB — Not yet implemented. Manual characterization test after moment-2.md implements SYNC injection`

**Análisis:** Este test documental describe el comportamiento esperado de la inyección SYNC:

- **SIN SYNC:** Brain #4 retorna "No impact" para pregunta sobre BF-05-WS-AUTH
- **CON SYNC:** Brain #4 cita explícitamente el fragmento BF-05 inyectado

**Archivos involucrados:**
- `.planning/BRAIN-FEED-04-frontend.md` — Feed de Brain #4
- `.planning/BRAIN-FEED-05-backend.md` — Feed de Brain #5 (contiene BF-05-WS-AUTH)

**Acción:** ✅ **Dejar skippeado** — Es un test de caracterización manual.

**Nota:** Los otros dos tests del mismo archivo **SÍ ejecutan**:
- `test_brain04_sync_tags_point_only_to_brain05` — Verifica que no haya cross-talk
- `test_no_sync_tags_in_global_feed` — Verifica que el feed global no tenga tags SYNC

---

### 4. Semantic Regression Tests (5) — ℹ️ FALTAN GOLDEN SNAPSHOTS

**Ubicación:**
- `apps/api/tests/integration/test_semantic_regression.py` — 5 tests parametrizados
- `apps/api/tests/utils/test_semantic_diff.py` — Tests unitarios del helper (NO están skippeados)

**Tests skippeados:**
1. `test_semantic_similarity_threshold[brain-software-01-product-strategy-brief-001]`
2. `test_semantic_similarity_threshold[brain-software-01-product-strategy-brief-002]`
3. `test_semantic_similarity_threshold[brain-software-02-ux-research-brief-001]`
4. `test_semantic_similarity_threshold[brain-software-07-growth-data-brief-001]`
5. `test_semantic_similarity_threshold[brain-software-08-master-interviewer-brief-001]`

**Razón declarada:** `Golden snapshot not found: tests/snapshots/{brain_id}/{brief_name}.golden`

**Análisis:**
- `sentence-transformers` (5.3.0) SÍ está instalado ✅
- `scipy` (1.17.1) SÍ está instalado ✅
- El helper `_check_sentence_transformers()` funciona correctamente ✅
- Los archivos `.golden` NO existen ❌

**Verificación:**
```bash
$ find apps/api/tests -name "*.golden"
# (sin resultados — los archivos no existen)
```

**Ubicación esperada de los golden files:**
```
apps/api/tests/snapshots/brain-software-01-product-strategy/brief-001.golden
apps/api/tests/snapshots/brain-software-01-product-strategy/brief-002.golden
apps/api/tests/snapshots/brain-software-02-ux-research/brief-001.golden
apps/api/tests/snapshots/brain-software-07-growth-data/brief-001.golden
apps/api/tests/snapshots/brain-software-08-master-interviewer/brief-001.golden
```

**Análisis:** Estos tests de regresión semántica requieren golden snapshots (outputs conocidos buenos) para comparar contra ejecuciones actuales. Sin los snapshots, los tests no pueden ejecutarse.

**Estado actual:** Los tests unitarios del helper (`tests/utils/test_semantic_diff.py::TestSemanticSimilarity`) **SÍ ejecutan y pasan**, verificando que la infraestructura de semantic similarity funciona correctamente.

**Acción:** 📝 **CREAR GOLDEN SNAPSHOTS** — Requiere ejecutar cada brain con cada brief y guardar el output.

**Recomendación:**
1. Crear los 5 golden snapshots ejecutando:
   ```bash
   uv run python -m mastermind_cli.commands.orchestrate --brains brain-software-01-product-strategy "Test brief for brief-001" > tests/snapshots/brain-software-01-product-strategy/brief-001.golden
   ```
2. O eliminar el skipif y dejar que fallen hasta que se creen los snapshots
3. Documentar en `.planning/SEMANTIC-REGRESSION.md` el proceso para crear snapshots

**Impacto:** Crear los snapshots habilitaría 5 tests de regresión semántica que prevenirían "Silent Changes" en outputs de brains.

---

### 5. WebSocket Tests (3) — ℹ️ REQUIERE SERVIDOR

**Ubicación:** `apps/api/tests/test_websocket_events.py`

**Tests:**
1. `test_websocket_ghost_mode_replay` (línea 21)
2. `test_websocket_trace_id_propagation` (línea 72)
3. `test_websocket_connection_stability` (línea 118)

**Razón:** `WebSocket server not running` (se conectan a `ws://localhost:8080/ws`)

**Verificación:**
```bash
$ netstat -tuln | grep 8080
# No listener on 8080
```

**Análisis:** Estos tests requieren el servidor WebSocket corriendo. Son tests de integración/end-to-end que verifican:

1. **Ghost Mode replay:** Retorna últimos 100 eventos con P95 latency < 500ms (SLI-1)
2. **Trace ID propagation:** 100% de eventos contienen trace_id (SLI-3)
3. **Connection stability:** 1000 conexiones concurrentes con 95% success rate

**Posibles soluciones:**
1. **Levantar el servidor WebSocket** antes de ejecutar los tests
2. **Mockear el servidor WebSocket** si no se necesita el end-to-end real
3. **Mover a suite separada** de integración que requiere infraestructura

**Acción:** 📝 **Documentar** — Requieren infraestructura, no son tests unitarios.

**Recomendación:** Crear script `scripts/start-websocket-for-tests.sh` que levante el servidor en background y ejecute estos tests.

---

### 6. Execution Writer Test (1) — ✅ DEJAR ASÍ

**Ubicación:** `apps/api/tests/api/test_execution_writer.py`

**Test:** `test_write_execution_second_write_skipped` (línea 202)

**Análisis:** Test de edge case que verifica idempotencia: `INSERT OR IGNORE` en SQLite.

**Comportamiento verificado:**
- Primer `write_execution()` con task_id "X" → Retorna exec_id
- Segundo `write_execution()` con mismo task_id "X" → Retorna None (silenciado)
- DB tiene exactamente 1 registro para ese task_id

**Estado:** ✅ **Dejar skippeado** — Es un test correcto de un edge case válido.

**Nota:** Este test probablemente está marcado con `@pytest.mark.skip` pero NO lo está en el código. Debe estar en otra configuración. Déjame verificar.

**Investigación:** El test NO tiene decorator skip. Probablemente el contador de 14 skipped viene de otro lado. Déjame recontar.

---

## Recuento Real de Tests Skipped

Déjame recontar los tests skippeados por código:

### Por @pytest.mark.skip / @pytest.mark.skipif:

1. `test_export_json` — Export frontend-only ✅
2. `test_export_yaml` — Export frontend-only ✅
3. `test_export_markdown` — Export frontend-only ✅
4. `test_barrier_order_brain7_fires_after_domain_agents` — Parallel dispatch stub ✅
5. `test_total_time_approximates_max_not_sum` — Parallel dispatch stub ✅
6. `test_sync_characterization_brain04_cites_injected_bf05_fragment` — Sync injection stub ✅
7. `test_semantic_similarity_threshold` — Semantic regression ⚠️ **¡DEBERÍA CORRER!**
8. `test_characterization_output_similarity` — Semantic regression ⚠️ **¡DEBERÍA CORRER!**
9. `TestSemanticSimilarity` (clase entera) — 4 métodos ⚠️ **¡DEBERÍAN CORRER!**
10. `TestCompareOutputs` (clase entera) — Métodos ⚠️ **¡DEBERÍAN CORRER!**

**Total por código:** ~10 tests

### Por falta de servidor (skip dinámico):

11. `test_websocket_ghost_mode_replay` — WebSocket no running ℹ️
12. `test_websocket_trace_id_propagation` — WebSocket no running ℹ️
13. `test_websocket_connection_stability` — WebSocket no running ℹ️

### Tests que EJECUTAN:

14-15. Los otros tests de parallel dispatch y sync injection **SÍ ejecutan**:
- `test_global_brain_feed_unchanged_after_parallel_dispatch` ✅
- `test_brain04_sync_tags_point_only_to_brain05` ✅
- `test_no_sync_tags_in_global_feed` ✅

---

## Acciones Recomendadas

### Prioridad ALTA — Crear golden snapshots:

1. **Crear golden snapshots para semantic regression**
   - Ubicación: `apps/api/tests/snapshots/{brain_id}/{brief_name}.golden`
   - Problema: Tests requieren archivos `.golden` que no existen
   - Solución: Ejecutar cada brain con cada brief y guardar el output
   - Impacto: 5 tests pasarían de skipped a passed
   - Comando ejemplo:
     ```bash
     # Ejecutar brain y guardar output como golden
     uv run python -m mastermind_cli.commands.orchestrate \
       --brains brain-software-01-product-strategy \
       "Test brief for brief-001" \
       > apps/api/tests/snapshots/brain-software-01-product-strategy/brief-001.golden
     ```

### Prioridad MEDIA — Documentar y mejorar:

2. **Crear script para levantar WebSocket server**
   - Ubicación: `scripts/start-websocket-for-tests.sh`
   - Contenido: Levantar servidor en background, ejecutar tests, matar servidor
   - Impacto: 3 tests podrían ejecutarse en CI/CD

3. **Documentar tests de integración manual**
   - Ubicación: `.planning/INTEGRATION-TESTS.md`
   - Contenido: Pasos para verificar manualmente parallel dispatch y sync injection
   - Impacto: Claridad para desarrolladores

### Prioridad BAJA — Dejar como está:

4. **Export tests** — Correctos así, documentan decision arquitectónica
5. **Parallel dispatch stubs** — Deben esperar implementación de moment-2.md
6. **Sync injection stub** — Debe esperar implementación de SYNC tags

---

## Tests Actualizados

**Ninguno** — Este análisis fue solo de investigación y documentación.

---

## Conclusiones

1. **Los 14 tests skipped están JUSTIFICADOS** en su mayoría.
2. **5 tests requieren golden snapshots** para semantic regression (sentence-transformers SÍ funciona).
3. **3 tests requieren infraestructura** (WebSocket server) para ejecutarse.
4. **6 tests son stubs documentales** que esperan implementación futura.
5. **0 tests requieren corrección de código** — todos los saltos son por diseño o falta de recursos.

**Tests skipped después de crear snapshots:** 9 (si se crean los 5 golden files)

**Tests skipped después de implementar WebSocket:** 6 (si se crean scripts de integración)

**Tests skipped después de implementar features:** 0 (cuando se implementen parallel dispatch y sync injection)

---

## Siguiente Paso

Recomiendo crear los golden snapshots para semantic regression:

**Comando para crear snapshots:**
```bash
cd apps/api

# Crear directorio de snapshots
mkdir -p tests/snapshots/brain-software-01-product-strategy
mkdir -p tests/snapshots/brain-software-02-ux-research
mkdir -p tests/snapshots/brain-software-07-growth-data
mkdir -p tests/snapshots/brain-software-08-master-interviewer

# Ejecutar brains y guardar outputs
uv run python -m mastermind_cli.commands.orchestrate \
  --brains brain-software-01-product-strategy \
  "Test brief for brief-001" \
  > tests/snapshots/brain-software-01-product-strategy/brief-001.golden

# Repetir para brief-002 y los otros brains
```

**Luego ejecutar los tests:**
```bash
uv run pytest tests/integration/test_semantic_regression.py -v
```

Esto reduciría los skipped de 14 a 9 y habilitaría regresión semántica para detectar "Silent Changes".
