# Stack Research: MasterMind Framework v2.1 Frontend

**Domain:** Real-time War Room Frontend (Next.js + React + Tailwind + Component Libraries)
**Researched:** 2026-03-17
**Confidence:** HIGH (Next.js 16, Tailwind 4, shadcn/ui — all verified via official docs and release notes)

> **Note:** This file replaces the v2.0 Python/FastAPI stack research for the current milestone.
> The backend stack (FastAPI, Pydantic, asyncio) is already validated and unchanged.
> This document covers ONLY the new `apps/web/` frontend.

---

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **Next.js** | 16.1.7 (latest patch) | React framework + App Router | Turbopack stable, React 19.2 built-in, Server Components + Client Components split for real-time UI |
| **React** | 19.2.x | UI runtime | Required by Next.js 16; includes ViewTransitions, `useEffectEvent`, `<Activity/>` |
| **TypeScript** | 5.1+ (required by Next.js 16) | Type safety | Minimum 5.1.0 per Next.js 16 breaking changes — use 5.9.x for latest |
| **Tailwind CSS** | 4.x | Styling | Configured in CSS only (@import syntax), no tailwind.config.js — breaking change from v3 |
| **shadcn/ui** | latest (Tailwind v4 mode) | Component primitives | CLI auto-detects Tailwind v4, outputs `new-york` style by default, OKLCH colors |
| **@xyflow/react** | 12.10.1 | DAG visualization | React Flow v12 — package renamed from `reactflow`, React 19 + Tailwind 4 native support |
| **Zustand** | 5.x | WebSocket dispatcher + client state | Single WS connection in store, per-component subscriptions via selectors |
| **Magic UI** | latest (Tailwind v4 mode) | Animated components (Bento Grid, Animated Beam, Orbiting Circles) | Copy-paste model via `magicui-cli`, Tailwind 4 + React 19 by default as of 2026 |

**Confidence:** HIGH — versions verified from official release notes and npm as of 2026-03-17

---

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **tw-animate-css** | latest | CSS animations | Replaces `tailwindcss-animate` — shadcn/ui deprecated tailwindcss-animate, tw-animate-css is the v4 default |
| **motion** (Framer Motion) | 11+ | Magic UI dependency | Magic UI installs via `magicui-cli`, which pulls motion for animated components |
| **clsx** | 2.x | Conditional className builder | Part of the `cn()` utility from shadcn/ui |
| **tailwind-merge** | 2.x | Merge Tailwind classes without conflicts | Used in `cn()` — prevents class collision when composing components |
| **lucide-react** | latest | Icon library | shadcn/ui default icon set — use latest for React 19 compatibility |
| **@radix-ui/*** | latest | shadcn/ui headless primitives | Update all `@radix-ui/*` packages when upgrading to Tailwind v4 |

---

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| **Turbopack** | Default bundler in Next.js 16 | Enabled by default — 2-5x faster builds, 10x faster Fast Refresh. Use `next dev --webpack` only if custom webpack plugin required |
| **ESLint (Flat Config)** | Linting | Next.js 16 defaults to ESLint Flat Config format — `eslint.config.mjs`, not `.eslintrc.json` |
| **@types/node** | Node.js type stubs | Required for `next.config.ts` |

---

## Installation

### Step 1 — Bootstrap Next.js 16 with Tailwind 4 and TypeScript

```bash
# In apps/web/ (already a placeholder dir)
npx create-next-app@latest . \
  --typescript \
  --tailwind \
  --app \
  --turbopack \
  --import-alias "@/*"
```

This generates: Next.js 16.x, React 19.2, TypeScript 5.x, Tailwind 4, App Router, Turbopack.

**Resulting package.json core deps:**
```json
{
  "next": "^16.1.7",
  "react": "^19.2.1",
  "react-dom": "^19.2.1",
  "typescript": "^5.9.3"
}
```

### Step 2 — Initialize shadcn/ui (Tailwind v4 mode)

```bash
# Inside apps/web/
npx shadcn@latest init -t next
```

The CLI detects Tailwind v4 automatically and configures:
- `globals.css` with `@import "tailwindcss"` and `@import "tw-animate-css"` (NOT `@tailwind base/components/utilities`)
- `@theme inline` block with OKLCH colors (NOT HSL variables in `:root`)
- `components.json` with `new-york` style by default (NOT `default` — deprecated in Tailwind v4)
- Deprecates `tailwindcss-animate` → installs `tw-animate-css`

**Add components as needed:**
```bash
npx shadcn@latest add button card dialog input label
```

### Step 3 — Initialize Magic UI

```bash
# Inside apps/web/ — after shadcn/ui is initialized
npx magicui-cli init
npx magicui-cli add bento-grid
npx magicui-cli add animated-beam
npx magicui-cli add orbiting-circles
```

Magic UI uses the same copy-paste model as shadcn/ui. Components land in `components/magicui/`. Dependencies installed: `motion` (Framer Motion v11+).

### Step 4 — React Flow

```bash
npm install @xyflow/react
```

**Critical CSS change for Tailwind 4:** Do NOT import `@xyflow/react/dist/style.css` in JSX. Import in `globals.css` instead:

```css
/* globals.css */
@import "tailwindcss";
@import "tw-animate-css";

