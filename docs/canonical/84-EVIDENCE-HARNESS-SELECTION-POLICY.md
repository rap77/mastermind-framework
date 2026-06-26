# Evidence Harness Selection Policy

## 1. Propósito

Definir cuándo MasterMind debe usar el pipeline de evidencia, cuándo basta un harness simple y cuándo debe escalar a AI-DLC u otro workflow.

## 2. Tesis central

No toda tarea necesita el mismo nivel de ceremonia. El selector debe escoger el camino mínimo suficiente.

## 3. Inputs de decisión

El selector evalúa:

- tipo de fuente
- complejidad de la evidencia
- nivel de incertidumbre
- cantidad de gaps
- necesidad de entrevista
- riesgo de la decisión
- costo de tokens
- necesidad de trazabilidad

## 4. Rutas posibles

### 4.1 Evidence Intake Only

Usar solo intake cuando la fuente es clara y la extracción es directa.

### 4.2 Evidence Intake + Canonization

Usar cuando la fuente tiene valor, pero no requiere entrevista ni gaps complejos.

### 4.3 Full Evidence Loop

Usar cuando hay evidencia incompleta, contradicciones o necesidad de clarificación.

### 4.4 AI-DLC Harness

Usar cuando además del intake hay que hacer discovery, requirements, design, construction y archive formal.

## 5. Regla de selección

Elegir la ruta más pequeña que cumpla con:

- cobertura suficiente
- trazabilidad mínima
- costo aceptable
- riesgo controlado

## 6. Cuándo escalar

Escalar al full evidence loop si:

- la fuente no cubre todo
- hay contradicciones entre fuentes
- faltan decisiones clave
- el usuario debe aclarar intención
- la confianza de extracción es baja

Escalar a AI-DLC si:

- el trabajo ya pasó de análisis a ejecución
- hay que diseñar e implementar algo
- se necesita trazabilidad de fases
- la complejidad justifica el overhead

## 7. Cuándo no escalar

No escalar si:

- basta un resumen corto
- el cambio es trivial
- el riesgo es bajo
- la evidencia ya es suficiente

## 8. Output

El selector debe devolver:

- ruta elegida
- ruta descartada
- razón
- riesgos
- siguiente paso

## 9. No-goals

- no usar AI-DLC por costumbre
- no entrevistar si no hay gaps reales
- no reanalizar la misma fuente sin motivo
