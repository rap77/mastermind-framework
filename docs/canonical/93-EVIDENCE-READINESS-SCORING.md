# Evidence Readiness Scoring

## 1. Propósito

Combinar confianza, severidad de gaps y cobertura para decidir si una evidencia está lista para especificación.

## 2. Tesis central

Readiness es una decisión compuesta, no un solo número aislado.

## 3. Inputs

- confidence score
- gap severity distribution
- coverage level
- contradiction count
- user clarification state

## 4. Scoring bands

### 4.1 Ready

- confidence alta
- gaps críticos = 0
- coverage full o near-full
- contradicciones resueltas

### 4.2 Conditionally ready

- confidence media-alta
- gaps críticos = 0
- puede haber gaps importantes no bloqueantes

### 4.3 Not ready

- confidence media o baja
- gaps críticos > 0
- coverage parcial o insuficiente

### 4.4 Blocked

- contradicciones persistentes
- falta información esencial
- el usuario no respondió lo necesario

## 5. Decision rule

La spec solo puede generarse si el estado final es `ready`.

## 6. No-goals

- no compensar gaps críticos con confianza alta
- no aprobar por cantidad de fuentes
- no confundir actividad con readiness
