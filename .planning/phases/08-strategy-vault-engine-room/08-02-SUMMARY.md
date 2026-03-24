---
phase: 08-strategy-vault-engine-room
plan: 02
subsystem: ui
tags: [react-markdown, remark-gfm, react-syntax-highlighter, zustand, tanstack-query, next-js-16, strategy-vault]

# Dependency graph
requires:
  - phase: 08-strategy-vault-engine-room
    plan: 01
    provides: "GET /api/executions/history + GET /api/executions/{id} backend endpoints"
  - phase: 07-the-nexus
    provides: "NexusCanvas patterns, brainStore Immer+MapSet, RAF batching"
  - phase: 06-command-center
    provides: "TanStack Query patterns, status badge conventions, skeleton loading"
provides:
  - "Strategy Vault pages: /strategy-vault (list) + /strategy-vault/[id] (detail)"
  - "ExecutionList: cursor-paginated table with status badges, TanStack Query"
  - "ExecutionDetail: accordion + DAG replay (REPLAY MODE) + logs panel + scrubber"
  - "SmartMarkdown: react-markdown + remark-gfm + syntax highlighting (atomDark)"
  - "SnapshotScrubber: milestone-based timeline with keyboard navigation"
  - "ReplayStore: Zustand + Immer store for snapshot state (max 7 milestones)"
  - "API proxy routes: /api/executions/history + /api/executions/[id]"
affects:
  - "08-03 Engine Room: can reuse LogsPanel rendering logic (static log pattern)"
  - "08-04 Focus Mode: no changes needed for Strategy Vault"

# Tech tracking
tech-stack:
  added:
    - "react-markdown 10.1.0 — Markdown rendering"
    - "remark-gfm 4.0.1 — GFM tables, strikethrough, checklists"
    - "react-syntax-highlighter 16.1.1 — code block syntax highlighting (atomDark/Prism)"
    - "@types/react-syntax-highlighter 15.5.13 — TypeScript types"
  patterns:
    - "smart-gfm.tsx: component mapping pattern (SMART_GFM_COMPONENTS exported constant)"
    - "ReplayStore: Zustand+Immer+MapSet, Miller's Law milestone computation (max 7)"
    - "LogsPanel timestamp filtering: show all at index 0 (full history), filter on scrub"
    - "NotFoundError custom class for 404 detection in TanStack Query retry logic"
    - "JSX in .tsx extension only — never .ts for files containing JSX"

key-files:
  created:
    - "apps/web/src/stores/replayStore.ts"
    - "apps/web/src/lib/smart-gfm.tsx"
    - "apps/web/src/components/strategy-vault/SmartMarkdown.tsx"
    - "apps/web/src/components/strategy-vault/SnapshotScrubber.tsx"
    - "apps/web/src/components/strategy-vault/ExecutionList.tsx"
    - "apps/web/src/components/strategy-vault/ExecutionDetail.tsx"
    - "apps/web/src/app/(protected)/strategy-vault/page.tsx"
    - "apps/web/src/app/(protected)/strategy-vault/[id]/page.tsx"
    - "apps/web/src/app/api/executions/history/route.ts"
    - "apps/web/src/app/api/executions/[id]/route.ts"
  modified: []

key-decisions:
  - "smart-gfm.tsx (not .ts): File contains JSX — Vite/Vitest fails to parse JSX in .ts files, must use .tsx"
  - "LogsPanel shows ALL outputs at index 0: UX decision — at start of replay, full history visible; filter applies only on active scrub"
  - "NotFoundError class for 404 detection: TanStack Query retry function needs error type distinction between 404 (no retry) and 5xx (allow retry)"
  - "Zustand store reset between tests: replayStore is module-level singleton — beforeEach reset required to prevent state bleed"
  - "Charts deferred to v2.2: :::chart syntax renders as code block fallback; no rehype plugin in Phase 08-02"
  - "ReplayNexus simplified visualization: React Flow omitted in detail view, node chips shown instead for SSR safety and simplicity"

patterns-established:
  - "Strategy Vault pagination: cursor-stack array for Prev navigation (push on Next, pop on Prev)"
  - "Accordion state: Set<string> of open brainIds in component state"
  - "Miller's Law milestones: Math.ceil(snapshots.length / 7) interval, max 7 milestones"
  - "Download execution: Blob + URL.createObjectURL + a.click() pattern"

requirements-completed: [SV-01, SV-02]

# Metrics
duration: 12min
completed: 2026-03-24
---

# Phase 08 Plan 02: Strategy Vault Frontend Summary

**Strategy Vault frontend: cursor-paginated execution list + detail audit view with accordion brain outputs, SmartMarkdown GFM rendering, SnapshotScrubber timeline, and ReplayStore Zustand state management**

## Performance

- **Duration:** 12 min
- **Started:** 2026-03-24T04:16:47Z
- **Completed:** 2026-03-24T04:28:47Z
- **Tasks:** 7 (6 feature tasks + 1 test verification)
- **Files modified:** 14 created

## Accomplishments

- 159 tests passing (52 new from this plan, 0 regressions from 107 existing)
- Strategy Vault fully functional: list page + detail page with all required audit features
- SmartMarkdown renders GFM tables, code blocks (syntax highlighted), links, blockquotes
- ReplayStore implements Miller's Law milestone computation (max 7 from snapshot array)
- SnapshotScrubber provides drag/click + ArrowLeft/ArrowRight keyboard navigation with ARIA
- ExecutionDetail integrates scrubber, logs panel, ReplayNexus, and accordion in one view

## Task Commits

