---
phase: 07-the-nexus
plan: 02
subsystem: ui
tags: [react-flow, dagre, zustand, shadcn, tdd, vitest, ghost-architecture, nexus-canvas]

# Dependency graph
requires:
  - phase: 07-the-nexus
    provides: "07-01: GET /api/tasks/{id}/graph BE-02 compatible, source/target edges"
  - phase: 06-command-center
    provides: "fetchBrains(), Brain type, GET /api/brains endpoint, brainStore + useBrainState(id)"
provides:
  - "NexusCanvas: React Flow canvas with dagre TB layout, NODE_TYPES at module level, Ghost Architecture"
  - "BrainNode: React.memo custom node, nodrag+nopan on button, useBrainState(id) targeted selector"
  - "NodeStatusIndicator: 5-state display (blueprint/idle/active/complete/error) with icon+color pairs"
  - "NodeDetailPanel: shadcn Sheet side panel, live-bound via useBrainState, canvas shrinks 30%"
  - "NexusSkeleton: 24 pulsing cards for loading state, stagger animation"
  - "CooldownFAB: keyboard-first FAB ([Enter]/[V]/[R]/[Esc]) after task completion"
  - "/nexus route: Server Component, Suspense skeleton, Ghost Architecture passed as blueprintBrains"
  - "getLayoutedNodes: exported function for test isolation"
  - "9 tests: 3 layout stability, 4 BrainNode isolation/nodrag/nopan, 2 NODE_TYPES stability"
affects: [07-03, phase-08, frontend-nexus-ws-illumination]

# Tech tracking
tech-stack:
  added:
    - "@dagrejs/dagre ^2.0.4 — dagre TB layout for 24-node star topology"
    - "@types/dagre ^0.7.54 — TypeScript types for dagre"
    - "shadcn sheet (base-ui Dialog) — side panel for NodeDetailPanel"
  patterns:
    - "NODE_TYPES at module level — prevents React Flow canvas remount on render"
    - "dagre layout via useState initializer — runs exactly once at mount, positions latched"
    - "nodes array is layout-only — brain status from brainStore via useBrainState(id)"
    - "Ghost Architecture — blueprint nodes at 20% opacity + dashed border when no active task"
    - "nodrag + nopan on ALL interactive children inside React Flow nodes (NEX-03)"
    - "React.memo on BrainNode + displayName set after memo wrapping"
    - "module-level dagreGraph singleton — reused for position stability across multiple calls"
    - "Server Component + Suspense + force-dynamic for /nexus page"

key-files:
  created:
    - apps/web/src/components/nexus/NexusCanvas.tsx
    - apps/web/src/components/nexus/BrainNode.tsx
    - apps/web/src/components/nexus/NodeStatusIndicator.tsx
    - apps/web/src/components/nexus/NodeDetailPanel.tsx
    - apps/web/src/components/nexus/NexusSkeleton.tsx
    - apps/web/src/components/nexus/CooldownFAB.tsx
    - apps/web/src/app/(protected)/nexus/page.tsx
    - apps/web/src/components/nexus/__tests__/NexusCanvas.test.tsx
    - apps/web/src/components/nexus/__tests__/BrainNode.test.tsx
    - apps/web/src/components/nexus/__tests__/layout.test.ts
    - apps/web/src/components/ui/sheet.tsx
  modified:
    - apps/web/package.json
    - apps/web/pnpm-lock.yaml

key-decisions:
  - "dagreGraph as module-level singleton + clearNode/clearEdge before each call — ensures positional stability across multiple getLayoutedNodes invocations"
  - "NODE_TYPES_EXPORT named export from NexusCanvas — allows test isolation to verify module-level reference without rendering the full canvas"
  - "buildBlueprintNodes passes onSelect via data prop (not nodeData.onSelect directly) — pattern established so Plan 07-03 can extend node data without breaking existing flow"
  - "CooldownFAB [R] disabled with cursor-not-allowed — Day 2 feature placeholder, intentionally non-functional"
  - "NexusSkeleton uses animationDelay stagger capped at 460ms (max 500ms per Brain-03 spec)"

