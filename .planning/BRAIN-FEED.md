# BRAIN-FEED — MasterMind Framework v2.2

> Living document. Updated after each completed phase.
> Always pass this to brains before querying. It is the accumulated codebase reality.
> Last updated: 2026-03-28 after Phase 09
> ⚠️ Gap: Phase 07 and 08 learnings not yet distilled (frontend UX polish, Strategy Vault, Engine Room)

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

### Brain Agent Architecture (v2.2)
- Brain Bundle = 3-file directory: `brain-NN-domain.md` + `criteria.md` + `warnings.md` — never combine into one file
- `model: inherit` + `mcpServers: notebooklm-mcp` required in all brain agent frontmatter
- `global-protocol.md` is the governance layer — agents read it, never duplicate its constraints inline
- No notebook IDs in agent files — `brain-selection.md` is the single source of truth
- `BRAIN-FEED-NN-domain.md` domain split files do NOT exist yet — Phase 10 creates them
- Brain #7 dispatched AFTER domain brains (#1-#6) always — never in parallel, never without domain context
- Brain #7 uses `[CROSS-DOMAIN REALITY]` block — synthesizes domain outputs, NOT codebase state

### Delta-Velocity Measurement
- Scale: 1=Wrong / 2=Junior / 3=Peer / 4=Senior / 5=Principal
- T1 Profitability Threshold: T1 > 300s = agent-unprofitable (manual is already losing money)
- Pre-migration manual T1 baseline: 210-270s — all profitable, agents reduce margin further
- Frozen Context Block = control variable — same product context, different ticket per baseline
- Measurement anchor commit: `bcfb93803e7ca5ca1c6b99c554fd190c77196f5a` — Phase 11 A/B comparison target

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
| The Nexus (Phase 07) | `apps/web/src/app/nexus/` | NexusCanvas, BrainNode, React Flow DAG |
| Strategy Vault (Phase 08) | `apps/web/src/app/strategy-vault/` | Phase 08 — see git history |
| Engine Room (Phase 08) | `apps/web/src/app/engine-room/` | Phase 08 — see git history |
| Brain Agent Bundles | `.claude/agents/mm/` | 7 brain bundles × 3 files + global-protocol.md (22 files) |
| Baseline anchors | `tests/baselines/` | baseline-schema.md + 5 pre-migration measurement records |

---

## Active Constraints

Hard limits that brains must respect:

- **React Compiler: DISABLED** — double-memoization conflicts with `React.memo` on React Flow nodes
- **No inline NODE_TYPES** — always module level, no exceptions
- **No layout recalculation on WS events** — positions are locked after dagre runs
- **WS updates touch only `data` prop of nodes** — never positions, never topology
- **No `npm` or `pip`** — pnpm for Node, uv for Python
- **Brain #7 dispatch order** — ALWAYS after domain brains complete, never concurrent
- **No notebook IDs in agent files** — decouple via `brain-selection.md`, prevents 7-file re-edit when IDs change
- **Structured output required in all brain agent responses** — free-text prose causes information leaks across multi-brain chains (proven in baseline 04: cascade re-run added 50s to T3)
- **`uv run pytest` must run from `apps/api/`** — running from project root fails with pre-existing `ModuleNotFoundError` for `mastermind_cli`

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

### Phase 07 — The Nexus *(learnings not yet distilled — see git history)*

### Phase 08 — Strategy Vault, Engine Room & UX Polish *(learnings not yet distilled — see git history)*

### Phase 09 — Baselines + Agent Authoring
Key discoveries:
- **Brain Bundle invariant**: 3 files per domain, persona opens verbatim first, 6-step protocol as identity (first-person, not step-list). Deviating from this produces checklists agents optionally follow instead of how they think.
- **`[CORRECTED ASSUMPTIONS]` twice rule**: embed once in protocol section, again in "Always Include" block — redundancy is intentional, prevents the block from being skipped under cognitive load
- **Output Format section is non-negotiable**: without it, free-text prose from domain brains causes cascade errors in Brain #7 (proven: baseline 04 T3 elevated 50s due to re-run caused by imprecise language)
- **Brain #7 `[CROSS-DOMAIN REALITY]` distinction**: it synthesizes domain agent outputs from orchestrator context — it does NOT independently query feeds or re-read codebase state
- **Adversarial baseline delta_velocity=4 signal**: `@xyflow/react v12 nodeInternals` + `IntersectionObserver` was an unprompted architectural insight — genuine Senior output not in the ticket. This is the stretch target for Phase 11 agent comparison.
- **Domain feed paths intentionally broken at Phase 09**: `BRAIN-FEED-NN-domain.md` files referenced in agent Step 1 and Step 6 don't exist yet — Phase 10 creates them. Agents can be authored before their domain feed exists.

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
| Free-text prose in brain output | Information leak across multi-brain chain — Brain #7 receives garbage | Structured Output Format section in every agent |
| Notebook IDs hardcoded in agent files | Re-edit 7 files when IDs change | Reference `brain-selection.md` as single source of truth |
| `BRAIN-FEED-NN-domain.md` created in Phase 09 | Premature — empty files are noise | Phase 10 creates them with proper content |
| Brain #7 dispatched in parallel with domain brains | Evaluates without seeing domain outputs — useless | Always dispatch AFTER domain brains complete |
| `uv run pytest` from project root | `ModuleNotFoundError: mastermind_cli` (pre-existing conftest discovery issue) | `cd apps/api && uv run pytest` |
