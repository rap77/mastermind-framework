# BRAIN-FEED-06 — QA Domain Feed

> Written by Brain #6 (QA/DevOps). Read-only for other agents.
> Orchestrator reads this after all domain feeds to write BRAIN-FEED.md (global synthesis).
> Last updated: 2026-04-05

---

## Test Infrastructure

- `uv run pytest` must run from `apps/api/` — running from project root fails with pre-existing `ModuleNotFoundError` for `mastermind_cli`
- Vitest over Jest — ESM-native, better Next.js 16 integration
- `websocket-metrics.ts` with `WS_SLOS` — define guardrail metrics before implementing

---

## Baseline Anchors

- Adversarial baseline delta_velocity=4 signal: `@xyflow/react v12 nodeInternals` + `IntersectionObserver` was an unprompted Senior insight from Brain #4 — genuine delta_velocity=4 output not in the ticket. This is the stretch target for Phase 11 agent comparison.
- Current test suite state: 631 backend (apps/api/) + 407 frontend (apps/web/) — established 2026-04-05 baseline
- **631 NOT 620** — collected count is 631 as of 2026-04-05. Roadmap numbers are stale.

---

## Anti-patterns (QA)

- `uv run pytest` from project root → use `cd apps/api && uv run pytest` (pre-existing conftest discovery issue)

---

## 2026-03-31 — Phase 12 QA Evaluation: Autonomous Agent Restructuring

### Verified Insights

**Test Suite Count Correction (verified by collection):**
- Domain feed said 575 backend. Actual count as of 2026-03-31: `589 tests collected` (cd apps/api && uv run pytest --collect-only -q)
- Update the baseline anchor: **589 backend + 407 frontend**. The feed was stale by 14 tests from Phase 12 experience/schema tests already written.

**startup_event() gap — CONFIRMED:**
- `create_experience_schema()` exists in `database.py` (line 305) and is tested offline in `tests/e2e/test_experience_logging.py`
- It is NOT yet wired into `startup_event()` in `app.py` — this is the plan item to add
- There are ZERO existing tests for `startup_event()` behavior (grep confirmed: no `startup_event` matches in tests/)
- Gap: test_app_startup_creates_experience_table must be added before closing phase

**asyncio.create_task() vs BackgroundTasks — CONFIRMED risk:**
- `asyncio.create_task()` is currently only used in `cancellation.py` and `stateless_coordinator.py` — NOT in `tasks.py`
- `tasks.py` has explicit TODO: "Integrate with Coordinator.orchestrate() in Task 2"
- The plan proposes `asyncio.create_task()` inside a route handler — this creates orphan tasks
- Correct pattern for FastAPI: `BackgroundTasks` parameter injection — testable via `httpx.AsyncClient` + mock on the background function

**GET /api/experiences/{brain_id} — IDOR risk confirmed:**
- Existing `brains.py` correctly scopes by `user_id` (WHERE user_id = current_user.id)
- The proposed endpoint is brain-scoped, not user-scoped — this is an IDOR if brain_ids are predictable
- Test required: user_b cannot read user_a's experiences for same brain_id

**aiosqlite transaction isolation — CONFIRMED gap:**
- The existing `DatabaseConnection` context manager does NOT use explicit transactions (`async with db.begin()`)
- `tasks.py` does `await db.conn.commit()` manually after each mutation
- task_runner.py mid-flight crash scenario: partial write + no explicit transaction = corrupt state
- Test required: mock StatelessCoordinator to raise after first DB write, assert zero rows in experience_records

**brain_memory.py CLI in CI — pattern established:**
- Use `pytest` + `monkeypatch` to set `MM_DB_PATH` to `tmp_path / "test.db"` before import
- Do NOT test via subprocess for unit coverage — use direct function call with AsyncMock on ExperienceLogger
- Subprocess test is acceptable for exit_code contract only (CLI arg validation)

### Deferred Items

- Deferred: Embedding_stub column: NULL today, pgvector in v3.0. No test needed now beyond the existing NULL acceptance test.
- Deferred: WebSocket broadcast in task_runner.py: WS_SLOS guardrail metrics should be defined before Phase 13 if WS broadcast is added to task completion path.

---

## 2026-04-05 — Phase 13 Vertical Slice: Testing Strategy

### Verified Insights

**1. MINIMUM TESTING INFRASTRUCTURE — 5 layers, not 1**

The vertical slice needs these test layers, ordered by priority:

| Layer | What | Tool | Count Target | Offline? |
|-------|------|------|-------------|----------|
| Rust unit tests | Axum handlers, gRPC client logic, domain types | `cargo test` | 20-30 | Yes |
| Proto contract tests | Generated types match .proto, serialization round-trip | `cargo test` + `pytest` | 5-8 | Yes |
| gRPC integration tests | Rust tonic client -> Python grpclib server | Docker Compose + `pytest` | 3-5 | No (needs Docker) |
| PostgreSQL parity tests | Same DB operations against SQLite AND PostgreSQL | `pytest` (parametrized) | 10-15 | No (needs PostgreSQL) |
| End-to-end smoke test | Next.js -> Rust -> gRPC -> Python -> response | Docker Compose + shell script | 1-2 | No (needs all services) |

**Why this order:** Rust unit tests and proto contract tests provide the fastest feedback loop (< 30 seconds). gRPC integration tests validate the actual wire format. PostgreSQL parity tests catch migration issues. E2E smoke test is the final gate, not the first line of defense.

**2. POSTGRESQL MIGRATION STRATEGY — The Hard Problem**

Verified against codebase:
- `DatabaseConnection` in `/home/rpadron/proy/mastermind/apps/api/mastermind_cli/state/database.py` uses raw aiosqlite with `CREATE TABLE IF NOT EXISTS` DDL
- Zero ORM. Zero SQLAlchemy. Zero Alembic. All DDL is inline Python strings.
- `conftest.py` uses `:memory:` SQLite. API conftest uses `tmp_path` file-based SQLite.
- No `asyncpg`, no `psycopg`, no PostgreSQL drivers in `uv.lock` (verified)

This means the 631 tests do NOT need "migration." They need a **DatabaseConnection abstraction** that works with both backends. Here is the concrete strategy:

**Phase 13 Step 1: Abstract the database layer (BEFORE writing Rust)**
- Extract `DatabaseConnection` into a protocol/ABC with two implementations: `SQLiteConnection` and `PostgreSQLConnection`
- The `conftest.py` `async_db` fixture already uses `:memory:` — this stays as-is for unit tests
- Add a NEW `postgres_db` fixture that uses `testcontainers-postgres` or Docker Compose PostgreSQL
- Parametrize the integration tests: `@pytest.mark.parametrize("db_fixture", ["async_db", "postgres_db"])`

**Phase 13 Step 2: SQLite vs PostgreSQL divergence points (verified risks)**
These WILL break when running against PostgreSQL. I grepped the codebase and found:

- **Boolean handling:** SQLite treats `0`/`1` as boolean. PostgreSQL has native `BOOLEAN`. The `status TEXT` columns will work, but any implicit `WHERE status` (truthy check) will fail.
- **TIMESTAMP type:** SQLite `TIMESTAMP` is text. PostgreSQL `TIMESTAMP` is a native type. `created_at TIMESTAMP` in `create_task_schema()` works in both, but `CURRENT_TIMESTAMP` format differs (SQLite: ISO string, PostgreSQL: timestamp object).
- **AUTOINCREMENT:** SQLite uses `INTEGER PRIMARY KEY`. PostgreSQL uses `SERIAL`/`GENERATED ALWAYS AS IDENTITY`. Current schema uses `TEXT PRIMARY KEY` with UUID — this is fine.
- **JSON storage:** SQLite stores JSON as TEXT. PostgreSQL has native `JSONB`. The `progress TEXT` and `result TEXT` columns work as-is but lose PostgreSQL indexing benefits. Migration to `JSONB` is a Phase 15 concern.
- **CONCAT and string functions:** SQLite `||` vs PostgreSQL `CONCAT()`. Grep shows no raw SQL string concatenation — safe.

**Phase 13 Step 3: Docker Compose PostgreSQL in CI**
Add a PostgreSQL service to `.github/workflows/ci.yml`:
```yaml
services:
  postgres:
    image: postgres:16
    env:
      POSTGRES_DB: mastermind_test
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
    ports:
      - 5432:5432
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
```
Run parity tests as a separate CI job that only executes on pull requests touching `apps/api/mastermind_cli/state/`.

**3. PROTO SYNC CI GATE — Design**

Verified: `buf` and `protoc` are NOT installed. Zero `.proto` files exist. This is greenfield.

The gate needs 3 components:

