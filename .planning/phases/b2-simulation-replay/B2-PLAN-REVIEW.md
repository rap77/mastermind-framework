# Phase B2 — Plan Review Context
> Generated: 2026-04-16T22:45:00Z
> Iteration: 1
> Purpose: Full context for Brain #7 plan validation

---

[IMPLEMENTED REALITY]

From BRAIN-FEED.md (v2.2 locked stack):
- Frontend: Next.js 16, React 19, TypeScript 5, Tailwind 4, Zustand 5, TanStack Query v5
- Graph: @xyflow/react v12 (React Flow v12)
- State: Map + Immer + RAF pattern proven in brainStore.ts
- Replay infrastructure EXISTS: replayStore.ts (4.3K) with BrainStateReplay, Snapshot, SnapshotMilestone types
- UI component EXISTS: SnapshotScrubber.tsx (8.7K) in Strategy Vault

From Phase B1 (just completed):
- FlowDesignerStore.ts (456 lines) — Zustand + Immer pattern
- FlowDesignerCanvas.tsx — React Flow v12 integration
- flow-serializer.ts — JSON export/import
- All tests passing (660 total)

[PLAN SUMMARIES]

### B2: Simulation & Replay Engine

**What:** Visual replay of past executions with timeline scrubber, node status highlighting, latency on edges, error detection.

**Why:** Debug failed/slow executions visually — unique competitive feature.

**Current state:** 40% built already (replayStore.ts + SnapshotScrubber.tsx exist).

**Files to create:**
1. SimulationCanvas.tsx — reuse Flow Designer canvas with status overlay
2. TimelineScrubber.tsx — extend SnapshotScrubber pattern
3. EventLog.tsx — NEW
4. ReplayControls.tsx — play/pause/reset/speed
5. ErrorSummary.tsx — NEW
6. simulationStore.ts — extend replayStore pattern
7. /simulation route page.tsx — NEW
8. api.ts — ADD simulation endpoints

**Acceptance Criteria:**
- Load execution from execution_history
- Timeline scrubber with play/pause/reset/skip
- Speed selector: 0.5x, 1x, 2x, 5x
- Node status highlighting:
  - Blue glow = running
  - Green border = success
  - Red background + error tooltip = failed
  - Yellow border + "SLOW" badge = latency > threshold
- Edge labels show latency in ms
- Event log filtered to current timestamp
- Error summary: total errors, slow nodes, total execution time
- All components theme-aware (light/dark)
- 8+ unit tests for simulationStore
- 5+ component tests for SimulationCanvas

**Checkpoint B:** Flow Designer + Simulation both functional, all tests green.

[CODE SNIPPETS]

Existing replayStore.ts pattern (4.3K, already works):
```typescript
type BrainStateReplay = Map<string, SnapshotMilestone>
type Snapshot = {
  timestamp: string
  brain_states: Record<string, unknown>
}
type SnapshotMilestone = {
  snapshot: Snapshot
  label: string
}
```

Existing SnapshotScrubber.tsx (8.7K, already works):
- Timeline UI with play/pause
- Timestamp filtering
- Works with Map-based state

FlowDesignerStore.ts (just built in B1):
```typescript
interface FlowDesignerStore {
  nodes: Map<string, FlowNode>
  edges: Map<string, FlowEdge>
  addNode: (node: FlowNode) => void
  // ... Zustand + Immer pattern
}
```

[CODE REALITY — BLOCKERS RESOLVED]

**✅ BLOCKER 1 RESOLVED: graph_snapshot format defined**
- `graph_snapshot` is `dict[str, object]` per Execution model (line 132)
- Format: React Flow v12 compatible structure (from B1 types.ts)
  - nodes: Array<FlowNode> with {id, type, position, data}
  - edges: Array<FlowEdge> with {id, source, target, label}
  - FlowNodeData.status enum: 'idle' | 'running' | 'success' | 'error'
- Transformation step: Parse JSON → FlowDefinition via importFlow()
- Evidence: flow-serializer.ts lines 73-119

**✅ BLOCKER 2 RESOLVED: error detection heuristics defined**
- Error = `brain_outputs[brain_id].status === "error"`
- Timeout = `duration_ms > brain.timeout_ms` (if timeout defined)
- Partial failure = count errors vs total brains
- Evidence: Execution model lines 147-154 (status validation)

**✅ BLOCKER 3 RESOLVED: latency threshold defined**
- Fixed threshold: 1000ms (1 second) for "SLOW" badge
- Dynamic: p95 of all node durations in execution (computed per execution)
- Default: Use fixed 1000ms, allow user adjustment in settings
- Evidence: Industry standard (1s = perceptible delay)

**✅ CONDITION 4 RESOLVED: API endpoints specified**
- NO new endpoint needed
- Extend existing GET /api/executions/{id} (already exists)
- Add `graph_snapshot` field to response (already returned)
- Evidence: executions.py lines 130, 253

[CORRECTED ASSUMPTIONS]

**What Brain #7 might assume wrong:**
1. ❌ "Building from scratch" → 40% already exists (replayStore + SnapshotScrubber)
2. ❌ "Need to invent replay pattern" → Pattern proven in Strategy Vault
3. ❌ "New React Flow integration" → B1 just proved @xyflow/react v12 works
4. ❌ "No theming context" → A1+A2 complete, all components theme-aware

**Dependencies:**
- A2 (UI Redesign) ✅ COMPLETE
- B1 (Flow Designer) ✅ COMPLETE
- No external dependencies beyond stack

[WHAT I NEED]

1. **Planning Fallacy check** — what are we underestimating?
   - Mapping execution_history → FlowDefinition complexity
   - Error detection heuristics (what counts as "failed"?)
   - Performance: replaying large executions (1000+ events)

2. **Omission Bias** — what's missing that will block execution?
   - execution_history schema undefined
   - API endpoints for simulation data not specified
   - "latency threshold" not defined (what ms value?)

3. **Systems Thinking** — what feedback loops between plans?
   - Simulation depends on Flow Designer flow structure (B1)
   - Simulation depends on execution_history schema (undefined)
   - D2 (wiring) needs both B1 + B2 outputs

4. **Over-engineering risk** — what won't be used?
   - 5 speeds (0.5x, 1x, 2x, 5x) — do users need all?
   - ErrorSummary component — redundant with EventLog?

5. **Acceptance criteria quality** — are done criteria verifiable?
   - "latency > threshold" — WHAT threshold?
   - "error detection" — HOW defined?
   - "load execution" — FROM WHERE?

Be specific about WHICH plan and WHICH task.

**Specific concerns for Brain #7:**
- Plan B2.1 (simulationStore): execution_history schema is undefined — 🔴 BLOCKER
- Plan B2.2 (SimulationCanvas): error detection heuristics undefined — 🔴 BLOCKER
- Plan B2.3 (API endpoints): not specified what endpoints to add — 🔴 BLOCKER
- Plan B2.4 (tests): "5+ component tests" vague — what scenarios?

## RESOLUTION — All Blockers Cleared

**Iteration 2:** After codebase investigation, all 3 BLOCKERS resolved:

1. ✅ graph_snapshot format = React Flow v12 FlowDefinition
2. ✅ Error detection = status==="error" OR duration>timeout
3. ✅ Latency threshold = 1000ms fixed (p95 dynamic optional)
4. ✅ API endpoints = extend existing GET /api/executions/{id}

**Updated Verdict:** APPROVED — Proceed to GSD execution

<!-- This file was consumed by Brain #7 (brain-07-growth) -->
