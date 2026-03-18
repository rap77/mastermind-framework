# Project Research Summary

**Project:** MasterMind Framework v2.1 — War Room Frontend
**Domain:** Real-time AI orchestration dashboard (Next.js + React + WebSocket + DAG visualization)
**Researched:** 2026-03-19
**Confidence:** HIGH

## Executive Summary

MasterMind v2.1 is a real-time "war room" frontend layered on top of a production-ready FastAPI backend. The backend (apps/api/) is complete and unchanged — 24 brains with parallel execution (4.65x speedup), WebSocket server, JWT auth, SQLite WAL persistence, and a full REST API. The entire scope of v2.1 is the apps/web/ Next.js 16 frontend replacing the existing Alpine.js/HTMX dashboard. The recommended approach centers on four screens: Command Center (brief input + Bento Grid status tiles), The Nexus (React Flow DAG with live node illumination), Strategy Vault (execution history + brain outputs), and Engine Room (live logs + config). The technology choices — Next.js 16, Tailwind 4, shadcn/ui, Magic UI, @xyflow/react 12, and Zustand 5 — are all verified against current official documentation and form a coherent, non-conflicting stack.

The single most important architectural decision is the WebSocket dispatcher pattern: one module-level Zustand store manages the WS connection, three of the four screens depend on it, and building it wrong means rewriting every real-time feature. Per-brain selectors with Immer and a requestAnimationFrame batching layer for burst events from parallel brain completion are non-negotiable — at 24 brains completing in milliseconds, a naive implementation causes 300-500ms UI freezes. React Flow's performance model requires nodes to read state from the Zustand store directly (not from the React Flow nodes array), with React.memo on every custom node component.

The critical risks are all front-loaded in Phase 1: React Flow CSS must be imported inside `@layer base` in globals.css (not in tsx files) or Tailwind 4 silently kills node handles and edges in production builds; WebSocket initialization must be lazy (not module-level) or Next.js SSR crashes at build time; JWT verification must happen at every protected Server Component and Route Handler (not just proxy.ts) to avoid CVE-2025-29927; and FastAPI CORS must include `allow_credentials=True` for httpOnly cookie auth. Every one of these pitfalls has low recovery cost if caught in Phase 1 and high recovery cost if discovered later during feature work.

---

## Key Findings

### Recommended Stack

The stack is Next.js 16 (App Router, Turbopack default) + React 19.2 + TypeScript 5.9 + Tailwind 4 (CSS-only config, no tailwind.config.js) + shadcn/ui (new-york style, OKLCH colors, tw-animate-css) + @xyflow/react 12 + Zustand 5 + Magic UI. All versions are verified from official release notes as of 2026-03-17. Node.js 20.9+ is a hard minimum — Next.js 16 dropped Node 18.

Tailwind 4 is a breaking change from v3: configuration moves entirely to CSS via `@theme` directives, `tailwindcss-animate` is replaced by `tw-animate-css`, and `@tailwind base/components/utilities` directives are replaced by `@import "tailwindcss"`. Any tutorial or documentation predating Tailwind 4 is wrong in every config detail.

**Core technologies:**
- **Next.js 16 (App Router):** React framework — Turbopack stable, proxy.ts replaces middleware.ts, React 19.2 built-in, Server/Client component split essential for real-time UI
- **Zustand 5:** WebSocket dispatcher + brain state — module-level singleton survives navigation, per-brain selectors with Immer prevent re-render storms, Map-based store critical for 24 independent entities
- **@xyflow/react 12:** DAG visualization — renamed from reactflow, React 19 + Tailwind 4 native support, NodeStatusIndicator built-in for brain state visualization, dagre layout for automatic DAG positioning
- **Magic UI (Tailwind v4 mode):** Animated Bento Grid — copy-paste model via magicui-cli, Framer Motion already in stack via this dependency, zero extra bundle cost
- **shadcn/ui (Tailwind v4 mode):** Component primitives — OKLCH colors, new-york style default, works inside React Flow custom nodes as Client Components

### Expected Features

The MVP is the complete "war room" loop: authenticate → submit brief → watch brains execute in real-time → retrieve outputs. All four screens are P1.

