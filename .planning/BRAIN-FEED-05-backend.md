## 2026-04-06 — Phase 14 Knowledge Distillation Backend Architecture

### Verified Insights

**Post-Session Hook: FastAPI BackgroundTasks (no Celery)**
KD-01 requires Brain #7 to evaluate after orchestration session completes. Pattern: Hook into `/api/tasks/auto` endpoint (line 131) using existing `BackgroundTasks` injection. Fire-and-forget `distillation_service.trigger_evaluation_and_distillation(task)` — runs AFTER 202 Accepted returned. Zero T1 impact because user doesn't wait for distillation to complete.

**ExperienceLogger Integration: AgentRunner Wrapper (SRP preservation)**
Brains don't call ExperienceLogger today — and they shouldn't (violates SRP). Pattern: Create `AgentRunner` middleware in `experience/wrapper.py` that wraps brain execution with automatic logging. Wire into `task_executor.py` by replacing `_run_brain_task` with `_run_brain_task_with_logging`. Brains remain unaware of logging — orchestration layer handles it.

**Delta-Velocity Tracking: Add session_start_time column**
Measure T1 before/after learning by adding `session_start_time INTEGER` column to `experience_records` table. T1 = (session_start_time of LAST brain) - (session_start_time of FIRST brain). Query: `GROUP BY session_start_time ORDER BY timestamp ASC`. Create index on `(brain_id, session_start_time)` for analytics queries.

