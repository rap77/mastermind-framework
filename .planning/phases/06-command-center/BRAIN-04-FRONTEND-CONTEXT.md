# brain-04 (Frontend) — Phase 06 Command Center Consultation

**Date:** 2026-03-20
**Brain:** brain-04-frontend
**Notebook:** 85e47142-0a65-41d9-9848-49b8b5d2db33

---

## Framework Validation

**Next.js 16 + React 19** está validado para su uso de Server Components (RSC) como default, lo cual reduce el bundle de JavaScript del cliente y mejora LCP (Largest Contentful Paint) manejando data fetching en el servidor.

**React 19's concurrent features** son esenciales para mantener una UI responsiva durante procesamiento pesado de streams WebSocket.

---

## Component Hierarchy

### Pages
- **CommandCenterDashboard**: Root layout implementando `BentoGrid` y manejando el lifecycle de conexión WebSocket
- **BrainFocusView**: Vista especializada triggered por `layoutId` transitions para deep inspection de un solo nodo

### Layout
- **BentoGridContainer**: Usa **CSS Grid** (`grid-template-areas`) para 2D semantic clustering de nichos
- **NicheCluster**: Component de grouping lógico que mapea un niche slice específico del `brainStore`

### Shared
- **BrainTile**: Unidad interactiva individual usando `useBrainState(id)` para subscribirse solo a updates relevantes
- **StatusSentinel**: Región `aria-live` accesible que anuncia cambios críticos de WebSocket status a screen readers

---

## State Management

**Zustand 5 (Client State) + TanStack Query (Server State)**

Siguiendo el principio de separar server y client state:
- **TanStack Query** manejará metadata "Brain" y nichos iniciales
- **Zustand 5** maneja updates de WebSocket de alta frecuencia en tiempo real

**brainStore structure:**
```typescript
Map<string, Brain[]>  // keys are niche IDs
```

Esto habilita lookups O(1) para clustering y previene el anti-patrón "mega-store".

**Critical:** Access a tiles individuales debe usar selectores atómicos como `useBrainState(id)` para asegurar que solo la tile específica re-render cuando sus datos cambian, manteniendo 60fps.

---

## Styling Approach

**Tailwind CSS 4 + shadcn/ui + Framer Motion**

Tailwind 4 provee un engine de utility de alta performance para el layout BentoGrid.

**BorderBeam Effect:**
- **Recomendación:** CSS-only implementation (usando `@keyframes` y `conic-gradient` en pseudo-element)
- **NO usar:** Magic UI's JavaScript-heavy approach
- **Razón:** Mantiene la animación en el compositor thread del browser

**Focus Elevation (2x1 → 2x2):**
- **Recomendación:** Framer Motion's `layoutId`
- **Razón:** Usa técnica FLIP para animar cambios de layout smoothly sin cálculo manual de coordenadas

---

## Routing Strategy

Next.js App Router usando convención file-based:
- `/dashboard`: Main Command Center con full BentoGrid
- `/dashboard?focus={id}`: Focused state utilizando **URL State** para asegurar que la view es bookmarkable y persiste a través de reloads

---

## Performance Targets

### Target 60fps
Implementar **RAF (requestAnimationFrame) batching** para WebSocket updates. Procesar 24 tiles simultáneamente es escalable si updates son batched en un solo render cycle cada 16.6ms, evitando congestión del **Main Thread**.

### INP (Interaction to Next Paint) < 200ms
Usar React 19's `useTransition` cuando se filtran nichos para asegurar que la UI permanezca responsiva a user clicks durante recalculaciones pesadas de layout.

---

## Build Tools

- **Vite/Next Compiler:** Para HMR (Hot Module Replacement) rápido durante desarrollo
- **ESLint 9+ (Flat Config):** Configurado con `react-hooks/exhaustive-deps` para prevenir infinite re-render loops en WebSocket effects

---

## Key Insights for Phase 06

### Q1: BorderBeam (Magic UI) vs CSS-only para 60fps?
**Respuesta:** **CSS-only es superior.** Magic UI usa JavaScript que puede bloquear el main thread. CSS `@keyframes` corre en el compositor thread.

### Q2: ¿Cómo estructurar brainStore para niche clustering?
**Respuesta:** `Map<string, Brain[]>` donde keys son niche IDs. Esto permite O(1) lookups y previene mega-store anti-pattern.

### Q3: ¿Framer Motion layoutId es útil para Focus Elevation?
**Respuesta:** **SÍ, altamente recomendado.** Usa FLIP technique para animar layout changes sin cálculo manual de coordenadas.

### Q4: ¿RAF batching de Phase 05 escala a 24 tiles?
**Respuesta:** **SÍ, si se implementa correctamente.** 24 updates simultáneos en un solo render cycle (16.6ms) es escalable. Critical: usar selectores atómicos `useBrainState(id)` para prevenir re-renders en cascada.

---

## Implementation Recommendations

1. **BentoGrid layout:** CSS Grid con `grid-template-areas` para 2D semantic clustering
2. **brainStore:** `Map<nicheId, Brain[]>` con selectores atómicos
3. **Animaciones:** CSS-only para BorderBeam, Framer Motion para layout transitions
4. **WebSocket:** RAF batching probado en Phase 05 escala a 24 tiles
5. **Performance:** Target 60fps con `useTransition` para filtros de nichos

---

*Output saved: 2026-03-20*
*Notebook: 85e47142-0a65-41d9-9848-49b8b5d2db33*
