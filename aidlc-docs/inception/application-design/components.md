# Components

## 1. CoordinatorAdapter
- **Purpose**: envolver el borde del `Coordinator` sin romper la interfaz pública.
- **Responsibilities**:
  - recibir `brief` + contexto de ejecución
  - construir `Intention`
  - invocar governance antes de delegar
  - pasar control al `Coordinator`

## 2. HarnessRegistry
- **Purpose**: fuente tipada de verdad para los harnesses soportados por MasterMind.
- **Responsibilities**:
  - registrar harnesses disponibles
  - declarar responsabilidades y contratos
  - exponer compatibilidad con loops y capacidades

## 3. LoopSelector
- **Purpose**: elegir el loop mínimo suficiente para la tarea.
- **Responsibilities**:
  - clasificar complejidad/riesgo/verificabilidad
  - seleccionar loop base
  - decidir composición de loops adicionales
  - imponer límites de iteración/costo/tiempo

## 4. EnvelopeContract
- **Purpose**: contrato transversal de salida entre fases/harnesses.
- **Responsibilities**:
  - estandarizar `status`, `summary`, `artifacts`, `risks`,
    `next_actions`, `verification` y `recovery`
  - evitar dependencia en prosa libre

## 5. GovernanceInterceptor
- **Purpose**: chain of responsibility determinista para policies.
- **Responsibilities**:
  - ejecutar policies en orden
  - consolidar veredictos
  - activar audit trail
  - devolver `allow`, `deny`, `pause_and_ask`

## 6. PolicySet
- **Purpose**: agrupar reglas específicas.
- **Subcomponents**:
  - `ScopePolicy`
  - `RiskPolicy`
  - `SecretPolicy`
  - `MainBranchPolicy`
  - `LargeChangePolicy`
  - `ProductionWritePolicy`

## 7. BudgetEnforcer
- **Purpose**: controlar consumo proyectado y real.
- **Responsibilities**:
  - evaluar pre-call
  - registrar post-call
  - emitir warnings/gates/stops
  - consultar estado de task/session budget

## 8. EvidenceChainWriter
- **Purpose**: persistir eventos append-only.
- **Responsibilities**:
  - escribir JSON Lines de governance
  - escribir eventos de budget
  - exponer lectura básica para morning report y meta-loop

## 9. ExecutionHarness
- **Purpose**: encapsular ejecución real de trabajo sobre código/artefactos.
- **Responsibilities**:
  - ejecutar pasos de implementación con aislamiento suficiente
  - producir artifacts y evidence
  - devolver envelope tipado

## 10. VerificationHarness
- **Purpose**: validar estado logrado con evidencia ejecutable.
- **Responsibilities**:
  - correr tests/lint/typecheck/checks
  - evaluar criterios de aceptación verificables
  - devolver veredicto independiente del maker

## 11. ReviewHarness
- **Purpose**: ejecutar maker-checker / review adversarial.
- **Responsibilities**:
  - revisar correctness, architecture, security y performance
  - operar con fresh context cuando aplique
  - devolver issues accionables y decisión de aprobación

## 12. RecoveryHarness
- **Purpose**: manejar fallos estructurales sin recursión descontrolada.
- **Responsibilities**:
  - local retry
  - local patch
  - request replan
  - escalate / stop

## 13. EvalHarnessService
- **Purpose**: ejecutar retrieval eval sobre corpus estable.
- **Responsibilities**:
  - cargar corpus indexado
  - cargar qrels sellados
  - calcular scorecards
  - comparar contra baseline

## 14. QrelGenerationSupport
- **Purpose**: ayudar a generar candidatos de qrels.
- **Responsibilities**:
  - extraer decisiones/fixes/temporal candidates desde docs
  - producir candidatos para validación humana

## 15. CapabilityRegistry
- **Purpose**: inventario dinámico de capacidades operativas del sistema.
- **Responsibilities**:
  - indexar harnesses, loops, brains, skills, MCPs, commands, verificadores y
    recovery policies
  - exponer metadatos de costo, riesgo, prerequisitos y compatibilidad
  - permitir selección contextual por objetivo

## 16. OvernightSupervisor
- **Purpose**: ejecutar modo nocturno cauteloso.
- **Responsibilities**:
  - secuenciar una tarea por vez
  - escribir checkpoint
  - consultar governance/budget/backend health
  - producir morning report

## 17. ResumeCheckpointStore
- **Purpose**: resumir estado de overnight y sesiones largas.
- **Responsibilities**:
  - guardar task completada, pendientes, fallos y budget restante
  - proveer snapshot para reanudación humana
