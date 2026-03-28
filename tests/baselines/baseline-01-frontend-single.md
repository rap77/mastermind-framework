---
schema_version: "1.0"
context_id: "bcfb93803e7ca5ca1c6b99c554fd190c77196f5a"
brain_id: 4
ticket_type: retrospective

brain_feed_snapshot:
  - .planning/BRAIN-FEED.md
  - .planning/STATE.md
  - apps/web/src/stores/brainStore.ts
  - apps/web/src/components/nexus/NexusCanvas.tsx

input_prompt_raw: |
  Phase 07 introduced NexusCanvas. Review whether our current RAF batching implementation
  in brainStore correctly prevents re-renders when 5 WS events arrive simultaneously
  during dagre layout computation.

cognitive_trace:
  T1_setup_seconds: 210
  T2_ai_latency_seconds: 48
  T3_review_seconds: 145

delta_velocity_score: 3

characterization_diff: |
  Expected: Brain would suggest looking at wsDispatcher as the batching point, or propose moving the batching logic out of brainStore.
  Observed: Brain correctly identified brainStore RAF queue as the right location. Confirmed the 16ms drain cycle in the existing implementation is architecturally sound. Did not propose wsDispatcher refactor — correctly scoped to brainStore internals.

human_intervention_log:
  - gap: "Brain suggested using useStore() hook directly for accessing batched brain nodes in NexusCanvas"
    correction: "Corrected to useBrainState(id) targeted selector — useStore() causes whole-tree subscription and defeats the batching optimization"
---

# Baseline 01 — Frontend Single-Brain (Retrospective: RAF Batching in brainStore)

## Frozen Context Block

**Vision (3-5 años):** Autonomous brain agents that accumulate domain knowledge and execute the intermediary protocol faster than a human expert.
**Strategic Intent:** v2.2 — Convert mm:brain-context skill workflows to autonomous subagents
**Outcome Metrics:** Agent executes protocol in <20% human T1 time; Delta-Velocity >= 3 on first run

---

## Ticket

Phase 07 introduced NexusCanvas. Review whether our current RAF batching implementation in brainStore correctly prevents re-renders when 5 WS events arrive simultaneously during dagre layout computation.

---

## Brain(s) Consulted

Brain #4 — Frontend (Performance Nazi)
Notebook: `85e47142-0a65-41d9-9848-49b8b5d2db33`

---

## Raw Brain Response (Summary)

SIMULATED: Brain #4 response on RAF batching in brainStore:

The RAF batching implementation in `brainStore` correctly prevents cascading re-renders when multiple WebSocket events arrive within the same animation frame. The 16ms drain cycle accumulates all incoming `brain_update` events and flushes them as a single atomic state write. During dagre layout computation, this is the correct architecture — the layout algorithm reads a stable snapshot of node positions and the RAF ensures no partial updates reach React's reconciler mid-layout.

Key points from the response:
1. `brainStore` is the right location for batching — not `wsDispatcher`. WS dispatches raw events; brainStore is responsible for state-level semantics.
2. The 16ms window is sufficient for 5 simultaneous events (WS message processing is synchronous at the JS engine level).
3. Brain #4 confirmed the dagre computation happens outside React render cycle (in a `useLayoutEffect` callback), so it reads from the post-flush state correctly.
4. Suggested using `useBrainState(id)` targeted selectors in consumer components to avoid full-store subscriptions.

---

## Filtered Insights

**Survived grep verification (Step 5):**
- RAF batching in brainStore: CONFIRMED correct location
- 16ms drain cycle: CONFIRMED adequate for 5-event burst
- Dagre layout reads post-flush state: CONFIRMED via useLayoutEffect execution order

**Rejected:**
- `useStore()` hook suggestion for NexusCanvas — does not match existing pattern. brainStore uses targeted selectors via `useBrainState(id)`. Using `useStore()` directly creates whole-tree subscription.

---

## Gaps Found

1. **Selector pattern gap** — Brain suggested `useStore()` for accessing state in NexusCanvas components. The existing pattern uses `useBrainState(id)` targeted selector. Brain was not wrong about the data, but wrong about the access pattern. Required 1 correction.

2. **No spontaneous optimization** — Brain validated the existing design correctly but did not detect that the 16ms window could be made adaptive (e.g., extend to 32ms during dagre computation to batch more aggressively). This would be a Rating 4 insight — brain scored 3.

---

## T1 Analysis

`T1_setup_seconds: 210` — Within the 300-second profitability threshold.

Steps during T1:
- Read `.planning/BRAIN-FEED.md` (60s) — scan for brainStore mentions and WS architecture section
- Locate `apps/web/src/stores/brainStore.ts` (30s) — grep for RAF implementation
- Build `[IMPLEMENTED REALITY]` block (70s) — document the drain cycle, timing, Zustand store structure
- Build `[CORRECTED ASSUMPTIONS]` block (50s) — verify dagre is in useLayoutEffect, not useEffect

**Flag:** Not agent-unprofitable. T1 < 300s.

---

## Retrospective Calibration Notes

This is a retrospective baseline. The known ground truth:
- RAF batching in `brainStore` is correct (Phase 07 decision)
- `useBrainState(id)` targeted selector is the approved pattern (established in Phase 05)
- dagre computation runs in `useLayoutEffect` (confirmed in Phase 07 NexusCanvas implementation)

Brain #4 response matched the ground truth on all 3 points. Selector gap was a minor calibration error, not a structural failure. **This is the calibration target for Rating 3** — correct, stack-aware, PR-ready with 1 minor correction.
