---
name: mm:plan-phase
description: "Brain-aware phase planning with automatic Engram context recovery. Recovers historical context, consults domain brains, validates with Brain #7, then delegates to GSD. Use instead of /gsd:plan-phase."
argument-hint: "[phase-number] [--auto] [--research] [--skip-research] [--prd <file>]"
---

You are the MasterMind orchestrator running brain-aware phase planning with **automatic context recovery**.

## What You Do

1. **Automatic Context Recovery** — Run `mm-flow context --phase N` to recover Engram context
2. **Read Context** — Load CONTEXT.md if available, understand prior decisions + warnings
3. **Moment 2 — Domain Brain Consultation** — Brains see historical context automatically
4. **Delegate to GSD** — Standard planning with brain-informed recommendations

## Step 0 — Automatic Context Recovery (NEW)

Before anything else, recover context from Engram:

```bash
# From repo root, run:
mm-flow context --phase {phase_number}
```

This command:
- Queries Engram for observations about this phase
- Generates `.planning/phases/0N-*/CONTEXT.md` with:
  - **Prior Decisions**: Architectural choices from prior phases
  - **Warnings**: Gotchas, edge cases, issues discovered before
  - **Learnings & Precedents**: Patterns and conventions that worked
  - **Cross-Phase Contracts**: Agreements spanning multiple phases

**If context recovery fails** (mm-flow not available, Engram error, etc.):
- ✅ This is OK — continue planning without context
- ⚠️ Log the issue but don't block
- Planning proceeds with graceful degradation

### How to Execute Context Recovery in Claude

1. Use Bash tool: `cd /home/rpadron/proy/mastermind && python -m planning.mm_flow.cli.commands context --phase {N}`
2. Check for file: `.planning/phases/{:02d}-*/CONTEXT.md`
3. If file exists, read it and proceed to Step 1
4. If not found, proceed to Step 1 (graceful degradation)

### Example Output

After running `mm-flow context --phase 19`, you'll see:

```
✅ Context generated: /home/rpadron/proy/mastermind/.planning/phases/19-ui-evolution/CONTEXT.md
   Use this context when planning phase 19.
```

Or:

```
⚠️  No context found in Engram for phase 19.
   This is OK — proceeding without prior context.
```

## Step 1 — Read and Inject Context (NEW)

If CONTEXT.md exists from Step 0:

1. **Read** the file: `.planning/phases/0{phase_num}-*/CONTEXT.md`
2. **Prepend** to the planning preamble:

```markdown
# Phase {N} Planning — With Historical Context

## Historical Context (Recovered from Engram)

[PASTE FULL CONTEXT.MD HERE]

---

## Planning Task

[Original planning prompt continues below...]
```

**Why?** Brains see historical decisions and warnings automatically. No copy-paste, no manual context injection.

**What if CONTEXT.md doesn't exist?** Skip this step — planning proceeds without context.

## Step 2 — Read Everything First

Read these files BEFORE dispatching any brain:
- `.planning/BRAIN-FEED.md` — codebase reality
- `.planning/STATE.md` — current position
- `.planning/phases/NN-name/CONTEXT.md` — if exists (from Step 1)
- Code relevant to this phase's domain

Key information to extract:
- What patterns are already implemented (prevent re-inventing)
- What dependencies exist (APIs, stores, types)
- What constraints apply (performance, security, accessibility)
- **What warnings or gotchas exist** (from CONTEXT.md)

## Step 3 — Select Brains

Match phase domain to brains using this table:

| Phase type | Primary brains |
|-----------|---------------|
| Frontend UI/UX heavy | #2 UX + #3 UI + #4 Frontend + #6 QA |
| Frontend state/perf | #4 Frontend + #6 QA |
| Backend API | #5 Backend + #6 QA |
| Full stack feature | #4 + #5 + #2/#3 if UI + #6 |
| Infra/testing | #6 QA |

Read `.claude/skills/mm/brain-context/references/brain-selection.md` for full routing.

## Step 4 — Build Context Blocks

Build `[IMPLEMENTED REALITY]` and `[CORRECTED ASSUMPTIONS]` blocks from BRAIN-FEED.md + code reading + CONTEXT.md.

See `.claude/skills/mm/brain-context/references/intermediary-protocol.md` for the 6-step protocol.

## Step 5 — Dispatch Domain Brains in Parallel (Option D)

Dispatch ALL selected domain brains SIMULTANEOUSLY in a SINGLE message using the `Agent` tool.

Each brain gets: `[IMPLEMENTED REALITY] + [CORRECTED ASSUMPTIONS] + [HISTORICAL CONTEXT] + [WHAT I NEED: domain perspective]`

The agents are autonomous — they read their own feeds and query NotebookLM internally. You do NOT need to resolve SYNC tags or inject domain feed content.

**Important**: Include context reference in the prompt:

```
## Historical Context

Context has been automatically recovered from Engram for this phase.
Review the CONTEXT.md section above if present.
```

Wait for ALL agents to return.

## Step 6 — Write NN-BRAIN-OUTPUTS.md

After all domain agents return, write their outputs to:
`.planning/phases/NN-name/NN-BRAIN-OUTPUTS.md`

Format:
```markdown
# Phase NN — Domain Brain Outputs
> Generated: [ISO timestamp]
> Status: complete
> Context source: Engram (automatic recovery)

## Brain #1 — Product Strategy
[Full output]

## Brain #2 — UX Research
[Full output]

[... all dispatched brains ...]

## Dispatch Meta
| Property | Value |
|----------|-------|
| Total brains dispatched | N |
| All returned successfully | yes/no |
| Context recovery | ✅ CONTEXT.md injected / ⚠️ not available |
```

This file is consumed by Brain #7. Do NOT copy outputs into Brain #7's prompt.

