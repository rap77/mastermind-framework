# Phase 05 — Brain Context (Momento 2)

**Brain consultado:** brain-04-frontend (via NotebookLM MCP)
**Fecha:** 2026-03-18
**Fase:** Foundation, Auth & WebSocket Infrastructure

---

## Output del Brain

### Framework
Next.js 16 + React 19 con App Router. React Server Components (RSC) como default — mejora LCP desplazando el data fetching al servidor y reduciendo el JS bundle al cliente. React 19 provee los primitivos para high-frequency updates y concurrent rendering.

### Component Hierarchy

**Pages:**
- `WarRoomPage` — Client Component (`'use client'`) que renderiza el canvas xyflow, integrado con `brainStore`
- `LoginPage` — Enfocada en el JWT Auth Gate, procesa credenciales y maneja el handshake con FastAPI

**Layouts:**
- `AuthGuardLayout` — Server Component que realiza JWT verification en cada request. Lee httpOnly cookies para storage seguro (mitiga XSS vs localStorage)
- `RootLayout` — Configuración global, metadata y font optimization para minimizar CLS

**Shared:**
- `WSBrainBridge` — Componente no-visual que actúa como pipeline entre WebSocket y `brainStore`. Los datos se validan via Zod schemas ANTES de actualizar el estado
- `FlowCanvas` — Wrapper especializado para @xyflow/react v12, optimizado con memoización y stable keys para node rendering

### State Management

Zustand 5, multi-store approach:
- **`wsStore`** — Maneja conectividad WebSocket y lazy initialization (no module-level side effects)
- **`brainStore`** — Lógica de dominio del War Room. Incorpora **RAF batching** para mensajes WS entrantes — Main Thread permanece responsivo, target INP < 200ms

### Styling

Tailwind 4 + shadcn/ui + Magic UI.
- **CRÍTICO:** React Flow CSS va únicamente en `@layer base` de `globals.css` — evita specificity wars con Tailwind 4
- Design Tokens via CSS Custom Properties — mantenibilidad y soporte de themes dinámicos

### Routing

App Router con nested layouts:
- `/` (War Room) — Dashboard autenticado principal con canvas @xyflow/react
- `/login` — Entry point del JWT auth flow

### Performance Targets

- **LCP < 2.5s** — Server Components para data fetching inicial + `<Image />` con `priority` para assets críticos
- **INP < 200ms** — RAF batching en `brainStore` previene que WS updates de alta frecuencia bloqueen la UI

### Build Tools

- **Zod** — Schema bridge entre Pydantic (FastAPI) y el frontend. Runtime validation en el boundary del sistema
- **npx shadcn@latest** — Installer principal que corrige el ENOENT de Magic UI

---

## Instrucción para el Planner

Al crear los planes de Phase 05, tener en cuenta:

1. `WSBrainBridge` valida con Zod ANTES de updatear Zustand — el schema bridge (SB-01) y el WS store son una sola pieza integrada
2. `AuthGuardLayout` es Server Component — JWT verification ocurre en el layout, no solo en proxy.ts
3. React Flow CSS en `globals.css @layer base` es el primer smoke test del Plan 05-01
4. `wsStore` usa lazy init — `connect()` action guarded por `typeof window !== 'undefined'`
5. RAF batching va en el `brainStore`, no en el WS event handler directamente
