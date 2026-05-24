# Window Scheduler Architecture

## 1. Propósito

Definir la arquitectura canónica para la capacidad de MasterMind que orquesta múltiples cuentas, proveedores y modelos cuando existen ventanas limitadas de disponibilidad, especialmente bajo suscripciones con límites temporales.

El objetivo es permitir que el sistema:

- detecte agotamiento de ventanas
- estime y registre cuándo vuelve a estar disponible un backend
- haga checkpoint antes de cambiar
- cambie al siguiente backend elegible
- pause o continúe según la política activa
- deje un rastro auditable para revisión posterior

---

## 2. Definición

> El Window Scheduler es la capa del core responsable de administrar capacidad temporal de ejecución entre múltiples backends, preservando continuidad de trabajo, gobernanza y trazabilidad.

---

## 3. Problema que resuelve

MasterMind no solo necesita elegir un modelo o proveedor. También necesita administrar:

- cuentas distintas dentro del mismo proveedor
- backends con límites por ventana temporal
- backends con costos o riesgos distintos
- continuidad de tareas largas o nocturnas
- cambios automáticos sin pérdida de contexto

Sin esta capa, la estrategia multi-LLM queda incompleta.

---

## 4. Lugar en la arquitectura general

El Window Scheduler pertenece al **core reutilizable** y no al Project Adapter.

### Relación con otras capas

- **Platform Architecture Brain**: define límites entre scheduler, adapters y runtime
- **Agent Runtime & LLM Ops Brain**: dueño principal de la estrategia
- **Governance & Safety Brain**: define gates, pausas y límites
- **Product Operations Brain**: define experiencia de uso y reportes humanos
- **Minimal Memory Rules**: gobierna checkpoints y recuperación
- **Minimal Orchestration Path**: gobierna cuándo y cómo reanudar trabajo

---

## 5. Componentes principales

### A. Provider Registry

Mantiene el inventario de backends disponibles.

Cada entrada debe incluir como mínimo:

- `backend_id`
- `provider`
- `account_id`
- `auth_mode` (`subscription`, `api_key`, `hybrid`)
- `model_family`
- `priority`
- `cost_tier`
- `risk_tier`
- `overnight_allowed`
- `automatic_switch_allowed`
- `human_confirmation_required`

### B. Availability Tracker

Mantiene el estado operativo y temporal de cada backend.

Debe registrar:

- estado actual
- inicio de ventana observada
- agotamiento observado
- próximo reset estimado
- última verificación exitosa
- confianza de la estimación

### C. Eligibility Engine

Decide qué backends son elegibles para una tarea determinada según:

- modo de ejecución activo
- tipo de tarea
- costo permitido
- riesgo permitido
- restricciones del proyecto
- disponibilidad actual

### D. Switch Policy Engine

Aplica la política de orden y cambio entre backends.

Debe decidir:

- cuándo seguir en el backend actual
- cuándo cambiar automáticamente
- cuándo pausar
- cuándo escalar al usuario
- cuándo reintentar un backend agotado

### E. Checkpoint Manager

Crea un checkpoint obligatorio antes de un cambio de backend.

Debe capturar:

- tarea actual
- subpaso actual
- resumen mínimo del contexto
- outputs parciales
- decisiones ya tomadas
- archivos relevantes
- siguiente paso recomendado

### F. Resume Manager

Reconstruye el estado mínimo necesario para que el siguiente backend continúe.

Debe usar:

- checkpoint estructurado
- contexto resumido
- referencias a artefactos del proyecto
- política de rehidratación mínima

### G. Audit Logger

Registra todo evento importante del scheduler.

Debe producir eventos como:

- `window_started`
- `window_exhausted`
- `backend_switch`
- `pause_for_user`
- `automatic_resume`
- `retry_scheduled`
- `all_backends_blocked`

### H. Morning Report Generator

Genera un resumen humano de lo ocurrido en ejecuciones automáticas.

Debe incluir:

- backends usados
- switches realizados
- checkpoints creados
- errores o bloqueos
- tiempos estimados de reactivación
- estado final
- siguiente acción sugerida

---

## 6. Modelo de datos mínimo

### BackendSession

```yaml
backend_session:
  backend_id: "claude-sub-01"
  provider: "claude"
  account_id: "personal-main"
  auth_mode: "subscription"
  model_family: "claude"
  status: "available"
  priority: 10
  cost_tier: "low"
  risk_tier: "medium"
  overnight_allowed: true
  automatic_switch_allowed: true
  human_confirmation_required: false
```

### AvailabilityState

```yaml
availability_state:
  backend_id: "claude-sub-01"
  state: "active"
  window_started_at: "2026-05-23T00:05:00-04:00"
  window_exhausted_at: null
  estimated_reset_at: null
  estimation_confidence: "unknown"
  last_verified_at: "2026-05-23T01:10:00-04:00"
```

### SchedulerEvent

```yaml
scheduler_event:
  event_id: "evt-204"
  type: "backend_switch"
  project_id: "mastermind"
  run_id: "night-run-001"
  from_backend: "claude-sub-01"
  to_backend: "codex-sub-01"
  reason: "window_exhausted"
  checkpoint_id: "chk-099"
  created_at: "2026-05-23T02:14:00-04:00"
```

### RunPolicy

