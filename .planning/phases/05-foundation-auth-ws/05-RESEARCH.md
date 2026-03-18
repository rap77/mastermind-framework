# Phase 05: Foundation, Auth & WebSocket Infrastructure - Research

**Researched:** 2026-03-18
**Domain:** Next.js 16 App Router + JWT auth + WebSocket dispatcher + Zustand state
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md — Brain-04 frontend expert)

### Locked Decisions
- Framework: Next.js 16 + React 19, App Router, RSC default
- State: Zustand 5 — wsStore (module singleton) + brainStore (Map<brainId,BrainState> + Immer)
- Auth: JWT stored as httpOnly cookie (mitigates XSS vs localStorage)
- Auth architecture: JWT verified at AuthGuardLayout (Server Component) AND proxy.ts — NOT only proxy.ts (CVE-2025-29927)
- WS init: Lazy inside connect() action guarded by `typeof window !== 'undefined'` — NEVER module-level
- React Flow CSS: `@xyflow/react/dist/style.css` inside `@layer base` in globals.css only — never tsx import
- RAF batching: Lives in brainStore, not in WS event handler directly
- WSBrainBridge: Validates with Zod BEFORE updating Zustand — schema bridge and WS store are one integrated piece
- Styling: Tailwind 4 (CSS-only config, no tailwind.config.js) + shadcn/ui (new-york, OKLCH) + Magic UI
- Package manager: pnpm always for Node.js — npm/yarn prohibited
- React Compiler: Disabled for v2.1 — double-memoization conflicts with React.memo on React Flow nodes unvalidated

### Claude's Discretion
- Exact file/folder naming within Next.js conventions
- Error boundary placement and granularity
- TypeScript strictness settings in tsconfig.json
- ESLint flat config rule selection
- Zod schema generator implementation approach (script vs build-time)
- Smoke test component choice for Magic UI animation verification

### Deferred Ideas (OUT OF SCOPE)
- WS reconnection with exponential backoff (deferred to v2.2)
- React Compiler enablement (deferred until React Flow double-memoization validated)
- SSE streaming of brain outputs token-by-token (v2.2+)
- Mobile responsive layout (v2.2)
- WebSocket reconnection strategy (v2.2)
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| FND-01 | Developer can initialize apps/web/ with Next.js 16, Tailwind 4, shadcn/ui (new-york), and Magic UI — React Flow CSS loads correctly without style conflicts, Magic UI @keyframes animations verified working after install | Scaffold commands verified; CSS layer ordering documented; Magic UI ENOENT fix identified |
| FND-02 | User can authenticate via login page with JWT stored as httpOnly cookie (proxy.ts route protection, CVE-2025-29927 mitigated) | Auth flow fully documented from FastAPI backend analysis; cookie storage pattern verified |
| FND-03 | User is redirected to login when accessing any protected route without a valid JWT | AuthGuardLayout as Server Component + proxy.ts dual-layer pattern documented |
| FND-04 | Frontend connects to FastAPI WebSocket at api:8000 directly from the browser without CORS errors (Docker networking confirmed) | CORS config verified in app.py: allow_credentials=True already set; docker-compose port mapping confirmed |
| SB-01 | Developer can run a schema generator script that produces Zod types from Pydantic models in apps/api/ and outputs them to apps/web/src/types/api.ts | Pydantic models analyzed; generator script approach documented; Zod 4 patterns established |
| WS-01 | WebSocket connection established once per session, survives client-side route changes | wsStore singleton pattern with module-level store, lazy init inside connect() documented |
| WS-02 | UI remains responsive at 60fps when 24 brains fire events simultaneously | RAF batching pattern for brainStore documented; existing WS throttling (300ms) confirmed in backend |
| WS-03 | Each brain tile and node updates independently via targeted Map<brainId, BrainState> selectors — no cascade re-renders | Map<brainId, BrainState> + useBrainState(id) targeted selector pattern documented |
</phase_requirements>

---

## Summary

Phase 05 lays the infrastructure that every subsequent phase builds on. The FastAPI backend (apps/api/) is fully operational — JWT auth, WebSocket server with 300ms throttled broadcasting, CORS with `allow_credentials=True` already configured. The entire scope of this phase is creating apps/web/ from zero: scaffold → auth → WS pipeline proven end-to-end.

The three plans map cleanly to three isolated concerns: (1) scaffolding and smoke-testing the CSS layer ordering before writing any component, (2) auth gate with dual-layer JWT verification, and (3) WS→BrainStore pipeline with RAF batching. Every critical pitfall in this phase is known and documented — none require research during execution.

**Primary recommendation:** Execute plans strictly in order (scaffold → auth → WS). Do not start Plan 05-03 until `npm run build` is clean after Plan 05-01 and auth redirects work correctly after Plan 05-02. The WS pipeline proof requires a running FastAPI instance via `docker compose up -d`.

