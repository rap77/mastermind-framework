# Spec Generation Harness Spec

## 1. Propósito

Definir el harness que convierte evidencia canónica, gaps cerrados y respuestas del usuario en una especificación lista para implementación.

## 2. Tesis central

La especificación no debe inventar. Debe ensamblar lo ya verificado en una forma clara, accionable y trazable.

## 3. Precondiciones

El harness solo corre si:

- la evidencia fue canonizada
- los gaps críticos están cerrados
- la readiness verification dio `ready`
- hay source refs o decisiones trazables

## 4. Entradas

El harness acepta:

- objective
- canonical blocks
- resolved gaps
- user answers
- source refs
- constraints
- target audience
- token budget

## 5. Salidas

El harness debe producir:

- spec document
- scope
- requirements
- non-functional requirements
- assumptions
- exclusions
- acceptance criteria
- open questions residuales, si existen

## 6. Estructura mínima de la spec

### 6.1 Objective

Qué se quiere lograr.

### 6.2 Scope

Qué entra y qué no entra.

### 6.3 Canonical basis

Qué evidencia soporta la spec.

### 6.4 Requirements

Qué debe hacer el sistema.

### 6.5 Constraints

Qué límites aplican.

### 6.6 Acceptance criteria

Cómo se verifica que la spec está completa.

## 7. Reglas

- no agregar requisitos no respaldados
- no ocultar dudas resueltas a medias
- no mezclar especulación con evidencia
- no reabrir gaps cerrados sin razón
- no generar una spec si readiness no es `ready`

## 8. Token policy

- usar bloques canónicos pequeños
- citar solo lo necesario
- generar la spec en secciones compactas
- evitar repetir evidencia cruda

## 9. Relación con otros componentes

Este harness recibe output de:

- Evidence Intake Harness
- Gap Detection Loop
- Spec Readiness Verification Harness

Y entrega output a:

- AI-DLC Requirements / Design
- implementation planning
- archive step

## 10. No-goals

- no reemplazar la verificación
- no generar “specs bonitas” pero vacías
- no usar lenguaje ambiguo donde hace falta decisión
