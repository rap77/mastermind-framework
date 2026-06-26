# Gap to Question Mapping

## 1. Propósito

Traducir gaps detectados en preguntas concretas para entrevistas con el usuario.

## 2. Tesis central

Cada gap crítico debe producir una pregunta corta que cierre exactamente ese hueco.

## 3. Mapping rules

### 3.1 Functional gap

Preguntar por comportamiento, condiciones o flujo.

### 3.2 Structural gap

Preguntar por boundaries, componentes o dependencias.

### 3.3 Data gap

Preguntar por entidades, campos, estados o relaciones.

### 3.4 NFR gap

Preguntar por performance, seguridad, escalabilidad u observabilidad.

### 3.5 Decision gap

Preguntar por preferencia, tradeoff o criterio de elección.

## 4. Question format

Cada pregunta debe incluir:

- `question`
- `gap_id`
- `severity`
- `why_it_matters`
- `blocking_status`

## 5. Prioritization

Preguntar primero por:

1. gaps críticos
2. gaps importantes
3. gaps opcionales solo si ayudan a acelerar otras decisiones

## 6. No-goals

- no convertir un gap en varias preguntas si una basta
- no preguntar sobre gaps opcionales antes de cerrar críticos
- no preguntar por lo ya resuelto por evidencia