**Component A: buf.yaml in proto/ directory**
```
version: v2
lint:
  use:
    - DEFAULT
breaking:
  use:
    - FILE
```

**Component B: Proto Sync CI job in `.github/workflows/ci.yml`**
```yaml
proto-sync:
  name: Proto Sync Gate
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: bufbuild/buf-setup-action@v1
    - run: buf lint proto/
    - run: buf generate proto/ --template buf.gen.yaml
    - name: Check generated code matches committed
      run: git diff --exit-code apps/api/proto/ apps/rust/src/proto/ apps/web/src/proto/
```

This runs on EVERY pull request. If anyone edits `.proto` without regenerating types, the build fails. If someone edits generated code directly, the build fails.

**Component C: Makefile target for local development**
```makefile
proto-gen:
    buf generate proto/ --template buf.gen.yaml
    @echo "Generated Rust, Python, and TypeScript types from .proto"
```

**When it runs:** Every PR. No exceptions. This is a hard gate, not a warning.

**What it checks:** (1) `.proto` files are valid (`buf lint`), (2) Generated code matches committed code (`git diff --exit-code`), (3) No breaking changes against main branch (`buf breaking` -- optional for Phase 13, mandatory for Phase 15+).

**4. DUAL-WRITE TEST STRATEGY — Phased Verification**

The dual-write period (SQLite + PostgreSQL simultaneously) needs 3 test types:

**Test Type A: Write Fidelity Test (offline, fast)**
- Write one row to SQLite. Write one row to PostgreSQL. Read from both. Assert identical data.
- This tests the abstraction layer, not the network.
- Run with `cargo test` (Rust) and `pytest` (Python) in unit test suite.
- Count: 5-8 tests.

**Test Type B: Schema Parity Test (needs PostgreSQL, medium)**
- Run `create_task_schema()`, `create_auth_schema()`, `create_api_keys_v2_schema()`, `create_execution_history_schema()`, `create_experience_schema()` against both backends.
- For each schema, INSERT a representative row, SELECT it back, and compare.
- This catches type coercion differences (SQLite `TEXT` vs PostgreSQL `VARCHAR`, `TIMESTAMP` behavior).
- Count: 10-15 tests (one per table, parametrized).

**Test Type C: Consistency Gate (needs PostgreSQL + load, slow)**
- Run 100 concurrent writes to both backends via dual-write path.
- Read all rows from both backends. Assert row count matches AND every row is identical.
- This catches: write ordering differences, transaction isolation issues, partial failures.
- Count: 2-3 tests. Run in CI only, not pre-push.

**5. RUST VELOCITY MEASUREMENT PROTOCOL — Concrete, Not Abstract**

The ROADMAP says "if Rust velocity < 0.5x Python, escape hatch activates." Here is how to measure that:

**Metric 1: Time-to-compilation (cold start)**
- Measure: `time cargo build --release` for the Rust service.
- Python baseline: `time uv run uvicorn mastermind_cli.api.app:get_app --factory` (cold import).
- Compare: if Rust cold build > 2x Python cold start, this impacts development velocity.

**Metric 2: Time-to-running-test (hot loop)**
- Measure: `time cargo test` after changing one handler function.
- Python baseline: `time uv run pytest tests/unit/test_brain_router.py` after changing one function.
- This is the metric that matters for developer experience. Rust must be < 0.5x slower on iterative test cycles.

**Metric 3: Feature velocity (lines of code per feature)**
- Implement the same feature (e.g., `POST /api/tasks/create` handler) in Rust and Python.
- Measure: total LOC, time to write, time to get passing tests.
- If Rust takes > 2x the LOC AND > 2x the time, the escape hatch triggers.

**When to measure:** At Phase 13 midpoint (after VS-01 is implemented). Not at the end — by then it is too late.

**Who measures:** The developer implementing VS-01. Record in `.planning/phases/13/velocity-measurements.md`.

**What counts as "0.5x Python":** Rust takes MORE than 2x the wall-clock time to implement the same feature with equivalent test coverage. If Rust is 1.5x slower but produces better performance, that is acceptable. If Rust is 3x slower AND the compiled binary is only marginally faster, that is the escape hatch trigger.

### Corrections to Roadmap/Planning Assumptions

- **CORRECTION:** ROADMAP says "620 existing tests passing". Actual count is **631** as of 2026-04-05. Any planning document referencing 620 is stale.
- **CORRECTION:** ROADMAP says "Alembic migration". There is ZERO SQLAlchemy in this project. All DDL is raw SQL strings in `DatabaseConnection`. The migration strategy must be "abstract the connection layer," not "add Alembic."
- **CORRECTION:** STATE.md says "PostgreSQL 16 + pgvector is running in development with all 620 existing tests passing." This is aspirational, not implemented. Zero PostgreSQL drivers exist. Zero `.proto` files exist. Zero Rust code exists.

### Pre-Requisites for Phase 13 (Must Exist Before Writing Rust)

1. `buf` CLI installed (`brew install buf` or `npm install -g @bufbuild/buf`)
2. `protoc` installed (comes with `buf` or via `brew install protobuf`)
3. PostgreSQL 16 running locally (Docker Compose or native)
4. `asyncpg` added to `apps/api/pyproject.toml` dependencies
5. `testcontainers-postgres` added to `apps/api/pyproject.toml` dev dependencies
6. `proto/` directory created at project root with first `.proto` file
7. `buf.yaml` and `buf.gen.yaml` configured for Rust (tonic+prost), Python (grpclib), TypeScript (ts-proto)

### Deferred Items

- Deferred: `buf breaking` against main branch — add in Phase 15 when multiple `.proto` files exist. Phase 13 has one proto file, so breaking change detection is overkill.
- Deferred: pgvector testing — no vector operations in Phase 13. The `embedding_stub BLOB` column stays as-is.
- Deferred: Rust integration with CI — add `cargo test` job after VS-01 handler exists. No point adding CI for zero tests.
- Deferred: ts-proto TypeScript codegen testing — Phase 13 focuses on Rust/Python. TypeScript types from `.proto` are generated but not consumed until Phase 16+.

### CI Pipeline Changes Required

**File: `.github/workflows/ci.yml`**

Current pipeline: 4 jobs (typecheck, tests, semantic, e2e). Phase 13 adds:

| New Job | Depends On | Runs On | Timeout |
|---------|-----------|---------|---------|
| `proto-sync` | Nothing | Every PR | 3 min |
| `rust-tests` | `proto-sync` | Every PR | 5 min |
| `postgres-parity` | Nothing | PRs touching `state/` | 10 min |

**Modified existing jobs:**
- `level2-tests`: Add `postgres_db` fixture support behind `--run-postgres` flag. Default off for speed.
- `level4-e2e`: Add Rust service to Docker Compose. Add gRPC health check before tests.

### Offline Guarantee

- Rust unit tests: `cargo test` — fully offline. No network, no Docker, no PostgreSQL.
- Proto contract tests: `cargo test` + `pytest` — offline. Tests generated types, not network calls.
- gRPC integration tests: REQUIRE Docker Compose (Rust + Python services). NOT offline. Mark with `@pytest.mark.integration`.
- PostgreSQL parity tests: REQUIRE PostgreSQL. NOT offline. Mark with `@pytest.mark.postgres`.
- E2E smoke test: REQUIRE full Docker Compose stack. NOT offline. Mark with `@pytest.mark.e2e`.

**Pre-push hook (`.pre-commit-config.yaml`) additions for Phase 13:**
```yaml
# Rust unit tests (pre-push only, like Python)
- repo: local
  hooks:
    - id: cargo-test
      name: Rust Unit Tests
      entry: bash -c 'cd apps/rust && cargo test'
      language: system
      pass_filenames: false
      stages: [pre-push]

# Proto sync check (pre-push only)
- repo: local
  hooks:
    - id: proto-sync
      name: Proto Sync Check
      entry: bash -c 'buf generate proto/ --template buf.gen.yaml && git diff --exit-code'
      language: system
      pass_filenames: false
      stages: [pre-push]
```

### Regression Impact on Baseline

- **631 backend tests:** ZERO impact. All existing tests continue to use `:memory:` SQLite via `async_db` fixture. New PostgreSQL tests are SEPARATE fixtures and SEPARATE CI jobs.
- **407 frontend tests:** ZERO impact. Phase 13 adds no frontend test changes.
- **New Rust tests:** Additive only. 20-30 new tests in `apps/rust/`. Does not touch existing counts.
- **New PostgreSQL parity tests:** Additive. 10-15 new tests in `apps/api/tests/postgres/`. Does not modify existing test files.
- **Total after Phase 13:** ~668-676 backend + 407 frontend + ~25 Rust = ~1,100-1,108 total.


---

## 2026-04-06 — Phase 14 QA Strategy: Knowledge Distillation Testing

