---
phase: 07-the-nexus
plan: 03
subsystem: ui
tags: [react-flow, zustand, immer, websocket, tdd, vitest, hybrid-flow-edge, cooldown-mode, ghost-trace]

# Dependency graph
requires:
  - phase: 07-the-nexus
    provides: "07-02: NexusCanvas with Ghost Architecture, BrainNode nodrag/nopan, /nexus route"
  - phase: 07-the-nexus
    provides: "07-01: GET /api/tasks/{id}/graph BE-02 compatible, source/target edges"
provides:
  - "brainStore extended: historyStack + sessionInvocationCounts + pushHistorySnapshot + incrementInvocationCount"
  - "HybridFlowEdge: 4-state neon glow edge (idle/active/complete/error) with prefers-reduced-motion guard"
  - "NexusCanvas: EDGE_TYPES at module level, Cooldown Mode on task_completed, CooldownFAB wired"
  - "WSBrainBridge: pushHistorySnapshot + incrementInvocationCount called on every WS brain event"
  - "CommandCenterWrapper: router.push('/nexus') after successful brief submission"
  - "Ghost Trace data structures ready for Phase 08 replay"
affects: [phase-08, frontend-nexus-ws-illumination, ghost-trace-replay]

# Tech tracking
tech-stack:
  added:
    - "immer enableMapSet() — required for Map.get/iteration inside Immer set() callbacks"
  patterns:
    - "enableMapSet() called once at module level in brainStore — enables Map proxy in Immer"
    - "EDGE_TYPES at module level in NexusCanvas — same invariant as NODE_TYPES"
    - "HybridFlowEdge data-latching pattern: reads source brain status via useBrainState(edge.source)"
    - "pushHistorySnapshot() uses new Map(state.brains) — structural copy, not Immer reference"
    - "Cooldown Mode triggered by task_completed WS event — subscribe in useEffect, setCooldownMode(true)"
    - "prefers-reduced-motion: window.matchMedia guard in HybridFlowEdge, conditional on typeof window"

key-files:
  created:
    - apps/web/src/components/nexus/HybridFlowEdge.tsx
  modified:
    - apps/web/src/stores/brainStore.ts
    - apps/web/src/stores/__tests__/brainStore.test.ts
    - apps/web/src/components/nexus/NexusCanvas.tsx
    - apps/web/src/components/nexus/__tests__/BrainNode.test.tsx
    - apps/web/src/components/ws/WSBrainBridge.tsx
    - apps/web/src/components/command-center/CommandCenterWrapper.tsx

key-decisions:
  - "enableMapSet() at module level in brainStore — Immer cannot proxy Map.get() without MapSet plugin; the existing state.brains.set() worked before only because .set() is a write operation that Immer intercepts without the plugin, but new Map(state.brains) (iteration) requires it"
  - "EDGE_TYPES_EXPORT added alongside NODE_TYPES_EXPORT — consistent test isolation pattern, allows future stability assertion for edges without rendering canvas"
  - "router.push in CommandCenterWrapper (not BriefInputModal) — BriefInputModal is a controlled component that delegates to onSubmit prop; navigation belongs in the parent that owns the task creation flow"
  - "HybridFlowEdge complete=latched solid (#64FFDA no animation) distinct from active=animated — data-latching: once brain completes, edge permanently illuminated until Cooldown Esc"

patterns-established:
  - "BrainNode.test.tsx vi.mocked() pattern: vi.mock factory + vi.mocked(brainStore.useBrainState).mockReturnValue() per test — avoids hoisting errors with variable references"
  - "Cooldown Mode subscribe/unsubscribe in NexusCanvas useEffect — [subscribe] dependency, returned cleanup prevents listener leak"
  - "HybridFlowEdge useMemo keyed on sourceState?.status — edge appearance only recomputes when status changes"

requirements-completed: [NEX-02]

# Metrics
duration: 12min
completed: 2026-03-22
---

# Phase 07 Plan 03: The Nexus — WebSocket Illumination Summary

**WS illumination wired end-to-end: HybridFlowEdge 4-state neon glow, brainStore Ghost Trace extensions, Cooldown Mode on task completion, and brief submission navigates to /nexus**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-03-22T16:10:14Z
- **Completed:** 2026-03-22T16:22:00Z
- **Tasks:** 2 (Task 1: brainStore TDD, Task 2: HybridFlowEdge + wiring)
- **Files created:** 1 | **Files modified:** 6

## Accomplishments

- brainStore extended: `historyStack`, `sessionInvocationCounts`, `pushHistorySnapshot()`, `incrementInvocationCount()` — Ghost Trace data structures ready for Phase 08 replay
- `enableMapSet()` from Immer added — fixes silent Map iteration proxy failure in Immer set() callbacks
- HybridFlowEdge: custom React Flow edge with 4-state machine (idle=muted ghost, active=animated neon cyan glow, complete=latched green solid, error=pulsing red-orange dashed)
- EDGE_TYPES at module level in NexusCanvas — same invariant as NODE_TYPES (no `edgeTypes={{` inline)
- WSBrainBridge extended: `pushHistorySnapshot()` and `incrementInvocationCount()` called after every WS brain event
- Cooldown Mode: NexusCanvas subscribes to `task_completed` WS event → `setCooldownMode(true)` → CooldownFAB visible + background shifts to `#111113` + canvas read-only
- CommandCenterWrapper: `router.push('/nexus')` after successful brief submission (closes the submit→Nexus UX loop)
- 21/21 tests passing (nexus __tests__/ + brainStore)

## Task Commits

Each task was committed atomically:

