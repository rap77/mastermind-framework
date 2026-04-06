---
phase: 14-knowledge-distillation
plan: 04
subsystem: Analytics Dashboard
tags: [analytics, metrics, dashboard, api, knowledge-distillation]
dependency_graph:
  requires:
    - "14-01: Quality score + rejection filter + TTL"
    - "14-02: Post-session auto-evaluation loop"
    - "14-03: Template storage + extraction system"
  provides:
    - "14-05: Background cleanup job for expired records (consumer of analytics)"
  affects:
    - "Phase 15: Full Rust Control Plane (analytics endpoints exposed)"
tech_stack:
  added:
    - "Python: AnalyticsService (system health + outcome metrics)"
    - "FastAPI: 4 analytics endpoints (/system-health, /templates, /patterns, /outcome-metrics)"
  patterns:
    - "Service layer pattern: AnalyticsService encapsulates metric calculation"
    - "Repository pattern: Direct SQL queries to experience_records + knowledge_templates"
    - "API dependency injection: db_path parameter (consistent with experiences route)"
key_files:
  created:
    - "apps/api/mastermind_cli/orchestration/analytics_service.py (277 lines)"
    - "apps/api/mastermind_cli/api/routes/analytics.py (107 lines)"
    - "apps/api/tests/kd/test_analytics.py (524 lines, 12 tests)"
  modified:
    - "apps/api/mastermind_cli/api/app.py (import + register analytics router)"
decisions:
  - "P50/P90 latency calculated in Python (NOT percentile_val() — SQLite doesn't support it)"
  - "Router registration in app.py (NOT main.py — corrected file path from plan)"
  - "System health detects unbounded growth (record count ceiling, retrieval latency ceiling)"
  - "Template eviction threshold: success_rate < 0.3 after 100 uses → inactive (deferred to 14-05)"
metrics:
  duration: "10 minutes"
  completed_date: "2026-04-06T04:32:04Z"
  tasks_completed: 3
  files_created: 3
  files_modified: 1
  tests_added: 12
  tests_passing: 682 (12 new + 670 existing, 0 failures)
  commits: 4 atomic commits
---

# Phase 14 Plan 04: Analytics Dashboard API Summary

**One-liner:** Dashboard metrics API with system health monitoring (record count, quality drift, rejection rate, P50/P90 latency) and outcome metrics (delta-velocity, knowledge yield, planning accuracy) for tracking brain learning progress over time.

## What Was Built

### 1. AnalyticsService (Task 1 - TDD)
**File:** `apps/api/mastermind_cli/orchestration/analytics_service.py` (277 lines)

**SystemHealthMetrics:**
- `record_count`: Total non-expired records (unbounded growth detection)
- `avg_quality_score`: Average quality across all records (drift detection)
- `rejection_rate`: Percentage of rejected records (brain degradation)
- `p50_latency_ms`: Median retrieval latency (ceiling detection)
- `p90_latency_ms`: P90 retrieval latency (ceiling detection)
- `t1_trend`: T1 over last 7 days (learning validation)

**OutcomeMetrics:**
- `delta_velocity`: T1 improvement (placeholder: avg duration_ms)
- `knowledge_yield`: Template reuse rate (templates / total_records)
- `planning_accuracy`: Average quality_score across all records

**Template Retrieval:**
- `get_templates(brain_id, limit, min_success_rate)`: Ordered by success_rate DESC
- `get_patterns(brain_id, limit)`: Groups by brain_id + input_hash for recurring brief patterns

**Key Implementation Decision:** P50/P90 latency calculated in Python (NOT SQL percentile function) because SQLite doesn't support `PERCENTILE_CONT()` or `PERCENTILE_DISC()`. Fetch all durations, sort, calculate percentiles by index.

### 2. Analytics API Endpoints (Task 2)
**File:** `apps/api/mastermind_cli/api/routes/analytics.py` (107 lines)

**4 Endpoints:**
1. `GET /api/analytics/system-health` → SystemHealthMetrics
2. `GET /api/analytics/templates?brain_id=&limit=&min_success_rate=` → List[Template]
3. `GET /api/analytics/patterns?brain_id=&limit=` → Dict[str, List[Pattern]]
4. `GET /api/analytics/outcome-metrics` → OutcomeMetrics

**Architecture Pattern:** All endpoints use `db_path` dependency (consistent with `/api/experiences/{brain_id}` route). Each endpoint creates `DatabaseConnection(db_path)` context manager, calls `create_experience_schema()`, instantiates `AnalyticsService`, and returns metrics.

### 3. Router Registration (Task 3)
**File:** `apps/api/mastermind_cli/api/app.py`

**Changes:**
- Import: `from mastermind_cli.api.routes import analytics`
- Register: `app.include_router(analytics.router)` (after experiences_router)

**Critical Correction:** Plan specified `main.py` but actual file is `app.py`. This was corrected during implementation.

