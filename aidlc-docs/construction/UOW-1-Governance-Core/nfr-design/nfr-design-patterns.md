# NFR Design Patterns — UOW-1 Governance Core

## Purpose

Traducir los NFRs de UOW-1 a patrones lógicos que garanticen determinismo, seguridad, bajo overhead y trazabilidad sin romper el `Coordinator`.

## 1. Interceptor Boundary Pattern

### Pattern
`GovernanceInterceptor` envuelve el punto de entrada al `Coordinator` y actúa como única puerta de paso para intenciones evaluables.

### Applies To
- backward compatibility
- interceptación total de acciones de riesgo
- aislamiento del cambio

### Design Effect
- callers existentes pueden seguir usando `Coordinator` con `governance=None`
- cuando governance está habilitado, todo side effect potencial debe pasar por esta frontera

## 2. Ordered Policy Chain Pattern

### Pattern
`PolicySet` fijo y ordenado con evaluación secuencial.

### Applies To
- determinismo fuerte
- costo lineal y predecible
- short-circuit

### Design Effect
- el orden de policies es parte del comportamiento observable
- la primera policy con `deny` o `pause_and_ask` corta la cadena
- evita evaluación extra y protege el overhead <5%

## 3. Fail-Closed Guard Pattern

### Pattern
Toda incertidumbre crítica o falla de persistencia degrada a decisión bloqueante.

### Applies To
- seguridad
- continuidad
- trazabilidad mínima

### Design Effect
- datos insuficientes => `pause_and_ask`
- falla del audit writer => no delegar al `Coordinator`
- falla de una policy por condición insegura => nunca escalar a `allow`

## 4. Redact-Before-Persist Pattern

### Pattern
La evidencia se sanea antes de tocar el writer append-only.

### Applies To
- protección de secretos
- persistencia segura
- observabilidad sin fuga

### Design Effect
- tokens, cookies, headers y secretos equivalentes no llegan al storage
- la evidencia conserva `reason_code`, targets relevantes y snapshot seguro

## 5. Append-Only Audit Trail Pattern

### Pattern
Cada decisión produce `AuditEvent` inmutable en formato JSON Lines.

### Applies To
- replayability
- continuidad cross-session
- operabilidad mínima

### Design Effect
- permite reconstruir `intention -> policy -> verdict -> reason`
- habilita contadores por policy/veredicto sin infraestructura extra

## 6. Pure Policy Evaluation Pattern

### Pattern
Las policies no hacen side effects ni consultan red; solo evalúan `Intention` + `TaskContext`.

### Applies To
- determinismo
- testabilidad aislada
- performance

### Design Effect
- unit tests baratos y estables
- decisiones idénticas con mismo input
- menor latencia en el camino crítico

## 7. Explicit Approval Escalation Pattern

### Pattern
`pause_and_ask` representa riesgos aprobables; `deny` representa límites duros no sobreescribibles.

### Applies To
- large changes
- writes sensibles
- gobernanza humana controlada

### Design Effect
- el sistema distingue entre bloqueo definitivo y escalación humana
- una aprobación solo puede destrabar `pause_and_ask`, nunca un `deny`

## 8. Test Seam Pattern

### Pattern
Separar constructor de intención, chain de policies y writer de evidencia en seams testeables.

### Applies To
- TDD futuro
- integración incremental
- regresión controlada

### Design Effect
- tests unitarios por policy
- tests de integración para short-circuit y fail-closed
- posibilidad de usar doubles del audit writer sin tocar lógica de decisión
