# Phase 13 — Plan Review Context
> Generated: 2026-04-05T16:00:00Z
> Updated: 2026-04-05T17:00:00Z
> Iteration: 4 (FINAL)
> Purpose: Full context for Brain #7 plan validation (ALL blockers addressed)
> Pre-mortem completed: pre-mortem-13.md

---

## IMPLEMENTED REALITY

From BRAIN-FEED.md (global patterns + invariants):

**Stack (Locked):**
- Next.js 16.x (App Router only, no Pages)
- React 19.x (Compiler disabled, conflicts with React.memo on RF nodes)
- TypeScript 5.x (strict mode)
- Tailwind CSS 4.x (CSS-only config)
- Zustand 5.x + Immer middleware
- Python 3.14, uv (never pip/poetry)
- pnpm (never npm/yarn)

**Architecture Invariants:**
- Brain Bundle = 3-file directory: brain-NN-domain.md + criteria.md + warnings.md
- Brain #7 dispatched AFTER domain brains complete (never in parallel)
- Structured output required in all brain agent responses (free-text causes information leaks)
- Domain feeds are READ-ONLY for agents (never modify)

**Implemented Features:**
- Auth flow: `apps/web/src/app/(auth)/login/` (Server Actions, httpOnly cookie)
- JWT verification: `apps/web/src/lib/auth.ts` (jose, Edge Runtime)
- WS infrastructure: `apps/web/src/stores/wsDispatcher.ts` (module singleton)
- POST /api/tasks: `apps/web/src/app/api/tasks/route.ts` (creates task, returns taskId)
- Brain Agent Bundles: `.claude/agents/mm/` (7 brain bundles)
- 985 tests total (578 backend pytest + 407 frontend vitest)

**Active Constraints:**
- No `npm` or `pip` — pnpm for Node, uv for Python
- Brain #7 dispatch order: ALWAYS after domain brains complete
- Structured output required in all brain agent responses

---

## PLAN SUMMARIES

### Plan 13-01: Foundation (Wave 1)
**Objective:** Unify environment variables + PostgreSQL + baseline + rollback

**Task 1:** Unify env vars (FASTAPI_URL/API_URL → CONTROL_PLANE_URL/AGENT_RUNTIME_URL)
- Search all 15+ references
- Update docker-compose.yml, .env.example files
- Update apps/web/src/app/actions/tasks.ts to use CONTROL_PLANE_URL
- Migration guide in .env.example comments

**Task 2:** Add PostgreSQL 16 + pgvector to Docker Compose
- pgvector/pgvector:pg16 image
- Persistent volume
- healthcheck: pg_isready
- api service depends on postgres healthy
- Add asyncpg to apps/api/pyproject.toml

**Task 3:** Measure Python baseline + document rollback plan
- Measure time/LOC/test cycle for existing POST /api/tasks/auto
- Measure local boot time (docker compose up -d)
- Document rollback scenarios in rollback-plan.md
- Create velocity-baseline.md

**Success Criteria:**
- Zero FASTAPI_URL references in production code
- PostgreSQL 16 service healthy in Docker Compose
- velocity-baseline.md contains Python baseline metrics
- rollback-plan.md documents escape hatch
- Local boot time ≤ 90s

---

### Plan 13-02: Proto + Rust Setup (Wave 2)
**Objective:** Protobuf contract + Rust Control Plane project foundation

**Task 1:** Install buf CLI + create proto directory
- brew install bufbuild/buf/buf
- Create proto/mastermind/v1/brain_runtime.proto
- Define BrainRuntime.DispatchTask RPC
- buf.yaml + buf.gen.yaml for code generation

**Task 2:** Initialize Rust Control Plane project
- apps/control-plane/ with cargo init
- Cargo.toml: axum 0.7, tokio, tonic 0.11, prost, sqlx
- build.rs with tonic-build for proto codegen
- config.rs reads CONTROL_PLANE_URL, AGENT_RUNTIME_URL, POSTGRES_URL

**Task 3:** Generate proto code for all 3 languages
- buf generate creates: Rust, Python (protoc), TypeScript (ts-proto)
- Add grpclib to Python pyproject.toml
- Pre-commit hook prevents editing generated code

**Task 4:** Create proto sync CI gate
- .github/workflows/proto-sync.yml
- buf lint + buf generate + drift check
- Verify proto imports in Rust, Python, TypeScript

**Success Criteria:**
- brain_runtime.proto defines BrainRuntime.DispatchTask
- buf lint passes, proto sync CI gate active
- Rust Control Plane project builds (cargo check)
- Python grpclib installed
- Generated code is read-only (pre-commit hook)
- CI verifies proto modules are imported

