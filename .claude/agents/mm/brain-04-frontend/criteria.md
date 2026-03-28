# Brain #04-Frontend — Evaluation Criteria

## Rating 3 (Peer) vs Rating 4 (Senior)

A Rating 3 response is PR-ready with minor tweaks. A Rating 4 response improves the codebase by detecting something not in the ticket. Use this table to distinguish them:

| Attribute | Rating 3 (Peer) | Rating 4 (Senior) |
|-----------|-----------------|-------------------|
| State access | Correct Zustand 5 API usage | Identifies unnecessary re-renders — proposes `useBrainState(id)` selector split with specific component names |
| Performance | Correct React patterns (useMemo, useCallback applied) | Detects MISSING useMemo/useCallback with a specific render budget reason (e.g., "NexusCanvas re-renders 24x per WS burst without this") |
| Async | Correct async/await usage | Identifies RAF batching opportunity or event loop issue before it becomes a production bug — names the specific queue collision |
| WS integration | Correct wsDispatcher usage following existing patterns | Proposes buffering strategy for burst events (e.g., simultaneous brain activations) — quantifies the event rate scenario |
| Architecture | Follows existing patterns (NODE_TYPES at module level, targeted selectors) | Identifies deviation before it becomes technical debt — cites the specific component or hook that sets the precedent |
| Type safety | No TypeScript errors | Identifies implicit `any` risks in WS message handling or store state transitions — proposes discriminated union fix |

## Observable Signal for Rating 4

**The O(1) selector test:** A Rating 4 response uses `useBrainState(id)` with Map lookup AND explains WHY the O(1) access pattern prevents cascade re-renders when any unrelated brain's state changes. A Rating 3 response just uses it correctly without naming the cascade prevention reason.

> Example of Rating 4 observable behavior: "Using `useBrainState(id)` instead of `useStore((s) => s.brains)` means this component only re-renders when brain `id` changes — not when any of the other 6 brains update. At 5 simultaneous brain activations, this reduces NexusCanvas re-renders from O(N*activations) to O(activations)."

## Auto-Reject Conditions

These conditions trigger automatic rejection before the Rating 3 threshold:

**Global Selector (Rating 1 — Stack Lock violation):**
Any suggestion to use `useStore()` or equivalent non-targeted selector = immediate Rating 1.
> `useBrainState(id)` targeted selector is the ONLY valid access pattern. Map lookup is O(1). Non-targeted access causes cascade re-renders on every state change.
> Rejection: `Rejected: useStore() global selector violates Stack Hard-Lock. Source: global-protocol.md > Stack Hard-Lock | brain-04-frontend/warnings.md > Global Selector`

**Redux Suggestion (Rating 1 — Stack Hallucination):**
Any suggestion for Redux, MobX, Recoil, or Jotai for any state management need = automatic Rating 1.
> Rejection: `Rejected: [library] violates Stack Hard-Lock. Source: global-protocol.md > Stack Hard-Lock | brain-04-frontend/warnings.md > Redux Suggestion`

**React Compiler Enabled (Rating 1 — production bug risk):**
Any suggestion to enable the React Compiler or remove `React.memo` from React Flow nodes = automatic Rating 1.
> React Compiler is DISABLED. Enabling it conflicts with manual `React.memo` on RF nodes — causes infinite re-render loop on NexusCanvas.
> Rejection: `Rejected: React Compiler DISABLED in this codebase. Source: global-protocol.md > Stack Hard-Lock | brain-04-frontend/warnings.md > Compiler Assumption`

**Inline NODE_TYPES (Rating 1 — causes production bug):**
Defining NODE_TYPES inside a React component or JSX expression = automatic Rating 1.
> Every render recreates the object reference, forcing React Flow to re-create all nodes. Module level is mandatory.
> Rejection: `Rejected: NODE_TYPES must be at module level. Source: global-protocol.md > Cross-Domain Anti-Patterns | brain-04-frontend/warnings.md > Inline NODE_TYPES`

## Rating 5 Threshold

Rating 5 responses propose a solution that unlocks a downstream roadmap phase:

> Example: Identifies a render optimization opportunity that reduces DOM operations measurably — specifically, a virtualization strategy for NexusCanvas at 50+ nodes using locked `@xyflow/react v12` APIs that reduces DOM node count by 60% and enables Phase 12 parallel dispatch without visual jitter.

The Rating 5 signal is: "This response contained information that changed what we plan for Phase N+1."

## Profitability Gate

T1 (context setup time) < 300 seconds (5 minutes). If context setup takes longer than 5 minutes, the agent is not profitable versus the manual mm:brain-context skill.

Flag any baseline where T1 > 300s as "agent-unprofitable" — these identify automation candidates for future phases.
