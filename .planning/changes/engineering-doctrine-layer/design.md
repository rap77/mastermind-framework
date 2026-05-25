# Design — engineering-doctrine-layer

## Architecture / Boundaries
- All changes are limited to the Python FastAPI backend (`apps/api/`).
- No frontend, Rust, or SQLite schema changes required.
- Doctrine stored as JSONB in `project.metadata_json["doctrine"]` — no new tables.

## Technical Approach

### New request schema (in `project_overview.py` or a schemas file)
```python
class DoctrineRuleRequest(BaseModel):
    rule_id: str
    summary: str
    severity: str = "mandatory"
    check: str | None = None

class DoctrineUpdateRequest(BaseModel):
    methodology: str | None = None
    methodology_reason: str | None = None
    required_phases: list[str] | None = None
    mandatory_rules: list[DoctrineRuleRequest] | None = None
    recommended_rules: list[DoctrineRuleRequest] | None = None
    architecture_constraints: list[str] | None = None
    quality_gates: list[str] | None = None
    exception_policy: dict[str, bool] | None = None
```

### New service method in `ProjectOverviewService`
```python
def update_project_doctrine(
    self, project_id: str, request: DoctrineUpdateRequest
) -> DoctrineProjectionResponse | None:
    # 1. Load project, return None if not found
    # 2. Get current metadata_json (or {})
    # 3. Merge request fields into metadata_json["doctrine"] (skip None fields)
    # 4. Persist, return updated doctrine projection
```

### New route
```
PATCH /{project_id}/doctrine
→ auth: get_current_user_any
→ body: DoctrineUpdateRequest
→ returns: DoctrineProjectionResponse
→ 404 if project not found
```

### Test pattern (write → read cycle)
```python
# PATCH to set doctrine
await client.patch(f"/api/projects/{project_id}/doctrine", json={...}, headers=auth)
# GET to verify projection reflects the write
await client.get(f"/api/projects/{project_id}/tasks/{task_id}/doctrine-projection", headers=auth)
```

## Dependencies
- Depends on `project-state-mvp` (done — Project model + ProjectOverviewService exist)

## Files / Areas Touched
- `apps/api/mastermind_cli/api/routes/project_overview.py` — new PATCH route
- `apps/api/mastermind_cli/project_state/services/project_overview.py` — new service method
- `apps/api/mastermind_cli/project_state/schemas/` or inline — new request schemas
- `apps/api/tests/api/test_project_doctrine_projection.py` — new write → read test

## Validation Strategy
- `cd apps/api && uv run pytest tests/api/test_project_doctrine_projection.py -v`
- All tests must pass (currently 1 passing test + 1 new test after T2)

## Important Tradeoffs
- Doctrine is merged (not replaced) on PATCH — allows incremental updates without full rewrites.
- `None` fields in the request are ignored (partial update semantics).
- No validation of rule_id uniqueness in this slice — deferred to enforcement objective.

## Context Notes
- Existing GET endpoint: `routes/project_overview.py:399-417`
- Existing service method: `services/project_overview.py:603`
- Existing test: `tests/api/test_project_doctrine_projection.py`
