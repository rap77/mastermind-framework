---
name: mastermind-consultant
description: Use MasterMind Framework's 7 specialized brains for product and technical guidance
triggers:
  - User asks for product/tech/business advice
  - User mentions "mastermind", "cerebro", "framework", "consult"
  - User asks to evaluate/validate/approve something
  - .mastermind-active file exists in project
  - User asks about architecture, design, UX, or strategy
---

# MasterMind Consultant Skill

## Overview

This skill provides access to **7 specialized expert brains** via the MasterMind Framework. Each brain contains distilled knowledge from world-class experts in their domain.

## When This Skill Activates

This skill automatically activates when:
1. `.mastermind-active` file exists in the current project root
2. User asks questions that would benefit from expert consultation
3. User explicitly mentions "mastermind", "cerebro", or "consult"

## The 7 Brains

| Brain | ID | Expertise | Key Experts |
|-------|-----|-----------|-------------|
| **#1 Product Strategy** | `f276ccb3-0bce-4069-8b55-eae8693dbe75` | What & Why - Product definition, strategy, discovery | Marty Cagan, Teresa Torres, Perri, Eric Ries |
| **#2 UX Research** | `ea006ece-00a9-4d5c-91f5-012b8b712936` | User Experience - Research methods, user insights | Don Norman, Jakob Nielsen, Erika Hall |
| **#3 UI Design** | `8d544475-6860-4cd7-9037-8549325493dd` | Visual Design - Design systems, components, patterns | Alan Cooper, Luke Wroblewski, Dan Saffer |
| **#4 Frontend** | `85e47142-0a65-41d9-9848-49b8b5d2db33` | Frontend Architecture - React, Next.js, state mgmt | Dan Abramov, Sebastian Markbåge |
| **#5 Backend** | `c6befbbc-b7dd-4ad0-a677-314750684208` | Backend Architecture - APIs, databases, services | Martin Fowler, Eric Evans |
| **#6 QA/DevOps** | `74cd3a81-1350-4927-af14-c0c4fca41a8e` | Quality & Operations - Testing, CI/CD, reliability | Jez Humble, Charity Majors, Google SRE |
| **#7 Growth/Data** | `d8de74d6-7028-44ed-b4d4-784d6a9256e6` | Growth & Evaluation - Metrics, experimentation | Brian Balfour, Ron Kohavi |

## How to Query Brains

### Using NotebookLM MCP (Recommended)

```python
# Query a single brain
mcp__notebooklm-mcp__notebook_query(
    notebook_id="f276ccb3-0bce-4069-8b55-eae8693dbe75",
    query="How should I prioritize features for an MVP?",
    source_ids=null  # Query all sources in the brain
)

# Query with project context
mcp__notebooklm-mcp__notebook_query(
    notebook_id="85e47142-0a65-41d9-9848-49b8b5d2db33",
    query="""
    Context: Building a SaaS marketplace with Next.js 16, React 19, and Zustand.
    Question: What state management patterns should I use for a multi-tenant product catalog?
    """
)
```

### Quick Brain Selection Guide

| Question Type | Use Brain |
|---------------|-----------|
| "Should I build this?" | #1 Product Strategy |
| "How do users interact with this?" | #2 UX Research |
| "How should this look/feel?" | #3 UI Design |
| "How do I build the frontend?" | #4 Frontend |
| "How do I build the backend?" | #5 Backend |
| "How do I test/deploy this?" | #6 QA/DevOps |
| "Is this good? How do I improve?" | #7 Growth/Data |

## Standard Flows

### 1. Validation Only (Quick)
```
Brief → Brain #1 → Brain #7 → Verdict
```
**For:** "Is this idea worth pursuing?", "Should I pivot?"

### 2. Full Product (Complete)
```
Brief → #1 → #2 → #3 → #4 → #5 → #6 → #7 → Verdict
```
**For:** New product/features requiring full analysis