### Verified Insights

**1. LEARNING LOOP VALIDATION (KD-01) — Characterization Testing Pattern**

**Problem:** How do we TEST that Brain #7 evaluation actually improves outputs without live MCP calls?

**Solution:** Shadow Loop A/B Test with Static Mock Fixtures

**Test Implementation:**
```
File: apps/api/tests/kd/test_loop.py (NEW)
Layer: Integration (requires ExperienceLogger + mocked Brain #7)
Count: 5-8 tests
Offline: YES (mocked Brain #7 responses)
```

**Test Pattern:**
- **Path A (Cold):** Run brain consultation WITHOUT memory access. Measure T1_cold.
- **Path B (Warm):** Run same consultation WITH memory from ExperienceLogger. Measure T1_warm.
- **Assertion:** `delta_velocity = T1_cold - T1_warm` must show trend toward sub-90s target.
- **Profitability Gate:** If T1_warm > 300s, test FAILS (agent-unprofitable constraint).

**Mock Strategy:**
- Adapt `MockMCPClient` pattern from `test_stateless_coordinator.py` (lines 37-81)
- Generate "optimized" Brain #7 responses using SHA256 hashing of query content
- Store mock evaluations as JSON fixtures in `apps/api/tests/fixtures/brain7_evaluations/`
- No live NotebookLM calls — fully offline

**Benchmark Tool:**
- `pytest-benchmark` already in project (>=4.0.0 in pyproject.toml)
- Use `time.perf_counter()` pattern from `test_parallel_execution.py` (lines 134-148)
- Benchmark decorator: `@pytest.mark.benchmark(group="kd-01-learning-loop")`

**Test Coverage Map:**
1. `test_cold_start_baseline()` — Measure T1 without memory (baseline)
2. `test_warm_start_improvement()` — Measure T1 with memory (improvement)
3. `test_delta_velocity_calculation()` — Verify delta formula correct
4. `test_profitability_threshold()` — FAIL if T1 > 300s
5. `test_concurrent_learning()` — Parallel sessions don't corrupt memory
6. `test_brain7_evaluation_quality()` — Mock evaluation detects real improvements

**Regression Impact:**
- **631 backend tests:** ZERO impact — new test directory, isolated fixtures
- **Additive only:** ~5-8 new tests, doesn't modify existing test files

---

**2. TEMPLATE QUALITY GATE (KD-02) — Contract-First Validation**

**Problem:** How do we ensure auto-generated templates from successful interactions are actually useful?

**Solution:** Template Instantiation Test + Human Review Gate

**Test Implementation:**
```
File: apps/api/tests/kd/test_synthesis.py (NEW)
Layer: Integration (requires Template Synthesizer + ExperienceLogger)
Count: 6-10 tests
Offline: YES
```

**Test Pattern:**
- **Step 1:** Process successful interaction log → generate template (Python/JSON)
- **Step 2:** Instantiate template (load module, parse JSON schema)
- **Step 3:** Run template against existing 631 backend tests
- **Step 4:** If ANY test fails → template REJECTED → marked `pending_review`

**Quality Gates:**
1. **Schema Validation:** Template must match expected structure (fields, types)
2. **Instantiation Test:** Template must load without errors
3. **Regression Test:** Template must not break existing test suite
4. **Human Review (Optional):** CLI flag `--review-required` moves failed templates to `pending/` for manual verification

**Test Coverage Map:**
1. `test_template_schema_validation()` — Verify structure correctness
2. `test_template_instantiation()` — Load template without errors
3. `test_template_regression_test()` — Run against 631 backend tests
4. `test_failed_template_marked_pending()` — Rejected templates go to pending/
5. `test_successful_template_deployed()` — Approved templates become active
6. `test_template_versioning()` — Templates stored in ExperienceLogger with version
7. `test_template_revert()` — Rollback to previous version if new one fails

**Human-in-the-Loop Pattern:**
```bash
# CLI command (future implementation)
python3 -m mastermind_cli.tools.template_synthesizer --review-required
# → Generates templates, runs tests, moves failures to pending/
# → Human reviews pending/ and approves via:
python3 -m mastermind_cli.tools.template_synthesizer --approve template_id
```

**Regression Impact:**
- **631 backend tests:** USED AS VALIDATION — template must pass all existing tests
- **Additive only:** ~6-10 new tests in `tests/kd/`

---

**3. DASHBOARD TESTING (KD-03) — Synthetic Event Replay**

**Problem:** What's the test strategy for the analytics dashboard showing patterns, insights, correlations, delta-velocity trends?

**Solution:** Synthetic Event Replay + Frontend Component Tests

**Test Implementation:**
```
Backend: apps/api/tests/kd/test_analytics.py (NEW)
Frontend: apps/web/tests/dashboard/analytics.spec.ts (NEW)
Layers: Integration (backend) + Component (frontend)
Count: 8-12 backend + 5-8 frontend
Offline: YES (synthetic data)
```

**Backend Test Pattern:**
- Generate synthetic `experience_records` with known patterns:
  - T1 times: 270s → 210s → 150s → 85s (improvement curve)
  - Success rates: 60% → 75% → 90% (learning curve)
  - Brain correlations: brain-01 + brain-04 = 2x better outcomes
- Query analytics endpoints (`GET /api/analytics/delta-velocity`, etc.)
- Assert calculated metrics match synthetic data

**Frontend Test Pattern:**
- Use existing 407 frontend test patterns (Vitest + React Testing Library)
- Mock analytics API responses with synthetic data
- Test components render charts, trend lines, correlation matrices correctly
- Verify responsive layout (mobile vs desktop)

**Test Coverage Map:**

**Backend (test_analytics.py):**
1. `test_delta_velocity_trend_calculation()` — Verify trend line from synthetic data
2. `test_success_rate_improvement()` — Verify learning curve detection
3. `test_brain_correlation_analysis()` — Verify brain-brain correlations
4. `test_pattern_extraction()` — Verify recurring pattern detection
5. `test_analytics_cache_performance()` — Ensure queries < 100ms (p95)
6. `test_high_cardinality_events()` — Handle 10k+ synthetic records
7. `test_time_window_filtering()` — Verify date range filters work
8. `test_aggregation_accuracy()` — Verify sum/avg/min/max correct

**Frontend (analytics.spec.ts):**
1. `test_delta_velocity_chart_renders()` — Trend line displays correctly
2. `test_correlation_matrix_display()` — Brain-brain correlations visible
3. `test_pattern_cards_show_insights()` — Recurring patterns highlighted
4. `test_mobile_responsive_layout()` — Charts stack on mobile
5. `test_loading_state()` — Skeleton screens while data loads
6. `test_error_state()` — Graceful fallback if API fails
7. `test_real_time_updates()` — WebSocket updates refresh charts (if implemented)

**Dashboard Smoke Test Enhancement:**
- Extend existing `test_dashboard_smoke.py` (Playwright E2E)
- Add synthetic data seeding before navigation
- Verify analytics panels render correctly

**Regression Impact:**
- **631 backend tests:** ZERO impact — synthetic data in separate test DB
- **407 frontend tests:** ZERO impact — new test file `analytics.spec.ts`
- **Additive only:** ~8-12 backend + ~5-8 frontend tests

---

### Corrections to Planning Assumptions

**CORRECTION:** "Need to define delta-velocity" → FALSE — Already defined in BRAIN-FEED-01 + BRAIN-FEED-07. T1 baseline: 210-270s. Target: sub-90s. Profitability: T1 > 300s = FAIL. Implementation required, not definition.

**CORRECTION:** "Dashboard requires real session data" → FALSE — Use synthetic event replay for testing. Real sessions in production, tests use pre-generated fixtures. Offline guarantee maintained.

**CORRECTION:** "Template quality requires human review for all" → FALSE — Automated regression test gate (must pass 631 backend tests). Human review ONLY for failed templates in `pending/`. Most templates auto-deploy if tests pass.

**CORRECTION:** "Learning loop requires live Brain #7" → FALSE — Mock Brain #7 evaluations using SHA256 hash pattern from `test_stateless_coordinator.py`. Static fixtures in `tests/fixtures/brain7_evaluations/`. Fully offline.

---

### Pre-Requisites for Phase 14 Testing

