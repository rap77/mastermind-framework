---
phase: 14-knowledge-distillation
plan: 02
title: "Wire Post-Session Auto-Evaluation Loop with High-Value Detection"
completed_date: "2026-04-06"
status: complete
subsystem: orchestration
tags: [knowledge-distillation, brain-7, background-tasks, tdd]
depends_on: ["14-01"]
provides:
  - "KnowledgeDistillationService for high-value detection"
  - "DistillationTask model for session metadata"
  - "AgentRunner wrapper for T1 tracking"
  - "BackgroundTasks hook in /api/tasks/auto"
affects:
  - "POST /api/tasks/auto endpoint (non-blocking distillation hook)"
  - "experience_records table (evaluation triggers logged)"
tech_stack:
  added:
    - "KnowledgeDistillationService (orchestration/distillation_service.py)"
    - "DistillationTask Pydantic model"
    - "AgentRunner wrapper (orchestration/agent_runner.py)"
  patterns:
    - "Fire-and-forget BackgroundTasks pattern (non-blocking)"
    - "TDD workflow (RED → GREEN → commit)"
    - "High-value detection: duration > 5min OR planning_score_changed OR mm:complete-phase"
key_files:
  created:
    - "apps/api/mastermind_cli/orchestration/distillation_service.py"
    - "apps/api/mastermind_cli/orchestration/agent_runner.py"
    - "apps/api/tests/kd/test_high_value.py"
  modified:
    - "apps/api/mastermind_cli/api/routes/tasks.py"
decisions:
  - "Post-session hook uses fire-and-forget pattern (non-blocking via FastAPI BackgroundTasks)"
  - "High-value criteria: duration > 5min OR planning_score_delta != 0 OR invocation_method == 'mm:complete-phase'"
  - "DistillationTask captures execution_start_ms, execution_end_ms, planning_score_delta, invocation_method"
  - "AgentRunner provides interface for T1 tracking (integration deferred to future phases)"
  - "Brain #7 evaluation NOT implemented in this plan (deferred to 14-03) - only hook established"
metrics:
  duration: "15 minutes"
  tasks_completed: "3/3 (100%)"
  tests_added: 8
  tests_passing: 658
  tests_failing: 0
  commits: 3
---

# Phase 14 Plan 02: Wire Post-Session Auto-Evaluation Loop with High-Value Detection Summary

**One-liner:** Post-session auto-evaluation loop with fire-and-forget BackgroundTasks hook, high-value detection (duration > 5min OR planning_score_changed OR mm:complete-phase), DistillationTask model, and AgentRunner wrapper for T1 tracking.

## Objective

Enable Brain #7 to automatically evaluate every high-value orchestration session and adjust brain memory. This creates the learning loop where brains improve over time through feedback (KD-01). The hook runs non-blocking via FastAPI BackgroundTasks, so users don't wait for evaluation.

## What Was Built

### 1. KnowledgeDistillationService (distillation_service.py)

