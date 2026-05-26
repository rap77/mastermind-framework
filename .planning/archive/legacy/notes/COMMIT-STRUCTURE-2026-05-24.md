# Commit Structure — 2026-05-24

## Goal

Split the current accumulated working tree into coherent commits instead of one giant mixed commit.

---

## First: exclude local/runtime noise

These files should **not** be part of product/history commits:

- `.planning/.mm-flow/runtime-state.json`
- `.planning/task-progress.json`
- `.planning/BACKEND-USAGE.json`
- `mastermind.db`
- `apps/api/.mastermind/`
- `apps/api/.mastermind-active`
- `tasks/todo.md.backup_*`

`/.gitignore` was updated to cover these paths.

---

## Commit A — Rust control-plane consolidation

### Intent
Remove the duplicate old Rust control-plane and keep `rust_control_plane` as the canonical implementation.

### Include
- `apps/control-plane/**` deletions
- `docker-compose.yml`
- `docker/control-plane/Dockerfile`
- `proto/buf.gen.yaml`

### Suggested commit
```bash
refactor(control-plane): consolidate rust control plane into rust_control_plane
```

---

## Commit B — MasterMind flow cutover

### Intent
Introduce the objective-based MM workflow and remove active reliance on the old legacy planning flow.

### Include
- `.claude/commands/mm/discover-handler.py`
- `.claude/commands/mm/discover-contract-check.py`
- `.claude/commands/mm/discover-contract-check.md`
- `.claude/commands/mm/complete-task-handler.py`
- `.claude/commands/mm/continue-task.md`
- `.claude/commands/mm/update-todo-times.py`
- `.claude/commands/mm/notify-complete.py`
- `.claude/commands/mm/discover.md`
- `.claude/commands/mm/complete-task.md`
- `.claude/commands/mm/init-handler.py`
- `.claude/commands/mm/project-health-check.md`
- `.claude/agents/mm/discover-planner/discover-planner.md`
- `.claude/agents/mm/rediscovery-auditor/rediscovery-auditor.md`
- `.claude/agents/mm/task-executor/task-executor.md`
- `tests/unit/test_mm_discover_workflow.py`

### Suggested commit
```bash
feat(mm-flow): add objective-based discover and execution workflow
```

---

## Commit C — Project State MVP

### Intent
Commit the new backend/frontend thin slice for project state, including realtime and write-side status updates.

### Include
- `apps/api/mastermind_cli/api/app.py`
- `apps/api/mastermind_cli/api/dependencies.py`
- `apps/api/mastermind_cli/api/routes/project_overview.py`
- `apps/api/mastermind_cli/project_state/**`
- `apps/api/tests/api/test_project_overview.py`
- `apps/api/tests/api/test_project_state_detail.py`
- `apps/api/tests/api/test_project_cost_summary.py`
- `apps/api/tests/api/test_project_activity_feed.py`
- `apps/api/tests/api/test_project_decisions.py`
- `apps/api/tests/api/test_project_context_projection.py`
- `apps/api/tests/api/test_project_doctrine_projection.py`
- `apps/api/tests/api/test_projects_list_detail.py`
- `apps/api/tests/api/test_project_runs.py`
- `apps/api/tests/api/test_project_tasks_graph.py`
- `apps/api/tests/api/test_project_token_usage.py`
- `apps/api/tests/api/test_project_time_summary.py`
- `apps/api/tests/api/test_project_write_side.py`
- `apps/api/tests/unit/test_project_overview_service.py`
- `apps/web/src/app/(protected)/project-state/**`
- `apps/web/src/app/actions/project-state.ts`
- `apps/web/src/components/project-state/**`
- `apps/web/src/lib/project-state-api.ts`
- `apps/web/src/components/layout/AppSidebar.tsx`

### Suggested commit
```bash
feat(project-state): add project state dashboard, realtime, and write-side MVP
```

---

## Commit D — Planning and canonical docs

### Intent
Commit the new planning artifacts, roadmap, objective package, and canonical docs that teach the new workflow.

### Include
- `docs/canonical/**`
- `.planning/roadmap/**`
- `.planning/changes/project-state-mvp/**`
- `.planning/HANDOFF-CURRENT.md`
- `.planning/HANDOFF-PROJECT-STATE-2026-05-24.md`
- `.planning/SOURCE-OF-TRUTH.md`
- `.planning/BRAIN-FEED-01-product.md`
- `.planning/BRAIN-FEED-05-backend.md`
- `.planning/BRAIN-FEED-06-qa.md`
- `.planning/BRAIN-FEED-07-growth.md`
- `README.md`
- `AGENTS.md`
- `CLAUDE.md`

### Suggested commit
```bash
docs(planning): add hybrid spec flow, roadmap, and objective packages
```

---

## Commit E — Misc repo changes (review carefully)

These files are outside the core changes above and should be reviewed before staging:

- `apps/api/tests/api/conftest.py`
- `apps/api/tests/e2e/test_multi_user.py`
- `apps/api/tests/kd/test_analytics.py`
- `benches/**`
- `BACKEND-DEPLETION.md`
- `rust_control_plane/src/handlers/brain_event.rs`
- `rust_control_plane/src/websocket/events_handler.rs`

Possible outcomes:
- split into a dedicated commit
- postpone
- or discard if unrelated

---

## Recommended order

1. Commit A — Rust consolidation
2. Commit B — MM flow cutover
3. Commit C — Project State MVP
4. Commit D — Docs / planning
5. Commit E — only after review

---

## Important rule

Do **not** commit the whole working tree with a single `git add .`.
This branch contains architecture work, product work, planning artifacts, and cleanup all mixed together.