@layer base {
  @import "@xyflow/react/dist/style.css";
}
```

### Step 5 — Zustand 5

```bash
npm install zustand
```

No additional plugins needed for basic WebSocket dispatcher pattern.

---

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| `next@16.x` | `react@19.2.x` | React 19.2 is bundled — install both to keep package.json accurate |
| `next@16.x` | `typescript@5.1+` | Hard minimum 5.1.0 — Next.js 16 breaking change |
| `next@16.x` | Node.js 20.9+ | Hard minimum 20.9.0 — Node.js 18 dropped |
| `tailwindcss@4.x` | No `tailwind.config.js` | v4 configured entirely in CSS — `tailwind.config.js/ts` is NOT used |
| `shadcn/ui` (Tailwind v4) | `tw-animate-css` | `tailwindcss-animate` is deprecated — shadcn auto-installs `tw-animate-css` |
| `@xyflow/react@12.x` | `react@18+` | React 18 and 19 both supported |
| `@xyflow/react@12.x` | Tailwind 4 | Import style.css in globals.css (not in App.tsx/layout.tsx) — breaking change from v11 |
| `shadcn/ui` components | `@radix-ui/*` latest | All Radix packages must be updated together when migrating to Tailwind v4 |
| `zustand@5.x` | Next.js App Router | Store must be defined outside `app/` dir (e.g. `lib/stores/`) — avoids SSR instantiation issues |
| `magic-ui` | `motion@11+` | Magic UI depends on Framer Motion v11 — verify no conflict with React 19 |

---

## Tailwind 4 Configuration (CRITICAL — Breaking Change from v3)

### globals.css structure (Tailwind v4 + shadcn/ui + React Flow)

```css
/* apps/web/app/globals.css */

/* 1. Tailwind v4 — replaces @tailwind base/components/utilities */
@import "tailwindcss";

/* 2. Animation library — replaces tailwindcss-animate */
@import "tw-animate-css";

/* 3. React Flow styles — must be in globals.css, NOT in layout.tsx */
@layer base {
  @import "@xyflow/react/dist/style.css";
}

/* 4. shadcn/ui theme — OKLCH colors, @theme inline (NOT :root + HSL) */
@theme inline {
  --radius-sm: calc(var(--radius) - 4px);
  --radius-md: calc(var(--radius) - 2px);
  --radius-lg: var(--radius);
  --color-background: oklch(1 0 0);
  --color-foreground: oklch(0.145 0 0);
  --color-primary: oklch(0.205 0 0);
  --color-primary-foreground: oklch(0.985 0 0);
  /* ... rest of shadcn/ui theme variables */
}
```

### What does NOT exist in Tailwind v4

| v3 concept | v4 replacement |
|------------|----------------|
| `tailwind.config.js` | CSS `@theme` directive in globals.css |
| `@tailwind base` | `@import "tailwindcss"` |
| `@tailwind components` | removed — handled by `@layer components` |
| `@tailwind utilities` | removed — handled by `@layer utilities` |
| `tailwindcss-animate` plugin | `tw-animate-css` package |
| PostCSS-only setup | `@tailwindcss/vite` plugin available (faster) |
| `:root` HSL variables | `@theme inline` with OKLCH |

---

## Next.js 16 Configuration (next.config.ts)

```typescript
// apps/web/next.config.ts
const nextConfig = {
  // Turbopack is default — no explicit config needed
  // Enable only if you need these features:
  reactCompiler: false,  // Keep false unless profiling shows gains; adds Babel overhead
  cacheComponents: false, // "use cache" directive — opt in per route when needed
};

