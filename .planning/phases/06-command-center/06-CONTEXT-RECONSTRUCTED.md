# Phase 06 Command Center — CONTEXT RECONSTRUCTED

**Date:** 2026-03-20
**Status:** Reconstructed from session memories
**Source:** session/2026-03-20-phase06-discussion-complete + session/2026-03-20-phase06-brain-consultation-complete

---

## From Session: 06-Discussion (Momento 1)

### Layout del Bento Grid
- **Dynamic Semantic Clusters:** Master como "Sol" central (tile 2x2)
- **Nichos orbitan alrededor:** Software (7), Marketing (16), Master (1)
- **Hybrid Smart Spacing:** gap-2 intra-nicho, gap-8 inter-nicho
- **Interactive Pulse Mode (mobile):** Lista prioritaria en móvil

### Contenido del Brain Tile
- **Ghost Context:** Minimalista en reposo, reveal on hover
- **Semantic Polymorphism:** Métricas inteligentes por tipo (LLM→tokens, Script→progreso)
- **Focus Elevation:** Active expande 2x1 o 2x2 con Framer Motion layoutId
- **Tactical Quick-Actions:** STOP/FOLLOW LOGS (active), RETRY/CONFIG (idle)

### Animaciones de Estado
- **Adaptive Cyberpunk:** Reposo minimalista → Acción con neones
- **Neural Pulse:** Icono+punto laten asíncronamente (0.4↔1.0 opacity)
- **Pulse & Flow:** BorderBeam velocidad ∝ carga (tokens/seg)
- **Glitch & Static:** Shake + parpadeo rojo/cyan → borde rojo pulsante

### Modal de Brief Input
- **Semantic Auto-Expand:** Single-line → Shift+Enter expande a textarea (máx 400px)
- **Hierarchical Smart-Select:** @nichos → @nichos/cerebro específico
- **Intent-Aware Context:** /comandos con payload, color cambia según tipo
- **Semantic Execution Ghost:** Footer con avatares [📢 Marketing x16], peso tarea, dry run path

---

## From Session: Brain Consultation (Momento 2)

### brain-02 (UX Research) Insights
- **Miller's Law Risk:** 24 tiles vs 5-9 working memory items
- **Recommendation:** Progressive disclosure por nicho (no tile-level)
- **Key Insight:** "Niche-level disclosure significantly superior to tile-level"

### brain-04 (Frontend) Insights
- **Next.js 16 + React 19** patterns validated
- **Zustand 5 + TanStack Query** for data fetching
- **60fps target** with RAF batching
- **React.memo** for preventing cascade re-renders

### brain-05 (Backend) Insights
- **Clean Architecture** for FastAPI
- **Models:** Brain, BrainStatusUpdate, CommandCenterRegistry
- **JWT RS256** for authentication
- **WebSocket** schema for real-time updates

### brain-06 (QA/DevOps) Insights
- **Test Pyramid:** 70% unit, 20% integration, 10% E2E
- **SLOs:** p99 latency < 200ms, p99 > 55fps for UI
- **Playwright E2E** for critical flows
- **k6 stress testing** for WebSocket load

---

## Brain-07 Evaluation (Momento 3 - Initial)

### Initial Verdict: REJECT
**Premisa INCORRECTA:** "24 tiles always visible + 24 WebSockets always active"
- **Planning Fallacy:** Asumió 24 conexiones simultáneas
- **Memory Leak Risk:** Sin gestión de conexiones

### User Clarification (CRITICAL)
**Usuario:** "No se usan los 24 cerebros en una interacción — el ORQUESTADOR decide cuáles"

### Architecture Correction
- **Orquestador (brain-08)** decide QUÉ cerebros (3-6 típicos)
- **Nichos como unidades de progressive disclosure**
- **Max concurrent WebSockets:** 3-6 (típico), 8-10 (peak) — NOT 24
- **Solo cerebros ACTIVOS** se destacan visualmente
- **WebSocket lifecycle:** Orquestador managea connect/disconnect

---

## Brain-07 Re-evaluation (Momento 3 - Revised)

### Final Verdict: ✅ CONDITIONAL APPROVAL (8.5/10)

### 4 Conditions (Non-blocking for Phase 06)
1. **Guardrail Metrics para Orquestador** — Hard cap concurrent brains
2. **Pre-mortem selection logic + Manual Override** — Human intervention
3. **Checklist + Anti-patrones implementation** — Safety mechanisms
4. **Reference Class Forecasting para UI scalability** — Data-driven projections

### Key Insights
- "Niche-level progressive disclosure is significantly superior to tile-level"
- Orquestador-driven architecture resolves all initial concerns
- 60fps target is valid for war room visual feedback

---

## Pending Questions for Re-consultation

### To brain-02 (UX Research)
1. ¿Ghost Context + reveal on hover es suficiente para Miller's Law?
2. ¿Mobile: Lista prioritaria es mejor que mini-grid?

### To brain-04 (Frontend)
1. ¿BorderBeam (Magic UI) vs CSS-only para 60fps?
2. ¿Cómo extender brainStore para nicho clustering?
3. ¿Framer Motion layoutId para Focus Elevation?

### To brain-05 (Backend)
1. ¿GET /api/brains: 24 brains simultáneos o paginado?
2. ¿Sequence_number handling en WebSocket events?

### To brain-06 (QA/DevOps)
1. ¿Cómo testear RAF batching a 60fps?
2. ¿k6 stress test para WebSocket: cuántas conexiones simultáneas?

---

## Next Step

**Re-consultar los 4 brains técnicos** con preguntas específicas + obtener outputs completos guardados en archivos.