---

## Backend Analysis (Verified from Source)

This section documents the FastAPI backend capabilities that the frontend must integrate against. All findings are from direct source inspection — not assumptions.

### Authentication Endpoints (verified from apps/api/mastermind_cli/api/routes/auth.py)

| Endpoint | Method | Auth Required | Response |
|----------|--------|---------------|----------|
| `/api/auth/login` | POST | None | `{ access_token, refresh_token, token_type, expires_in }` |
| `/api/auth/refresh` | POST | None (refresh_token in body) | `{ access_token, refresh_token, token_type, expires_in }` |
| `/api/auth/logout` | POST | JWT or API key | `{ message }` |
| `/api/auth/api-keys` | POST | JWT or API key | `{ id, name, key, created_at }` |
| `/api/auth/api-keys` | GET | JWT or API key | `{ api_keys: [...] }` |
| `/api/auth/api-keys/{id}` | DELETE | JWT or API key | `{ message }` |

**Token specs:**
- Access token: JWT HS256, expires in 1800s (30 min), payload `{ sub: user_id, exp, type: "access", jti }`
- Refresh token: JWT HS256, expires in 24h, payload `{ sub: user_id, exp, type: "refresh", jti }`
- JWT secret: `MM_SECRET_KEY` env var (default: `"your-secret-key-change-in-production"` — must match docker-compose)
- API key format: `mm_` + 32 hex chars (CLI format; web uses JWT only)

**LoginRequest schema (for Zod bridge):**
```python
username: str (min_length=1, max_length=100)
password: str (min_length=1, max_length=100)
```

**TokenResponse schema (for Zod bridge):**
```python
access_token: str
refresh_token: str
token_type: str = "Bearer"
expires_in: int = 1800
```

### WebSocket Endpoint (verified from apps/api/mastermind_cli/api/websocket.py)

- **URL:** `ws://localhost:8000/ws/tasks/{task_id}?token={jwt_access_token}`
- **Auth:** JWT or API key passed as `token` query param
- **Server → Client message shape:** `{ type: "task_update_batch", data: [update_data, ...] }`
- **Throttling:** 300ms batch interval (ThrottledBroadcaster already implemented)
- **Ghost Mode buffer:** Last 100 events per task buffered for reconnect resync
- **Current limitation:** WS endpoint is task-scoped (`/ws/tasks/{task_id}`) — frontend must connect once a task is created, not a global session connection

**CRITICAL INSIGHT:** The existing WS endpoint is task-scoped, not session-scoped. WS-01 requirement ("established once per session") means the wsStore must manage a task-specific connection that persists across client-side route changes without reconnecting. The wsStore reconnects only when the active task changes, not when navigating between screens.

### CORS Configuration (verified from apps/api/mastermind_cli/api/app.py)

```python
CORSMiddleware(
    allow_origins=["*"],    # All origins — FND-04 is satisfied
    allow_credentials=True, # Required for httpOnly cookie auth
    allow_methods=["*"],
    allow_headers=["*"],
)
```

`allow_credentials=True` is already set. FND-04 (CORS errors) is already resolved server-side — no backend changes needed.

### Brain Registry (verified from brain_registry.py + config/brains.yaml)

Brains are loaded from `config/brains.yaml`. Each brain has: `id`, `niche`, `name`, `short_id`, `notebook_id`, `system_prompt`, `expertise[]`, `status`. The `GET /api/brains` endpoint does NOT exist yet — that is Phase 6 scope (BE-01). Phase 05 does NOT need it.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Next.js | 16.x | React framework + App Router | proxy.ts (replaces middleware.ts), React 19.2 built-in, Turbopack default |
| React | 19.2 | UI runtime | Concurrent features, auto-batching in sync scope, useTransition |
| TypeScript | 5.9 | Type safety | Strict mode, no `any`, Zod inference integration |
| Tailwind CSS | 4.x | Utility CSS | CSS-only config (no tailwind.config.js), `@import "tailwindcss"` in globals.css |
| shadcn/ui | latest (Tailwind v4 mode) | Component primitives | OKLCH colors, new-york style, tw-animate-css replaces tailwindcss-animate |
| Zustand | 5.x | Global state | Module-level singleton, no Provider needed, Immer middleware |
| Zod | 4.x | Runtime validation | Schema bridge at WS boundary; `z.email()` not `z.string().email()` in v4 |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Magic UI | latest | Animated components (Bento Grid, etc.) | Install via `npx shadcn@latest add` — NOT magicui CLI directly |
| @xyflow/react | 12.x | DAG visualization | Phase 05 only needs CSS import in globals.css; first real use in Phase 07 |
| Immer | via Zustand middleware | Immutable updates | brainStore mutations (Map<brainId, BrainState>) |
| jose | 5.x | JWT verification in Server Components | Edge-compatible JWT verification (NOT jsonwebtoken which is Node-only) |
| clsx + tailwind-merge | latest | cn() utility | Conditional class merging |
| tw-animate-css | latest | CSS animations | Replaces tailwindcss-animate in Tailwind 4 |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| jose (JWT verify) | jsonwebtoken | jsonwebtoken is Node.js only — crashes in Next.js Edge Runtime used by Server Components |
| proxy.ts | middleware.ts | middleware.ts removed in Next.js 16 — proxy.ts is the replacement |
| pnpm | npm | Prohibited by project rules |
| Zod schema generator script | OpenAPI client gen | Simpler, no OpenAPI spec required, portable — confirmed out-of-scope alternative |

