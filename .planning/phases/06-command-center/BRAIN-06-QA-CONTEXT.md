# brain-06 (QA/DevOps) — Phase 06 Command Center Consultation

**Date:** 2026-03-20
**Brain:** brain-06-qa-devops
**Notebook:** 74cd3a81-1350-4927-af14-c0c4fca41a8e

---

## Testing Strategy

**Whole-team approach** + **Shift-left testing** + **70/20/10 Test Pyramid**

**Performance:** Iterativo, integrado en pipeline. SLOs: p99 > 55fps, latencia < 200ms.

---

## Unit Testing (70%)

**Framework:** Vitest/Jest para lógica de datos de 24 tiles.

**Pattern:** "Seams" para romper dependencias, testear transformación WebSocket sin conexión real.

**Test-first:** Código testeable desde concepción.

**Goal:** Tests en milisegundos, feedback inmediato.

---

## Integration Testing (20%)

**Enfoque:** Cliente WebSocket ↔ gestor de estado.

**RAF Batching Verification:**
- Mock requestAnimationFrame
- Verificar: múltiples mensajes en mismo tick = un solo render combinado

**Contratos:** Esquema mensajes = expectativas frontend.

---

## E2E Testing (10%)

**Framework:** Playwright para flujos críticos.

### Medición 60fps
- Chrome DevTools Protocol (CDP) vía Playwright
- Capturar trazas durante burst updates
- Test falla si p99 < 55fps

### Escenarios Críticos
1. **Carga inicial:** 24 tiles con datos
2. **Burst Updates:** 24 simultáneos + interacción
3. **Reconexión WS:** Sin pérdida de estado

---

## CI/CD Pipeline

### Stage 1 (Commit)
Compilación + Unit Tests + SAST (SonarQube)

### Stage 2 (Acceptance)
Integration + Playwright E2E (fps measurement, headless)

### Stage 3 (Performance)
k6 stress tests WebSocket

### Stage 4 (Deploy)
Trunk-Based Development (main daily)

---

## k6 Configuration

```javascript
export const options = {
  stages: [
    { duration: '1m', target: 6 },   // Typical load
    { duration: '3m', target: 6 },
    { duration: '1m', target: 10 },  // Peak
    { duration: '2m', target: 10 },  // Stress
    { duration: '1m', target: 0 },
  ],
  thresholds: {
    'ws_connecting_duration': ['p(99)<200'],
  },
};
```

---

## Monitoring

**Observability Engineering:** Descubrir unknown-unknowns.

- **SLOs:** p99 fps + latencia desde RUM
- **Alerting:** Error Budget (1% para 99% fps >55)
- **Logs:** IDs correlación para trazar cliente→servidor

---

## Deployment

**IaC:** Staging = producción.

**Canary/Blue-Green + Feature Flags:**
- 1% usuarios inicialmente
- Monitorear performance (blast radius)
- Rollout total después de validación

**Inmutabilidad:** Servidores como "Cattle", reemplazados cada deploy.

---

## Answers to Questions

### Q1: ¿Cómo medir fps en tests?
**Playwright + CDP.** Trazas performance + assert p99 > 55fps.

### Q2: ¿Conexiones WS simultáneas en k6?
**6 típico, 10 peak.** p(99) < 200ms threshold.

### Q3: ¿Testear RAF batching?
**Mock RAF + verificar** múltiples mensajes = un render.

### Q4: ¿Flows críticos Playwright?
**3 scenarios:** Carga inicial, Burst updates, Reconexión.

---

*Saved: 2026-03-20*
