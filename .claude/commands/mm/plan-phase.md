---
name: mm:plan-phase
description: "Brain-aware phase planning. Runs Moment 2 (domain brains inject expert knowledge) then delegates to /gsd:plan-phase. Use instead of /gsd:plan-phase for brain-enriched plans."
argument-hint: "[phase-number] [--auto] [--research] [--skip-research] [--prd <file>]"
---

You are the MasterMind orchestrator running a brain-aware phase planning.

## What You Do

1. **Moment 2 — Domain Brain Consultation (automatic, Option D)**
2. **Delegate to GSD — standard planning with brain-informed CONTEXT.md**

## Step 1 — Read Everything First

Read these files BEFORE dispatching any brain:
- `.planning/BRAIN-FEED.md` — codebase reality
- `.planning/STATE.md` — current position
- `.planning/phases/NN-name/NN-CONTEXT.md` — if discuss-phase ran already
- Code relevant to this phase's domain

Key information to extract:
- What patterns are already implemented (prevent re-inventing)
- What dependencies exist (APIs, stores, types)
- What constraints apply (performance, security, accessibility)

## Step 2 — Select Brains

Match phase domain to brains using this table:

| Phase type | Primary brains |
|-----------|---------------|
| Frontend UI/UX heavy | #2 UX + #3 UI + #4 Frontend + #6 QA |
| Frontend state/perf | #4 Frontend + #6 QA |
| Backend API | #5 Backend + #6 QA |
| Full stack feature | #4 + #5 + #2/#3 if UI + #6 |
| Infra/testing | #6 QA |

Read `.claude/skills/mm/brain-context/references/brain-selection.md` for full routing.

## Step 3 — Build Context Blocks

Build `[IMPLEMENTED REALITY]` and `[CORRECTED ASSUMPTIONS]` blocks from BRAIN-FEED.md + code reading.

See `.claude/skills/mm/brain-context/references/intermediary-protocol.md` for the 6-step protocol.

## Step 4 — Dispatch Domain Brains in Parallel (Option D)

Dispatch ALL selected domain brains SIMULTANEOUSLY in a SINGLE message using the `Agent` tool.

Each brain gets: `[IMPLEMENTED REALITY] + [CORRECTED ASSUMPTIONS] + [WHAT I NEED: domain perspective]`

The agents are autonomous — they read their own feeds and query NotebookLM internally. You do NOT need to resolve SYNC tags or inject domain feed content.

Wait for ALL agents to return.

## Step 5 — Write NN-BRAIN-OUTPUTS.md

After all domain agents return, write their outputs to:
`.planning/phases/NN-name/NN-BRAIN-OUTPUTS.md`

Format:
```markdown
# Phase NN — Domain Brain Outputs
> Generated: [ISO timestamp]
> Status: complete

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
```

This file is consumed by Brain #7. Do NOT copy outputs into Brain #7's prompt.

## Step 6 — Dispatch Brain #7 (Barrier Pattern)

After NN-BRAIN-OUTPUTS.md is written, dispatch Brain #7:

```
Agent(
    subagent_type="brain-07-growth",
    prompt="[IMPLEMENTED REALITY] + [CORRECTED ASSUMPTIONS]

Read .planning/phases/NN-name/NN-BRAIN-OUTPUTS.md before evaluating.
That file contains all domain brain outputs.

[ANTI-MEDIOCRE CONSTRAINT]
Do NOT reconcile contradictions. Name the conflict. Pick the strongest expert position.

[WHAT I NEED]
Evaluate using your Systems Thinker lens. Return 5-section output + verdict.
Global Rating (0-100)."
)
```

## Step 7 — Filter and Synthesize

For each recommendation from any brain:
- Verify against codebase (grep/read)
- Mark: ✅ already solved / 📅 deferred / 🔴 real gap
- Cascade 🔴 gaps to domain brains immediately

Write `.planning/phases/NN-name/NN-CONTEXT.md` with concrete implementation decisions.

## Step 8 — Display Synthesis

```
## Brain Consultation Complete

**Brains consulted:** [list]
**Brain #7 verdict:** [APPROVED/APPROVED_WITH_CONDITIONS]
**Key decisions:** [3-5 bullet points]
```

## Step 9 — Delegate to GSD

Use the `Skill` tool to invoke `gsd:plan-phase` with the same phase number and all flags.

The planner will use the brain-informed CONTEXT.md. Plans will reflect expert knowledge.

## Anti-Patterns

- ❌ Dispatching brains one-at-a-time instead of in parallel
- ❌ Copying brain outputs inline into Brain #7's prompt (use NN-BRAIN-OUTPUTS.md)
- ❌ Running brain consultation AFTER GSD planning (brains must run BEFORE)
- ❌ Accepting brain responses without filtering against codebase
