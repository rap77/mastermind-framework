# Architecture Research

**Domain:** Next.js 16 frontend integrating with existing FastAPI backend (War Room v2.1)
**Researched:** 2026-03-18
**Confidence:** HIGH

---

## Context

This document supersedes the v2.0 architecture research. The backend (apps/api/) is complete and
stable. This research addresses the six specific integration questions for the v2.1 Next.js frontend:

1. JWT auth flow with httpOnly cookies
2. Single WebSocket connection shared across navigation
3. Zustand store shape for WebSocket + brain state
4. React Flow custom nodes and the Server/Client boundary
5. API calls strategy (server vs client, CORS)
6. Build order for fastest feedback loop

---

## Critical Next.js 16 Breaking Change: middleware → proxy

**IMPORTANT:** Next.js 16 deprecated `middleware.ts`. Route protection now lives in `proxy.ts`.

```
middleware.ts  →  proxy.ts
export function middleware()  →  export function proxy()
```

The proxy runtime is **Node.js only** (not edge). The `jose` library must be used for JWT
verification (not `jsonwebtoken`, which is Node-only and breaks edge). Since we are now on Node.js
runtime anyway, `jsonwebtoken` works too — but `jose` is the safer cross-version choice.

Cookies API is now **fully async**. `cookies()` must be awaited everywhere (breaking change from v15).

---

## System Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        Browser (Next.js 16)                      │
├──────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────────┐ │
│  │proxy.ts     │  │ Server       │  │ Client Components        │ │
│  │(route guard)│  │ Components   │  │ "use client"             │ │
│  │             │  │ (data fetch) │  │ - WS events              │ │
│  │cookie check │  │ no WS/store  │  │ - React Flow             │ │
│  └──────┬──────┘  └──────┬───────┘  └────────────┬─────────────┘ │
│         │                │                       │               │
│         │          server-side fetch             │               │
│         │         (Authorization header)         │               │
│         │                │                       │               │
│  ┌──────┴──────────────── ┴────────────────── ──┘│               │
│  │              Zustand Store (Client-side)      │               │
│  │  wsStore: connection + event subscriptions   │               │
│  │  brainStore: nodes map (brain_id → state)    │               │
│  │  authStore: access_token (memory only)       │               │
│  └───────────────────────┬──────────────────────┘               │
└──────────────────────────┼───────────────────────────────────────┘
                           │ WebSocket ws://localhost:8000/ws/tasks/{task_id}?token=...
                           │ REST   http://localhost:8000/api/...
┌──────────────────────────▼───────────────────────────────────────┐
│              FastAPI Backend (apps/api/ — UNCHANGED)             │
├──────────────────────────────────────────────────────────────────┤
│  POST /api/auth/login    → { access_token, refresh_token }       │
│  POST /api/auth/refresh  → { access_token, refresh_token }       │
│  POST /api/tasks         → { task_id, status }                   │
│  GET  /api/tasks         → task list                             │
│  GET  /api/tasks/{id}/graph → nodes[], edges[]                   │
│  WS   /ws/tasks/{id}?token=... → brain events                    │
└──────────────────────────────────────────────────────────────────┘
```

---

## 1. JWT Auth Flow: httpOnly Cookies + proxy.ts

### Decision: Dual-Token Storage Strategy

Store tokens in httpOnly cookies, never in localStorage or Zustand state.

**Why httpOnly cookies:**
- XSS protection: client-side JS cannot read the token
- `proxy.ts` can read them synchronously for route protection
- Survives page refresh without re-auth

**Why NOT memory-only tokens for access_token:**
- Lost on navigation/refresh
- Forces re-auth on every page load

**Why NOT localStorage:**
- Accessible to XSS attacks
- Violates security best practices for JWTs

### Cookie Layout

```
access_token   httpOnly, SameSite=Lax, Path=/
refresh_token  httpOnly, SameSite=Lax, Path=/api/auth/refresh
```

Setting `Path=/api/auth/refresh` for the refresh token means it is only sent to the refresh
endpoint, reducing attack surface.

### Token Flow

```
Login (Server Action)
  → POST /api/auth/login → { access_token, refresh_token }
  → Set-Cookie: access_token (httpOnly, 30min)
  → Set-Cookie: refresh_token (httpOnly, 24h, Path=/api/auth/refresh)
  → redirect('/command-center')

