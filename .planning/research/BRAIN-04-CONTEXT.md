# Frontend Brain Context — War Room Frontend v2.1
**Brain:** brain-04-frontend
**Brief:** War Room Frontend — 4 screens

## FRAMEWORK

Next.js 16 (App Router) with React 19. This architecture leverages React Server Components (RSC) as the default to minimize client-side JavaScript bundle sizes and improve Largest Contentful Paint (LCP) [1, 2]. React 19 is selected for its advanced support for Concurrent Features, Server Actions for data mutations, and enhanced hook stability [3, 4].

## COMPONENT HIERARCHY

{'pages': ['**CommandCenterPage:** Implements a **Bento Grid** using Magic UI, integrating the `cmdk` palette for a global "quick action" layer with strict **Focus Management** for accessibility [18, 19].', '**NexusFlowPage:** High-performance **DAG visualization** using `@xyflow/react` v12. Node processing for complex flows should be offloaded to **Web Workers** if execution logic exceeds 16ms to maintain a responsive UI [20, 21].', '**StrategyVaultPage:** A searchable history view using **Server Components** for initial data fetching and **Suspense** for streaming search results [4, 22].', '**EngineRoomPage:** Real-time log streaming via **WebSocket** integrated with `react-logviewer`, utilizing **Virtualization** (via `react-virtual` or similar) to handle high-frequency log updates without crashing the browser [23, 24].'], 'layout': ['**SidebarLayout:** A persistent navigation shell that manages the **Auth Boundary**. Authentication uses **JWT** with access tokens in memory (Zustand) and refresh tokens in **HttpOnly cookies** to mitigate XSS risks [25, 26].', "**ErrorContainmentZones:** Independent **Error Boundaries** wrapping each of the 4 screens to ensure a failure in the Nexus DAG doesn't crash the Command Center [27, 28]."], 'shared': ['**CommandPalette (`cmdk`):** A globally accessible interface using **Keyboard-first navigation** and ARIA live regions to announce search results to screen readers [29, 30].', '**TypeSafeDataTable:** A generic table component for the Strategy Vault using **TypeScript Discriminated Unions** to handle `loading`, `error`, and `success` states without impossible state overlaps [31, 32].']}

## STATE MANAGEMENT

Hybrid Client/Server State approach. Use Zustand 5 for global Client State (e.g., the open/closed state of the `cmdk` palette, layout preferences, and UI toggles) because it is lightweight and avoids Redux-level boilerplate [5, 6]. Use TanStack Query v5 for Server State (history, logs, and brain outputs) to manage caching, deduplication, and automatic invalidation [7, 8]. Real-time WebSocket streams for the Nexus and Engine Room will be encapsulated in Custom Hooks to manage lifecycle and cleanups [9, 10].

## STYLING APPROACH

Tailwind CSS 4 with shadcn/ui and Magic UI. Styling will rely on CSS Custom Properties for design tokens to ensure maintainability and seamless Dark Mode support [11, 12]. Components will follow the Compound Component Pattern for maximum flexibility in the Bento Grid layout [13, 14]. All layouts will implement `box-sizing: border-box` globally to prevent common layout bugs [15].

## ROUTING STRATEGY

Next.js App Router using file-based routing and URL-first state for filters and search in the Strategy Vault [16, 17].
- `/` (Command Center): Entry point with Bento Grid.
- `/nexus`: DAG visualization.
- `/vault`: Brain outputs history.
- `/engine`: Real-time monitoring.

## PERFORMANCE TARGETS

- **LCP < 2.5s:** Achieved by prioritizing "above-the-fold" images in the Command Center and using **Next.js Image** for automatic WebP conversion and space reservation to prevent **Cumulative Layout Shift (CLS)** [36-38].
- **INP < 200ms:** Ensuring interactions remain "instant" by using **useTransition** for heavy state updates and avoiding long tasks on the main thread [39, 40].

## BUILD TOOLS

- **ESLint 9+ (Flat Config):** Enforcing `react-hooks/exhaustive-deps` and `@typescript-eslint/no-explicit-any` to maintain code quality [10, 33].
- **Husky & lint-staged:** Pre-commit hooks to run **TypeScript** verification (`tsc --noEmit`) and linting before any code reaches the repository [34, 35].

## GENERATED AT

2026-03-18 16:25:57.754093
