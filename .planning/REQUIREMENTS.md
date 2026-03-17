# Requirements: MasterMind Framework v2.0

**Defined:** 2026-03-13
**Completed:** 2026-03-17
**Core Value:** Expert AI collaboration that scales through parallel execution, type safety, and web interface

## v1 Requirements

Requirements for v2.0 initial release. All requirements shipped and verified via UAT (2026-03-17).

### Parallel Execution

- [x] **PAR-01**: System resolves brain dependencies from flow configurations and builds directed acyclic graph (DAG)
- [x] **PAR-02**: System executes independent brains in parallel using asyncio.TaskGroup
- [x] **PAR-03**: System maintains centralized task state in SQLite database (status, progress, result)
- [x] **PAR-04**: User can cancel running tasks with graceful shutdown (in-flight brains complete)
- [x] **PAR-05**: System provides task status indication (progress percentage, current brain, ETA)
- [x] **PAR-06**: System displays clear error messages when brains fail (not stack traces)
- [x] **PAR-07**: System persists execution configurations for re-run (save/load configs)
- [x] **PAR-08**: System provides real-time progress dashboard via WebSocket (live task cards)
- [x] **PAR-09**: System prevents false parallelism (no threading for I/O-bound work, asyncio only)

### Type Safety

- [x] **TS-01**: All data structures have Pydantic v2 models (requests, responses, brain outputs, configs)
- [x] **TS-02**: Codebase passes `mypy --strict` mode without errors
- [x] **TS-03**: MCP wrapper is type-safe (request/response models, validated)
- [x] **TS-04**: System validates types at runtime before execution (Pydantic validation)
- [x] **TS-05**: System provides clear type error messages for mismatches
- [x] **TS-06**: CLI-to-Orchestrator boundary uses typed interfaces (no raw dicts)
- [x] **TS-07**: Brain outputs conform to typed schemas (backward compatible with v1 brains)

### Web UI

- [x] **UI-01**: System provides web dashboard built with FastAPI backend
- [x] **UI-02**: System implements basic authentication (username/password, session tokens)
- [x] **UI-03**: System manages user sessions across requests (session storage, timeout)
- [x] **UI-04**: System provides real-time progress updates via WebSocket connections
- [x] **UI-05**: UI is responsive on mobile and tablet devices (CSS grid/flexbox)
- [x] **UI-06**: User can export execution results in JSON, YAML, or Markdown formats
- [x] **UI-07**: System maintains audit logging (timestamp, user, action, execution ID)
- [x] **UI-08**: Multiple users can have isolated sessions (per-request orchestrator instances)
- [x] **UI-09**: System displays visual dependency graph of brains (D3.js or Cytoscape.js)
- [x] **UI-10**: User can trigger brain execution manually via web form

### Architecture Foundation (v3.0 Prep)

- [x] **ARCH-01**: System logs all executions with ExperienceRecord schema (including embedding_stub placeholder)
- [x] **ARCH-02**: Brain-to-brain communication protocol defined (message format, routing)
- [x] **ARCH-03**: System supports session isolation (no shared global state in coordinator)
- [x] **ARCH-04**: Experience storage uses JSONB files (upgradable to PostgreSQL + pgvector in v3.0)
- [x] **ARCH-05**: System provides keyword-based search over execution logs (semantic search deferred to v3.0)

### Backward Compatibility

- [x] **BC-01**: Existing v1.3.0 CLI commands continue to work without changes
- [x] **BC-02**: All 23 existing brains (Software Dev + Marketing) remain compatible
- [x] **BC-03**: Existing Brain #8 (Master Interviewer) functionality preserved
- [x] **BC-04**: Existing E2E tests continue to pass
- [x] **BC-05**: Configuration file formats remain backward compatible (brains.yaml, flows.yaml)

### Performance

- [x] **PERF-01**: Parallel execution achieves 3-10x speedup for independent brains vs sequential
- [x] **PERF-02**: Task state queries complete in <100ms (SQLite indexed)
- [x] **PERF-03**: WebSocket latency for progress updates <500ms
- [x] **PERF-04**: Web dashboard initial page load <2 seconds

### Testing

- [x] **TEST-01**: All parallel execution scenarios covered by unit tests
- [x] **TEST-02**: Type safety verified by mypy in CI pipeline
- [x] **TEST-03**: E2E tests cover web UI workflows (login, execute, view progress, export)
- [x] **TEST-04**: Multi-user session isolation tested (no cross-session pollution)
- [x] **TEST-05**: MCP integration tested under concurrent load

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Web UI Differentiators

