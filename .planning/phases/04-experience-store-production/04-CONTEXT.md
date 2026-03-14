# Phase 4: Experience Store & Production - Context

**Gathered:** 2026-03-14
**Status:** Ready for planning

## Phase Boundary

Architecture foundation for v3.0 (ML/RAG ready), backward compatibility verification for v1.3.0, and production hardening with CI/CD. This phase ensures the 23 existing brains continue working, establishes the experience logging system for future learning, and implements automated quality gates.

**Out of scope:**
- Full RAG vector database (v3.0+)
- Machine learning auto-improvement training
- Multi-tenant SaaS infrastructure
- Real-time collaborative editing

**Requirements mapeados:** ARCH-01, ARCH-02, ARCH-04, ARCH-05, BC-01, BC-02, BC-03, BC-04, BC-05, TEST-01, TEST-02, TEST-03, TEST-04, TEST-05 (15 requirements)

---

## Implementation Decisions

### Experience Logging Strategy (La Memoria del Sistema)

**Granularidad: JSON Completo**
- Full fidelity logging: inputs, outputs, metadata completos
- Motivación: Debugging de alucinaciones (ver exactamente qué recibió el Brain #23 del Brain #22)
- Motivación: Fine-tuning futuro (LoRA training con JSONs históricos)
- Motivación: RAG nativo sobre outputs pasados para que nuevos brains no repitan errores
- Trade-off: Almacenamiento es barato, datos perdidos son irre recuperables

**PII/Secrets: Semantic Redaction (Pydantic-Aware)**
- Auto-filtrado regex para patrones conocidos (API keys: sk-, mmsk_, emails, DNI/SSN)
- Pydantic SecretStr/exclude=True fields redactados automáticamente
- Dos líneas de defensa: regex + schema-aware redaction
- Output: [REDACTED_SECRET] para sensitive data antes de persistir

**Retención: Archive JSONL**
- Logs de últimos 30 días en SQLite (DB flaca, queries rápidas)
- Logs viejos → .jsonl.gz comprimidos fuera de DB (cron job cada domingo 3AM)
- SQLite health: mantener DB bajo 500MB para Dashboard instantáneo
- WSL2 friendly: .jsonl.gz manipulables con zgrep, jq

**Schema: Extensible JSONB + Lineage & Trace**
- Campos fijos: id, brain_id, input_hash, output_json, timestamp, duration_ms, status, embedding_stub(NULL)
- Campos extensible: custom_metadata JSONB para métricas brain-specific sin ALTER TABLE
- Lineage fields: parent_brain_id, trace_context_id para reconstruir árbol de decisiones
- SQLite JSONB soporta queries nativos sobre custom_metadata

### Brain-to-Brain Protocol (El Sistema Nervioso)

**Modelo de Ejecución: State-Machine Orchestrator + Hybrid Pulse**
- Orchestrator monitorea SQLite, lanza brains cuando dependencias completan (YA IMPLEMENTADO Phase 2)
- Hybrid Pulse: Event-Bus activa brains para máxima velocidad
- Check-in cada 500ms: Orchestrator verifica si algún brain debió activarse y no lo hizo (fallback)
- Combina velocidad de paralelismo con seguridad de orquestador que nunca pierde estado

**Message Payload: Typed Interfaces (Pydantic) con Smart Reference**
- Pydantic InputSchema → OutputSchema por par brain-brain
- Smart Reference: Lazy loading con .get_parent_output() helpers
- IDE autocomplete: editor dice exactamente qué campos devolvió Brain #3
- Runtime validation: falla antes de llamar API de Anthropic (ahorra tokens)

**Message Format: Wrapped Envelope (Hybrid)**
- Sobre propietario simple: from_brain, to_brain, payload, correlation_id
- Contenido interno: YAML-based del ROADMAP (from, to, type, content, task_id, version)
- Metadata de transporte: transport_latency, retry_attempt sin ensuciar contrato de datos

**Routing: Orchestrator-directed DAG con Conditional Branching**
- Flow YAML define orden topológico (determinista, predecible)
- Conditional Branching evolución futura: brains pueden activar/saltar ramas según estado
- Zero race conditions: Orchestrator dicta orden basado en flow.yaml
- Visualización 1:1 con Dashboard de Phase 3 (Bento Grid + Grafo)

### Backward Compatibility & Stability (La Armadura)

**Versioning: Snapshot Pinning**
- Prompt hash guardado en flow.yaml
- Si cambia → sistema avisa: "El contrato ha cambiado, ¿deseas actualizar el grafo?"
- Detección de "Silent Changes": borra línea de prompt = hash mismatch = ejecución detenida
- Transparencia en Git: cambios en lógica de brain registrados en commits
- Baja fricción: no gestión de números SemVer complejos

**Breaking Change: Additive Only = OK**
- Schema change (eliminar/cambiar tipo campo) = breaking
- Agregar campos = backwards compatible (brains viejos ignoran campos nuevos)
- Evolución sin miedo: Brain #2 añade market_sentiment, sistema sigue funcionando
- Delete protection: solo borras campos si sabes que romperás el flujo

**Testing: Hybrid (Core Automated + Manual Quarterly)**
- Core flows automated: brains #1 (Product Strategy), #7 (Growth), #8 (Master Interviewer)
- Resto (20 brains): manual checklist quarterly
- Pareto 80/20: 20% cerebros generan 80% valor + errores críticos
- Optimización de recursos: enfoca artillería pesada donde riesgo es mayor

**Regression Detection: Semantic Similarity**
- Golden outputs + embeddings (sentence-transformers)
- Score de similitud semántica (ej. 0.94)
- Umbral por brain tipo: finanzas requieren 0.98, creatividad permiten 0.85
- Deploy se detiene si score < 90%
- Resiliente: "Es fundamental" vs "Es esencial" = semánticamente equivalente
- Costo cero: librería local, sin gastar tokens en tests de integración

### CI Pipeline Complexity (La Armadura Automatizada)

**CI Levels: Tiered Verification**
- **Nivel 1 (mypy + ruff):** Todos los PRs. Feedback instantáneo (segundos). Errores de sintaxis/tipos.
- **Nivel 2 (Unit & Contract Tests):** Todos los PRs. Verifica que sistema no se rompe funcionalmente. Par de minutos.
- **Nivel 3 (Semantic Integration):** Releases/main tags. Ejecuciones híbridas + métricas de similitud semántica. Lento + consume tokens.
- Protección de rama main: versión "producción" pasa juicio más estricto
- Gestión de costos: no gastas tokens en ramas experimentales

**Environment: Runner-native con uv**
- uv run python + pytest en actions/checkout
- uv.lock garantiza versiones idénticas en WSL2 y CI
- Velocidad extrema: CI listo en <30 segundos
- Debugging simple: test falla en CI → replicable con `uv run pytest` en WSL2
- Ubuntu 24.04 parity: GitHub runners (ubuntu-latest) = tu entorno

**Security: Secrets Only + Git-Hook Shield**
- Trufflehog en CI: escanea API keys, secrets
- Pre-commit local (Git-Hook Shield): primera línea de defensa en tu máquina
- Commit con API key → proceso se detiene antes de salir de tu computadora
- Prioridad de impacto: secreto filtrado = problema de "hoy", vulnerabilidad dep = "mañana"
- Cero ruido: sin alertas constantes de librerías secundarias

**Deployment: Docker Registry**
- CI pasa → tag semántico (v2.0.0) → git push origin main → Docker registry push
- Deployment: docker pull + docker run en servidor
- Inmutabilidad: lo que probaste en CI = exactamente lo que corre en producción
- Portabilidad: WSL2 → VPS (DigitalOcean, AWS) mismo comando
- Clean setup: cada versión en contenedor aislado, no ensucias Ubuntu global
- Rollback instantáneo: docker pull versión anterior

---

## Specific Ideas

- "Storage is cheap, lost data is irrecoverable" → JSON Completo para full fidelity
- "No quiero que un glitch de 2 segundos arruine 10 minutos de trabajo" → Hybrid Pulse (Event-Bus + Orchestrator fallback)
- "Quiero evitar que Brain #2 cambie y rompa Brain #23 sin saberlo" → Snapshot Pinning (hash en flow.yaml)
- "Quiero sleep tranquilo después de cada push" → Trufflehog + Git-Hook Shield (pre-commit local)

**Referencias técnicas:**
- sentence-transformers para semantic similarity
- Trufflehog para secret detection
- Docker registry para deployment inmutable
- Pydantic SecretStr para schema-aware redaction

---

## Existing Code Insights

### Reusable Assets

**Phase 3 (Web UI Platform):**
- `mastermind_cli/state/database.py` → SQLite async connection (WAL mode)
- `mastermind_cli/state/logger.py` → Database logger (471 LOC, 26 funciones)
- `mastermind_cli/auth/api_keys.py` → API Key auth system (330 lines, 26/26 tests)
- `mastermind_cli/api/` → FastAPI backend, WebSocket, JWT auth

**Phase 2 (Parallel Execution):**
- `mastermind_cli/orchestrator/dependency_resolver.py` → Kahn's algorithm (topological sort)
- `mastermind_cli/orchestrator/stateless_coordinator.py` → Per-request orchestrator instances
- `mastermind_cli/state/models.py` → TaskRecord, TaskState Pydantic models
- executions table (SQLite): FlowConfig JSON, brief, created_at, status

**Phase 1 (Type Safety):**
- `mastermind_cli/types/interfaces.py` → Pure function interfaces (Brief, BrainInput, ProductStrategy, etc.)
- `mastermind_cli/types/coordinator.py` → CoordinatorRequest, CoordinatorResponse
- `mastermind_cli/types/parallel.py` → FlowConfig, TaskState, ProviderConfig

### Established Patterns

- **Async/await:** todo el código usa asyncio + aiosqlite
- **Pydantic validation:** runtime validation en todos los boundaries
- **SQLite persistence:** WAL mode, async operations
- **YAML configs:** brains.yaml, flows.yaml, providers.yaml
- **Per-request instances:** Stateless coordinator (ARCH-03 cumplido en Phase 3)

### Integration Points

**Experience Logging:**
- Nueva tabla: `experience_records` (id, brain_id, input_hash, output_json, timestamp, duration_ms, status, embedding_stub, parent_brain_id, trace_context_id, custom_metadata JSONB)
- Integración con `logger.py` para escribir registros
- Archivo script: `/archive` .jsonl.gz rotation (cron job)

**Brain-to-Brain:**
- Integración con `stateless_coordinator.py` (orquestador per-request)
- Message passing via SQLite: coordinator escribe estado, brains leen outputs de padres
- Event-Bus (si se implementa): `mastermind_cli/events/` nuevo módulo para pub/sub

**Backward Compatibility:**
- Script de verificación: `tests/integration/test_backward_compat.py` (23 brains × 5 briefs)
- Semantic similarity: `tests/utils/semantic_diff.py` (embeddings + scoring)
- Snapshot storage: `tests/snapshots/` (golden outputs por brain)

**CI Pipeline:**
- `.github/workflows/ci.yml` → GitHub Actions con uv
- `.pre-commit-config.yaml` → Git-Hook Shield (trufflehog local)
- `Dockerfile` → Para imagen de Docker registry

---

## Deferred Ideas

**Out of scope para Phase 4:**
- Full RAG vector database (PostgreSQL + pgvector/qdrant) — v3.0+
- Machine learning auto-improvement training pipeline — v3.0+
- Multi-tenant SaaS infrastructure — single-tenant deployment only
- Real-time collaborative editing — v3.0+

**Noted para roadmap backlog:**
- Hot-reload de brains sin restart
- Type-aware auto-completion en Web UI (Monaco editor)
- Custom metrics dashboard (success rate, brain usage charts)
- Granular permissions (per-brain, per-niche RBAC)

---

*Phase: 04-experience-store-production*
*Context gathered: 2026-03-14*
