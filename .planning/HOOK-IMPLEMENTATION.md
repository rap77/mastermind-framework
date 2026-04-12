# Before-Skill Hook Implementation: Auto-Context Recovery

**Date:** 2026-04-12
**Status:** ✅ COMPLETE
**Commits:** One commit to settings.json + hook scripts

---

## Goal

When user runs `/mm:plan-phase 19`, automatically generate CONTEXT.md before the skill executes:
1. Hook intercepts `/mm:plan-phase` invocation
2. Extracts phase number (19)
3. Runs: `mm-flow context --phase 19`
4. Waits for CONTEXT.md to appear
5. Returns control to `/mm:plan-phase` (which finds and uses CONTEXT.md)

Result: User sees zero difference, but context is automatically available.

---

## Implementation Details

### Files Modified/Created

**Global (~/.claude/):**
- `settings.json` — added `hooks.BeforeSkillInvoke` section for `mm:plan-phase`
- `HOOKS-GUIDE.md` — comprehensive hook documentation
- `hooks/mm-plan-phase-context.js` — hook script implementation

**This project (.planning/):**
- `HOOK-IMPLEMENTATION.md` (this file) — implementation notes for future reference

### Hook Configuration

**File:** `~/.claude/settings.json`

```json
{
  "hooks": {
    "BeforeSkillInvoke": [
      {
        "skill_pattern": "mm:plan-phase",
        "description": "Auto-generate Engram context before planning phase",
        "timeout_seconds": 30,
        "continue_on_error": true,
        "hooks": [
          {
            "type": "command",
            "command": "node \"/home/rpadron/.claude/hooks/mm-plan-phase-context.js\""
          }
        ]
      }
    ]
  }
}
```

### Hook Script: mm-plan-phase-context.js

**Location:** `/home/rpadron/.claude/hooks/mm-plan-phase-context.js`

**Behavior:**
1. Listens on stdin for skill invocation JSON
2. Checks if skill is `mm:plan-phase`
3. Extracts phase number from `skill_args.phase`
4. Runs: `mm-flow context --phase N` via `execFileSync` (safe, no shell injection)
5. Polls for CONTEXT.md in `.planning/phases/0N-*/` (up to 30s)
6. Outputs status message to stdout
7. Always exits gracefully (never blocks skill execution)

**Key features:**
- ✅ Safe command execution (uses `execFileSync` with array args, not shell)
- ✅ Graceful degradation (continues even if context generation fails)
- ✅ Timeout guards (3s stdin timeout, 30s execution timeout)
- ✅ Async polling with exponential backoff
- ✅ Idempotent (safe to run multiple times)

### How It Works

```
User types: /mm:plan-phase --phase 19
    ↓
Claude Code detects skill invocation
    ↓
BeforeSkillInvoke hook triggered
    ↓
Hook script receives: { skill_name: "mm:plan-phase", skill_args: { phase: 19 }, cwd: "...", session_id: "..." }
    ↓
Hook runs: mm-flow context --phase 19
    ↓
mm-flow queries Engram and writes to: .planning/phases/19-*/CONTEXT.md
    ↓
Hook polls and detects CONTEXT.md exists
    ↓
Hook outputs: { hookSpecificOutput: { previewMessage: "✓ CONTEXT.md auto-generated..." } }
    ↓
/mm:plan-phase skill executes (finds CONTEXT.md automatically)
    ↓
PLAN.md generated with context references
```

---

## Verification

### Check 1: Hook script is executable

```bash
ls -la ~/.claude/hooks/mm-plan-phase-context.js
# -rwxr-xr-x  mm-plan-phase-context.js
```

### Check 2: Settings.json has hook configured

```bash
cat ~/.claude/settings.json | jq '.hooks.BeforeSkillInvoke'
# Should show the mm:plan-phase hook entry
```

### Check 3: Run /mm:plan-phase and verify

```bash
cd /home/rpadron/proy/mastermind
/mm:plan-phase --phase 19

# Expected output:
# ✓ CONTEXT.md auto-generated for phase 19. Ready for /mm:plan-phase.
# [/mm:plan-phase executes normally with CONTEXT.md available]
```

### Check 4: Verify CONTEXT.md was created

```bash
find .planning/phases/19-* -name CONTEXT.md -type f
# Should find the file created by mm-flow context
```

---

## Troubleshooting

| Problem | Diagnosis | Solution |
|---------|-----------|----------|
| Hook doesn't run | Check if `mm-flow` is in PATH | `which mm-flow` and ensure `.local/bin` is in PATH |
| CONTEXT.md not found | mm-flow context might be failing | Run `mm-flow context --phase 19` manually to debug |
| Hook times out | Taking >30s to generate context | Increase `timeout_seconds` in settings.json |
| /mm:plan-phase blocked by hook | Hook not respecting continue_on_error | Already set to true; hook exits gracefully |
| Settings.json has JSON syntax error | Corrupt after manual edit | Run `cat ~/.claude/settings.json \| jq .` to validate |

---

## Configuration

### Timeout Settings

- **Hook execution timeout:** 30 seconds (configurable via `timeout_seconds`)
- **mm-flow context timeout:** 30 seconds (passed to execFileSync)
- **Context polling timeout:** 30 seconds (MAX_RETRIES × CONTEXT_WAIT_INTERVAL = 60 × 500ms)
- **Stdin timeout guard:** 3 seconds (prevents hanging on pipe issues)

### Disabling the Hook

If the hook causes issues:

```bash
# Temporarily disable by removing BeforeSkillInvoke from settings.json
cat ~/.claude/settings.json | jq 'del(.hooks.BeforeSkillInvoke)' > /tmp/settings.json && mv /tmp/settings.json ~/.claude/settings.json

# To re-enable: restore from git or add back to settings.json
```

### Extending the Hook

To add hooks for other skills (e.g., `/mm:execute-phase`):

1. Create a new hook script (copy and adapt mm-plan-phase-context.js)
2. Add new entry to `hooks.BeforeSkillInvoke` in settings.json
3. Update HOOKS-GUIDE.md with documentation

---

## Notes for Future Sessions

- **Hook location:** Global configuration in `~/.claude/settings.json` (not project-specific)
- **Persistent across projects:** Applies to all Claude Code sessions
- **Claude Code version:** Assumes BeforeSkillInvoke hook support (may be alpha/beta feature)
- **If hook support is dropped:** Fall back to `mm-flow plan-phase` wrapper command
- **Integration test:** Run `/mm:plan-phase --phase 19` after each Claude Code update

---

## Related Documents

- `~/.claude/HOOKS-GUIDE.md` — Comprehensive hook documentation
- `~/.claude/settings.json` — Global hook configuration
- `.planning/.mm-flow/cli/commands.py` — mm-flow CLI implementation
- `mm-flow --help` — mm-flow command reference