export default nextConfig;
```

**Breaking change — proxy.ts replaces middleware.ts:**
```typescript
// apps/web/proxy.ts  (was middleware.ts)
// proxy.ts runs on Node.js runtime (not Edge)
import { type NextRequest, NextResponse } from "next/server";

export default function proxy(request: NextRequest) {
  const token = request.cookies.get("mm_token");
  if (!token && request.nextUrl.pathname.startsWith("/dashboard")) {
    return NextResponse.redirect(new URL("/login", request.url));
  }
  return NextResponse.next();
}
```

Note: `middleware.ts` still works in Next.js 16 (deprecated, not removed) — but new projects should use `proxy.ts`.

---

## Zustand 5 WebSocket Dispatcher Pattern

The single-connection WebSocket dispatcher stores the WS reference inside the Zustand store and routes events to state by event type.

```typescript
// apps/web/lib/stores/ws-dispatcher.ts
"use client";

import { create } from "zustand";
import { devtools } from "zustand/middleware";

type WsStatus = "disconnected" | "connecting" | "connected" | "error";

interface BrainStepEvent {
  type: "brain_step_completed";
  brain_id: string;
  step: number;
  output: string;
}

interface TaskStatusEvent {
  type: "task_status";
  task_id: string;
  status: "pending" | "running" | "completed" | "failed";
}

type WsEvent = BrainStepEvent | TaskStatusEvent | { type: "execution_complete"; task_id: string };

interface WsDispatcherStore {
  status: WsStatus;
  brainEvents: BrainStepEvent[];
  taskStatus: Record<string, TaskStatusEvent["status"]>;
  connect: (taskId: string, token: string) => void;
  disconnect: () => void;
}

let ws: WebSocket | null = null;

export const useWsDispatcher = create<WsDispatcherStore>()(
  devtools(
    (set) => ({
      status: "disconnected",
      brainEvents: [],
      taskStatus: {},

      connect: (taskId, token) => {
        if (ws) ws.close();
        set({ status: "connecting" });

        ws = new WebSocket(`ws://localhost:8000/ws/session/${taskId}?token=${token}`);

        ws.onopen = () => set({ status: "connected" });

        ws.onmessage = (event) => {
          const data: WsEvent = JSON.parse(event.data);
          if (data.type === "brain_step_completed") {
            set((state) => ({ brainEvents: [...state.brainEvents, data] }));
          }
          if (data.type === "task_status") {
            set((state) => ({
              taskStatus: { ...state.taskStatus, [data.task_id]: data.status },
            }));
          }
        };

        ws.onclose = () => set({ status: "disconnected" });
        ws.onerror = () => set({ status: "error" });
      },

      disconnect: () => {
        ws?.close();
        ws = null;
        set({ status: "disconnected" });
      },
    }),
    { name: "WsDispatcher" }
  )
);
```

**Component consumption pattern (select only what you need):**
```typescript
import { useShallow } from "zustand/react/shallow";
import { useWsDispatcher } from "@/lib/stores/ws-dispatcher";

// In a Client Component:
function BrainStatusCard({ brainId }: { brainId: string }) {
  const events = useWsDispatcher(
    useShallow((state) => state.brainEvents.filter((e) => e.brain_id === brainId))
  );
  // ...
}
```

---

## React Flow in App Router (Server/Client boundary)

React Flow requires a Client Component — it uses browser APIs and event listeners.

```typescript
// apps/web/components/nexus/dag-view.tsx
"use client";  // REQUIRED — React Flow is not SSR-compatible

