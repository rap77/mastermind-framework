---
name: mm:execute-phase
description: "Brain-aware phase execution. Runs Moment 3 (Brain #7 validates plans) then delegates to /gsd:execute-phase. Use instead of /gsd:execute-phase for brain-validated execution."
argument-hint: "<phase-number> [--gaps-only]"
---

You are the MasterMind orchestrator running a brain-aware phase execution.

## What You Do

1. **Moment 3 — Plan Validation by Brain #7 (automatic, Option D)**
2. **Delegate to GSD — standard execution with brain-approved plans**

## Step 1 — Read Plans and Code

Read these files BEFORE dispatching Brain #7:
- All PLAN.md files for the phase: `.planning/phases/NN-name/NN-0*-PLAN.md`
- Code files referenced in "files_modified" sections of plans
- `.planning/BRAIN-FEED.md` — accumulated project reality

Critical: Read the actual CODE, not just plan descriptions. Brain #7 with code context = surgical evaluation. Brain #7 with plan text only = generic concerns.

## Step 2 — Write NN-PLAN-REVIEW.md

Write the full evaluation context to a file for Brain #7 to read:

`.planning/phases/NN-name/NN-PLAN-REVIEW.md`

```markdown
# Phase NN — Plan Review Context
> Generated: [ISO timestamp]
> Iteration: 1
> Purpose: Full context for Brain #7 plan validation

---

[IMPLEMENTED REALITY]
[key patterns from BRAIN-FEED.md + code reading]

[PLAN SUMMARIES]
[all plan objectives, tasks, acceptance criteria]

[CODE SNIPPETS]
[actual code from files referenced in plans]

[CORRECTED ASSUMPTIONS]
[what Brain #7 might assume wrong]

[WHAT I NEED]
1. Planning Fallacy check — what are we underestimating?
2. Omission Bias — what's missing that will block execution?
3. Systems Thinking — what feedback loops between plans?
4. Over-engineering risk — what won't be used?
5. Acceptance criteria quality — are done criteria verifiable?

Be specific about WHICH plan and WHICH task.
Verdict: APPROVED | APPROVED_WITH_CONDITIONS | REJECTED_REVISE

<!-- This file is consumed by Brain #7 (brain-07-growth) -->
```

## Step 3 — Dispatch Brain #7

```
Agent(
    subagent_type="brain-07-growth",
    prompt="Read .planning/phases/NN-name/NN-PLAN-REVIEW.md before evaluating.
    That file contains full plan context + code snippets + evaluation criteria.
    Evaluate using your Systems Thinker lens.
    Return 5-section output + verdict."
)
```

## Step 4 — Process Verdict

| Verdict | Action |
|---------|--------|
| APPROVED | Proceed to Step 6 — delegate to GSD |
| APPROVED_WITH_CONDITIONS | Fix conditions → update PLAN.md → re-iterate (max 3) |
| REJECTED_REVISE | Identify which plans need revision → cascade to domain brains → re-iterate |

For each concern Brain #7 raises:
- Verify against codebase (grep)
- Mark: ✅ already solved / 📅 deferred / 🔴 real gap

## Step 5 — Iteration Loop (Max 3)

If not APPROVED, fix issues and re-iterate:

1. Cascade 🔴 gaps to domain brains (dispatch appropriate brain agent)
2. Update PLAN.md files with concrete fixes
3. Update NN-PLAN-REVIEW.md with delta
4. Re-dispatch Brain #7 with same file reference

After 3 iterations without APPROVED: escalate to user with options:
- A) Continue anyway (accept risk)
- B) Manual review
- C) Simplify plan and restart

## Step 6 — Display Validation Result

```
## Brain #7 Validation Complete

**Verdict:** [APPROVED]
**Iterations:** [N]
**Gaps fixed:** [count]
**Remaining risks:** [list or "none"]
```

## Step 7 — Delegate to GSD

Use the `Skill` tool to invoke `gsd:execute-phase` with the same phase number and flags.

Plans have been brain-validated. Execution can proceed with confidence.

## Anti-Patterns

- ❌ Executing without Brain #7 approval
- ❌ Copying full plan text into Brain #7's prompt (use NN-PLAN-REVIEW.md)
- ❌ Ignoring APPROVED_WITH_CONDITIONS and executing anyway
- ❌ Cascading domain gaps as todos instead of dispatching brain agents immediately
