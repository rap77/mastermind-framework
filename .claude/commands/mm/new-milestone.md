---
name: mm:new-milestone
description: "Brain-aware milestone creation. Runs Moment 1 (Brain #1 + #7 validate milestone structure) then delegates to /gsd:new-milestone. Use instead of /gsd:new-milestone for brain-validated planning."
argument-hint: "[milestone name, e.g. 'v3.0 Custom Workflows']"
---

You are the MasterMind orchestrator running a brain-aware milestone creation.

## What You Do

1. **Moment 1 — Brain Consultation (automatic)**
2. **Delegate to GSD — standard milestone flow with brain insights**

## Step 1 — Read Current Reality

Read these files BEFORE dispatching any brain:
- `.planning/PROJECT.md` — what this is, requirements, constraints
- `.planning/BRAIN-FEED.md` — accumulated patterns (if exists)
- `.planning/STATE.md` — current position + decisions

Extract:
- What was completed (features, patterns, tech decisions)
- What's deferred or known gaps
- Hard constraints (performance targets, security requirements)
- The milestone the user wants to create

## Step 2 — Build Context Block

```
[IMPLEMENTED REALITY]
Milestone prev: [brief summary of what exists]
Proven patterns: [2-3 key architectural decisions]
Known gaps: [what was deferred]

[MILESTONE BRIEF]
Goal: [what this milestone needs to achieve]
Constraints: [hard limits]

[CORRECTED ASSUMPTIONS]
[What might Brain #1 assume wrong about the current state?]
[What scope creep risks should Brain #7 be aware of?]
```

## Step 3 — Dispatch Brain #1 and Brain #7 in Parallel

Use the `Agent` tool to dispatch both simultaneously in a SINGLE message:

**Brain #1 — Product Strategy** (`subagent_type="brain-01-product"`)

Prompt:
```
[context block from Step 2]

[WHAT I NEED]
I'm breaking this milestone into phases. Help me:
1. Validate the phase order — is this the right sequence given dependencies?
2. Identify any phase that tries to do too much (scope risk)
3. Flag any missing phase — what am I not thinking about?
Focus: phase boundaries and sequencing. Not implementation details.
```

**Brain #7 — Growth/Data Evaluator** (`subagent_type="brain-07-growth"`)

Prompt:
```
[context block from Step 2]

[WHAT I NEED]
Evaluate this milestone plan with your critical lens:
1. Planning Fallacy risks — what am I underestimating?
2. Omission Bias — what critical phases am I not including?
3. Systems Thinking — what feedback loops or dependencies am I missing?
No generic advice. Give me specific concerns about this milestone structure.
```

## Step 4 — Display Brain Insights

After both brains return, show the user:

```
## Brain Validation Complete

**Brain #1 (Product Strategy):**
- [2-3 key insights about phase structure]

**Brain #7 (Evaluator):**
- [2-3 key risk flags]

**Integrated into ROADMAP:** [what changed based on brain input]
```

## Step 5 — Delegate to GSD

Now run the standard GSD milestone flow:

Use the `Skill` tool to invoke `gsd:new-milestone` with the milestone name.

The ROADMAP will reflect brain-validated phase structure and risk flags.

## Anti-Patterns

- ❌ Dispatching brains without reading codebase first
- ❌ Accepting brain responses without filtering against code
- ❌ Skipping brain consultation "because we already know"
- ❌ Running Moment 1 and GSD in parallel (Moment 1 must complete first)
