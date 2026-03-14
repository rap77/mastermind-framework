# Roadmap: MasterMind Framework v2.0

## Overview

Transform the CLI-only sequential orchestration engine into a type-safe parallel execution platform with web interface. The journey builds from foundational type safety through parallel execution core to complete web dashboard, while maintaining backward compatibility with 23 existing brains and laying groundwork for v3.0 ML capabilities.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3, 4): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Type Safety Foundation** - Pydantic models and mypy strict enforcement (completed 2026-03-13)
- [x] **Phase 2: Parallel Execution Core** - Dependency-aware concurrent brain execution (completed 2026-03-13)
- [ ] **Phase 3: Web UI Platform** - FastAPI backend with real-time progress dashboard
- [ ] **Phase 4: Experience Store & Production** - Architecture foundation, backward compatibility, and polish

## Phase Details

### Phase 1: Type Safety Foundation
**Goal**: Type-safe data structures and strict type checking across all components
**Depends on**: Nothing (first phase)
**Requirements**: TS-01, TS-02, TS-03, TS-04, TS-05, TS-06, TS-07
**Success Criteria** (what must be TRUE):
  1. All coordinator/brain/MCP data structures use Pydantic v2 models (requests, responses, configs)
  2. Codebase passes `mypy --strict` mode with zero errors
  3. MCP wrapper validates request/response models at runtime
  4. Type errors provide clear messages indicating exact mismatch location
  5. Brain outputs conform to typed schemas while remaining backward compatible with v1.3.0 brains
**Plans**: 3 plans created

Plans:
- [x] 01-01: Create comprehensive Pydantic models for all orchestration data structures
- [x] 01-02: Enable mypy strict mode and resolve all type errors incrementally
- [x] 01-03: Build type-safe MCP wrapper with runtime validation

### Phase 2: Parallel Execution Core
**Goal**: Dependency-aware parallel brain execution with centralized task state
**Depends on**: Phase 1
**Requirements**: PAR-01, PAR-02, PAR-03, PAR-04, PAR-05, PAR-06, PAR-07, PAR-09, PERF-01
**Success Criteria** (what must be TRUE):
  1. System resolves brain dependencies from flow configurations and builds valid DAG
  2. Independent brains execute in parallel achieving 3-10x speedup vs sequential execution
  3. Task state persists to SQLite database with accurate status/progress/result tracking
  4. User can cancel running tasks with graceful shutdown (in-flight brains complete cleanly)
  5. System provides clear error messages when brains fail (no raw stack traces to users)
**Plans**: 4 plans created

Plans:
- [x] 02-01: Build dependency resolver that constructs DAG from brain flow configurations (completed 2026-03-13)
- [x] 02-02: Implement parallel executor using asyncio.TaskGroup with retry logic and Circuit Breaker (completed 2026-03-13)
- [x] 02-03: Add graceful cancellation and error message formatting (completed 2026-03-13)
- [x] 02-04: Validate performance speedup and add configuration persistence (completed 2026-03-13)

### Phase 3: Web UI Platform
**Goal**: Full-featured web dashboard with real-time progress and multi-user support
**Depends on**: Phase 2
**Requirements**: UI-01, UI-02, UI-03, UI-04, UI-05, UI-06, UI-07, UI-08, UI-09, UI-10, ARCH-03, PAR-08, PERF-02, PERF-03, PERF-04
**Success Criteria** (what must be TRUE):
  1. User can access web dashboard via browser with username/password authentication
  2. Dashboard displays real-time progress updates via WebSocket connections (<500ms latency)
  3. Multiple users have isolated sessions (no cross-user task pollution)
  4. User can trigger brain execution via web form and export results in JSON/YAML/Markdown
  5. UI is responsive on mobile and tablet devices using CSS grid/flexbox
**Plans**: 4 plans created (2026-03-13)

Plans:
- [ ] 03-00: Test infrastructure - Create 14 test stub files (Wave 0)
- [ ] 03-01: Build FastAPI backend with REST routes, JWT auth, WebSocket support, audit logging
- [ ] 03-02: Create frontend dashboard with HTMX/Alpine.js for task management and progress visualization
- [ ] 03-03: Add visual dependency graph rendering with React Flow

### Phase 4: Experience Store & Production
**Goal**: Architecture foundation for v3.0, backward compatibility verification, and production hardening
**Depends on**: Phase 3
**Requirements**: ARCH-01, ARCH-02, ARCH-03, ARCH-04, ARCH-05, BC-01, BC-02, BC-03, BC-04, BC-05, TEST-01, TEST-02, TEST-03, TEST-04, TEST-05
**Success Criteria** (what must be TRUE):
  1. All executions logged with ExperienceRecord schema including embedding_stub placeholder
  2. Brain-to-brain communication protocol enables message routing between specialized brains
  3. Experience storage uses JSONB files with keyword-based search (upgradable to PostgreSQL + pgvector)
  4. All existing v1.3.0 CLI commands work without changes
  5. All 23 existing brains (Software Dev + Marketing) remain compatible and E2E tests pass
**Plans**: 5 plans created (2026-03-14)

Plans:
- [ ] 04-01: ExperienceRecord schema and JSONB storage with PII redaction
- [ ] 04-02: Brain-to-brain communication protocol with message routing
- [ ] 04-03: Backward compatibility verification (23 brains + v1.3.0 CLI)
- [ ] 04-04: Comprehensive E2E test suite (multi-user, MCP, experience logging)
- [ ] 04-05: CI pipeline with tiered verification (typecheck → tests → semantic)

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Type Safety Foundation | 3/3 | Complete    | 2026-03-13 |
| 2. Parallel Execution Core | 4/4 | Complete    | 2026-03-13 |
| 3. Web UI Platform | 0/4 | Planned ✅  | 2026-03-13 |
| 4. Experience Store & Production | 0/5 | Planned ✅  | 2026-03-14 |

**Overall Progress: 7/15 plans complete (47%), 12/15 planned (80%)**

---

*Roadmap updated: 2026-03-14 (Phase 4 planning complete)*
