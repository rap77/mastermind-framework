# Brain #04-Frontend — Warnings & Anti-Patterns

These patterns trigger automatic rejection. When rejecting, cite the source using the Oracle Pattern:

```
Rejected: [specific library or pattern] violates [constraint].
Source: global-protocol.md > [Section] | brain-04-frontend/warnings.md > [pattern name]
```

Generic rejections without source citation = Rating 2 maximum.

---

## Universal BRAIN-FEED Poisoning Patterns

These 4 patterns apply across ALL brain domains. Source: Brain #6 consultation (2026-03-27).

### 1. Stack Hallucination

**Definition:** Brain suggests a library or tool not declared in the root `uv.lock` or `pnpm-lock.yaml`.

**Rule:** `PROHIBITED: Suggesting external dependencies not declared in the root lockfile.`

**Frontend Examples:** Suggesting Redux Toolkit, MobX, Recoil, Jotai, React Query (use TanStack Query — verify name in lock file), SWR, or any state management library not in `pnpm-lock.yaml`. Suggesting a CSS-in-JS library when Tailwind 4 is the ONLY styling layer.

**Rejection format:**
```
Rejected: [library name] is not declared in root pnpm-lock.yaml or uv.lock.
Source: global-protocol.md > Stack Hard-Lock | brain-04-frontend/warnings.md > Stack Hallucination
```

---

### 2. Toil-Inducer

**Definition:** Brain suggests manual steps instead of code — direct DB access, SSH, manual file edits in production.

**Rule:** `ANTI-PATTERN: Any recommendation requiring manual production access is an architecture failure.`

**Rejection format:**
```
Rejected: [manual step] requires manual production access.
Source: global-protocol.md > Cross-Domain Anti-Patterns | brain-04-frontend/warnings.md > Toil-Inducer
```

---

### 3. Security Bypass

**Definition:** Brain suggests hardcoded credentials, plain-text secrets, or disabled authentication — even in test examples or "temporary" configurations.

**Rule:** `BLOCKER: Never suggest hardcoded credentials, not even in test examples.`

**Frontend Examples:** Hardcoding API keys in frontend code. Bypassing the `/api/auth/token` handoff. Storing JWT in localStorage instead of httpOnly cookie. Disabling auth guards "to test the flow."

**Rejection format:**
```
Rejected: hardcoded credentials violates Security Bypass rule.
Source: global-protocol.md > Cross-Domain Anti-Patterns | brain-04-frontend/warnings.md > Security Bypass
```

---

### 4. Legacy Drift

**Definition:** Brain ignores existing tests in `apps/web/` or proposes changes that break existing contracts without a migration plan.

**Rule:** `PROHIBITED: Proposals that invalidate existing test contracts without explicit migration plan.`

**Frontend Examples:** Proposing a store refactor that breaks the 407-test frontend suite. Suggesting a component interface change without addressing existing component tests. Recommending a routing change that invalidates existing route tests.

**Rejection format:**
```
Rejected: [proposal] invalidates existing test contracts without migration plan.
Source: global-protocol.md > Cross-Domain Anti-Patterns | brain-04-frontend/warnings.md > Legacy Drift
```

---

## Domain-Specific Anti-Patterns — Frontend Architecture

### Global Selector

**Definition:** Using `useStore()` or any equivalent non-targeted selector in a component that will re-render on unrelated state changes.

**Rule:** `PROHIBITED. Use useBrainState(id) targeted selector only. O(1) Map lookup, no cascade re-renders.`

**Why:** The `Map<brainId, BrainState>` architecture enables O(1) lookup. `useStore((s) => s.brains)` subscribes the component to every brain state change — at 5 simultaneous brain activations, this causes 5x unnecessary re-renders for every component using the global selector. With 24 possible brains, this scales to O(N) re-renders per event.

**Examples:**
- `const brains = useStore((s) => s.brains)` — subscribes to ALL brain updates
- `const { brains } = useBrainStore()` without selector argument
- Any pattern that doesn't narrow to a specific `brainId`

**Correct pattern:** `const brain = useBrainState(brainId)` — O(1) Map lookup, only re-renders when THIS brain changes.

**Rejection format:**
```
Rejected: useStore() global selector causes cascade re-renders on every brain state change.
Source: global-protocol.md > Stack Hard-Lock | brain-04-frontend/warnings.md > Global Selector
```

---

### Compiler Assumption

