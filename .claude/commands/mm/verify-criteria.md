---
name: mm:verify-criteria
description: Verify and mark acceptance criteria in plan.md as completed. Used after task completion to manually verify what was actually implemented.
argument-hint: "<task-id> [--all] [--criteria <n,n,...>]"
---

# /mm:verify-criteria

Verify and mark acceptance criteria in `tasks/plan.md` as completed.

## Usage

```bash
# Show status only
/mm:verify-criteria C1

# AUTO-VERIFY: Check each criterion and mark only what passes
/mm:verify-criteria C1 --verify

# MANUAL: Mark all as verified (use with caution)
/mm:verify-criteria C1 --all

# MANUAL: Mark specific criteria by number
/mm:verify-criteria C1 --criteria 1,3,5
```

## What It Does

### Mode 1: Show status (default)
Lists all acceptance criteria with their current verification state.

### Mode 2: Auto-verify (`--verify`)
**RECOMMENDED** — Automatically verifies each criterion:
- Executes handlers and checks for errors
- Verifies file existence
- Tests command flags
- Checks autocomplete availability
- **Marks ONLY the criteria that pass verification**
- Reports which ones need manual verification

### Mode 3: Manual mark (`--all`, `--criteria`)
Marks criteria WITHOUT verification. Use with caution.

## What Gets Auto-Verified

| Criterion Type | Verification |
|----------------|--------------|
| `Handler ejecuta sin errores` | Runs handler, checks it doesn't crash |
| `Handler --flag funciona` | Runs handler with flag, checks output |
| `Archivo X existe` | Checks file exists on disk |
| `/mm:X aparece en autocomplete` | Checks command file exists |
| `Archivo X no existe` (cleanup) | Checks file was deleted |

**NOT auto-verified:**
- Complex functional requirements
- UI/UX checks
- Integration tests
- Business logic validation

## Examples

### Interactive Mode

```
/mm:verify-criteria C1

INFO: Task C1: Crear review-handler.py
INFO: 4/9 criteria already verified

Criterion #5: "Handler ejecuta sin errores"
  → Did you verify this works? [y/N]
```

### Mark Specific Criteria

```bash
# Mark criteria 1, 3, and 5 as verified
/mm:verify-criteria C1 --criteria 1,3,5
```

### Mark All (Use Carefully)

```bash
# Mark ALL remaining criteria as verified
/mm:verify-criteria C1 --all
```

## Output

```
INFO: Task C1: Crear review-handler.py
INFO: 4/9 criteria verified
✓ Criterion #1: [x] Handler ejecuta sin errores
✓ Criterion #2: [x] --staged genera diff correcto
  Criterion #3: [ ] --last-commit genera diff del ultimo commit
✓ Criterion #4: [x] Payload incluye lista de archivos
  Criterion #5: [ ] Payload incluye diff truncado

Summary: 4/9 verified (44%)
```

## Files Modified

- `tasks/plan.md` — Updates `[ ]` to `[x]` for verified criteria

## Notes

- This command is meant to be run AFTER `/mm:complete-task` finishes
- It does NOT commit changes (use `/mm:safe-commit` separately)
- Use `--all` only if you manually verified every criterion

## Related Commands

- `/mm:complete-task` — Execute tasks with agent-skills cycle
- `/mm:safe-commit` — Commit with pre-commit validation
