# Phase 14: Knowledge Distillation — Context (Brain-Informed)

> Generated: 2026-04-06
> Brain #7 Verdict: APPROVED_WITH_CONDITIONS (72/100)
> Moment 2 (Domain) + Moment 3 (Validation) complete

## Phase Goal

Build auto-learning system where brains improve over time through:
1. **KD-01:** Brain #7 evaluates every output → feedback → memory adjustment
2. **KD-02:** Successful interactions → reusable templates
3. **KD-03:** Dashboard shows patterns, insights, delta-velocity trends

**Current State:** ExperienceLogger exists (0 records), 7 brain agents exist, but learning loop is NOT wired.

## Concrete Implementation Decisions

### Decision 1: Template Storage (Brains #1, #5, #7 aligned)

**SEPARATE `knowledge_templates` table** (NOT flag on experience_records)

**Schema:**
```sql
CREATE TABLE knowledge_templates (
    id TEXT PRIMARY KEY,
    brain_id TEXT NOT NULL,
    template_name TEXT NOT NULL,
    template_data TEXT NOT NULL,  -- JSONB
    success_rate REAL DEFAULT 1.0,
    usage_count INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    last_used_at TEXT,

    INDEX idx_templates_brain_id (brain_id),
    INDEX idx_templates_success_rate (success_rate DESC)
);
```

**Why:** Screaming Architecture — templates are domain concepts, experience logs are infrastructure.

---

### Decision 2: Pattern Extraction (Brains #1, #5 aligned)

**Use pgvector embeddings** for semantic intent matching (NOT keywords)

**Why:** Keywords match words. Embeddings match semantic intent. "Database query" (shallow) vs "data modeling decision with consistency tradeoffs" (deep).

**Implementation:** Phase 15 PostgreSQL migration adds `embedding_vector` column. Template extraction = clustering over embeddings, NOT ML training (out of scope).

---

### Decision 3: Quality Score Rubric (Brain #7 wins tension)

**3-tier threshold** (NOT single threshold):

| Score | Action | Rationale |
|-------|--------|-----------|
| >= 3.0 | Store as template candidate | High-quality, reusable |
| >= 1.0 | Store as experience record | Worth remembering, not templating |
| < 1.0 | Discard | "Dead offer" — noise |

**Formula (Hormozi value equation):**
```
Quality Score = (Precision × Success_Probability) / (T1 × Tokens/Compute)
```

**Where:**
- Precision: % of output that was actionable (not fluff)
- Success_Probability: Likelihood this output works for similar briefs
- T1: Time from brief to completion (user attention time)
- Tokens/Compute: Cost to generate this output

**Penalties:**
- Twaddle penalty: Output > 2000 words without structure → score penalty
- Inversion check: Cannot state "what to avoid" → score penalty

---

### Decision 4: Rejection Handling (Brain #7 wins tension)

**Store rejected outputs with `status='rejected'`** (NOT silent deletion)

**Implementation:**
```python
# In ExperienceLogger.log_execution()
await self.log_execution(
    brain_id=brain_id,
    input_json=input_json,
    output_json=output_json,
    status="rejected",  # <-- NEW: tracks failures
    quality_score=0.0,  # <-- NEW: explicit zero
    ...
)
```

**Retrieval filter (MANDATORY):**
```python
# In ExperienceLogger.get_recent_by_brain()
# MUST filter to prevent rejected outputs from polluting prompts
WHERE quality_score >= 1.0 AND status != 'rejected'
```

