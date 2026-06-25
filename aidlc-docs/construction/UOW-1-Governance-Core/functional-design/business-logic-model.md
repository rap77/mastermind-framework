# Business Logic Model — UOW-1 Governance Core

## Purpose

Definir la lógica de evaluación determinista que inspecciona una intención de ejecución y decide si puede delegarse al `Coordinator`.

## Core Workflow

1. **Construcción de intención**
   - Se deriva una `Intention` desde el brief, la acción solicitada, los targets y el contexto de tarea.
   - La intención es el objeto normalizado que todas las policies inspeccionan.

2. **Construcción de contexto**
   - Se construye `TaskContext` con:
     - scope permitido
     - tipo de tarea
     - sensibilidad de archivos/rutas
     - presupuesto estimado
     - estado de approvals
     - flags de dry-run/producción

3. **Evaluación secuencial de policies**
   - Las policies se ejecutan en orden fijo.
   - La primera policy que devuelve `deny` o `pause_and_ask` corta la cadena.
   - Si ninguna policy bloquea, el veredicto final es `allow`.

4. **Persistencia de evidencia**
   - Toda evaluación produce evento auditable, incluso si el resultado es `allow`.
   - El evento contiene:
     - intención evaluada
     - policy disparada
     - veredicto
     - razón
     - timestamp

5. **Delegación condicional**
   - Solo `allow` delega al `Coordinator`.
   - `pause_and_ask` devuelve control al caller sin ejecutar.
   - `deny` finaliza la acción solicitada con mensaje y evidencia.

## Evaluation Order

Orden recomendado:

1. `SecretPolicy`
2. `ScopePolicy`
3. `RiskPolicy`
4. `ProductionWritePolicy`
5. `MainBranchPolicy`
6. `LargeChangePolicy`

## Decision Logic

### Allow
- la intención cae dentro del scope
- no expone secretos
- no ejecuta acción destructiva prohibida
- no toca producción o ramas protegidas sin autorización
- no supera umbrales de cambio sensible

### Pause and Ask
- el cambio es grande/sensible pero no intrínsecamente prohibido
- la acción excede un threshold aprobable
- falta aprobación humana requerida

### Deny
- la intención viola una policy dura
- intenta operar fuera del scope
- intenta tocar secretos o credenciales
- intenta ejecutar operaciones irreversibles o de alto riesgo prohibidas

## Coordination Boundary

- El modelo es **technology-agnostic** respecto a archivos reales, red o base de datos.
- La resolución de “qué se intenta hacer” ocurre antes de cualquier side effect.
- La persistencia de evidencia es una consecuencia del veredicto, no un insumo para decidir.
