# Spec Readiness Verification Harness

## 1. Propósito

Verificar que la base canónica, la evidencia y las respuestas del usuario son suficientes para escribir una especificación sin huecos críticos.

## 2. Tesis central

Antes de especificar, el sistema debe demostrar que entiende el problema, sus límites y sus decisiones clave.

## 3. Cuándo se usa

Este harness se ejecuta:

- después de evidence intake
- después de gap detection
- después de clarifications
- antes de la spec

## 4. Criterios de readiness

La especificación solo puede avanzar si:

- el objetivo está claro
- los límites están claros
- las capacidades relevantes están identificadas
- los gaps críticos están cerrados
- las alternativas principales tienen criterio de decisión
- el nivel de confianza es suficiente

## 5. Flujo

### 5.1 Check completeness

Verificar cobertura funcional, estructural, de datos y NFR.

### 5.2 Check consistency

Verificar que no existan contradicciones entre fuentes o respuestas.

### 5.3 Check confidence

Confirmar que la evidencia es suficiente para especificar con bajo riesgo.

### 5.4 Check traceability

Confirmar que cada decisión tiene fuente, delta o respuesta asociada.

### 5.5 Verdict

Emitir uno de estos estados:

- ready
- not_ready
- needs_more_evidence
- needs_user_interview

## 6. Salidas

El harness debe devolver:

- readiness verdict
- missing items
- risk summary
- rework suggestions
- next action

## 7. Regla de bloqueo

Si hay gaps críticos abiertos, la spec no se genera.

## 8. Relación con otros componentes

Este harness cierra el flujo entre:

- intake
- gap detection
- user interview
- canonicalization
- spec generation

## 9. No-goals

- no aprobar una spec por intuición
- no ocultar gaps debajo de texto genérico
- no confundir abundancia de texto con readiness real
