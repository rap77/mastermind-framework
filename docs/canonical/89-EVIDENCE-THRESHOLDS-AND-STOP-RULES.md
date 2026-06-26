# Evidence Thresholds and Stop Rules

## 1. Propósito

Definir umbrales prácticos para saber cuándo seguir, cuándo detenerse y cuándo pedir más información.

## 2. Tesis central

La calidad no mejora indefinidamente al seguir iterando; mejora hasta que los gaps críticos desaparecen.

## 3. Stop rules

Detener el loop cuando:

- no aparecen nuevos gaps críticos
- las respuestas del usuario cierran los huecos abiertos
- la confianza supera el umbral
- la evidencia ya cubre el alcance
- el costo marginal supera el beneficio

## 4. Continue rules

Seguir iterando cuando:

- persisten gaps críticos
- hay contradicciones entre fuentes
- el objetivo sigue ambiguo
- la confianza es baja
- la spec sería especulativa

## 5. Threshold bands

### 5.1 Confidence

- **High**: suficiente para pasar a spec
- **Medium**: suficiente para canonizar, no siempre para spec
- **Low**: requiere más evidencia o entrevista

### 5.2 Gap severity

- **Critical**: bloquea spec
- **Important**: debe cerrarse antes de implementación
- **Optional**: puede quedar para iteración posterior

### 5.3 Coverage

- **Full**: cubre scope y decisiones principales
- **Partial**: cubre parte importante, pero falta cierre
- **Insufficient**: no permite avanzar

## 6. Exit condition

El loop sale solo si:

- coverage suficiente
- gaps críticos resueltos
- confidence acceptable
- traceability intacta

## 7. No-goals

- no seguir por perfeccionismo
- no parar con gaps críticos abiertos
- no usar umbrales invisibles o subjetivos sin registro