### Installation

```bash
# In apps/web/ (after scaffold)
pnpm add zustand immer jose clsx tailwind-merge
pnpm add @xyflow/react
pnpm add -D tw-animate-css
# shadcn/ui and Magic UI via CLI:
npx shadcn@latest init  # selects Tailwind v4 mode automatically
npx shadcn@latest add button input label card  # shadcn primitives
npx shadcn@latest add [magic-ui-component]     # Magic UI via shadcn@latest
```

---

## Architecture Patterns

### Recommended Project Structure

```
apps/web/
├── src/
│   ├── app/
│   │   ├── layout.tsx              # RootLayout — global metadata, fonts
│   │   ├── globals.css             # @import "tailwindcss", React Flow CSS @layer base
│   │   ├── (auth)/
│   │   │   └── login/
│   │   │       └── page.tsx        # LoginPage — 'use client', form, POST /api/auth/login
│   │   └── (protected)/
│   │       ├── layout.tsx          # AuthGuardLayout — Server Component, JWT verify
│   │       └── page.tsx            # War Room page (future phases)
│   ├── components/
│   │   └── ws/
│   │       └── WSBrainBridge.tsx   # 'use client', invisible, mounts in protected layout
│   ├── stores/
│   │   ├── wsStore.ts              # Zustand — WS lifecycle, connect/disconnect/subscribe
│   │   └── brainStore.ts           # Zustand + Immer — Map<brainId, BrainState>, RAF batching
│   ├── types/
│   │   └── api.ts                  # Generated by schema bridge script (SB-01)
│   └── lib/
│       ├── auth.ts                 # JWT verification helper (uses jose, server-only import)
│       └── cn.ts                   # cn() utility (clsx + tailwind-merge)
├── scripts/
│   └── generate-types.ts           # Zod schema generator (SB-01)
├── proxy.ts                        # Route protection (replaces middleware.ts)
├── next.config.ts                  # Minimal config, no Turbopack flags needed (default)
└── package.json
```

### Pattern 1: Dual-Layer JWT Auth (CVE-2025-29927 mitigation)

**What:** JWT verification happens in BOTH proxy.ts (route redirect) AND AuthGuardLayout Server Component (data access point). CVE-2025-29927 allows header-forging to bypass proxy.ts alone on unpatched Next.js. Next.js 16 is patched but defense-in-depth is the standard.

**When to use:** Every protected route/layout.

```typescript
// proxy.ts — route-level guard (redirect)
import { NextRequest, NextResponse } from 'next/server'
import { jwtVerify } from 'jose'

export async function proxy(request: NextRequest) {
  const token = request.cookies.get('access_token')?.value

  if (!token) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  try {
    const secret = new TextEncoder().encode(process.env.MM_SECRET_KEY)
    await jwtVerify(token, secret)
    return NextResponse.next()
  } catch {
    return NextResponse.redirect(new URL('/login', request.url))
  }
}

export const config = {
  matcher: ['/((?!login|_next/static|_next/image|favicon.ico).*)'],
}
```

```typescript
// app/(protected)/layout.tsx — data-access-point guard (Server Component)
import { cookies } from 'next/headers'
import { jwtVerify } from 'jose'
import { redirect } from 'next/navigation'
import 'server-only'

export default async function AuthGuardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const cookieStore = await cookies()  // async in Next.js 16
  const token = cookieStore.get('access_token')?.value

  if (!token) redirect('/login')

  try {
    const secret = new TextEncoder().encode(process.env.MM_SECRET_KEY)
    await jwtVerify(token, secret)
  } catch {
    redirect('/login')
  }

  return (
    <>
      <WSBrainBridge />  {/* Mounted once — invisible, WS lifecycle */}
      {children}
    </>
  )
}
```

### Pattern 2: wsStore — Module Singleton with Lazy Init

**What:** Zustand store at module level (survives navigation), WebSocket instance created ONLY inside `connect()` action guarded by `typeof window !== 'undefined'`. Never at module level or store initializer.

**When to use:** Any WS connection management.

