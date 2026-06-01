# Todo — project-state-mvp

## Execution Checklist

- [ ] PS1: Realtime events for project_state
  - [ ] PS1.1: Review requirements and design context for PS1
  - [ ] PS1.2: Implement PS1 end-to-end
  - [ ] PS1.3: Run validation for PS1
  - depends_on: none
  - validation: cd apps/api && . .venv/bin/activate && pytest -q tests/api/test_project_activity_feed.py tests/api/test_project_runs.py | cd apps/web && pnpm exec tsc --noEmit

- [ ] PS2: Richer write-side operations
  - [ ] PS2.1: Review requirements and design context for PS2
  - [ ] PS2.2: Implement PS2 end-to-end
  - [ ] PS2.3: Run validation for PS2
  - depends_on: PS1
  - validation: cd apps/api && . .venv/bin/activate && pytest -q tests/api/test_project_write_side.py | cd apps/web && pnpm exec eslint src/app/actions/project-state.ts src/components/project-state/ProjectStateWritePanel.tsx

- [ ] PS3: Replace transitional audit gap
  - [ ] PS3.1: Review requirements and design context for PS3
  - [ ] PS3.2: Implement PS3 end-to-end
  - [ ] PS3.3: Run validation for PS3
  - depends_on: PS1, PS2
  - validation: cd apps/api && . .venv/bin/activate && pytest -q tests/api/test_project_write_side.py tests/api/test_project_activity_feed.py