### 3. Technical Review
```
Current implementation → #5 → #6 → #7 → Recommendations
```
**For:** Code review, architecture decisions

### 4. Design Sprint
```
Problem → #1 → #2 → #3 → #7 → Design
```
**For:** UX/UI design without full implementation

## Query Best Practices

### DO ✓
- Include project context (tech stack, phase, constraints)
- Ask specific questions (not "what do you think?")
- Reference current sprint/phase if applicable
- Mention constraints (time, budget, team size)

### DON'T ✗
- Ask generic "what do you think" questions
- Query without context
- Skip relevant brain for the domain
- Assume the brain knows your project details

### Example Query (Good)

```python
mcp__notebooklm-mcp__notebook_query(
    notebook_id="f276ccb3-0bce-4069-8b55-eae8693dbe75",
    query="""
    Project: B2B marketplace for vehicle dealers (SaaS multi-tenant)
    Current Phase: Sprint 5-6 (Product CRUD implementation)
    Tech Stack: Next.js 16, FastAPI, PostgreSQL
    Team: 2 developers
    Constraint: Need to launch MVP in 6 weeks

    Question: Should we invest time in a custom VIN decoder or use a 3rd party API?
    Consider: Development time, cost, accuracy, maintainability.
    """
)
```

### Example Query (Bad)

```python
# BAD - Too generic, no context
mcp__notebooklm-mcp__notebook_query(
    notebook_id="f276ccb3-0bce-4069-8b55-eae8693dbe75",
    query="What do you think about VIN decoders?"
)
```

## Integration with Current Project

The framework is configured in `.mastermind/config.yaml`:

```yaml
brains:
  #1:
    name: Product Strategy
    notebook_id: f276ccb3-0bce-4069-8b55-eae8693dbe75
    active: true
  # ... (other brains)
```

## Available CLI Commands

```bash
# Check framework status
mastermind install status

# Check individual brain status
mastermind brain status #1

# Full orchestration (all brains)
mastermind orchestrate brief.md --flow full_product

# Quick validation (brains #1 + #7)
mastermind orchestrate brief.md --flow validation_only
```

## Memory References

The framework has centralized memories accessible via Serena MCP:

- `MEMORY-FINAL-2026-03-03` - Complete framework status
- `HANDOFF-2026-03-03-FRAMEWORK-100-PERCENT-COMPLETE` - Completion documentation

These can be read from ANY project:

```python
mcp__serena__read_memory(memory_name="MEMORY-FINAL-2026-03-03")
```

## Example Workflows

### Workflow 1: Architecture Decision

```
User: "Should I use Server Actions or API Routes for file upload?"

1. Identify domain: Frontend/Backend → Brains #4, #5
2. Query both brains with context
3. Get tradeoff analysis
4. Make informed decision
```

### Workflow 2: Feature Validation

```
User: "Should I add social login?"

1. Brief the feature
2. Brain #1: Strategic assessment
3. Brain #7: Viability check
4. Get APPROVE/CONDITIONAL/REJECT verdict
```

### Workflow 3: Debug Guidance

```
User: "My auth flow is failing intermittently"

1. Identify domain: Backend/QA → Brains #5, #6
2. Query with specific error details
3. Get debugging strategies
4. Implement fix
```

## Troubleshooting

### "Brain not responding"
- Check NotebookLM MCP connection
- Verify notebook ID in `.mastermind/config.yaml`
- Try: `mastermind brain status #1`

### "Which brain should I use?"
- Use the Quick Brain Selection Guide above
- When in doubt, start with #1 (Product Strategy)
- For technical questions, use domain-specific brain (#4-#6)

### "Getting vague responses"
- Add more project context to your query
- Be specific about your question
- Mention constraints and tradeoffs you care about

## Version

This skill works with MasterMind Framework v1.0.0+

For updates, check: https://github.com/rap77/mastermind-framework
