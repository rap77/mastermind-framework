---
description: Consult Backend brain about backend architecture and APIs
argument-hint: "[your question about backend, APIs, databases]"
---

<objective>
Query the Backend brain (Brain #5) via Agent dispatch to get expert guidance on backend architecture, APIs, and databases.
Returns domain-specific expert analysis grounded in codebase reality.
</objective>

<context>
Project reality: @.planning/BRAIN-FEED.md
Domain feed: @.planning/BRAIN-FEED-05-backend.md
</context>

<process>

## Step 1 — Read Feeds

Before dispatch, read both feeds to build the IMPLEMENTED REALITY context block:
- `.planning/BRAIN-FEED.md` (global — READ ONLY)
- `.planning/BRAIN-FEED-05-backend.md` (domain feed — READ ONLY)

## Step 2 — Dispatch brain-05-backend

Dispatch `brain-05-backend` using the Task tool:

```
Task(
    subagent_type="brain-05-backend",
    prompt="""
[IMPLEMENTED REALITY]
[Paste relevant entries from both feeds that apply to this question]

[WHAT I NEED]
$ARGUMENTS

Focus: backend/API design, data models, async patterns, performance.
No generic backend patterns. Specific to FastAPI + Python 3.14 + THIS codebase.
"""
)
```

## Step 3 — Present Output

Present the agent's response directly. The agent returns structured output with verified insights and explicit codebase references.

</process>

<success_criteria>
- Expert analysis from Backend brain received
- Recommendations grounded in IMPLEMENTED REALITY (not generic advice)
- Codebase-specific references cited
</success_criteria>