**High-Value Detection Criteria (Brain #7 conditions):**
- Session duration > 5 minutes (300000ms)
- Planning score changed (planning_score_delta != 0)
- Invoked via `/mm:complete-phase` (explicit completion)

**Key Methods:**
- `_is_high_value_session(task: DistillationTask) -> bool`: Evaluates session against high-value criteria
- `trigger_evaluation_and_distillation(task: DistillationTask) -> None`: Post-session hook (async, fire-and-forget)
- Lazy database connection via `_get_db()`

**Current Behavior (Plan 14-02):**
- Logs evaluation trigger to `experience_records` table
- Does NOT call Brain #7 agent yet (deferred to Plan 14-03)

### 2. DistillationTask Model

**Pydantic model capturing session metadata:**
```python
class DistillationTask(BaseModel):
    session_id: str
    brain_ids: list[str]
    brief_summary: str
    execution_start_ms: int
    execution_end_ms: int
    planning_score_delta: Optional[float] = None
    invocation_method: str  # "mm:execute-phase" | "mm:complete-phase"
    user_id: Optional[str] = None
```

### 3. BackgroundTasks Hook (tasks.py)

**Modified `/api/tasks/auto` endpoint:**
```python
# Fire-and-forget: Non-blocking, executes AFTER user receives 202 response
background_tasks.add_task(
    distillation_service.trigger_evaluation_and_distillation,
    distillation_task,
)
```

**Key Design Decision:**
- User receives 202 Accepted immediately
- Distillation runs in background after response
- Non-blocking (doesn't affect user experience)

### 4. AgentRunner Wrapper (agent_runner.py)

**Session metadata capture interface:**
```python
runner = AgentRunner(session_id="task-123")
runner.start_execution()
# ... run brain orchestration ...
runner.end_execution()

distillation_task = runner.to_distillation_task(
    brain_ids=["brain-01-product"],
    brief_summary="Implement feature X",
    invocation_method="mm:execute-phase",
    user_id="user-123",
)
```

**Properties:**
- `duration_ms`: Session duration (end - start)
- `planning_score_delta`: Score change (after - before)
- `to_distillation_task()`: Converts to DistillationTask for post-session evaluation

**Integration Note:** AgentRunner NOT integrated into StatelessCoordinator in this plan (deferred to future phases when T1 tracking is implemented).

## Tests

### TDD Workflow (Task 1)

**RED Phase:** Created 5 failing tests for DistillationTask + high-value detection
**GREEN Phase:** Implemented KnowledgeDistillationService with all tests passing

**Test Coverage (8 tests total):**
1. ✅ DistillationTask model validates required fields
2. ✅ DistillationTask accepts optional fields
3. ✅ High-value when duration > 5 minutes (300000ms)
4. ✅ High-value when planning_score_delta != 0
5. ✅ High-value when invocation_method == "mm:complete-phase"
6. ✅ Returns False for short sessions with no changes
7. ✅ Edge case: Exactly 5 minutes is NOT high-value (must be > 5min)
8. ✅ Negative planning_score_delta (decrease) still counts as change

**Coverage:** `distillation_service.py` 71%, `agent_runner.py` not covered (interface only, no integration yet)

### Verification Results

**New Tests:** 8 passing (5 required + 3 edge cases)
**Existing Tests:** 658 passing, 11 skipped (0 failures)
**Zero Regressions:** All 631 backend tests still pass

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| 1 | `08c4102` | TDD: RED + GREEN for distillation service (8 tests) |
| 2 | `f026dfd` | Wire BackgroundTasks hook in /api/tasks/auto endpoint |
| 3 | `6b6ec46` | Create AgentRunner wrapper for session metadata capture |

## Deviations from Plan

**None** - Plan executed exactly as written.

## Brain #7 Conditions Applied

✅ **BackgroundTasks hook uses fire-and-forget pattern (non-blocking)**
- User receives 202 Accepted immediately
- Distillation runs in background after response

✅ **High-value detection implemented:**
- duration > 5min (300000ms)
- planning_score_changed (delta != 0)
- mm:complete-phase invocation

✅ **Manual quality_score seeding (from Plan 14-01):**
- success: 2.0
- timeout: 0.5
- failure: 0.0

**Deferred to Plan 14-03:**
- Actual Brain #7 agent call (only logging in this plan)
- Template extraction from high-value sessions
- Brain memory adjustment based on evaluation

## Technical Decisions

### 1. Fire-and-Forget Pattern

**Decision:** Use FastAPI BackgroundTasks for non-blocking post-session evaluation.

**Rationale:**
- User shouldn't wait for Brain #7 evaluation
- 202 Accepted response returned immediately
- Distillation executes in background after response

**Trade-off:** If distillation fails, user won't see error (acceptable for evaluation use case).

### 2. High-Value Detection Criteria

**Decision:** Three criteria (OR logic):
1. Long-running sessions (> 5 minutes)
2. Planning score changed (pivot detected)
3. Explicit phase completion (mm:complete-phase)

**Rationale:**
- Avoid noise from quick, low-value sessions
- Capture strategic pivots (score changes)
- Respect explicit completion requests

**Brain #7 Rationale:** Brain #7 should focus on high-leverage learning moments, not every session.

### 3. AgentRunner Wrapper Interface

**Decision:** Create AgentRunner wrapper without integrating into StatelessCoordinator.

**Rationale:**
- Plan 14-02 establishes the interface
- Integration deferred to future phases when T1 tracking is implemented
- Avoids premature optimization

**Future Work:** Integrate AgentRunner into StatelessCoordinator to capture actual session metrics.

### 4. TYPE_CHECKING Import

**Decision:** Use `TYPE_CHECKING` to import DistillationTask for type hints without circular dependency.

**Rationale:**
- AgentRunner needs DistillationTask type hint
- DistillationService imports from AgentRunner in future plans
- TYPE_CHECKING allows type hints without runtime import

## Next Steps

**Plan 14-03:** Implement Brain #7 evaluation call in `trigger_evaluation_and_distillation()`
**Plan 14-04:** Extract templates from high-value sessions and store in brain memory

## Self-Check: PASSED

**Created Files:**
- ✅ `apps/api/mastermind_cli/orchestration/distillation_service.py` (112 lines)
- ✅ `apps/api/mastermind_cli/orchestration/agent_runner.py` (126 lines)
- ✅ `apps/api/tests/kd/test_high_value.py` (149 lines, 8 tests)

**Modified Files:**
- ✅ `apps/api/mastermind_cli/api/routes/tasks.py` (+25 lines, BackgroundTasks hook)

**Commits Exist:**
- ✅ `08c4102` (Task 1)
- ✅ `f026dfd` (Task 2)
- ✅ `6b6ec46` (Task 3)

**Tests Passing:**
- ✅ 8 new tests (high-value detection)
- ✅ 658 existing tests (zero regressions)
