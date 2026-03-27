---
description: Consult QA/DevOps brain about testing and operations
argument-hint: [your question about testing, QA, CI/CD, DevOps]
---

<objective>
Query the QA/DevOps brain (Brain #6) to get expert guidance on testing, quality assurance, and operations.

This helps answer "how do we test this?" and "how do we deploy this?" using world-class QA/DevOps expertise.
</objective>

<context>
Project: ! `pwd`
Config: @ .mastermind/config.yaml
</context>

<process>
1. Identify the core QA/DevOps question from
2. Build query with project context
3. Read notebook_id from config.yaml: brains['6'].notebook_id — query QA/DevOps brain via MCP with that id
4. Present the brain's response with testing and operations recommendations
</process>

<success_criteria>
- QA/DevOps brain consulted
- Testing strategy provided
- Operations guidance included
</success_criteria>
