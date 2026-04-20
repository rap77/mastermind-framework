# Discover Planner Agent

**Purpose:** Analyze new project ideas and generate SPEC.md, plan.md, and todo.md

**Input:** User's raw idea (text)

**Output:**
- `SPEC.md` — Complete specification (15 sections)
- `tasks/plan.md` — Implementation plan with horizontal slicing
- `tasks/todo.md` — Detailed checklist
- `README.md` — Project overview
- `CLAUDE.md` — Instructions for Claude Code

---

## Protocol

### Step 1: Brain #1 Consultation (Product Strategy)

```python
mcp__notebooklm-mcp__notebook_query(
    notebook_id="f276ccb3-0bce-4069-8b55-eae8693dbe75",
    query=f"""
Project Idea: {user_idea}

Please analyze this idea and provide:

1. **Problem Statement**: What problem are we solving? Be specific.

2. **Target Users**: Who is this for? Define 2-3 user personas with:
   - Name and role
   - Pain points
   - Goals
   - Technical proficiency

3. **MoSCoW Prioritization** for MVP (must ship in 8 weeks):
   - **Must Have**: Core features without which it's not viable
   - **Should Have**: Important but not critical
   - **Could Have**: Nice to have if time permits
   - **Won't Have**: Explicitly out of scope for v1

4. **Competitive Analysis**: Top 3 competitors
   - What they do well
   - What they miss (opportunity for differentiation)
   - Our unique selling proposition (USP)

5. **Non-negotiables**:
   - Technical constraints (if any)
   - Business constraints (budget, timeline)
   - UX constraints (accessibility, mobile)

6. **Success Criteria**: What does "success" look like?
   - User engagement metrics
   - Technical metrics (performance, uptime)
   - Business metrics (conversion, retention)

Constraints:
- MVP must ship in < 8 weeks
- Be specific about user personas (avoid "everyone")
- Identify what makes this different from existing solutions
""",
    timeout=120
)
```

**Parse Brain #1 output into structured data:**
```python
brain1_output = {
    "problem": "...",
    "user_personas": [...],
    "moscow": {"must": [...], "should": [...], "could": [...], "wont": [...]},
    "competitors": [...],
    "usp": "...",
    "non_negotiables": [...],
    "success_criteria": {...}
}
```

---

### Step 2: Brain #4 + #5 Consultation (Backend + Frontend)

