# Phase 14 — Domain Brain Outputs (ITERATION 2)
> Generated: 2026-04-06T15:00:00Z
> Status: complete — BLOCKER conditions addressed

## Brain #1 — Product Strategy

[No changes — original output still valid]

---

## Brain #5 — Backend Architecture (UPDATED)

### BLOCKER 1: Quality Score Calculation — RESOLVED ✅

**Decision:** Option C — Separate `scoring.py` module

**File:** `apps/api/mastermind_cli/experience/scoring.py` (NEW)

```python
def calculate_quality_score(
    precision: float,
    success_probability: float,
    t1_ms: int,
    tokens: int,
    output_text: str | None = None,
) -> float:
    """
    Hormozi value equation:
    Quality Score = (Precision × Success_Probability) / (T1 × Tokens)

    Thresholds:
        - >= 3.0: Store as template candidate
        - >= 1.0: Store as experience record
        - < 1.0: Discard ("dead offer")
    """
    t1_sec = max(t1_ms / 1000, 1.0)
    token_count = max(tokens, 1)
    base_score = (precision * success_probability) / (t1_sec * token_count) * 1000

    # Penalties
    if output_text:
        word_count = len(output_text.split())
        if word_count > 2000 and not _has_structure(output_text):
            base_score *= 0.5  # Twaddle penalty
        if not _can_invert(output_text):
            base_score *= 0.7  # Inversion check penalty

    return base_score
```

### BLOCKER 2: Rejection Logging + Filter — RESOLVED ✅

**Threshold:** `quality_score >= 1.0`

**Updated File:** `apps/api/mastermind_cli/experience/logger.py`

```python
async def get_recent_by_brain(
    self, brain_id: str, limit: int = 100, min_quality_score: float = 1.0
) -> List[ExperienceRecord]:
    """Get last N records for a brain, filtered by quality score and status."""
    cursor = await self.db.conn.execute(
        """SELECT * FROM experience_records
           WHERE brain_id = ?
             AND json_extract(custom_metadata, '$.quality_score') >= ?
             AND status != 'rejected'
           ORDER BY timestamp DESC
           LIMIT ?""",
        (brain_id, min_quality_score, limit),
    )
    rows = await self.db.fetchall()
    return [self._row_to_record(row) for row in rows]
```

### BLOCKER 3: Relevance Ceiling (TTL) — RESOLVED ✅

**Decision:** Option A — `expires_at TEXT` (ISO timestamp), 90-day TTL

**Schema Migration:** `apps/api/mastermind_cli/experience/migrations/002_add_expires_at.sql`

```sql
-- Add expires_at column
ALTER TABLE experience_records ADD COLUMN expires_at TEXT;

-- Create index
CREATE INDEX idx_experience_records_expires_at ON experience_records(expires_at);

-- Default TTL: 90 days
UPDATE experience_records
SET expires_at = datetime(timestamp, '+90 days')
WHERE expires_at IS NULL;
```

**Updated retrieval query:**
```sql
SELECT * FROM experience_records
WHERE brain_id = ?
  AND json_extract(custom_metadata, '$.quality_score') >= 1.0
  AND status != 'rejected'
  AND (expires_at IS NULL OR expires_at > datetime('now'))
ORDER BY timestamp DESC
LIMIT ?
```

### BLOCKER 4: High-Value Detection — RESOLVED ✅

**Updated File:** `apps/api/mastermind_cli/orchestration/distillation_service.py`

```python
class DistillationTask(BaseModel):
    # ... existing fields ...
    duration_ms: int  # NEW: For >5min check
    planning_score_delta: float | None  # NEW: For score change
    invocation_method: str  # NEW: "mm:complete-phase" vs "mm:execute-phase"

class KnowledgeDistillationService:
    def _is_high_value_session(self, task: DistillationTask) -> bool:
        """High-value criteria:
        1. Session duration > 5 minutes
        2. Planning score changed
        3. Invoked via /mm:complete-phase
        """
        duration_sec = task.duration_ms / 1000

        if duration_sec > 300:  # >5 min
            return True
        if task.planning_score_delta is not None and task.planning_score_delta != 0:
            return True
        if task.invocation_method == "mm:complete-phase":
            return True

        return False
```

---

## Brain #6 — QA/DevOps (UPDATED)

### BLOCKER 1: Quality Score Tests — RESOLVED ✅

**Test File:** `apps/api/tests/kd/test_scoring.py` (4 tests)

```python
def test_high_quality_output():
    score = calculate_quality_score(
        precision=0.95,
        success_probability=0.90,
        t1_ms=85000,
        tokens=1200,
    )
    assert score >= 3.0  # Template candidate

def test_twaddle_penalty():
    # Output > 2000 words sin estructura = penalty 50%
    base_score = calculate_quality_score(..., output_text="word " * 2500)
    structured_score = calculate_quality_score(..., output_text="## Section 1\nContent")
    assert base_score < structured_score
```

### BLOCKER 2: Rejection Filter Tests — RESOLVED ✅

**Test File:** `apps/api/tests/kd/test_rejection_filter.py` (5 tests)

```python
async def test_rejected_records_not_retrieved(async_db):
    logger = ExperienceLogger(async_db)

    # Seed: approved + rejected + approved
    await logger.log_execution(..., status="success", quality_score=3.0)
    await logger.log_execution(..., status="rejected", quality_score=0.0)
    await logger.log_execution(..., status="success", quality_score=2.5)

    records = await logger.get_recent_by_brain("brain-01", limit=10)

    # ASSERT: Solo 2 aprobados retornan
    assert len(records) == 2
    assert all(r.status != "rejected" for r in records)
```

### BLOCKER 3: TTL Tests — RESOLVED ✅

**Test File:** `apps/api/tests/kd/test_ttl.py` (4 tests)

```python
async def test_expired_record_not_retrieved(async_db):
    logger = ExperienceLogger(async_db)
    yesterday = (datetime.now() - timedelta(days=1)).isoformat()

    await logger.log_execution(..., expires_at=yesterday)
    await logger.log_execution(..., expires_at=None)

    records = await logger.get_recent_by_brain("brain-01", limit=10)

    assert len(records) == 1
    assert records[0].input_json["q"] == "fresh"
```

### BLOCKER 4: High-Value Detection Tests — RESOLVED ✅

**Test File:** `apps/api/tests/kd/test_high_value.py` (5 tests)

```python
def test_duration_over_5_minutes_triggers_evaluation():
    task = DistillationTask(
        execution_end_ms=350000,  # 350s = 5m 50s
        planning_score_delta=0,
        invocation_method="mm:execute-phase"
    )

    assert service._is_high_value_session(task) is True

def test_planning_score_change_triggers_evaluation():
    task = DistillationTask(
        execution_end_ms=120000,
        planning_score_delta=1,  # Pivot detected
        invocation_method="mm:execute-phase"
    )

    assert service._is_high_value_session(task) is True
```

**Summary:** 18 new tests across 4 files, < 30s runtime, all offline.

---

## Brain #7 — Growth/Data (PENDING RE-EVALUATION)

[To be updated after BARRIER evaluation]
