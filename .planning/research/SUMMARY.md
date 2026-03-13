# Project Research Summary

**Project:** MasterMind Framework v2.0
**Domain:** Multi-agent Cognitive Architecture Platform (Python)
**Researched:** 2026-03-13
**Confidence:** HIGH

## Executive Summary

MasterMind v2.0 is a **parallel orchestration platform** that evolves from sequential CLI-based brain execution to type-safe, concurrent task processing with web interface. This is fundamentally a **distributed systems refactoring project** requiring dependency-aware parallelization, strict type safety enforcement, and dual interface support (CLI + Web).

Expert approach prioritizes **asyncio for I/O-bound concurrency** (not multiprocessing for CPU-bound), **Pydantic v2 + mypy strict for type safety** (not gradual typing), and **FastAPI + HTMX for web dashboard** (not Streamlit/Dash). Key risks: false parallelism from mixing sync/async, race conditions from implicit brain dependencies, and MCP protocol bottlenecks under concurrent load. Mitigation: profile before parallelizing, explicit dependency DAGs, and semaphore limiting on MCP connections.

The architecture maintains **backward compatibility** with 23 existing brains across 2 niches while enabling 3-10x speedups for independent brains. Foundation is laid for v3.0 vector DB integration through v3.0-ready ExperienceRecord schema, but ML features are explicitly deferred to avoid premature optimization.

## Key Findings

### Recommended Stack

**Core technologies:**
- **asyncio + anyio (Python 3.14+)**: Parallel task execution — I/O-bound brains (MCP calls, API requests) benefit from true concurrency without threading/GIL overhead
- **Pydantic 2.10+ + mypy strict**: Type safety enforcement — Runtime validation at boundaries (MCP, CLI, Web) + static type checking catches bugs before runtime
- **FastAPI + WebSocket**: Web dashboard backend — Native async framework with automatic OpenAPI, WebSocket built-in, no extra dependencies for real-time updates
- **HTMX + Alpine.js + Tailwind**: Frontend — Server-driven UI without SPA complexity, no build step, progressive enhancement

**Explicitly NOT recommended for v2.0:**
- Celery/RQ (adds Redis dependency, overkill for single-host)
- Streamlit/Dash (wrong paradigm: notebook-style vs orchestration UI)
- React SPA (build complexity, HTMX sufficient for MVP)
- multiprocessing (unnecessary for I/O-bound tasks)

### Expected Features

**Must have (v2.0 table stakes):**
- **Task State Management** — SQLite-based store with pending/running/completed/failed states
- **Dependency Graph Resolution** — Detect brain dependencies, build DAG, topological sort
- **Parallel Executor** — asyncio-based concurrent execution respecting dependencies
- **Strict Pydantic Models** — All coordinator/brain/MCP data as typed models
- **Mypy Strict Mode** — Enable strict type checking, fix all errors incrementally
- **FastAPI Backend** — REST API for orchestration endpoints
- **Basic Auth** — Simple username/password (single-tenant)
- **Task Status Page** — List active/completed tasks with status

**Should have (v2.1 differentiators):**
- **Real-Time Progress** — WebSocket updates for live brain execution status
- **Visual Dependency Graph** — D3.js interactive DAG visualization
- **Multi-User Support** — Session isolation, per-user task lists
- **Execution History** — Browse past runs, view outputs

**Defer (v3.0+):**
- **Full RAG Vector DB** — Semantic search across all brains (premature optimization)
- **ML-Based Optimization** — Learn optimal execution paths (R&D heavy)
- **Real-Time Collaborative Editing** — CRDT complexity overkill
- **Mobile Native Apps** — PWA sufficient, app store overhead

### Architecture Approach

**Four-layer architecture with API Gateway pattern:**

**Major components:**
1. **Interface Layer** — CLI (Click commands) + Web UI (FastAPI + WebSocket) both consume OrchestratorAPI
2. **API Gateway Layer** — OrchestratorAPI (service layer) with Pydantic models at all boundaries, single source of truth for orchestration logic
3. **Parallel Orchestration Layer** — DependencyResolver (builds DAG), ParallelExecutor (asyncio.TaskGroup), ResultAggregator
4. **Knowledge Layer** — BrainExecutor (type-safe MCP wrapper), NotebookLM integration

