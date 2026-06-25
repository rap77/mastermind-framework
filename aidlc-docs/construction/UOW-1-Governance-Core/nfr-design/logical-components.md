# Logical Components — UOW-1 Governance Core

## 1. GovernanceInterceptor

### Responsibility
Punto de entrada que recibe la solicitud, construye la intención/contexto, ejecuta governance y decide si delega al `Coordinator`.

### Key NFR Role
- interceptación total
- backward compatibility
- enforcement de fail-closed

## 2. IntentionFactory

### Responsibility
Normalizar brief, acción y targets en una `Intention` consistente.

### Key NFR Role
- costo predecible
- inputs deterministas para las policies

## 3. TaskContextBuilder

### Responsibility
Construir `TaskContext` con scope, sensibilidad, approvals, dry-run y modo producción a partir del contexto ya disponible.

### Key NFR Role
- evita lookups remotos
- asegura datos mínimos de evaluación

## 4. PolicySet

### Responsibility
Mantener la colección ordenada de policies y ejecutar la cadena con short-circuit.

### Key NFR Role
- orden estable
- overhead controlado
- comportamiento observable testeable

## 5. Individual Policies

### Components
- `SecretPolicy`
- `ScopePolicy`
- `RiskPolicy`
- `ProductionWritePolicy`
- `MainBranchPolicy`
- `LargeChangePolicy`

### Responsibility
Aplicar reglas puras y devolver `PolicyResult`.

### Key NFR Role
- pureza
- determinismo
- aislamiento para unit tests

## 6. DecisionReducer

### Responsibility
Consolidar resultados de policy en una `GovernanceDecision` final.

### Key NFR Role
- separación clara entre evaluación y decisión final
- manejo explícito de `allow`, `deny`, `pause_and_ask`

## 7. EvidenceRedactor

### Responsibility
Limpiar snapshot y razones antes de persistir evidencia.

### Key NFR Role
- evita fuga de secretos
- protege la persistencia append-only

## 8. AuditWriter

### Responsibility
Persistir `AuditEvent` en JSON Lines append-only.

### Key NFR Role
- continuidad cross-session
- replayability
- condición bloqueante si falla

## 9. CoordinatorAdapter

### Responsibility
Delegar al `Coordinator` solo cuando existe `allow` y evidencia persistida correctamente.

### Key NFR Role
- evita bypass accidental
- mantiene aislada la integración con el runtime actual

## 10. Test Doubles Boundary

### Responsibility
Proveer seams para dobles de `AuditWriter`, builders y policies en pruebas.

### Key NFR Role
- facilita TDD en Code Generation
- permite probar fail-closed, ordering y short-circuit sin infraestructura real