patterns-established:
  - "Ghost Architecture: nodes with undefined brainState render opacity-20 + border-dashed — visual signal of idle canvas"
  - "BrainNode button uses nodrag + nopan to prevent canvas drag events from intercepting click — NEX-03 invariant"
  - "layout.test.ts uses buildTestNodes() with fixed 1 coordinator (brain-08) + 23 satellites — reuse this shape in 07-03 tests"
  - "vi.mock('@xyflow/react') stub pattern in BrainNode.test — avoids canvas/WebGL in jsdom"

requirements-completed: [NEX-01, NEX-03]

# Metrics
duration: 7min
completed: 2026-03-22
---

# Phase 07 Plan 02: The Nexus — NexusCanvas Frontend Summary

**React Flow canvas with 24 ghost brain nodes in dagre TB star topology, NODE_TYPES at module level, BrainNode with nodrag/nopan isolation, and /nexus page with Suspense skeleton**

## Performance

- **Duration:** ~7 min
- **Started:** 2026-03-22T15:59:55Z
- **Completed:** 2026-03-22T16:07:00Z
- **Tasks:** 3 (Task 1: deps+stubs, Task 2: TDD canvas, Task 3: page+FAB)
- **Files created:** 11 | **Files modified:** 2

## Accomplishments

- NexusCanvas with React Flow v12, dagre TB layout, NODE_TYPES at module level (critical invariant), star topology edges, Obsidian #0B0C10 background
- BrainNode: React.memo + useBrainState(id) targeted selector + nodrag/nopan on interactive button (NEX-03 closed)
- Ghost Architecture: 24 blueprint nodes at 20% opacity + dashed border when no active task
- 9/9 tests passing: layout stability (positions non-NaN, stable, coordinator level), BrainNode isolation (nodrag, nopan, onSelect, displayName), NODE_TYPES reference stability
- /nexus route: Server Component, Suspense + NexusSkeleton, CooldownFAB keyboard shortcuts

## Task Commits

Each task was committed atomically:

1. **Task 1: Install deps + test stubs** - `12df0b9` (chore)
2. **TDD RED: Failing layout + BrainNode tests** - `074bddf` (test)
3. **TDD GREEN: NexusCanvas, BrainNode, NodeStatusIndicator, NodeDetailPanel** - `e820c9a` (feat)
4. **Task 3: /nexus page, NexusSkeleton, CooldownFAB, NexusCanvas tests** - `21af423` (feat)

_TDD task had 2 commits: RED (failing tests) then GREEN (implementation)_

## Files Created/Modified

- `apps/web/src/components/nexus/NexusCanvas.tsx` — React Flow canvas, getLayoutedNodes, NODE_TYPES at module level, NODE_TYPES_EXPORT for tests
- `apps/web/src/components/nexus/BrainNode.tsx` — React.memo node, nodrag+nopan button, Ghost Architecture opacity, displayName
- `apps/web/src/components/nexus/NodeStatusIndicator.tsx` — 5-state display with icon+color pairing, motion-reduce guards
- `apps/web/src/components/nexus/NodeDetailPanel.tsx` — shadcn Sheet, live useBrainState binding, canvas shrinks 30%
- `apps/web/src/components/nexus/NexusSkeleton.tsx` — 24 pulsing cards, stagger animation, aria-busy
- `apps/web/src/components/nexus/CooldownFAB.tsx` — keyboard-first FAB, [Enter]/[V]/[R]/[Esc], auto-focus
- `apps/web/src/app/(protected)/nexus/page.tsx` — Server Component, Suspense, force-dynamic
- `apps/web/src/components/ui/sheet.tsx` — shadcn Sheet component (base-ui Dialog)
- `apps/web/src/components/nexus/__tests__/NexusCanvas.test.tsx` — NODE_TYPES stability tests
- `apps/web/src/components/nexus/__tests__/BrainNode.test.tsx` — nodrag/nopan/onSelect/displayName tests
- `apps/web/src/components/nexus/__tests__/layout.test.ts` — dagre position stability tests
- `apps/web/package.json` + `pnpm-lock.yaml` — @dagrejs/dagre + @types/dagre added

## Decisions Made

