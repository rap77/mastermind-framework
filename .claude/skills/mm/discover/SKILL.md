---
name: mm-discover
description: >
  Discovery skill for MasterMind: analyzes new ideas or audits existing projects
  to generate SPEC.md, plan.md, and todo.md ready for /mm:complete-task.
  Integrates with Brain #1 (Product), #4 (Backend), #5 (Frontend), #7 (Growth).
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0.0"
---

# mm-discover — Discovery & Planning Skill

**Misión:** Convertir ideas crudas en planes accionables (o auditar proyectos existentes) mediante el proceso de discovery con los cerebros especializados de MasterMind.

## ¿Cuándo Usar?

Esta skill es **PROACTIVA** — se activa cuando:

**Modo Nuevo (Proyecto):**
- El usuario ejecuta `/mm:discover "idea..."`
- El usuario expresa una idea de proyecto ("quiero construir...", "estoy pensando en...")
- No existe `tasks/plan.md` en el proyecto actual
- El usuario pregunta "¿cómo empiezo este proyecto?"

**Modo Existente (Audit):**
- El usuario ejecuta `/mm:discover --existing`
- El proyecto ya tiene `tasks/plan.md` pero está desactualizado
- El usuario pregunta "¿qué falta para terminar?", "¿qué está roto?", "health check"
- El usuario quiere re-planificar basado en el estado actual

**No esperés a que el usuario lo pida explícitamente.** Si detectás alguno de estos indicios, activá la skill.

---

## Modo A: Proyecto Nuevo

### Paso 1: Clarification (Brain #1)

```python
# Consultar Brain #1 para clarificar la idea
mcp__notebooklm-mcp__notebook_query(
    notebook_id="BRAIN_01_PRODUCT_STRATEGY",
    query=f"""
Project Idea: {user_idea}

Questions:
1. What problem are we solving? (Problem Statement)
2. For whom? (Target Users, User Personas)
3. What's the MVP vs v1? (MoSCoW prioritization)
4. What are the non-negotiables? (Technical, business, or UX constraints)
5. What's the USP vs existing solutions?

Constraints:
- Be specific about user personas (avoid "everyone")
- Identify top 3 competitors
- MVP must ship in < 8 weeks
- """
)
```