```typescript
// src/stores/wsStore.ts
import { create } from 'zustand'

type Listener = (data: unknown) => void

interface WSState {
  socket: WebSocket | null
  taskId: string | null
  connected: boolean
  listeners: Map<string, Set<Listener>>
  connect: (taskId: string, token: string) => void
  disconnect: () => void
  subscribe: (event: string, listener: Listener) => () => void
}

export const useWSStore = create<WSState>((set, get) => ({
  socket: null,
  taskId: null,
  connected: false,
  listeners: new Map(),

  connect: (taskId, token) => {
    // CRITICAL: Guard for SSR — this action must only run in browser
    if (typeof window === 'undefined') return

    const { socket, disconnect } = get()
    if (socket && get().taskId === taskId) return  // Already connected to same task
    disconnect()

    const ws = new WebSocket(
      `${process.env.NEXT_PUBLIC_WS_URL}/ws/tasks/${taskId}?token=${token}`
    )

    ws.onopen = () => set({ connected: true })
    ws.onclose = () => set({ socket: null, connected: false, taskId: null })

    ws.onmessage = (event) => {
      // RAF batching handled in brainStore — raw dispatch here
      const msg = JSON.parse(event.data)
      const { listeners } = get()
      const handlers = listeners.get(msg.type)
      if (handlers) handlers.forEach(fn => fn(msg.data))
    }

    set({ socket: ws, taskId, connected: false })
  },

  disconnect: () => {
    const { socket } = get()
    socket?.close()
    set({ socket: null, connected: false, taskId: null })
  },

  subscribe: (event, listener) => {
    const { listeners } = get()
    if (!listeners.has(event)) listeners.set(event, new Set())
    listeners.get(event)!.add(listener)
    return () => listeners.get(event)?.delete(listener)
  },
}))
```

### Pattern 3: brainStore — Map + Immer + RAF Batching

**What:** Map<brainId, BrainState> for O(1) per-brain updates. RAF accumulator drains queued events before each paint — prevents 24 simultaneous setState calls from blocking the main thread.

**When to use:** Any brain state update from WebSocket.

```typescript
// src/stores/brainStore.ts
import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'

export type BrainStatus = 'idle' | 'active' | 'complete' | 'error'

export interface BrainState {
  id: string
  status: BrainStatus
  lastUpdated: number
}

interface BrainStoreState {
  brains: Map<string, BrainState>
  _queue: BrainState[]
  _rafId: number | null
  updateBrain: (brain: BrainState) => void
  _drainQueue: () => void
}

export const useBrainStore = create<BrainStoreState>()(
  immer((set, get) => ({
    brains: new Map(),
    _queue: [],
    _rafId: null,

    updateBrain: (brain) => {
      // Accumulate in queue — RAF drains before each paint
      get()._queue.push(brain)
      if (!get()._rafId) {
        const id = requestAnimationFrame(() => {
          get()._drainQueue()
        })
        set(state => { state._rafId = id })
      }
    },

    _drainQueue: () => {
      set(state => {
        for (const brain of state._queue) {
          state.brains.set(brain.id, brain)
        }
        state._queue = []
        state._rafId = null
      })
    },
  }))
)

// Targeted selector — prevents cascade re-renders
export const useBrainState = (id: string) =>
  useBrainStore(state => state.brains.get(id))
```

### Pattern 4: WSBrainBridge — Invisible Event Router

**What:** Client Component with null render that mounts once in the protected layout. Subscribes to WS events, validates with Zod, dispatches to brainStore.

**When to use:** Bridge between wsStore and brainStore.

```typescript
// src/components/ws/WSBrainBridge.tsx
'use client'

import { useEffect } from 'react'
import { useWSStore } from '@/stores/wsStore'
import { useBrainStore } from '@/stores/brainStore'
import { z } from 'zod'

// Zod schema for brain event — validates BEFORE store update
const BrainEventSchema = z.object({
  brain_id: z.string(),
  status: z.enum(['idle', 'active', 'complete', 'error']),
  timestamp: z.number(),
})

export function WSBrainBridge() {
  const subscribe = useWSStore(state => state.subscribe)
  const updateBrain = useBrainStore(state => state.updateBrain)

  useEffect(() => {
    const unsubscribe = subscribe('task_update_batch', (data) => {
      const result = BrainEventSchema.safeParse(data)
      if (result.success) {
        updateBrain({
          id: result.data.brain_id,
          status: result.data.status,
          lastUpdated: result.data.timestamp,
        })
      }
    })
    return unsubscribe
  }, [subscribe, updateBrain])

  return null  // No render output
}
```

### Pattern 5: React Flow CSS in globals.css

**What:** `@xyflow/react/dist/style.css` imported inside `@layer base` — the ONLY correct location for Tailwind 4. Any tsx import (even `import '@xyflow/react/dist/style.css'`) silently breaks node handles and edges in production builds.