import { ReactFlow, Background, Controls, MiniMap } from "@xyflow/react";
import { useDagStore } from "@/lib/stores/dag-store";

export function DagView() {
  const { nodes, edges, onNodesChange, onEdgesChange } = useDagStore(
    useShallow((s) => ({
      nodes: s.nodes,
      edges: s.edges,
      onNodesChange: s.onNodesChange,
      onEdgesChange: s.onEdgesChange,
    }))
  );

  return (
    <div className="h-full w-full">
      <ReactFlow nodes={nodes} edges={edges} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange}>
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  );
}
```

**Tailwind 4 + React Flow style collision prevention:**
- Import `@xyflow/react/dist/style.css` in `globals.css` inside `@layer base` — this ensures Tailwind's reset does not override React Flow's base styles
- React Flow uses CSS variables prefixed with `--xy-` — no collision with Tailwind or shadcn/ui theme variables
- Do NOT use `className` with React Flow internal components for layout/position — use the wrapper `div` with Tailwind classes instead

---

## shadcn/ui Inside React Flow Custom Nodes

This is a supported pattern — shadcn/ui components work inside React Flow custom nodes because they are Client Components.

```typescript
// apps/web/components/nexus/brain-node.tsx
"use client";

import { Handle, Position, type NodeProps } from "@xyflow/react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

type BrainNodeData = {
  brainId: string;
  brainName: string;
  status: "idle" | "running" | "completed" | "failed";
};

