# Source Registry Schema

## 1. Propósito

Bajar el Source Registry a un esquema persistible para versionar fuentes externas, sus snapshots y los deltas de adopción.

## 2. Tesis central

Las fuentes externas deben vivir como entidades rastreables, no como notas sueltas en documentos.

## 3. Entidades principales

### 3.1 source_registry

Registro maestro de fuentes.

Campos sugeridos:

- `source_id`
- `name`
- `source_type`
- `url`
- `local_path`
- `snapshot_ref`
- `snapshot_hash`
- `captured_at`
- `purpose`
- `owner`
- `confidence`
- `adoption_state`
- `risk_level`
- `change_expectation`
- `tags`
- `notes`
- `created_at`
- `updated_at`

### 3.2 source_snapshots

Versiones específicas de una fuente.

Campos sugeridos:

- `snapshot_id`
- `source_id`
- `snapshot_ref`
- `snapshot_hash`
- `captured_at`
- `captured_by`
- `summary`
- `created_at`

### 3.3 source_capabilities

Capacidades detectadas en una fuente.

Campos sugeridos:

- `id`
- `snapshot_id`
- `capability_name`
- `capability_kind`
- `description`
- `confidence`
- `relevance`
- `notes`
- `created_at`

### 3.4 source_anti_patterns

Patrones no recomendados.

Campos sugeridos:

- `id`
- `snapshot_id`
- `anti_pattern`
- `reason`
- `severity`
- `notes`
- `created_at`

### 3.5 source_deltas

Cambios entre snapshots.

Campos sugeridos:

- `delta_id`
- `source_id`
- `from_snapshot_id`
- `to_snapshot_id`
- `delta_summary`
- `adoption_impact`
- `risk_change`
- `created_at`

### 3.6 source_adoption_decisions

Decisiones de adopción o rechazo.

Campos sugeridos:

- `decision_id`
- `source_id`
- `snapshot_id`
- `decision_state`
- `decision_reason`
- `adopted_as`
- `replaces`
- `created_at`

Decision states:

- `candidate`
- `adopted`
- `adapted`
- `rejected`
- `deprecated`

### 3.7 source_links

Relaciones entre fuentes.

Campos sugeridos:

- `link_id`
- `from_source_id`
- `to_source_id`
- `relation_type`
- `reason`
- `created_at`

Relation types:

- `inspired_by`
- `compares_with`
- `supersedes`
- `conflicts_with`
- `complements`

## 4. Índices recomendados

- `name`
- `source_type`
- `adoption_state`
- `snapshot_hash`
- `captured_at`
- `source_links(from_source_id, relation_type)`
- `source_links(to_source_id, relation_type)`

## 5. Operaciones mínimas

### 5.1 Register source

Crear un registro de fuente.

### 5.2 Capture snapshot

Persistir una snapshot nueva.

### 5.3 Extract capabilities

Registrar capabilities detectadas.

### 5.4 Record anti-patterns

Guardar lo que no conviene adoptar.

### 5.5 Record delta

Comparar snapshots y guardar el cambio.

### 5.6 Record adoption decision

Guardar la decisión de adoptar, adaptar o rechazar.

### 5.7 Link sources

Relacionar fuentes entre sí.

## 6. Query patterns

El sistema debe poder preguntar:

- “qué cambió en Hermes desde la última snapshot”
- “qué capability nueva merece adopción”
- “qué anti-pattern debe evitarse”
- “qué decisión se tomó y por qué”
- “qué fuente inspira este harness”

## 7. Delta rules

- Nunca sobrescribir una snapshot previa.
- Siempre dejar una decisión si cambia el estado.
- Toda capability nueva debe apuntar a una snapshot.
- Todo rechazo debe justificar riesgo, costo o desalineación.

## 8. Integration rules

El source registry alimenta:

- Research Harness
- Discovery Harness
- Source-aware architecture docs
- Capability Registry
- Memory Layer

## 9. No-goals

- no mezclar snapshots con memoria durable
- no perder la versión anterior al capturar una nueva
- no tratar la fuente como texto plano sin estructura
- no guardar análisis sin source_ref
