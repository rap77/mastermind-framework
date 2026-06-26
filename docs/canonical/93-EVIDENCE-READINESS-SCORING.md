# Evidence Readiness Scoring

## 1. Propósito

Combinar confianza, cobertura, trazabilidad y completitud para decidir si una evidencia está lista para especificación.

## 2. Tesis central

Readiness es una decisión compuesta, no un solo número aislado.

## 3. Inputs

- confidence score
- coverage level
- traceability completeness
- user clarification state
- critical gap count
- important gap count
- optional gap count
- contradiction count

## 4. Scoring model

### 4.1 Weights

- confidence: 40
- coverage: 35
- traceability: 15
- completeness: 10

### 4.2 Penalties

- critical gaps: up to 30 points
- important gaps: up to 20 points
- optional gaps: up to 10 points
- contradictions: up to 40 points
- missing user answers with low coverage: 5 points

### 4.3 Gating rule

- `score >= 80` and no contradictions or critical gaps → `ready`
- `score >= 65` and no contradictions or critical gaps → `conditionally_ready`
- critical gaps present with no contradictions → `not_ready`
- contradictions present → `blocked`

## 5. Scoring bands

### 5.1 Ready

- confidence alta
- gaps críticos = 0
- coverage full o near-full
- contradicciones resueltas
- score alto y estable

### 5.2 Conditionally ready

- confidence media-alta
- gaps críticos = 0
- puede haber gaps importantes no bloqueantes

### 5.3 Not ready

- confidence media o baja
- gaps críticos > 0
- coverage parcial o insuficiente

### 5.4 Blocked

- contradicciones persistentes
- falta información esencial
- el usuario no respondió lo necesario

## 6. Decision rule

La spec solo puede generarse si el gate final es `ready`.

## 7. No-goals

- no compensar gaps críticos con confianza alta
- no aprobar por cantidad de fuentes
- no confundir actividad con readiness
