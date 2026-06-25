# Business Logic Model — UOW-5 Core Runtime Contracts

## Purpose

Definir la lógica de negocio que permite a MasterMind seleccionar el control
mínimo suficiente para una tarea mediante:

- `HarnessRegistry`
- `CapabilityRegistry`
- `LoopSelector`
- `EnvelopeContract`

## Core Workflow

1. **Perfilado de tarea**
   - Se deriva un `TaskProfile` desde el brief, flow, artefactos disponibles,
     tipo de cambio, riesgo y verificabilidad esperada.
   - El perfil clasifica la tarea como simple, media o compleja, y además
     determina si es sensible, destructiva, subjetiva o fácilmente verificable.

2. **Resolución de harnesses**
   - `HarnessRegistry` expone los harnesses soportados.
   - El runtime filtra harnesses incompatibles con la tarea actual.
   - El resultado no es “todos los harnesses”, sino el conjunto mínimo útil.

3. **Resolución de capabilities**
   - `CapabilityRegistry` agrega harnesses, loops, brains, skills, MCPs,
     verificadores y recovery policies bajo un mismo inventario consultable.
   - Cada capability declara metadatos:
     - objetivo
     - costo
     - riesgo
     - prerequisitos
     - compatibilidad
     - necesidad de fresh context
     - necesidad de checker separado

4. **Selección de loop**
   - `LoopSelector` aplica política de minimum sufficient control.
   - Reglas base:
     - tarea simple y determinística → `ToolLoop`
     - tarea con outcome verificable → `GoalLoop`
     - tarea no trivial → añade `VerificationLoop`
     - tarea subjetiva o de diseño → puede añadir `ReflectionLoop`
     - fallo estructural → activa `RecoveryLoop`
     - cambio riesgoso o no trivial → puede exigir `ReviewLoop`

5. **Construcción del envelope**
   - Cada harness/fase devuelve un `ExecutionEnvelope`.
   - El envelope permite decidir continuidad sin interpretar prosa libre.

6. **Decisión de continuidad**
   - El caller evalúa:
     - `status`
     - `verification`
     - `recovery`
     - `next_actions`
   - Si el envelope indica fallo recuperable, el runtime activa recovery.
   - Si el envelope indica aprobación y aceptación completa, el loop finaliza.

## Selection Logic

### Tool Loop

Usar cuando:
- la tarea es acotada
- no requiere branching dinámico
- el resultado es directamente observable

### Goal Loop

Usar cuando:
- la tarea requiere varias iteraciones
- existe una condición verificable clara
- el costo de iterar es aceptable

### Verification Loop

Usar cuando:
- el resultado no debe evaluarse por texto sino por evidencia ejecutable
- la tarea modifica código, contratos, configuración o behavior

### Reflection Loop

Usar cuando:
- la calidad puede mejorar con crítica/refinamiento
- la verificación objetiva no basta por sí sola
- la tarea involucra diseño, propuestas o diagnosis

### Recovery Loop

Usar cuando:
- aparece fallo estructural
- hay timeout, compile/test/runtime failure
- hay señales de no progreso

### Review Loop

Usar cuando:
- el maker no debe autoaprobarse
- el cambio es mediano/grande/riesgoso
- se requiere perspectiva fresh-context o adversarial

## Decision Boundaries

- `LoopSelector` elige control; no ejecuta trabajo.
- `CapabilityRegistry` resuelve inventario; no decide éxito.
- `EnvelopeContract` comunica outcomes; no decide políticas.
- `Verification` y `Review` producen evidence para finalización o recovery.

## Failure Modes To Prevent

1. **Un solo loop para todo**
   - produce overhead o insuficiente control según tarea.

2. **Un solo agente para todo**
   - mezcla ejecución, verificación y aprobación en la misma mente/contexto.

3. **Prosa libre como handoff**
   - hace que el orquestador adivine el siguiente paso.

4. **Recovery sin límites**
   - lleva a recursión descontrolada y gasto inútil.

5. **Inventario pasivo**
   - skills/MCPs/harnesses existen pero no influyen la selección real.