**Key architectural decisions:**
- **Service Layer Pattern** — OrchestratorAPI separates business logic from interfaces, enables both CLI and Web to share type-safe orchestration
- **Structured Concurrency** — asyncio.TaskGroup (Python 3.11+) for automatic error handling and cleanup
- **Stateless Services** — No in-memory session state, all state persisted to ExperienceStore for crash recovery and multi-worker scaling
- **v3.0-Ready Schema** — ExperienceRecord designed with embedding_stub for future vector DB migration

### Critical Pitfalls

**Top 5 with prevention strategies:**

1. **False Parallelism (Threading Trap)** — Mixing sync/async or using threading for I/O-bound tasks → Profile before parallelizing, use pure asyncio for I/O, verify >2x speedup with real workloads
2. **Dependency Graph Blind Spot** — Brains share implicit state, parallelizing causes race conditions → Explicit dependency declarations in brain configs, state isolation, deterministic execution tests
3. **Type Safety Half-Migration** — Using `# type: ignore` or leaving MCP untyped → Pydantic models at all boundaries, accept `Any` only at external edges, enable mypy strict incrementally
4. **Multi-Orchestrator Race** — Global state causes User A to see User B's results → Per-request orchestrator instances, session-scoped execution context, database-backed orchestration
5. **MCP Integration Bottleneck** — Concurrent requests overwhelm NotebookLM MCP → Semaphore limiting (max 3-5 concurrent), request correlation IDs, circuit breaker

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Type Safety Foundation
**Rationale:** Pydantic models at all boundaries are prerequisite for parallel execution (type-safe task data) and web UI (API contracts). Mypy strict prevents accumulating technical debt before adding complexity.
**Delivers:** api/models.py (all Pydantic models), mypy strict configuration, type-hinted orchestrator components
**Addresses:** Strict Pydantic Models, Mypy Strict Mode (from FEATURES.md)
**Avoids:** Type Safety Half-Migration pitfall
**Stack:** Pydantic 2.10+, mypy 1.14+ strict mode

### Phase 2: Parallel Execution Core
**Rationale:** Independent of web UI, can be validated via CLI. Dependency resolution and parallel executor are highest-value features (3-10x speedup).
**Delivers:** DependencyResolver (DAG), ParallelExecutor (asyncio.TaskGroup), refactored Coordinator using OrchestratorAPI
**Addresses:** Dependency Graph Resolution, Parallel Executor, Task State Management
**Avoids:** False Parallelism, Dependency Graph Blind Spot, MCP Bottleneck
**Stack:** asyncio, anyio, NetworkX (for DAG)

### Phase 3: Web UI Backend
**Rationale:** FastAPI backend enables web interface and real-time progress. Building on typed OrchestratorAPI from Phase 1-2 ensures type-safe API contracts.
**Delivers:** FastAPI app, REST routes (/orchestrate, /brains, /sessions), WebSocket endpoint (/progress/{id})
**Addresses:** FastAPI Backend, Basic Auth, Task Status Page
**Avoids:** Multi-Orchestrator Race (stateless design), Auth State Schism (unified auth service)
**Stack:** FastAPI 0.115+, Uvicorn, WebSocket

### Phase 4: Web UI Frontend
**Rationale:** Simple HTMX frontend sufficient for MVP. No build complexity, progressive enhancement.
**Delivers:** dashboard.html (single-page app), WebSocket client for progress updates, responsive design
**Addresses:** Task Status Page, Manual Brain Trigger
**Stack:** HTMX 2.0+, Alpine.js 3.14+, Tailwind CSS 4.0+

### Phase 5: Experience Store (v3.0 Foundation)
**Rationale:** Can proceed in parallel with Phase 2-4. Logs executions in v3.0-ready schema without ML complexity.
**Delivers:** ExperienceRecord model, JSONB storage, keyword-based similarity search
**Addresses:** Audit Logging, future ML preparation
**Avoids:** Building Full ML System in v2.0 anti-pattern

