# Harness Escalation Policy

## 1. Propósito

Definir cuándo un flujo simple debe escalar a un harness más formal o a AI-DLC.

## 2. Tesis central

Escalar solo cuando el problema lo exige; no cuando el hábito lo sugiere.

## 3. Escalation triggers

Escalar si existe cualquiera de estos:

- evidencia contradictoria
- gaps críticos
- alta incertidumbre
- necesidad de entrevista
- riesgo alto
- necesidad de diseño o implementación
- necesidad de archive y lineage formal

## 4. Escalation ladder

### 4.1 Intake only

Cuando la fuente es clara y el objetivo es simple.

### 4.2 Intake + Canonization

Cuando hay valor, pero no hace falta entrevista.

### 4.3 Full Evidence Loop

Cuando faltan piezas o hay que validar.

### 4.4 Spec Generation

Cuando la evidencia ya es suficiente y se requiere una spec.

### 4.5 AI-DLC

Cuando además de la spec hace falta faseado, trazabilidad de desarrollo y cierre formal.

## 5. Escalation rule

Escalar al siguiente nivel solo si el nivel actual no puede garantizar:

- cobertura
- confianza
- trazabilidad
- control de riesgo

## 6. De-escalation rule

Bajar de nivel si:

- el problema era más simple de lo previsto
- ya no hay gaps críticos
- la evidencia se volvió suficiente
- el costo del workflow superó su valor

## 7. No-goals

- no escalar por nostalgia de proceso
- no bajar de nivel si aún hay riesgo real
- no mezclar decisión de workflow con preferencia personal
