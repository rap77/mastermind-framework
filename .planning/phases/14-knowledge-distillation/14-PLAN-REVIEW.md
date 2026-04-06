# Phase 14 — Plan Review Context
> Generated: 2026-04-06T03:45:00Z
> Updated: 2026-04-06T04:00:00Z
> Iteration: 2
> Purpose: Full context for Brain #7 plan validation

---

## ITERATION DELTA (Changes from Iteration 1)

### Fix 1: SQLite Percentile Function Replaced (Plan 14-04 Task 1)
**What changed**: Replaced `percentile_val()` with Python-based calculation
**Before**: `SELECT percentile_val(0.5, duration_ms)` (SQLite doesn't support this)
**After**: Fetch all durations, calculate P50/P90 in Python using array indexing
**Impact**: BLOCKING gap resolved — runtime error prevented

### Fix 2: Analytics Router Registration Explicit (Plan 14-04 Task 3)
**What changed**: Corrected file path and added explicit registration step
**Before**: `apps/api/mastermind_cli/api/main.py` (wrong file)
**After**: `apps/api/mastermind_cli/api/app.py` with explicit include_router call
**Impact**: BLOCKING gap resolved — 404 errors prevented

### Fix 3: Cold Start Fallback Added (Plan 14-03 Task 2)
**What changed**: Added cold start detection + threshold lowering logic
**Before**: No fallback — zero templates = zero value
**After**: If zero templates exist, lower threshold to 2.0 with warning
**Impact**: HIGH RISK gap resolved — system can bootstrap itself

### Fix 4: Quality Score Calibration Note Added (Plan 14-01 Task 1)
**What changed**: Added note that Precision/Success scores come from Brain #7 auto-eval
**Before**: No source specified
**After**: Documented that Brain #7 assigns scores during post-session evaluation
**Impact**: MEDIUM RISK acknowledged — full calibration deferred to Phase 15

---

---

## IMPLEMENTED REALITY

From BRAIN-FEED.md (cross-domain patterns):
- **Stack Locked**: Next.js 16, React 19, TypeScript 5, Tailwind 4, Zustand 5, Python 3.14 + uv
- **Brain Agent Architecture**: 3-file bundles (brain + criteria + warnings), dispatched AFTER domain brains
- **Delta-Velocity**: T1 > 300s = unprofitable, pre-migration baseline 210-270s
- **Two-level Feed**: Global (product/UX) + Domain feeds (technical), read-only for agents

From STATE.md:
- **Phase 13 COMPLETE**: Rust velocity 6.2x faster than Python, escape hatch NOT triggered
- **v3.0 Stack**: Rust (Axum + Tokio) + Python (FastAPI) + TypeScript (Next.js)
- **Knowledge Distillation**: Pulled forward to Phase 14 (leveraging existing 7 brains + brain_memory.py + experience_records)
- **Baseline T1**: 210-270s (pre-migration manual workflow)
- **Tests**: 631 backend pytest + 407 frontend vitest = 1038 total

From codebase reading:

**ExperienceLogger** (`apps/api/mastermind_cli/experience/logger.py`):
- `log_execution()` accepts `custom_metadata` dict (JSONB storage)
- `get_recent_by_brain()` returns `List[ExperienceRecord]` with NO quality filtering
- `search_by_metadata()` uses `json_extract()` for JSONB queries
- ALLOWED_METADATA_KEYS whitelist includes `"quality_score"`

**ExperienceRecord** (`apps/api/mastermind_cli/experience/models.py`):
- `custom_metadata: dict[str, Any]` (extensible metadata)
- `status: str` (pattern: success|failure|timeout)
- NO `quality_score` field (to be added via custom_metadata)
- NO `expires_at` field (to be added via migration)

**PostgreSQL NOT YET MIGRATED**:
- Current: SQLite with `aiosqlite`
- Migration to PostgreSQL planned for Phase 15
- Plan 14 uses SQLite SQL dialect (no CTEs, no window functions)

---

## PLAN SUMMARIES

### Plan 14-01 (Foundation) — Quality Score + Rejection Filter + TTL

**Objective**: Build quality score calculation + rejection filter + TTL ceiling

**Key Truths**:
- Quality score: ≥3.0 (template), ≥1.0 (record), <1.0 (discard)
- Rejection filter: `WHERE quality_score >= 1.0 AND status != 'rejected'`
- TTL ceiling: 90-day expiry with `expires_at` column
- Penalties: Twaddle 50%, Inversion 30%

**Artifacts**:
1. `scoring.py` — Hormozi value equation: `(Precision × Success) / (T1 × Tokens) × 1000`
2. `logger.py` updated — rejection filter in `get_recent_by_brain()`
3. `002_add_expires_at.sql` — TTL migration with 90-day default

**Tests**: 13 (4 scoring + 5 rejection + 4 TTL)

---

### Plan 14-02 (Auto-evaluation Loop) — High-Value Detection + Background Hook

**Objective**: Wire post-session auto-evaluation with high-value detection

**Key Truths**:
- High-value criteria: duration > 5min OR planning_score_changed OR `mm:complete-phase`
- Post-session hook: FastAPI `BackgroundTasks.add_task()` (non-blocking)
- `DistillationTask` captures session metadata (T1, duration, planning_score_delta)

**Artifacts**:
1. `distillation_service.py` — `KnowledgeDistillationService` + `DistillationTask` model
2. `tasks.py` updated — BackgroundTasks hook in `/api/tasks/auto`
3. `agent_runner.py` — Wrapper for T1 tracking (interface only, full integration later)

**Tests**: 5 (high-value detection)

**Dependencies**: Plan 14-01 (quality_score calculation)

---

### Plan 14-03 (Template Generation) — Pattern Extraction + Storage

**Objective**: Build template storage + extraction system for reusable patterns

**Key Truths**:
- `knowledge_templates` table (separate from `experience_records` per Screaming Architecture)
- Templates auto-extracted from quality_score >= 3.0 records
- Template tracks `success_rate` (starts 1.0) + `usage_count` (starts 0)

**Artifacts**:
1. `003_create_knowledge_templates.sql` — Template table with indexes
2. `template_extractor.py` — `TemplateExtractor` with pattern extraction
3. `distillation_service.py` updated — Template extraction integration

**Tests**: 6 (template table + extraction + integration)

**Dependencies**: Plan 14-01 (quality_score), Plan 14-02 (distillation service)

---

### Plan 14-04 (Dashboard API) — System Health + Outcome Metrics

**Objective**: Build dashboard API for system health + outcome metrics

**Key Truths**:
- `GET /api/analytics/system-health` — record count, avg quality_score, rejection rate, P50/P90 latency, T1 trend
- `GET /api/analytics/templates` — templates ordered by success_rate DESC
- `GET /api/analytics/patterns` — recurring patterns per brain (grouped by brief similarity)
- System health detects unbounded growth (record count ceiling, retrieval latency ceiling)

**Artifacts**:
1. `analytics_service.py` — `AnalyticsService` with `SystemHealthMetrics` + `OutcomeMetrics`
2. `analytics.py` — 4 API endpoints (/system-health, /templates, /patterns, /outcome-metrics)
3. `main.py` updated — Router registration

**Tests**: 7 (service + endpoints)

**Dependencies**: Plan 14-01, 14-02, 14-03

---

## CODE SNIPPETS

**Existing `get_recent_by_brain()` (logger.py:129-149)**:
```python
async def get_recent_by_brain(
    self, brain_id: str, limit: int = 100
) -> List[ExperienceRecord]:
    cursor = await self.db.conn.execute(
        """SELECT * FROM experience_records
           WHERE brain_id = ?
           ORDER BY timestamp DESC
           LIMIT ?""",
        (brain_id, limit),
    )
    rows = await self.db.fetchall()
    return [self._row_to_record(row) for row in rows]
```

**Proposed change (Plan 14-01)**:
```python
async def get_recent_by_brain(
    self, brain_id: str, limit: int = 100, min_quality_score: float = 1.0
) -> List[ExperienceRecord]:
    cursor = await self.db.conn.execute(
        """SELECT * FROM experience_records
           WHERE brain_id = ?
             AND json_extract(custom_metadata, '$.quality_score') >= ?
             AND status != 'rejected'
             AND (expires_at IS NULL OR expires_at > datetime('now'))
           ORDER BY timestamp DESC
           LIMIT ?""",
        (brain_id, min_quality_score, limit),
    )
    # ...
```

**Scoring formula (Plan 14-01)**:
```python
def calculate_quality_score(
    precision: float, success_probability: float, t1_ms: int, tokens: int,
    output_text: Optional[str] = None,
) -> float:
    t1_sec = max(t1_ms / 1000, 1.0)
    token_count = max(tokens, 1)
    base_score = (precision * success_probability) / (t1_sec * token_count) * 1000

    if output_text:
        if word_count > 2000 and not _has_structure(output_text):
            base_score *= 0.5  # Twaddle penalty
        if not _can_invert(output_text):
            base_score *= 0.7  # Inversion penalty

    return round(base_score, 2)
```

**BackgroundTasks hook (Plan 14-02)**:
```python
# In tasks.py /api/tasks/auto endpoint
background_tasks.add_task(
    distillation_service.trigger_evaluation_and_distillation,
    distillation_task
)
```

**Template extraction (Plan 14-03)**:
```python
async def extract_and_store_template(self, record: ExperienceRecord) -> Optional[str]:
    quality_score = record.custom_metadata.get("quality_score", 0.0)
    if quality_score < 3.0:
        return None

    template_id = str(uuid.uuid4())
    # ... INSERT INTO knowledge_templates ...
    return template_id
```

---

## CORRECTED ASSUMPTIONS

### What Brain #7 might assume wrong:

1. **"PostgreSQL already migrated"** — NO. PostgreSQL migration is Phase 15. Plan 14 uses SQLite with aiosqlite.
   - Impact: SQL queries must use SQLite dialect (no CTEs, no window functions like `percentile_cont`)
   - Plan 14-04 uses `percentile_val()` which may not exist in SQLite — need to verify

2. **"Brain #7 LLM call in Plan 14-02"** — NO. Plan 14-02 creates the hook but defers actual Brain #7 LLM call to future plans.
   - Plan 14-02 only logs that evaluation was triggered
   - Actual Brain #7 agent dispatch deferred to avoid scope creep

3. **"AgentRunner integrated into StatelessCoordinator"** — NO. Plan 14-02 creates the wrapper interface but doesn't integrate it.
   - Full integration (T1 tracking) deferred to future phase
   - This plan establishes the pattern only

4. **"Real delta-velocity calculation"** — NO. Plan 14-04 uses avg duration_ms as proxy.
   - Real delta-velocity requires session grouping by user brief (complex query)
   - Simplified approach acceptable for v1

5. **"pgvector embedding search"** — NO. Plan 14-03 uses hash-based matching (input_hash).
   - Semantic similarity via pgvector deferred to Phase 15
   - Hash-based approach sufficient for template deduplication

---

## WHAT I NEED

Brain #7, evaluate using your **Systems Thinker** lens:

1. **Planning Fallacy check** — What are we underestimating?
   - Are task time estimates realistic?
   - Any hidden dependencies between plans?
   - Test coverage adequate for complexity?

2. **Omission Bias** — What's missing that will block execution?
   - Database migration order (002 before 003)?
   - Router registration (analytics in main.py)?
   - Edge cases in rejection filter?

3. **Systems Thinking** — What feedback loops between plans?
   - Quality score → Template extraction (Plan 14-01 → 14-03)
   - Template reuse → Delta-velocity (Plan 14-03 → 14-04)
   - Rejection filter → Analytics accuracy (Plan 14-01 → 14-04)
   - Are these loops coherent?

4. **Over-engineering risk** — What won't be used?
   - Is `agent_runner.py` wrapper premature? (Plan 14-02)
   - Is 3-tier quality score (template/record/discard) too complex?
   - Are 7 analytics endpoints overkill for v1?

5. **Acceptance criteria quality** — Are done criteria verifiable?
   - "High-value detection works" — how verify? (Plan 14-02)
   - "System health detects unbounded growth" — what threshold? (Plan 14-04)
   - "Templates track success_rate" — how measured? (Plan 14-03)

Be specific about WHICH plan and WHICH task.

**Verdict format**:
```
## Verdict: [APPROVED | APPROVED_WITH_CONDITIONS | REJECTED_REVISE]

## Gaps Found
- [Gap 1]: Which plan, which task, why blocking
- [Gap 2]: Which plan, which task, why blocking

## Conditions (if APPROVED_WITH_CONDITIONS)
- [Condition 1]: What must change before execution
- [Condition 2]: What must change before execution

## Systems Thinking Insights
[Feedback loops, emergent properties, second-order effects]
```

---

<!-- This file is consumed by Brain #7 (brain-07-growth) -->
<!-- Read this file BEFORE evaluating. DO NOT rely on plan text only. -->