### Phase 6: Migration & Polish
**Rationale:** Final integration, E2E testing, documentation. Ensures backward compatibility with v1.3.0 brains.
**Delivers:** CLI refactored to use OrchestratorAPI, E2E tests for parallel/web, migration guide
**Addresses:** Backward compatibility, production readiness

### Phase Ordering Rationale

- **Type Safety first:** Pydantic models enable everything else (parallel executor needs typed tasks, web UI needs typed API)
- **Parallel execution before web UI:** Validate core value prop (speedup) via CLI before building UI
- **Web backend before frontend:** API contract must exist before consuming it
- **Experience Store in parallel:** No dependencies on parallel/web, can develop concurrently
- **Polish last:** Integration testing requires all components

**Avoids pitfalls through ordering:**
- Phase 1 prevents Type Safety Half-Migration
- Phase 2 profiling prevents False Parallelism
- Phase 3 stateless design prevents Multi-Orchestrator Race
- Phase 5 explicit deferral prevents premature ML optimization

### Research Flags

**Phases likely needing deeper research during planning:**
- **Phase 2 (Parallel Execution):** MCP concurrent request handling patterns, semaphore tuning, NotebookLM rate limits under load
- **Phase 3 (Web UI Backend):** FastAPI WebSocket connection state management, reconnection logic patterns

**Phases with standard patterns (skip research-phase):**
- **Phase 1 (Type Safety):** Well-documented Pydantic v2 + mypy strict patterns
- **Phase 4 (Web UI Frontend):** HTMX + Alpine.js are established, low complexity
- **Phase 6 (Migration):** Standard E2E testing patterns, no unknowns

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All choices production-proven with official support (asyncio, Pydantic v2, FastAPI) |
| Features | MEDIUM | WebSearch unavailable during research, codebase analysis + ecosystem knowledge solid but lacking 2026-specific validation |
| Architecture | HIGH | Based on existing v1.3.0 codebase analysis + established distributed systems patterns (service layer, structured concurrency) |
| Pitfalls | MEDIUM | Drawn from Python ecosystem knowledge + existing CONCERNS.md, lack recent 2026 post-mortems (WebSearch limit) |

**Overall confidence:** HIGH — Stack and architecture are grounded in established patterns, features/pitfalls would benefit from WebSearch verification but are directionally sound.

### Gaps to Address

- **MCP concurrent load handling:** No benchmarks for NotebookLM MCP under parallel requests → Address in Phase 2 planning: implement semaphore limiting, test with 3-10 concurrent requests
- **2026 async Python best practices:** WebSearch limit reached → Rely on Python 3.14 official docs (TaskGroup is mature since 3.11), validate during Phase 2 implementation
- **FastAPI WebSocket patterns:** 2026-specific patterns unverified → Use official FastAPI docs (WebSocket support is stable), validate during Phase 3 testing

## Sources

### Primary (HIGH confidence)
- **Python 3.14 asyncio documentation** — TaskGroup, structured concurrency, async/await patterns
- **Pydantic v2 documentation** — Type-safe boundaries, strict mode, mypy plugin
- **FastAPI official documentation** — WebSocket support, async routes, automatic OpenAPI
- **Existing MasterMind v1.3.0 codebase** — 23 brains across 2 niches, sequential execution patterns, MCP integration

### Secondary (MEDIUM confidence)
- **NetworkX DAG documentation** — Dependency resolution, topological sort
- **HTMX documentation** — Server-driven UI, WebSocket integration
- **anyio documentation** — Portable async backend abstraction
- **Clean Architecture / Hexagonal Architecture patterns** — Service layer separation

### Tertiary (LOW confidence — WebSearch limit reached)
- **Ecosystem knowledge** — Celery/Airflow competitor analysis (LangChain, LangGraph, Prefect)
- **Common refactoring patterns** — Sequential to parallel migration war stories
- **Framework architecture principles** — Dependency injection, state isolation

**Research completed:** 2026-03-13
**Ready for roadmap:** yes
