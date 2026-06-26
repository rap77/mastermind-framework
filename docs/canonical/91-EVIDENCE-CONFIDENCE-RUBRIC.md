# Evidence Confidence Rubric

## 1. Propósito

Definir una escala fina para medir cuánta confianza tiene MasterMind en una extracción, canonización o decisión.

## 2. Tesis central

La confianza no es binaria. Debe poder graduarse para decidir si avanzar, pedir más evidencia o entrevistar al usuario.

## 3. Escala

### 3.1 0.90-1.00 High confidence

- la evidencia es directa
- la interpretación es estable
- no hay contradicciones relevantes
- la salida puede ir a spec o archive

### 3.2 0.70-0.89 Medium-high confidence

- la evidencia es buena
- hay pocos supuestos
- puede canonizarse con riesgo bajo
- puede requerir validación ligera

### 3.3 0.50-0.69 Medium confidence

- la evidencia es útil pero parcial
- hay gaps relevantes
- se necesita full evidence loop o entrevista

### 3.4 0.30-0.49 Low confidence

- la extracción es frágil
- hay ambigüedad o contexto insuficiente
- no debe pasar a spec

### 3.5 0.00-0.29 Very low confidence

- la evidencia no soporta una decisión fiable
- solo sirve como pista exploratoria

## 4. Uso

La confianza debe acompañar:

- source summary
- capability block
- pattern block
- anti-pattern block
- decision block
- gap block

## 5. Rule of thumb

- `>= 0.80`: eligible for downstream use
- `0.60-0.79`: usable with caution
- `< 0.60`: needs more evidence or interview

## 6. No-goals

- no inflar confianza por volumen de texto
- no usar un único score para todo sin contexto
- no ocultar incertidumbre tras lenguaje vago
