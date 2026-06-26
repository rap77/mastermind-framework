# Gap Detection and Clarification Loop

## 1. Propósito

Detectar qué falta en la evidencia antes de escribir la especificación y cerrar esos huecos con preguntas al usuario.

## 2. Tesis central

Si la evidencia no cubre el 100% del objetivo, MasterMind debe parar, identificar el gap y preguntar antes de inventar.

## 3. Cuándo se activa

Este loop se activa cuando:

- falta contexto crítico
- hay ambigüedad funcional
- la fuente no cubre casos importantes
- hay contradicciones entre fuentes
- la confianza de extracción es baja
- la spec se volvería especulación

## 4. Tipos de gaps

### 4.1 Functional gaps

Falta comportamiento, flujo o regla de negocio.

### 4.2 Structural gaps

Falta arquitectura, dependencia o boundary.

### 4.3 Data gaps

Faltan entidades, campos, relaciones o estados.

### 4.4 NFR gaps

Falta performance, seguridad, escalabilidad u observabilidad.

### 4.5 Decision gaps

Falta criterio para elegir entre alternativas.

## 5. Flujo

### 5.1 Detect

Comparar la evidencia contra la base canónica esperada.

### 5.2 Classify

Etiquetar cada hueco por tipo y severidad.

### 5.3 Prioritize

Ordenar gaps por impacto sobre la especificación.

### 5.4 Ask

Generar preguntas concretas al usuario solo para los huecos relevantes.

### 5.5 Resolve

Incorporar las respuestas y volver a evaluar.

## 6. Reglas de preguntas

- preguntas cortas
- una idea por pregunta
- sin doble sentido
- enfocadas en decisión, no en teoría
- solo preguntar lo necesario para cerrar el gap

## 7. Salida

El loop debe devolver:

- gap list
- unresolved gaps
- preguntas emitidas
- respuestas recibidas
- gaps cerrados
- readiness status

## 8. Relación con otros harnesses

Este loop alimenta:

- Evidence Intake Harness
- Verification Harness
- Spec Generation Harness
- AI-DLC Discovery / Requirements

## 9. No-goals

- no preguntar por curiosidad
- no convertir cada duda en entrevista larga
- no avanzar a spec con gaps críticos abiertos
