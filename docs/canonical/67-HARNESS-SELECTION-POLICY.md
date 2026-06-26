# Harness Selection Policy

## 1. Propósito

Definir cómo MasterMind elige el harness y el loop mínimo suficiente para cada objetivo.

## 2. Principio rector

> No se selecciona un harness por preferencia. Se selecciona por utilidad, riesgo, verificabilidad y costo de tokens.

## 3. Variables de selección

El selector debe considerar:

- complejidad
- riesgo
- verificabilidad
- coste de tokens
- necesidad de revisión separada
- necesidad de MCP
- necesidad de memoria histórica
- necesidad de recuperación
- necesidad de investigación externa
- necesidad de construcción de código

## 4. Regla general

1. Resolver el objetivo con el harness más simple posible.
2. Escalar solo si el objetivo lo exige.
3. Añadir review o verification solo cuando aporten evidencia útil.
4. Evitar multi-agent si el trabajo se puede cerrar con un loop simple.

## 5. Mapeo recomendado por situación

### 5.1 Descubrimiento o ambigüedad alta

Usar:

- Discovery Harness
- Goal Loop

### 5.2 Investigación externa

Usar:

- Research Harness
- Verification Loop

### 5.3 Diseño de arquitectura o contrato

Usar:

- Design Harness
- Reflection Loop

### 5.4 Implementación de código

Usar:

- Implementation Harness
- Goal Loop
- Verification Loop

### 5.5 Cambio riesgoso o sensible

Usar:

- Implementation Harness
- Review Harness
- Verification Harness
- Recovery Harness si falla

### 5.6 Cambio pequeño y determinístico

Usar:

- Tool Loop
- Maintenance Harness si hace falta

### 5.7 Cierre y preservación

Usar:

- Archive Harness

### 5.8 Recuperación de fallo

Usar:

- Recovery Harness
- Verification Harness

## 6. AI-DLC como opción, no obligación

AI-DLC se usa cuando:

- hay que pasar por discovery → design → implementation → verification → archive
- el cambio afecta varios componentes
- hay documentación o trazabilidad fuerte requerida
- conviene estructurar el trabajo en slices

AI-DLC no se usa cuando:

- la tarea es trivial
- el cambio es pequeño y aislado
- la verificación es directa y barata
- el overhead del workflow sería mayor que su beneficio

## 7. Reglas de escalación

Escalar a un harness más pesado cuando:

- hay incertidumbre relevante
- hay riesgo alto
- hay múltiples dependencias
- el costo de error es alto
- el cambio será reutilizado
- hay necesidad de auditoría o approval

## 8. Reglas de desescalación

Bajar a un harness más simple cuando:

- la tarea se aclaró
- la evidencia ya es suficiente
- el problema quedó acotado
- el overhead del workflow ya no compensa

## 9. Salida del selector

El selector debe devolver un envelope con:

- harness elegido
- loop elegido
- razones
- riesgos
- alternativa descartada
- next actions

## 10. No-goals

- no forzar AI-DLC para todo
- no usar review en tareas triviales
- no usar research si ya hay evidencia suficiente
- no usar multi-agent cuando un solo harness basta
