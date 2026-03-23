# Brain-06 QA/DevOps — Phase 07: The Nexus

**Date:** 2026-03-22

---

## Testing Strategy (Pyramid)
- **70% Unit (Vitest)**: lógica pura de brainStore (Zustand + Immer), Map selectors (sin cascade re-renders), función de layout radial de dagre (posiciones estables), historyStack mutations
- **20% Integration**: Contract Testing WS events → brainStore → React Flow node illumination. Validar integración Zustand ↔ React Flow. Test persistencia de historyStack por WS event
- **10% E2E (Playwright)**: Ghost Architecture load desde `/api/brains`, transición idle→active (iluminación), Cooldown Mode shortcuts ([Enter]/[V]/[R]/[Esc])

## Key Test Scenarios
1. **NODE_TYPES stability** — verificar que cambiar BrainState NO causa re-mount del canvas
2. **Dagre stability** — posiciones de 24 nodos no cambian entre renders
3. **60fps regression** — k6 load test con 24 WS eventos simultáneos
4. **prefers-reduced-motion** — todas las animaciones se desactivan cuando el guard está activo
5. **nodrag nopan** — elementos interactivos dentro de nodos no triggean drag/pan del canvas

## CI/CD
- Stage 1 (Commit): lint + SAST + unit tests
- Stage 2 (Acceptance): env efímero + integration + E2E
- Stage 3 (Performance): k6 para latencia de renderizado del DAG

## SLOs
- 99.9% de WS events procesados y renderizados en < 16ms (60fps)
- CLS < 0.1 durante ejecución con 24 nodos simultáneos
