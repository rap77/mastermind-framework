---
description: Run comprehensive 7-brain analysis on any project - new, in-progress, or stuck
argument-hint: [project-type: new|in-progress|stuck] [optional: specific focus area]
---

<objective>
Execute a comprehensive project audit using all 7 MasterMind brains to analyze current state, identify gaps, recommend improvements, and generate missing documentation.

This works for THREE project scenarios:
- **NEW**: Projects with only documentation (PRD, brief) - validates architecture before coding
- **IN-PROGRESS**: Partially built projects - analyzes what's working, what's missing, what to improve
- **STUCK**: Projects needing redirection - identifies issues and creates recovery plan
</objective>

<context>
Current project: ! `pwd`
Project type: <project-type> (default: in-progress)
Git status: ! `git status --short 2>/dev/null || echo "Not a git repo"'
Tech stack detection: ! `fd -tf -d 2 "(package\.json|requirements\.txt|go\.mod|Cargo\.toml|composer\.json)" . 2>/dev/null | head -5 || echo "No package files found"'
Config: @ .mastermind/config.yaml 2>/dev/null || @ ~/proy/mastermind/.mastermind/config.yaml
</context>

<process>
1. **Detect Project State**:
   - Scan for code, documentation, tests
   - Identify tech stack from package files
   - Determine completion percentage

2. **Query Relevant Brains** (based on project type):
   - **NEW**: Brains #1, #2, #3, #5 (architecture + design before code)
   - **IN-PROGRESS**: All 7 brains (comprehensive audit)
   - **STUCK**: Brains #1, #5, #6, #7 (diagnose issues + recovery)

3. **Generate Per-Brain Analysis Documents**:
   - Create `docs/audit/brain-{N}-{name}.md` for each consulted brain
   - Each document includes: what's good, what's missing, improvement roadmap

4. **Generate Missing Documentation**:
   - UI/UX Design System (if frontend detected)
   - API Documentation (if backend detected)
   - Testing Strategy (if tests missing)
   - Deployment Guide (if DevOps relevant)

5. **Create Executive Summary**:
   - `docs/audit/EXECUTIVE-SUMMARY.md` with overall health score, priorities, quick wins
</process>

<output>
Files created in `docs/audit/`:
- `EXECUTIVE-SUMMARY.md` - Overall project health, priorities, quick wins
- `brain-1-product-strategy.md` - Product alignment, feature prioritization, user needs
- `brain-2-ux-research.md` - UX patterns, user journey, research gaps
- `brain-3-ui-design.md` - Design system audit, component review, visual consistency
- `brain-4-frontend.md` - Frontend architecture, state management, component quality
- `brain-5-backend.md` - Backend architecture, database design, API quality
- `brain-6-qa-devops.md` - Test coverage, CI/CD, deployment, monitoring
- `brain-7-growth-data.md` - Metrics tracking, experimentation, improvement opportunities
- `missing-docs-{type}.md` - Generated documentation for gaps identified
</output>

<notebooklm_naming>
When creating a NotebookLM notebook for this audit, ALWAYS use this naming standard:

  [AUDIT] {Project Name} - {Niche} - {YYYY-MM-DD}

Examples:
  [AUDIT] ProSell SaaS - Software Development - 2026-03-05
  [AUDIT] TiendaX - E-Commerce - 2026-04-01
  [AUDIT] AppSalud - Healthcare - 2026-05-15

- {Project Name}: name of the project being audited
- {Niche}: active niche of the framework (e.g. Software Development)
- {YYYY-MM-DD}: today's date
</notebooklm_naming>

<success_criteria>
- All relevant brains consulted via NotebookLM MCP
- NotebookLM audit notebook created with correct naming standard [AUDIT] format
- Per-brain analysis documents created with actionable recommendations
- Executive summary with health score and prioritized action items
- Missing critical documentation generated (UI/UX, API, testing)
- Clear next steps identified for project continuation
</success_criteria>
