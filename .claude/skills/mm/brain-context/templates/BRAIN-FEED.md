# BRAIN-FEED — [Project Name]

> Living document. Updated after each completed phase.
> Always pass this to brains before querying. It is the accumulated codebase reality.
> Last updated: [DATE] after Phase [N]

---

## Stack (Locked)

| Layer | Library | Version | Notes |
|-------|---------|---------|-------|
| Framework | Next.js | 16.x | App Router, no Pages |
| UI | React | 19.x | Compiler disabled (conflicts with React.memo on RF nodes) |
| Language | TypeScript | 5.x | strict mode |
| Styling | Tailwind CSS | 4.x | CSS-only config, no tailwind.config.js |
| Components | shadcn/ui | Nova preset | OKLCH color system, base-ui |
| State | Zustand | 5.x | + Immer middleware |
| Query | TanStack Query | v5 | staleTime: 30s default |
| Graph | @xyflow/react | v12 | React Flow v12 |
| Auth | jose | latest | Edge Runtime compatible |
| Sanitization | DOMPurify | latest | XSS prevention |
| Package mgr | pnpm | — | Never npm/yarn |
| Python | uv | — | Never pip/poetry |

---

## Architecture Patterns (Invariants)

Patterns proven in production that brains must know:

### State Management
- `Map<brainId, BrainState>` in Zustand — O(1) lookups, Immer for immutable updates
- `useBrainState(id)` targeted selector — prevents cascade re-renders (not `useStore()`)
- RAF batching in `brainStore` (not WS handler) — queues burst events, drains before paint
- WS is a module singleton (`wsDispatcher`) — lazy init inside `connect()` action, `typeof window` guard

### React Flow
- `NODE_TYPES` declared at **module level** (never inline in JSX) — prevents infinite re-render loop
- `EDGE_TYPES` same rule
- dagre layout runs **once** via `useState` initializer — never recalculate on WS updates
- nodes array is layout-only — brain state comes from `brainStore` directly
- React Flow CSS in `globals.css @layer base` — Tailwind 4 silently breaks handles otherwise

### Auth & Security
- JWT verified at Server Components + Route Handlers (not only `proxy.ts`) — CVE-2025-29927 mitigation
- httpOnly cookie storage — XSS defense (not localStorage)
- WS token handoff via `/api/auth/token` endpoint — server-side cookie read, token not in client bundle
- DOMPurify + `html.escape` backend — defense in depth for XSS

### API
- TanStack Query Eager Loading — single query fetches all 24 brains (N+1 prevention)
- Pagination from day one: `page`, `page_size` (default 24, max 100) — Margin of Safety

---

## Implemented Features (What Exists)

Prevents brains from suggesting what's already built:

| Feature | Location | Notes |
|---------|----------|-------|
| Auth flow | `apps/web/src/app/(auth)/login/` | Server Actions, httpOnly cookie |
| JWT verification | `apps/web/src/lib/auth.ts` | jose, Edge Runtime |
| WS infrastructure | `apps/web/src/stores/wsDispatcher.ts` | Module singleton |
| Brain state store | `apps/web/src/stores/brainStore.ts` | Map + Immer + RAF |
| GET /api/brains | `apps/api/.../routes/brains.py` | JWT, pagination, IDOR protection |
| POST /api/tasks | `apps/web/src/app/api/tasks/route.ts` | Creates task, returns taskId |
| Command Center | `apps/web/src/app/command-center/` | BentoGrid, BrainTile, BriefInputModal |

---

## Active Constraints

Hard limits that brains must respect:

- **React Compiler: DISABLED** — double-memoization conflicts with `React.memo` on React Flow nodes
- **No inline NODE_TYPES** — always module level, no exceptions
- **No layout recalculation on WS events** — positions are locked after dagre runs
- **WS updates touch only `data` prop of nodes** — never positions, never topology
- **No `npm` or `pip`** — pnpm for Node, uv for Python

---

## Phase Learnings

### Phase 05 — Foundation, Auth & WS Infrastructure
Key discoveries:
- Vitest over Jest — ESM-native, better Next.js 16 integration
- `cookies()` is async in Next.js 16 — `await cookies()` required
- React Flow CSS in `@layer base` — without this, edge handles break silently
- Zustand RAF batching prevents dropped frames when 24 brains fire simultaneously

### Phase 06 — Command Center
Key discoveries:
- ICE Scoring prevents over-engineering — only implement animations with ICE ≥ 15
- `CLUSTER_CONFIGS` data-driven array — add niches without touching component code
- `websocket-metrics.ts` with `WS_SLOS` — define guardrail metrics before implementing
- TanStack Query `staleTime: 30s` — brains config is stable data, no refetch on focus

---

## Anti-patterns (Tried and Rejected)

| Pattern | Why rejected | What we use instead |
|---------|--------------|---------------------|
| `useStore()` for brain state | Re-renders ALL consumers on ANY brain update | `useBrainState(id)` targeted selector |
| WS reconnect on every render | Creates duplicate connections | Module singleton with ref counting |
| `jwt.verify()` from jsonwebtoken | Not Edge Runtime compatible | `jose` library |
| `localStorage` for JWT | XSS attack vector | httpOnly cookie |
| Inline `NODE_TYPES` in JSX | Infinite re-render loop in React Flow | Module-level constant |
| Recalculate dagre on data update | 60fps violation, layout thrash | Lock positions after first dagre run |
| `tailwind.config.js` | No CSS-only config support in v4 | `@theme` in globals.css |
