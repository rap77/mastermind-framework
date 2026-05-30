# Requirements — token-cost-quality-telemetry

## Problem / Purpose

Deliver the smallest coherent telemetry slice that captures token usage, cost, and
quality signals per project/task/run so operators and models can compare providers,
strategies, and trade cost against quality over time.

Canonical reference: `docs/canonical/25-TOKEN-COST-AND-QUALITY-TELEMETRY.md`

## Stakeholders / Users

- Primary: execution models (task-executor, brain agents) recording usage events
- Secondary: human operators reading cost/quality via `/api/projects/{id}/costs/summary`
  and `/api/projects/{id}/token-usage`

## Baseline (already shipped by project-state-mvp)

The following is already implemented and tested — do NOT re-implement:

- `ps_token_usage_events` table (SQLAlchemy model: `token_usage.py`)
- `TelemetryRepository`: `create_event`, `list_recent_by_project`, `get_project_cost_aggregate`
- `GET /api/projects/{id}/costs/summary` — aggregated token + cost totals per provider
- `GET /api/projects/{id}/token-usage` — recent events list (tested)
- `POST /api/projects/{id}/tasks/{task_id}/token-usage` — write side (tested)

## Scope for this objective

Extend the existing telemetry slice with quality signal support:

1. **Quality signals in token-usage metadata**: The `metadata_json` field on
   `TokenUsageEvent` already accepts arbitrary JSON. The `RecordTokenUsageRequest`
   schema must document and validate the quality signal keys:
   - `review_pass` (bool): whether the code-reviewer passed this run
   - `verification_pass` (bool): whether acceptance criteria were verified
   - `rework_count` (int): number of retry/rework iterations before completion

2. **Agent/brain linkage**: Add optional `agent_id` field to `RecordTokenUsageRequest`
   so events can be attributed to a specific brain or sub-agent, enabling per-brain
   cost and quality analysis.

3. **Cost-quality read endpoint**: Add `GET /api/projects/{id}/costs/quality-summary`
   that returns aggregated quality signals alongside cost totals — enabling the
   "cost vs quality" view described in the canonical spec.

## Out of Scope

- No unrelated rewrites to existing token usage model or repository.
- No new database tables (extend via metadata_json and a new schema field).
- Do not bypass backend services with direct database access from frontend.
- Dashboard/frontend UI for quality signals — deferred to a separate objective.
- Machine learning on quality signals — deferred.

## Non-negotiables

- Preserve the backend-authority boundary for all writes.
- All new fields must be optional and backward-compatible.
- Existing tests must continue to pass after changes.

## Objective-level Acceptance Criteria

- [x] `GET /api/projects/{id}/costs/summary` returns aggregated cost (already shipped)
- [x] `GET /api/projects/{id}/token-usage` returns events list (already shipped)
- [x] `POST /api/projects/{id}/tasks/{task_id}/token-usage` records events (already shipped)
- [x] `RecordTokenUsageRequest` accepts and validates `agent_id`, `review_pass`,
      `verification_pass`, `rework_count` as optional fields
- [x] `POST /token-usage` persists quality fields into `metadata_json` (backward-compatible)
- [x] `GET /api/projects/{id}/costs/quality-summary` returns cost + quality aggregates
- [x] All new endpoints and schema changes have test coverage
- [x] Validation commands pass after implementation