---

### Plan 13-03: Backend Vertical Slice (Wave 3)
**Objective:** Python gRPC server + Rust client + PostgreSQL repo + Axum handler

**Task 1:** Python gRPC server (BrainRuntimeServicer)
- apps/api/mastermind_cli/api/routes/brain_runtime.py
- grpclib server on port 50051
- DispatchTask RPC calls FlowDetector.auto_detect()
- Return task_id, status, accepted_at_unix_ms
- Register in app.py startup event
- Integration tests pass

**Task 2:** Rust gRPC client to Python
- apps/control-plane/src/grpc/client.rs
- BrainRuntimeClient connects to localhost:50051
- dispatch_task() method uses generated proto types
- Unit tests with mock Python server

**Task 3:** PostgreSQL repository in Rust
- apps/control-plane/src/postgres/repo.rs
- ExecutionRepo with create_execution, get_execution
- SQLx compile-time verified queries (sqlx::query! macros)
- Migration creates executions table
- Unit tests pass

**Task 4:** Axum handler for POST /api/tasks/auto
- apps/control-plane/src/handlers/tasks.rs
- JWT validation (placeholder for VS, full in Phase 15)
- Calls gRPC client, creates execution in PostgreSQL
- Returns task_id, status, flow
- Integration tests pass

**Success Criteria:**
- Python gRPC server handles DispatchTask RPC
- Rust gRPC client connects to Python server
- PostgreSQL repository stores executions
- Axum handler routes POST /api/tasks/auto through complete backend chain
- All backend tests pass (Python + Rust)
- Zero regressions in existing Python tests (631 passing)

---

### Plan 13-04: Frontend + Docker + Checkpoint (Wave 4)
**Objective:** Frontend integration + Docker Compose + velocity report

**Task 1:** Update Next.js Server Action
- apps/web/src/app/actions/tasks.ts
- Change FASTAPI_URL → CONTROL_PLANE_URL
- Server Action calls Rust Control Plane POST /api/tasks/auto
- TypeScript compilation passes

**Task 2:** Add Rust Control Plane to Docker Compose
- docker/control-plane/Dockerfile (multi-stage build)
- control-plane service in docker-compose.yml
- All 4 services: web, control-plane, api, postgres
- Health checks for all services
- curl test passes

**Task 3:** Measure Rust velocity + create report
- Measure Rust time/LOC/test cycle
- Compare against Python baseline from velocity-baseline.md
- Calculate ratios: time, LOC, test cycle
- Document escape hatch decision in velocity-report.md
- Recommendation for Phase 15

**Task 4:** Checkpoint — Human verification
- Manual E2E test: UI → Rust → gRPC → Python → PostgreSQL → UI
- All services healthy in Docker Compose
- Response time < 2s
- Velocity report complete
- User types "approved" to continue

**Success Criteria:**
- User can trigger POST /api/tasks/auto from UI
- Full request flows through all 5 layers
- All 4 services run healthy in Docker Compose
- Response time < 2s
- Rust velocity measured vs Python baseline
- Escape hatch decision documented
- Zero regressions in existing tests

---

## CODE SNIPPETS

### Current State (Before Phase 13)

**apps/web/src/app/actions/tasks.ts (lines 23-24):**
```typescript
const FASTAPI_URL = process.env.FASTAPI_URL || "http://localhost:8001"
const response = await fetch(`${FASTAPI_URL}/api/tasks`, {...})
```

**docker-compose.yml (lines 28-29):**
```yaml
environment:
  API_URL: http://api:8001
```

**apps/api/pyproject.toml:**
- Uses aiosqlite for database
- No asyncpg dependency yet
- No grpclib dependency yet

### Target State (After Phase 13)

**apps/web/src/app/actions/tasks.ts (planned change):**
```typescript
const CONTROL_PLANE_URL = process.env.CONTROL_PLANE_URL || "http://localhost:3001"
const response = await fetch(`${CONTROL_PLANE_URL}/api/tasks/auto`, {...})
```

**proto/mastermind/v1/brain_runtime.proto (planned):**
```protobuf
syntax = "proto3";
package mastermind.v1;

service BrainRuntime {
  rpc DispatchTask(DispatchTaskRequest) returns (DispatchTaskResponse);
}

message DispatchTaskRequest {
  string brief = 1;
  string user_id = 2;
  string flow = 3;
}

message DispatchTaskResponse {
  string task_id = 1;
  string status = 2;
  int64 accepted_at_unix_ms = 3;
}
```