export function BrainNode({ data }: NodeProps<BrainNodeData>) {
  return (
    <>
      <Handle type="target" position={Position.Top} />
      <Card className="w-40 border-slate-700 bg-slate-900">
        <CardHeader className="pb-1 pt-3 px-3">
          <span className="text-xs text-slate-400">{data.brainId}</span>
        </CardHeader>
        <CardContent className="px-3 pb-3">
          <p className="text-sm font-medium text-white">{data.brainName}</p>
          <Badge
            className={cn(
              "mt-1 text-xs",
              data.status === "running" && "bg-blue-500",
              data.status === "completed" && "bg-green-500",
              data.status === "failed" && "bg-red-500"
            )}
          >
            {data.status}
          </Badge>
        </CardContent>
      </Card>
      <Handle type="source" position={Position.Bottom} />
    </>
  );
}
```

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| **Next.js 16 App Router** | Next.js 15 Pages Router | Never for new projects — App Router is the current standard |
| **Tailwind 4** | Tailwind 3 | If the project already has Tailwind 3 and migration cost is too high |
| **@xyflow/react 12** | `reactflow` 11 | Never for new projects — package renamed, v11 no longer maintained |
| **Zustand 5** | Redux Toolkit | RTK adds boilerplate; Zustand is idiomatic for single-app WebSocket state |
| **Zustand 5** | React Context + useReducer | Context re-renders ALL consumers; Zustand selectors prevent unnecessary re-renders |
| **Magic UI** | Framer Motion directly | Magic UI gives you pre-built animated components — use Framer Motion directly only for custom animations beyond what Magic UI provides |
| **shadcn/ui** | Chakra UI / MUI | shadcn/ui is copy-paste (you own the code), fully Tailwind 4 native, no runtime overhead |
| **tw-animate-css** | tailwindcss-animate | tailwindcss-animate is deprecated in Tailwind v4 context — tw-animate-css is the official replacement |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `reactflow` (old package) | Abandoned — last published 2 years ago (v11.11.4) | `@xyflow/react` v12 |
| `tailwindcss-animate` | Deprecated by shadcn/ui for Tailwind v4 — causes warnings | `tw-animate-css` |
| `tailwind.config.js` | Does not exist in Tailwind v4 | CSS `@theme` directive in globals.css |
| `import '@xyflow/react/dist/style.css'` in `.tsx` files | Breaks Tailwind 4 style cascade | Import inside `@layer base` in globals.css |
| `middleware.ts` in new code | Deprecated in Next.js 16 | `proxy.ts` with exported `proxy` function |
| `experimental.ppr` in next.config | Removed in Next.js 16 | `cacheComponents: true` (opt-in) |
| `experimental.turbopack` in next.config | Moved to top-level in Next.js 16 | `turbopack: {}` at root of config |
| `react@18` | Next.js 16 requires React 19 | `react@19.2.x` |
| Node.js 18 | Dropped by Next.js 16 | Node.js 20.9+ (LTS) |
| `serverRuntimeConfig` / `publicRuntimeConfig` | Removed in Next.js 16 | `.env` files + `NEXT_PUBLIC_*` prefix |
| Default shadcn style ("default") | Deprecated in Tailwind v4 shadcn/ui | "new-york" style |
| `useStore()` (select full store in Zustand) | Re-renders on any state change | Use selectors: `useStore((s) => s.specificField)` or `useShallow` |

---

## Stack Patterns by Variant

**For Server Components (data fetching, no real-time):**
- Use `async` page/layout components directly
- Fetch from FastAPI REST endpoints in the component body
- No Zustand, no hooks

**For Client Components (real-time, interactive):**
- Add `"use client"` directive
- Subscribe to Zustand store with selectors
- Never put WebSocket logic directly in a component — always via the WS dispatcher store

**For React Flow custom nodes:**
- Nodes are always Client Components
- Wrap in `"use client"` directive
- Use shadcn/ui components freely inside node — they work as regular React components
- Connect node status to the Zustand WS dispatcher store for live illumination

**For Magic UI Bento Grid:**
- Copy-pasted component lives in `components/magicui/bento-grid.tsx`
- Tailwind classes control grid layout — Tailwind 4 `grid-cols-*` syntax unchanged
- Animated transitions use `motion` (Framer Motion) — already installed by `magicui-cli`

---

## Version Compatibility Matrix (Full Stack)

| Package | Version | Node Required | React Required |
|---------|---------|---------------|----------------|
| `next` | 16.1.7 | 20.9+ | 19.2+ |
| `react` / `react-dom` | 19.2.1 | 20.9+ | — |
| `typescript` | 5.9.3 | — | — |
| `tailwindcss` | 4.x | — | — |
| `@xyflow/react` | 12.10.1 | — | 18+ |
| `zustand` | 5.x | — | 18+ |
| `tw-animate-css` | latest | — | — |
| `motion` (framer-motion) | 11+ | — | 18+ |
| `clsx` | 2.x | — | — |
| `tailwind-merge` | 2.x | — | — |

---

## Sources

- [Next.js 16 release blog](https://nextjs.org/blog/next-16) — Breaking changes, version requirements, proxy.ts, React 19.2 — HIGH confidence
- [Next.js 16.1 release blog](https://nextjs.org/blog/next-16-1) — Patch notes — HIGH confidence
- [shadcn/ui Tailwind v4 docs](https://ui.shadcn.com/docs/tailwind-v4) — Migration steps, tw-animate-css, OKLCH, new-york style — HIGH confidence
- [React Flow UI Tailwind 4 update](https://reactflow.dev/whats-new/2025-10-28) — CSS import change, shadcn/ui + React 19 update — HIGH confidence
- [Magic UI Tailwind v4 support](https://v3.magicui.design/docs/tailwind-v4) — Confirmed Tailwind 4 + React 19 default — MEDIUM confidence (page rendered as CSS, installation details from magicui-cli npm page)
- `@xyflow/react` npm + GitHub releases — v12.10.1 latest as of Feb 2025 — HIGH confidence
- [Zustand WebSocket integration discussion](https://github.com/pmndrs/zustand/discussions/1651) — Single connection + reducer pattern — MEDIUM confidence (community, not official docs)
- Skill files: `~/.claude/skills/nextjs-15/SKILL.md`, `~/.claude/skills/tailwind-4/SKILL.md`, `~/.claude/skills/zustand-5/SKILL.md` — Applied as coding standards

---

*Stack research for: MasterMind Framework v2.1 War Room Frontend*
*Researched: 2026-03-17*
*Confidence: HIGH*
