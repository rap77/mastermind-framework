# Source Adoption and Review Cadence

## 1. Propósito

Definir cada cuánto y bajo qué disparadores se reevalúan las fuentes externas para que las decisiones no se vuelvan obsoletas.

## 2. Tesis central

Una adopción útil hoy puede dejar de serlo después de una nueva versión. La revisión debe ser periódica y también event-driven.

## 3. Disparadores de revisión

Revisar una fuente cuando ocurra cualquiera de estos eventos:

- nueva release o commit relevante
- cambio en capabilities detectadas
- cambio en seguridad o permisos
- cambio en costos de token o contexto
- cambio en compatibilidad con MasterMind
- nueva necesidad del producto
- feedback de uso real

## 4. Cadencia sugerida

### 4.1 Fuentes críticas

Revisión frecuente, porque impactan arquitectura o memory flow.

### 4.2 Fuentes tácticas

Revisión cuando cambian features, workflows o integrations.

### 4.3 Fuentes exploratorias

Revisión solo si siguen mostrando valor.

## 5. Resultado de revisión

Cada revisión debe cerrar con uno de estos resultados:

- mantener adopción
- adaptar de nuevo
- degradar a candidate
- marcar deprecated
- eliminar de la ruta activa

## 6. Regla de continuidad

Si una fuente se revisa varias veces, el sistema debe conservar:

- línea temporal de decisiones
- snapshots comparadas
- cambios de criterio
- razones de cambio

## 7. Relación con el core

La cadencia de revisión debe estar conectada al:

- Source Registry
- Capability Registry
- Memory Layer
- Harness Selector
- AI-DLC archive step

## 8. No-goals

- no revisar por moda
- no reabrir decisiones sin gatillo
- no perder el motivo histórico de una adopción
