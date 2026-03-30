---
description: Consult QA/DevOps brain about testing and operations
argument-hint: "[your question about testing, QA, CI/CD, DevOps]"
---

<objective>
Query the QA/DevOps brain (Brain #6) via Agent dispatch to get expert guidance on testing, quality assurance, and operations.
Returns domain-specific expert analysis grounded in codebase reality.
</objective>

<context>
Project reality: @.planning/BRAIN-FEED.md
Domain feed: @.planning/BRAIN-FEED-06-qa.md
</context>

<process>

## Step 1 — Read Feeds

Before dispatch, read both feeds to build the IMPLEMENTED REALITY context block:
- `.planning/BRAIN-FEED.md` (global — READ ONLY)
- `.planning/BRAIN-FEED-06-qa.md` (domain feed — READ ONLY)

## Step 2 — Dispatch brain-06-qa

Dispatch `brain-06-qa` using the Task tool:

```
Task(
    subagent_type="brain-06-qa",
    prompt="""
[IMPLEMENTED REALITY]
[Paste relevant entries from both feeds that apply to this question]

[WHAT I NEED]
$ARGUMENTS

Focus: testing strategy, reliability, CI/CD pipeline, quality assurance.
No generic testing theory. Specific to pytest + uv + Playwright + THIS codebase.
"""
)
```

## Step 3 — Present Output

Present the agent's response directly. The agent returns structured output with verified insights and explicit codebase references.

</process>

<success_criteria>
- Expert analysis from QA/DevOps brain received
- Recommendations grounded in IMPLEMENTED REALITY (not generic advice)
- Codebase-specific references cited
</success_criteria>