**apps/control-plane/src/handlers/tasks.rs (planned):**
```rust
pub async fn create_auto_task(
  State(grpc_client): State<BrainRuntimeClient>,
  State(repo): State<ExecutionRepo>,
  Json(request): Json<AutoTaskRequest>,
) -> Result<Json<AutoTaskResponse>, StatusCode> {
  // Call Python via gRPC
  let grpc_response = grpc_client
    .dispatch_task(request.brief.clone(), user_id.to_string(), None)
    .await?;

  // Create execution in PostgreSQL
  repo.create_execution(&request.brief, user_id, &grpc_response.flow).await?;

  Ok(Json(AutoTaskResponse {
    task_id: grpc_response.task_id,
    status: grpc_response.status,
    flow: grpc_response.flow,
  }))
}
```

---

## CORRECTED ASSUMPTIONS

**What Brain #7 might assume wrong:**

1. **"Next.js uses Pages Router"** — FALSE. Next.js 16 uses App Router only (no pages/ directory).
2. **"Python tests use pytest fixture"** — TRUE, but 631 tests stay on SQLite (:memory:), only new PostgreSQL tests added.
3. **"Frontend change is one-line"** — FALSE per Brain #7. AD-06 says "API CONTRACT CHANGE" not just URL change. `/api/tasks` uses `{brief}` body, `/api/tasks/auto` uses `AutoTaskRequest`. Must change URL + request schema + response handling.
4. **"Rust workspace from start"** — FALSE. AD-03 says single crate for VS, workspace decomposition is Phase 15.
5. **"PostgreSQL replaces SQLite in Phase 13"** — FALSE. AD-04 says PostgreSQL ONLY for Rust executions table. Python stays on SQLite. Dual-write is Phase 15.
6. **"grpclib is fast to install"** — CONDITIONAL. Brain #7 Condition 2: if grpclib install fails or takes > 30min, record as "setup overhead" and continue with mock gRPC.

---

## CORRECTIONS APPLIED (Iteration 2)

**Addressing Brain #7 BLOCKER #1 — Config unification:**
- DECISION MADE: FASTAPI_URL → CONTROL_PLANE_URL, API_URL → AGENT_RUNTIME_URL
- ZERO legacy names remain — clean migration, no aliases
- Updated Plan 13-01 Task 1 with explicit decision

**Addressing Brain #7 BLOCKER #2 — Pre-requisite time-box:**
- Time budget added: 1-2 days max for toolchain setup
- Breakdown: rustup/cargo/buf/protoc (4-6h), PostgreSQL Docker (1-2h), dependencies (1-2h)
- If > 2 days, record as "setup overhead" in velocity-baseline.md

**Addressing Brain #7 CONDITION #3 — Baseline specification:**
- SPECIFIED: Measure POST /api/tasks/auto (same endpoint Rust will implement)
- NOT /api/tasks (different endpoint, different functionality)
- Must measure full orchestration flow, not just handler in isolation

**Addressing Brain #7 CONDITION #5 — Local boot time SLI:**
- Measure BEFORE Phase 13 starts (current 2-service baseline)
- Target: 4 services ≤ 90s
- If > 120s during Phase 13 → valid escape hatch trigger