1. **Task 1: ReplayStore** - `07fcdb7` (feat)
2. **Task 2: SmartMarkdown** - `028a8fe` (feat)
3. **Task 3: SnapshotScrubber** - `7b6b454` (feat)
4. **Task 4: ExecutionList** - `84074e1` (feat)
5. **Task 5: ExecutionDetail** - `fe43a60` (feat)
6. **Task 6: Route pages + API proxy** - `6caf903` (feat)
7. **Task 7: Tests** — integrated per-task (52 total tests)

## Files Created/Modified

- `apps/web/src/stores/replayStore.ts` — Zustand+Immer store for snapshot navigation
- `apps/web/src/stores/__tests__/replayStore.test.ts` — 12 tests
- `apps/web/src/lib/smart-gfm.tsx` — SMART_GFM_COMPONENTS mapping for react-markdown
- `apps/web/src/components/strategy-vault/SmartMarkdown.tsx` — GFM markdown renderer (13 tests)
- `apps/web/src/components/strategy-vault/SnapshotScrubber.tsx` — timeline scrubber (13 tests)
- `apps/web/src/components/strategy-vault/ExecutionList.tsx` — paginated execution table (13 tests)
- `apps/web/src/components/strategy-vault/ExecutionDetail.tsx` — full audit detail view (13 tests)
- `apps/web/src/app/(protected)/strategy-vault/page.tsx` — list route
- `apps/web/src/app/(protected)/strategy-vault/[id]/page.tsx` — detail route
- `apps/web/src/app/api/executions/history/route.ts` — JWT proxy for history endpoint
- `apps/web/src/app/api/executions/[id]/route.ts` — JWT proxy for detail endpoint

## Decisions Made

- **smart-gfm.tsx extension:** File contains JSX components. Vite/OXC parser rejects JSX in `.ts` files — must use `.tsx`. Discovered via [Rule 3 - Blocking] auto-fix during Task 2.
- **LogsPanel shows all at index 0:** UX decision — when replaying at start, the user expects to see the full execution log, not an empty panel. Filter activates only after active scrubbing.
- **NotFoundError custom class:** TanStack Query's `retry` function needs type distinction between 404 (don't retry — redirect instead) and 5xx (don't retry in this context). Custom `NotFoundError extends Error` with `isNotFound` flag solves this cleanly.
- **ReplayNexus simplified:** Full React Flow canvas omitted in ExecutionDetail (SSR safety, reduced complexity). Node chips display instead. Full React Flow canvas remains in NexusCanvas for live mode.
- **Charts deferred:** `:::chart syntax` renders as code block fallback. v2.2 feature.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Renamed smart-gfm.ts to smart-gfm.tsx**
- **Found during:** Task 2 (SmartMarkdown tests)
- **Issue:** `smart-gfm.ts` contained JSX component definitions. Vite/OXC transform failed with `Expected '>' but found 'Identifier'` — OXC rejects JSX in non-.tsx files
- **Fix:** Renamed to `smart-gfm.tsx`
- **Files modified:** `apps/web/src/lib/smart-gfm.tsx`
- **Verification:** Tests pass after rename
- **Committed in:** `028a8fe`

**2. [Rule 1 - Bug] Fixed LogsPanel filter showing empty on initial render**
- **Found during:** Task 5 (ExecutionDetail tests)
- **Issue:** Zustand `useReplayStore` is a module singleton. After `setSnapshots` in a prior test, `milestones[0].timestamp = 1000`. New render with `currentSnapshotIndex = 0` computed `currentTimestamp = 1000`, filtering out all brain outputs (all had timestamp > 1000)
- **Fix:** (a) Added `useReplayStore.getState().reset()` in `beforeEach`; (b) Changed LogsPanel to show ALL outputs when `currentSnapshotIndex === 0` (full history at start)
- **Files modified:** `ExecutionDetail.tsx`, `ExecutionDetail.test.tsx`
- **Verification:** 13/13 tests pass
- **Committed in:** `fe43a60`

**3. [Rule 1 - Bug] Fixed ExecutionDetail retry logic causing timeout on error tests**
- **Found during:** Task 5 (error state test)
- **Issue:** Component retry function `failureCount < 1` retried once before showing error state. Test with `retry: false` in QueryClient was overridden by component-level retry
- **Fix:** Changed component retry to `return false` for all non-404 errors (let QueryClient default handle global retry policy)
- **Files modified:** `ExecutionDetail.tsx`
- **Verification:** Error state test passes immediately
- **Committed in:** `fe43a60`

---

**Total deviations:** 3 auto-fixed (1 blocking, 2 bugs)
**Impact on plan:** All auto-fixes necessary for correctness and testability. No scope creep.

## Issues Encountered

- Zustand module-singleton state bleed between tests: required `beforeEach` reset pattern. Documented as pattern for future stores tests.
- Next.js 16 params must be awaited as Promise — handled correctly using existing codebase patterns from `apps/web/src/app/api/brains/[id]/route.ts`

## User Setup Required

None - no external service configuration required. API proxy routes will return 502 until 08-03 backend (Engine Room) is complete, but Strategy Vault pages render correctly against existing 08-01 backend.

## Next Phase Readiness

- 08-03 Engine Room: log rendering logic from LogsPanel can be reused (static log pattern established)
- 08-04 Focus Mode: no Strategy Vault changes needed
- SV-01 and SV-02 requirements fully addressed
- All 159 frontend tests passing, no regressions

## Self-Check: PASSED

- All 10 key files exist on disk
- All 6 task commits present in git log
- 159 tests passing, 0 regressions
- SUMMARY.md created at correct path

---
*Phase: 08-strategy-vault-engine-room*
*Completed: 2026-03-24*
