# /mm:plan-phase Skill — Context Recovery Integration

This skill integrates automatic Engram context recovery into brain-aware phase planning.

## Quick Start

```bash
/mm:plan-phase 19
```

This runs:
1. ✅ Context recovery: `mm-flow context --phase 19`
2. ✅ Context injection: Reads CONTEXT.md, prepends to preamble
3. ✅ Brain consultation: Domain brains see context automatically
4. ✅ GSD delegation: Standard planning with context references

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Complete skill documentation (10 steps) |
| `README.md` | This file — quick reference |

## Workflow (Under the Hood)

```
User runs: /mm:plan-phase 19
    ↓
Step 0 (NEW):
    Bash: mm-flow context --phase 19
    Output: .planning/phases/19-*/CONTEXT.md
    ↓
Step 1 (NEW):
    Read CONTEXT.md if exists
    Prepend to planning preamble
    ↓
Steps 2-9:
    Brain consultation (domains see context automatically)
    Write NN-BRAIN-OUTPUTS.md
    Brain #7 evaluation (barrier pattern)
    Filter & synthesize
    ↓
Step 10:
    Delegate to /gsd:plan-phase
    ↓
Output:
    PLAN.md with context references
    "As learned in phase 15..." (references to CONTEXT.md)
```

## Context Recovery Details

### What Gets Recovered?

From Engram (via `mm-flow context`):

- **Prior Decisions**: Architectural choices from phases 1-18
- **Warnings**: Gotchas, edge cases, issues discovered before
- **Learnings & Precedents**: Patterns and conventions that worked
- **Cross-Phase Contracts**: Agreements spanning multiple phases

### What Happens If Context Is Missing?

✅ **Graceful degradation**: Planning proceeds normally.

Example scenarios:

| Scenario | Behavior |
|----------|----------|
| Phase 1 (no prior context) | ✅ Plan without context |
| mm-flow not available | ✅ Continue, log warning |
| Engram query fails | ✅ Continue, log warning |
| CONTEXT.md empty | ✅ Continue, proceed to brain consultation |

### When Should Context Be Created?

Context is created automatically by:

1. **You** (developer): Save observations to Engram via `mem_save`
   - Type: `decision`, `discovery`, `bugfix`, `pattern`, etc.
   - Next time `mm-flow context --phase N` runs, new observations included

2. **Next session**: When `/mm:plan-phase N` runs, `mm-flow context` queries updated Engram

## Example: Phase 19 Planning

```bash
/mm:plan-phase 19
```

Output:

```
Step 0: Recovering context from Engram...
✅ Context generated: .planning/phases/19-ui-evolution/CONTEXT.md
   - Prior Decisions: 3 items
   - Warnings: 2 items
   - Learnings & Precedents: 5 items
   - Cross-Phase Contracts: 4 items

Step 1: Injecting context into planning preamble...
✅ CONTEXT.md (847 chars) prepended

Step 2-9: Consulting domain brains...
[Brains see: historical context + domain expertise]

Brain #2 UX Research output:
  "As noted in Phase 15 (CONTEXT.md), button alignment should use
   the 16px grid pattern. Continuing with that precedent..."

Brain #7 verdict:
  ✅ APPROVED_WITH_CONDITIONS
  Rating: 89/100

Step 10: Delegating to /gsd:plan-phase...
[GSD planning with context references]

Output:
  PLAN.md created: .planning/phases/19-ui-evolution/PLAN.md
  Status: ready for review
```

## Key Differences from Original Command

Original command (`.claude/commands/mm/plan-phase.md` — deprecated):
- Manual brain consultation
- No context recovery
- No historical context in preamble
- Brains saw only current state

New skill (`.claude/skills/mm/plan-phase/SKILL.md`):
- ✅ Automatic context recovery from Engram
- ✅ Context prepended to preamble
- ✅ Brains see historical context automatically
- ✅ CONTEXT.md references in PLAN.md output
- ✅ Graceful degradation if context missing
- ✅ Everything transparent, inside Claude session

## Troubleshooting

### "mm-flow command not found"

**Symptom**: Bash error when running `mm-flow context --phase N`

**Solution**:
1. Check Python path: `cd /home/rpadron/proy/mastermind`
2. Try explicit: `python -m planning.mm_flow.cli.commands context --phase N`
3. Skill continues gracefully if command fails

### "No context found in Engram"

**This is normal** if no prior sessions saved context for this phase.

**To create context next time**:
1. Use `mem_save` to save decisions/discoveries to Engram
2. Run `/mm:plan-phase N` again
3. `mm-flow context --phase N` will include new observations

### "CONTEXT.md is empty"

**Check**:
1. Does Engram have observations for phase? (`mem_search "phase N"`)
2. Does phase folder exist? (`.planning/phases/0N-*/`)
3. Are observations actually for this project?

## Files & References

**Skill location**: `.claude/skills/mm/plan-phase/SKILL.md`

**Context recovery**:
- CLI: `.planning/.mm-flow/cli/commands.py` (mm-flow context)
- Loader: `.planning/.mm-flow/context_loader.py` (EngramContextLoader)

**Engram integration**:
- Save: `mem_save(title="...", type="decision")`
- Search: `mem_search("phase N")`
- Recover: `mm-flow context --phase N`

**Brain consultation**:
- Brain routing: `.claude/skills/mm/brain-context/references/brain-selection.md`
- Protocol: `.claude/skills/mm/brain-context/references/intermediary-protocol.md`
- Brain agents: `.claude/agents/mm/brain-01-product/` through `brain-07-growth/`

**GSD delegation**:
- Skill: `/gsd:plan-phase` (standard GSD planning)
- Output: `.planning/phases/0N-*/PLAN.md`

## Next Steps

1. ✅ Skill created with context recovery integrated
2. ✅ Context recovery from Engram automated
3. ✅ Documentation complete
4. **TODO**: Create git commit: "feat(skill): integrate automatic Engram context recovery into /mm:plan-phase"
5. **TODO**: Test workflow: `/mm:plan-phase 19 --project mastermind`

## Questions?

See SKILL.md for complete documentation (10 steps, anti-patterns, graceful degradation).
