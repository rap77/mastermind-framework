---
description: Conduct structured discovery interview using Brain #8 (Master Interviewer)
argument-hint: [your vague problem, requirement, or idea]
---

<objective>
Extract clear requirements from vague input through structured interview.

Brain #8 (Master Interviewer) conducts an iterative interview to:
- Detect and clarify ambiguity in your input
- Ask structured questions about users, platforms, features
- Route responses to domain brains (#1-7) for expert follow-ups
- Generate a complete Q&A document with insights and gaps
</objective>

<context>
Project: ! `pwd`
Config: @ .mastermind/config.yaml
</context>

<process>
1. Parse the brief from {{ argument }}

2. Create Python script that:
   - Imports Coordinator from mastermind_cli.orchestrator.coordinator
   - Calls coordinator._detect_flow(brief) to check if discovery is needed
   - If discovery: Calls coordinator._execute_discovery_flow(brief)
   - The coordinator will:
     * Query Brain #8 via MCP to generate interview plan
     * Conduct iterative Q&A with input() prompts
     * Route responses to domain brains (#1-7) for follow-ups
     * Generate final deliverable (JSON/YAML/Markdown)

3. Execute the script with uv run

4. Present the interview document to user with:
   - Session ID and metadata
   - Questions asked and answers received
   - Insights from domain brains
   - Gaps detected (if any)
   - Recommendations

5. Show output file locations:
   - YAML: logs/interviews/hot/YYYY-MM/INTERVIEW-*.yaml
   - JSON: logs/interviews/json/YYYY-MM/INTERVIEW-*.json
</process>

<success_criteria>
- Brief analyzed for ambiguity
- Interview plan generated via Brain #8
- Iterative questions asked interactively
- Domain brains consulted for follow-ups
- Complete Q&A document generated
- Output files created in logs/interviews/
</success_criteria>

<examples>
Example 1 - Vague app idea:
{{ argument }} = "Quiero una app moderna"
→ Detects ambiguity (short + "moderna" marker)
→ Asks about industry, users, platforms, what "modern" means
→ Routes to Product (#1), UX (#2), Frontend (#4) brains
→ Generates clarified requirements document

Example 2 - Client onboarding:
{{ argument }} = "Cliente de retail necesita sistema de inventario"
→ Covers users, platforms, features, business logic
→ 10-15 questions across multiple categories
→ Structured brief ready for development team

Example 3 - Technical specification:
{{ argument }} = "Necesito integrar OAuth con Google y Microsoft"
→ Focuses on technical requirements
→ Brain #5 (Backend) provides deep security follow-up
→ Generates technical specification with API endpoints

Example 4 - Gap detection:
{{ argument }} = "SEO and content marketing system"
→ Interview proceeds normally
→ Brain #8 detects SEO expertise not in current brains
→ Recommends creating Brain #9 (Growth Marketing)
</examples>

<notes>
**Duration:** 5-15 minutes (10-20 questions typical)

**When to use:**
- Client onboarding for agencies
- Feature request clarification
- Vague ideas need direction
- Technical specifications needed
- Detecting expertise gaps

**Output formats:**
- Markdown: Displayed in response (human-readable)
- YAML: logs/interviews/hot/YYYY-MM/ (logging)
- JSON: logs/interviews/json/YYYY-MM/ (machine-readable)

**Brains involved:**
- Brain #8 (Master Interviewer) - conducts interview
- Brains #1-7 (Domain experts) - provide follow-up insights

**Related commands:**
- /mm:ask-product - Get product insights without interview
- /mm:generate-prp - Create implementation plan from requirements
- /mm:project-health-check - Full 7-brain project analysis
</notes>

<on_error>
If MCP is unavailable, the coordinator falls back to mock mode:
- Generates basic interview plan without Brain #8
- Uses simple follow-up logic
- Still creates valid output documents
</on_error>
