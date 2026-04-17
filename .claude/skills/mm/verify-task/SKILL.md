---
name: mm:verify-task
description: Verify MasterMind tasks are complete and mark acceptance criteria in plan.md. Trigger: user asks to verify/complete a task, or after /mm:complete-task finishes.
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
---

## When to Use

Use this skill when:
- User asks to verify if a task is complete (e.g., "verify D1", "is D1 done?")
- User asks to mark a task as complete in plan.md
- After `/mm:complete-task` finishes but plan.md criteria are still unchecked
- User wants to validate acceptance criteria before moving to next phase

## Critical Patterns

### 1. ALWAYS Verify Before Marking

NEVER mark criteria as complete without verification. Check:
- Code exists and matches requirements
- Tests pass (run `cd apps/web && pnpm test` for frontend)
- No hardcoded colors in relevant files
- Screens render in both light/dark modes

### 2. Verification Sequence

```
1. Read task definition from tasks/plan.md
2. Read completion checklist from tasks/todo.md
3. Verify each acceptance criterion:
   - Code inspection (grep, find, read files)
   - Test execution (if applicable)
   - Visual verification (if applicable)
4. Mark verified criteria as [x] in plan.md
5. Update task status line (if exists)
```

### 3. What Gets Verified

| Criterion Type | Verification Method |
|----------------|---------------------|
| Code exists | `find` / `grep` / `Read` |
| No hardcoded colors | `grep -rn '#[0-9a-fA-F]'` |
| Tests pass | `pnpm test` / `pytest` |
| Theme-aware | Check `var(--color-*)` or Tailwind semantic tokens |
| Screens render | Manual verification or component tests |

### 4. NEVER Guess

If unsure whether a criterion is met:
- Ask user for clarification
- Run verification commands
- Don't mark as complete without evidence

## Code Examples

### Verification Command Pattern

```bash
# Check for hardcoded hex colors (exclude comments, globals.css, tests)
grep -rn '#[0-9a-fA-F]\{3,6\}' apps/web/src/components/ \
  | grep -v '.test.' | grep -v 'globals.css' | grep -v 'var(' | grep -v '//'

# Verify theme tokens are used
grep -l "var(--color-" apps/web/src/components/*/tsx

# Run tests
cd apps/web && pnpm test
cd apps/api && uv run pytest
```

### plan.md Update Pattern

```markdown
**Acceptance Criteria:**
- [x] Zero hardcoded hex colors in any screen component  ← VERIFIED
- [x] All screens render correctly in light mode
- [x] All screens render correctly in dark mode
- [x] React Flow canvas adapts to theme (Nexus + Flow Designer)
- [x] All 628+ existing tests pass (722 passing)
```

## Commands

```bash
# Verify D1 (example)
/mm:verify-task D1

# Verify and report only (don't mark)
/mm:verify-task D1 --dry-run

# Verify specific criterion
/mm:verify-task D1 --criterion "hardcoded colors"
```

## Verification Matrix

| Task | Key Checks | Command |
|------|------------|---------|
| **D1** (Theme-aware) | No hex colors, theme tokens, tests pass | `grep -rn '#[0-9a-fA-F]'` + `pnpm test` |
| **D2** (Wiring) | Simulate button, Edit button, adapter exists | `find flow-execution-adapter.ts` |
| **A1** (Theming) | ThemeProvider, toggle, localStorage | Check `theme-provider.tsx` |
| **B1** (Flow Designer) | React Flow canvas, nodes, edges | `find FlowDesignerCanvas.tsx` |

## Output Format

After verification, output:

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

## Resources

- **Task definitions**: [tasks/plan.md](../../../../tasks/plan.md)
- **Completion checklist**: [tasks/todo.md](../../../../tasks/todo.md)
- **Acceptance criteria**: Defined in each task section of plan.md
- **Test commands**: See [assets/test-commands.sh](assets/test-commands.sh)

## Error Handling

If verification fails:
- Report which criterion failed
- Show evidence (grep output, test failure, etc.)
- DON'T mark any criteria as complete
- Suggest next steps to fix

If partial completion:
- Mark only verified criteria as [x]
- Report remaining work clearly
- Update task status line if exists
