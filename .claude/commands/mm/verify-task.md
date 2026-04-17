---
name: mm:verify-task
description: Verify MasterMind tasks are complete and mark acceptance criteria in plan.md
argument-hint: "<task-id> [--dry-run] [--criterion <name>]"
---

# /mm:verify-task

Verify that a MasterMind task is complete and mark its acceptance criteria in `tasks/plan.md`.

## Usage

```bash
/mm:verify-task D1              # Verify D1 and mark complete criteria
/mm:verify-task D1 --dry-run    # Verify only, don't mark
/mm:verify-task D1 --criterion "hardcoded colors"  # Verify specific criterion
```

## What It Does

1. **Reads** task definition from `tasks/plan.md`
2. **Reads** completion checklist from `tasks/todo.md`
3. **Verifies** each acceptance criterion:
   - Code inspection (grep, find, Read)
   - Test execution (if applicable)
   - Visual verification (if applicable)
4. **Marks** verified criteria as `[x]` in plan.md
5. **Reports** verification results

## Verification Process

The skill runs these checks:

| Criterion Type | Verification Method |
|----------------|---------------------|
| Code exists | `find` / `grep` / `Read` |
| No hardcoded colors | `grep -rn '#[0-9a-fA-F]'` |
| Tests pass | `pnpm test` / `pytest` |
| Theme-aware | Check `var(--color-*)` or Tailwind semantic tokens |
| Screens render | Manual verification or component tests |

## Example Output

```
## Verification Report: D1 - All Screens Theme-Aware

### Acceptance Criteria
✅ Zero hardcoded hex colors in any screen component
   - Verified: 0 hardcoded colors found (comments excluded)
✅ All screens render correctly in light mode
   - Verified: All use semantic Tailwind tokens
✅ All screens render correctly in dark mode
   - Verified: ThemeProvider + token system
✅ React Flow canvas adapts to theme
   - Verified: Nexus uses var(--color-*)
✅ All 628+ existing tests pass
   - Verified: 722/722 passing

### Status: COMPLETE ✅

### Action: Updated plan.md with [x] marks
```

## Files

- `tasks/plan.md` — Task definitions and acceptance criteria (gets updated)
- `tasks/todo.md` — Completion checklist (reference)
- `.claude/skills/mm/verify-task/SKILL.md` — Skill definition
- `.claude/skills/mm/verify-task/assets/test-commands.sh` — Verification commands

## When to Use

- After `/mm:complete-task` finishes but plan.md criteria are still unchecked
- Before starting next phase to ensure current phase is complete
- When user asks "is D1 done?" or "verify D1"
- To validate acceptance criteria before marking complete

## Related Commands

- `/mm:complete-task` — Execute tasks with full agent-skills cycle
- `/mm:safe-commit` — Validate and commit changes