**Backend (Brain #4):**
```python
mcp__notebooklm-mcp__notebook_query(
    notebook_id="85e47142-0a65-41d9-9848-49b8b5d2db33",
    query=f"""
Project Context:
{brain1_output_summary}

Please recommend:

1. **Backend Architecture**: Monolith, microservices, or serverless?
   - Justification based on project needs

2. **Tech Stack**:
   - Language: Python, Node.js, Rust, Go?
   - Framework: FastAPI, Django, Express, Spring?
   - Database: PostgreSQL, MongoDB, MySQL?
   - ORM: SQLAlchemy, Prisma, TypeORM?

3. **Key API Endpoints** (REST or GraphQL):
   - Authentication (signup, login, logout)
   - Core resources (CRUD operations)
   - Business logic endpoints

4. **Data Model**:
   - Key entities (User, Resource, etc.)
   - Relationships (one-to-many, many-to-many)
   - Indexing strategy

5. **Non-negotiable Technical Constraints**:
   - Security requirements
   - Performance requirements (concurrent users, response time)
   - Scalability considerations
""",
    timeout=120
)
```

**Frontend (Brain #5):**
```python
mcp__notebooklm-mcp__notebook_query(
    notebook_id="c6befbbc-b7dd-4ad0-a677-314750684208",
    query=f"""
Project Context:
{brain1_output_summary}

Please recommend:

1. **Frontend Framework**: React, Vue, Next.js, Svelte?
   - Justification based on project needs

2. **State Management**: Redux, Zustand, Context, Pinia?
   - Complexity level of state needed

3. **Component Architecture**:
   - Atomic design or container/presentational?
   - Key component families needed

4. **Mobile Strategy**:
   - Responsive web only?
   - PWA?
   - Native app (React Native, Flutter)?

5. **UI/UX Considerations**:
   - Accessibility requirements (WCAG level?)
   - Design system (Material UI, Tailwind, custom?)
   - Key interaction patterns

6. **Performance Budget**:
   - Bundle size limits
   - Load time targets
""",
    timeout=120
)
```

**Parse into structured data:**
```python
tech_stack = {
    "backend": {
        "architecture": "...",
        "language": "...",
        "framework": "...",
        "database": "...",
        "orm": "..."
    },
    "frontend": {
        "framework": "...",
        "state_management": "...",
        "components": "...",
        "mobile": "...",
        "styling": "..."
    }
}
```

---

### Step 3: Generate SPEC.md

```markdown
# [Project Name] — Specification

**Generated:** YYYY-MM-DD
**Mode:** New Project Discovery
**Idea:** [Original user idea]

---

## 1. Problem Statement

[From Brain #1]

**Current Pain Points:**
- [Pain point 1]
- [Pain point 2]
- [Pain point 3]

**Why Now:** [Market timing, urgency]

---

## 2. Proposed Solution

[High-level solution description]

**Our Approach:** [How we solve it differently]

**Key Differentiators:**
1. [Differentiator 1]
2. [Differentiator 2]
3. [Differentiator 3]

---

## 3. Target Users

### Persona 1: [Name]
**Role:** [Job title]
**Pain Points:**
- [Pain 1]
- [Pain 2]

**Goals:**
- [Goal 1]
- [Goal 2]

**Technical Proficiency:** [Low/Medium/High]

### Persona 2: [Name]
[...]

---

## 4. Key Features

### Must Have (MVP)
1. [Feature 1] — [Description]
2. [Feature 2] — [Description]
3. [Feature 3] — [Description]

### Should Have (v1.1)
1. [Feature 4] — [Description]
2. [Feature 5] — [Description]

### Could Have (v1.2)
1. [Feature 6] — [Description]
2. [Feature 7] — [Description]

### Won't Have (Out of Scope)
1. [Feature 8] — [Reason]
2. [Feature 9] — [Reason]

---

## 5. Success Criteria

### Frontend Criteria (F1-F10)
- **F1**: [ ] [Specific frontend criterion]
- **F2**: [ ] [Specific frontend criterion]
- [...]
- **F10**: [ ] [Specific frontend criterion]

### Backend Criteria (B1-B6)
- **B1**: [ ] [Specific backend criterion]
- **B2**: [ ] [Specific backend criterion]
- [...]
- **B6**: [ ] [Specific backend criterion]

### Functional Criteria (X1-X7)
- **X1**: [ ] [Specific functional criterion]
- **X2**: [ ] [Specific functional criterion]
- [...]
- **X7**: [ ] [Specific functional criterion]

### Integration Criteria (I1-I5)
- **I1**: [ ] [Specific integration criterion]
- **I2**: [ ] [Specific integration criterion]
- [...]
- **I5**: [ ] [Specific integration criterion]

**Total: 27+ success criteria**

---

## 6. Architecture Overview

```
┌─────────────┐         ┌─────────────┐
│   Frontend  │◄────────┤   Backend   │
│  ([Framework])│  API   │ ([Framework])│
└─────────────┘         └──────┬──────┘
                              │
                       ┌──────▼──────┐
                       │  Database   │
                       │ ([DB Type]) │
                       └─────────────┘
```

**Architecture Pattern:** [Monolith/Microservices/Serverless]

**Key Design Decisions:**
1. [Decision 1] — [Rationale]
2. [Decision 2] — [Rationale]
3. [Decision 3] — [Rationale]

---

## 7. Tech Stack

### Frontend
- **Framework:** [Framework] [Version]
- **State Management:** [Library]
- **Styling:** [Approach]
- **Build Tool:** [Tool]
- **Testing:** [Framework] + [Library]

### Backend
- **Language:** [Language] [Version]
- **Framework:** [Framework] [Version]
- **Database:** [Database] [Version]
- **ORM:** [ORM] [Version]
- **Auth:** [Strategy]
- **Testing:** [Framework] + [Library]

### Infrastructure
- **Hosting:** [Provider]
- **CI/CD:** [Platform]
- **Monitoring:** [Tool]

---

## 8. Data Model

### Key Entities

**User**
- id: UUID (PK)
- email: String (unique)
- password_hash: String
- created_at: Timestamp
- updated_at: Timestamp

**[Entity 2]**
- [Field 1]: [Type]
- [Field 2]: [Type]
- [...]

### Relationships

```
User ──1:N──► [Entity 2]
[Entity 2] ──N:M──► [Entity 3]
```

### Indexes

- `users_email_idx` on `users(email)`
- `[index_2]` on `[table]([column])`
- [...]

---

## 9. API Endpoints

### Authentication
- `POST /api/auth/signup` — Create new user
- `POST /api/auth/login` — Login and receive JWT
- `POST /api/auth/logout` — Invalidate token
- `GET /api/auth/me` — Get current user

### [Resource 1]
- `GET /api/[resource]` — List all
- `GET /api/[resource]/:id` — Get one
- `POST /api/[resource]` — Create
- `PUT /api/[resource]/:id` — Update
- `DELETE /api/[resource]/:id` — Delete

### [Resource 2]
[...]

---

## 10. UI/UX Considerations

### Design Principles
1. [Principle 1] — [Description]
2. [Principle 2] — [Description]
3. [Principle 3] — [Description]

### Key Screens
1. **[Screen 1]** — [Purpose]
   - Key elements: [Element 1], [Element 2]
   - User flow: [Flow description]

2. **[Screen 2]** — [Purpose]
   - [...]

### Accessibility
- **WCAG Level:** [AA/AAA]
- **Keyboard Navigation:** [Yes/No + details]
- **Screen Reader Support:** [Yes/No + details]
- **Color Contrast:** [Ratio requirement]

---

## 11. Security Requirements

### Authentication
- **Strategy:** [JWT/Session/OAuth]
- **Password Requirements:** [Complexity rules]
- **2FA:** [Yes/No + implementation]

### Authorization
- **Role-Based Access Control:** [Yes/No]
- **Permissions Model:** [Description]

### Data Protection
- **Encryption at Rest:** [Yes/No + method]
- **Encryption in Transit:** [TLS version]
- **PII Handling:** [Compliance requirements]

### API Security
- **Rate Limiting:** [Strategy]
- **Input Validation:** [Approach]
- **SQL Injection Prevention:** [Method]
- **XSS Prevention:** [Method]

---

## 12. Performance Requirements

### Response Times
- **API p95:** [Target]ms
- **API p99:** [Target]ms
- **Page Load:** [Target]s
- **Time to Interactive:** [Target]s

### Scalability
- **Concurrent Users:** [Target]
- **Requests/Second:** [Target]
- **Database Size:** [Estimate]

### Optimization Strategy
- **Caching:** [Strategy]
- **CDN:** [Yes/No + provider]
- **Lazy Loading:** [Strategy]
- **Code Splitting:** [Strategy]

---

## 13. Testing Strategy

### Frontend Testing
- **Unit Tests:** [Framework] — [Target coverage]%
- **Component Tests:** [Framework] — [Target coverage]%
- **E2E Tests:** [Framework] — [Critical paths]

### Backend Testing
- **Unit Tests:** [Framework] — [Target coverage]%
- **Integration Tests:** [Framework] — [Target coverage]%
- **API Tests:** [Framework] — [All endpoints]

### Quality Gates
- **Pre-commit:** [Tools]
- **CI Pipeline:** [Stages]
- **Code Review:** [Required reviewers]

---

## 14. Deployment Strategy

### Environments
- **Development:** [Setup]
- **Staging:** [Setup]
- **Production:** [Setup]

### CI/CD Pipeline
```
[Trigger] → [Build] → [Test] → [Deploy]
```

### Release Strategy
- **Frequency:** [Weekly/Bi-weekly/Monthly]
- **Versioning:** [Semantic versioning]
- **Rollback:** [Strategy]

---

## 15. Dependency Graph

```
PHASE A: Foundation (no dependencies)
  A1. Project Setup ─────────┐
  A2. Auth System ───────────┤
                             │
PHASE B: Core Features (depends on A)
  B1. [Feature 1] ────────────┤
  B2. [Feature 2] ────────────┤
                             │
PHASE C: Polish (depends on all)
  C1. Performance ────────────┘
```

**Critical Path:** A1 → A2 → B1 → C1

---

**Next Steps:**
1. Review SPEC.md with stakeholders
2. Run `/mm:complete-task A1` to start implementation
3. Monitor progress with `/mm:complete-task --status`
```

---

### Step 4: Generate tasks/plan.md

```markdown
# [Project Name] — Implementation Plan

**Generated:** YYYY-MM-DD
**Based on:** SPEC.md

## Dependency Graph

```
PHASE A: Foundation (no dependencies)
  A1. Project Setup ─────────┐
  A2. Auth System ───────────┤
                             │
PHASE B: Core Features (depends on A)
  B1. [Feature 1] ────────────┤
  B2. [Feature 2] ────────────┤
                             │
PHASE C: Polish (depends on all)
  C1. Performance ────────────┘
```

**Critical Path:** A1 → A2 → B1 → C1

---

## PHASE A — Foundation

### A1: Project Setup

**What:** Initialize project with tech stack

**Why:** Foundation for all development

**Files to create:**
- `package.json` with dependencies
- `tsconfig.json` with strict mode
- `.eslintrc.js` with rules
- `jest.config.js` for testing
- `.gitignore` with appropriate exclusions
- `README.md` with project overview

**Acceptance Criteria:**
- [ ] TypeScript compiles without errors (`tsc --noEmit`)
- [ ] Linter runs without warnings (`eslint . --ext .ts,.tsx`)
- [ ] Tests can run with `npm test`
- [ ] Git repo initialized with proper `.gitignore`
- [ ] README.md includes setup instructions

**Estimated:** 2 hours

---

### A2: Authentication System

**What:** User authentication with JWT

**Why:** Secure access control for all features

**Files to create:**
- `src/auth/jwt.ts` — JWT generation/validation
- `src/auth/middleware.ts` — Auth middleware for protected routes
- `src/auth/routes.ts` — Login/signup endpoints
- `src/auth/types.ts` — TypeScript interfaces

**Acceptance Criteria:**
- [ ] User can signup with email/password
- [ ] User can login and receive JWT
- [ ] Protected routes validate JWT
- [ ] JWT expires after 24h
- [ ] 5 tests pass for auth logic
- [ ] Passwords are hashed (bcrypt, cost=10)

**Estimated:** 4 hours

---

## PHASE B — Core Features

[Continue with B1, B2, etc. based on Must Have features from Brain #1]

---

## PHASE C — Polish

[Continue with C1, C2, etc. for performance, monitoring, etc.]

---

**Total Estimated Time:** [X] hours
**Target MVP Ship Date:** [Date + 8 weeks from start]

**Next:** Run `/mm:complete-task A1` to start implementation
```

---

### Step 5: Generate tasks/todo.md

```markdown
# [Project Name] — Task List

**Generated:** YYYY-MM-DD
**Based on:** tasks/plan.md

## Status Legend
- [ ] Pending
- [~] In Progress
- [x] Complete

---

## PHASE A — Foundation

### A1: Project Setup
- [ ] Initialize Git repository
- [ ] Create package.json with dependencies
- [ ] Configure TypeScript (tsconfig.json)
- [ ] Configure ESLint (.eslintrc.js)
- [ ] Configure Jest (jest.config.js)
- [ ] Create .gitignore
- [ ] Write README.md with setup instructions
- [ ] Verify TypeScript compiles
- [ ] Verify linter runs
- [ ] Verify tests can run

### A2: Authentication System
- [ ] Create src/auth/types.ts
- [ ] Create src/auth/jwt.ts (generate, validate, expire)
- [ ] Create src/auth/middleware.ts (verify token)
- [ ] Create src/auth/routes.ts (signup, login, logout)
- [ ] Implement password hashing (bcrypt)
- [ ] Write 5 tests for JWT logic
- [ ] Write 3 tests for middleware
- [ ] Write 2 tests for routes
- [ ] Verify all tests pass

[Continue with B1, B2, C1, etc.]

---

**Total Tasks:** [N]
**Estimated Hours:** [X]
**Target Ship Date:** [Date]
```

---

### Step 6: Generate README.md

```markdown
# [Project Name]

[One-line description]

## Overview

[2-3 sentence description of what this project does and for whom]

## Features

- [Feature 1] — [Description]
- [Feature 2] — [Description]
- [Feature 3] — [Description]

## Tech Stack

**Frontend:**
- [Framework] [Version]
- [State Management]
- [Styling]

**Backend:**
- [Language] [Version]
- [Framework] [Version]
- [Database] [Version]

## Getting Started

### Prerequisites

- [Node.js] >= [Version]
- [Database] >= [Version]

### Installation

```bash
# Clone the repo
git clone [repo-url]
cd [project-name]

# Install dependencies
npm install

# Setup environment
cp .env.example .env
# Edit .env with your values

# Run database migrations
npm run db:migrate

# Start development server
npm run dev
```

## Development

```bash
# Run tests
npm test

# Run linter
npm run lint

# Build for production
npm run build

# Start production server
npm start
```

## Project Structure

```
.
├── src/
│   ├── auth/          # Authentication logic
│   ├── components/    # React components
│   ├── pages/         # Page components
│   ├── api/           # API routes
│   └── lib/           # Utilities
├── tests/             # Test files
└── docs/              # Documentation
```

## Contributing

[Contributing guidelines]

## License

[License]

---

**Generated by MasterMind /mm:discover**
```

---

### Step 7: Generate CLAUDE.md

```markdown
# CLAUDE.md

This file provides guidance to Claude Code when working on [Project Name].

## Project Overview

[One-line description]

**Tech Stack:**
- Frontend: [Framework]
- Backend: [Language] + [Framework]
- Database: [Database]
- Testing: [Test Framework]

## Development Commands

```bash
# Install dependencies
npm install

# Run tests
npm test

# Run linter
npm run lint

# Build for production
npm run build

# Start development server
npm run dev
```

## Architecture

[High-level architecture description]

## Key Files

- `src/auth/` — Authentication logic
- `src/api/` — API routes
- `src/components/` — React components
- `tests/` — Test files

## Conventions

- **Code Style:** [Style guide]
- **Commit Convention:** [Conventional commits]
- **Branch Strategy:** [Git flow / trunk-based]

## Testing

- **Target Coverage:** [X]%
- **Test Framework:** [Framework]
- **All tests must pass** before committing

## Package Manager

- **Node.js:** Use `npm` (not `yarn` or `pnpm`)

## Language

All code comments and documentation in **English**.
Variable names in **English**.
Commit messages in **English**.

---

**Generated by MasterMind /mm:discover**
```

---

### Step 8: Validate and Save

```python
# Validate files exist
files_to_validate = [
    "SPEC.md",
    "tasks/plan.md",
    "tasks/todo.md",
    "README.md",
    "CLAUDE.md"
]

for file in files_to_validate:
    if not Path(file).exists():
        raise Exception(f"Failed to create {file}")

# Save to memory
mcp__plugin_engram_engram__mem_save(
    title=f"Discovery complete: {project_name}",
    type="decision",
    content=f"""
**What**: Completed new project discovery for {project_name}

**Idea:** {user_idea}

**Decisions:**
- Tech stack: {tech_stack}
- Architecture: {architecture}
- MVP scope: {mvp_features}
- Estimated time: {estimated_hours}h
- Target ship date: {ship_date}

**Files generated:**
- SPEC.md (15 sections, 27+ success criteria)
- tasks/plan.md ({n_tasks} tasks across {n_phases} phases)
- tasks/todo.md (detailed checklist)
- README.md (project overview)
- CLAUDE.md (instructions for Claude Code)

**Next:** /mm:complete-task A1 to start implementation
""",
    project="mastermind"
)
```

---

## Output Format

When complete, report:

```markdown
✅ Discovery Complete: [Project Name]

📋 Files Generated:
- SPEC.md (15 sections, 27+ criteria)
- tasks/plan.md ([N] tasks, [M] phases)
- tasks/todo.md ([X] checklist items)
- README.md
- CLAUDE.md

🎯 Tech Stack:
- Frontend: [Framework] + [State]
- Backend: [Language] + [Framework]
- Database: [Database]

⏱️  Estimated: [X] hours
📅 Target Ship: [Date]

🚀 Next Step: /mm:complete-task A1
```

---

## Notes

- **Working Directory:** `/home/rpadron/proy/mastermind` (or project root)
- **Brain Integration:** Uses NotebookLM MCP server
- **Memory Integration:** Uses Engram MCP server
- **Background Mode:** Agent runs in background to not block main session
- **Context Budget:** Save checkpoints every 2-3 steps
