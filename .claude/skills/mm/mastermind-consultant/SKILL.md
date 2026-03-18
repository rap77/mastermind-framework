---
name: mm-mastermind-consultant
description: Use when user asks for expert product, UX, design, frontend, backend, QA, or growth guidance in a MasterMind-enabled project, mentions "cerebro", "brain", "consult", or asks to evaluate/validate a feature or architecture decision. Do NOT use when project has no NotebookLM MCP connection or no .mastermind config.
---

# MasterMind Consultant

## Brain IDs (Software Dev niche)

| # | Brain | Notebook ID | Expertos |
|---|-------|-------------|---------|
| 1 | Product Strategy | `f276ccb3-0bce-4069-8b55-eae8693dbe75` | Cagan, Torres, Ries |
| 2 | UX Research | `ea006ece-00a9-4d5c-91f5-012b8b712936` | Norman, Nielsen, Hall |
| 3 | UI Design | `8d544475-6860-4cd7-9037-8549325493dd` | Cooper, Wroblewski, Saffer |
| 4 | Frontend | `85e47142-0a65-41d9-9848-49b8b5d2db33` | Abramov, Markbåge |
| 5 | Backend | `c6befbbc-b7dd-4ad0-a677-314750684208` | Fowler, Evans |
| 6 | QA/DevOps | `74cd3a81-1350-4927-af14-c0c4fca41a8e` | Humble, Majors |
| 7 | Growth/Data | `d8de74d6-7028-44ed-b4d5-784d6a9256e6` | Balfour, Kohavi |

## Quick Selection

| Question | Brain |
|----------|-------|
| Should I build this? | #1 Product Strategy |
| How do users interact? | #2 UX Research |
| How should it look/feel? | #3 UI Design |
| How do I build the frontend? | #4 Frontend |
| How do I build the backend? | #5 Backend |
| How do I test/deploy? | #6 QA/DevOps |
| Is this good? How to improve? | #7 Growth/Data |

## Standard Flows

| Flow | Sequence | When |
|------|----------|------|
| Validation | #1 → #7 | "Should I build/pivot?" |
| Full product | #1 → #2 → #3 → #4 → #5 → #6 → #7 | New feature/product |
| Technical review | #5 → #6 → #7 | Architecture/code decisions |
| Design sprint | #1 → #2 → #3 → #7 | UX/UI without implementation |

## How to Query

Always include: project name, tech stack, current phase, specific question, constraints.

```python
mcp__notebooklm-mcp__notebook_query(
    notebook_id="<brain-id>",
    query="""
    Project: B2B marketplace (Next.js 16, FastAPI, PostgreSQL)
    Phase: Sprint 5 — Product CRUD
    Team: 2 devs | Constraint: MVP in 6 weeks

    Question: Custom VIN decoder vs 3rd party API?
    Consider: dev time, cost, accuracy, maintainability.
    """
)
```

## CLI (alternative — uses context chaining)

```bash
cd <mm-cli-dir>
uv run mm orchestrate run "<brief>" --brains brain-04-frontend,brain-05-backend --use-mcp
```
