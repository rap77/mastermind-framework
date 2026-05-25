# Design — backend-service-boundary-for-agents

## Architecture / Boundaries

El boundary ya está estructuralmente aplicado: la ruta HTTP llama al service, el service llama
al repositorio. Los agentes no tienen acceso directo a la DB.

El gap concreto es un endpoint de escritura faltante: token-usage recording via agente.

## Technical Approach for T2

### Endpoint a implementar

```
POST /api/projects/{project_id}/tasks/{task_id}/token-usage
```

**Request body:**
```json
{
  "model": "claude-sonnet-4-6",
  "input_tokens": 1234,
  "output_tokens": 567,
  "cache_read_tokens": 0,
  "cache_write_tokens": 0,
  "cost_usd": 0.0042,
  "phase": "implementation",
  "metadata": {}
}
```

**Response:** `201 Created` con el evento registrado.

### Files to touch

- `apps/api/mastermind_cli/project_state/schemas/overview.py` — `RecordTokenUsageRequest` schema
- `apps/api/mastermind_cli/project_state/services/project_overview.py` — `record_token_usage(task_id, project_id, ...)` method
- `apps/api/mastermind_cli/project_state/repositories/` — via `TelemetryRepository` existente
- `apps/api/mastermind_cli/api/routes/project_overview.py` — agregar el POST endpoint
- `apps/api/tests/api/test_project_write_side.py` — tests TDD

### Pattern to follow

Mismo patrón que `create_project_decision` (líneas 340-370 en project_overview.py):
1. Route recibe request body
2. Route llama `service.record_token_usage(...)`
3. Service valida y llama `self.telemetry.create_event(...)`
4. Route retorna 201

### Existing infrastructure

`TelemetryRepository` ya existe. `TokenUsageEvent` model ya existe.
Solo falta el método de servicio y el endpoint de escritura.

## Dependencies

- Depends on `project-state-mvp` (done)
- Depends on `artifact-versioning-and-lineage` (done)

## Validation Strategy

- `cd apps/api && uv run pytest tests/api/test_project_write_side.py -q`
- `cd apps/api && uv run pytest tests/api/test_project_activity_feed.py tests/api/test_project_runs.py -q` (regression)

## Important Tradeoffs

- `cost_usd` puede ser 0.0 si el agente no tiene acceso al precio — el campo debe ser nullable.
- No emitir evento realtime por ahora (el endpoint de GET ya lo expone vía activity feed).
