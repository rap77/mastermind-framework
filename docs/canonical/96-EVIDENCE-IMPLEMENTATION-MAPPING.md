# Evidence Implementation Mapping

## 1. Propósito

Conectar el flujo de evidencia con la implementación real del sistema para que el canon no se quede solo en documentación.

## 2. Tesis central

Cada harness, loop y rubric debe poder aterrizar en servicios, storage, runtime y policy enforcement.

## 3. Implementation targets

### 3.1 Source registry service

Persistir fuentes, snapshots, d deltas y decisiones.

### 3.2 Evidence intake service

Ingerir fuentes, normalizarlas y extraer bloques canónicos.

### 3.3 Gap detection service

Calcular gaps, severidad y cobertura.

### 3.4 Clarification service

Generar preguntas y registrar respuestas.

### 3.5 Readiness service

Emitir verdicts `ready / conditionally_ready / not_ready / blocked` y un score `0..100`.

### 3.6 Spec generation service

Construir la spec final solo cuando haya readiness.

### 3.7 Archive service

Guardar lineage, decisiones y versiones.

## 4. Runtime enforcement

La implementación debe poder:

- bloquear spec si readiness gate no es `ready`
- registrar contradicciones
- persistir confidence / gap severity / coverage
- reusar snapshots previas

## 5. Storage mapping

Mínimo:

- Postgres para registro, snapshots, gaps, preguntas y decisiones
- vector search opcional para retrieval semántico
- relaciones explícitas para lineage y contradictions

## 6. Integration points

- MCP para acceso seguro a datos y tools
- selector de harness para routing
- memory layer para contexto durable
- AI-DLC para fases más formales

## 7. No-goals

- no dejar el canon sin backing de ejecución
- no duplicar lógica en múltiples servicios
- no permitir que la implementación ignore la política de readiness