**Must have (table stakes):**
- Auth gate (login page, JWT in httpOnly cookies, proxy.ts route protection)
- WebSocket Dispatcher (Zustand store, single connection, typed event subscriptions, reconnect logic)
- Command Center: Bento Grid with 24 brain status tiles + Raycast-style command input modal (cmdk)
- The Nexus: React Flow DAG with node illumination on WS events via NodeStatusIndicator
- Strategy Vault: execution list with pagination + individual view with accordion brain outputs + react-markdown
- Engine Room: react-logviewer wired to WS log events, filter by brain name and log level

**Should have (competitive differentiators):**
- React Flow edge animation when brain activates (flip `animated: true` on outgoing edges in Zustand)
- Brain group pre-selection in command modal (checkbox grid before submitting brief)
- Engine Room API key management (list/create/revoke)
- Engine Room YAML editor (Monaco + YAML schema validation, save to API)
- Time-to-first-output metric in Command Center
- Bento Grid brain tile click navigates to Strategy Vault filtered to that brain

**Defer (v2.2+):**
- Execution diff view (compare two runs side-by-side)
- Execution replay / time-travel through DAG
- Brain analytics (slowest brains, error rates, token usage)
- Collaborative viewing (multiple users watching same execution)
- SSE streaming of brain outputs token-by-token

### Architecture Approach

The architecture separates concerns into three Zustand stores (wsStore for WS lifecycle + pub/sub, brainStore for brain states with Immer, authStore for token in memory) and a WSBrainBridge component that routes WS events to brainStore with no render output. Server Components handle initial data fetching using httpOnly cookie tokens; Client Components subscribe to Zustand stores. React Flow nodes read brain state from useBrainStore directly — the React Flow nodes array is layout-only and never mutates after initial mount. Token flows from Server Component layout → WSProvider Client Component → wsStore in memory (never from JS reading httpOnly cookies directly).

**Major components:**
1. **proxy.ts** — Route protection (replaces middleware.ts), JWT verification + token refresh on every protected request
2. **useWSStore** — Module-level singleton, WebSocket lifecycle, typed pub/sub listener Map, connect/disconnect/subscribe actions
3. **useBrainStore** — Map<brain_id, BrainState> with Immer middleware, targeted selector `useBrainState(id)` per component
4. **WSBrainBridge** — Invisible bridge component (null render), subscribes to WS events, dispatches to brainStore, mounted once in protected layout
5. **NexusCanvas** — ReactFlow with stable nodes array (layout only), BrainNode reads from brainStore via targeted selector
6. **BrainNode** — React.memo wrapped custom node, reads only its own brain state, `nodrag nopan` on all interactive child elements

**Build order from architecture research:** Login → WebSocket Dispatcher + BrainStore → Command Center (validates WS→BrainStore pipeline with real events) → The Nexus (depends on working WS infrastructure from Command Center) → Strategy Vault + Engine Room (read-only, no new integration patterns).

### Critical Pitfalls

1. **React Flow CSS in wrong location** — Import `@xyflow/react/dist/style.css` inside `@layer base` in globals.css only. Any tsx file import silently breaks handles, edges, and canvas background in Tailwind 4. Catch in Phase 1 with a 2-node smoke test before writing any real component.

2. **WebSocket SSR crash** — Never initialize `new WebSocket()` at module level or store initializer. Use lazy init inside the `connect()` action guarded by `typeof window !== 'undefined'`. Failing this crashes `npm run build` with `ReferenceError: WebSocket is not defined`.

3. **JWT middleware-only auth (CVE-2025-29927)** — Never rely solely on proxy.ts for authentication. Verify JWT independently in every protected Server Component and Route Handler. CVE-2025-29927 allows header forgery to skip middleware entirely on Next.js < 15.2.3. Use Next.js 16 (patched) AND verify at data access point.

4. **Zustand re-render storm on parallel brain burst** — 24 brains completing simultaneously fire 24 `setState` calls outside React 19's synchronous batching scope (async events). Must implement RAF-based message accumulator in ws.onmessage, per-brain selectors, and React.memo on all node/tile components. Retrofitting after Bento Grid is built requires touching every subscriber.

