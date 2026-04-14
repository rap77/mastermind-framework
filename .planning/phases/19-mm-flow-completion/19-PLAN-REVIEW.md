# Phase 19 — MM-Flow Completion Plan Review
> Generated: 2026-04-14T13:00:00Z
> Iteration: 1 (FASE 2-4 evaluation — FASE 1 already shipped and UAT verified)
> Purpose: Full context for Brain #7 plan validation
> Scope: FASES 2, 3, 4 only. FASE 1 = DONE (don't re-evaluate)

---

## [IMPLEMENTED REALITY]

### What FASE 1 delivered (VERIFIED via UAT 7/7)
- PostgreSQL `mastermind_bd` running (mastermind-postgres-1)
- 9 audit trail tables applied via `docker/postgres/mm-flow-audit.sql`
- `agent_registry` table created + 7 dev brains seeded (UNIQUE org+project+brain)
- `apps/api/mastermind_cli/mm_flow/` package created:
  - `__init__.py`
  - `config_loader.py` (deep merge, ConfigError, 5 tests passing)
- `.planning/.mm-flow/config.yml` (3 model profiles, 4 routing moments)

### CRITICAL CORRECTION: What the plan calls "existing" that DOES NOT EXIST
The MM-Flow completion plan has a section "Diagnostico - Implementado y funciona" that lists
`.mm-flow/multi_backend_manager.py`, `.mm-flow/state_machine.py`, `.mm-flow/cli/commands.py`, etc.

THESE FILES DO NOT EXIST ON DISK. The `.mm-flow/` directory IS EMPTY.

This means:
- Task 2.1 says "Modificar `cli/commands.py`" — but it MUST BE CREATED from scratch
  - Target path: `apps/api/mastermind_cli/mm_flow/cli.py` (new file in FASE 1 package)
  - `StateMachine` import path: UNCONFIRMED (class may not exist — need to write directly to phase_executions)
- Task 2.2 references replacing a `.mm-flow/brain_router.py` that doesn't exist
  - The real brain_router is at `apps/api/mastermind_cli/orchestrator/brain_router.py`
  - DynamicDispatchEngine and orchestrator brain_router serve DIFFERENT dispatch contexts

### What DOES exist that matters for FASE 2-4

**Python:**
- `apps/api/mastermind_cli/mm_flow/config_loader.py` — `load_config()` ready, FASE 2 depends on it
- `apps/api/mastermind_cli/orchestrator/brain_router.py` — keyword-based router (different domain)
- `apps/api/routers/audit.py` — 13 routes (lines 341-1451), ZERO `get_current_user_any` dependencies
  - Routes: `get_project_timeline`, `get_phase_details`, `record_decision`, `list_decisions`,
    `get_phase_gates`, `list_sessions`, `get_project_metrics`, + 5 more
  - `from fastapi import APIRouter, Query, Path, Depends, HTTPException` already imported
  - `get_current_user_any` is NOT imported — needs to be added
  - Routes use SQLite via `DatabaseConnection` (NOT PostgreSQL)

**TypeScript:**
- `apps/web/src/stores/wsStore.ts` lines 131-164: `CostUpdateEvent` interface exists
  but `callback(data as CostUpdateEvent)` at line 164 is an UNSAFE cast
- CONFLICT: existing `CostUpdateEvent.brainId` is `string`, plan's new schema wants `brain_id: z.number().int()`
- `apps/web/src/types/api.ts`: Zod schemas exist — `CostUpdateEventSchema` does NOT exist yet

**Hooks:**
- `~/.claude/hooks/mm-flow-statusline.js` — 74 lines, FULLY FUNCTIONAL
  Lines 24-43 = context window percentage logic with thresholds (PRESERVE EXACTLY)
  Currently outputs: `model | branch | dirname | context_bar%`
  Target post-extension: adds `| Phase 19 PLANNING | Brain #5 [ACTIVE]`
- `~/.claude/hooks/mm-flow-context-monitor.js` — 191 lines (PostToolUse hook), EXTEND NOT replace

---

## [PLAN SUMMARIES]

### FASE 2 — CLI bridge (Task 2.1, 2.2, 2.3)

Task 2.1: Create `apps/api/mastermind_cli/mm_flow/cli.py` with Click:
- `execute-phase --phase INT --start` writes phase_executions row + runtime-state.json,
  echoes `execution_id:<uuid>`
- `execute-phase --phase INT --complete --commit <hash>` updates row, clears state
- Mutually exclusive guard: start+complete = UsageError
- asyncio.run() wrapper around async DB calls

Task 2.2: Create `apps/api/mastermind_cli/mm_flow/dispatch_engine.py`:
- Pydantic v2 strict models: BrainDispatch, DispatchResult
- DynamicDispatchEngine.dispatch(phase, moment) reads config.yml via load_config()
- _get_brains_from_registry() queries agent_registry in PostgreSQL
- _check_budget() raises BudgetExceededError if >80% consumed
- DISPATCH_ORACLE table for SLI-3 unit tests
- asyncio.wait_for(30.0) for Brain #7 barrier latency (SLI-2)

Task 2.3: Modify `.claude/skills/mm/execute-phase/SKILL.md` and `mm/plan-phase/SKILL.md`:
- Add Bash tool calls at skill start/end for CLI bookends
- Verifiable: `SELECT * FROM phase_executions WHERE phase = 19` returns row

### FASE 3 — Context Persistence (Tasks 3.1-3.4)

Task 3.1: Stop hook split architecture:
- `~/.claude/hooks/mm-flow-stop.js` — thin JS: detects write tool calls in last 10 transcript messages,
  dispatches to `python3 ~/.mm-flow/checkpoint_writer.py` if any found
- `~/.mm-flow/checkpoint_writer.py` — Python lógica real, testeable in CI
- Writes `.planning/SESSION-CHECKPOINT.md` with `saved: false`
- Add to settings.json Stop hooks

Task 3.2: Modify `mm-flow-session-init.js` — stale checkpoint detection (>48h warning)

Task 3.3: EXTEND `mm-flow-context-monitor.js` — scan last 10 messages for write ops,
  inject checkpoint reminder if any found

Task 3.4: context_loader stub stays; fix is skill `/mm:plan-phase` writes CONTEXT.md via mem_search

### FASE 4 — Audit Auth + Missing Pieces (Tasks 4.1, 4.3, 4.4)

Task 4.1 (HIGHEST SECURITY RISK):
- Add `current_user: User = Depends(get_current_user_any)` to all 13 route functions
- 26 tests (13 x 401 without token + 13 x 200 with token)
- AST-based CI gate counts routes without auth, fails if > 0
- Add tests/api/ to level2-tests step in ci.yml
- SLI-5: `grep -c "get_current_user_any" apps/api/routers/audit.py` target: 13

Task 4.3: Create `~/.claude/backends.sh` with credential export functions

Task 4.4: EXTEND mm-flow-statusline.js (preserve lines 24-43):
- Read `.planning/.mm-flow/runtime-state.json` for phase/brain state
- NO DB queries (latency 200-500ms = unacceptable for statusline)
- ANSI color: ACTIVE=green, BARRIER=amber, IDLE=dim, OFFLINE=red

---

## [CODE SNIPPETS]

### config_loader.py (FASE 1 — FASE 2 depends on this)
```
load_config(path) -> MMFlowConfig
BrainRoutingRule: brains=[1,2,3], parallel=True, barrier=[7], blocking=False
VALID_MODEL_KEYS = {"quality", "balanced", "budget"}
```

### audit.py 13 routes confirmed, ZERO auth
```
All 13 routes have only: db_path: str = Depends(get_db_path)
Missing: current_user: User = Depends(get_current_user_any)
get_current_user_any not imported anywhere in the file
```

### wsStore.ts existing CostUpdateEvent (line 135-145)
```typescript
export interface CostUpdateEvent {
  brainId: string        // NOTE: string not number
  totalTokens: number
  totalDuration: number
  totalCost: number
  lastActivityAt: string
  successRate: number
}
// Line 164: callback(data as CostUpdateEvent)  <- unsafe cast
```

### Plan's proposed CostUpdateEventSchema (CONFLICT with existing)
```typescript
// Plan wants this in apps/web/src/types/api.ts:
export const CostUpdateEventSchema = z.object({
  type: z.literal("cost_update"),     // field not in existing interface
  brain_id: z.number().int(),         // CONFLICT: existing uses brainId: string
  tokens_used: z.number().int(),      // CONFLICT: existing uses totalTokens
  model_profile: z.enum([...]),       // CONFLICT: not in existing interface
  execution_id: z.string().uuid(),    // CONFLICT: not in existing interface
})
```

### mm-flow-statusline.js lines 24-43 (PRESERVE)
```javascript
const AUTO_COMPACT_BUFFER_PCT = 16.5;
const usableRemaining = Math.max(0, ((remaining - AUTO_COMPACT_BUFFER_PCT) / (100 - AUTO_COMPACT_BUFFER_PCT)) * 100);
const used = Math.max(0, Math.min(100, Math.round(100 - usableRemaining)));
// Color thresholds: <50=green, <65=amber, <80=orange, >=80=red+blink
```

---

## [CORRECTED ASSUMPTIONS]

1. `.mm-flow/*.py` files exist → WRONG. Directory is EMPTY. CLI created as new mm_flow package files.

2. StateMachine class is importable → UNCONFIRMED. May need to write directly to phase_executions
   table via asyncpg/SQLAlchemy instead of using a StateMachine abstraction.

3. CostUpdateEventSchema should use brain_id:number → CONFLICT with existing brainId:string interface.
   Resolution must be explicit in implementation: either align to existing OR document breaking change.

4. audit.py and phase_executions are on the same DB → FALSE.
   audit.py = SQLite (DatabaseConnection + get_db_path deps)
   phase_executions / agent_registry = PostgreSQL
   FASE 4 auth adds JWT to SQLite-backed routes. FASE 2 dispatch engine queries PostgreSQL.
   Test setup must handle both databases.

5. asyncio.wait_for(30.0) times out Brain #7 → DESIGN CONFUSION.
   Brain #7 is a Claude Code agent invoked via Agent tool in a skill Markdown file.
   Python asyncio.wait_for cannot timeout a Claude agent invocation.
   The 30s timeout only makes sense if DynamicDispatchEngine has an HTTP callback endpoint
   that Brain #7 calls when done — that endpoint is not specified in the plan.

---

## [WHAT I NEED]

1. Planning Fallacy — what are we underestimating?
   - Task 2.1: StateMachine dependency unverified. May require creating minimal DB writer first.
   - Task 4.1: tests/api/conftest.py with auth_headers fixture may not exist. If missing,
     the 26 tests cannot run. This fixture creation is NOT in the task scope.
   - Task 2.2: how does CLI Click app get PostgreSQL connection? Via DATABASE_URL env var?
     This DB connection bootstrapping for CLI context is not specified.

2. Omission Bias — what's missing that will block execution?
   - FASE 2 Task 2.3: Skill files are Markdown executed by Claude. "Adding bash bookends"
     means adding Bash tool call instructions to the SKILL.md prose. The plan doesn't clarify
     how the skill passes EXEC_ID to the completion call (stored in env? in a temp file?).
   - FASE 3 Task 3.1: `~/.mm-flow/checkpoint_writer.py` lives in HOME, not in project git.
     Distribution/installation not specified. First session after checkout = missing file.
   - FASE 4 CI gate: if tests/api/ is added to level2-tests without conftest.py, CI breaks immediately.

3. Systems Thinking — feedback loops between plans?
   - FASE 2 bookends + FASE 3 checkpoint: if --start fails, stop hook writes checkpoint
     with unknown phase state. Independent failure is fine, but stale state may mislead.
   - CostUpdateEventSchema conflict: adding new schema with different field names
     will NOT break subscribeToCostUpdates (it still uses old interface for existing consumers),
     but creates two competing type definitions for the same WS event. Technical debt accumulates.
   - Dual-DB complexity: audit.py (SQLite) + dispatch_engine (PostgreSQL) in same test suite
     requires two DB fixtures. If not explicitly scoped, test setup complexity grows quadratically.

4. Over-engineering risk — what won't be used?
   - asyncio.wait_for(30.0) in DynamicDispatchEngine: Brain #7 is not a Python coroutine.
     This timeout does not protect anything in the current architecture.
   - backends.sh: low ROI, no consumer defined, credentials already managed elsewhere.
   - CostUpdateEventSchema with execution_id + model_profile: these are MM-Flow concepts
     that the existing WS infrastructure (Phase 17, costStore.ts) was not designed for.
     Adding them to the schema risks frontend breakage if the schema replaces the existing type.

5. Acceptance criteria quality — are done criteria verifiable?
   - GOOD: SLI-5 grep count for audit auth (task 4.1)
   - GOOD: SELECT phase_executions for task 2.3
   - GOOD: DISPATCH_ORACLE oracle table for task 2.2
   - WEAK: task 4.4 statusline — no regression test for existing context bar
   - WEAK: task 3.3 PostToolUse extension — no test confirms write-detection logic fires correctly

Verdict: APPROVED | APPROVED_WITH_CONDITIONS | REJECTED_REVISE
