# Brain-04 (Frontend) — Phase 06 Technical Context

**Generated:** 2026-03-20
**Source:** MasterMind CLI orchestrate (brain-04-frontend)

## Framework & Stack

**Next.js 16 (App Router) + React 19**
- React Server Components (RSC) para grid rendering inicial (mejora LCP)
- Streaming con Suspense para alta concurrencia de 24 brains
- `useTransition` para UI responsiva durante actualizaciones intensas

## Component Hierarchy

**Pages:**
- `WarRoomDashboard`: Bento Grid con dynamic semantic clustering (Master como "Sol") usando CSS Grid `auto-fit` y `minmax`
- `BrainDetailModal`: Dialog accesible con Focus Trap y cmdk shortcuts

**Layout:**
- `CommandCenterLayout`: Root shell con Command Palette y WebSocket provider
- `ClusterGroup`: CSS Grid Areas para agrupar brains en "orbits" semánticas (Software, Marketing)

**Shared:**
- `BrainTile`: Componente polimórfico con Framer Motion para "Ghost Context" transitions, `layoutId` para smooth reordering
- `ActivityMonitor`: Feedback visual con `aria-live` para screen readers

## State Management

**Hybrid: Zustand 5 + TanStack Query v5**
- Zustand 5: `brainStore` (Map-based) para client state y clustering, selectors para prevenir re-renders innecesarios
- TanStack Query: Server state (GET /api/brains) con caching, deduplication, sync con FastAPI

## Styling Approach

**Tailwind CSS 4 + shadcn/ui + Magic UI**
- Tailwind 4: Foundation utility-first para Adaptive Cyberpunk theme
- CSS Custom Properties: Dynamic neon shifts basados en activity levels
- Magic UI BorderBeam: `will-change: transform` para mantener neones off main thread

## Routing Strategy

**File-based App Router con parallel/intercepted routes:**
- `/command-center`: War Room view con Bento Grid
- `/command-center/[brainId]`: Detail view como intercepted modal

## Performance Targets

- **INP < 200ms**: `useTransition` para evitar bloquear main thread
- **60fps Fluidity**: Animaciones restringidas a `opacity` y `transform` (no layout reflows)
- **Risk Assessment**:
  - Memory Leaks: 24 WebSocket listeners → AbortController cleanup
  - Cognitive Load: `prefers-reduced-motion` guard
  - Race Conditions: TanStack Query cache como single source of truth

## Build Tools

- Next.js Turbo: HMR rápida y compilación rápida
- Lighthouse CI: Performance budgets enforcement