## Step 7 — Dispatch Brain #7 (Barrier Pattern)

After NN-BRAIN-OUTPUTS.md is written, dispatch Brain #7:

```
Agent(
    subagent_type="brain-07-growth",
    prompt="[IMPLEMENTED REALITY] + [CORRECTED ASSUMPTIONS]

## Historical Context (Engram Recovery)

[CONTEXT.md if available, or 'No prior context available']

Read .planning/phases/NN-name/NN-BRAIN-OUTPUTS.md before evaluating.
That file contains all domain brain outputs.

[ANTI-MEDIOCRE CONSTRAINT]
Do NOT reconcile contradictions. Name the conflict. Pick the strongest expert position.

[WHAT I NEED]
Evaluate using your Systems Thinker lens. Return 5-section output + verdict.
Global Rating (0-100)."
)
```

## Step 8 — Filter and Synthesize

For each recommendation from any brain:
- Verify against codebase (grep/read)
- Mark: ✅ already solved / 📅 deferred / 🔴 real gap
- Cascade 🔴 gaps to domain brains immediately
- **Cross-reference with CONTEXT.md** — ensure no contradictions with prior decisions

Write `.planning/phases/NN-name/NN-PLAN-CONTEXT.md` with concrete implementation decisions and references to recovered context.

Example:

```markdown
## Implementation Decisions

### Decision 1: Use TypeScript for API types
- **Rationale**: As decided in Phase 15 (see CONTEXT.md), TypeScript reduces runtime errors
- **Constraint**: Must align with gRPC/Protobuf for Rust interop
- **Status**: ✅ Approved by Brain #7
```

## Step 9 — Display Synthesis

```
## Brain Consultation Complete ✅

**Context Recovery**: ✅ Engram context recovered and injected
**Brains Consulted**: [list]
**Brain #7 Verdict**: [APPROVED/APPROVED_WITH_CONDITIONS]
**Key Decisions**: [3-5 bullet points with context references]
**Context Conflicts**: [Any contradictions with prior decisions]
```

## Step 9.5 — Lifecycle Registration: Planning Start

Before delegating to GSD, register this planning session in the MM-Flow audit trail:

```bash
cd /home/rpadron/proy/mastermind/apps/api
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/mastermind_bd"
uv run python -m mastermind_cli.mm_flow.cli execute-phase --phase PHASE_NUMBER --start
```

Read `execution_id` from the output line `execution_id:<uuid>`.
Store it — the same UUID is available in `.planning/.mm-flow/runtime-state.json`.

**If DATABASE_URL is unavailable** (graceful degradation): log a warning and continue.
Planning proceeds normally without DB registration.

## Step 10 — Delegate to GSD

Use the `Skill` tool to invoke `gsd:plan-phase` with the same phase number and all flags.

The planner will use the brain-informed CONTEXT.md and recommendations. Plans will reflect expert knowledge + historical continuity.

## How Context Recovery Works (Transparent)

| Step | What Happens | User Sees |
|------|--------------|-----------|
| 0 | Skill runs `mm-flow context --phase N` | ✅ Context generated: ... |
| 1 | Skill reads CONTEXT.md if exists | (transparent) |
| 2-9 | Brains see context in prompt | Domain experts make better decisions |
| Output | PLAN.md with context references | "As learned in phase 12..." |

**Everything happens inside Claude's session.** No external hooks, no manual context injection.

## Graceful Degradation

| Scenario | Behavior |
|----------|----------|
| CONTEXT.md exists | ✅ Injected into preamble, brains use it |
| mm-flow not available | ⚠️ Continue without context |
| Engram query fails | ⚠️ Continue without context |
| Phase folder doesn't exist | ⚠️ Continue without context |
| All above | ✅ Planning proceeds normally (context is optional) |

## Anti-Patterns

- ❌ Dispatching brains one-at-a-time instead of in parallel
- ❌ Copying brain outputs inline into Brain #7's prompt (use NN-BRAIN-OUTPUTS.md)
- ❌ Running brain consultation AFTER GSD planning (brains must run BEFORE)
- ❌ Accepting brain responses without filtering against codebase
- ❌ Ignoring context recovered from Engram (always read and reference it)
- ❌ Treating context as gospel — verify recommendations against codebase

## Troubleshooting

### Q: "mm-flow command not found"
**A**: Skill continues without context (graceful degradation). This is OK.

### Q: "No context found in Engram"
**A**: This is expected if no prior sessions saved context. Planning proceeds normally.

### Q: "CONTEXT.md exists but looks empty"
**A**: Check if Engram has observations for this phase. If not, add them via `mem_save`.

### Q: "How do I update CONTEXT.md for next time?"
**A**: Save important discoveries/decisions to Engram via `mem_save` with `type=decision` or `type=discovery`. Next time `mm-flow context --phase N` runs, it will be included.

## Key Files

- **Skill**: `.claude/skills/mm/plan-phase/SKILL.md` (this file)
- **CLI**: `.planning/.mm-flow/cli/commands.py` (`mm-flow context`, `mm-flow plan-phase`)
- **Loader**: `.planning/.mm-flow/context_loader.py` (EngramContextLoader)
- **Brain Context**: `.claude/skills/mm/brain-context/` (routing, protocol)
- **Current Command**: `.claude/commands/mm/plan-phase.md` (original, now replaced by skill)

## References

- `.planning/BRAIN-FEED.md` — codebase reality
- `.planning/STATE.md` — current project position
- `.planning/phases/0N-*/CONTEXT.md` — recovered Engram context (Step 0 output)
- `.planning/phases/0N-*/BRAIN-OUTPUTS.md` — domain brain outputs (Step 6 output)
- `.planning/phases/0N-*/PLAN.md` — final GSD plan
