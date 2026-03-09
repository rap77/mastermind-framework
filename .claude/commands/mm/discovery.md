---
description: Conduct structured discovery interview using Brain #8 with AskUserQuestion UI
argument-hint: [your vague problem, requirement, or idea]
---

<objective>
Extract clear requirements from vague input through structured interview with tabulated options.

Brain #8 (Master Interviewer) generates an interview plan, then YOU conduct the interview:
- Show coverage tracker before each question
- Use AskUserQuestion with 2-4 tabulated options per question
- Route complex responses to domain brains (#1-7) for expert follow-ups
- Generate complete Q&A document with insights and gaps
</objective>

<context>
Project: ! `pwd`
Config: @ .mastermind/config.yaml
</context>

<process>
## Phase 1: Pre-Analysis (Forked Research)

Before asking questions, use Task tool with `subagent_type: Explore` to:
1. Analyze the brief for ambiguity markers
2. Cross-reference the codebase for existing patterns
3. Identify tech stack and constraints

## Phase 2: Generate Interview Plan

1. Parse brief from {{ argument }}

2. Create Python script that:
   ```python
   from mastermind_cli.orchestrator.coordinator import Coordinator
   coordinator = Coordinator(use_mcp=True)
   result = coordinator.generate_discovery_plan(brief, use_mcp=True)
   print(result['plan'])
   ```

3. Execute with `uv run` and parse the plan

## Phase 3: Conduct Interview (AskUserQuestion)

### Initialize Coverage Tracker
```
Coverage: Problem [pending] | Users [pending] | Platforms [pending] | Features [pending]
```

### For each category in the plan:
1. **Display coverage tracker** - Mark current category as [in_progress]
2. **Parse question from plan** - Extract question, target_brain, context
3. **Generate 2-4 options** - Create smart choices based on:
   - The question context
   - Common patterns in the domain
   - The target brain's expertise
   - "Other" option for custom input

4. **Use AskUserQuestion:**
   ```python
   AskUserQuestion(
       questions=[{
           "question": "<parsed question>",
           "header": "<category name>",
           "options": [
               {"label": "Option A", "description": "Explanation"},
               {"label": "Option B", "description": "Explanation"},
               {"label": "Other", "description": "Custom response"}
           ],
           "multiSelect": false
       }]
   )
   ```

5. **Route to domain brain if needed:**
   - If target_brain is set and response is complex
   - Query that brain via MCP for follow-up insights
   - Present insights as next question context

6. **Mark category as [done]** after satisfactory response

### Completion Criteria
- All categories marked [done]
- OR user requests to end early
- Propose completion: "I think we've covered [list]. Ready to generate requirements document?"

## Phase 4: Generate Deliverable

Compile all Q&A pairs into:
```markdown
# Discovery Interview Results

## Session Metadata
- Brief: {{ argument }}
- Date: {{ timestamp }}
- Categories covered: {{ list }}

## Questions & Answers
### Users & Personas
**Q:** What type of users...?
**A:** {{ response }}

### Domain Brain Insights
**Brain #1 (Product Strategy):** {{ insights }}

## Gaps Detected
{{ list }}

## Recommendations
{{ list }}
```

Save to:
- `logs/interviews/hot/YYYY-MM/INTERVIEW-{{timestamp}}.yaml`
- `logs/interviews/json/YYYY-MM/INTERVIEW-{{timestamp}}.json`

Display markdown version in response.
</process>

<success_criteria>
- Brief analyzed for ambiguity
- Interview plan generated via Brain #8 MCP
- Questions asked via AskUserQuestion with 2-4 tabulated options
- Coverage tracker displayed before each question
- Domain brains consulted for follow-ups
- Complete Q&A document generated in YAML/JSON/Markdown
- Output files created in logs/interviews/
</success_criteria>

<examples>
Example 1 - Vague app idea:
{{ argument }} = "Quiero una app moderna"

Phase 1: Explore codebase → existing tech stack detected
Phase 2: Brain #8 generates plan with categories: Users, Platforms, "Modern" definition
Phase 3:
  Coverage: Problem [done] | Users [in progress] | Platforms [pending]

  AskUserQuestion:
    "¿Qué tipo de usuarios usarán esta app?"
    Options: B2B enterprise, B2C consumers, Both, Other

  User selects "B2B enterprise"
  Route to Brain #1 (Product) → insights about enterprise needs

  Coverage: Problem [done] | Users [done] | Platforms [in progress]

  AskUserQuestion:
    "¿Plataforma de lanzamiento?"
    Options: Web only, Mobile first (iOS/Android), Web + Mobile, Other

  User selects "Mobile first"
  Route to Brain #4 (Frontend) → React Native vs native insights

Phase 4: Generate clarified requirements document

Example 2 - Marketing brief:
{{ argument }} = "quiero una agencia de marketing digital y redes sociales"

Phase 2: Brain #8 detects need for niche definition
Phase 3:
  Coverage: Nicho [in progress] | Servicios [pending] | Clientes [pending]

  AskUserQuestion:
    "¿Qué nicho de marketing digital te interesa?"
    Options: B2B lead gen, E-commerce, Content marketing, Todos

  User selects "E-commerce"

  AskUserQuestion:
    "¿Servicios principales a ofrecer?"
    Options: SEO + Ads, Social media management, Full funnel, Otros

Phase 4: Document specifies e-commerce marketing agency focus
</examples>

<notes>
**Duration:** 5-15 minutes (10-20 questions typical)

**When to use:**
- Client onboarding for agencies
- Feature request clarification
- Vague ideas need direction
- Technical specifications needed
- Detecting expertise gaps

**Coverage Tracker Format:**
Display as: `Coverage: Cat1 [status] | Cat2 [status] | ...`
Status values: [pending], [in progress], [done]

**AskUserQuestion Options:**
- Always provide 2-4 smart options (never obvious choices)
- Include "Other" as last option for custom input
- Set multiSelect: false for single choice, true for multiple
- Descriptions should explain the implications of each choice

**Brains mapping:**
- Brain #1 (Product): What to build and why
- Brain #2 (UX): User experience and research
- Brain #3 (UI): Visual design
- Brain #4 (Frontend): Frontend architecture
- Brain #5 (Backend): Backend and APIs
- Brain #6 (QA): Testing and operations
- Brain #7 (Growth): Metrics and evaluation

**Related commands:**
- /mm:ask-product - Get product insights without interview
- /mm:generate-prp - Create implementation plan from requirements
- /mm:project-health-check - Full 7-brain project analysis
</notes>

<on_error>
If MCP is unavailable:
- Generate basic plan with 2-3 generic questions
- Use simple options for AskUserQuestion
- Still generate valid deliverable
- Warn user: "Brain #8 unavailable, using basic interview mode"
</on_error>
