# Phase 14 — Implemented Reality

> Snapshot of codebase BEFORE planning Phase 14

## Experience Logging Infrastructure (EXISTS)

**Location:** `apps/api/mastermind_cli/experience/logger.py`

**Components:**
```python
class ExperienceLogger:
    async def log_execution(
        brain_id: str,
        input_json: dict,
        output_json: dict,
        status: str,  # "success" | "error" | "timeout"
        duration_ms: int | None = None,
        custom_metadata: dict | None = None,
    ) -> str  # returns record_id

    async def get_recent_by_brain(
        brain_id: str,
        limit: int = 10,
    ) -> list[ExperienceRecord]

    async def search_by_trace_context(
        trace_context: str,
    ) -> list[ExperienceRecord]
```

**Database Schema:**
```sql
CREATE TABLE IF NOT EXISTS experience_records (
    id TEXT PRIMARY KEY,  -- UUID
    brain_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,  -- ISO string
    input_json TEXT NOT NULL,  -- JSON
    output_json TEXT NOT NULL,  -- JSON (PII-redacted)
    status TEXT NOT NULL,  -- success|error|timeout
    duration_ms INTEGER,
    trace_context TEXT,
    custom_metadata TEXT,  -- JSONB
    quality_score REAL,

    INDEX idx_experience_brain_timestamp (brain_id, timestamp DESC)
);
```

**Metadata whitelist (searchable):**
- quality_score, user_id, session_id, brain_version, model_version, prompt_version, trace_id, category, priority, tags

## Brain Memory CLI (EXISTS)

**Location:** `apps/api/mastermind_cli/tools/brain_memory.py`

**Usage:**
```bash
# Query recent experiences
python3 apps/api/mastermind_cli/tools/brain_memory.py query --brain-id brain-01-product --limit 5

# Log an experience
python3 apps/api/mastermind_cli/tools/brain_memory.py log \
    --brain-id brain-01-product \
    --input '{"brief": "..."}' \
    --output '{"recommendation": "..."}' \
    --status success
```

## Brain Agents (EXIST - 7 total)

**Location:** `.claude/agents/mm/`

**Structure:**
```
brain-01-product/  ← Product Strategy (Cagan, Torres, Perri)
brain-02-ux/       ← UX Research (Norman, Nielsen)
brain-03-ui/       ← UI Design (Cooper, Wroblewski)
brain-04-frontend/ ← Frontend (Abramov, Markbåge)
brain-05-backend/  ← Backend (Fowler, Evans, Hohpe)
brain-06-qa/       ← QA/DevOps (Humble, Majors)
brain-07-growth/   ← Growth/Data (Balfour, Kohavi, Munger)
```

**Protocol:** All read `.claude/agents/mm/global-protocol.md` (stack hard-lock, architecture constraints)

## Experience Records API (EXISTS)

**Location:** `apps/api/mastermind_cli/api/routes/experiences.py`

**Endpoints:**
```python
GET /api/experiences/{brain_id}  # Get recent by brain_id
```

**Status:** EXISTS but NOT called by brain agents yet. Zero records in production.

## T1 Baseline (KNOWN)

**Pre-migration manual baseline:** 210-270 seconds

**Definition:** Time from user brief to agent completion (human attention time, not wall-clock)

**Profitability threshold:** T1 > 300s = agent-unprofitable vs manual workflow

## Delta-Velocity (CONCEPT, NOT IMPLEMENTED)

**Definition:** Improvement in T1 vs baseline after brains learn from past interactions

**Target:** 210-270s → sub-90s (from Phase 12 context)

**Measurement:** Compare T1 of second consultation (with memory) vs first consultation (cold start)

## Gaps (NOT IMPLEMENTED)

1. **Auto-evaluation loop:** Brain #7 does NOT automatically evaluate every brain output today
2. **Feedback mechanism:** No automatic adjustment of brain memory after evaluation
3. **Delta-velocity tracking:** No T1 comparison before/after learning
4. **Template generation:** No automatic extraction of reusable patterns from successful interactions
5. **Dashboard:** No UI showing patterns, insights, correlations, trends

## Current Brain #7 Role

**Today:** Evaluates domain outputs during phase planning (Moment 2 + Moment 3 in GSD workflow)

**Not today:** Does NOT run after every orchestration session in production

## State Snapshot (2026-04-06)

- ExperienceLogger: ✅ IMPLEMENTED, 0 records
- brain_memory.py CLI: ✅ IMPLEMENTED, unused by brains
- 7 brain agents: ✅ EXIST, don't call ExperienceLogger
- Delta-velocity tracking: ❌ DOES NOT EXIST
- Template auto-generation: ❌ DOES NOT EXIST
- Pattern dashboard: ❌ DOES NOT EXIST
