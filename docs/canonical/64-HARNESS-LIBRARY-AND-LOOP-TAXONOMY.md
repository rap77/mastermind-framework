# Harness Library and Loop Taxonomy

## 1. Propósito

Definir la biblioteca de harnesses de MasterMind y la taxonomía de loops que el orquestador puede seleccionar según tarea, riesgo, costo y necesidad de verificación.

## 2. Idea central

MasterMind no usa un único método.
Selecciona el harness correcto y luego aplica el loop mínimo suficiente.

## 3. Harnesses canónicos

### 3.1 Discovery Harness

**Uso:** entender contexto, problema, restricciones y alcance.

**Entradas típicas:**

- objetivo del usuario
- repo/fuente
- señales iniciales
- constraints conocidas

**Salidas típicas:**

- summary del problema
- open questions
- source candidates
- next action recomendada

### 3.2 AI-DLC Harness

**Uso:** convertir una idea en requisitos, diseño, unidades, construcción, verificación y archivo.

**Entradas típicas:**

- objetivo
- scope
- contexto del proyecto
- restricciones

**Salidas típicas:**

- requirements
- design
- units
- plan de construcción
- verification notes
- archive notes

### 3.3 Research Harness

**Uso:** explorar fuentes, comparar repos, sintetizar patrones y producir artefactos canónicos.

**Entradas típicas:**

- URLs / repos / docs
- temas a comparar
- preguntas de investigación

**Salidas típicas:**

- source summary
- capability map
- adoption candidates
- anti-patterns
- delta notes

### 3.4 Design Harness

**Uso:** convertir objetivos en arquitectura, contratos, capacidades y dependencias.

**Entradas típicas:**

- requirements
- constraints
- current architecture

**Salidas típicas:**

- architecture decision
- component map
- contract outline
- implementation boundaries

### 3.5 Adaptive Delivery Harness

**Uso:** ejecutar DeliveryUnits trazables mediante domain adapters, producción,
verificación, integración, review y recovery.

`Implementation Harness` permanece como alias de compatibilidad para software.
La implementación concreta de código pertenece al `software-delivery` adapter,
no al core universal.

**Entradas típicas:**

- approved delivery intent
- delivery unit o task slice
- acceptance criteria
- domain adapter

**Salidas típicas:**

- produced artifacts
- unit e integration evidence
- acceptance verdict
- delivery/recovery notes

### 3.6 Verification Harness

**Uso:** comprobar que el resultado cumple el criterio esperado.

**Entradas típicas:**

- artifact
- acceptance criteria
- test commands

**Salidas típicas:**

- pass/fail verdict
- evidence
- gaps
- next actions

### 3.7 Review Harness

**Uso:** evaluación adversarial o fresh-context review.

**Entradas típicas:**

- diff
- design
- spec
- verification output

**Salidas típicas:**

- findings
- severity
- recommended fixes
- confidence

### 3.8 Recovery Harness

**Uso:** gestionar fallos, rollback, retries, replan y escalación.

**Entradas típicas:**

- failure report
- checkpoint
- recent history

**Salidas típicas:**

- recovery action
- retry plan
- rollback plan
- escalation note

### 3.9 Archive Harness

**Uso:** consolidar artefactos finales, decisiones y lecciones.

**Entradas típicas:**

- final diff
- verified outputs
- decisions

**Salidas típicas:**

- archived summary
- canonical links
- memory write request

### 3.10 Maintenance Harness

**Uso:** housekeeping, updates incrementales y delta review.

**Entradas típicas:**

- repo state
- updates
- external deltas

**Salidas típicas:**

- maintenance report
- dependency notes
- action list

## 4. Loop taxonomy

### 4.1 Tool Loop

Tareas pequeñas y determinísticas.

**Criterios:**

- una acción clara
- bajo riesgo
- sin necesidad de review profundo

### 4.2 Goal Loop

Iteración hasta una condición verificable.

**Criterios:**

- objetivo medible
- aceptación clara
- cierre por evidencia

### 4.3 Verification Loop

Validación externa del resultado.

**Criterios:**

- criterio explícito
- evidencia ejecutable
- falla si no hay proof

### 4.4 Reflection Loop

Crítica y refinamiento cuando la calidad lo exige.

**Criterios:**

- ambigüedad
- calidad insuficiente
- necesidad de mejorar claridad o cobertura

### 4.5 Recovery Loop

Retry, patch, replan o escalación.

**Criterios:**

- fallo repetido
- estado inconsistente
- checkpoint disponible

### 4.6 Review Loop

Maker-checker, evaluación adversarial o fresh-context review.

**Criterios:**

- cambio medianamente riesgoso o mayor
- necesidad de second opinion
- salida sensible

### 4.7 Heartbeat Loop

Monitoreo o automatización recurrente.

**Criterios:**

- periodicidad definida
- output pequeño
- propósito de observabilidad o recordatorio

### 4.8 Canonization Loop

Iteración cerrada para convertir contexto en canon canónico con recomendación, aceptación, ejecución y resumen final auditable.

**Criterios:**

- el usuario quiere aceptar recomendaciones durante la canonicación
- la tarea termina con un resumen completo de decisiones y acciones
- el siguiente paso debe quedar explícito al cierre

**Salidas típicas:**

- recommendation
- applied changes
- decisions made
- final summary
- next recommendation

## 5. Reglas de selección

- No todo necesita multi-agent.
- No todo necesita review.
- No todo necesita AI-DLC.
- Tareas simples usan Tool Loop.
- Tareas complejas usan combinaciones de loops.
- Cambios de alto riesgo requieren checker separado.
- Tareas de investigación usan Research Harness antes de Implementation.
- Tareas con muchas decisiones usan Discovery + Design antes de construir.

## 6. Selector mínimo suficiente

El orquestador debe escoger el menor conjunto que satisfaga:

- complejidad
- riesgo
- verificabilidad
- costo de tokens
- necesidad de checker separado
- necesidad de MCP
- necesidad de memoria histórica
- reuso posterior

## 7. Outputs esperados por harness

Cada harness debe producir un envelope con, como mínimo:

- status
- summary
- artifacts
- risks
- next_actions
- verification
- recovery

## 8. Criterios de diseño

- contratos claros
- límites explícitos
- artefactos persistibles
- bajo consumo de tokens
- trazabilidad
- reutilización
- selección por objetivo, no por preferencia personal