**When to use:** Once, in globals.css. Never elsewhere.

```css
/* src/app/globals.css */
@import "tailwindcss";
@import "tw-animate-css";

@layer base {
  /* React Flow — MUST be in @layer base to survive Tailwind 4 cascade */
  @import "@xyflow/react/dist/style.css";

  /* CSS Custom Properties for design tokens */
  :root {
    --background: 0 0% 100%;
    --foreground: 0 0% 3.9%;
    /* ... shadcn/ui OKLCH tokens ... */
  }

  .dark {
    --background: 0 0% 3.9%;
    /* ... */
  }
}
```

### Pattern 6: Zod Schema Generator for SB-01

**What:** A script that reads Pydantic model source files and outputs matching Zod schemas to `apps/web/src/types/api.ts`. The schema must reflect the actual FastAPI models (LoginRequest, TokenResponse, etc.) that were verified from source.

**Approach:** Manual parity script (not auto-generated from OpenAPI) — project decision. The generator reads from Pydantic model source or writes idiomatic Zod 4 equivalents. TypeScript errors surface immediately when schemas diverge.

```typescript
// apps/web/src/types/api.ts (output of SB-01 generator)
import { z } from 'zod'

// Matches mastermind_cli/types/auth.py LoginRequest
export const LoginRequestSchema = z.object({
  username: z.string().min(1).max(100),
  password: z.string().min(1).max(100),
})

// Matches mastermind_cli/types/auth.py TokenResponse
export const TokenResponseSchema = z.object({
  access_token: z.string(),
  refresh_token: z.string(),
  token_type: z.string().default('Bearer'),
  expires_in: z.number().default(1800),
})

// Matches WS brain event data shape
export const BrainEventSchema = z.object({
  brain_id: z.string(),
  status: z.enum(['idle', 'active', 'complete', 'error']),
  timestamp: z.number(),
})

// WS message envelope (task_update_batch)
export const WSMessageSchema = z.object({
  type: z.literal('task_update_batch'),
  data: z.array(BrainEventSchema),
})

export type LoginRequest = z.infer<typeof LoginRequestSchema>
export type TokenResponse = z.infer<typeof TokenResponseSchema>
export type BrainEvent = z.infer<typeof BrainEventSchema>
```

### Anti-Patterns to Avoid

- **WebSocket at module level:** `const ws = new WebSocket(...)` outside any function crashes `npm run build` with `ReferenceError: WebSocket is not defined`. Always lazy in `connect()` action with `typeof window` guard.
- **React Flow CSS in tsx:** `import '@xyflow/react/dist/style.css'` in any .tsx file silently breaks handles and edges in Tailwind 4 production build.
- **JWT only in proxy.ts:** CVE-2025-29927 allows forging the `x-middleware-subrequest` header to skip proxy.ts. Always re-verify at Server Component data access point.
- **`jsonwebtoken` in Server Components:** `jsonwebtoken` is Node.js only — crashes Edge Runtime. Use `jose` (Edge-compatible) for all JWT verification.
- **`useWSStore()` selecting entire store:** Always select specific fields to prevent re-renders. Use `useWSStore(state => state.connect)` not `const store = useWSStore()`.
- **Magic UI via `npx magicui-cli`:** Uses `tailwind.config.ts` which doesn't exist in Tailwind 4. Always use `npx shadcn@latest add [component]` which has the Tailwind v4 ENOENT fix.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JWT verification in Server Components | Custom JWT parser | `jose` (jwtVerify) | Edge-compatible, handles expiry, signature verification, algorithm enforcement |
| CSS class merging | String concatenation | `cn()` via clsx + tailwind-merge | Handles Tailwind conflict resolution (`px-2 px-4` → `px-4`) |
| Form validation on login | Manual checks | Zod + react-hook-form | Type inference, async validation, field-level errors |
| Immutable Map updates in Zustand | Spread/clone | Immer middleware | O(n) vs structural sharing; `state.brains.set(id, v)` reads as mutation, works correctly |
| WS message type narrowing | `if (msg.type === ...)` | Zod discriminated union | Runtime validation catches schema drift from backend changes |

---

## Common Pitfalls

### Pitfall 1: React Flow CSS Specificity Destroyed by Tailwind 4

**What goes wrong:** Node handles are invisible, edges don't render, canvas background missing — only in production build (dev often works due to different CSS ordering).
**Why it happens:** Tailwind 4's `@layer` cascade overrides third-party CSS not explicitly placed in a layer. React Flow CSS has no layer declaration, so it goes to the unlayered pile — lower specificity than Tailwind utilities in production.
**How to avoid:** Import inside `@layer base` in globals.css. Smoke test with a 2-node ReactFlow graph in Plan 05-01 BEFORE writing any real component.
**Warning signs:** Edges invisible in `npm run build` output but visible in `npm run dev`.

