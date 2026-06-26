# Evidence Lineage Schema

## 1. Propósito

Bajar el lineage de evidencia a un esquema persistible para conservar versiones, deltas, decisiones y trazabilidad.

## 2. Entidades

### 2.1 evidence_sources

Registro maestro de la fuente.

Campos sugeridos:

- `evidence_source_id`
- `source_type`
- `name`
- `uri`
- `owner`
- `purpose`
- `created_at`
- `updated_at`

### 2.2 evidence_versions

Versiones concretas de la fuente o del extracto.

Campos sugeridos:

- `evidence_version_id`
- `evidence_source_id`
- `version_ref`
- `version_hash`
- `captured_at`
- `captured_by`
- `summary`
- `state`

### 2.3 evidence_blocks

Bloques canónicos extraídos.

Campos sugeridos:

- `evidence_block_id`
- `evidence_version_id`
- `block_type`
- `title`
- `summary`
- `confidence`
- `impact`
- `source_ref`

### 2.4 evidence_deltas

Deltas entre versiones.

Campos sugeridos:

- `evidence_delta_id`
- `from_version_id`
- `to_version_id`
- `delta_type`
- `summary`
- `risk`
- `decision`

### 2.5 evidence_gaps

Huecos detectados.

Campos sugeridos:

- `gap_id`
- `evidence_version_id`
- `gap_type`
- `severity`
- `summary`
- `status`

### 2.6 evidence_questions

Preguntas emitidas para cerrar gaps.

Campos sugeridos:

- `question_id`
- `gap_id`
- `question`
- `why_it_matters`
- `answer`
- `blocking_status`

### 2.7 evidence_readiness

Veredictos de readiness.

Campos sugeridos:

- `readiness_id`
- `evidence_version_id`
- `confidence_score`
- `coverage_score`
- `gap_count`
- `verdict`
- `created_at`

## 3. Indices recomendados

- `evidence_versions(evidence_source_id, captured_at)`
- `evidence_blocks(evidence_version_id, block_type)`
- `evidence_deltas(from_version_id, to_version_id)`
- `evidence_gaps(evidence_version_id, severity)`
- `evidence_questions(gap_id)`

## 4. No-goals

- no mezclar lineage con memoria general
- no perder la relación bloque-version-fuente
- no almacenar decisiones sin origen
