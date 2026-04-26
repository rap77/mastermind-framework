# Bug Fixes - Phase D E2E Test

## Bugs Found During E1 Testing

### Bug #1: discover-handler.py working_dir hardcoded

**File:** `.claude/commands/mm/discover-handler.py`
**Lines:** 116, 128
**Severity:** 🔴 CRITICAL

**Problem:**
```python
# Line 116
"working_dir": "/home/rpadron/proy/mastermind",

# Line 128
"working_dir": "/home/rpadron/proy/mastermind",
```

**Impact:**
- Discover agent writes to wrong project when executed from external projects
- Breaks `/mm:discover` functionality in non-mastermind projects

**Fix:**
```python
# Line 116 - Change to:
"working_dir": str(root_dir),

# Line 128 - Change to:
"working_dir": str(root_dir),
```

---

### Bug #2: ship-handler.py SPEC.md path incorrect

**File:** `.claude/commands/mm/ship-handler.py`
**Line:** 199
**Severity:** 🟡 MEDIUM

**Problem:**
```python
# Line 199
spec_path = Path("tasks/SPEC.md")
```

**Impact:**
- Ship precondition check fails to find SPEC.md
- False negative: reports "SPEC.md does not exist" when it actually exists

**Fix:**
```python
# Line 199 - Change to:
spec_path = Path(".planning/tasks/SPEC.md")
```

---

## Execution Plan

1. Fix discover-handler.py (2 lines)
2. Fix ship-handler.py (1 line)
3. Test fixes manually
4. Run tests to ensure no regression
5. Commit with message: `fix(phase-D): E2E bugs - discover working_dir + ship SPEC path`

## Tests to Verify Fixes

### Bug #1 Fix Test
```bash
# From external project
cd /tmp/mm-test-project
/mm:discover "Test idea"
# Should create files in /tmp/mm-test-project, NOT /home/rpadron/proy/mastermind
```

### Bug #2 Fix Test
```bash
# From mastermind project
python3 .claude/commands/mm/ship-handler.py --verify
# Should report: spec_exists: true (if .planning/tasks/SPEC.md exists)
```

---

**Status:** 🔧 Ready to fix
**Created:** 2026-04-25 (E1 testing)