**Definition:** Suggesting enabling the React Compiler, removing `React.memo` from React Flow nodes, or relying on automatic memoization from the Compiler.

**Rule:** `BLOCKER. React Compiler DISABLED — conflicts with React.memo on RF nodes. Enabling it causes infinite re-render loop on NexusCanvas.`

**Why:** `@xyflow/react v12` requires manually-memoized custom node components. The React Compiler's automatic memoization conflicts with the manual `React.memo` wrapper — when both exist, the Compiler generates code that invalidates the manual memo, causing React Flow to re-create all nodes on every render. This is a production bug, not a performance issue.

**Evidence:** `next.config.ts` — React Compiler is explicitly disabled. Verify with `grep -r "reactCompiler\|experimental" apps/web/next.config.ts`.

**Examples:**
- "Enable the React Compiler for automatic optimization."
- "Remove React.memo — the Compiler handles this now."
- "Use React Forget to avoid manual memoization."
- Any suggestion that assumes automatic memoization is available.

**Rejection format:**
```
Rejected: React Compiler is DISABLED in next.config.ts — conflicts with React.memo on RF nodes.
Source: global-protocol.md > Stack Hard-Lock | brain-04-frontend/warnings.md > Compiler Assumption
```

---

### Inline NODE_TYPES

**Definition:** Defining the `NODE_TYPES` constant (or equivalent custom node type map) inside a React component function or JSX expression.

**Rule:** `PROHIBITED. Module-level definition only. Inline definition causes React Flow to re-create all nodes on every render — production bug.`

**Why:** `@xyflow/react v12` uses referential equality to detect node type changes. If `NODE_TYPES` is defined inside a component, it gets a new object reference on every render. React Flow interprets this as "all node types changed" and re-creates all nodes — this breaks animations, resets positions, and spikes CPU.

**Examples:**
- `const nodeTypes = { brain: BrainNode }` inside a React component
- `<ReactFlow nodeTypes={{ brain: BrainNode }}>` — inline object literal
- Defining nodeTypes in a `useMemo` (still wrong — `useMemo` doesn't guarantee stable reference across React Flow's internal comparison)

**Correct pattern:**
```typescript
// At module level, OUTSIDE the component:
const NODE_TYPES = { brain: BrainNode } as const

// Inside the component:
<ReactFlow nodeTypes={NODE_TYPES}>
```

**Rejection format:**
```
Rejected: NODE_TYPES must be defined at module level — inline definition causes React Flow node re-creation on every render.
Source: global-protocol.md > Cross-Domain Anti-Patterns | brain-04-frontend/warnings.md > Inline NODE_TYPES
```

---

### Layout Drift

**Definition:** Triggering dagre layout recalculation when WebSocket data events arrive (brain state updates, activations, completions).

**Rule:** `ANTI-PATTERN. Positions locked after initial dagre run. WS events update BrainState data, not node positions.`

**Why:** dagre layout is an expensive computation (O(N log N) for N nodes). WS events arrive at 16ms intervals during active sessions. Recalculating on every WS event = 60 layout computations per second = CPU spike that degrades animation smoothness. The NexusCanvas is designed as a fixed-position graph with dynamic data overlaid — not a live-layout graph.

**Examples:**
- Calling `getLayoutedElements()` in the WS message handler
- Subscribing to `brainState` changes and re-running dagre in a `useEffect`
- Any pattern that moves node positions in response to state updates

**Correct pattern:** dagre runs ONCE on initial load (or on explicit user action). WS events call `updateBrainState(id, newState)` which updates the store but never touches node positions.

---

### Redux Suggestion

**Definition:** Proposing Redux, MobX, Recoil, Jotai, or any state management library other than Zustand 5 + Immer for any state management need.

**Rule:** `PROHIBITED = Stack Hallucination = Rating 1.`

**Why:** The state architecture (Zustand 5 + Immer + `Map<brainId, BrainState>`) is locked by the project. Suggesting an alternative state library signals the brain has hallucinated the stack. This is not a preference — it is a codebase constraint.

**Examples:**
- "Use Redux Toolkit for predictable state management."
- "Consider Jotai for atomic state — it's lighter than Zustand."
- "React Context would work fine here since it's a small component tree."
- Any suggestion framing Zustand as optional or replaceable.

**Rejection format:**
```
Rejected: [library] is PROHIBITED — Zustand 5 + Immer is the ONLY approved state solution.
Source: global-protocol.md > Stack Hard-Lock | brain-04-frontend/warnings.md > Redux Suggestion
```
