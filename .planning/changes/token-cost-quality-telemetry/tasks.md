# Tasks — token-cost-quality-telemetry

## Execution Rules

- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Each task must declare purpose, dependencies, likely file touchpoints, validation commands, and acceptance criteria.

## T1: Define and stabilize the slice

### Purpose

Tighten the planning package to reflect the real boundary: what the project-state-mvp
already shipped (baseline) vs what this objective must deliver (quality signal extension).

### Depends On

None

### Parallelizable

no

### Files / Areas Likely Touched

- `.planning/changes/token-cost-quality-telemetry/requirements.md`
- `.planning/changes/token-cost-quality-telemetry/design.md`
- `.planning/changes/token-cost-quality-telemetry/tasks.md`

### Validation Commands

- `python3 .claude/commands/mm/discover-contract-check.py --objective token-cost-quality-telemetry`
- Review that requirements distinguish baseline (done) from new scope (pending)

### Acceptance Criteria

- [x] Baseline (project-state-mvp deliverables) is explicitly documented and marked done
- [x] New scope (quality signals + quality-summary endpoint) is specified with enough
      detail for a model to implement without re-reading the full codebase
- [x] Architecture constraints (no DB migration, metadata_json approach) are documented
- [x] Validation commands are documented in design.md

## T2: Implement the smallest coherent deliverable

### Purpose

Extend `RecordTokenUsageRequest` with optional quality signal fields, wire them
through the service layer into `metadata_json`, and add the
`GET /api/projects/{id}/costs/quality-summary` read endpoint.

### Depends On

T1

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/project_state/schemas/overview.py`
  - Add `agent_id`, `review_pass`, `verification_pass`, `rework_count` to `RecordTokenUsageRequest`
  - Add `ProjectQualitySummaryResponse` schema
- `apps/api/mastermind_cli/project_state/repositories/telemetry.py`
  - Add `get_project_quality_aggregate(project_id)` — reads `metadata_json` quality fields
- `apps/api/mastermind_cli/project_state/services/project_overview.py`
  - Update `record_token_usage` to merge quality fields into `metadata_json`
  - Add `get_project_quality_summary(project_id)` method
- `apps/api/mastermind_cli/api/routes/project_overview.py`
  - Add `GET /{project_id}/costs/quality-summary` endpoint
- `apps/api/tests/api/test_project_quality_summary.py` (new test file)
  - Test quality-summary endpoint: events with review_pass/fail, empty project

### Validation Commands

- `cd apps/api && uv run pytest tests/api/test_project_token_usage.py tests/api/test_project_cost_summary.py -v`
  - All existing tests still pass
- `cd apps/api && uv run pytest tests/api/test_project_quality_summary.py -v`
  - New tests pass
- `cd apps/api && uv run pytest --tb=short -q`
  - Full suite passes with 0 new failures

### Acceptance Criteria

- [ ] `RecordTokenUsageRequest` accepts `agent_id`, `review_pass`, `verification_pass`, `rework_count` as optional fields
- [ ] `POST /token-usage` persists quality fields into `metadata_json` (backward-compatible with existing callers)
- [ ] `GET /api/projects/{id}/costs/quality-summary` returns aggregated quality signals + cost totals
- [ ] Existing `test_project_token_usage.py` and `test_project_cost_summary.py` still pass
- [ ] New test file `test_project_quality_summary.py` has at least 3 test cases

## T3: Close the continuity loop

### Purpose

Refresh handoff notes, confirm validation commands pass, and archive the objective
package in a state that lets the next model understand what was delivered.

### Depends On

T2

### Parallelizable

no

### Files / Areas Likely Touched

- `.planning/changes/token-cost-quality-telemetry/HANDOFF-CURRENT.md`
- `.planning/changes/token-cost-quality-telemetry/tasks.md` (acceptance criteria marked)
- `.planning/changes/token-cost-quality-telemetry/todo.md` (via handler)

### Validation Commands

- `python3 .claude/commands/mm/discover-contract-check.py --objective token-cost-quality-telemetry`
- `cd apps/api && uv run pytest tests/api/test_project_quality_summary.py tests/api/test_project_cost_summary.py tests/api/test_project_token_usage.py -v`

### Acceptance Criteria

- [ ] Handoff notes are refreshed with next recommended work
- [ ] Acceptance criteria in tasks.md are checked for T2
- [ ] Validation commands are documented and pass
- [ ] Objective is ready for archiving or handoff to next model/session