### Pitfall 2: WebSocket SSR Crash at Build Time

**What goes wrong:** `npm run build` fails with `ReferenceError: WebSocket is not defined`.
**Why it happens:** Next.js evaluates module-level code during SSR/build. `new WebSocket()` doesn't exist in Node.js.
**How to avoid:** wsStore's `connect()` action must start with `if (typeof window === 'undefined') return`. Verify with `npm run build` after implementing wsStore, before wiring any components.
**Warning signs:** Build error mentioning `WebSocket` or `window is not defined`.

### Pitfall 3: Magic UI ENOENT on Tailwind 4

**What goes wrong:** `ENOENT: no such file or directory, open 'tailwind.config.ts'` when installing some Magic UI components.
**Why it happens:** Old Magic UI CLI expects `tailwind.config.ts` which doesn't exist in Tailwind 4 (CSS-only config).
**How to avoid:** Always use `npx shadcn@latest add [component]` — this version has the ENOENT fix (PR #620). Verify `@keyframes` are present in globals.css after each animated component install.
**Warning signs:** Install command fails with ENOENT; animations work in CLI but not in browser.

### Pitfall 4: 24 Simultaneous setState Calls Freeze UI

**What goes wrong:** When 24 brains complete simultaneously, 24 WS events arrive in rapid succession. Each triggers `setState` in brainStore. React 19 auto-batches synchronous updates but NOT async events. Result: 24 sequential renders, 300-500ms UI freeze.
**Why it happens:** WebSocket `onmessage` is an async event — outside React 19's synchronous batching scope.
**How to avoid:** RAF accumulator in brainStore. Queue events in `_queue`, drain queue once per animation frame. Per-brain `useBrainState(id)` selectors ensure only the affected tile re-renders.
**Warning signs:** FPS drops on multi-brain completion; React DevTools shows many rapid re-renders.

### Pitfall 5: cookies() Not Awaited in Next.js 16

**What goes wrong:** TypeScript error or runtime warning: "cookies() should be awaited before using its value".
**Why it happens:** Next.js 16 made `cookies()` async (was synchronous in Next.js 14/15).
**How to avoid:** `const cookieStore = await cookies()` in every Server Component that reads cookies.
**Warning signs:** TypeScript error on `cookies()` call; runtime warning in server logs.

### Pitfall 6: WS Token Passthrough to Client Components

**What goes wrong:** JWT access token is in an httpOnly cookie — JavaScript cannot read it. Client Component that tries to initialize wsStore needs the token.
**Why it happens:** httpOnly cookies are intentionally inaccessible to JS. The token handoff from Server Component to Client Component requires a mechanism.
**How to avoid:** Server Component (AuthGuardLayout) verifies JWT, extracts user_id from payload, passes a short-lived session token or the access token value as a prop to the Client WSProvider. Alternative: expose a `/api/auth/me` route that returns the token for the WS connection (token from cookie → Server Action → Client).
**Warning signs:** wsStore.connect() receiving undefined token; WS connection failing with 1008 code.

### Pitfall 7: allow_origins Wildcard with allow_credentials

**What goes wrong:** Browser blocks request with "Wildcard '*' is not allowed with credentials".
**Why it happens:** CORS spec prohibits `allow_origins=["*"]` combined with `allow_credentials=True` AND a non-`*` `Origin` header. Chrome/Firefox enforce this strictly.
**How to avoid:** The existing FastAPI CORS config uses `allow_origins=["*"]` — this WILL break when the frontend sends credentials (httpOnly cookies). For Phase 05, update `allow_origins` to explicitly list the Next.js origin: `["http://localhost:3000"]`. Note: the current code has this bug that must be fixed in Plan 05-02.
**Warning signs:** `Access-Control-Allow-Origin: *` header in response when credentials are sent; browser console CORS error on cookie requests.

---

## Code Examples

### Login Action (Server Action in LoginPage)

```typescript
// app/(auth)/login/actions.ts
'use server'

import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import { TokenResponseSchema } from '@/types/api'

export async function loginAction(formData: FormData) {
  const response = await fetch(`${process.env.API_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: formData.get('username'),
      password: formData.get('password'),
    }),
  })

  if (!response.ok) {
    return { error: 'Invalid credentials' }
  }

  const parsed = TokenResponseSchema.safeParse(await response.json())
  if (!parsed.success) {
    return { error: 'Invalid server response' }
  }

  const cookieStore = await cookies()
  cookieStore.set('access_token', parsed.data.access_token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: parsed.data.expires_in,
    path: '/',
  })
  cookieStore.set('refresh_token', parsed.data.refresh_token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 86400,  // 24h
    path: '/',
  })

  redirect('/')
}
```

### Zustand Targeted Selector (prevents cascade re-renders)

```typescript
// In any component displaying a single brain's state
import { useBrainState } from '@/stores/brainStore'