1. **TDD RED: brainStore historyStack + invocationCounts tests** - `daa3fb5` (test)
2. **TDD GREEN: extend brainStore** - `9c86b1c` (feat)
3. **BrainNode blueprint/active tests** - `a26999e` (test)
4. **HybridFlowEdge + WS illumination wiring** - `ed7c47a` (feat)

## Files Created/Modified

- `apps/web/src/stores/brainStore.ts` — enableMapSet(), historyStack, sessionInvocationCounts, pushHistorySnapshot, incrementInvocationCount, JSDoc on useBrainStore + useBrainState
- `apps/web/src/stores/__tests__/brainStore.test.ts` — 5 new tests: snapshot push, snapshot immutability, incrementCount, empty Map init, setState reset
- `apps/web/src/components/nexus/HybridFlowEdge.tsx` — NEW: 4-state edge component, useBrainState(source), getBezierPath + BaseEdge, prefers-reduced-motion guard
- `apps/web/src/components/nexus/NexusCanvas.tsx` — EDGE_TYPES at module level, EDGE_TYPES_EXPORT, buildBlueprintEdges type:'hybridFlow', Cooldown Mode state + subscribe, CooldownFAB wired, canvas background shift
- `apps/web/src/components/nexus/__tests__/BrainNode.test.tsx` — 2 new tests: opacity-20+border-dashed on undefined, ring-2 on active; vi.mocked pattern fix
- `apps/web/src/components/ws/WSBrainBridge.tsx` — pushHistorySnapshot + incrementInvocationCount subscribed, unused BrainEvent import removed
- `apps/web/src/components/command-center/CommandCenterWrapper.tsx` — useRouter import, router.push('/nexus') after wsStore.connect()

## Decisions Made

- **enableMapSet() required:** The existing `state.brains.set()` in `_drainQueue` worked without MapSet plugin because Immer intercepts `.set()` as a mutation operation. However, `new Map(state.brains)` (Map copy/iteration) requires the plugin — this was the root cause of 4 test failures immediately after adding `pushHistorySnapshot`. Added `enableMapSet()` at module level to unblock. Categorized as [Rule 1 - Bug].

- **CommandCenterWrapper vs BriefInputModal for navigation:** The plan said "In BriefInputModal.tsx...navigate to /nexus". But BriefInputModal is a controlled presentational component that only calls `onSubmit(brief)` — it has no knowledge of POST success/failure. Navigation belongs in CommandCenterWrapper where the task creation and WS connection happen. Moving it there is architecturally cleaner and testable.

- **EDGE_TYPES_EXPORT added:** Consistent with NODE_TYPES_EXPORT from Phase 07-02. Enables future test isolation to verify edge types reference stability.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Immer MapSet plugin missing — Map iteration failed in set() callbacks**
- **Found during:** Task 1 TDD GREEN — 4 tests failed immediately after implementing pushHistorySnapshot
- **Issue:** `new Map(state.brains)` inside Immer's `produce()` callback throws `[Immer] The plugin for 'MapSet' has not been loaded`. The existing `state.brains.set()` in `_drainQueue` worked silently without MapSet because Immer handles `.set()` writes differently — but Map iteration/copy requires the plugin.
- **Fix:** Added `import { enableMapSet } from 'immer'` and called `enableMapSet()` at module level in brainStore.ts
- **Files modified:** `apps/web/src/stores/brainStore.ts`
- **Verification:** All 10 brainStore tests pass
- **Committed in:** `9c86b1c` (GREEN commit)

**2. [Rule 1 - Bug] vi.mock hoisting prevented variable reference in factory**
- **Found during:** Task 2 BrainNode.test.tsx — `ReferenceError: Cannot access 'mockUseBrainState' before initialization`
- **Issue:** `vi.mock` is hoisted by Vitest to top of file before variable declarations — referencing `const mockUseBrainState = vi.fn()` inside the factory causes the hoisting error
- **Fix:** Changed to `vi.mock('@/stores/brainStore', () => ({ useBrainState: vi.fn().mockReturnValue(undefined) }))` and used `vi.mocked(brainStore.useBrainState).mockReturnValue()` in `beforeEach`
- **Files modified:** `apps/web/src/components/nexus/__tests__/BrainNode.test.tsx`
- **Verification:** All 6 BrainNode tests pass
- **Committed in:** `a26999e` (test commit)

---

**Total deviations:** 2 auto-fixed (Rule 1 — bugs)
**Pre-existing failures out of scope:** `ClusterGroup.test.tsx` (2), `route.test.ts` (6) — present before this plan, documented in deferred-items

## Next Phase Readiness

- Wave 3 complete: WS illumination wired, edges animate per brain state, Cooldown Mode on task completion
- Awaiting human checkpoint: visual verification of The Nexus screen
- Phase 08 readiness: `historyStack` populated on every WS event — Ghost Trace replay data ready
- BrainNode ×N counter still shows `×0` placeholder — `sessionInvocationCounts` data available but BrainNode doesn't yet read it (intentional — Phase 08 scope or quick follow-up)

---
*Phase: 07-the-nexus*
*Completed: 2026-03-22*

## Self-Check: PASSED

All created files verified:
- FOUND: apps/web/src/components/nexus/HybridFlowEdge.tsx
- FOUND: .planning/phases/07-the-nexus/07-03-SUMMARY.md

All commits verified:
- FOUND: daa3fb5 (TDD RED: brainStore tests)
- FOUND: 9c86b1c (TDD GREEN: brainStore extensions)
- FOUND: a26999e (BrainNode tests)
- FOUND: ed7c47a (HybridFlowEdge + wiring)