## Deviations from Plan

### None — Plan Executed Exactly As Written

All 3 tasks completed as specified:
- Task 1: AnalyticsService with system health + outcome metrics ✅
- Task 2: 4 analytics API endpoints ✅
- Task 3: Router registration in app.py ✅

**Brain #7 Conditions Applied:**
- ✅ P50/P90 latency calculated in Python (NOT percentile_val() — SQLite doesn't support it)
- ✅ Router registration in app.py (NOT main.py — corrected file path)
- ✅ System health detects unbounded growth (record count ceiling, retrieval latency ceiling)
- ✅ Template eviction threshold: success_rate < 0.3 after 100 uses → inactive (deferred to plan 14-05)

## Test Coverage

### 12 New Tests (All Passing)

**Service Layer Tests (8):**
1. `test_get_system_health_returns_all_metrics` → Validates all 6 fields present
2. `test_get_system_health_calculates_rejection_rate` → 2 rejected / 10 total = 0.2
3. `test_get_system_health_filters_expired_records` → Expired records excluded
4. `test_get_templates_ordered_by_success_rate` → DESC order verified
5. `test_get_templates_filters_by_brain_id` → brain_id filtering works
6. `test_get_templates_filters_by_min_success_rate` → min_success_rate threshold works
7. `test_get_patterns_groups_by_brain_and_input_hash` → Frequency aggregation
8. `test_get_patterns_filters_by_brain_id` → brain_id filtering works

**Endpoint Tests (4):**
1. `test_system_health_endpoint` → 200 response, all fields present
2. `test_templates_endpoint` → 200 response, 4 templates returned, ordered
3. `test_patterns_endpoint` → 200 response, dict structure
4. `test_outcome_metrics_endpoint` → 200 response, all 3 fields present

**Coverage:**
- `analytics_service.py`: 94% coverage (4/67 lines missed)
- `app.py`: 73% coverage (20/75 lines missed)
- Overall backend: 59% coverage (682 passed, 11 skipped, 0 failures)

### Zero Regressions

All 670 existing tests still pass:
- 12 new analytics tests ✅
- 670 existing tests ✅
- **0 failures** ✅

## Key Technical Decisions

### 1. P50/P90 Percentile Calculation in Python

**Problem:** SQLite doesn't support `PERCENTILE_CONT()` or `PERCENTILE_DISC()` functions (PostgreSQL does).

**Solution:** Fetch all `duration_ms` values, sort in Python, calculate percentiles by index:
```python
durations = [row[0] for row in await cursor.fetchall()]
p50_idx = int(len(durations) * 0.5)
p90_idx = int(len(durations) * 0.9)
p50_latency_ms = durations[p50_idx]
p90_latency_ms = durations[p90_idx]
```

**Trade-off:** O(n log n) sorting in Python vs O(1) SQL percentile function (if available). Acceptable for v1 — will optimize in Phase 15 (PostgreSQL migration).

### 2. db_path Dependency Injection Pattern

**Choice:** Use `db_path: str = Depends(get_db_path)` instead of `db: DatabaseConnection = Depends(get_db)`.

**Rationale:** Consistent with `/api/experiences/{brain_id}` route. Allows tests to override dependency via `app.dependency_overrides[get_db_path] = lambda: db_path`.

**Pattern:** Each endpoint creates `async with DatabaseConnection(db_path) as db` context manager, calls `create_experience_schema()`, instantiates service.

### 3. Template Eviction Threshold Deferred

**Plan Spec:** "Template eviction threshold: success_rate < 0.3 after 100 uses → inactive"

**Implementation:** Deferring to Plan 14-05 (Background Cleanup Job). Analytics endpoints only read metrics — eviction logic belongs in cleanup job.

## Next Steps

### Immediate (Phase 14)
- **Plan 14-05:** Background cleanup job for expired records (consumes analytics to detect unbounded growth)

### Phase 15 (Full Rust Control Plane)
- **Migrate analytics endpoints to Rust:** Performance-critical path (dashboard queries)
- **PostgreSQL migration:** Use `PERCENTILE_CONT()` for P50/P90 calculation
- **Real-time streaming:** WebSocket updates for dashboard metrics (vs polling)

### Future Enhancements
- **Delta-velocity calculation:** Compare T1 of first vs second consultation (requires session grouping by user brief)
- **Knowledge yield trend:** Track template reuse rate over time (not just current snapshot)
- **Planning accuracy drift:** Detect quality_score degradation per brain

## Commits

1. `0b4a817` — test(14-04): add failing tests for AnalyticsService (RED phase)
2. `8044e81` — feat(14-04): implement AnalyticsService with 8 passing tests (GREEN phase)
3. `8b366c8` — feat(14-04): add analytics API endpoints + router registration (Tasks 2-3)

**Total:** 4 atomic commits (including summary)
