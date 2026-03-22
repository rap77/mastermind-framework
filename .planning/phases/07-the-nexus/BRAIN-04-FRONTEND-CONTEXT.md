# Brain-04 Frontend — Phase 07: The Nexus

**Date:** 2026-03-22

---

## Framework
Next.js 16 App Router + React 19. RSC para fetchear Ghost Architecture inicial via `GET /api/brains` (minimiza JS cliente). React 19 Suspense para manejar WS bursts sin bloquear main thread.

## Routing
- `app/(protected)/nexus/page.tsx` — War Room canvas principal
- Parallel Routes (@sidepanel) para el Sheet sin desmontar el canvas ni cortar WS

## Component Hierarchy
- **NexusCanvas** (`@xyflow/react`): dagre radial layout calculado UNA SOLA VEZ en mount. Posiciones fijadas post-cálculo (`draggable: false`). WS updates solo tocan la prop `data` de los nodos via Zustand selectors — NUNCA recalcular layout en updates
- **BrainNode**: `React.memo` — solo re-renderiza si su `BrainState` en el Map cambia. `nodrag nopan` en elementos internos
- **NODE_TYPES declarado a module level** (fuera del componente) — evita re-renders infinitos del canvas (NEX-01 crítico)

## State Management
- **TanStack Query**: initial brain config + Ghost Architecture loading state (caching automático)
- **Zustand 5 + Immer**: `brainStore` con `Map<brainId, BrainState>` para O(1) lookups. `historyStack` array para Ghost Trace
- **RAF batching**: ya probado en Phase 05 — mantener mismo pattern

## Styling
- Idle nodes: `opacity-20 border-dashed`
- Active neon glow: `shadow-[0_0_15px_var(--brain-color)]` (Tailwind 4 arbitrary values)
- Niche colors via CSS Custom Properties (`--brain-08-hub`, `--niche-software`, etc.) — escalable para dark mode y high-contrast

## Performance Targets
- **60fps**: RAF batching + transiciones solo con `transform`/`opacity` (GPU compositor, no layout recalculation)
- **CLS < 0.1**: posiciones de nodos latched post-dagre. Cero re-layouts en WS updates
- **Web Worker**: si `historyStack` processing supera 16ms, moverlo a worker

## Critical Implementation Notes
- `NODE_TYPES` DEBE ser constante a nivel de módulo, NO inline en JSX
- Dagre corre una vez al montar con los 24 nodos del blueprint; posiciones se guardan en Zustand
- Para el Side Panel: Parallel Routes `@sidepanel` evita desmontar el canvas al navegar