```yaml
run_policy:
  execution_mode: "hybrid"
  max_switches_per_run: 6
  allow_paid_api_fallback: false
  overnight_mode: true
  require_human_for_high_risk_actions: true
  max_cost_tier: "medium"
```

---

## 7. Estados del sistema

### Estados por backend

- `available`
- `active`
- `exhausted`
- `cooling_down`
- `paused`
- `disabled`
- `blocked`

### Estados por ejecución

- `running`
- `checkpointing`
- `switching_backend`
- `waiting_for_window`
- `paused_for_user`
- `completed`
- `failed`

---

## 8. Flujo principal

```text
Start run
→ Select eligible backend
→ Execute work
→ Detect exhaustion or stop condition
→ Create checkpoint
→ Log event
→ Evaluate next backend
→ Switch / Pause / Wait
→ Resume from checkpoint
→ Continue until completion or blocked state
```

---

## 9. Detección de agotamiento

La detección puede venir por varias vías.

### A. Señal explícita del proveedor

Cuando el proveedor devuelve un error o estado claro de límite agotado.

### B. Heurística observada

Cuando no existe señal formal y el sistema infiere agotamiento por comportamiento repetido.

### C. Configuración manual asistida

Cuando el usuario o proyecto declara supuestos iniciales sobre la ventana.

### Regla

La arquitectura debe permitir las tres y registrar qué tipo de evidencia respalda la estimación de reset.

---

## 10. Política de switching

El cambio de backend nunca debe ocurrir sin:

1. checkpoint
2. evento de auditoría
3. reevaluación de elegibilidad
4. validación del modo de ejecución

### Orden sugerido

1. backend actual si sigue elegible
2. siguiente subscription elegible
3. fallback API elegible si la política lo permite
4. pausa o espera si no hay backend aceptable

---

## 11. Interacción con modos de ejecución

El scheduler no decide solo. Debe obedecer la política activa.

### Pause and Ask

- checkpoint
- registrar causa
- pausar
- pedir confirmación humana

### Automatic Cycle

- checkpoint
- registrar reset estimado
- cambiar al siguiente backend elegible
- continuar automáticamente

### Hybrid

- cambiar automáticamente dentro de límites permitidos
- pausar si el siguiente paso cruza costo, riesgo o gobernanza definida

---

## 12. Guardrails mínimos

- máximo de switches por ejecución
- límite configurable de costo
- límite configurable de riesgo
- prohibición de cambiar sin checkpoint
- acciones de alto riesgo siempre pausable
- si todos los backends están bloqueados, generar pausa limpia y reporte

---

## 13. Trazabilidad obligatoria

Cada transición debe dejar evidencia suficiente para responder:

- qué backend estaba activo
- por qué se agotó o cambió
- qué tarea estaba en curso
- qué checkpoint se creó
- a qué backend se pasó
- por qué ese backend era elegible
- qué queda pendiente

---

## 14. Reporte matutino mínimo

Toda ejecución nocturna automática debe producir un resumen con:

- backends usados y duración aproximada
- puntos de agotamiento
- próximos resets estimados
- checkpoints relevantes
- errores
- bloqueos
- decisión final del scheduler
- siguiente acción sugerida para el operador humano

---

## 15. Límites de esta capa

El Window Scheduler no debe:

- redefinir doctrina de un brain
- decidir calidad del output por sí mismo
- saltarse la gobernanza del proyecto
- ejecutar acciones de alto riesgo sin respetar la policy activa

Su responsabilidad es **capacidad temporal y continuidad operativa**, no juicio de negocio o calidad final.

---

## 16. Riesgos principales

### Riesgo 1
Cambios automáticos que pierdan continuidad por checkpoints pobres.

### Riesgo 2
Estimaciones de reset demasiado optimistas.

### Riesgo 3
Costos inesperados al caer en fallbacks pagos.

### Riesgo 4
Automatización nocturna sin reporte confiable.

### Riesgo 5
Demasiada lógica local en project adapters en lugar de core reusable.

---

## 17. Decisiones canónicas derivadas

### Decisión 1
La gestión de ventanas de suscripción es parte del core runtime.

### Decisión 2
No puede existir switch automático sin checkpoint y auditoría.

### Decisión 3
La elegibilidad de backend depende de policy, no solo de disponibilidad.

### Decisión 4
La experiencia nocturna requiere un reporte matutino de primer nivel.

---

## 18. Relación con DR-002

Este documento cumple el Gate 1 definido en:

- `docs/canonical/decision-records/DR-002-SUBSCRIPTION-WINDOW-STRATEGY.md`

Los siguientes gates relacionados son:

- política explícita de modos de ejecución
- garantía de checkpoint + audit event por switch

---

## 19. Próximos artefactos recomendados

1. `17-EXECUTION-MODES-POLICY.md`
2. `DR-003-BACKEND-SWITCH-AUDIT-MINIMUMS.md`
3. `WINDOW-SCHEDULER-DATA-SCHEMA.md`
4. `MORNING-REPORT-TEMPLATE.md`

## Key Learnings:

1. El problema real no es elegir un modelo, sino administrar capacidad temporal entre múltiples backends con continuidad y control.
2. El checkpoint obligatorio antes de cada switch es la pieza más crítica del diseño.
3. La auditoría y el reporte matutino son tan importantes como el failover mismo para generar confianza operativa.