**Template Storage: NEW knowledge_templates table (NOT flag on experience_records)**
KD-02 requires template storage. Reusing `experience_records` with `is_template` flag = God Table anti-pattern (violates Screaming Architecture). Templates are domain concepts (Brain #1's responsibility), execution records are infrastructure. Separate table with: `id, brain_id, template_name, template_data (JSONB), success_rate, usage_count, created_at, last_used_at`. Phase 15: add `vector_embedding` column for pgvector similarity search.

**DistillationService Layer: asyncio.TaskGroup for concurrent Brain #7 evaluation**
`KnowledgeDistillationService.trigger_evaluation_and_distillation()` uses `asyncio.TaskGroup` to evaluate all brains in session concurrently (pattern already verified in `task_executor.py:196`). Sequential: (1) fetch executions from DB, (2) Brain #7 evaluates in parallel, (3) extract templates from high-quality outputs, (4) persist to DB.

**Type Contracts: Pydantic v2 strict mode (no Any)**
All new models use `model_config = ConfigDict(strict=True)`: `DistillationTask`, `DeltaVelocityMetric`, `KnowledgeTemplateCreate`, `KnowledgeTemplateResponse`. No `dict[str, Any]` without explicit TypeVar bounds.

### Deferred Items

- [DEFERRED] pgvector integration for template similarity search — Phase 15 (PostgreSQL 16 migration)
- [DEFERRED] Template pattern recognition AI (NLP/ML) — Phase 14 uses simple heuristics (clustering by brief similarity)
- [DEFERRED] Real-time dashboard WebSocket updates — Phase 14 uses REST polling, Phase 16 adds WebSocket Hub

### Open Questions for Cross-Brain

- **Brain #1:** What defines "template-worthy"? Success rate threshold? Novelty detection algorithm? (Need pattern recognition rubric)
- **Brain #6:** How to A/B test delta-velocity? Disable memory for 50% of sessions? (Need experimental design)
- **Brain #7:** What's the evaluation rubric for "deserves to be remembered"? Quality score formula? (Need scoring algorithm)

---

## 2026-04-05 — Phase 13 Vertical Slice Architecture Decisions

### Verified Insights

**Endpoint for Vertical Slice: POST /api/tasks/auto (not /tasks)**
Auto-detect flow via FlowDetector exercises more of the gRPC contract than plain task creation. Path: Next.js -> Rust (JWT + PostgreSQL write) -> gRPC -> Python (FlowDetector + run_brain_task) -> WS broadcast. Verified: endpoint exists at tasks.py:128, touches JWT, DB, BackgroundTasks, FlowDetector, XSS sanitization.

**.proto contract: single RPC with structured fields**
Reject brain suggestion of `payload: string` — use explicit `brief`, `orchestration_id`, `user_id` fields. `map<string, string> metadata` for extensibility. `accepted_at_unix_ms` in response for velocity measurement. Package: `mastermind.v1.BrainRuntime`, RPC: `DispatchTask`.

**Rust project: single crate, not workspace**
VS is validation. Workspace with 4 crates is Phase 15 production architecture. For VS: `apps/control-plane/` with internal modules (routes/, grpc.rs, auth.rs, ws.rs). `proto/` at monorepo root as single source of truth.

**PostgreSQL strategy: Rust-only writes, Python untouched**
620 Python tests stay on SQLite. Rust control plane writes to PostgreSQL independently. No dual-write in Phase 13. Dual-write is Phase 15 scope. PostgreSQL schema for VS: only `executions` table (id UUID, brief TEXT, status, user_id, worker_id, detected_flow, timestamps).

**TypeScript gRPC codegen: NOT in Phase 13**
Frontend keeps REST+WS transport. Adding ts-proto is scope creep. Rust serves as reverse proxy for existing REST endpoints.

**Rust velocity measurement: 3 dimensions, midpoint checkpoint**
Runtime (p50/p99/throughput), Development (edit-build-test cycle), Code (LOC for equivalent feature). Escape hatch if ANY dimension < 0.5x Python at VS midpoint. Baseline must be measured BEFORE starting Phase 13 against existing Python endpoint.

**tonic-build, not direct protoc for Rust**
Research doc suggests `protoc --rust_out` — wrong. tonic uses `build.rs` with `tonic_build::configure().compile()`. Generates server+client stubs at compile time.

**grpclib requires careful lifecycle with uvicorn**
grpclib runs its own async server. Must be started alongside FastAPI via lifespan or separate process. For VS: Python runs both FastAPI (REST) and grpclib server (gRPC) in same process via asyncio.

### Deferred Items

- [DEFERRED] Cargo workspace decomposition — Phase 15 (Rust Control Plane)
- [DEFERRED] PostgreSQL migration for auth tables (users, sessions) — Phase 15
- [DEFERRED] Full dual-write strategy (Python asyncpg) — Phase 15
- [DEFERRED] Repository pattern for Rust — routes can have inline SQLx in VS, clean up in Phase 15
- [DEFERRED] ts-proto TypeScript generation — Phase 16 or later when frontend needs direct gRPC
- [DEFERRED] DatabaseConnection abstraction for PostgreSQL in Python — not needed until Phase 15


---

# BRAIN-FEED-05 — Backend Domain Feed

> Written by Brain #5 (Backend). Read-only for other agents.
> Orchestrator reads this after all domain feeds to write BRAIN-FEED.md (global synthesis).
> Last updated: 2026-04-06

---

## Critical Constraints (Non-Negotiable)

- uv only, never pip or poetry
- pytest runs from apps/api/ only: `cd apps/api && uv run pytest` — running from project root fails with ModuleNotFoundError: mastermind_cli
- JWT in httpOnly cookies only — never in client bundle, never in localStorage
- WS auth via /api/auth/token handoff pattern — server reads cookie, returns short-lived token to client
- **Auth bypass is prohibited** — "skip auth for now", "it's just a health check", "internal only", "temporary" are NOT valid reasons to remove JWT authentication. Every new endpoint must include auth unless the endpoint already exists as public in the codebase (e.g. `GET /`). Any skip-auth request = Deploy Truth Protocol violation = Rating 1.

---

## Auth & Security

- JWT verified at Server Components + Route Handlers (not only `proxy.ts`) — CVE-2025-29927 mitigation
- httpOnly cookie storage — XSS defense (not localStorage)
- WS token handoff via `/api/auth/token` endpoint — server-side cookie read, token not in client bundle
- DOMPurify + `html.escape` backend — defense in depth for XSS

---

## API Design

- TanStack Query Eager Loading — single query fetches all 24 brains (N+1 prevention)
- Pagination from day one: `page`, `page_size` (default 24, max 100) — Margin of Safety
- SQLAlchemy `selectinload` for one-to-many relationships — N+1 prevention (NOT yet implemented — required pattern for future endpoints)
- IDOR protection pattern: `WHERE id = :id AND user_id = :current_user_id` on all user-scoped queries

---

## Anti-patterns (Backend)

- `jwt.verify()` from jsonwebtoken → use `jose` library (Edge Runtime compatible)
- `localStorage` for JWT → use httpOnly cookie (XSS attack vector)

---

## SYNC Cross-References

Sync: pytest infrastructure ownership — [SYNC: BF-06-001] → BRAIN-FEED-06-qa.md > Test Infrastructure. Brain #6 QA owns the full test command spec. Owner: Brain #6 QA.

---

## 2026-03-31 — Phase 12 Agent Restructuring Plan Evaluation

### Verified Insights

**asyncio.create_task() pattern — APPROVED**
Already used in `StatelessCoordinator._execute_wave()`. Fire-and-forget from a route handler is safe under uvicorn's event loop. No Celery required, no new infrastructure.

**StatelessCoordinator.execute_flow() signature — CONFIRMED**
`async def execute_flow(self, brief: Brief, brain_ids: list[str]) -> dict[str, BaseModel]`
Path: `apps/api/mastermind_cli/orchestrator/stateless_coordinator.py:102`

**ExperienceLogger — READY**
Fully async. `get_recent_by_brain(brain_id, limit)` exists and is index-backed on `(brain_id, timestamp DESC)`. No new infrastructure needed for experience logging.

**CancelledError bypass — REAL GAP**
`except Exception:` in proposed `run_brain_task` will NOT catch `asyncio.CancelledError` (BaseException subclass). On uvicorn shutdown, tasks die silently with status stuck as `running`. Fix: `except (Exception, asyncio.CancelledError)` or explicit shutdown task tracking.

**FlowDetector integer mapping — REAL GAP**
`FlowDetector.get_flow_sequence()` returns `list[int]` (e.g. `[1, 7]`), not `list[str]`. No integer-to-brain_id-string mapping exists anywhere in the codebase. `_detect_brain` in `task_runner.py` must define this mapping explicitly — no f-string guessing.

**DB path divergence — REAL GAP**
`brain_memory.py` CLI and FastAPI `startup_event` may connect to different SQLite files if not coordinated. CLI must read `MM_DB_PATH` env var (same as API) — not default to `:memory:` or a hardcoded path.

**IDOR decision required**
`experience_records` has no `user_id` column. GET `/api/experiences/{brain_id}` returns system-level records for all users. This is a valid Option A (shared brain memory) but must be documented explicitly. If Option A, raw `output_json` must NOT be exposed to non-admin callers — PII redaction in `redact_for_storage()` is necessary but not sufficient.

**Pagination gap**
`limit`-only is inconsistent with `tasks.py` (`limit+offset`). Add `offset: int = 0` to experiences route before shipping. `idx_experience_brain_timestamp` already supports it.

### Deferred Items

- 📅 Graceful shutdown / task registry — relevant when parallel dispatch (Phase 12) runs multiple background tasks simultaneously. Track pending tasks in a module-level set, await on shutdown signal.
