---
description: Consult Backend brain about backend architecture and APIs
argument-hint: [your question about backend, APIs, databases]
---

<objective>
Query the Backend brain (Brain #5) to get expert guidance on backend architecture, APIs, and databases.

This helps answer "how do we build the backend?" and "what API design?" using world-class backend expertise.
</objective>

<context>
Project: ! `pwd`
Config: @ .mastermind/config.yaml
</context>

<process>
1. Identify the core backend question from
2. Build query with project context
3. Read notebook_id from config.yaml: brains['5'].notebook_id — query Backend brain via MCP with that id
4. Present the brain's response with architecture recommendations
</process>

<success_criteria>
- Backend brain consulted
- Architecture guidance provided
- Implementation patterns suggested
</success_criteria>
