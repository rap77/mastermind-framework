# Technical Debt & Improvements — Post Phase 06

**Source:** Brain-07 Final Evaluation (9.5/10)
**Status:** Non-blocking recommendations for 10/10 score
**Date:** 2026-03-20

---

## Non-Blocking Recommendations

### 1. Empty States (Cold Start Problem) — Priority: MEDIUM

**Description:**
Asegúrate de que el Command Center tenga una UI diseñada para cuando el usuario tiene **cero cerebros**. Evita el sentimiento de "producto vacío" proporcionando un path claro de creación.

**Implementation:**
- [ ] Diseñar UI de "Empty State" para Command Center
- [ ] Agregar mensaje claro: "No tienes cerebros configurados aún"
- [ ] Proporcionar botón CTA: "Agregar primer cerebro" o "Configurar nicho"
- [ ] Considerar ilustración o icono para reducir fricción visual

**Reference:** Brain-07 cita "Cold Start Problem" — evitar sentimiento de producto vacío

**When to implement:** Phase 08 (UX Polish) o post-v2.1

---

### 2. Graceful Degradation — Priority: HIGH

**Description:**
Dado que ahora tienes SLIs para el WebSocket, define qué sucede visualmente cuando el SLO de latencia se rompe (ej: ¿un indicador de "Slow Connection" o un fallback a polling?).

**Implementation:**
- [ ] Definir comportamiento cuando `message_latency_p99 > 200ms`
- [ ] Agregar indicador visual de "Slow Connection" (toast/banner)
- [ ] Implementar fallback a polling si WS disconnects
- [ ] Considerar modo offline con cache local
- [ ] Testear con Network Throttling en Chrome DevTools

**SLI Triggers:**
- `connection_success_rate < 99%` → Reconnect indicator
- `message_latency_p99 > 200ms` → Slow mode warning
- `reconnection_rate > 0.1/min` → Unstable connection banner

**Reference:** websocket-metrics.ts (WS_SLOS)

**When to implement:** Phase 08 (UX Polish) o post-v2.1

---

## Future Enhancements (Not Debt)

### 3. Cluster-Level Animations (ICE Deferred)

**Status:** DEFERRED per ICE Scoring (ICE ≤ 6)

**Rationale:**
Cluster-level decorative animations (glow, scan) no pasaron el filtro ICE porque:
- Impact: Bajo (decorativo, no reduce esfuerzo del usuario)
- Confidence: Medio (depende de preferencias visuales)
- Ease: Medio (requiere testing de performance)

**Future consideration:**
Si usuarios lo solicitan explícitamente, re-evaluar con datos de uso real.

**When to revisit:** Post-v2.1 basado en user feedback

---

## Tracking

| Item | Priority | Phase | Status |
|------|----------|-------|--------|
| Empty States | MEDIUM | 08 or post-v2.1 | Pending |
| Graceful Degradation | HIGH | 08 or post-v2.1 | Pending |
| Cluster Animations | LOW | Post-v2.1 | Deferred (ICE) |

---

## Notes

- Estas recomendaciones vienen de Brain-07 (Critical Evaluator)
- Son **no bloqueantes** para Phase 06 execution
- Deben implementarse basándose en **user feedback** y **datos de producción**
- Graceful Degradation tiene mayor prioridad porque afecta UX cuando hay problemas de red

---

*Created: 2026-03-20*
*Source: BRAIN-07-FINAL-EVALUATION.md*
*Brain-07 Score: 9.5/10 — APPROVED*