**Why:** Silent deletion = invisible learning loss (Kohavi's statistical leakage). Rejection logging enables pre-mortem analysis.

---

### Decision 5: Post-Session Hook (Brain #5 architecture)

**FastAPI `BackgroundTasks.add_task()`** in `/api/tasks/auto` endpoint

**Implementation:**
```python
# apps/api/mastermind_cli/api/routes/tasks.py
@router.post("/auto", response_model=AutoTaskResponse)
async def create_auto_task(
    request: AutoTaskRequest,
    background_tasks: BackgroundTasks,
    ...
) -> AutoTaskResponse:
    # ... existing FlowDetector logic ...

    # NEW: Hook distillation after orchestration completes
    from mastermind_cli.orchestration.distillation_service import KnowledgeDistillationService

    distillation_service = KnowledgeDistillationService(db_path=db_path)
    distillation_task = DistillationTask(
        session_id=task_id,
        brain_ids=detected_flow,
        brief_summary=request.brief[:200],
        execution_start_ms=int(time.time() * 1000),
        ...
    )

    # Fire-and-forget: Non-blocking, executes AFTER user receives 202 response
    background_tasks.add_task(
        distillation_service.trigger_evaluation_and_distillation,
        distillation_task
    )

    return AutoTaskResponse(task_id=task_id, ...)
```

**Why:** Non-blocking — Brain #7 evaluation runs in background. User doesn't wait.

---

### Decision 6: High-Value Detection (Brain #1 criteria)

**Evaluate ONLY high-value sessions** (NOT every session)

**Criteria:**
1. Session duration > 5 minutes (complexity signal)
2. Brain #7's planning score changed during session
3. User invoked `/mm:complete-phase` (vs. `/mm:execute-phase`)

**Implementation:**
```python
# In distillation_service.trigger_evaluation_and_distillation()
high_value = (
    session.duration_ms > 300000  # 5 minutes
    or session.planning_score_delta != 0
    or session.invocation_method == "mm:complete-phase"
)
```

**Why:** Evaluating every session creates systemic noise (Meadows' leverage points). Focus on learning quality.

---

### Decision 7: Relevance Ceiling (Brain #7 systemic risk)

**Implement TTL before Phase 14 ships** (unbounded growth ceiling is BLOCKER)

**Choose ONE:**
- **Option A:** `expires_at` timestamp (auto-expire after 90 days)
- **Option B:** `version_id` (invalidate all records when project major version changes)
- **Option C:** `last_used_at` decay (relevance halves if not retrieved in 30 days)

**Retrieval latency guardrail:**
```python
# In experience routes
P95_RETRIEVAL_LATENCY_MS = 50
CEILING_MS = 200

if measured_p95_latency > CEILING_MS:
    # Stop writing, alert operator
    logger.warning("Retrieval latency ceiling hit. Stop writing.")
    return Response(status_code=503, content="System degraded")
```

**Why:** At 1000+ records, retrieval latency > 200ms → T1 increases, not decreases. Kill switch prevents death spiral.

---

### Decision 8: Dashboard Metrics (Brain #7 system health)

**PRIMARY: System Health (NOT vanity)**

1. **Record count per brain** — Unbounded growth detection
2. **Avg quality_score per brain** — Drift detection
3. **Rejection rate per brain** — Brain degradation detection
4. **P50/P90 retrieval latency** — Ceiling detection
5. **T1 trend over time** — Learning validation

**SECONDARY: Outcome metrics** (from Brain #1)
6. Delta-T1 (Learning Efficiency) — PRIMARY outcome
7. Knowledge Yield (Reuse Rate) — Template viability
8. Planning Accuracy (Brain #7 Quality Score) — Quality guard

**Why:** Dashboard showing "patterns and insights" without system health is vanity metrics graveyard.

---

### Decision 9: Testing Strategy (Brain #6 QA)

**~30-46 new tests** across 3 layers:

**Unit Tests (~3):**
- Delta-velocity calculation formula verification
- Template schema validation
- Aggregation accuracy (sum/avg/min/max)

**Integration Tests (~19-30):**
- Cold vs warm T1 (shadow loop A/B)
- Template instantiation + regression against 631 tests
- Delta-velocity trend, correlation analysis, pattern extraction

**E2E Tests (~8-13):**
- Analytics dashboard smoke test
- Frontend components render charts (Playwright)

**Profitability gate:** If T1_warm > 300s, test FAILS (agent-unprofitable constraint).

---

## BLOCKER Conditions (Must Resolve Before Phase 14 Ships)

### [BLOCKER] Condition 1: Quality Score Calculation

**File:** `apps/api/mastermind_cli/experience/scoring.py`

**Must implement:**
```python
def calculate_quality_score(
    precision: float,  # % actionable
    success_probability: float,
    t1_ms: int,
    tokens: int,
) -> float:
    """Hormozi value equation."""
    base_score = (precision * success_probability) / (t1_ms * tokens)

    # Penalties
    if tokens > 2000 and not has_structure():
        base_score *= 0.5  # Twaddle penalty

    if not can_invert():  # Cannot state "what to avoid"
        base_score *= 0.7  # Inversion check penalty

    return base_score
```

**Verification:** Unit test `test_quality_score_formula` passes.

---

### [BLOCKER] Condition 2: Rejection Logging + Filter

**File:** `apps/api/mastermind_cli/experience/logger.py`

**Must implement:**
```python
# In log_execution()
await self.conn.execute(
    "INSERT INTO experience_records ... status=?, quality_score=?",
    (status, quality_score)  # Explicit rejected tracking
)

# In get_recent_by_brain()
await self.conn.execute(
    "SELECT * FROM experience_records
     WHERE brain_id=?
       AND quality_score >= 1.0
       AND status != 'rejected'
     ORDER BY timestamp DESC
     LIMIT ?",
    (brain_id, limit)
)
```

**Verification:** Integration test `test_rejected_outputs_not_retrieved` passes.

---

### [BLOCKER] Condition 3: Relevance Ceiling

**Schema change:**
```sql
ALTER TABLE experience_records ADD COLUMN expires_at TEXT;
```

**Implementation:**
```python
# In get_recent_by_brain()
WHERE brain_id=?
  AND quality_score >= 1.0
  AND status != 'rejected'
  AND (expires_at IS NULL OR expires_at > datetime('now')  # <-- NEW
```

**Verification:** Integration test `test_expired_records_not_retrieved` passes.

---

### [BLOCKER] Condition 4: High-Value Detection

**File:** `apps/api/mastermind_cli/orchestration/distillation_service.py`

**Must implement:**
```python
def _is_high_value_session(self, task: DistillationTask) -> bool:
    """Determine if session warrants Brain #7 evaluation."""
    duration_sec = (task.execution_end_ms - task.execution_start_ms) / 1000

    return (
        duration_sec > 300  # 5 minutes
        or task.planning_score_delta != 0
        or task.invocation_method == "mm:complete-phase"
    )
```

**Verification:** Unit test `test_high_value_detection` passes.

---

### [CONDITION] Condition 5: Dashboard System Health

**Dashboard must display:**
1. Record count per brain
2. Avg quality_score per brain
3. Rejection rate per brain
4. P50/P90 retrieval latency
5. T1 trend over time

**Verification:** E2E test `test_dashboard_shows_health_metrics` passes.

---

## Open Questions (Resolve During Implementation)

1. **TTL duration:** 90 days? 180 days? (Product decision)
2. **Embedding model:** Which OpenAI model for pgvector? (Backend decision)
3. **Similarity threshold:** What cosine similarity = "same pattern"? (Backend decision)

---

## Next Steps

1. ✅ Brain consultation complete (Moment 2 + 3)
2. ✅ CONTEXT.md written with concrete decisions
3. → **Delegate to `/gsd:plan-phase 14`** for detailed plans
4. → Resolve 4 BLOCKER + 1 CONDITION during implementation
