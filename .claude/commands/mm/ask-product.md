---
description: Consult Product Strategy brain about what to build and why
argument-hint: "[your question about product, features, prioritization]"
---

<objective>
Query the Product Strategy brain (Brain #1) via Agent dispatch to get expert guidance on product decisions, feature prioritization, and strategic direction.
Returns domain-specific expert analysis grounded in codebase reality.
</objective>

<context>
Project reality: @.planning/BRAIN-FEED.md
Domain feed: @.planning/BRAIN-FEED-01-product.md
</context>

<process>

## Step 1 — Read Feeds

Before dispatch, read both feeds to build the IMPLEMENTED REALITY context block:
- `.planning/BRAIN-FEED.md` (global — READ ONLY)
- `.planning/BRAIN-FEED-01-product.md` (domain feed — READ ONLY)

## Step 2 — Dispatch brain-01-product

Dispatch `brain-01-product` using the Task tool:

```
Task(
    subagent_type="brain-01-product",
    prompt="""
[IMPLEMENTED REALITY]
[Paste relevant entries from both feeds that apply to this question]

[WHAT I NEED]
$ARGUMENTS

Focus: product strategy, discovery, prioritization, user outcomes.
No generic product theory. Specific decisions for THIS codebase.
"""
)
```

## Step 3 — Present Output

Present the agent's response directly. The agent returns structured output with verified insights and explicit codebase references.

</process>

<success_criteria>
- Expert analysis from Product Strategy brain received
- Recommendations grounded in IMPLEMENTED REALITY (not generic advice)
- Codebase-specific references cited
</success_criteria>