5. **Magic UI installer fails on Tailwind 4** — `ENOENT: tailwind.config.ts not found` on some components. Use latest `npx shadcn@latest` (fix shipped in PR #620), verify keyframes are present in globals.css after each install, manually add missing `@keyframes` for animation components.

---

## Implications for Roadmap

Based on research, 6 suggested phases with clear dependency ordering:

### Phase 1: Frontend Foundation
**Rationale:** All 7 critical pitfalls from PITFALLS.md are Phase 1 concerns. Building on a broken foundation (wrong CSS cascade, SSR-crashing WS, insecure auth) has exponentially increasing recovery cost. This phase establishes infrastructure before any features.
**Delivers:** Next.js 16 app scaffolded with Tailwind 4 + shadcn/ui + Magic UI smoke-tested (one animated Bento component), React Flow CSS verified in prod build, WS singleton SSR-safe (`npm run build` clean), JWT auth architecture (httpOnly cookies + proxy.ts + independent Server Component verification), FastAPI CORS correct with `allow_credentials=True`, login page end-to-end working (cookie set, route protection redirects, token handoff to WSProvider).
**Addresses:** Auth gate table stakes feature; WebSocket Dispatcher infrastructure prerequisite
**Avoids:** Pitfalls 1 (CSS), 2 (Magic UI installer), 4 (WS SSR), 6 (JWT CVE-2025-29927), 7 (CORS + credentials)
**Research flag:** SKIP — all setup steps are documented with official sources and exact commands in STACK.md

### Phase 2: WebSocket Infrastructure + Brain State
**Rationale:** Three of four screens depend on the WebSocket dispatcher. The brainStore with RAF batching and per-brain selectors is the performance foundation. Building this wrong requires rewriting all consumers. Isolated phase ensures the WS→BrainStore pipeline is verified before any UI is built on top.
**Delivers:** useWSStore (module singleton, pub/sub listener Map, reconnect), useBrainStore (Map<id, BrainState> + Immer, targeted selectors), WSBrainBridge (invisible event router), WSProvider layout integration, WS connection proven end-to-end against FastAPI backend with real brain events.
**Uses:** Zustand 5 with Immer middleware, RAF batching pattern
**Avoids:** Pitfall 5 (re-render storm — RAF batching + per-brain Map selectors)
**Research flag:** SKIP — complete architecture with code-level examples in ARCHITECTURE.md, no unknowns

### Phase 3: Command Center
**Rationale:** First user-facing screen; exercises the REST API (brain list, task creation) and validates the WS→BrainStore pipeline with real execution events. Simpler than The Nexus (no React Flow) — proves the state management architecture before adding DAG complexity. Contains the only known backend gap.
**Delivers:** Bento Grid with 24 brain status tiles (Magic UI + per-brain Zustand selectors + status color classes), Raycast-style command input modal (shadcn Command + cmdk + textarea for multi-line brief), brief submission (`POST /api/tasks`), WS connection initiation on task start, time-to-first-output metric.
**Addresses:** Command Center table stakes; differentiator features (animated tiles, command input modal)
**Gap to resolve first:** `GET /api/brains` endpoint is MISSING from the FastAPI backend. The Command Center Bento Grid needs to list all 24 brains. Must be added to apps/api/ (likely from `brain_registry.py`) before Phase 3 can complete.
**Research flag:** NEEDS RESEARCH — verify exact `GET /api/brains` endpoint design; validate Magic UI Bento Grid animation behavior during 24-tile bulk status updates before committing to the animation approach

### Phase 4: The Nexus (DAG Visualization)
**Rationale:** Highest complexity screen — React Flow + Zustand bridge + dagre layout + edge animation. Depends entirely on WS→BrainStore pipeline proven in Phase 2 and validated with real events in Phase 3. The `nodrag/nopan` BaseNode pattern must be established here as the template for all 24 node variants.
**Delivers:** React Flow canvas with dagre layout (run once on mount, positions locked during execution), BrainNode custom component (React.memo, reads from useBrainStore via targeted selector, NodeStatusIndicator for loading/success/error states, `nodrag nopan` on interactive children), edge animation on brain activation (flip `animated: true` on outgoing edges in Zustand), Server Component page fetching `GET /api/tasks/{id}/graph`.
**Avoids:** Pitfall 3 (nodrag/nopan on interactive node children), Pitfall 5 (stable nodes array + external state — nodes array is layout-only, brain state from store)
**Research flag:** NEEDS RESEARCH — validate `GET /api/tasks/{id}/graph` response schema against React Flow's `Node` and `Edge` types; confirm NodeStatusIndicator API in @xyflow/react 12.10.x

### Phase 5: Strategy Vault + Engine Room
**Rationale:** Lowest complexity — Strategy Vault has no WebSocket dependency (reads completed REST data), Engine Room's log viewer wires directly to existing WS log events. Both can be built in parallel. Deferred to last because they deliver no new infrastructure patterns.
**Delivers:** Strategy Vault (execution list with pagination 20/page, individual execution view with accordion brain outputs + react-markdown + memoization, copy-to-clipboard per brain); Engine Room logs (react-logviewer wired to WS log events, filter by brain name + log level, download as .txt).
**Addresses:** Strategy Vault and Engine Room table stakes
**Research flag:** SKIP — react-logviewer and react-markdown patterns are standard and well-documented

### Phase 6: Post-MVP Enhancements (v2.1.x)
**Rationale:** Features validated as "should have" differentiators by FEATURES.md, not blocking the MVP war room concept. Build after the core loop is validated end-to-end.
**Delivers:** Engine Room API key management (list/create/revoke, show once pattern); Engine Room YAML editor (Monaco + YAML schema validation, save to API); brain group pre-selection in command modal; execution diff view in Strategy Vault.
**Research flag:** NEEDS RESEARCH — Monaco editor integration (@monaco-editor/react) in Next.js 16 App Router has known SSR concerns — requires `dynamic(() => import(...), { ssr: false })`, verify no conflicts with App Router streaming before implementation

### Phase Ordering Rationale

- **Foundation before features:** All 7 critical pitfalls are foundational — misconfigured globals.css or module-level WebSocket breaks every feature that follows with difficult-to-diagnose failures
- **WS infrastructure isolated:** The WS→BrainStore pipeline is the dependency of 3/4 screens; proving it in isolation eliminates the risk of discovering fundamental architecture issues during feature work
- **Command Center before Nexus:** Command Center validates the WS→BrainStore pipeline against real events without React Flow complexity; The Nexus's most dangerous pattern (stable nodes array + external state) is only safe to build after WS event flow is confirmed working
- **Vault + Engine Room last:** Both screens consume existing data flows (REST for Vault, WS for Engine Room) — no new integration patterns required, they are safe to build quickly after the infrastructure is proven

### Research Flags

Phases needing deeper research during planning:
- **Phase 3 (Command Center):** `GET /api/brains` API endpoint confirmed MISSING from FastAPI backend. Must be designed, added to apps/api/, and tested before Phase 3 begins. Check `brain_registry.py` as the likely data source.
- **Phase 4 (The Nexus):** Validate `GET /api/tasks/{id}/graph` response schema against React Flow expected Node and Edge types. Confirm NodeStatusIndicator props and behavior in @xyflow/react 12.10.x against actual usage.
- **Phase 6 (Post-MVP):** Monaco editor (@monaco-editor/react) in Next.js 16 App Router — verify SSR handling before committing to implementation approach.

Phases with standard patterns (skip research):
- **Phase 1 (Foundation):** All setup steps documented with official sources and exact CLI commands in STACK.md
- **Phase 2 (WS Infrastructure):** Complete architecture with code-level examples in ARCHITECTURE.md — no unknowns
- **Phase 5 (Vault + Engine Room):** react-logviewer and react-markdown are well-documented; no App Router-specific concerns

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All versions verified from official release notes as of 2026-03-17; Next.js 16, Tailwind 4, shadcn/ui Tailwind v4 mode all have official migration docs; version compatibility matrix explicitly verified |
| Features | HIGH | Backend capabilities verified from existing v2.0 implementation (292 passing tests); frontend features verified against official component docs for React Flow, Magic UI, shadcn/ui |
| Architecture | HIGH | Official Next.js App Router, React Flow state management, and Zustand docs used; specific code patterns verified; proxy.ts breaking change from Next.js 16 official changelog confirmed |
| Pitfalls | HIGH | CVE-2025-29927 is a disclosed CVE; CSS cascade issue from official React Flow Tailwind 4 changelog; Magic UI bug is a resolved GitHub issue (PR #620); WS SSR crash is documented Next.js behavior |

**Overall confidence:** HIGH

### Gaps to Address

- **`GET /api/brains` missing from backend:** The Command Center Bento Grid needs to list all 24 brains. This endpoint does not exist in the current FastAPI API. The `brain_registry.py` file likely contains the data; a new route must be added to apps/api/ before Phase 3 can complete. Scope this as a backend task at the start of Phase 3.

- **`GET /api/tasks/{id}/graph` response schema:** Architecture research confirms the endpoint exists but the exact field names and shape (does it match React Flow's `Node` and `Edge` types directly, or does it require a transformation layer?) needs verification against the actual FastAPI implementation before Phase 4 begins.

- **WS reconnection strategy:** Current WS store design has no exponential backoff on disconnect. Acceptable for v2.1 local dev (tokens last 30 min, tasks typically complete faster). Requires implementation in v2.2 for production. Track as a known limitation in the roadmap.

- **React Compiler + React.memo on React Flow nodes:** Enabling React Compiler (disabled by default in Next.js 16) with React.memo-wrapped React Flow custom nodes may create double-memoization conflicts. Needs validation before enabling. Conservative recommendation: leave React Compiler disabled for v2.1.

---

## Sources

### Primary (HIGH confidence)
- [Next.js 16 release blog](https://nextjs.org/blog/next-16) — Breaking changes, proxy.ts, React 19.2 requirement, Node 20.9 minimum
- [Next.js 16 upgrade guide](https://nextjs.org/docs/app/guides/upgrading/version-16) — proxy.ts, async cookies API, Turbopack default
- [shadcn/ui Tailwind v4 docs](https://ui.shadcn.com/docs/tailwind-v4) — Migration steps, tw-animate-css, OKLCH, new-york style
- [React Flow Tailwind 4 update (Oct 2025)](https://reactflow.dev/whats-new/2025-10-28) — CSS import change, shadcn/ui + React 19 compatibility
- [React Flow state management](https://reactflow.dev/learn/advanced-use/state-management) — Zustand bridge pattern
- [React Flow performance](https://reactflow.dev/learn/advanced-use/performance) — React.memo requirement, node re-render prevention
- [React Flow utility classes](https://reactflow.dev/learn/customization/utility-classes) — nodrag, nopan
- [React Flow NodeStatusIndicator](https://reactflow.dev/ui/components/node-status-indicator) — Built-in status states (loading/success/error/initial)
- [Next.js authentication guide](https://nextjs.org/docs/app/guides/authentication) — httpOnly cookies, Server Actions
- [CVE-2025-29927](https://projectdiscovery.io/blog/nextjs-middleware-authorization-bypass) — Middleware auth bypass disclosure

### Secondary (MEDIUM confidence)
- [Magic UI Tailwind v4 docs](https://v3.magicui.design/docs/tailwind-v4) — Confirmed Tailwind 4 + React 19 support (page rendered via CSS, install details from npm)
- [Zustand WebSocket integration discussion](https://github.com/pmndrs/zustand/discussions/1651) — Single connection + reducer pattern
- [Magic UI Issue #548 / PR #620](https://github.com/magicuidesign/magicui/issues/548) — tailwind.config.ts ENOENT fix
- [React 19 batching for async events](https://codehustle.tech/posts/react-19-features-guide-complete-update/) — Async WS events not auto-batched (multiple sources agree)
- [react-logviewer (melloware)](https://github.com/melloware/react-logviewer) — WS + ANSI + virtual scroll, actively maintained 2025

### Tertiary (LOW confidence)
- React Compiler + React.memo interaction with React Flow nodes — needs validation during build (inference from separate docs, no documented precedent found)

---

*Research completed: 2026-03-19*
*Ready for roadmap: yes*
