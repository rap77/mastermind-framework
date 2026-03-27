---
description: Consult Product Strategy brain about what to build and why
argument-hint: [your question about product, features, prioritization]
---

<objective>
Query the Product Strategy brain (Brain #1) to get expert guidance on product decisions, feature prioritization, and strategic direction.

This helps answer "what should we build?" and "why should we build it?" using world-class product expertise.
</objective>

<context>
Project: ! `pwd`
Config: @ .mastermind/config.yaml
</context>

<process>
1. Identify the core product question from
2. Build query with project context (name, tech stack, current phase)
3. Read notebook_id from config.yaml: brains['1'].notebook_id — query Product Strategy brain via MCP with that id
4. Present the brain's response clearly with key insights
</process>

<success_criteria>
- Product Strategy brain consulted
- Response includes strategic rationale
- Actionable recommendations provided
</success_criteria>
