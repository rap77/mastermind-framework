# brain-06 QA/DevOps — Key Insights

**Score:** 9/10
**Verdict:** APPROVE

## Testing Strategy
- 70/20/10 Test Pyramid
- Playwright + CDP para medir fps
- k6 stress: 6 typical, 10 peak

## 3 Critical Scenarios
1. Carga inicial: 24 tiles render
2. Burst updates: 24 simultáneos + interacción
3. Reconexión WS: Sin pérdida de estado

## Deployment
- Canary/Blue-Green + Feature Flags
- 1% blast radius inicial
- Error Budget alerting

---
*Full context: BRAIN-06-QA-CONTEXT.md*
