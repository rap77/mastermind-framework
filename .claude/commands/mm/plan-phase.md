---
name: mm:plan-phase
description: "⚠️ DEPRECATED — Use the SKILL version instead. Skill location: .claude/skills/mm/plan-phase/SKILL.md"
argument-hint: "[phase-number] [--auto] [--research] [--skip-research] [--prd <file>]"
---

## ⚠️ DEPRECATED

This command file is **DEPRECATED**. A new **SKILL** version has been created with automatic Engram context recovery.

**Use**: `/mm:plan-phase [phase-number]` (same syntax)

**What changed**: The skill now automatically:
1. ✅ Runs `mm-flow context --phase N` to recover Engram context
2. ✅ Reads CONTEXT.md and injects it into the planning preamble
3. ✅ Brains see historical context automatically
4. ✅ No manual context injection needed

**Skill location**: `.claude/skills/mm/plan-phase/SKILL.md`

**Why the deprecation**: This command file is static and updated externally. The skill is versioned in the codebase and includes context recovery transparently.

---

## Original Documentation (Archived)

See `.claude/skills/mm/plan-phase/SKILL.md` for the full, updated documentation with context recovery integrated.

Key features in the skill version:
- **Step 0**: Automatic context recovery from Engram
- **Step 1**: Context injection into planning preamble
- **Steps 2-10**: Brain consultation + GSD delegation
- **Graceful degradation**: Planning proceeds without context if unavailable

### For Reference Only (Do Not Use)

The original steps below are now handled by the skill. Archive reference only:

1. **Moment 2 — Domain Brain Consultation (automatic, Option D)**
2. **Delegate to GSD — standard planning with brain-informed CONTEXT.md**

See skill file for full workflow.
