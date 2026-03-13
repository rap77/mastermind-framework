# Requirements: MasterMind Framework v2.0

**Defined:** 2026-03-13
**Core Value:** Expert AI collaboration that scales through parallel execution, type safety, and web interface

## v1 Requirements

Requirements for v2.0 initial release. Each maps to roadmap phases.

### Parallel Execution

- [ ] **PAR-01**: System resolves brain dependencies from flow configurations and builds directed acyclic graph (DAG)
- [ ] **PAR-02**: System executes independent brains in parallel using asyncio.TaskGroup
- [ ] **PAR-03**: System maintains centralized task state in SQLite database (status, progress, result)
- [ ] **PAR-04**: User can cancel running tasks with graceful shutdown (in-flight brains complete)
- [ ] **PAR-05**: System provides task status indication (progress percentage, current brain, ETA)
- [ ] **PAR-06**: System displays clear error messages when brains fail (not stack traces)
- [ ] **PAR-07**: System persists execution configurations for re-run (save/load configs)
- [ ] **PAR-08**: System provides real-time progress dashboard via WebSocket (live task cards)
- [ ] **PAR-09**: System prevents false parallelism (no threading for I/O-bound work, asyncio only)

### Type Safety

- [x] **TS-01**: All data structures have Pydantic v2 models (requests, responses, brain outputs, configs)
- [x] **TS-02**: Codebase passes `mypy --strict` mode without errors
- [x] **TS-03**: MCP wrapper is type-safe (request/response models, validated)
- [x] **TS-04**: System validates types at runtime before execution (Pydantic validation)
- [x] **TS-05**: System provides clear type error messages for mismatches
- [x] **TS-06**: CLI-to-Orchestrator boundary uses typed interfaces (no raw dicts)
- [x] **TS-07**: Brain outputs conform to typed schemas (backward compatible with v1 brains)

### Web UI

- [ ] **UI-01**: System provides web dashboard built with FastAPI backend
- [ ] **UI-02**: System implements basic authentication (username/password, session tokens)
- [ ] **UI-03**: System manages user sessions across requests (session storage, timeout)
- [ ] **UI-04**: System provides real-time progress updates via WebSocket connections
- [ ] **UI-05**: UI is responsive on mobile and tablet devices (CSS grid/flexbox)
- [ ] **UI-06**: User can export execution results in JSON, YAML, or Markdown formats
- [ ] **UI-07**: System maintains audit logging (timestamp, user, action, execution ID)
- [ ] **UI-08**: Multiple users can have isolated sessions (per-request orchestrator instances)
- [ ] **UI-09**: System displays visual dependency graph of brains (D3.js or Cytoscape.js)
- [ ] **UI-10**: User can trigger brain execution manually via web form

### Architecture Foundation (v3.0 Prep)

- [ ] **ARCH-01**: System logs all executions with ExperienceRecord schema (including embedding_stub placeholder)
- [ ] **ARCH-02**: Brain-to-brain communication protocol defined (message format, routing)
- [ ] **ARCH-03**: System supports session isolation (no shared global state in coordinator)
- [ ] **ARCH-04**: Experience storage uses JSONB files (upgradable to PostgreSQL + pgvector in v3.0)
- [ ] **ARCH-05**: System provides keyword-based search over execution logs (semantic search deferred to v3.0)

### Backward Compatibility

- [ ] **BC-01**: Existing v1.3.0 CLI commands continue to work without changes
- [ ] **BC-02**: All 23 existing brains (Software Dev + Marketing) remain compatible
- [ ] **BC-03**: Existing Brain #8 (Master Interviewer) functionality preserved
- [ ] **BC-04**: Existing E2E tests continue to pass
- [ ] **BC-05**: Configuration file formats remain backward compatible (brains.yaml, flows.yaml)

### Performance

- [ ] **PERF-01**: Parallel execution achieves 3-10x speedup for independent brains vs sequential
- [ ] **PERF-02**: Task state queries complete in <100ms (SQLite indexed)
- [ ] **PERF-03**: WebSocket latency for progress updates <500ms
- [ ] **PERF-04**: Web dashboard initial page load <2 seconds

### Testing

- [ ] **TEST-01**: All parallel execution scenarios covered by unit tests
- [ ] **TEST-02**: Type safety verified by mypy in CI pipeline
- [ ] **TEST-03**: E2E tests cover web UI workflows (login, execute, view progress, export)
- [ ] **TEST-04**: Multi-user session isolation tested (no cross-session pollution)
- [ ] **TEST-05**: MCP integration tested under concurrent load

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

Which phases cover which requirements. Updated during roadmap creation.

### Phase 1: Type Safety Foundation

| Requirement | Phase | Status |
|-------------|-------|--------|
| TS-01 | Phase 1 | Complete |
| TS-02 | Phase 1 | Complete |
| TS-03 | Phase 1 | Complete |
| TS-04 | Phase 1 | Complete |
| TS-05 | Phase 1 | Complete |
| TS-06 | Phase 1 | Complete |
| TS-07 | Phase 1 | Complete |

### Phase 2: Parallel Execution Core

| Requirement | Phase | Status |
|-------------|-------|--------|
| PAR-01 | Phase 2 | Pending |
| PAR-02 | Phase 2 | Pending |
| PAR-03 | Phase 2 | Pending |
| PAR-04 | Phase 2 | Pending |
| PAR-05 | Phase 2 | Pending |
| PAR-06 | Phase 2 | Pending |
| PAR-07 | Phase 2 | Pending |
| PAR-08 | Phase 2 | Pending |
| PAR-09 | Phase 2 | Pending |
| PERF-01 | Phase 2 | Pending |

### Phase 3: Web UI Platform

| Requirement | Phase | Status |
|-------------|-------|--------|
| UI-01 | Phase 3 | Pending |
| UI-02 | Phase 3 | Pending |
| UI-03 | Phase 3 | Pending |
| UI-04 | Phase 3 | Pending |
| UI-05 | Phase 3 | Pending |
| UI-06 | Phase 3 | Pending |
| UI-07 | Phase 3 | Pending |
| UI-08 | Phase 3 | Pending |
| UI-09 | Phase 3 | Pending |
| UI-10 | Phase 3 | Pending |
| ARCH-03 | Phase 3 | Pending |
| PERF-02 | Phase 3 | Pending |
| PERF-03 | Phase 3 | Pending |
| PERF-04 | Phase 3 | Pending |

### Phase 4: Experience Store & Production

| Requirement | Phase | Status |
|-------------|-------|--------|
| ARCH-01 | Phase 4 | Pending |
| ARCH-02 | Phase 4 | Pending |
| ARCH-04 | Phase 4 | Pending |
| ARCH-05 | Phase 4 | Pending |
| BC-01 | Phase 4 | Pending |
| BC-02 | Phase 4 | Pending |
| BC-03 | Phase 4 | Pending |
| BC-04 | Phase 4 | Pending |
| BC-05 | Phase 4 | Pending |
| TEST-01 | Phase 4 | Pending |
| TEST-02 | Phase 4 | Pending |
| TEST-03 | Phase 4 | Pending |
| TEST-04 | Phase 4 | Pending |
| TEST-05 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 34 total
- Mapped to phases: 34 ✓
- Unmapped: 0
- Coverage: 100%

---
*Requirements defined: 2026-03-13*
*Last updated: 2026-03-13 after roadmap creation*