proxy.ts (every protected route)
  → const cookies = await cookies()
  → const token = cookies.get('access_token')
  → if (!token) redirect('/login')
  → verify token with jose (JWTS_HS256)
  → if expired → attempt refresh via internal fetch
  → if refresh fails → redirect('/login')

Server Components (data fetch)
  → const cookies = await cookies()
  → fetch(`${API_URL}/api/tasks`, {
      headers: { Authorization: `Bearer ${cookies.get('access_token')}` }
    })

WebSocket (Client Component)
  → token cannot be read from httpOnly cookie in client JS
  → SOLUTION: route handler GET /api/token-hint returns token for WS use only
  → OR: pass token as prop from Server Component to Client Component
  → RECOMMENDED: pass access_token as prop from Server layout to WS context provider
```

### Implementation: proxy.ts (replaces middleware.ts)

```typescript
// apps/web/proxy.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { jwtVerify } from "jose";

const SECRET = new TextEncoder().encode(
  process.env.MM_SECRET_KEY ?? "change-me-in-production"
);

const PROTECTED = ["/command-center", "/nexus", "/vault", "/engine-room"];

export async function proxy(request: NextRequest) {
  const isProtected = PROTECTED.some((p) =>
    request.nextUrl.pathname.startsWith(p)
  );

  if (!isProtected) return NextResponse.next();

  const token = request.cookies.get("access_token")?.value;

  if (!token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  try {
    await jwtVerify(token, SECRET);
    return NextResponse.next();
  } catch {
    // Token expired — attempt refresh via internal API call
    const refreshToken = request.cookies.get("refresh_token")?.value;
    if (!refreshToken) {
      return NextResponse.redirect(new URL("/login", request.url));
    }

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/auth/refresh`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      }
    );

    if (!response.ok) {
      return NextResponse.redirect(new URL("/login", request.url));
    }

    const { access_token, refresh_token } = await response.json();
    const nextResponse = NextResponse.next();
    nextResponse.cookies.set("access_token", access_token, {
      httpOnly: true,
      sameSite: "lax",
      path: "/",
      maxAge: 60 * 30, // 30 min
    });
    nextResponse.cookies.set("refresh_token", refresh_token, {
      httpOnly: true,
      sameSite: "lax",
      path: "/api/auth/refresh",
      maxAge: 60 * 60 * 24, // 24h
    });
    return nextResponse;
  }
}

export const config = {
  matcher: ["/command-center/:path*", "/nexus/:path*", "/vault/:path*", "/engine-room/:path*"],
};
```

### Token Handoff for WebSocket

The access_token in httpOnly cookies is invisible to client JS. The WS endpoint requires a token
query param. Solution: pass the token from the Server Component layout as a prop.

```typescript
// app/(protected)/layout.tsx — Server Component
import { cookies } from "next/headers";
import { WSProvider } from "@/components/ws-provider";

export default async function ProtectedLayout({ children }) {
  const cookieStore = await cookies();
  const token = cookieStore.get("access_token")?.value ?? "";

  return (
    <WSProvider token={token}>
      {children}
    </WSProvider>
  );
}
```

This is the cleanest solution: no Route Handler needed, token flows from server to client in a
single React tree pass. The `WSProvider` is a Client Component that initializes the Zustand store.

---

## 2. WebSocket: Single Connection Across Navigation

### Problem

Client Components are re-mounted on navigation. A naive `useEffect(() => new WebSocket(...))` in a
component creates a new connection every time the user navigates between screens, multiplying
connections.

### Solution: Module-Level Singleton + Zustand Store Lifecycle

The WebSocket connection is managed at **module scope** inside the Zustand store, not inside a
React component. The store persists across renders and navigation because Zustand stores are module
singletons.

```typescript
// apps/web/src/stores/ws-store.ts
import { create } from "zustand";

type BrainEvent =
  | { type: "brain_step_started"; brain_id: string; brain_name: string; task_id: string }
  | { type: "brain_step_completed"; brain_id: string; output: string; duration_ms: number }
  | { type: "brain_step_failed"; brain_id: string; error: string }
  | { type: "execution_complete"; task_id: string; total_duration_ms: number };

interface WSStore {
  socket: WebSocket | null;
  taskId: string | null;
  token: string | null;
  status: "disconnected" | "connecting" | "connected" | "error";
  connect: (taskId: string, token: string) => void;
  disconnect: () => void;
  // Event subscribers by type
  listeners: Map<string, Set<(event: BrainEvent) => void>>;
  subscribe: (type: BrainEvent["type"], fn: (event: BrainEvent) => void) => () => void;
}

export const useWSStore = create<WSStore>((set, get) => ({
  socket: null,
  taskId: null,
  token: null,
  status: "disconnected",
  listeners: new Map(),

  connect: (taskId, token) => {
    const { socket, taskId: currentTask } = get();

    // Reuse connection if same task is already connected
    if (socket && currentTask === taskId && socket.readyState === WebSocket.OPEN) {
      return;
    }

    // Close previous connection
    if (socket) {
      socket.close();
    }

    set({ status: "connecting", taskId, token });

    const ws = new WebSocket(
      `${process.env.NEXT_PUBLIC_WS_URL}/ws/tasks/${taskId}?token=${token}`
    );

    ws.onopen = () => set({ socket: ws, status: "connected" });
    ws.onclose = () => set({ socket: null, status: "disconnected" });
    ws.onerror = () => set({ socket: null, status: "error" });

    ws.onmessage = (event) => {
      const data: BrainEvent = JSON.parse(event.data);
      const listeners = get().listeners.get(data.type);
      if (listeners) {
        listeners.forEach((fn) => fn(data));
      }
    };
  },

  disconnect: () => {
    const { socket } = get();
    if (socket) socket.close();
    set({ socket: null, status: "disconnected", taskId: null });
  },

  subscribe: (type, fn) => {
    const { listeners } = get();
    if (!listeners.has(type)) listeners.set(type, new Set());
    listeners.get(type)!.add(fn);

    // Return unsubscribe function
    return () => {
      listeners.get(type)?.delete(fn);
    };
  },
}));
```

### Why this works across navigation

Zustand store is module-level. When the user navigates from `/nexus` to `/command-center`, React
unmounts the Nexus components but the store module stays in memory. The `socket` reference is
preserved. New components subscribe to events from the existing connection.

### WSProvider (Client Component — wraps protected layout)

```typescript
// apps/web/src/components/ws-provider.tsx
"use client";
import { useEffect } from "react";
import { useWSStore } from "@/stores/ws-store";

interface WSProviderProps {
  token: string;
  children: React.ReactNode;
}

export function WSProvider({ token, children }: WSProviderProps) {
  const setToken = useWSStore((s) => s.token);

  // Store token so components can initiate WS connections
  useEffect(() => {
    useWSStore.setState({ token });
  }, [token]);

  return <>{children}</>;
}
```

---

## 3. Zustand Store Architecture

### Three stores, each with a single responsibility

```
useWSStore       — WebSocket lifecycle + event pub/sub
useBrainStore    — Brain states (updated by WS events)
useAuthStore     — Token in memory for WS (NOT cookies, those are server-only)
```

### useBrainStore: The Re-render Prevention Store

This is the most performance-critical store. With 24 brains, we must NOT store all nodes in a
single array — updating one brain would re-render all 24 node components.

**Key insight:** Store brains as a `Map<brain_id, BrainState>` and use Immer for surgical updates.
Each React Flow node reads ONLY its own state via a targeted selector.

```typescript
// apps/web/src/stores/brain-store.ts
import { create } from "zustand";
import { immer } from "zustand/middleware/immer";

export type BrainStatus = "idle" | "pending" | "running" | "completed" | "failed";

export interface BrainState {
  brainId: string;
  brainName: string;
  status: BrainStatus;
  output: string | null;
  error: string | null;
  durationMs: number | null;
  startedAt: number | null;
}

interface BrainStore {
  brains: Map<string, BrainState>;
  activeTaskId: string | null;
  setActiveTask: (taskId: string, initialNodes: { id: string; label: string }[]) => void;
  handleBrainStarted: (brainId: string, brainName: string, taskId: string) => void;
  handleBrainCompleted: (brainId: string, output: string, durationMs: number) => void;
  handleBrainFailed: (brainId: string, error: string) => void;
  resetTask: () => void;
}

export const useBrainStore = create<BrainStore>()(
  immer((set) => ({
    brains: new Map(),
    activeTaskId: null,

    setActiveTask: (taskId, initialNodes) =>
      set((state) => {
        state.activeTaskId = taskId;
        state.brains = new Map(
          initialNodes.map((n) => [
            n.id,
            {
              brainId: n.id,
              brainName: n.label,
              status: "pending",
              output: null,
              error: null,
              durationMs: null,
              startedAt: null,
            },
          ])
        );
      }),

    handleBrainStarted: (brainId, brainName, taskId) =>
      set((state) => {
        const brain = state.brains.get(brainId);
        if (brain) {
          brain.status = "running";
          brain.startedAt = Date.now();
        }
      }),

    handleBrainCompleted: (brainId, output, durationMs) =>
      set((state) => {
        const brain = state.brains.get(brainId);
        if (brain) {
          brain.status = "completed";
          brain.output = output;
          brain.durationMs = durationMs;
        }
      }),

    handleBrainFailed: (brainId, error) =>
      set((state) => {
        const brain = state.brains.get(brainId);
        if (brain) {
          brain.status = "failed";
          brain.error = error;
        }
      }),

    resetTask: () =>
      set((state) => {
        state.brains = new Map();
        state.activeTaskId = null;
      }),
  }))
);

// Targeted selector — component ONLY re-renders when its own brain changes
export const useBrainState = (brainId: string) =>
  useBrainStore((s) => s.brains.get(brainId));
```

### WS Event → Brain Store Bridge

This bridge component lives once at the app level. It subscribes to WS events and dispatches to
the brain store. It has NO render output.

```typescript
// apps/web/src/components/ws-brain-bridge.tsx
"use client";
import { useEffect } from "react";
import { useWSStore } from "@/stores/ws-store";
import { useBrainStore } from "@/stores/brain-store";

export function WSBrainBridge() {
  const subscribe = useWSStore((s) => s.subscribe);
  const { handleBrainStarted, handleBrainCompleted, handleBrainFailed } = useBrainStore();

  useEffect(() => {
    const unsubs = [
      subscribe("brain_step_started", (e) => {
        if (e.type === "brain_step_started") {
          handleBrainStarted(e.brain_id, e.brain_name, e.task_id);
        }
      }),
      subscribe("brain_step_completed", (e) => {
        if (e.type === "brain_step_completed") {
          handleBrainCompleted(e.brain_id, e.output, e.duration_ms);
        }
      }),
      subscribe("brain_step_failed", (e) => {
        if (e.type === "brain_step_failed") {
          handleBrainFailed(e.brain_id, e.error);
        }
      }),
    ];
    return () => unsubs.forEach((u) => u());
  }, [subscribe, handleBrainStarted, handleBrainCompleted, handleBrainFailed]);

  return null;
}
```

---

## 4. React Flow: Server/Client Boundary + Node Re-render Prevention

### Boundary Rule

React Flow is entirely a Client Component concern. No React Flow import belongs in a Server
Component. The pattern is:

```
Server Component (page.tsx)
  → fetch /api/tasks/{id}/graph  (nodes[], edges[])
  → pass nodes/edges as props to NexusCanvas (Client Component)

NexusCanvas ("use client")
  → initializes React Flow with nodes from props
  → hands off state management to useBrainStore for live updates
```

### Preventing 23-node cascade re-renders

The critical mistake is passing WS state through React Flow's `nodes` array. When one brain
changes, React Flow would re-compute and re-render all nodes.

**Correct pattern: stable node data + external state lookup in each node**

```typescript
// The nodes array passed to ReactFlow NEVER changes (position/layout only)
// Brain state comes from useBrainStore inside each node component

// ✅ CORRECT: Custom node reads its own state from store
// apps/web/src/components/brain-node.tsx
"use client";
import { memo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import { useBrainState } from "@/stores/brain-store";
import { cn } from "@/lib/utils";

const STATUS_COLORS: Record<string, string> = {
  idle: "border-slate-600 bg-slate-900",
  pending: "border-slate-500 bg-slate-800",
  running: "border-blue-500 bg-blue-950 animate-pulse",
  completed: "border-emerald-500 bg-emerald-950",
  failed: "border-red-500 bg-red-950",
};

function BrainNodeComponent({ id, data }: NodeProps) {
  // Targeted selector — only re-renders when THIS brain's state changes
  const brainState = useBrainState(id);
  const status = brainState?.status ?? "idle";

  return (
    <div className={cn("rounded-lg border-2 px-4 py-3 min-w-[140px]", STATUS_COLORS[status])}>
      <Handle type="target" position={Position.Top} />
      <p className="text-xs font-medium text-white truncate">{data.label as string}</p>
      <p className="text-xs text-slate-400 capitalize">{status}</p>
      {brainState?.durationMs && (
        <p className="text-xs text-slate-500">{brainState.durationMs}ms</p>
      )}
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

// React.memo prevents re-render when PARENT re-renders
// The store selector handles re-render when brain state changes
export const BrainNode = memo(BrainNodeComponent);
```

```typescript
// ❌ WRONG: Passing ws state through node data
const nodes = brains.map(b => ({
  id: b.id,
  data: { status: b.status }  // This triggers full node array replacement → all nodes re-render
}));
```

### NexusCanvas Client Component

```typescript
// apps/web/src/components/nexus-canvas.tsx
"use client";
import { useMemo } from "react";
import { ReactFlow, Background, Controls, type Node, type Edge } from "@xyflow/react";
import { BrainNode } from "./brain-node";
import "@xyflow/react/dist/style.css";

// Declared OUTSIDE component — prevents new reference on every render
const NODE_TYPES = { brainNode: BrainNode };

interface NexusCanvasProps {
  initialNodes: Node[];
  initialEdges: Edge[];
}

export function NexusCanvas({ initialNodes, initialEdges }: NexusCanvasProps) {
  // Layout-only nodes — these NEVER change after mount
  // State comes from useBrainStore inside each node
  const nodes = useMemo(
    () => initialNodes.map((n) => ({ ...n, type: "brainNode" })),
    [initialNodes]  // Only recomputes if layout changes (navigation to new task)
  );

  return (
    <div className="h-full w-full">
      <ReactFlow
        nodes={nodes}
        edges={initialEdges}
        nodeTypes={NODE_TYPES}
        fitView
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}
```

---

## 5. API Calls: Server vs Client, CORS

### CORS: Already Configured

The FastAPI backend has `CORSMiddleware` with `allow_origins=["*"]`. No CORS changes needed in
the backend for development. For production, tighten to `allow_origins=["http://localhost:3000"]`
or the production domain.

### Server-side fetch (Server Components)

Use for: initial page data, task lists, brain configs, anything that benefits from SSR or caching.

```typescript
// apps/web/src/lib/api.ts
import { cookies } from "next/headers";
import "server-only";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const cookieStore = await cookies();
  const token = cookieStore.get("access_token")?.value;

  const res = await fetch(`${API}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init?.headers,
    },
    // No cache by default — dashboard is real-time
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${path}`);
  }

  return res.json();
}
```

### Client-side fetch (Client Components)

Use for: mutations triggered by user interaction (create task, cancel task), cases where the result
must update UI without navigation.

```typescript
// apps/web/src/lib/client-api.ts — Client-safe API utility
// Does NOT use cookies() — reads token from WSStore which holds it in memory

export async function clientFetch<T>(path: string, init?: RequestInit): Promise<T> {
  // Token was passed from Server Component → WSProvider → stored in wsStore
  const token = useWSStore.getState().token;

  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init?.headers,
    },
  });

  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}
```

### When to use Server vs Client fetch

| Use case | Approach | Why |
|----------|----------|-----|
| Initial task list on page load | Server Component + `apiFetch` | SSR, faster initial paint |
| Task graph for Nexus | Server Component + `apiFetch` | Data available before hydration |
| Create task (form submit) | Server Action | Progressive enhancement |
| Cancel running task (button) | Client Component + `clientFetch` | Immediate UI feedback |
| Poll task status | NOT needed | WebSocket handles real-time updates |

---

## 6. Build Order: Fastest Feedback Loop

Build in this order because each screen validates the next layer's foundation.

### Screen 1: Login (authentication plumbing)

**Why first:** Every other screen depends on auth. Building login first validates the entire
auth flow: cookie setting, proxy.ts route protection, token handoff to WSProvider.

- Server Action for form submission
- `POST /api/auth/login` → set httpOnly cookies
- proxy.ts redirect validation
- If login works → auth architecture is correct

### Screen 2: Command Center (brief input + brain grid)

**Why second:** Exercises REST API (brain list, task creation) and the WS connection initiation.
The Bento Grid with 24 brain cards validates the `useBrainStore` and `useBrainState` selectors.
No React Flow complexity yet.

- `GET /api/brains` (need to verify this endpoint exists — see gaps below)
- `POST /api/tasks` → get task_id → open WS
- WS events → useBrainStore updates → BrainCard components update individually
- Validates re-render prevention before Nexus complexity

### Screen 3: The Nexus (React Flow DAG)

**Why third:** Depends on task_id from Command Center and WS infrastructure from Screen 2.
Build after WS → BrainStore pipeline is proven correct.

- `GET /api/tasks/{id}/graph` → nodes[], edges[]
- ReactFlow with custom BrainNode components
- BrainNode reads from useBrainStore (already working from Screen 2)
- Test: launch task in Command Center, switch to Nexus → nodes illuminate

### Screen 4: Strategy Vault + Engine Room

**Why last:** Read-only views of data already in the API. Lowest risk, no new integration
patterns. Build after the complex screens prove the infrastructure.

---

## Recommended Project Structure

```
apps/web/
├── proxy.ts                    # Route protection (NOT middleware.ts — Next.js 16)
├── next.config.ts
├── src/
│   ├── app/
│   │   ├── layout.tsx          # Root layout (fonts, global styles)
│   │   ├── (auth)/
│   │   │   └── login/
│   │   │       └── page.tsx    # Server Component — login form
│   │   └── (protected)/
│   │       ├── layout.tsx      # Server Component — fetches token, wraps WSProvider
│   │       ├── command-center/
│   │       │   └── page.tsx    # Server Component — fetches brain list
│   │       ├── nexus/
│   │       │   └── page.tsx    # Server Component — fetches task graph
│   │       ├── vault/
│   │       │   └── page.tsx
│   │       └── engine-room/
│   │           └── page.tsx
│   ├── actions/
│   │   ├── auth.ts             # "use server" — login, logout, refresh
│   │   └── tasks.ts            # "use server" — create task, cancel task
│   ├── components/
│   │   ├── ws-provider.tsx     # "use client" — initializes token in wsStore
│   │   ├── ws-brain-bridge.tsx # "use client" — routes WS events to brainStore
│   │   ├── brain-node.tsx      # "use client" — React Flow custom node
│   │   ├── nexus-canvas.tsx    # "use client" — React Flow canvas
│   │   ├── brain-card.tsx      # "use client" — Bento Grid brain card
│   │   └── command-input.tsx   # "use client" — Raycast-style input
│   ├── stores/
│   │   ├── ws-store.ts         # WebSocket lifecycle + pub/sub
│   │   └── brain-store.ts      # Brain states map + Immer updates
│   └── lib/
│       ├── api.ts              # "server-only" — server-side fetch with cookies
│       ├── client-api.ts       # Client-side fetch with token from wsStore
│       └── utils.ts            # cn() and other utilities
```

---

## Architectural Patterns

### Pattern 1: Token Waterfall (Server → Client)

**What:** httpOnly cookie token flows from Server Component → Client Component prop → Zustand
store. No client JS ever reads cookies directly.

**When to use:** Any time a Client Component needs auth credentials (WS, client-side API calls).

**Trade-offs:**
- Safe against XSS (cookies not accessible to JS)
- Token is briefly visible in React component tree (in memory only, not DOM)
- Requires Server Component wrapping the Client Component — always true with App Router layouts

### Pattern 2: Map-Based Brain Store with Immer

**What:** Store brains as `Map<string, BrainState>` with Immer middleware. Update individual
entries without touching others. Each node component uses a targeted selector.

**When to use:** Any time you have N independent entities that receive independent real-time
updates. Anti-pattern is an array with spread replacement.

**Trade-offs:**
- Zero cascade re-renders when one brain updates
- Immer enables direct mutation syntax (safer for Maps)
- Map is not JSON-serializable (no persist middleware on this store)

### Pattern 3: WS Pub/Sub Inside Zustand

**What:** The WS `onmessage` handler dispatches to a Map of typed listeners. Components/bridges
subscribe and unsubscribe in useEffect. Store manages the WebSocket lifecycle.

**When to use:** Multiple components need different WS event types without prop drilling or context
re-renders.

**Trade-offs:**
- Decouples WS from React tree (no re-render on every event)
- Subscribers self-manage (unsubscribe on unmount)
- Debugging requires Redux DevTools or console inspection

### Pattern 4: Stable Node Array + External State in Custom Nodes

**What:** React Flow's `nodes` array contains ONLY layout data (id, position, type). Live state
comes from useBrainStore inside each custom node component via targeted selector.

**When to use:** React Flow graphs with real-time node state updates.

**Trade-offs:**
- Eliminates the single biggest React Flow performance pitfall
- Custom node must be wrapped in `React.memo` and declared outside parent component
- NODE_TYPES object must be declared outside the parent component (prevents new reference)

---

## Data Flow

### Happy Path: User submits brief → brains execute → Nexus illuminates

```
1. User types brief → Command Center input
2. Server Action: POST /api/tasks → { task_id: "abc123" }
3. Client Component: useWSStore.connect("abc123", token)
4. WS open: ws://localhost:8000/ws/tasks/abc123?token=...
5. useBrainStore.setActiveTask("abc123", initialNodes)
6. WSBrainBridge subscriptions active

7. WS event: brain_step_started { brain_id: "brain-01" }
   → WSBrainBridge → handleBrainStarted("brain-01", ...)
   → Immer updates brains.get("brain-01").status = "running"
   → ONLY brain-01 BrainCard/BrainNode re-renders (targeted selector)

8. WS event: brain_step_completed { brain_id: "brain-01", output, duration_ms }
   → handleBrainCompleted → status = "completed"
   → brain-01 node turns green

9. WS event: execution_complete
   → useWSStore.disconnect()
```

### Auth Refresh Flow

```
1. proxy.ts intercepts request
2. jwtVerify(access_token) → throws (expired)
3. POST /api/auth/refresh with refresh_token cookie
4. New tokens received → set new cookies in response
5. Request continues → no user interruption
```

---

## Integration Points

### New vs Modified

| Component | Status | Notes |
|-----------|--------|-------|
| `apps/api/` | **UNCHANGED** | All endpoints already exist and work |
| `apps/web/proxy.ts` | **NEW** | Replaces middleware.ts — route protection |
| `apps/web/src/stores/ws-store.ts` | **NEW** | WS lifecycle + pub/sub |
| `apps/web/src/stores/brain-store.ts` | **NEW** | Brain states with Immer |
| `apps/web/src/components/ws-brain-bridge.tsx` | **NEW** | Bridges WS events to brain store |
| `apps/web/src/components/brain-node.tsx` | **NEW** | React Flow custom node |
| `apps/web/src/actions/auth.ts` | **NEW** | Server Actions for login/logout |
| `apps/web/src/lib/api.ts` | **NEW** | Server-only fetch utility |
| `docker-compose.yml` | **UNCHANGED** | web:3000 already configured |

### Backend Endpoints Required

| Endpoint | Status | Notes |
|----------|--------|-------|
| `POST /api/auth/login` | Exists | Returns `access_token` + `refresh_token` |
| `POST /api/auth/refresh` | Exists | Rotation implemented |
| `POST /api/tasks` | Exists | Returns `task_id` |
| `GET /api/tasks` | Exists | Pagination supported |
| `GET /api/tasks/{id}/graph` | Exists | Returns `nodes[]`, `edges[]` |
| `WS /ws/tasks/{id}?token=` | Exists | Throttled 300ms, Ghost Mode buffer |
| `GET /api/brains` | **MISSING** | Need to verify — Command Center needs brain list |

**Gap:** The `/api/brains` endpoint is not in the existing routes. The Command Center Bento Grid
needs to list all 24 brains with their current status. This endpoint must be added to the API
before Screen 2 can be completed.

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: middleware.ts (Next.js 15 pattern)

**What people do:** Create `middleware.ts` from tutorials written before Next.js 16.
**Why it's wrong:** Deprecated in Next.js 16. Renamed to `proxy.ts`, function renamed to `proxy()`.
The `edge` runtime is NOT supported in proxy. Code will still run (backward compat) but emits
deprecation warnings and the runtime constraint differs.
**Do this instead:** Use `proxy.ts` from day one.

### Anti-Pattern 2: Token in localStorage

**What people do:** Store JWT in `localStorage` for easy client-side access.
**Why it's wrong:** XSS vulnerable. Any injected script reads the token.
**Do this instead:** httpOnly cookies + token waterfall from Server Component layout.

### Anti-Pattern 3: Full Node Array Replacement on WS Event

**What people do:** `setNodes(nodes.map(n => n.id === updated.id ? {...n, data: newData} : n))`
**Why it's wrong:** Returns new array reference → React Flow reconciles all 24 nodes → 24
re-renders per WS event. At 300ms throttle and 24 parallel brains = potentially 80 re-renders
per second.
**Do this instead:** External store with Map + targeted selector per node. React Flow's node array
is layout-only and never changes after initial render.

### Anti-Pattern 4: useEffect WebSocket in a Component

**What people do:** `useEffect(() => { const ws = new WebSocket(...) }, [taskId])`
**Why it's wrong:** Creates new connection on every component mount. Navigation to another screen
and back = new connection. Parallel subscriptions from different components = multiple connections.
**Do this instead:** Module-level singleton in Zustand store. `connect()` is idempotent — checks
if same task is already connected before opening new socket.

### Anti-Pattern 5: useWSStore() without selector

**What people do:** `const wsStore = useWSStore()` (selects entire store)
**Why it's wrong:** Component re-renders on ANY store change, including `onmessage` firing for
every WS packet.
**Do this instead:** `const connect = useWSStore((s) => s.connect)` — select only what you need.
For multiple fields: `useShallow`.

---

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| Single user (v2.1) | Current design — sufficient. SQLite WAL, single WS per task. |
| 5-10 concurrent users | No changes needed. FastAPI async handles concurrent WS connections. |
| 50+ users | Replace SQLite with PostgreSQL. Add WS reconnection with exponential backoff. |
| Production hardening | nginx reverse proxy (eliminates CORS), HTTPS, rate limiting (v2.2 scope). |

---

## Open Gaps

1. **`GET /api/brains` endpoint:** The Command Center Bento Grid needs to list all 24 brains. This
   endpoint does not exist in the current API. The `brain_registry.py` file likely has the data;
   a new route must expose it.

2. **WS reconnection strategy:** The current WS store has no exponential backoff on disconnect.
   For v2.1 this is acceptable (local dev, no flaky network). For production (v2.2), implement
   reconnection with max retries.

3. **Token expiry during active WS session:** If the access_token expires while a WS connection
   is open, the next REST call will 401. The client needs a silent refresh hook. Acceptable to
   defer to v2.2 since tokens last 30 minutes and tasks typically complete faster.

4. **React Compiler stability:** Next.js 16 includes React Compiler (stable) but disabled by
   default. Custom React Flow nodes wrapped in `React.memo` PLUS React Compiler = double
   memoization. Enable React Compiler only after verifying no conflicts with `@xyflow/react`.

---

## Sources

**HIGH confidence (official documentation):**
- [Next.js 16 upgrade guide](https://nextjs.org/docs/app/guides/upgrading/version-16) — proxy.ts, async cookies, Turbopack default
- [React Flow state management](https://reactflow.dev/learn/advanced-use/state-management) — Zustand integration pattern
- [React Flow performance](https://reactflow.dev/learn/advanced-use/performance) — React.memo requirement, node re-render prevention
- [Zustand 5 patterns](https://github.com/pmndrs/zustand) — useShallow, immer middleware, module singleton

**MEDIUM confidence (verified against official + multiple sources):**
- JWT httpOnly cookie pattern for Next.js App Router — multiple 2026 sources consistent
- Zustand singleton for WS (module-level store survives navigation) — verified via zustand discussions
- Token waterfall (Server Component → Client Component prop) — official App Router patterns

**LOW confidence (single source or inference):**
- React Compiler + React.memo interaction with React Flow nodes — needs validation during build

---

*Architecture research for: MasterMind Framework v2.1 — Next.js 16 War Room Frontend*
*Researched: 2026-03-18*
*Confidence: HIGH*