- **NODE_TYPES_EXPORT named export:** The plan said "confirm by grep that nodeTypes={{ doesn't appear inline". To make the stability assertion testable in Vitest (not just via grep), we export NODE_TYPES as `NODE_TYPES_EXPORT` — allows `Object.is(ref1, ref2)` assertion and BrainNode reference verification. Grep check still passes (no `nodeTypes={{` found).
- **dagreGraph singleton with clear before each call:** The plan said "module-level dagreGraph singleton". Without clearing nodes/edges, repeated calls with same input accumulate stale state. Adding `removeNode`/`removeEdge` before re-registration guarantees stable positions across multiple invocations (tested in layout.test.ts stability test).
- **data as unknown as BrainNodeData:** React Flow's `NodeProps.data` is typed as `Record<string, unknown>` — direct `as BrainNodeData` cast was rejected by TypeScript strict mode. Using `as unknown as BrainNodeData` is idiomatic for this pattern in React Flow v12 custom nodes.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed TypeScript cast for NodeProps.data**
- **Found during:** Task 2 — TypeScript check after NexusCanvas.tsx creation
- **Issue:** `data as BrainNodeData` caused `TS2352: Conversion of type 'Record<string, unknown>' to type 'BrainNodeData'` — React Flow NodeProps.data is typed as `Record<string, unknown>`, not compatible with direct cast
- **Fix:** Changed to `data as unknown as BrainNodeData` — idiomatic two-step cast for React Flow custom nodes
- **Files modified:** `apps/web/src/components/nexus/BrainNode.tsx`
- **Verification:** `pnpm tsc --noEmit` returns clean
- **Committed in:** `e820c9a` (GREEN commit)

**2. [Rule 1 - Bug] Fixed `await import()` inside synchronous test function**
- **Found during:** Task 3 — running NexusCanvas.test.tsx
- **Issue:** `const { BrainNode } = await import('../BrainNode')` inside a sync `it()` callback caused Vite OXC transform error (top-level await not allowed in non-async function)
- **Fix:** Changed `it('...', () => {` to `it('...', async () => {`
- **Files modified:** `apps/web/src/components/nexus/__tests__/NexusCanvas.test.tsx`
- **Verification:** All 2 NexusCanvas tests pass
- **Committed in:** `21af423` (Task 3 commit)

---

**Total deviations:** 2 auto-fixed (Rule 1 — bugs)
**Impact on plan:** Both bugs found during standard TypeScript/test verification. No scope creep. Both necessary for compilation and test execution.

## Issues Encountered

- Task 1 was partially pre-done (dagre deps installed, test stubs created, sheet.tsx installed by WIP commit). Verified state via git diff before committing — deps were modified but uncommitted. Committed cleanly as Task 1.

## Next Phase Readiness

- Wave 2 complete: NexusCanvas renders Ghost Architecture, BrainNode has nodrag/nopan, NodeDetailPanel opens on click
- Ready for 07-03: WS illumination — connect brainStore updates to BrainNode visual state transitions
- brainStore `sessionInvocationCounts` extension needed in 07-03 (placeholder `×0` in BrainNode now)
- CooldownFAB visible prop wired to task_completed WS event in 07-03
- `/nexus` route navigable, requires running FastAPI server for actual brain data

---
*Phase: 07-the-nexus*
*Completed: 2026-03-22*

## Self-Check: PASSED

All created files verified:
- FOUND: apps/web/src/components/nexus/NexusCanvas.tsx
- FOUND: apps/web/src/components/nexus/BrainNode.tsx
- FOUND: apps/web/src/components/nexus/NodeStatusIndicator.tsx
- FOUND: apps/web/src/components/nexus/NodeDetailPanel.tsx
- FOUND: apps/web/src/components/nexus/NexusSkeleton.tsx
- FOUND: apps/web/src/components/nexus/CooldownFAB.tsx
- FOUND: apps/web/src/app/(protected)/nexus/page.tsx
- FOUND: apps/web/src/components/ui/sheet.tsx

All commits verified:
- FOUND: 12df0b9 (Task 1: deps+stubs)
- FOUND: 074bddf (TDD RED)
- FOUND: e820c9a (TDD GREEN)
- FOUND: 21af423 (Task 3)
