# Evidence Criteria Matrix

## 1. Propósito

Definir criterios concretos para elegir el harness correcto y decidir si avanzar, detenerse o escalar.

## 2. Tesis central

MasterMind debe usar el workflow más pequeño que aún produzca una decisión confiable y trazable.

## 3. Dimensiones de decisión

### 3.1 Evidence clarity

- **Clear**: la evidencia cubre el objetivo con poco margen de ambigüedad
- **Partial**: la evidencia es útil pero deja huecos
- **Ambiguous**: hay contradicciones o falta de definición

### 3.2 Objective complexity

- **Simple**: extracción puntual o resumen corto
- **Moderate**: canonización y comparación ligera
- **High**: discovery, gaps, entrevista y spec

### 3.3 Risk level

- **Low**: error barato, bajo impacto
- **Medium**: requiere validación
- **High**: afecta arquitectura, producto o decisión de largo plazo

### 3.4 Token pressure

- **Low**: puede operar con más contexto
- **Medium**: debe priorizar resumen y top-k
- **High**: necesita fuerte compresión y gating

## 4. Matrix

| Evidence clarity | Objective complexity | Risk level | Recommended path |
| --- | --- | --- | --- |
| Clear | Simple | Low | Intake only |
| Clear | Moderate | Low/Medium | Intake + Canonization |
| Partial | Moderate | Medium | Full Evidence Loop |
| Partial | High | Medium/High | Full Evidence Loop + Readiness |
| Ambiguous | Any | Any | Full Evidence Loop + Clarification |
| Clear/Partial | High | High | AI-DLC or full pipeline with verification |

## 5. Decision rule

If multiple paths are possible, choose the smallest path that:

- closes critical gaps
- keeps traceability
- fits token budget
- contains risk

## 6. No-goals

- no elegir AI-DLC por inercia
- no usar intake only si faltan gaps críticos
- no sobrediseñar cuando una ruta corta basta