**Addressing Brain #7 CONDITION #6 — Velocity Protocol:**
- 4 metrics from Brain #6: wall-clock time, LOC handler, LOC tests, test cycle time
- 0.5x trigger for runtime/dev cycle (Brain #5)
- 2.0x trigger for LOC (Brain #6)

**Addressing Brain #7 CONDITION #7 — Observability:**
- Added Treatment Exposure Rate metric
- Track % of requests to /api/tasks/auto vs /api/tasks
- If < 50% by midpoint → VS not validated

---

## CORRECTIONS APPLIED (Iteration 3) — FINAL BLOCKERS

**Addressing BLOCKER — Rollback Plan (Iteration 2 gap):**
- ADDED detailed decision tree in Plan 13-01 Task 3
- 4 scenarios documented: velocity escape hatch, boot time escape hatch, grpclib setup failure, PostgreSQL migration failure
- Each scenario specifies: what to DELETE, what to KEEP, what to REVERT
- Pre-mortem complete before first Rust line

**Addressing CONDITION — Boot time baseline documentation:**
- ADDED explicit instruction: "Document in velocity-baseline.md: Baseline (2026-04-05): 2 services (api + web) = X seconds to healthy"
- Timestamp, service names, time to healthy all specified

---

## ITERATION 3 — FINAL REQUEST

Brain #7, please provide FINAL evaluation:

All 7 conditions from Iteration 1 have been addressed:
1. ✅ BLOCKER #1 (Config unification) — DECISION MADE, clean migration
2. ✅ BLOCKER #2 (Time-box) — 1-2 days with breakdown
3. ✅ CONDITION #3 (Baseline spec) — POST /api/tasks/auto specified
4. ✅ CONDITION #4 (Rollback plan) — DETAILED decision tree added
5. ✅ CONDITION #5 (Boot time SLI) — Measure BEFORE start with explicit documentation
6. ✅ CONDITION #6 (Velocity Protocol) — 4 metrics with triggers defined
7. ✅ CONDITION #7 (Observability) — Treatment Exposure Rate added

**Are all blockers and conditions now adequately addressed? Is the plan ready for execution?**

**Verdict:** APPROVED | APPROVED_WITH_CONDITIONS | REJECTED_REVISE

**Addressing Brain #7 BLOCKER #1 — Config unification:**
- DECISION MADE: FASTAPI_URL → CONTROL_PLANE_URL, API_URL → AGENT_RUNTIME_URL
- ZERO legacy names remain — clean migration, no aliases
- Updated Plan 13-01 Task 1 with explicit decision

**Addressing Brain #7 BLOCKER #2 — Pre-requisite time-box:**
- Time budget added: 1-2 days max for toolchain setup
- Breakdown: rustup/cargo/buf/protoc (4-6h), PostgreSQL Docker (1-2h), dependencies (1-2h)
- If > 2 days, record as "setup overhead" in velocity-baseline.md

**Addressing Brain #7 CONDITION #3 — Baseline specification:**
- SPECIFIED: Measure POST /api/tasks/auto (same endpoint Rust will implement)
- NOT /api/tasks (different endpoint, different functionality)
- Must measure full orchestration flow, not just handler in isolation

**Addressing Brain #7 CONDITION #5 — Local boot time SLI:**
- Measure BEFORE Phase 13 starts (current 2-service baseline)
- Target: 4 services ≤ 90s
- If > 120s during Phase 13 → valid escape hatch trigger

**Addressing Brain #7 CONDITION #6 — Velocity Protocol:**
- 4 metrics from Brain #6: wall-clock time, LOC handler, LOC tests, test cycle time
- 0.5x trigger from Brain #5 for runtime/dev cycle (aggressive)
- 2.0x trigger from Brain #6 for LOC (lenient — Rust verbosity acceptable)

**Addressing Brain #7 CONDITION #7 — Observability:**
- Added Treatment Exposure Rate metric
- Track % of requests to /api/tasks/auto vs /api/tasks
- If < 50% by midpoint → VS not being validated

---

## WHAT I NEED

Brain #7, please evaluate using your **Systems Thinker** lens:

1. **Planning Fallacy check** — What are we underestimating?
   - Toolchain setup time (rustup, cargo, buf, protoc, PostgreSQL Docker)
   - Proto sync CI gate complexity
   - Generated code read-only enforcement (will developers edit it anyway?)

2. **Omission Bias** — What's missing that will block execution?
   - grpclib server startup in FastAPI app.py (asyncio.create_task vs blocking start)
   - Axum JWT middleware (placeholder in VS, but does it break the chain?)
   - PostgreSQL migration tool (migrate.sql manually vs sqlx-cli vs other tool)

3. **Systems Thinking** — What feedback loops between plans?
   - Plan 13-01 env var unification MUST complete before Plan 13-02 Rust config.rs reads CONTROL_PLANE_URL
   - Plan 13-02 proto generation MUST complete before Plan 13-03 gRPC client/server can compile
   - Plan 13-03 backend MUST work before Plan 13-04 frontend can connect

4. **Over-engineering risk** — What won't be used?
   - TypeScript proto types in apps/web/src/proto/ (Plan 13-02 generates them, Plan 13-04 doesn't use them yet)
   - PostgreSQL parity tests (Plan 13-03 creates them, but Phase 15 is dual-write, so when do we run these?)

5. **Acceptance criteria quality** — Are done criteria verifiable?
   - "Local boot time ≤ 90s" — YES, can measure with `time docker compose up -d`
   - "Rust velocity measured vs Python baseline" — YES, but escape hatch trigger (0.5x) is vague. Is it wall-clock time? Dev cycle time (code + test + debug)? What about learning curve overhead?

**Be specific about WHICH plan and WHICH task.**

---

## ITERATION 2 REQUEST

Brain #7, please re-evaluate the plans with corrections applied:

1. **BLOCKER #1 (Config unification)** — DECISION MADE in Plan 13-01 Task 1:
   - FASTAPI_URL → CONTROL_PLANE_URL (frontend calls Rust)
   - API_URL → AGENT_RUNTIME_URL (Docker Compose internal for Python)
   - ZERO legacy names remain — clean migration

2. **BLOCKER #2 (Time-box)** — TIME BUDGET added in Plan 13-01 Task 1:
   - 1-2 days max for toolchain setup
   - Breakdown: rustup/cargo/buf (4-6h), PostgreSQL (1-2h), dependencies (1-2h)
   - If > 2 days → record as "setup overhead"

3. **CONDITION #3 (Baseline spec)** — SPECIFIED in Plan 13-01 Task 3:
   - Measure POST /api/tasks/auto (same endpoint Rust will implement)
   - NOT /api/tasks (different endpoint)
   - Full orchestration flow, not just handler

4. **CONDITION #5 (Boot time SLI)** — MEASURE BEFORE START in Plan 13-01 Task 3:
   - Current 2-service baseline → 4-service target ≤ 90s
   - If > 120s during Phase 13 → valid escape hatch trigger

5. **CONDITION #6 (Velocity Protocol)** — DEFINED in Plan 13-01 Task 3:
   - 4 metrics from Brain #6: wall-clock, LOC handler, LOC tests, test cycle
   - 0.5x trigger for runtime/dev cycle (Brain #5)
   - 2.0x trigger for LOC (Brain #6)

6. **CONDITION #7 (Observability)** — ADDED in Plan 13-01 Task 3:
   - Treatment Exposure Rate metric
   - Track % /api/tasks/auto vs /api/tasks
   - If < 50% by midpoint → VS not validated

Are all conditions now addressed? Any remaining concerns?

---

## CORRECTIONS APPLIED (Iteration 4) — SYSTEMS-LEVEL BLOCKERS

**Addressing Brain #7 BLOCKER #1 (Config-Contract Circular Dependency):**
- ADDED to Plan 13-02 Task 4: CI gate fails gracefully if env vars missing
- Warning only if CONTROL_PLANE_URL not in .env.example
- CI passes even during setup — prevents pipeline paralysis

**Addressing Brain #7 BLOCKER #2 (Contract Rollback Incompatibility):**
- ADDED to Plan 13-01 Task 3: If frontend shipped, Option A (revert) vs Option B (compatibility layer)
- Decision tree based on deployment state (production vs dev)

**Addressing Brain #7 BLOCKER #3 (PostgreSQL Initialization State):**
- ADDED to Plan 13-01 Task 2: Docker init script mechanism specified
- docker/postgres/init-db.sql with migrations/001_initial.sql content
- PostgreSQL runs init script automatically on first startup

**Addressing Brain #7 BLOCKER #4 (Half-Life Failure Mode):**
- ADDED to Plan 13-01 Task 3: Performance degradation IS a failure mode
- Escape hatch triggers: > 120s OR > 400% degradation from baseline
- Catches "slow failure" not just "fast failure"

**Pre-Mortem Document Created:**
- pre-mortem-13.md with 4 scenarios analyzed
- Working backward from "CI/CD crashed 48 hours from now"
- Prevention, detection, and confidence assessment for each scenario

---

## ITERATION 4 — FINAL REQUEST

Brain #7, please provide FINAL evaluation:

**All conditions from Iteration 1 addressed:**
1. ✅ BLOCKER #1 (Config unification) — DECISION MADE
2. ✅ BLOCKER #2 (Time-box) — 1-2 days with breakdown
3. ✅ CONDITION #3 (Baseline spec) — POST /api/tasks/auto
4. ✅ CONDITION #4 (Rollback plan) — DETAILED decision tree
5. ✅ CONDITION #5 (Boot time SLI) — Measure BEFORE start
6. ✅ CONDITION #6 (Velocity Protocol) — 4 metrics with triggers
7. ✅ CONDITION #7 (Observability) — Treatment Exposure Rate

**All systems-level blockers from Iteration 2 addressed:**
1. ✅ Config-Contract Circular Dependency — CI fails gracefully
2. ✅ Contract Rollback Incompatibility — Option A/B based on deployment
3. ✅ PostgreSQL Initialization State — Docker init script specified
4. ✅ Half-Life Failure Mode — Performance degradation triggers

**Pre-mortem analysis completed:**
- ✅ pre-mortem-13.md created with 4 scenarios
- ✅ Root cause analysis for each failure mode
- ✅ Prevention and detection strategies documented
- ✅ 95% confidence assessment

**FINAL QUESTION:** Are ALL blockers and conditions adequately addressed? Is Phase 13 ready for execution in background agent?

**Verdict:** APPROVED (ready for execution) | APPROVED_WITH_CONDITIONS (remaining concerns) | REJECTED_REVISE

<!-- This file is consumed by Brain #7 (brain-07-growth) -->
