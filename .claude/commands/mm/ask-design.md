---
description: Consult UI Design brain about visual design and design systems
argument-hint: [your question about UI, visual design, components]
---

<objective>
Query the UI Design brain (Brain #3) to get expert guidance on visual design, design systems, and UI components.

This helps answer "how should this look?" and "what visual pattern?" using world-class design expertise.
</objective>

<context>
Project: ! `pwd`
Config: @ .mastermind/config.yaml
</context>

<process>
1. Identify the core design question from
2. Build query with project context
3. Read notebook_id from config.yaml: brains['3'].notebook_id — query UI Design brain via MCP with that id
4. Present the brain's response with visual design recommendations
</process>

<success_criteria>
- UI Design brain consulted
- Design guidance provided
- Visual patterns suggested
</success_criteria>