function BrainTile({ brainId }: { brainId: string }) {
  // Only re-renders when THIS brain's state changes
  const brain = useBrainState(brainId)
  return <div>{brain?.status ?? 'idle'}</div>
}
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| middleware.ts | proxy.ts | Next.js 16 | All route protection must use proxy.ts |
| `tailwind.config.js` | CSS-only `@theme` in globals.css | Tailwind 4 | No tailwind.config.js should exist |
| `@tailwind base/components/utilities` | `@import "tailwindcss"` | Tailwind 4 | Single import replaces three directives |
| `tailwindcss-animate` | `tw-animate-css` | shadcn/ui Tailwind v4 | Different package, different install |
| `cookies()` synchronous | `await cookies()` | Next.js 16 | Must await in every Server Component |
| jsonwebtoken | jose | Next.js Edge Runtime | Edge-compatible requirement |
| `import reactflow/dist/style.css` in tsx | `@layer base { @import "..." }` in globals.css | @xyflow/react + Tailwind 4 | CSS specificity fix |
| `z.string().email()` | `z.email()` | Zod 4 | Breaking API change |

**Deprecated/outdated:**
- `middleware.ts`: Removed in Next.js 16. Use `proxy.ts`.
- `tailwind.config.ts/js`: No longer used in Tailwind 4. CSS-only config.
- `tailwindcss-animate`: Replaced by `tw-animate-css`.
- `z.string().email()`: Zod 3 syntax. Use `z.email()` in Zod 4.

---

## Open Questions

1. **WS token handoff: Server Component → Client wsStore**
   - What we know: httpOnly cookies are inaccessible to JS; AuthGuardLayout runs on server; wsStore.connect() needs the JWT token string
   - What's unclear: The cleanest mechanism to pass the token value from the verified Server Component to the Client Component that calls wsStore.connect()
   - Recommendation: Expose a minimal `/api/auth/token` route handler that reads the httpOnly cookie (server-side) and returns the access_token value — called by the WSBrainBridge on mount. Alternatively, pass token as a Server Component prop to a Client WSProvider wrapper. The second approach is simpler (no extra API call) and is the recommended pattern.

2. **FastAPI CORS wildcard + credentials bug**
   - What we know: `allow_origins=["*"]` + `allow_credentials=True` is invalid per CORS spec; browsers reject it
   - What's unclear: Whether the existing Python tests cover CORS headers (if they do, changing allow_origins breaks tests)
   - Recommendation: Plan 05-02 must update `allow_origins` to `["http://localhost:3000"]` (or read from an `ALLOWED_ORIGINS` env var). Verify no existing tests assert `"*"` in CORS headers.

3. **WS message schema: exact brain event shape**
   - What we know: The WS broadcaster sends `{ type: "task_update_batch", data: [...update_data] }`. The `update_data` shape comes from the Coordinator's orchestration output.
   - What's unclear: The exact fields in each `update_data` item that map to brain status — no explicit BrainEvent Pydantic model found in the source inspection
   - Recommendation: Inspect `mastermind_cli/orchestrator/` coordinator output shape before finalizing BrainEventSchema in the schema bridge. The Zod schema may need adjustment in Plan 05-03 during integration testing.

---

## Validation Architecture

