---
description: Consult Growth/Data brain about metrics and evaluation
argument-hint: "[your question about growth, metrics, A/B testing, systems design]"
---

<objective>
Query the Growth/Data brain (Brain #7) via Agent dispatch. This is a single-brain dispatch —
Brain #7 responds from its growth/data/systems domain expertise directly.

Note: In full parallel dispatch (ask-all.md or Moment 2), Brain #7 acts as evaluator of domain agents.
In this single command, it responds directly as the Growth domain expert.
</objective>

<context>
Project reality: @.planning/BRAIN-FEED.md
Domain feed: @.planning/BRAIN-FEED-07-growth.md
</context>

<process>

## Step 1 — Read Feeds

Read both feeds to build the IMPLEMENTED REALITY context block for Brain #7.

## Step 2 — Dispatch brain-07-growth

Dispatch `brain-07-growth` using the Task tool:

```
Task(
    subagent_type="brain-07-growth",
    prompt="""
[IMPLEMENTED REALITY]
[Paste relevant entries from global + growth feeds]

[CONTEXT: This is a single-domain query, not a cross-domain evaluation]
You are responding directly from your Growth/Data/Systems domain expertise.
No domain agent outputs to evaluate — answer the question as the Growth domain expert.

[WHAT I NEED]
$ARGUMENTS

Focus: growth loops, experimentation strategy, metric design, second-order effects.
Grounded in the codebase reality provided above — no generic growth theory.
"""
)
```

## Step 3 — Present Output

Present the agent's response with growth/systems insights.

</process>

<success_criteria>
- Growth/Systems perspective received from Brain #7
- Insights grounded in codebase reality (not generic growth advice)
- Second-order effects identified
</success_criteria>