1. **pytest-benchmark** — Already installed (>=4.0.0 in pyproject.toml line 126)
2. **MockMCPClient pattern** — Already exists in `test_stateless_coordinator.py` (lines 37-81)
3. **time.perf_counter() pattern** — Already exists in `test_parallel_execution.py` (lines 134-148)
4. **New test directories:**
   - `apps/api/tests/kd/` (KD-01, KD-02, KD-03 backend tests)
   - `apps/api/tests/fixtures/brain7_evaluations/` (mock Brain #7 responses)
   - `apps/web/tests/dashboard/` (KD-03 frontend tests)
5. **Synthetic data fixtures:**
   - `apps/api/tests/fixtures/synthetic_experience_records.json` (10k rows with known patterns)

---

### CI Pipeline Changes Required

**File: `.github/workflows/ci.yml`**

Add new test job for KD tests:

```yaml
kd-tests:
  name: Knowledge Distillation Tests
  runs-on: ubuntu-latest
  timeout-minutes: 15
  steps:
    - uses: actions/checkout@v4
    - name: Install uv
      run: curl -LsSf https://astral.sh/uv/install.sh | sh
    - name: Install Python dependencies
      run: cd apps/api && uv sync
    - name: Run KD-01 learning loop tests
      run: cd apps/api && uv run pytest tests/kd/test_loop.py -v
    - name: Run KD-02 template synthesis tests
      run: cd apps/api && uv run pytest tests/kd/test_synthesis.py -v
    - name: Run KD-03 analytics backend tests
      run: cd apps/api && uv run pytest tests/kd/test_analytics.py -v
    - name: Run KD-03 dashboard frontend tests
      run: pnpm --prefix apps/web test run dashboard/analytics.spec.ts
```

**Pre-commit hook additions (`.pre-commit-config.yaml`):**
```yaml
# KD template synthesis tests (pre-commit)
- repo: local
  hooks:
    - id: kd-template-tests
      name: KD Template Quality Tests
      entry: bash -c 'cd apps/api && uv run pytest tests/kd/test_synthesis.py -v'
      language: system
      pass_filenames: false
      stages: [pre-commit]

# KD analytics tests (pre-push, slower)
- repo: local
  hooks:
    - id: kd-analytics-tests
      name: KD Analytics Tests
      entry: bash -c 'cd apps/api && uv run pytest tests/kd/test_analytics.py -v'
      language: system
      pass_filenames: false
      stages: [pre-push]
```

---

### Offline Guarantee

**KD-01 (Learning Loop):**
- Mock Brain #7 evaluations (SHA256 hash pattern)
- Static fixtures in `tests/fixtures/brain7_evaluations/`
- No MCP calls — fully offline

**KD-02 (Template Synthesis):**
- Template generation from existing experience_records (in-memory SQLite)
- Instantiation tests run offline
- Regression tests use existing 631 backend tests (all offline)

**KD-03 (Dashboard Analytics):**
- Synthetic data fixtures (pre-generated JSON)
- Backend queries test in-memory SQLite
- Frontend tests mock API responses — fully offline

**All KD tests:** `@pytest.mark.kd` marker — can run with `pytest -m kd` for isolated testing.

---

### Success Criteria

**KD-01 Success:**
1. Delta-velocity calculation test passes (formula verified)
2. Cold start T1 measured and stored as baseline
3. Warm start T1 shows improvement trend (not regression)
4. Profitability gate enforced (T1 > 300s = FAIL)
5. All 5-8 tests pass offline in < 60 seconds

**KD-02 Success:**
1. Template schema validation catches malformed templates
2. Instantiation test rejects templates that fail to load
3. Regression test blocks templates that break 631 backend tests
4. Failed templates marked `pending_review` correctly
5. Approved templates deploy without manual intervention
6. All 6-10 tests pass offline in < 90 seconds

**KD-03 Success:**
1. Analytics backend calculates correct metrics from synthetic data
2. Delta-velocity trend line matches expected curve (270s → 85s)
3. Correlation analysis detects brain-brain relationships
4. Frontend components render charts accurately from mocked data
5. Dashboard smoke test (Playwright) passes end-to-end
6. All 8-12 backend + 5-8 frontend tests pass offline in < 120 seconds

**Overall Phase 14 Testing Success:**
- **Test count:** ~631 + ~407 + ~19-30 KD = ~1,057-1,068 total
- **Baseline maintenance:** ZERO regressions in existing tests
- **Offline guarantee:** 100% of KD tests pass without network/MCP
- **Coverage:** All 3 KD requirements (KD-01, KD-02, KD-03) validated
- **CI/CD:** New `kd-tests` job passes on every PR
- **Pre-commit:** Template synthesis tests run before push
- **Profitability enforced:** T1 > 300s fails automatically via tests

---

### Deferred Items

- **Deferred:** Live A/B testing with real users — KD-01 establishes test framework, real user testing is Phase 15+ (after v3.0 production deployment)
- **Deferred:** ML-based pattern extraction — KD-02 uses clustering/statistical patterns, not neural networks (out of scope per REQUIREMENTS.md)
- **Deferred:** Real-time dashboard WebSocket updates — KD-03 tests polling-based updates first, WebSocket optimization is Phase 16 (RTU-01)
- **Deferred:** Multi-tenant analytics isolation — KD-03 tests single-tenant patterns, per-company isolation is Phase 17+ (TMP-02)


---

## 2026-04-06 — Phase 14 BLOCKER Verification Tests

### BLOCKER Condition 1: Quality Score Calculation (Hormozi Equation)

**Required Test File:** `apps/api/tests/kd/test_scoring.py` (NEW)
**Layer:** Unit (pure function, no database)
**Offline:** YES (deterministic calculation)
**Count:** 4 tests

**Test Implementation:**

```python
# apps/api/tests/kd/test_scoring.py
"""Tests for Hormozi value equation quality score calculation."""

import pytest
from mastermind_cli.experience.scoring import calculate_quality_score, has_structure, can_invert


class TestQualityScoreFormula:
    """Verify Hormozi equation: (Precision × Success_Probability) / (T1 × Tokens)"""

    def test_high_quality_output(self):
        """High precision + high success + low cost = template candidate (>= 3.0)."""
        score = calculate_quality_score(
            precision=0.95,      # 95% actionable
            success_probability=0.90,
            t1_ms=85000,         # 85 seconds (good)
            tokens=1200,         # Concise output
            output_text="Structured response with clear sections"
        )
        assert score >= 3.0, f"Score {score} below template threshold"

    def test_medium_quality_output(self):
        """Medium precision + medium success = experience record (1.0 - 3.0)."""
        score = calculate_quality_score(
            precision=0.70,      # 70% actionable
            success_probability=0.60,
            t1_ms=180000,        # 3 minutes
            tokens=2500,
            output_text="Some structure but verbose"
        )
        assert 1.0 <= score < 3.0, f"Score {score} outside experience range"

    def test_low_quality_output_discarded(self):
        """Low precision or high cost = discard (< 1.0)."""
        score = calculate_quality_score(
            precision=0.30,      # 30% actionable (fluff)
            success_probability=0.20,
            t1_ms=400000,        # 6.7 minutes (slow)
            tokens=5000,         # Very long
            output_text="Lorem ipsum dolor sit amet" * 100
        )
        assert score < 1.0, f"Score {score} should be discarded"

    def test_twaddle_penalty(self):
        """Output > 2000 words without structure gets 50% penalty."""
        base_score = calculate_quality_score(
            precision=0.80,
            success_probability=0.70,
            t1_ms=120000,
            tokens=3000,
            output_text="Word " * 2500  # > 2000 words, no structure
        )

        # Same input with structure should be 2x higher
        structured_score = calculate_quality_score(
            precision=0.80,
            success_probability=0.70,
            t1_ms=120000,
            tokens=3000,
            output_text="## Section 1\nContent\n## Section 2\nContent"
        )

        assert base_score < structured_score, "Twaddle penalty not applied"
        assert base_score * 2 >= structured_score * 0.9, "Penalty should be ~50%"

    def test_inversion_check_penalty(self):
        """Cannot state "what to avoid" gets 30% penalty."""
        # Output that doesn't mention what to avoid
        no_inversion_score = calculate_quality_score(
            precision=0.75,
            success_probability=0.65,
            t1_ms=100000,
            tokens=1500,
            output_text="Do this. Then do that. Finally this."
        )

        # Output with inversion (what to avoid)
        with_inversion_score = calculate_quality_score(
            precision=0.75,
            success_probability=0.65,
            t1_ms=100000,
            tokens=1500,
            output_text="Do this. Avoid that common pitfall. Then this."
        )

        assert no_inversion_score < with_inversion_score, "Inversion check penalty not applied"
        assert no_inversion_score * 1.3 >= with_inversion_score * 0.9, "Penalty should be ~30%"

    def test_formula_division_by_zero_protection(self):
        """T1 or tokens = 0 should not crash (return minimal score)."""
        score = calculate_quality_score(
            precision=1.0,
            success_probability=1.0,
            t1_ms=0,  # Edge case
            tokens=0,
            output_text="Test"
        )
        assert score == 0.0, "Zero division should return 0.0"


class TestStructureDetection:
    """Helper function tests for twaddle penalty."""

    def test_has_structure_detects_markdown_headers(self):
        assert has_structure("## Header\nContent") is True

    def test_has_structure_detects_numbered_lists(self):
        assert has_structure("1. First\n2. Second") is True

    def test_has_structure_rejects_wall_of_text(self):
        assert has_structure("word " * 100) is False


class TestInversionDetection:
    """Helper function tests for inversion check."""

    def test_can_invert_detects_avoid_keywords(self):
        assert can_invert("Avoid this. Don't do that.") is True

    def test_can_invert_detects_pitfalls_section(self):
        assert can_invert("## Pitfalls\nCommon mistake") is True

    def test_can_invert_rejects_purely_prescriptive(self):
        assert can_invert("Do this. Then that.") is False
```

**Fixture Data (tests/fixtures/quality_scores.json):**
```json
{
  "high_quality": {
    "precision": 0.95,
    "success_probability": 0.90,
    "t1_ms": 85000,
    "tokens": 1200,
    "output": "## Strategy\n1. Action A\n2. Action B\n## Pitfalls\nAvoid X",
    "expected_score_min": 3.0
  },
  "medium_quality": {
    "precision": 0.70,
    "success_probability": 0.60,
    "t1_ms": 180000,
    "tokens": 2500,
    "output": "Some good content but verbose",
    "expected_score_min": 1.0,
    "expected_score_max": 3.0
  },
  "low_quality": {
    "precision": 0.30,
    "success_probability": 0.20,
    "t1_ms": 400000,
    "tokens": 5000,
    "output": "Fluff content with no structure",
    "expected_score_max": 1.0
  }
}
```

**Run Command:**
```bash
cd apps/api && uv run pytest tests/kd/test_scoring.py -v
```

**Coverage Verification:**
- Formula correctness: Test with known inputs verify output matches hand-calculated value
- Penalty application: Twaddle and inversion penalties reduce score by expected percentage
- Edge cases: Zero division, negative inputs handled gracefully

---

### BLOCKER Condition 2: Rejection Logging + Filter

**Required Test File:** `apps/api/tests/kd/test_rejection_filter.py` (NEW)
**Layer:** Integration (requires ExperienceLogger with real SQLite)
**Offline:** YES (in-memory database)
**Count:** 5 tests

**Test Implementation:**

```python
# apps/api/tests/kd/test_rejection_filter.py
"""Tests that rejected outputs are logged but NOT retrieved."""

import pytest
from mastermind_cli.experience.logger import ExperienceLogger
from mastermind_cli.state.database import DatabaseConnection


@pytest.mark.asyncio
class TestRejectionLogging:
    """Verify rejected outputs are stored with status='rejected'."""

    async def test_log_rejected_execution(self, async_db):
        """Rejected execution stores quality_score=0 and status='rejected'."""
        logger = ExperienceLogger(async_db)

        record_id = await logger.log_execution(
            brain_id="brain-01",
            input_json={"query": "test"},
            output_json={"error": "Low quality output"},
            duration_ms=5000,
            status="rejected",
            custom_metadata={"quality_score": 0.0}
        )

        # Verify record exists
        record = await logger.get_by_id(record_id)
        assert record.status == "rejected"
        assert record.custom_metadata["quality_score"] == 0.0

    async def test_log_approved_execution(self, async_db):
        """Approved execution stores quality_score >= 1.0."""
        logger = ExperienceLogger(async_db)

        record_id = await logger.log_execution(
            brain_id="brain-01",
            input_json={"query": "test"},
            output_json={"result": "Good output"},
            duration_ms=3000,
            status="success",
            custom_metadata={"quality_score": 3.5}
        )

        record = await logger.get_by_id(record_id)
        assert record.status == "success"
        assert record.custom_metadata["quality_score"] >= 1.0


@pytest.mark.asyncio
class TestRejectionFilter:
    """Verify get_recent_by_brain() filters out rejected records."""

    async def test_rejected_records_not_retrieved(self, async_db):
        """Mix of approved + rejected records → only approved returned."""
        logger = ExperienceLogger(async_db)

        # Seed database with mix
        await logger.log_execution(
            brain_id="brain-01",
            input_json={"q": "1"},
            output_json={"result": "approved"},
            duration_ms=1000,
            status="success",
            custom_metadata={"quality_score": 3.0}
        )

        await logger.log_execution(
            brain_id="brain-01",
            input_json={"q": "2"},
            output_json={"error": "rejected"},
            duration_ms=1000,
            status="rejected",
            custom_metadata={"quality_score": 0.0}
        )

        await logger.log_execution(
            brain_id="brain-01",
            input_json={"q": "3"},
            output_json={"result": "approved2"},
            duration_ms=1000,
            status="success",
            custom_metadata={"quality_score": 2.5}
        )

        # Query recent records
        records = await logger.get_recent_by_brain("brain-01", limit=10)

        # ASSERT: Only 2 approved records returned
        assert len(records) == 2, f"Expected 2 records, got {len(records)}"
        assert all(r.status != "rejected" for r in records), "Rejected record leaked"
        assert all(r.custom_metadata.get("quality_score", 0) >= 1.0 for r in records), "Low score leaked"

    async def test_quality_score_threshold_filter(self, async_db):
        """Records with quality_score < 1.0 not retrieved."""
        logger = ExperienceLogger(async_db)

        # Seed with varying quality scores
        for score in [0.5, 0.9, 1.0, 1.5, 2.0, 3.0]:
            await logger.log_execution(
                brain_id="brain-07",
                input_json={"q": f"score_{score}"},
                output_json={"result": "test"},
                duration_ms=1000,
                status="success",
                custom_metadata={"quality_score": score}
            )

        records = await logger.get_recent_by_brain("brain-07", limit=10)

        # ASSERT: Only scores >= 1.0 returned
        assert len(records) == 4, f"Expected 4 records, got {len(records)}"
        assert all(r.custom_metadata["quality_score"] >= 1.0 for r in records)

    async def test_combined_filters(self, async_db):
        """Both status='rejected' AND quality_score < 1.0 filtered together."""
        logger = ExperienceLogger(async_db)

        # Rejected with score 0
        await logger.log_execution(
            brain_id="brain-05",
            input_json={"q": "rejected"},
            output_json={"error": "bad"},
            duration_ms=1000,
            status="rejected",
            custom_metadata={"quality_score": 0.0}
        )

        # Success with score 0.5 (edge case)
        await logger.log_execution(
            brain_id="brain-05",
            input_json={"q": "low_score"},
            output_json={"result": "weak"},
            duration_ms=1000,
            status="success",
            custom_metadata={"quality_score": 0.5}
        )

        # Success with score 2.0 (should return)
        await logger.log_execution(
            brain_id="brain-05",
            input_json={"q": "good"},
            output_json={"result": "good"},
            duration_ms=1000,
            status="success",
            custom_metadata={"quality_score": 2.0}
        )

        records = await logger.get_recent_by_brain("brain-05", limit=10)

        # ASSERT: Only the 2.0 score record returns
        assert len(records) == 1
        assert records[0].custom_metadata["quality_score"] == 2.0

    async def test_filter_performance_with_many_rejected(self, async_db):
        """1000 rejected + 100 approved → retrieval still fast (< 50ms)."""
        import time
        logger = ExperienceLogger(async_db)

        # Seed 1000 rejected
        for i in range(1000):
            await logger.log_execution(
                brain_id="brain-01",
                input_json={"q": f"rejected_{i}"},
                output_json={"error": "bad"},
                duration_ms=1000,
                status="rejected",
                custom_metadata={"quality_score": 0.0}
            )

        # Seed 100 approved
        for i in range(100):
            await logger.log_execution(
                brain_id="brain-01",
                input_json={"q": f"approved_{i}"},
                output_json={"result": "good"},
                duration_ms=1000,
                status="success",
                custom_metadata={"quality_score": 2.0 + (i % 10) * 0.1}
            )

        # Measure retrieval time
        start = time.perf_counter()
        records = await logger.get_recent_by_brain("brain-01", limit=100)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # ASSERT: Only approved records returned AND fast
        assert len(records) == 100
        assert elapsed_ms < 50, f"Retrieval took {elapsed_ms}ms, too slow"
```

**Schema Change Required:**
```sql
-- Migration to add quality_score to experience_records
ALTER TABLE experience_records ADD COLUMN quality_score REAL DEFAULT 0.0;
```

**Implementation Requirement (logger.py:129-149):**
```python
# MODIFIED: get_recent_by_brain() MUST filter
async def get_recent_by_brain(
    self, brain_id: str, limit: int = 100
) -> List[ExperienceRecord]:
    cursor = await self.db.conn.execute(
        """SELECT * FROM experience_records
           WHERE brain_id = ?
             AND json_extract(custom_metadata, '$.quality_score') >= 1.0
             AND status != 'rejected'
           ORDER BY timestamp DESC
           LIMIT ?""",
        (brain_id, limit),
    )
    rows = await cursor.fetchall()
    return [self._row_to_record(row) for row in rows]
```

**Run Command:**
```bash
cd apps/api && uv run pytest tests/kd/test_rejection_filter.py -v
```

---

### BLOCKER Condition 3: Relevance Ceiling (TTL)

**Required Test File:** `apps/api/tests/kd/test_ttl.py` (NEW)
**Layer:** Integration (requires ExperienceLogger with expires_at column)
**Offline:** YES (in-memory database)
**Count:** 4 tests

**Schema Change Required:**
```sql
-- Migration to add expires_at
ALTER TABLE experience_records ADD COLUMN expires_at TEXT;

-- Index for TTL queries
CREATE INDEX idx_expires_at ON experience_records(expires_at);
```

**Test Implementation:**

```python
# apps/api/tests/kd/test_ttl.py
"""Tests that expired records are NOT retrieved."""

import pytest
from datetime import datetime, timedelta
from mastermind_cli.experience.logger import ExperienceLogger


@pytest.mark.asyncio
class TestRelevanceCeiling:
    """Verify TTL filtering prevents unbounded growth."""

    async def test_expired_record_not_retrieved(self, async_db):
        """Record with expires_at in past excluded from results."""
        logger = ExperienceLogger(async_db)

        # Insert expired record (yesterday)
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        await logger.log_execution(
            brain_id="brain-01",
            input_json={"q": "expired"},
            output_json={"result": "old"},
            duration_ms=1000,
            status="success",
            custom_metadata={"quality_score": 2.0, "expires_at": yesterday}
        )

        # Insert fresh record (today)
        await logger.log_execution(
            brain_id="brain-01",
            input_json={"q": "fresh"},
            output_json={"result": "new"},
            duration_ms=1000,
            status="success",
            custom_metadata={"quality_score": 2.0, "expires_at": None}
        )

        records = await logger.get_recent_by_brain("brain-01", limit=10)

        # ASSERT: Only fresh record returned
        assert len(records) == 1
        assert records[0].input_json["q"] == "fresh"

    async def test_future_expiry_record_retrieved(self, async_db):
        """Record with expires_at in future still retrieved."""
        logger = ExperienceLogger(async_db)

        # Insert record expiring in 90 days
        future = (datetime.now() + timedelta(days=90)).isoformat()
        await logger.log_execution(
            brain_id="brain-01",
            input_json={"q": "future"},
            output_json={"result": "valid"},
            duration_ms=1000,
            status="success",
            custom_metadata={"quality_score": 2.0, "expires_at": future}
        )

        records = await logger.get_recent_by_brain("brain-01", limit=10)

        assert len(records) == 1
        assert records[0].input_json["q"] == "future"

    async def test_null_expires_at_treated_as_valid(self, async_db):
        """Records with expires_at=NULL never expire."""
        logger = ExperienceLogger(async_db)

        await logger.log_execution(
            brain_id="brain-01",
            input_json={"q": "permanent"},
            output_json={"result": "always valid"},
            duration_ms=1000,
            status="success",
            custom_metadata={"quality_score": 2.0, "expires_at": None}
        )

        records = await logger.get_recent_by_brain("brain-01", limit=10)

        assert len(records) == 1

    async def test_ttl_cleanup_job(self, async_db):
        """Background job deletes expired records (optional optimization)."""
        # This tests the cleanup job, not required for BLOCKER
        # but useful for maintenance
        logger = ExperienceLogger(async_db)

        # Insert 1000 expired records
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        for i in range(1000):
            await logger.log_execution(
                brain_id="brain-01",
                input_json={"q": f"expired_{i}"},
                output_json={"result": "old"},
                duration_ms=1000,
                status="success",
                custom_metadata={"quality_score": 2.0, "expires_at": yesterday}
            )

        # Run cleanup (if implemented)
        # await logger.cleanup_expired_records()

        # Verify cleanup worked
        records = await logger.get_recent_by_brain("brain-01", limit=1000)
        assert len(records) == 0, "Expired records not cleaned up"


@pytest.mark.asyncio
class TestTTLGeneration:
    """Verify new records get expires_at set correctly."""

    async def test_high_quality_template_gets_90_day_ttl(self, async_db):
        """Templates (score >= 3.0) get 90-day expiry."""
        logger = ExperienceLogger(async_db)

        await logger.log_execution(
            brain_id="brain-01",
            input_json={"q": "template"},
            output_json={"result": "reusable"},
            duration_ms=1000,
            status="success",
            custom_metadata={"quality_score": 3.5}
        )

        records = await logger.get_recent_by_brain("brain-01", limit=1)
        expires_at = records[0].custom_metadata.get("expires_at")

        assert expires_at is not None, "Template should have expiry"

        # Parse and verify ~90 days from now
        expiry_date = datetime.fromisoformat(expires_at)
        expected_min = datetime.now() + timedelta(days=89)
        expected_max = datetime.now() + timedelta(days=91)
        assert expected_min < expiry_date < expected_max

    async def test_low_quality_record_gets_30_day_ttl(self, async_db):
        """Experience records (1.0 <= score < 3.0) get 30-day expiry."""
        logger = ExperienceLogger(async_db)

        await logger.log_execution(
            brain_id="brain-01",
            input_json={"q": "experience"},
            output_json={"result": "ok"},
            duration_ms=1000,
            status="success",
            custom_metadata={"quality_score": 1.5}
        )

        records = await logger.get_recent_by_brain("brain-01", limit=1)
        expires_at = records[0].custom_metadata.get("expires_at")

        assert expires_at is not None

        expiry_date = datetime.fromisoformat(expires_at)
        expected_min = datetime.now() + timedelta(days=29)
        expected_max = datetime.now() + timedelta(days=31)
        assert expected_min < expiry_date < expected_max
```

**Implementation Requirement (logger.py:50-110):**
```python
# MODIFIED: log_execution() auto-sets expires_at based on quality_score
async def log_execution(
    self,
    brain_id: str,
    input_json: Dict[str, Any],
    output_json: Dict[str, Any],
    duration_ms: int,
    status: str,
    parent_brain_id: Optional[str] = None,
    trace_context_id: Optional[str] = None,
    custom_metadata: Dict[str, Any] | None = None,
) -> str:
    # ... existing record creation ...

    # AUTO-SET TTL based on quality_score
    quality_score = custom_metadata.get("quality_score", 0.0) if custom_metadata else 0.0
    expires_at = None

    if quality_score >= 3.0:
        # Templates: 90 days
        expires_at = (datetime.now() + timedelta(days=90)).isoformat()
    elif quality_score >= 1.0:
        # Experience records: 30 days
        expires_at = (datetime.now() + timedelta(days=30)).isoformat()
    # else: score < 1.0, no TTL (will be filtered anyway)

    if custom_metadata is None:
        custom_metadata = {}
    custom_metadata["expires_at"] = expires_at

    # ... existing INSERT with expires_at in custom_metadata ...
```

**Run Command:**
```bash
cd apps/api && uv run pytest tests/kd/test_ttl.py -v
```

---

### BLOCKER Condition 4: High-Value Detection

**Required Test File:** `apps/api/tests/kd/test_high_value.py` (NEW)
**Layer:** Unit (pure function, no database)
**Offline:** YES
**Count:** 5 tests

**Test Implementation:**

```python
# apps/api/tests/kd/test_high_value.py
"""Tests for high-value session detection (Brain #7 trigger)."""

import pytest
from mastermind_cli.orchestration.distillation_service import KnowledgeDistillationService, DistillationTask


class TestHighValueDetection:
    """Verify _is_high_value_session() logic."""

    def test_duration_over_5_minutes_triggers_evaluation(self):
        """Session > 5 minutes (300s) = high value."""
        service = KnowledgeDistillationService(db_path=":memory:")

        task = DistillationTask(
            session_id="test-1",
            brain_ids=["brain-01"],
            brief_summary="Test brief",
            execution_start_ms=0,
            execution_end_ms=350000,  # 350 seconds = 5m 50s
            results={},
            planning_score_delta=0,
            invocation_method="mm:execute-phase"
        )

        assert service._is_high_value_session(task) is True

    def test_duration_under_5_minutes_no_trigger(self):
        """Session < 5 minutes = NOT high value (unless other criteria met)."""
        service = KnowledgeDistillationService(db_path=":memory:")

        task = DistillationTask(
            session_id="test-2",
            brain_ids=["brain-01"],
            brief_summary="Quick brief",
            execution_start_ms=0,
            execution_end_ms=120000,  # 2 minutes
            results={},
            planning_score_delta=0,
            invocation_method="mm:execute-phase"
        )

        assert service._is_high_value_session(task) is False

    def test_planning_score_change_triggers_evaluation(self):
        """Brain #7's planning score changed = high value (pivot detected)."""
        service = KnowledgeDistillationService(db_path=":memory:")

        task = DistillationTask(
            session_id="test-3",
            brain_ids=["brain-01", "brain-07"],
            brief_summary="Brief with pivot",
            execution_start_ms=0,
            execution_end_ms=120000,  # Short duration
            results={},
            planning_score_delta=1,  # Planning score changed
            invocation_method="mm:execute-phase"
        )

        assert service._is_high_value_session(task) is True

    def test_complete_phase_invocation_triggers_evaluation(self):
        """User invoked /mm:complete-phase = high value (commitment signal)."""
        service = KnowledgeDistillationService(db_path=":memory:")

        task = DistillationTask(
            session_id="test-4",
            brain_ids=["brain-01"],
            brief_summary="Phase completion",
            execution_start_ms=0,
            execution_end_ms=120000,  # Short
            results={},
            planning_score_delta=0,
            invocation_method="mm:complete-phase"  # KEY SIGNAL
        )

        assert service._is_high_value_session(task) is True

    def test_all_criteria_false_no_trigger(self):
        """Short duration + no pivot + execute-phase = NOT high value."""
        service = KnowledgeDistillationService(db_path=":memory:")

        task = DistillationTask(
            session_id="test-5",
            brain_ids=["brain-01"],
            brief_summary="Simple query",
            execution_start_ms=0,
            execution_end_ms=60000,  # 1 minute
            results={},
            planning_score_delta=0,
            invocation_method="mm:execute-phase"
        )

        assert service._is_high_value_session(task) is False

    def test_multiple_criteria_true_still_triggers(self):
        """Duration + pivot + complete-phase = still True (not double-counted)."""
        service = KnowledgeDistillationService(db_path=":memory:")

        task = DistillationTask(
            session_id="test-6",
            brain_ids=["brain-01", "brain-07"],
            brief_summary="Major pivot with completion",
            execution_start_ms=0,
            execution_end_ms=600000,  # 10 minutes
            results={},
            planning_score_delta=2,  # Significant pivot
            invocation_method="mm:complete-phase"
        )

        assert service._is_high_value_session(task) is True

    def test_exact_5_minute_boundary(self):
        """Exactly 300 seconds = high value (boundary condition)."""
        service = KnowledgeDistillationService(db_path=":memory:")

        task = DistillationTask(
            session_id="test-7",
            brain_ids=["brain-01"],
            brief_summary="Boundary test",
            execution_start_ms=0,
            execution_end_ms=300000,  # Exactly 5 minutes
            results={},
            planning_score_delta=0,
            invocation_method="mm:execute-phase"
        )

        assert service._is_high_value_session(task) is True


class TestDistillationTaskModel:
    """Verify DistillationTask data contract."""

    def test_distillation_task_has_required_fields(self):
        """All fields required for high-value detection present."""
        task = DistillationTask(
            session_id="test",
            brain_ids=["brain-01"],
            brief_summary="Test",
            execution_start_ms=0,
            execution_end_ms=1000,
            results={},
            planning_score_delta=0,
            invocation_method="mm:execute-phase"
        )

        assert task.session_id == "test"
        assert task.execution_end_ms - task.execution_start_ms == 1000
        assert task.planning_score_delta == 0
        assert task.invocation_method == "mm:execute-phase"

    def test_duration_calculation_from_timestamps(self):
        """Duration derived from execution_end_ms - execution_start_ms."""
        task = DistillationTask(
            session_id="test",
            brain_ids=["brain-01"],
            brief_summary="Test",
            execution_start_ms=1000000,
            execution_end_ms=1350000,
            results={},
            planning_score_delta=0,
            invocation_method="mm:execute-phase"
        )

        duration_sec = (task.execution_end_ms - task.execution_start_ms) / 1000
        assert duration_sec == 350  # 5m 50s


class TestBackgroundExecution:
    """Verify distillation runs non-blocking."""

    @pytest.mark.asyncio
    async def test_distillation_service_runs_in_background(self, async_db):
        """trigger_evaluation_and_distillation() returns immediately."""
        from unittest.mock import AsyncMock

        service = KnowledgeDistillationService(db_path=":memory:")

        # Mock Brain #7 evaluation
        service._evaluate_with_brain_7 = AsyncMock(return_value={"quality_score": 3.5})

        task = DistillationTask(
            session_id="test-bg",
            brain_ids=["brain-01"],
            brief_summary="Background test",
            execution_start_ms=0,
            execution_end_ms=600000,
            results={},
            planning_score_delta=0,
            invocation_method="mm:complete-phase"
        )

        # Should return immediately (not wait for evaluation)
        start = pytest.importorskip("time").perf_counter()
        await service.trigger_evaluation_and_distillation(task)
        elapsed = pytest.importorskip("time").perf_counter() - start

        # ASSERT: Fast return (< 100ms), evaluation happens in background
        assert elapsed < 0.1, f"Function took {elapsed}s, should be non-blocking"
```

**Run Command:**
```bash
cd apps/api && uv run pytest tests/kd/test_high_value.py -v
```

---

### Summary: BLOCKER Verification Test Suite

| Blocker | Test File | Tests | Offline? | Run Command |
|---------|-----------|-------|----------|-------------|
| 1. Quality Score | `test_scoring.py` | 4 | YES | `cd apps/api && uv run pytest tests/kd/test_scoring.py -v` |
| 2. Rejection Filter | `test_rejection_filter.py` | 5 | YES | `cd apps/api && uv run pytest tests/kd/test_rejection_filter.py -v` |
| 3. TTL/Expiry | `test_ttl.py` | 4 | YES | `cd apps/api && uv run pytest tests/kd/test_ttl.py -v` |
| 4. High-Value Detection | `test_high_value.py` | 5 | YES | `cd apps/api && uv run pytest tests/kd/test_high_value.py -v` |

**Total BLOCKER Tests:** 18 tests
**All Offline:** YES (no MCP, no network, in-memory SQLite)
**Runtime:** < 30 seconds total

### CI/CD Integration

**Add to `.github/workflows/ci.yml`:**
```yaml
blocker-tests:
  name: Phase 14 BLOCKER Verification
  runs-on: ubuntu-latest
  timeout-minutes: 5
  steps:
    - uses: actions/checkout@v4
    - name: Install uv
      run: curl -LsSf https://astral.sh/uv/install.sh | sh
    - name: Install dependencies
      run: cd apps/api && uv sync
    - name: BLOCKER 1: Quality Score
      run: cd apps/api && uv run pytest tests/kd/test_scoring.py -v
    - name: BLOCKER 2: Rejection Filter
      run: cd apps/api && uv run pytest tests/kd/test_rejection_filter.py -v
    - name: BLOCKER 3: TTL
      run: cd apps/api && uv run pytest tests/kd/test_ttl.py -v
    - name: BLOCKER 4: High-Value Detection
      run: cd apps/api && uv run pytest tests/kd/test_high_value.py -v
```

### Pre-commit Hook

**Add to `.pre-commit-config.yaml`:**
```yaml
# Phase 14 BLOCKER tests (pre-commit, fast)
- repo: local
  hooks:
    - id: kd-blocker-tests
      name: Phase 14 BLOCKER Verification
      entry: bash -c 'cd apps/api && uv run pytest tests/kd/test_scoring.py tests/kd/test_high_value.py -v'
      language: system
      pass_filenames: false
      stages: [pre-commit]
```

### Regression Impact

- **631 backend tests:** ZERO impact — new test directory, isolated fixtures
- **407 frontend tests:** ZERO impact — no frontend changes
- **Additive only:** 18 new tests in `tests/kd/`
- **Total after Phase 14:** ~631 + ~407 + ~18 BLOCKER + ~19-30 KD = ~1,075-1,086 total


---

## 2026-04-06 — BLOCKER Test Verification Summary

### What Was Added

**18 specific tests** to verify Brain #7's 4 BLOCKER conditions before Phase 14 ships.

| Blocker | Tests | Key Assertion |
|---------|-------|---------------|
| 1. Quality Score (Hormozi) | 4 | Formula `(Precision × Success) / (T1 × Tokens)` correct, penalties applied |
| 2. Rejection Filter | 5 | `get_recent_by_brain()` excludes `status='rejected'` AND `quality_score < 1.0` |
| 3. TTL/Expiry | 4 | Records with `expires_at < NOW()` excluded from retrieval |
| 4. High-Value Detection | 5 | Duration > 300s OR planning_score_delta != 0 OR invocation_method == "mm:complete-phase" |

### Implementation Requirements

**Schema Changes:**
```sql
ALTER TABLE experience_records ADD COLUMN quality_score REAL DEFAULT 0.0;
ALTER TABLE experience_records ADD COLUMN expires_at TEXT;
CREATE INDEX idx_expires_at ON experience_records(expires_at);
```

**Code Changes (logger.py):**
- `get_recent_by_brain()`: Add `WHERE quality_score >= 1.0 AND status != 'rejected' AND (expires_at IS NULL OR expires_at > datetime('now'))`
- `log_execution()`: Auto-set `expires_at` based on quality_score (90 days for >= 3.0, 30 days for >= 1.0)

**New Files:**
- `apps/api/mastermind_cli/experience/scoring.py` — `calculate_quality_score()`, `has_structure()`, `can_invert()`
- `apps/api/mastermind_cli/orchestration/distillation_service.py` — `_is_high_value_session()`, `trigger_evaluation_and_distillation()`

### All Tests Offline

✅ No MCP calls
✅ No network
✅ In-memory SQLite
✅ Deterministic fixtures

### CI/CD Gate

**New job:** `blocker-tests` in `.github/workflows/ci.yml`
**Pre-commit:** Fast subset (quality score + high-value detection) runs before push

### Success Criteria

Before Phase 14 closes:
1. All 18 BLOCKER tests pass
2. Schema migrations applied
3. logger.py filters implemented
4. CI/CD gate passes on PR


---

## 2026-04-10 — Phase 18 Webhook Reliability: QA Strategy Consultation

### Context
Phase 18 (Multi-channel Gateway) requires webhook reliability testing for WhatsApp/Instagram/Email integration. Consulted NotebookLM Brain #6 (Humble, Majors, Feathers) for expert patterns.

### Verified Insights

**1. WEBHOOK TESTING PATTERNS — Idempotency & Deduplication**
- Test pattern: Send exact same payload twice with unique `transaction_id` header
- Success criteria: Second call returns `200 OK` or `204 No Content`, database verification ensures no duplicate agent tasks created
- Implementation: Use "seams" (Michael Feathers) to inject transaction IDs, isolate external provider dependencies
- File reference: Phase 16's `k6-websocket-load.js` provides template for load test structure with custom metrics (Trend, Rate)

**2. DLQ TESTING — Retry Logic Validation**
- Fault injection pattern: Mock transient `503 Service Unavailable` from backend
- Flow validation: Message transitions to DLQ → trigger "Retry Worker" → verify message re-queued and processed when service recovers
- Critical anti-pattern: "Silent Drop" — returning `200 OK` to provider before message is safely persisted in queue/database
- Test location: `apps/api/tests/integration/test_webhook_dlq.py` (new file needed)

**3. LOAD TESTING FOR WEBHOOK THROUGHPUT — k6 Scripts**
- Extend Phase 16's k6 setup: `rust_control_plane/tests/k6-websocket-load.js` → `k6-webhook-load.js`
- Target: 1000+ webhooks/second with p99 latency < 200ms (SLI from Brain #6)
- Soak testing: 1 hour at peak load to identify memory leaks in Rust/Python tracing layers
- Metrics: Use k6 Thresholds with `abortOnFail: true` for SLI enforcement
- Command: `k6 run rust_control_plane/tests/k6-webhook-load.js`

**4. MONITORING PATTERNS — SLO-Based Alerting**
- Error budget burn rate alerts (Charity Majors' ODD): If webhook failures will exhaust 99.9% reliability goal in 4 hours → immediate notification
- High-cardinality data in structured logs: `provider_response_code`, `payload_size_bytes`, `trace_id` in every event
- Distributed tracing: Ensure `trace_id` propagates from webhook gateway → PostgreSQL dual-write → agent response
- Prometheus metrics: `webhook_received_total`, `webhook_dlq_total`, `webhook_processing_duration_seconds` (histogram)

**5. SUCCESS CRITERIA — Measurable Reliability Outcomes**
- DORA Elite: Lead Time for Changes < 1 hour, Change Failure Rate < 15% for Phase 18
- Reliability SLO: 99.9% webhooks acknowledged + queued within 200ms (p99)
- MTTR: < 1 hour to recover/rollback from routing failure
- Infrastructure idempotence: Recreate webhook gateway from IaC in < 15 minutes

**6. CROSS-CHANNEL MESSAGE ROUTING TESTS**
- Test: WhatsApp message → routed to agent → response sent via WhatsApp (not Instagram/Email)
- Test: Channel Router brain agent selects optimal channel based on context
- Mock strategy: Use `respx` (Python) or `httpx_mock` to isolate external provider APIs
- No live MCP calls: All WhatsApp/Instagram API tests must use mocked responses

### Deferred Items

- Deferred: Circuit breaker implementation (Phase 18 design decision — Graceful degradation under stress)
- Deferred: Blameless postmortem template (after first load test failure)
- Deferred: Wheel of Misfortune training exercise (after initial k6 results)

### Corrected Assumptions (Always Include)

```
❌ "npm test is the test command" → ✅ pnpm --prefix apps/web test run (frontend) and cd apps/api && uv run pytest (backend)
❌ "pre-commit hooks run from apps/api/" → ✅ .pre-commit-config.yaml in ROOT; hooks run from repo root via bash -c 'cd apps/api && uv run ...'
❌ "docker compose runs from apps/api/" → ✅ docker compose up from ROOT only
❌ "Tests can have pre-existing failures" → ✅ ZERO tolerance for pre-existing failures. Suite must be 0 failures before any phase closes.
❌ "Integration tests require live MCP" → ✅ MCP calls must be mockable in tests — no test that requires live NotebookLM
```

### Test Layer Strategy (Phase 18)

| Layer | What | Tool | Count Target | Offline? |
|-------|------|------|-------------|----------|
| Webhook unit tests | Idempotency, deduplication, DLQ transitions | pytest | 15-20 | Yes |
| Provider contract tests | WhatsApp/Instagram API mock contracts | pytest + respx | 8-12 | Yes |
| Cross-channel routing tests | Channel Router brain agent selection | pytest | 5-8 | Yes |
| Load tests (k6) | 1000 webhooks/second, p99 latency < 200ms | k6 | 3-5 scripts | No (needs running gateway) |
| Soak tests | 1-hour endurance for memory leaks | k6 | 1-2 scripts | No (needs running gateway) |
| Integration tests | End-to-end webhook → agent → response | Docker Compose + pytest | 3-5 | No (needs all services) |

### Regression Impact

- Current baseline: 682 backend + 575 frontend = 1,257 total tests (as of Phase 16 completion)
- Phase 18 adds: ~50 new tests (webhook unit + contract + routing + load)
- No breaking changes to existing test suite
- New test files: `apps/api/tests/integration/test_webhook_*.py`, `rust_control_plane/tests/k6-webhook-*.js`

### Run Commands (Exact Paths)

```bash
# Backend webhook tests (from ROOT — per .pre-commit-config.yaml pattern)
cd apps/api && uv run pytest tests/integration/test_webhook_idempotency.py -v
cd apps/api && uv run pytest tests/integration/test_webhook_dlq.py -v
cd apps/api && uv run pytest tests/integration/test_cross_channel_routing.py -v

# Load tests (from ROOT — k6 scripts in rust_control_plane/tests/)
k6 run rust_control_plane/tests/k6-webhook-load.js
k6 run rust_control_plane/tests/k6-webhook-soak.js

# Full backend suite (baseline preservation)
cd apps/api && uv run pytest --cov=mastermind_cli --cov-report=xml

# Verify no regressions
pnpm --prefix apps/web test run
```

### Offline Guarantee

All webhook tests run without live network calls:
- Provider APIs mocked via `respx` or `httpx_mock`
- WhatsApp Business Cloud API → mock `https://graph.facebook.com` endpoints
- Instagram Graph API → mock `https://graph.instagram.com` endpoints
- Email sending → mock `aiosmtplib` via `pytest.mock.patch`
- DLQ tests use in-memory queue, no PostgreSQL dependency for unit layer

### Next Steps for Phase 18 Planning

1. Define webhook SLIs in `18-01-PLAN.md` (latency, throughput, error rate)
2. Create `apps/api/tests/integration/test_webhook_idempotency.py` with duplicate payload test
3. Create `rust_control_plane/tests/k6-webhook-load.js` based on Phase 16's WebSocket load test template
4. Add Prometheus metrics for webhook DLQ + processing duration
5. Implement circuit breaker pattern in Rust webhook handler (graceful degradation)
