# Canonicalization Completion Criteria

## 1. Propósito

Definir cuándo un bloque de canonicación puede considerarse completo y listo para pasar a implementación o a una nueva tanda de refinamiento.

## 2. Tesis central

La canonicación termina cuando el canon, el loop de trabajo y el resumen final ya dejan poca o ninguna ambigüedad operativa.

## 3. Criterios de completitud

### 3.1 Canon coverage

- los docs canónicos relevantes existen
- las relaciones entre docs están explicitadas
- los criterios de selección y cierre están definidos

### 3.2 Runtime coverage

- el comportamiento canónico tiene runtime mínimo o contrato claro
- el flujo de lectura/escritura está definido
- los deltas y lineage quedan persistidos

### 3.3 Review coverage

- cada ciclo deja resumen final
- las decisiones relevantes quedan auditablemente capturadas
- el siguiente paso recomendado queda explícito

### 3.4 Readiness coverage

- se puede decir qué está listo y qué no
- la frontera entre canonicación e implementación está clara
- no quedan huecos críticos de interpretación

## 4. Exit conditions

El bloque puede darse por completo si:

- no hay decisiones canónicas abiertas
- el loop de canonicación está formalizado
- el resumen final está estandarizado
- el handoff a implementación está definido

## 5. Handoff a implementación

Cuando se cumpla lo anterior, el siguiente trabajo debe ser:

- convertir el canon en slices de implementación
- mapear services/tables/jobs/MCPs
- priorizar el primer slice mínimo viable

## 6. No-goals

- no declarar completo un bloque con ambigüedad operativa fuerte
- no pasar a implementación sin handoff claro
- no confundir “mucho texto” con completitud real
