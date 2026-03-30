---
description: Consult UI Design brain about visual design and design systems
argument-hint: "[your question about UI, visual design, components]"
---

<objective>
Query the UI Design brain (Brain #3) via Agent dispatch to get expert guidance on visual design, design systems, and UI components.
Returns domain-specific expert analysis grounded in codebase reality.
</objective>

<context>
Project reality: @.planning/BRAIN-FEED.md
Domain feed: @.planning/BRAIN-FEED-03-ui.md
</context>

<process>

## Step 1 — Read Feeds

Before dispatch, read both feeds to build the IMPLEMENTED REALITY context block:
- `.planning/BRAIN-FEED.md` (global — READ ONLY)
- `.planning/BRAIN-FEED-03-ui.md` (domain feed — READ ONLY)

## Step 2 — Dispatch brain-03-ui

Dispatch `brain-03-ui` using the Task tool:

```
Task(
    subagent_type="brain-03-ui",
    prompt="""
[IMPLEMENTED REALITY]
[Paste relevant entries from both feeds that apply to this question]

[WHAT I NEED]
$ARGUMENTS

Focus: visual design, components, design system tokens, animation, accessibility.
CSS tokens, class names, Lucide icon names — not theory.
Specific to Tailwind 4 + shadcn/ui + THIS codebase.
"""
)
```

## Step 3 — Present Output

Present the agent's response directly. The agent returns structured output with verified insights and explicit codebase references.

</process>

<success_criteria>
- Expert analysis from UI Design brain received
- Recommendations grounded in IMPLEMENTED REALITY (not generic advice)
- Codebase-specific references cited
</success_criteria>
