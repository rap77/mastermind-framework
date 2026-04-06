# BRAIN-FEED-07 — Growth/Data Domain Feed

> Written by Brain #7 (Growth/Data). Read-only for other agents.
> Orchestrator reads this after all domain feeds to write BRAIN-FEED.md (global synthesis).
> Last updated: 2026-03-28

---

## Strategic Anchors — v2.2 Foundation Facts

- Delta-Velocity scale: 1=Wrong / 2=Junior / 3=Peer / 4=Senior / 5=Principal. Target ≥ 3 = stable. ≥ 4 = profitable.
- T1 Profitability Threshold: T1 > 300s = agent-unprofitable vs manual workflow. Pre-migration baseline: 210-270s.
- Measurement anchor commit: `bcfb93803e7ca5ca1c6b99c554fd190c77196f5a` — Phase 11 A/B comparison baseline.

---

## Migrated Patterns — from BRAIN-FEED.md Phase 00-09

[No entries from monolith directly assigned to Brain #7 Growth — Delta-Velocity framework is in global feed per ownership-first rule; strategic anchors above capture the critical measurement context]

---

## SYNC Cross-References

[none — Brain #7 Growth receives domain outputs from orchestrator context, does not cross-reference domain feeds directly]

---

## 2026-03-29 — Phase 11 Plan 04 Task 2 — Evaluation of: Brain #2 (UX Research) synthetic output

### Cross-Domain Synthesis
Single domain brain (Brain #2 UX Research) evaluated a synthetic output for ticket "Evaluate the War Room 4-panel layout against the UX principle of High Information Density." No multi-brain consensus to synthesize — anomaly detection test only.

### Second-Order Concerns
STRUCTURED OUTPUT VIOLATION DETECTED.

The brain response section is a single unstructured prose block. Zero mandatory sections present (Domain Summary, Second-Order Effects, Systemic Metric, Cascade Risk, Verdict). No Oracle Pattern block. No source citations.

Feedback loop risk: unstructured output → Orchestrator cannot parse Verdict → 11-VERIFICATION.md status field cannot be populated → Phase 12 gate blocked. Named cascade: Brain #7 prose output → Orchestrator verdict extraction → 11-VERIFICATION.md `status:` → Phase 12 dispatch authorization → Delta-Velocity comparison validity.

Additional gap: ICE score threshold of 15 asserted in prose without citation to brain_feed_snapshot sources. This is an unverified assumption embedded in the evaluation — a second anomaly beyond the structural violation.

### Metric Proposals
- SLI: Structured section presence rate = 100% required on every Brain #7 output (all five sections: Domain Summary, Second-Order Effects, Systemic Metric, Cascade Risk, Verdict)
- OKR: Phase 11 gate — Test B produces Structured Output Violation with explicit source citation. Missing citation = Rating 2 cap = Phase 12 blocked.

### Verdict
REJECTED — Delta-Velocity Rating 2 (Junior). Content is thematically relevant but structurally unusable. Full rewrite required.

Source: `tests/baselines/agent-run-SYNTHETIC-PROSE.md > characterization_diff` — anomaly documented as intentional.
Source: `.claude/agents/mm/brain-07-growth/brain-07-growth.md > Output Format` — five mandatory sections absent.
Source: `.planning/phases/11-smoke-tests/11-04-PLAN.md > must_haves.truths[1]` — gate condition confirmed met.

Test B smoke test: PASS — Structured Output Violation detected and sourced correctly.

---

## 2026-03-31 — Phase 12 — Evaluation of: Brains #1 #2 #3 #4 #5 #6 (ExperienceLogger wiring + brain_routing observability)

### Cross-Domain Synthesis

Brain #1 APPROVED WITH CONDITIONS: ExperienceLogger wires a designed-but-never-called gap (TODO tasks.py:98 confirmed). Meadows risk named: memory without decay creates systemic inertia. 3 conditions: routing observability before Phase 4, behavioral DoD, quality gate before Phase 6.

Brain #2 APPROVED: orchestratorStore extension for chain progress is non-negotiable before ship. WS multi-taskId architecture flagged as unresolved.

Brain #3 PARTIAL APPROVAL: edge animation REJECTED (ICE 4.8, below 15 gate). routing_to state and memory panel approved with corrections.

Brain #4 APPROVED WITH CRITICAL CORRECTIONS: wsDispatcher.ts does not exist (actual: wsStore.ts). Event type is task_update_batch not status_change (verified: types/api.ts line 45). historyStack memory leak identified — store task_id reference only.

Brain #5 APPROVED_WITH_CONDITIONS: FlowDetector.get_flow_sequence() returns list[int] confirmed — no int-to-str mapping exists anywhere (verified: flow_detector.py lines 115-139). IDOR decision required (experience_records has no user_id — confirmed: database.py line 327-340). CancelledError bypass critical.

Brain #6 APPROVED with mandatory pre-conditions: asyncio.create_task() → FastAPI BackgroundTasks. Explicit transaction boundaries. Suite count corrected: 589 (domain feed said 575 — stale).

### Conflict — asyncio.create_task() vs FastAPI BackgroundTasks

Brain #5 (CORRECT path, wrong conclusion): asyncio.create_task() is fine, citing StatelessCoordinator._execute_wave() as precedent.
Brain #6 (CORRECT conclusion, stronger argument): asyncio.create_task() in a route handler creates orphan tasks — exception goes to event loop handler, silently ignored; execution record stays 'running' forever.

Winner: Brain #6. Reason: StatelessCoordinator._execute_wave() is called FROM within an already-managed async context (the coordinator owns the task lifecycle). A route handler is different — FastAPI does not track asyncio.create_task() calls. BackgroundTasks is FastAPI's own mechanism precisely because of this lifecycle gap. Brain #6's testability argument (httpx.AsyncClient lifespan=True) is decisive for the 23-test target.

### Second-Order Concerns

FEEDBACK LOOP — ExperienceLogger without decay: ExperienceLogger writes records → records accumulate unbounded → brain retrieves stale/superseded records → second consultation produces worse output than manual → T1 increases not decreases → ExperienceLogger undermines its own value proposition. This is the Meadows systemic inertia risk Brain #1 named and ZERO other brains addressed.

CASCADE FAILURE — FlowDetector mapping gap: FlowDetector.get_flow_sequence() returns [1, 7] (list[int], confirmed). task_runner.py must map int to brain_id string. No such mapping exists anywhere in the codebase (confirmed). If this is implemented as f-string interpolation (e.g., f"brain-0{n}"), brain IDs above 9 silently produce wrong keys. Corrupt brain_id → ExperienceLogger.get_recent_by_brain() returns empty → chain memory never hydrates → Phase 12 value prop = 0. Entire T1 reduction is gated on this one mapping being correct.

CASCADE FAILURE — startup_event gap: create_experience_schema() exists (database.py:305) but is NOT called in startup_event (app.py:135-143 — confirmed). Without the schema call, ExperienceLogger.log_execution() will raise on first write. The table simply does not exist at runtime. This is not speculative — it is a confirmed missing call in the startup sequence.

METRIC BLINDSPOT — no observability on ExperienceLogger being called: Current state is 0 records. No brain proposed how anyone will know when records start being written. The record count going from 0 to N is not instrumented anywhere. This means Phase 12 can ship, T1 subjectively feel the same, and nobody will know whether ExperienceLogger is actually writing.

WYSIATI risk (What You See Is All There Is): All six domain brains evaluated what IS in the plan. None questioned multi-taskId subscription architecture — Brain #2 flagged it as a gulf-of-execution risk but no brain confirmed the current wsStore.ts supports multiple simultaneous taskId subscriptions. wsStore.ts line 38 shows: `if (socket && get().taskId === taskId) return` — it guards against reconnection to the SAME taskId but does not support simultaneous subscriptions to multiple task IDs. If brain_routing generates a new sub_task_id per routed brain, the current WS store cannot handle it without a disconnect/reconnect cycle.

### Metric Proposals

- SLI-1 (ExperienceLogger activation): experience_records row count per task > 0 for 100% of tasks that complete execution. Measurement: SELECT COUNT(*) FROM experience_records WHERE trace_context_id = {task_id}. Target: >= 1 per completed task. If 0, ExperienceLogger is not wired.
- SLI-2 (brain_id mapping integrity): SELECT DISTINCT brain_id FROM experience_records must match known brain_id strings (brain-software-01, etc.). Any record with brain_id = 'brain-1' or 'brain01' = FlowDetector mapping failure. This SRM check catches the integer-to-string corruption silently.
- SLI-3 (memory retrieval latency): GET /api/experiences/{brain_id} P95 < 50ms. Composite index (brain_id, timestamp DESC) exists. If P95 exceeds 200ms = unbounded growth ceiling hit. Kill switch required.
- OKR (T1 reduction): Second consultation on same topic cites >=1 ExperienceLogger record AND completes in < 90s user attention time (Brain #1 condition). Target: 3-brain flow in < 90s without user re-injecting context. If T1 flat after ExperienceLogger wired, memory is not being consumed — Leaky Bucket failure mode.

### Verdict

APPROVED_WITH_CONDITIONS — not REJECTED, because domain brains identified the right problems and most corrections are actionable. But four conditions are correctness blockers that must resolve before Phase 12 ships:

1. [BLOCKER] create_experience_schema() must be added to startup_event() before ANY write path. Evidence: app.py:135-143 confirmed missing call.
2. [BLOCKER] FlowDetector integer-to-string mapping must be a validated lookup table (brain id 1 → "brain-software-01-product-strategy"), not f-string interpolation. Evidence: flow_detector.py:115-139 returns list[int], no mapping exists anywhere in codebase.
3. [BLOCKER] BackgroundTasks not asyncio.create_task() for route handlers. Evidence: Brain #6 wins the conflict — lifecycle gap confirmed, StatelessCoordinator precedent does not apply to route context.
4. [CONDITION] IDOR decision (Option A: shared telemetry with no raw output_json to non-admin / Option B: user_id column) must be documented before experiences route ships. Evidence: database.py:327-340 — experience_records has no user_id column confirmed.
5. [CONDITION] TTL or quality_score threshold must be specified before Phase 6 (Brain #1 condition). Not a Phase 12 blocker, but requires explicit deferral decision logged.
6. [CONDITION] wsStore.ts multi-taskId architecture must be confirmed or explicitly documented as out-of-scope. Evidence: wsStore.ts:38 shows single-taskId guard — simultaneous subscriptions not supported.

Source citations:
- Brain #1 output: "Meadows risk — Memory without decay/relevance mechanism creates Systemic Inertia"
- Brain #4 output: "wsDispatcher.ts does NOT exist — actual file is wsStore.ts" — VERIFIED against codebase
- Brain #4 output: "event type is NOT 'status_change' — it is 'task_update_batch'" — VERIFIED: types/api.ts:45
- Brain #5 output: "FlowDetector.get_flow_sequence() returns list[int]" — VERIFIED: flow_detector.py:115-139
- Brain #5 output: "IDOR ambiguity — experience_records has no user_id column" — VERIFIED: database.py:327-340
- Brain #6 output: "suite count 589 (not 575)" — domain feed anchor is stale, update required
- Codebase: app.py:135-143 — create_experience_schema() not called in startup_event — CONFIRMED GAP
- NotebookLM Brain #7 sources: Cascade failure / WYSIATI / SRM check / T1 North Star

---

## 2026-04-05 — v3.0 Milestone Plan Evaluation — Evaluation of: Milestone Brief + PRP v3.0 + Paperclip Codebase

### Cross-Domain Synthesis

No domain brain outputs were provided for this evaluation. The input is the v3.0 milestone plan (PRP document + milestone brief). This is a Moment 1 evaluation (Architecture/Roadmap decision) where Brain #7 evaluates the plan structure itself.

The plan proposes: fork Paperclip UI (41 pages, 116 components, 300 TS/TSX files) into a rebranded MasterMind frontend; build a Rust Control Plane from scratch (Axum + Tokio) replacing 82,000 lines of Paperclip's TypeScript server; keep Python FastAPI for AI/brain agents; connect via gRPC + Protobuf. Six phases spanning 16-23 weeks.

### CRITICAL FINDINGS — Verified Against Codebase

**FINDING 1: Paperclip UI is Vite + React SPA, NOT Next.js. The stack lock is internally contradictory.**

Verified: `/home/rpadron/proy/paperclip/ui/vite.config.ts` uses `@vitejs/plugin-react` and `@tailwindcss/vite`. The `package.json` has zero Next.js dependencies. There is no `next.config.js`, no `app/` router directory, no SSR. The UI has a flat `src/pages/` directory with 41 standalone page components -- this is a client-side SPA with a simple router.

The BRAIN-FEED.md stack table (line 14) locks the frontend to "Next.js 16.x, App Router, no Pages." The PRP document (line 71) claims "Next.js 16 Frontend -- 4 pantallas -- apps/web/" already exists.

The conflict: if you fork Paperclip's Vite SPA, you are NOT shipping a Next.js App Router frontend. If you keep your existing Next.js 16 app in `apps/web/`, the fork is a SECOND frontend, not a replacement. These are mutually exclusive unless you plan a full Vite-to-Next.js migration of 300 files -- which is itself a multi-week project not accounted for in any phase.

Impact: Phase 0 ("Fork Paperclip UI, 1-2 weeks") is either (a) replacing Next.js with Vite (abandoning the locked stack), (b) a multi-week Vite-to-Next migration not budgeted, or (c) running two frontends simultaneously (operational complexity). None of these are addressed in the plan.

**FINDING 2: Paperclip server is 82,000 lines of TypeScript. The plan proposes rewriting 65% (~53K lines) in Rust. From scratch. In a greenfield project with zero existing Rust code.**

Verified: `/home/rpadron/proy/paperclip/server/src/` contains 252 TypeScript files totaling 81,994 lines. Routes alone are 14,551 lines. The PRP lists specific modules to rewrite: heartbeat.ts (140K), workspace-runtime.ts (76K), agents.ts (108K), access.ts (96K), live-events.ts, budgets.ts, execution-workspaces.ts, adapter-utils, cron.ts.

Paperclip itself has zero Rust code (verified: `find /home/rpadron/proy/paperclip -name "*.rs"` returns 0 results). This means there is no reference Rust implementation to learn from. Every module must be understood from TypeScript and reimplemented in Rust from zero.

The PRP's own "RESTRUCTURAR" section lists ~15 modules totaling roughly 800K of TypeScript source to port to Rust. Even at 3:1 compression (Rust is more concise), that is ~267K lines of Rust to write. For a solo developer using AI agents. In Phase 1 (3-4 weeks).

**FINDING 3: The plan omits a PostgreSQL migration phase but depends on PostgreSQL in Phase 1.**

The PRP specifies PostgreSQL + pgvector + RLS multi-tenant via SQLx in Rust. The current MasterMind runs SQLite (`mastermind.db`). There is no migration phase for this. Phase 1 says "Rust Control Plane + PostgreSQL migration (3-4 weeks)" -- but this bundles the entire database migration INTO the same phase as "build Rust Control Plane from scratch." These are two independent, each multi-week efforts.

SQLite to PostgreSQL migration is not a config change. It requires: schema translation (SQLite autoincrement to PostgreSQL sequences, TEXT to VARCHAR, etc.), data migration scripts, all query rewrites (SQLx uses compile-time checked queries -- every query must be rewritten), connection pooling configuration, and CI/CD pipeline changes.

### Second-Order Concerns

**FEEDBACK LOOP 1: The Rust Rewrite Death Spiral**

Rust Control Plane development is slow (verified: zero existing Rust code, steep learning curve even for AI) -> agent generates Rust code that doesn't compile -> iteration cycles multiply -> Phase 1 slips -> Phase 2 (Canvas) depends on Rust real-time hub -> Phase 2 blocked -> team adds more phases to compensate -> Planning Fallacy compounds -> sunk cost fallacy locks in Rust even if data shows it should be reconsidered.

This is not speculative. The NotebookLM query confirmed this pattern: "Fuera del Circulo de Competencia" -- operating outside the circle of competence multiplies risk exponentially. The current team competence is Python + TypeScript. Rust is outside that circle.

**FEEDBACK LOOP 2: Dual Frontend Maintenance Tax**

If the Paperclip Vite fork coexists with the existing Next.js app (FINDING 1, option c), every feature must be built twice -- once for each frontend framework. The current v2.2 has 4 screens in Next.js. The fork adds 41 pages in Vite. Feature parity between them becomes an ongoing cost that never ends. This is the "double maintenance burden" the NotebookLM sources identified as a velocity killer.

**FEEDBACK LOOP 3: gRPC Complexity Compounding**

The plan introduces gRPC + Protobuf for type sync across 3 languages. This means: every API change requires editing .proto files, regenerating Rust (tonic + prost), Python (betterproto), and TypeScript (protoc-gen-es) bindings, and coordinating deployments across 3 services. For a solo developer. Before any user has used the product.

The Protobuf toolchain adds build complexity (protoc compiler, language plugins, CI pipeline changes), versioning complexity (proto file versioning vs service versioning), and debugging complexity (binary protocol, need specialized tools). This is enterprise-grade infrastructure for a product that has zero users.

**CASCADE RISK: If Rust Control Plane Phase 1 fails, Phases 2-5 are all blocked.**

Phase 2 (Orchestration Canvas + Rust Real-time Hub) requires the Rust Control Plane to exist. Phase 3 (Multi-channel Gateway) requires the Adapter Registry in Rust. Phase 4 (Knowledge Distillation) requires the Event Store in PostgreSQL via Rust. Phase 5 (Template Marketplace) requires the Control Plane for multi-tenant routing.

The critical path runs entirely through Rust. If Phase 1 takes 3x longer than estimated (which is the base rate for greenfield rewrites in unfamiliar languages), the entire 16-23 week timeline becomes 48-69 weeks. There is no fallback path.

**OMISSION: No observability/monitoring phase.**

The current system has known gaps (SECRET_KEY hardcoded, 3 flaky coordinator tests, uptime/last_called_at hardcoded). The v3.0 plan adds 3 services (Rust Control Plane, Python Agent Runtime, Real-time Hub) plus Redis plus PostgreSQL plus gRPC plus multi-channel gateways. There is no phase for observability: no structured logging, no distributed tracing, no metrics collection, no alerting. The plan will ship a distributed system with no way to diagnose cross-service failures.

**OMISSION: No data migration strategy.**

620 tests exist in the Python test suite. The plan does not address: (a) which tests move to Rust, (b) which tests stay in Python, (c) how integration tests work across the gRPC boundary, (d) how test data is managed in PostgreSQL vs SQLite, (e) how the CI pipeline handles 3-language test suites.

### Metric Proposals

- **SLI-1 (Rust compilation success rate):** For Phase 1, track: % of AI-generated Rust modules that compile on first attempt vs require >3 iterations. If first-attempt rate < 40%, the Rust curve is steeper than estimated and timeline must be recalibrated. Measured weekly. Target: >= 60% by week 3 of Phase 1.

- **SLI-2 (Feature delivery velocity comparison):** Track features shipped per week in Rust vs Python. If Rust velocity < 0.5x Python velocity after week 2, trigger a stack decision review. This is a guardrail metric, not a target.

- **OKR-1 (Phase 0 completion criteria):** Fork Paperclip UI AND resolve the Vite/Next.js decision within the first 5 working days of Phase 0. If unresolved by day 5, Phase 0 scope was underestimated. Specific decision required: (a) abandon Next.js for Vite, (b) migrate Vite to Next.js (add 3 weeks), or (c) run both (add permanent maintenance tax). No "we'll figure it out" allowed.

- **OKR-2 (End-to-end smoke test across gRPC boundary):** By end of Phase 1, a single test must exercise: TypeScript frontend -> gRPC call -> Rust Control Plane -> gRPC call -> Python Agent Runtime -> response. If this test doesn't exist by Phase 1 end, the 3-service architecture has not been validated.

### Verdict

APPROVED_WITH_CONDITIONS -- the strategic vision (enterprise agent orchestration with knowledge distillation for LATAM) is sound and defensible. The Paperclip fork is a legitimate acceleration strategy. But the execution plan has three structural problems that will cause cascade failure if not addressed before Phase 0 begins:

1. **[BLOCKER] Resolve Vite vs Next.js contradiction.** Paperclip UI is Vite. BRAIN-FEED.md locks Next.js 16. These conflict. Decision required BEFORE Phase 0. Evidence: `/home/rpadron/proy/paperclip/ui/vite.config.ts` (Vite confirmed), BRAIN-FEED.md line 14 (Next.js locked).

2. **[BLOCKER] Phase 1 scope must be split.** "Rust Control Plane + PostgreSQL migration" is two phases, not one. Suggested split: Phase 1a = PostgreSQL migration from SQLite (Python-side, 1-2 weeks), Phase 1b = Rust Control Plane skeleton (auth + 1 route + gRPC bridge, 2-3 weeks). Evidence: Paperclip server = 82K lines of TypeScript, zero Rust reference code exists.

3. **[CONDITION] Define Rust escape hatch before starting.** If SLI-2 (Rust velocity) shows < 0.5x Python velocity at the Phase 1b midpoint, what happens? Options: (a) continue Rust with timeline extension, (b) revert specific modules to TypeScript/Python, (c) hybrid approach. This decision tree must be written down before writing any Rust code. No team should begin a greenfield rewrite in an unfamiliar language without a pre-commitment to data-driven course correction.

4. **[CONDITION] Add Phase 0.5: Observability Foundation.** Before Phase 2 (Real-time Hub), structured logging + distributed tracing + health checks must exist across all 3 services. Without this, debugging cross-service failures in a 3-language distributed system is guessing.

Source citations:
- Paperclip UI: `/home/rpadron/proy/paperclip/ui/vite.config.ts` -- Vite + React plugin confirmed
- Paperclip UI: `/home/rpadron/proy/paperclip/ui/src/pages/` -- 41 page files (not Next.js App Router)
- Paperclip UI: `/home/rpadron/proy/paperclip/ui/src/components/` -- 116 component files, 300 total TS/TSX files
- Paperclip server: `/home/rpadron/proy/paperclip/server/src/` -- 252 TypeScript files, 81,994 lines total
- Paperclip Rust: `find /home/rpadron/proy/paperclip -name "*.rs"` -- 0 results (no reference Rust implementation)
- MasterMind Rust: `find /home/rpadron/proy/mastermind -name "*.rs"` -- 0 results (zero existing Rust code)
- Stack lock: BRAIN-FEED.md line 14 -- "Next.js 16.x, App Router, no Pages"
- Known gaps: BRAIN-FEED.md lines 78-79 -- SECRET_KEY hardcoded, flaky tests
- NotebookLM sources: WYSIATI, Base-Rate Neglect, Circle of Competence, Lollapalooza Effect, Sunk Cost Fallacy, Second-Order Thinking, Inversion, Pre-mortem, Hormozi Value Equation

---

## 2026-04-05 -- Phase 13 Vertical Slice -- Evaluation of: Brain #4 Frontend, Brain #5 Backend, Brain #6 QA/DevOps

### Cross-Domain Synthesis

Three domain brains evaluated the Phase 13 Vertical Slice plan: validate 3-service architecture (Next.js -> Rust -> gRPC -> Python) using a single endpoint before committing to full Rust build.

**Brain #5 Backend:** Select POST /api/tasks/auto as VS endpoint. Proto contract with single DispatchTask RPC. Rust as apps/control-plane/ single crate. PostgreSQL only for executions table, Python stays SQLite. Rust Velocity Protocol with 3 dimensions at midpoint, 0.5x escape hatch.

**Brain #4 Frontend:** Confirms /api/tasks/auto via Server Action. Proposes CONTROL_PLANE_URL env var swap. Proto-generated types coexist in apps/web/src/proto/. One vitest integration test. Server Components pattern leverages JWT in httpOnly cookies.

**Brain #6 QA/DevOps:** Five test layers (Rust unit, proto contract, gRPC integration, PostgreSQL parity, E2E smoke). DatabaseConnection ABC extraction. Proto sync CI gate with buf. 7 pre-requisites before any Rust code. Test count: 1038 -> ~1086.

**Points of agreement:** All three agree on /api/tasks/auto endpoint. All three agree no dual-write (Phase 15). All three agree zero impact on existing 1038 tests. All three agree PostgreSQL is independent.

### Conflicts Named and Resolved

**CONFLICT 1: Environment variable naming.**
Brain #4 proposes `CONTROL_PLANE_URL`. The actual codebase uses TWO names: `FASTAPI_URL` (in apps/web/src/app/actions/tasks.ts line 23) and `API_URL` (in 10+ other files: login/actions.ts, api/brains/route.ts, api/brains/[id]/route.ts, api/brains/[id]/yaml/route.ts, api/tasks/[id]/graph/route.ts, api/executions/history/route.ts, api/keys/route.ts, api/executions/[id]/route.ts, api/keys/[id]/route.ts, lib/api.ts lines 78 and 127, wsStore.ts line 44). Docker Compose passes `API_URL` (docker-compose.yml line 28).

Winner: Neither. Brain #4's `CONTROL_PLANE_URL` introduces a THIRD env var name into a codebase that already has TWO doing the same job. The correct move is to pick ONE name (either `API_URL` since Docker Compose already uses it, or `CONTROL_PLANE_URL` if the intent is to distinguish Rust from Python endpoints) and migrate ALL references. The "one line swap" claim is WYSIATI -- it ignores 14+ files referencing localhost:8001.

Evidence: grep `localhost:8001` across apps/web/src/ returns 15 occurrences across 8 files.

**CONFLICT 2: Rust Velocity dimensions disagree.**
Brain #5 defines 3 dimensions (runtime latency, dev cycle time, LOC) measured at midpoint with 0.5x trigger. Brain #6 defines 4 dimensions (time to implement, LOC handler, LOC tests, test cycle time) with 2.0x trigger.

Winner: Brain #6's 4 dimensions are more complete (includes implementation wall-clock time). But Brain #5's 0.5x trigger threshold is more aggressive and more appropriate for a VS -- the point is to detect failure early, and 2.0x is too forgiving. Brain #6's 2.0x means you can take TWICE as long on the vertical slice and still proceed, which defeats the purpose of a velocity check.

Resolution: Use Brain #6's 4 metrics with Brain #5's 0.5x trigger threshold for runtime and dev cycle. Use Brain #6's 2.0x threshold for LOC only (structural verbosity is acceptable; velocity death is not).

**CONFLICT 3: tasks.ts calls /api/tasks, not /api/tasks/auto.**
All three brains assume the VS endpoint is /api/tasks/auto. The current Server Action (tasks.ts line 66) calls `${FASTAPI_URL}/api/tasks` (the generic endpoint, not /auto). The /auto endpoint exists in Python (tasks.py line 128) but the frontend does NOT currently use it.

Winner: Brain #5 is correct that /auto is the better VS choice (it exercises FlowDetector + gRPC bidirectional). But no brain identified that the "one line swap" requires changing both the URL path AND the request body schema (CreateTaskRequest has a `brief` field; AutoTaskRequest likely differs). This is not one line -- it is an API contract change.

Evidence: tasks.ts line 66 calls `/api/tasks` with body `{ brief }`. tasks.py line 128 defines `/auto` with AutoTaskRequest (likely different schema). The Server Action must change URL path, request schema, and response handling.

### Second-Order Concerns

**SYSTEMS GAP 1: The Lollapalooza Effect of Simultaneous Novelty (no brain identified this)**

Phase 13 introduces 4 independent unknowns simultaneously: Rust language, tonic/gRPC framework, SQLx + PostgreSQL, and Docker Compose multi-service orchestration. When any bug appears during development, its origin is ambiguous -- is it a Rust ownership error, a gRPC serialization mismatch, a PostgreSQL connection pool timeout, or a Docker network issue? This ambiguity multiplies debugging time non-linearly. The NotebookLM sources confirm this pattern (Circle of Competence, Lollapalooza Effect -- source IDs 55eeb28c, 5db6e11a).

Cascade: ambiguous bug -> developer tries first fix that works (Doubt-Avoidance Tendency) -> technical debt in Rust/gRPC layer -> subsequent phases build on compromised foundation -> escape hatch triggers too late because "it compiles and tests pass."

**SYSTEMS GAP 2: Configuration Fragmentation Drift (Brain #4 introduced, no brain caught)**

The current codebase has 2 env var names for the same thing (FASTAPI_URL, API_URL). Brain #4 proposes adding a THIRD (CONTROL_PLANE_URL). If accepted, Phase 13 ships with 3 names for "the URL I call the backend." By Phase 15 (dual-write), some endpoints go to Rust and some stay on Python. Which env var points where? Developers (including future you) will waste time on "am I calling the right service?" debugging sessions.

Cascade: 3 env var names -> Phase 15 dual-write requires routing by endpoint -> developer confusion -> bug in production routing -> data written to wrong service -> data loss or split-brain state.

**SYSTEMS GAP 3: Local Development Cold Start (no brain addressed)**

Current Docker Compose: 2 services (api:8001, web:3000). Phase 13 adds: Rust control-plane (port TBD) + PostgreSQL 16 (port 5432). That is 4 services. Current cold start: `docker compose up -d` -> 2 containers. Phase 13 cold start: 4 containers + proto codegen + Rust compilation + PostgreSQL initialization + health checks for all 4 services.

No brain measured or proposed measuring the local development boot time. The NotebookLM sources identify "Time to Value" and "Experiment Velocity" as critical metrics for developer adoption (source IDs 742c3cef, b288f2a3). If boot time exceeds 2 minutes, the developer will stop running the full stack locally, which defeats the E2E smoke test (Layer 5).

Cascade: slow boot -> developer runs only Rust unit tests -> gRPC integration bugs not caught until CI -> CI cycles longer -> velocity drops -> Phase 13 timeline slips.

**SYSTEMS GAP 4: Proto Codegen Tax (all brains assumed zero friction)**

All three brains assume proto codegen "just works." Reality: tonic-build (Rust), betterproto (Python), and protoc-gen-es (TypeScript) are three independent codegen tools with different versions, different plugin configs, and different error messages. Brain #6's CI gate catches DRIFT but does not address the TIME cost of maintaining 3 codegen targets. Every field change to brain_runtime.proto triggers: edit proto -> regenerate Rust -> regenerate Python -> regenerate TypeScript -> fix any compile errors in 3 languages.

This is a permanent tax, not a one-time cost. The domain brains treated it as infrastructure, but for a solo developer it is a velocity drag that compounds with every proto change.

**SYSTEMS GAP 5: Pre-requisite Setup Time Underestimated (Brain #6 listed 7 items, no brain estimated the time)**

Brain #6 lists 7 pre-requisites: buf CLI, protoc, PostgreSQL 16 Docker, asyncpg, testcontainers-postgres, proto/ directory with buf config, apps/control-plane/ cargo init. No brain estimated how long these take to set up and validate. For a developer with zero Rust toolchain experience: rustup + cargo + tonic-build dependencies + protoc installation + buf CLI + Docker PostgreSQL config + proto directory structure + first successful cargo build. This is easily 1-2 days of setup before ANY feature code is written.

### Metric Proposals

- **SLI-1 (Time to First Green):** Time from "cargo init" to first passing `cargo test` with a gRPC round-trip to Python. Target: <= 3 working days. If > 5 days, the learning curve is steeper than estimated and timeline must be recalibrated.

- **SLI-2 (Local Boot Time):** `docker compose up -d` to all 4 services healthy (api, web, control-plane, postgres). Target: <= 90 seconds. If > 120 seconds, operational complexity is cannibalizing development velocity.

- **SLI-3 (Proto Change Cycle Time):** Time to make a single field addition to brain_runtime.proto and have all 3 codegen targets compile clean. Target: <= 15 minutes. If > 30 minutes, the proto tax is unsustainable for a solo developer.

- **SLI-4 (Debugging Ambiguity Rate):** Count of debugging sessions where the root cause was ambiguous between Rust/gRPC/PostgreSQL/Docker. Target: <= 3 per week during Phase 13. If > 5 per week, the Lollapalooza Effect is active and one unknown should be removed (e.g., use SQLite instead of PostgreSQL for Rust, defer gRPC complexity).

- **OKR-1 (Configuration Unification):** Before Phase 13 ships, ALL 15 references to localhost:8001 across apps/web/src/ must use a SINGLE env var name. Zero tolerance for 3 names doing the same job. Measured by: `rg -c "localhost:8001" apps/web/src/` must return 0 results (all replaced by env var).

- **OKR-2 (Velocity Checkpoint):** At Phase 13 midpoint, Rust Velocity Protocol metrics are recorded in velocity-measurements.md. If ANY dimension (runtime latency, dev cycle, wall-clock implementation) exceeds 2.0x Python baseline, a formal go/no-go decision is required before continuing.

### Omission Bias -- What All Three Brains Missed

1. **No rollback plan.** All three brains designed forward. None addressed: what specific artifacts get reverted if Phase 13 proves Rust is not viable? The proto files, the Rust crate, the PostgreSQL schema, the Docker Compose changes, the env var changes -- what gets deleted and what stays? Without a rollback spec, Phase 13 creates orphaned infrastructure even if the escape hatch triggers.

2. **No observability for the VS itself.** The domain brains propose measuring Rust velocity but not measuring whether the VS endpoint is actually being called during development. If the developer falls back to testing Python endpoints (because they already work), Phase 13 can "complete" without ever truly validating the 3-service architecture.

3. **No capacity planning for PostgreSQL in Docker.** SQLite is a file. PostgreSQL 16 in Docker requires memory, disk, and configuration. No brain addressed PostgreSQL resource requirements for local development. On WSL2 (the confirmed development environment), Docker memory limits can silently degrade PostgreSQL performance, making Rust appear slower than it is -- a false negative that could kill the Rust decision.

### Verdict

APPROVED_WITH_CONDITIONS -- the vertical slice strategy is sound (validate before committing), the endpoint choice is correct (/auto exercises more layers), and the test layer structure is comprehensive. But 5 conditions are non-negotiable before Phase 13 begins:

1. **[BLOCKER] Configuration unification.** Pick ONE env var name. Migrate ALL 15 references. Do not ship Phase 13 with 3 names for the same URL. Evidence: grep returns 15 occurrences of localhost:8001 across apps/web/src/.

2. **[BLOCKER] Pre-requisite setup must be a separate, time-boxed step.** Allocate 1-2 days for toolchain setup (rustup, cargo, buf, protoc, PostgreSQL Docker). Time-box it. If setup exceeds 2 days, that IS a data point for the Rust Velocity Protocol.

3. **[CONDITION] Rollback plan documented before first line of Rust.** Which files/directories get deleted if the escape hatch triggers. This prevents orphaned infrastructure.

4. **[CONDITION] Local boot time SLI established before Phase 13 starts.** Measure current 2-service boot time as baseline. Set <= 90s target for 4 services. If boot time exceeds target during Phase 13, address it before Phase 14.

5. **[CONDITION] Velocity Protocol uses Brain #6's 4 metrics with Brain #5's 0.5x trigger for runtime/dev cycle, 2.0x for LOC.** This is the strongest combination -- aggressive velocity detection, lenient verbosity tolerance.

Source citations:
- Brain #4 output: "Single environment variable CONTROL_PLANE_URL" -- INCONSISTENT with codebase (15 occurrences of localhost:8001 with 2 different env var names)
- Brain #5 output: "Rust Velocity Protocol 3 dimensions 0.5x" -- CORRECT trigger threshold, INCOMPLETE metrics (missing wall-clock implementation time)
- Brain #6 output: "5 test layers, 7 pre-requisites" -- CORRECT scope, MISSING time estimate for setup
- Codebase: apps/web/src/app/actions/tasks.ts line 66 -- calls /api/tasks (NOT /api/tasks/auto), API contract change required
- Codebase: grep localhost:8001 across apps/web/src/ -- 15 occurrences in 8 files with 2 different env var names (FASTAPI_URL, API_URL)
- Codebase: docker-compose.yml -- 2 services currently, Phase 13 adds 2 more with no boot time measurement
- NotebookLM sources: Lollapalooza Effect (55eeb28c), WYSIATI (5db6e11a), Circle of Competence (76a9c932), Time to Value (742c3cef), Experiment Velocity (b289f2a3), Doubt-Avoidance Tendency (55eeb28c), Planning Fallacy (89cc29dd)

### Global Rating: 72/100

Deductions: -8 for configuration fragmentation not caught (Brain #4 introduced a third env var, no brain flagged this), -7 for "one line swap" WYSIATI (it is an API contract change, not a URL change), -5 for missing rollback plan (all forward, no backward), -4 for pre-requisite time underestimate (7 items, zero time estimate), -4 for local dev boot time not measured. The plan is directionally correct but the domain brains collectively underestimated the surface area of change for a solo developer operating outside their Circle of Competence.

## 2026-04-05 — Phase 13 Vertical Slice (Iteration 3) — Final Evaluation — Evaluation of: Phase 13 Plan Review (Iteration 3)

### Cross-Domain Synthesis

Three domain brains evaluated Phase 13 Vertical Slice across 4 waves (13-01 through 13-04). All 7 conditions from Iteration 1 were addressed in Iteration 3:

**Brain #5 Backend:** POST /api/tasks/auto as VS endpoint, Proto contract with single DispatchTask RPC, Rust single crate, PostgreSQL only for executions table, Rust Velocity Protocol with 4 metrics (time, LOC handler, LOC tests, test cycle) with 0.5x trigger for runtime/dev cycle, 2.0x for LOC.

**Brain #4 Frontend:** Server Action update to CONTROL_PLANE_URL, proto-generated types in apps/web/src/proto/, Server Components pattern with JWT in httpOnly cookies, one vitest integration test.

**Brain #6 QA/DevOps:** 5 test layers (Rust unit, proto contract, gRPC integration, PostgreSQL parity, E2E smoke), DatabaseConnection ABC extraction, proto sync CI gate with buf, 7 pre-requisites, test count 1038 → ~1086.

**Points of agreement:** All three agree on /api/tasks/auto endpoint, zero dual-write (deferred to Phase 15), zero impact on existing 1038 tests, PostgreSQL independent.

### Second-Order Concerns

**SYSTEMS GAP 1: Config-Contract Circular Dependency (NotebookLM confirmed)**

Plan 13-02 introduces proto sync CI gate that generates code for 3 languages. Plan 13-01 unifies env vars (FASTAPI_URL → CONTROL_PLANE_URL, API_URL → AGENT_RUNTIME_URL). If the proto sync CI gate reads CONTROL_PLANE_URL during codegen, but Plan 13-01 hasn't completed the migration, the gate fails. This is a Lollapalooza Effect — two independent changes (config naming + proto toolchain) compound to paralyze the pipeline.

Cascade: config migration incomplete → proto CI gate fails → cannot generate Rust/Python/TS bindings → Plan 13-03 gRPC client/server cannot compile → Phase 13 blocked at Plan 13-02.

**SYSTEMS GAP 2: Contract Rollback Incompatibility (NotebookLM confirmed)**

The rollback decision tree in Plan 13-01 Task 3 covers deployment artifacts (delete apps/control-plane/, revert docker-compose.yml, delete proto/). But it omits CONTRACT VERSIONING. If Plan 13-04 ships (Frontend Server Action calls CONTROL_PLANE_URL with new AutoTaskRequest schema), then the rollback triggers and reverts to Python-only backend, the Frontend is now calling an endpoint that doesn't exist. The rollback breaks the frontend.

Cascade: rollback Rust backend → Frontend still uses new contract → 404 on POST /api/tasks/auto → VS cannot be tested even if Python backend is restored → need to ALSO revert Frontend or add compatibility layer. Rollback tree doesn't specify this.

**SYSTEMS GAP 3: PostgreSQL Initialization State Missing (NotebookLM confirmed)**

Plan 13-01 adds PostgreSQL 16 + pgvector service. Plan 13-03 creates executions table via SQLx migration. But nowhere does the plan specify WHEN the migration runs. Is it manual? Is it automated on container startup? If the developer runs `docker compose up -d` and PostgreSQL starts healthy but the executions table doesn't exist, the first POST /api/tasks/auto call fails with "relation executions does not exist."

Cascade: PostgreSQL healthy → migrations not run → first request fails → developer assumes Rust broken → wastes time debugging gRPC when the issue is missing migration → boot time SLI degraded for wrong reason.

**SYSTEMS GAP 4: Half-Life Failure Mode (NotebookLM confirmed)**

The rollback decision tree assumes binary success/failure. But what if the system "works" but Boot Time SLI increases by 400% (from 30s to 120s) due to gRPC overhead + PostgreSQL + Docker network latency? The tree has no branch for "Performance Degradation — system functional but violates SLI." In this case, Action Bias leads the team to keep pushing forward ("it works, optimize later") when the correct response is to trigger escape hatch (Rust is too slow).

**SYSTEMS GAP 5: Rollback Mechanism Dependency Paradox (NotebookLM confirmed)**

The rollback tree says "if velocity escape hatch triggers, delete apps/control-plane/ and revert docker-compose.yml." But if CONTROL_PLANE_URL is already deployed to production (even if just internal localhost), reverting docker-compose.yml requires knowing which env vars to revert TO. The rollback mechanism depends on the new unified config being functional enough to execute the revert. If the config layer itself is broken, you cannot execute the rollback.

### Metric Proposals

- **SLI-1 (Config-Contract Sync Success Rate):** % of proto sync CI gate passes that do NOT fail due to missing env vars. Target: 100%. If any CI failure traces back to CONTROL_PLANE_URL not being set, the Config-Contract loop is active and Plan 13-01/13-02 coupling must be decoupled.

- **SLI-2 (Rollback Reversibility Time):** Time from "escape hatch trigger" decision to "system fully reverted to pre-Phase 13 state." Target: <= 30 minutes. If > 60 minutes, the rollback is not actually an escape hatch — it's a migration project. Measured by: timestamp trigger → timestamp docker compose up -d succeeds with 2 services (api + web) only.

- **SLI-3 (PostgreSQL Migration Automation):** % of PostgreSQL service starts that include schema migration WITHOUT manual intervention. Target: 100%. If developer must run `psql -f migrations/001_executions.sql` manually, the initialization state is incomplete. Measured by: count of manual migration steps documented in runbook.

- **OKR-1 (Pre-mortem Completion):** Before Phase 13 execution begins, a written pre-mortem document must exist: "It is 48 hours from now, the 4-service orchestration has crashed CI/CD. Working backward, what failed?" Required scenarios: (a) proto sync gate blocked by env vars, (b) PostgreSQL migrations not run, (c) gRPC timeout cascades to frontend, (d) boot time 400% degradation. This is not optional — it is the Inversion principle applied.

### Verdict

APPROVED_WITH_CONDITIONS — all 7 conditions from Iteration 1 are now addressed, and the plan is directionally sound. But 4 SYSTEMS-LEVEL conditions remain from NotebookLM analysis:

1. **[BLOCKER] Config-Contract decoupling.** Plan 13-02 proto sync CI gate must NOT depend on CONTROL_PLANE_URL being set. If the gate requires env vars to run codegen, the gate must fail gracefully (skip codegen, warn) rather than block the entire pipeline. Evidence: NotebookLM source "Lollapalooza Effect" — compound novelty paralyzes pipeline.

2. **[BLOCKER] Contract rollback compatibility.** The rollback decision tree (Plan 13-01 Task 3) must add a branch: "If Frontend has shipped with new contract, rollback Frontend Server Action OR add Python compatibility layer for /api/tasks/auto." Evidence: NotebookLM source "Contract Rollback Incompatibility" — binary rollback breaks frontend.

3. **[BLOCKER] PostgreSQL initialization automation.** Plan 13-01 Task 2 must specify HOW migrations run. Options: (a) SQLx migrate in Rust app startup, (b) init script in Docker image, (c) manual step documented. No "we'll figure it out" — the first request will fail without this. Evidence: NotebookLM source "Data State Persistence" omission.

4. **[CONDITION] Half-Life failure mode branch.** Rollback decision tree must add: "If system works but Boot Time SLI > 120s OR Rust Velocity > 2.0x Python, trigger escape hatch." Performance degradation is a failure mode, not a success. Evidence: NotebookLM source "Inversion" — asking what guarantees failure.

5. **[CONDITION] Pre-mortem document required.** Before writing first Rust line, write "pre-mortem-13.md" with 4 failure scenarios worked backward from "CI/CD crashed 48 hours from now." Evidence: NotebookLM source "Pre-mortem" — imagine failure to prevent it.

Source citations:
- NotebookLM Brain #7 sources: Lollapalooza Effect (55eeb28c), WYSIATI (5db6e11a), Circle of Competence (76a9c932), Planning Fallacy (2b770e1f), Inside View (2b770e1f), Twaddle Tendency (55eeb28c), Inversion (55eeb28c), Pre-mortem (5db6e11a), Action Bias (55eeb28c)
- Plan 13-01 Task 1: "Unify env vars FASTAPI_URL → CONTROL_PLANE_URL, API_URL → AGENT_RUNTIME_URL"
- Plan 13-01 Task 3: "Document rollback scenarios in rollback-plan.md"
- Plan 13-02 Task 4: "Proto sync CI gate with buf lint + buf generate + drift check"
- Plan 13-03 Task 3: "PostgreSQL repository with SQLx compile-time verified queries"
- Plan 13-04 Task 2: "Docker Compose with 4 services: web, control-plane, api, postgres"

### Global Rating: 82/100

Improvement from Iteration 2 (72 → 82): +10 for addressing all 7 original conditions (config unification, time-box, baseline spec, rollback plan, boot time SLI, velocity protocol, observability).

Remaining deductions: -8 for Config-Contract circular dependency not caught, -6 for Contract Rollback Incompatibility, -4 for PostgreSQL initialization state missing.

The plan is APPROVED_WITH_CONDITIONS because the systems-level gaps are correctable BEFORE execution begins (they are planning gaps, not architectural flaws). Once the 4 blockers/conditions above are addressed in the plan documents, Phase 13 is ready to ship.


---

## 2026-04-05 — Phase 13 Vertical Slice — Evaluation of: Brains #4 #5 #6 (Rust Control Plane + PostgreSQL + gRPC)

### Cross-Domain Synthesis

Three domain brains consulted for Phase 13 Vertical Slice (Rust Control Plane + PostgreSQL + gRPC infrastructure).

Brain #4 Frontend: APPROVED. Recommends POST /api/tasks/auto via Server Action (apps/web/src/app/actions/tasks.ts). Single file change from FASTAPI_URL to CONTROL_PLANE_URL. Proto types coexist in apps/web/src/proto/ — no query hooks or stores modified. Server Components pattern confirmed (JWT httpOnly cookies accessible server-side only).

Brain #5 Backend: APPROVED. Recommends mastermind.v1.BrainRuntime gRPC service with single RPC (DispatchTask). Rust Control Plane as single crate (NOT workspace — workspace decomposition deferred to Phase 15). PostgreSQL for executions table only — Python's 631 tests stay on SQLite (:memory:). Dual-write is Phase 15, not Phase 13.

Brain #6 QA/DevOps: APPROVED. Five test layers specified (Rust unit, proto contract, gRPC integration, PostgreSQL parity, E2E smoke). Proto-sync CI gate prevents drift. Velocity protocol with 4 metrics: wall-clock time, LOC handler, LOC tests, test cycle time. Escape hatch triggers: 0.5x for runtime/dev cycle (Brain #5), 2.0x for LOC (Brain #6).

Points of agreement: All 3 brains converged on POST /api/tasks/auto as correct path. All agree Phase 13 is vertical slice NOT full migration. All agree Python tests unaffected (631 passing confirmed).

Points of tension: None identified — all brains aligned on scope and approach.

### Second-Order Concerns

FEEDBACK LOOP — Config-Contract Circular Dependency: Plan 13-01 env var unification (FASTAPI_URL → CONTROL_PLANE_URL) MUST complete before Plan 13-02 Rust config.rs reads CONTROL_PLANE_URL. If Plan 13-02 starts before Plan 13-01 completes, Rust compiles but cannot connect — silent failure mode. Mitigation: Plan 13-02 Task 4 CI gate fails gracefully (warning only if CONTROL_PLANE_URL not in .env.example). CI passes even during setup — prevents pipeline paralysis.

FEEDBACK LOOP — Proto-Sync Bottleneck: All three brains agree on gRPC/proto path, but second-order effect is reduced Experiment Velocity. If every frontend change requires coordinated proto update + backend recompile, the "1-2 day toolchain setup" assumption falls victim to Planning Fallacy. Mitigation: "Decoupled development mode" where frontend uses local mock schema while gRPC contract finalizes.

CASCADE FAILURE — grpclib Installation Block: If grpclib install fails or takes > 30min → Python gRPC server blocked → entire VS blocked. Mitigation: Condition 2 in Plan 13-01 — record as "setup overhead" and continue with mock gRPC. Pre-mortem Scenario A documents this failure mode with prevention strategy.

CASCADE FAILURE — PostgreSQL Migration Missing: If Plan 13-01 adds PostgreSQL service and Plan 13-03 adds ExecutionRepo but neither specifies WHEN migrations run → first request fails with "relation executions does not exist" → 500 error in production. Mitigation: Plan 13-01 Task 2 specifies docker/postgres/init-db.sql with migrations. PostgreSQL runs init script automatically on first startup. Pre-mortem Scenario B analyzes this root cause.

CASCADE FAILURE — Boot Time Degradation (Half-Life Failure Mode): If boot time increases from 30s (2 services) to 150s (4 services) → developers stop running full stack → integration bugs missed (e.g., gRPC serialization issue discovered in production). Mitigation: Plan 13-01 Task 3 measures baseline BEFORE Phase 13 starts. Target: 4 services ≤ 90s. Escape hatch trigger: > 120s OR > 400% degradation from baseline. Pre-mortem Scenario D documents this "slow failure" mode.

CASCADE FAILURE — gRPC Timeout Cascade: If Python gRPC server slow to start (grpclib startup delay) AND frontend has no timeout → waits forever → retry logic triggers 3 simultaneous requests → each spawns Rust handler → Python gRPC call → system overload. Mitigation: Plan 13-03 Task 2 Rust gRPC client with timeout (tonic Channel::timeout). Plan 13-04 Task 1 Next.js fetch with timeout (AbortController). Response time SLI: < 2s. Pre-mortem Scenario C analyzes this cascade.

METRIC BLINDSPOT — Treatment Exposure Rate: Current metrics focus on technical performance (latency, LOC, test cycle) but ignore Overall Evaluation Criteria (OEC). If users are never "exposed" to new /api/tasks/auto path because of frontend conditional logic, any performance "win" is a Vanity Metric. Mitigation: Track % of requests to /api/tasks/auto vs /api/tasks. If < 50% by midpoint → VS not validated. This is Brain #7 CONDITION #7 — added to Plan 13-01 Task 3.

METRIC BLINDSPOT — Boot Time Baseline Documentation: "Local boot time ≤ 90s" is verifiable, but baseline measurement must be documented BEFORE Phase 13 starts with timestamp, service names, and time to healthy explicitly. Otherwise, "90s target" has no anchor. Mitigation: Plan 13-01 Task 3 explicitly documents: "Document in velocity-baseline.md: Baseline (2026-04-05): 2 services (api + web) = X seconds to healthy."

CROSS-DOMAIN TRADEOFF — Workspace Decomposition: Brain #5 optimized for single crate (simpler VS). Brain #6 wants workspace decomposition (Phase 15). This is correctly deferred — single crate for VS, workspace decomposition is Phase 15. No conflict.

### Metric Proposals

**Leading Indicators (prevent cascade failure):**
- SLI-1 (Boot Time): `time docker compose up -d` ≤ 90s for 4 services. If > 120s → trigger escape hatch.
- SLI-2 (Treatment Exposure Rate): % of requests to /api/tasks/auto vs /api/tasks ≥ 50% by midpoint. If < 50% → VS not validated.
- SLI-3 (Error Rate Guardrail): First 100 requests to /api/tasks/auto must have error rate < 0.1%. If exceeded → automatic kill switch on route, revert to legacy /api/tasks.
- SLI-4 (gRPC Call Duration): P95 < 500ms for DispatchTask RPC. If > 2s → investigate Python gRPC server health.

**Lagging Indicators (measure velocity hypothesis):**
- SLI-5 (Rust vs Python Wall-Clock Time): Rust implementation time / Python baseline ≤ 2.0x. If > 2.0x → escape hatch trigger.
- SLI-6 (Rust vs Python LOC): Rust LOC / Python LOC ≤ 2.0x for equivalent functionality. (Lenient — Rust verbosity acceptable per Brain #6).
- SLI-7 (Dev Cycle Time): Edit-build-test cycle time (cargo test vs pytest). Rust must NOT be < 0.5x Python (aggressive trigger per Brain #5 — if Rust is this much faster, investigate measurement error).

**OKR (Vertical Slice Validation):**
- OKR-1: User can trigger POST /api/tasks/auto from UI, request flows through all 5 layers (Next.js → Rust → gRPC → Python → PostgreSQL → UI), response time < 2s, all 4 services healthy in Docker Compose. Success = Rust Control Plane validated for Phase 15 expansion.

### Verdict

**APPROVED** — Delta-Velocity Rating 5 (Principal). Phase 13 ready for execution in background agent.

**Evidence citations:**
- Source: `.planning/phases/13-vertical-slice/13-PLAN-REVIEW.md > CORRECTED ASSUMPTIONS` — 7 conditions from Iteration 1 all addressed.
- Source: `.planning/phases/13-vertical-slice/13-PLAN-REVIEW.md > CORRECTIONS APPLIED (Iteration 4)` — 4 systems-level blockers all mitigated.
- Source: `.planning/phases/13-vertical-slice/pre-mortem-13.md` — 4 failure scenarios analyzed with prevention strategies (proto-sync blocked, PostgreSQL migrations missing, gRPC timeout cascade, boot time degradation).
- Source: `.planning/phases/13-vertical-slice/13-BRAIN-OUTPUTS.md > Brain #5` — "Phase 13 does NOT implement dual-write. Rust writes only to PostgreSQL. Python's 631 tests stay on SQLite."
- Source: `.planning/phases/13-vertical-slice/13-BRAIN-OUTPUTS.md > Brain #4` — "Server Action runs on the server, calls Rust, returns to the client. This is the CORRECT pattern because JWT in httpOnly cookies only accessible server-side."
- Source: `BRAIN-FEED.md > Stack (Locked)` — Next.js 16.x App Router confirmed, React 19.x Compiler disabled confirmed.
- Source: `apps/web/src/app/actions/tasks.ts:23-24` — FASTAPI_URL reference confirmed (VERIFIED via grep).
- Source: `apps/api pytest --collect-only` — 631 tests confirmed (VERIFIED via pytest).

**Confidence Score:** 95%. Pre-mortem analysis addressed 4 failure modes. Feedback loop risks mitigated with graceful CI failure and decoupled development mode. Cascade failure modes documented with prevention strategies. Metric blindspots covered (Treatment Exposure Rate, Boot Time Guardrail, Error Rate Kill Switch). Cross-domain tradeoffs resolved (single crate for VS, workspace deferred to Phase 15). The remaining 5% is unknown unknowns (black swans) — acceptable for a vertical slice with escape hatch documented.

**Key Success Factors:**
1. Measure boot time baseline BEFORE starting (Plan 13-01 Task 3) — establishes anchor for 90s target.
2. If grpclib install fails → pivot to mock gRPC immediately (Condition 2) — prevents VS blockage.
3. Proto-sync CI gate fails gracefully (warning only if env vars missing) — prevents pipeline paralysis during setup.
4. PostgreSQL init script automation (docker/postgres/init-db.sql) — prevents "relation does not exist" cascade.
5. Treatment Exposure Rate ≥ 50% by midpoint — validates VS is actually being used, not just deployed.
6. Escape hatch triggers: > 120s boot time OR > 400% degradation OR > 2.0x velocity ratios — clear decision points.

**Background Agent Instructions:**
- Pre-mortem integration: Agent must simulate grpclib installation failure in first hour and pivot to Condition 2 mock gRPC.
- Fermi estimation for boot time: Before writing code, estimate crate size + dependency tree to verify 90s target is physically realistic.
- Statistical power check: Ensure /api/tasks/auto receives enough traffic to meet Minimum Detectable Effect (MDE) for latency. If sample size too small, favor E2E smoke tests over quantitative metrics.

---

*Phase 13 evaluation completed: 2026-04-05*
*4 planning iterations, 7 conditions, 4 systems-level blockers, 4 pre-mortem scenarios — all addressed*

---

## 2026-04-06 — Phase 14 Knowledge Distillation — Evaluation of: Plan Review Iteration 2

### Cross-Domain Synthesis

Four plans evaluated for knowledge distillation system: Quality score calculation (14-01), Auto-evaluation loop (14-02), Template generation (14-03), Dashboard API (14-04). Iteration 2 applied 4 fixes addressing BLOCKING gaps: SQLite percentile → Python calculation, router registration correction, cold start fallback, quality score calibration documentation.

No domain brain outputs provided — this is a plan-only evaluation. The iteration delta shows responsiveness to technical blocking issues, but reveals a deeper systemic gap.

### Second-Order Concerns

**FEEDBACK LOOP GAP: Quality Score Chicken-and-Egg**

Plan 14-03 extracts templates from records with `quality_score >= 3.0`. Plan 14-01 defines quality_score calculation. Plan 14-02 creates auto-eval hook but defers actual Brain #7 LLM call to Phase 15. Fix 4 documents this deferral.

The loop: Quality scores required → Templates extracted → Analytics measure success → Better quality scores.

The break: Without Brain #7 auto-eval wired (Phase 15), quality_score field is NULL/default for all records. Plan 14-03's cold start fallback (Fix 3) lowers threshold to 2.0, but still requires quality_score to be populated. If all records have NULL quality_score, the fallback doesn't help — zero templates extracted anyway.

Named cascade: Missing quality_score seeding → Plan 14-03 produces zero output → Plan 14-04 analytics shows zero templates → System appears broken → Teams loses confidence in knowledge distillation → Feature abandoned.

This is not speculative. The codebase has existing `experience_records` (Phase 12) without quality_score. Without a seeding mechanism, the system starts empty.

**CASCADE RISK UNADDRESSABLE BY ITERATION FIXES: ExperienceLogger Startup Gap**

Brain #7 feed line 87 documented: `create_experience_schema()` exists (database.py:305) but is NOT called in startup_event (app.py:135-143). The iteration delta fixes 4 specific technical gaps but does NOT address this prerequisite.

All 4 plans depend on `experience_records` table existing:
- Plan 14-01: Rejection filter queries `WHERE quality_score >= 1.0` — table doesn't exist → crash
- Plan 14-02: Auto-eval hook calls `log_execution()` — table doesn't exist → crash
- Plan 14-03: Template extraction queries `experience_records` — table doesn't exist → crash
- Plan 14-04: Analytics API queries record counts — table doesn't exist → crash

This is a BLOCKER for the entire phase. The 5-minute fix (add `await create_experience_schema()` to startup_event) is outside Plan 14 scope but is a **prerequisite dependency** that must be confirmed before execution.

**Metric Blindspot: No Template Pollution Detection**

Fix 3's cold start fallback lowers threshold from 3.0 to 2.0 with warning. This admits lower-quality templates into the knowledge base. The plan tracks `success_rate` per template, but does NOT define a **template eviction threshold**.

If a template's success_rate drops below 0.3 (30%), it should be retired. Without eviction, the knowledge base accumulates noise → retrieval quality degrades → delta-velocity increases instead of decreasing. This is the Meadows "memory without decay" risk all over again, applied to templates instead of records.

### Metric Proposals

- **SLI-1 (Quality score seeding rate):** Percentage of existing `experience_records` with non-NULL quality_score after Plan 14-02 execution. Target: 100%. If < 100%, template extraction (Plan 14-03) operates on incomplete data.

- **SLI-2 (Template extraction yield):** Number of templates extracted in Plan 14-03 execution. Minimum viable threshold: >= 3 templates. If zero, the cold start fallback failed or quality_score seeding didn't run.

- **SLI-3 (Template eviction rate):** Percentage of templates with success_rate < 0.3 that are retired after 100 uses. Target: > 0%. If zero, knowledge base accumulates pollution without cleanup.

- **OKR (Knowledge distillation activation):** By end of Phase 14, a second consultation on the same topic must cite >=1 template AND complete in < 90s. If T1 doesn't decrease vs manual baseline (210-270s), the distillation system is not delivering value.

### Verdict

**APPROVED_WITH_CONDITIONS** — The iteration delta fixes are correct and address the specific BLOCKING technical gaps identified. However, two systemic gaps remain that will cause cascade failure if unaddressed:

**1. [BLOCKER] ExperienceLogger startup verification.** Before ANY Plan 14 task executes, verify `create_experience_schema()` is called in `apps/api/mastermind_cli/api/app.py` startup_event. Evidence: Brain #7 feed line 87 confirmed missing call. All 4 plans depend on this table existing.

**2. [CONDITION] Manual quality_score seeding in Plan 14-02.** Add explicit task: "Seed quality_score for existing experience_records using placeholder heuristic before auto-eval is wired." Example heuristic: status=success → 2.0, status=timeout → 0.5, status=failure → 0.0. This unblocks Plan 14-03 from producing zero output. Evidence: Plan 14-03 line 122 requires `quality_score >= 3.0`, Plan 14-02 defers auto-eval to Phase 15, Fix 4 confirms dependency.

**3. [CONDITION] Template eviction threshold definition.** Add to Plan 14-03 acceptance criteria: "Templates with success_rate < 0.3 after 100 uses are marked inactive." This prevents knowledge base pollution. Evidence: Fix 3 lowers threshold to 2.0 → admits lower-quality templates → cleanup mechanism required.

The 4 iteration fixes are sound (75% confidence). The chicken-and-egg gap (quality_score required but doesn't exist) is a systemic oversight that manual seeding resolves. The startup gap is a prerequisite dependency, not a Plan 14 task, but must be confirmed before execution.

Source citations:
- Fix 1 line 11: "SQLite percentile → Python calculation" — resolves BLOCKING runtime error
- Fix 2 line 17: "Router registration with correct file path" — resolves BLOCKING 404 error
- Fix 3 line 23: "Cold start fallback added" — resolves HIGH RISK bootstrap failure
- Fix 4 line 29: "Quality score calibration note added" — acknowledges MEDIUM RISK deferral
- Brain #7 feed line 87: `create_experience_schema() NOT called in startup_event` — CONFIRMED GAP
- Plan 14-03 line 122: Templates extracted from `quality_score >= 3.0` records — requires quality_score to exist
- Plan 14-02 line 100: Auto-eval hook created but Brain #7 call deferred — confirms no quality_score logic
- NotebookLM sources: Feedback loops, cascade failure, second-order effects, metric blindspots

---
