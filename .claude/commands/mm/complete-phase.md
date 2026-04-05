---
name: mm:complete-phase
description: "Full brain-aware phase lifecycle: execute + learn. Runs /mm:execute-phase then updates BRAIN-FEED.md with phase learnings. Use after a phase completes to ensure brains learn from what was built."
argument-hint: "<phase-number> [--gaps-only]"
---

You are the MasterMind orchestrator running the full brain-aware phase lifecycle.

## What You Do

1. **Execute the phase** (via `/mm:execute-phase` — includes Moment 3 validation)
2. **Update Brain Feed** — distill patterns from completed phase into BRAIN-FEED.md

## Step 1 — Execute the Phase

Run the full `/mm:execute-phase` workflow:
- Moment 3: Brain #7 validates plans
- GSD execution: plans are executed via subagents

Use the `Skill` tool to invoke `mm:execute-phase` with the phase number and flags.

Wait for all waves to complete.

## Step 2 — Post-Phase: Read What Was Built

After execution completes, read:
- All `SUMMARY.md` files for the completed phase: `.planning/phases/NN-name/NN-0*-SUMMARY.md`
- Key new files created (check SUMMARY for "files created" sections)
- `.planning/BRAIN-FEED.md` — current feed state

## Step 3 — Distill Phase Learnings

Extract from completed phase:
- New architectural invariants discovered
- Proven patterns (code that worked well)
- New libraries or tools introduced
- Anti-patterns caught and fixed
- Performance characteristics measured

Apply the compact distillation rule:
> "Will a brain give a BETTER answer because of this entry?"
> If yes → add to BRAIN-FEED.md. If no → skip.

## Step 4 — Update BRAIN-FEED.md

Append a new section to `.planning/BRAIN-FEED.md`:

```markdown
## Phase NN — [name] Learnings ([date])

### New Patterns
- [Pattern discovered with specific implementation detail]

### Invariants Locked
- [Rule that must be followed, with evidence]

### Libraries Added
- [Library name + version + what it's used for]

### Anti-Patterns Caught
- [Pattern that caused issues and how it was fixed]

### Performance Data
- [Any measured performance characteristics]
```

## Step 5 — Confirm Update

```
## Phase NN Complete

**Execution:** All plans completed
**BRAIN-FEED updated:** [N new entries added]
**Next consultation** will benefit from phase learnings.
```

## Anti-Patterns

- ❌ Copy-pasting SUMMARY.md into BRAIN-FEED (distill, don't copy)
- ❌ Adding entries that won't change brain recommendations (noise)
- ❌ Skipping feed update "because nothing was interesting" (there's always something)
- ❌ Writing to domain feeds (only write to global BRAIN-FEED.md)