nyquist_validation is enabled in `.planning/config.json`.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | None detected in apps/web/ — to be scaffolded. Next.js 16 ships with Jest config option during `create-next-app`. Use Vitest (faster, ESM-native) or Jest per project choice. |
| Config file | `vitest.config.ts` (Wave 0) or `jest.config.ts` |
| Quick run command | `pnpm test --run` (Vitest) or `pnpm test --watchAll=false` (Jest) |
| Full suite command | `pnpm test --run --coverage` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FND-01 | Next.js 16 scaffold produces clean `pnpm build` | smoke | `pnpm build` exits 0 | ❌ Wave 0 |
| FND-01 | React Flow CSS renders handles and edges | smoke | `pnpm build` + visual check (manual) | ❌ Wave 0 |
| FND-01 | Magic UI animated component renders @keyframes | smoke | `pnpm build` + visual check (manual) | ❌ Wave 0 |
| FND-02 | Login action sets httpOnly cookie on valid credentials | unit | `pnpm test -- loginAction` | ❌ Wave 0 |
| FND-02 | Login action returns error on invalid credentials | unit | `pnpm test -- loginAction` | ❌ Wave 0 |
| FND-03 | proxy.ts redirects unauthenticated requests to /login | unit | `pnpm test -- proxy` | ❌ Wave 0 |
| FND-03 | AuthGuardLayout redirects when JWT invalid/expired | unit | `pnpm test -- AuthGuardLayout` | ❌ Wave 0 |
| FND-04 | FastAPI CORS allows credentials from localhost:3000 | integration | `pnpm test -- cors` (against live API) | ❌ Wave 0 |
| SB-01 | Schema generator outputs api.ts matching Pydantic models | unit | `pnpm test -- generate-types` | ❌ Wave 0 |
| SB-01 | TypeScript error surfaces when backend model changes | type-check | `pnpm tsc --noEmit` | ❌ Wave 0 |
| WS-01 | wsStore.connect() is no-op when already connected to same taskId | unit | `pnpm test -- wsStore` | ❌ Wave 0 |
| WS-01 | wsStore survives client-side navigation (store not reset) | integration | `pnpm test -- wsStore navigation` | ❌ Wave 0 |
| WS-02 | brainStore RAF batching drains 24 queued events in single frame | unit | `pnpm test -- brainStore RAF` | ❌ Wave 0 |
| WS-03 | useBrainState(id) selector only triggers re-render for matching id | unit | `pnpm test -- useBrainState` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `pnpm tsc --noEmit && pnpm test --run`
- **Per wave merge:** `pnpm build && pnpm test --run --coverage`
- **Phase gate:** Full suite green + `pnpm build` clean before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `apps/web/vitest.config.ts` — test runner config (or jest.config.ts if Jest chosen during scaffold)
- [ ] `apps/web/src/stores/__tests__/wsStore.test.ts` — covers WS-01
- [ ] `apps/web/src/stores/__tests__/brainStore.test.ts` — covers WS-02, WS-03
- [ ] `apps/web/src/app/__tests__/proxy.test.ts` — covers FND-03
- [ ] `apps/web/src/app/__tests__/loginAction.test.ts` — covers FND-02
- [ ] `apps/web/scripts/__tests__/generate-types.test.ts` — covers SB-01
- [ ] Framework install: `pnpm add -D vitest @vitejs/plugin-react jsdom @testing-library/react` — if Vitest chosen

---

## Sources

### Primary (HIGH confidence)

- Verified from source: `apps/api/mastermind_cli/api/app.py` — CORS config, route registration
- Verified from source: `apps/api/mastermind_cli/api/routes/auth.py` — JWT endpoints, token shapes
- Verified from source: `apps/api/mastermind_cli/api/websocket.py` — WS endpoint URL, message format, auth
- Verified from source: `apps/api/mastermind_cli/types/auth.py` — Pydantic models for Zod bridge
- Verified from source: `apps/api/mastermind_cli/brain_registry.py` — Brain data structure
- Verified from source: `docker-compose.yml` — networking (api:8000, web:3000, `allow_credentials=True`)
- `.planning/research/SUMMARY.md` — Verified stack with official source citations (Next.js 16 blog, React Flow Tailwind 4 changelog, shadcn/ui Tailwind v4 docs, CVE-2025-29927)
- `.planning/phases/05-foundation-auth-ws/05-CONTEXT.md` — Brain-04 locked decisions
- `.planning/STATE.md` — Architecture decisions log

### Secondary (MEDIUM confidence)

- Project SUMMARY.md cites: [Next.js 16 release blog](https://nextjs.org/blog/next-16), [React Flow Tailwind 4 update (Oct 2025)](https://reactflow.dev/whats-new/2025-10-28), [shadcn/ui Tailwind v4 docs](https://ui.shadcn.com/docs/tailwind-v4), [CVE-2025-29927](https://projectdiscovery.io/blog/nextjs-middleware-authorization-bypass)
- Project SUMMARY.md cites: [Magic UI Issue #548 / PR #620](https://github.com/magicuidesign/magicui/issues/548) — ENOENT fix
- Project skills: `zustand-5/SKILL.md`, `tailwind-4/SKILL.md`, `zod-4/SKILL.md`, `nextjs-15/SKILL.md` — verified patterns

### Tertiary (LOW confidence)

- WS token handoff mechanism (Server Component → Client) — derived from Next.js auth patterns, specific to this project's httpOnly cookie + wsStore architecture, needs validation during Plan 05-03
- Exact WS brain event schema fields — backend orchestrator not fully inspected (only websocket.py broadcaster, not the Coordinator output shape)

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — All versions verified in SUMMARY.md with official source citations as of 2026-03-17
- Architecture patterns: HIGH — Verified from CONTEXT.md (Brain-04), STATE.md decisions, and direct backend source inspection
- Backend integration: HIGH — Auth endpoints, WS endpoint, CORS config all verified from source code
- Pitfalls: HIGH — CSS cascade (official React Flow changelog), WS SSR crash (documented behavior), CVE-2025-29927 (disclosed CVE), Magic UI ENOENT (resolved GitHub issue)
- WS event schema: MEDIUM — Broadcaster shape verified but individual update_data fields require Coordinator source inspection

**Research date:** 2026-03-18
**Valid until:** 2026-04-17 (stable stack — Next.js/Tailwind/Zustand change infrequently)