**Output de Brain #1:**
- Problem statement claro
- User personas identificadas
- MoSCoW list (Must/Should/Could/Won't)
- Non-negotiables
- Competitive analysis (3 competitors)

---

### Paso 2: Exploration (Brain #4 + #5)

**Backend (Brain #4):**
```python
mcp__notebooklm-mcp__notebook_query(
    notebook_id="BRAIN_04_BACKEND",
    query=f"""
Project Context: {brain1_output}

Questions:
1. What backend architecture fits this problem? (Monolith, Microservices, Serverless)
2. What's the recommended tech stack? (Language, Framework, Database)
3. What are the key API endpoints?
4. What data model is needed?
5. What are the non-negotiable technical constraints?
"""
)
```

**Frontend (Brain #5):**
```python
mcp__notebooklm-mcp__notebook_query(
    notebook_id="BRAIN_05_FRONTEND",
    query=f"""
Project Context: {brain1_output}

Questions:
1. What frontend framework fits this problem? (React, Vue, Next.js)
2. What UI components will we need?
3. What's the mobile strategy? (Responsive, PWA, Native)
4. What state management approach? (Redux, Zustand, Context)
5. What are the accessibility requirements?
"""
)
```

**Output:**
- Tech stack recomendado
- Architecture modular
- API endpoints identificados
- Data model propuesto
- UI/UX considerations

---

### Paso 3: Architecture

Basado en outputs de Brain #4 + #5, definir:

```
Architecture Overview:
- Frontend: [Framework] + [State Management]
- Backend: [Framework] + [Language]
- Database: [SQL/NoSQL] + [ORM]
- Auth: [Strategy]
- Hosting: [Provider]
```

---

### Paso 4: Spec Generation

Crear `SPEC.md` con 15 secciones:

```markdown
# [Project Name] — Specification

**Generated:** YYYY-MM-DD
**Mode:** New Project Discovery

## 1. Problem Statement
[From Brain #1]

## 2. Proposed Solution
[High-level solution]

## 3. Target Users
[User personas from Brain #1]

## 4. Key Features
[MVP features from MoSCoW]

## 5. Success Criteria
[27+ criteria across Frontend, Backend, Functional, Integration]

## 6. Architecture Overview
[From Step 3]

## 7. Tech Stack
[From Brain #4 + #5]

## 8. Data Model
[Key entities and relationships]

## 9. API Endpoints
[REST/GraphQL endpoints]

## 10. UI/UX Considerations
[From Brain #5]

## 11. Security Requirements
[Auth, encryption, GDPR, etc.]

## 12. Performance Requirements
[Load time, concurrent users, etc.]

## 13. Testing Strategy
[Unit, integration, E2E]

## 14. Deployment Strategy
[CI/CD, environments, rollback]

## 15. Dependency Graph
[Visual graph of dependencies]
```

---

### Paso 5: Task Breakdown

Crear `tasks/plan.md` con horizontal slicing:

```markdown
# [Project Name] — Implementation Plan

**Generated:** YYYY-MM-DD
**Based on:** SPEC.md

## Dependency Graph

```
PHASE A: Foundation (no dependencies)
  A1. Setup ─────────┐
  A2. Auth ──────────┤
                     │
PHASE B: Core Features (depends on A)
  B1. Feature X ──────┤
  B2. Feature Y ──────┘
                     │
PHASE C: Polish (depends on all)
  C1. Performance ────┘
```

## PHASE A — Foundation

### A1: Project Setup
**What:** Initialize project with tech stack
**Why:** Foundation for all development

**Files to create:**
- `package.json` with dependencies
- `tsconfig.json` with strict mode
- `.eslintrc.js` with rules
- `jest.config.js` for testing

**Acceptance Criteria:**
- [ ] TypeScript compiles without errors
- [ ] Linter runs without warnings
- [ ] Tests can run with `npm test`
- [ ] Git repo initialized with `.gitignore`

---

### A2: Authentication System
**What:** User auth with JWT
**Why:** Secure access control

**Files to create:**
- `src/auth/jwt.ts` — JWT generation/validation
- `src/auth/middleware.ts` — Auth middleware
- `src/auth/routes.ts` — Login/signup endpoints

**Acceptance Criteria:**
- [ ] User can signup with email/password
- [ ] User can login and receive JWT
- [ ] Protected routes validate JWT
- [ ] JWT expires after 24h
- [ ] 5 tests pass for auth logic

[... continue for all phases ...]
```

Crear `tasks/todo.md` con checklist detallado.

---

## Modo B: Proyecto Existente (`--existing`)

### Paso 1: Audit

Leer TODO el contexto del proyecto:

```python
# Read existing files
read_files = [
    "README.md",
    "CLAUDE.md",
    "tasks/plan.md",
    "tasks/todo.md",
    ".planning/ROADMAP.md",
    ".planning/task-progress.json",
]

# Use Serena for code analysis
from serena import get_symbols_overview, find_symbol

# Get git history
git_log = subprocess.run(["git", "log", "--oneline", "-20"], capture_output=True)
```

**Contexto recolectado:**
- ¿Qué se prometió? (specs originales)
- ¿Qué archivos existen?
- ¿Qué tests pasan/fail?
- ¿Qué commits recientes hay?

---

### Paso 2: Rediscovery (Brain #1 + #7)

```python
# Brain #1: What was promised?
mcp__notebooklm-mcp__notebook_query(
    notebook_id="BRAIN_01_PRODUCT_STRATEGY",
    query=f"""
Original Project Promise (from SPEC.md):
{spec_content}

Current State (from git log):
{recent_commits}

Questions:
1. What features were promised vs what's delivered?
2. What's the gap between MVP and current state?
3. What's blocking the MVP completion?
4. What are the critical bugs?
"""
)

# Brain #7: Quality assessment
mcp__notebooklm-mcp__notebook_query(
    notebook_id="BRAIN_07_GROWTH",
    query=f"""
Project Health:
- Test coverage: {coverage}%
- Tech debt indicators: {debt_metrics}
- Dependencies: {outdated_count} outdated

Questions:
1. Is this project on track for MVP?
2. What are the highest-impact gaps?
3. What's the risk assessment?
4. What should we prioritize next?
"""
)
```

---

### Paso 3: Health Check

```python
# Run tests
frontend_tests = subprocess.run(["pnpm", "test", "--", "--run"], capture_output=True)
backend_tests = subprocess.run(["uv", "run", "pytest"], capture_output=True)

# Check coverage
coverage = parse_coverage(frontend_tests.stdout, backend_tests.stdout)

# Check dependencies
outdated = subprocess.run(["pnpm", "outdated"], capture_output=True)

# Tech debt indicators
complexity = subprocess.run(["lizard", "src/"], capture_output=True)
```

**Crear `.planning/HEALTH-CHECK.md`:**
```markdown
# Project Health Check

**Date:** YYYY-MM-DD
**Branch:** master

## Test Coverage
- Frontend: XX% (YY/YY tests passing)
- Backend: XX% (ZZ/ZZ tests passing)

## Dependencies
- Outdated packages: N
- Security vulnerabilities: N
- Deprecated APIs: N

## Tech Debt
- Cyclomatic complexity: High/Medium/Low
- Code duplication: XX%
- TODO comments: N

## Git Status
- Uncommitted changes: N files
- Branches: N active
- Recent commits: Last X days
```

---

### Paso 4: Gap Analysis

**Crear `.planning/GAPS.md`:**
```markdown
# Gap Analysis

**Date:** YYYY-MM-DD

## Missing Features for MVP

| Feature | Status | Blocker | Priority |
|---------|--------|---------|----------|
| Feature X | Not started | Technical debt | High |
| Feature Y | Partial | Missing tests | Medium |
| Feature Z | Not started | None | Low |

## Known Bugs

| Bug | Impact | Status |
|-----|--------|--------|
| Bug #1 | Critical | Open |
| Bug #2 | Minor | Fixed |

## Tech Debt

| Item | Impact | Effort | Priority |
|------|--------|--------|----------|
| Refactor X | High | Medium | High |
| Update Y | Low | Low | Low |
```

---

### Paso 5: Re-plan

**Regenerar `SPEC.md`** (actualizado con estado actual)

**Regenerar `tasks/plan.md`** (SOLO LO QUE FALTA):
```markdown
# [Project Name] — Implementation Plan (UPDATED)

**Generated:** YYYY-MM-DD
**Based on:** Current state audit
**Mode:** Existing project re-plan

## What's Done ✅

- A1. Project Setup — Complete (commit abc123)
- A2. Auth System — Complete (commit def456)
- B1. Feature X — Partial (commit ghi789, missing tests)

## What's Missing 🔲

### C1: Complete Feature X (HIGH)
**What:** Add missing tests for Feature X
**Why:** Currently failing test coverage

**Files to modify:**
- `src/features/x.test.ts` — Add 3 tests

**Acceptance Criteria:**
- [ ] All tests pass for Feature X
- [ ] Coverage > 80% for Feature X

[... continue with ONLY missing tasks ...]
```

**Regenerar `tasks/todo.md`** (checklist actualizado)

---

## Integración con /mm:complete-task

Después de `/mm:discover`:

```bash
# El comando generó:
SPEC.md
tasks/plan.md
tasks/todo.md

# Ahora ejecutar:
/mm:complete-task A1  # Para primera tarea
```

---

## Brain Protocol

**Brain #1 (Product Strategy):**
- Clarificar ideas
- User personas
- MoSCoW prioritization
- Competitive analysis
- USP identification

**Brain #4 (Backend):**
- Architecture decisions
- Tech stack backend
- API design
- Data modeling
- Performance considerations

**Brain #5 (Frontend):**
- UI/UX considerations
- Component architecture
- State management
- Accessibility
- Responsive design

**Brain #7 (Growth/Data):**
- Quality validation
- Risk assessment
- Success criteria validation
- Impact analysis
- Prioritization

---

## Memoria Protocol

Después del discovery, guardar en memoria:

```python
mcp__plugin_engram_engram__mem_save(
    title=f"Discovery complete: {project_name}",
    type="decision",
    content=f"""
**What**: Completed {"new project" if mode == "new" else "existing project audit"} discovery

**Why**: User {"wanted to start" if mode == "new" else "wanted to audit"} {project_name}

**Where**: SPEC.md, tasks/plan.md, tasks/todo.md

**Decisions**:
- Tech stack: {stack}
- Architecture: {architecture}
- MVP scope: {mvp_features}
{"**Gaps identified**: " + str(gaps) if mode == "existing" else ""}
""",
    project="mastermind"
)
```

---

## Ejemplos de Uso

### Nuevo Proyecto

```bash
# Quick discovery
/mm:discover "SaaS de task management para equipos remotos"
# → SPEC.md + plan.md + todo.md in ~15 min

# Deep discovery
/mm:discover "E-commerce de café especial" --mode=deep
# → SPEC.md + plan.md + todo.md in ~60 min (more detailed)
```

### Proyecto Existente

```bash
# Full audit + re-plan
/mm:discover --existing
# → Analyzes everything, regenerates plan with gaps

# Health check only
/mm:discover --existing --health
# → Just .planning/HEALTH-CHECK.md

# Gap analysis only
/mm:discover --existing --gaps
# → Just .planning/GAPS.md

# Re-plan only
/mm:discover --existing --replan
# → Updates tasks/plan.md + tasks/todo.md with current gaps
```

---

## Referencias del Proyecto

- **Brain #1:** `.claude/agents/mm/brain-01-product-strategy/`
- **Brain #4:** `.claude/agents/mm/brain-04-backend/`
- **Brain #5:** `.claude/agents/mm/brain-05-frontend/`
- **Brain #7:** `.claude/agents/mm/brain-07-growth/`
- **Command:** `.claude/commands/mm/discover.md`
- **Handler:** `.claude/commands/mm/discover-handler.py`

---

**Remember:** This skill turns ideas into actionable plans (or audits existing projects) using expert knowledge from the 7 specialized brains. It's the first step before `/mm:complete-task`.
