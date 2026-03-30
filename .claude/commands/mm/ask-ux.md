---
description: Consult UX Research brain about user experience and research methods
argument-hint: "[your question about UX, research, user behavior]"
---

<objective>
Query the UX Research brain (Brain #2) via Agent dispatch to get expert guidance on user research, UX methodology, and user-centered design.
Returns domain-specific expert analysis grounded in codebase reality.
</objective>

<context>
Project reality: @.planning/BRAIN-FEED.md
Domain feed: @.planning/BRAIN-FEED-02-ux.md
</context>

<process>

## Step 1 — Read Feeds

Before dispatch, read both feeds to build the IMPLEMENTED REALITY context block:
- `.planning/BRAIN-FEED.md` (global — READ ONLY)
- `.planning/BRAIN-FEED-02-ux.md` (domain feed — READ ONLY)

## Step 2 — Dispatch brain-02-ux

Dispatch `brain-02-ux` using the Task tool:

```
Task(
    subagent_type="brain-02-ux",
    prompt="""
[IMPLEMENTED REALITY]
[Paste relevant entries from both feeds that apply to this question]

[WHAT I NEED]
$ARGUMENTS

Focus: user research, flows, interaction design, user-centered decisions.
No generic UX theory. Specific decisions for THIS codebase.
"""
)
```

## Step 3 — Present Output

Present the agent's response directly. The agent returns structured output with verified insights and explicit codebase references.

</process>

<success_criteria>
- Expert analysis from UX Research brain received
- Recommendations grounded in IMPLEMENTED REALITY (not generic advice)
- Codebase-specific references cited
</success_criteria>