- **UI-DIFF-01**: Type-aware auto-completion in web UI (Monaco editor with type hints)
- **UI-DIFF-02**: Live interview collaboration (shared cursor, real-time chat)
- **UI-DIFF-03**: Execution comparison view (side-by-side diff of brain outputs)
- **UI-DIFF-04**: Custom metrics dashboard (success rate, avg iterations, brain usage charts)
- **UI-DIFF-05**: Template library for reusable execution patterns

### Advanced Features

- **ADV-01**: Hot-reload brains (update without restart)
- **ADV-02**: Granular permissions (per-brain, per-niche RBAC)
- **ADV-03**: Smart caching (skip redundant brain queries by brief hash)
- **ADV-04**: Replay/debug mode (time-travel debugging for orchestration)

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Real-time collaborative editing | Extreme complexity (CRDTs), overkill for orchestration |
| Auto-scaling / Kubernetes | Premature optimization for single-host v2.0 |
| ML-based optimization | R&D heavy, defer to v3.0+ |
| Blockchain/immutable audit | Overengineering, file-based logs sufficient |
| Mobile native apps | Fragmented codebase, responsive web + PWA future |
| Voice interface | Low ROI, browser speech API later |
| Full RAG vector DB | NotebookLM sufficient for v2.0, v3.0 feature |
| Multi-tenant SaaS | Auth complexity, single-tenant deployment only |
| Celery/RQ task queues | asyncio sufficient for single-host, defer distributed workers |

## Traceability

Which phases cover which requirements. All Complete as of v2.0.0 (2026-03-17).

### Phase 1: Type Safety Foundation

| Requirement | Phase | Status |
|-------------|-------|--------|
| TS-01 | Phase 1 | ✅ Complete |
| TS-02 | Phase 1 | ✅ Complete |
| TS-03 | Phase 1 | ✅ Complete |
| TS-04 | Phase 1 | ✅ Complete |
| TS-05 | Phase 1 | ✅ Complete |
| TS-06 | Phase 1 | ✅ Complete |
| TS-07 | Phase 1 | ✅ Complete |

### Phase 2: Parallel Execution Core

| Requirement | Phase | Status |
|-------------|-------|--------|
| PAR-01 | Phase 2 | ✅ Complete |
| PAR-02 | Phase 2 | ✅ Complete |
| PAR-03 | Phase 2 | ✅ Complete |
| PAR-04 | Phase 2 | ✅ Complete |
| PAR-05 | Phase 2 | ✅ Complete |
| PAR-06 | Phase 2 | ✅ Complete |
| PAR-07 | Phase 2 | ✅ Complete |
| PAR-08 | Phase 2 | ✅ Complete |
| PAR-09 | Phase 2 | ✅ Complete |
| PERF-01 | Phase 2 | ✅ Complete |

### Phase 3: Web UI Platform

| Requirement | Phase | Status |
|-------------|-------|--------|
| UI-01 | Phase 3 | ✅ Complete |
| UI-02 | Phase 3 | ✅ Complete |
| UI-03 | Phase 3 | ✅ Complete |
| UI-04 | Phase 3 | ✅ Complete |
| UI-05 | Phase 3 | ✅ Complete |
| UI-06 | Phase 3 | ✅ Complete |
| UI-07 | Phase 3 | ✅ Complete |
| UI-08 | Phase 3 | ✅ Complete |
| UI-09 | Phase 3 | ✅ Complete |
| UI-10 | Phase 3 | ✅ Complete |
| ARCH-03 | Phase 3 | ✅ Complete |
| PERF-02 | Phase 3 | ✅ Complete |
| PERF-03 | Phase 3 | ✅ Complete |
| PERF-04 | Phase 3 | ✅ Complete |

### Phase 4: Experience Store & Production

| Requirement | Phase | Status |
|-------------|-------|--------|
| ARCH-01 | Phase 4 | ✅ Complete |
| ARCH-02 | Phase 4 | ✅ Complete |
| ARCH-04 | Phase 4 | ✅ Complete |
| ARCH-05 | Phase 4 | ✅ Complete |
| BC-01 | Phase 4 | ✅ Complete |
| BC-02 | Phase 4 | ✅ Complete |
| BC-03 | Phase 4 | ✅ Complete |
| BC-04 | Phase 4 | ✅ Complete |
| BC-05 | Phase 4 | ✅ Complete |
| TEST-01 | Phase 4 | ✅ Complete |
| TEST-02 | Phase 4 | ✅ Complete |
| TEST-03 | Phase 4 | ✅ Complete |
| TEST-04 | Phase 4 | ✅ Complete |
| TEST-05 | Phase 4 | ✅ Complete |

**Coverage:**
- v1 requirements: 45 total
- Completed: 45 ✓
- Pending: 0
- Coverage: 100%

---
*Requirements defined: 2026-03-13*
*Last updated: 2026-03-17 — v2.0.0 shipped, all 45 requirements verified via UAT*
