# Design — token-cost-quality-telemetry

## Architecture / Boundaries

- Monorepo: Python/FastAPI project_state domain owns all token/cost/quality state.
- No direct database access from frontend or from execution models — everything goes
  through the `/api/projects/{id}/...` REST boundary.
- Quality signals are carried as structured keys within the existing `metadata_json`
  field on `ps_token_usage_events`. No schema migration required for the MVP scope.

## Technical Approach

### Schema extension (backward-compatible)

`RecordTokenUsageRequest` (in `schemas/overview.py`) gains four optional fields:

```python
agent_id: str | None = Field(None, description="Brain or agent identifier")
review_pass: bool | None = Field(None, description="Code-review passed flag")
verification_pass: bool | None = Field(None, description="Acceptance-criteria verified flag")
rework_count: int | None = Field(None, ge=0, description="Retry/rework iteration count")
```

The service layer merges these into `metadata_json` before persisting, so no DB
migration is needed. Existing events with `metadata_json={}` remain valid.

### New read endpoint

`GET /api/projects/{id}/costs/quality-summary`

Response shape:

```json
{
  "project_id": "...",
  "total_events": 42,
  "review_pass_count": 35,
  "review_fail_count": 7,
  "review_pass_rate": 0.833,
  "verification_pass_count": 38,
  "verification_fail_count": 4,
  "verification_pass_rate": 0.904,
  "avg_rework_count": 0.71,
  "total_estimated_cost": 12.50,
  "cost_per_reviewed_event": 0.298
}
```

The repository aggregation reads from `ps_token_usage_events.metadata_json` using
SQLite JSON extraction (`json_extract`) or equivalent. This is a read-path only —
no writes change.

### Layer responsibilities

| Layer | What changes |
|-------|-------------|
| `schemas/overview.py` | Add 4 optional fields to `RecordTokenUsageRequest`; add `ProjectQualitySummaryResponse` |
| `repositories/telemetry.py` | Add `get_project_quality_aggregate(project_id)` |
| `services/project_overview.py` | Wire `record_token_usage` to merge quality fields; add `get_project_quality_summary` |
| `routes/project_overview.py` | Add `GET /{project_id}/costs/quality-summary` |

## Dependencies

- Depends on `project-state-mvp` (already done — baseline in place)
- No new Python packages required

## Validation Strategy

- Run `pytest tests/api/test_project_token_usage.py tests/api/test_project_cost_summary.py` — must still pass
- Run new tests for quality-summary endpoint
- Run full suite: `cd apps/api && uv run pytest` — 0 new failures

## Important Tradeoffs

- `metadata_json` for quality signals avoids a DB migration at the cost of losing
  indexed queries on quality fields. Acceptable for MVP — if query performance
  becomes an issue, a dedicated column migration is the path forward.
- Quality signals are optional — callers that don't provide them get no quality
  aggregation (fields show `null` in quality-summary).

## Context Notes

- Canonical spec: `docs/canonical/25-TOKEN-COST-AND-QUALITY-TELEMETRY.md`
- Baseline code: `apps/api/mastermind_cli/project_state/`
- Existing tests: `tests/api/test_project_token_usage.py`, `test_project_cost_summary.py`,
  `test_project_write_side.py` (lines 459+)
