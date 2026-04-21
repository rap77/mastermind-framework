---
name: mm:discover
description: Analyze ideas or audit existing projects to generate SPEC.md, plan.md, and todo.md ready for /mm:complete-task
argument-hint: "\"<idea>\" | --existing [--mode=fast|deep] [--health] [--gaps] [--replan]"
---

# /mm:discover

Discover and plan: from raw idea to actionable tasks (or audit existing projects).

## Usage

```bash
# Mode A: New Project (idea → plan)
/mm:discover "Quiero un SaaS de gestión de tareas para equipos remotos"
/mm:discover "E-commerce de café especial con suscripciones" --mode=deep
/mm:discover "App de meditation con sonidos binaurales" --mode=fast

# Mode B: Existing Project (audit → re-plan)
/mm:discover --existing
/mm:discover --existing --health       # Health check only
/mm:discover --existing --gaps         # Gap analysis only
/mm:discover --existing --replan      # Re-plan with current gaps
```

## What It Does

### Mode A: New Project (default)

**Input:** Raw idea (text)

**Process:**
1. **Brain #1 (Product Strategy):** Clarify the idea
   - What problem do we solve?
   - For whom? (User Personas)
   - MVP vs v1? (MoSCoW)
   - Non-negotiables?

2. **Exploration (Brain #4 + #5):** Research
   - Competitive analysis (3 competitors)
   - Tech stack recommendation
   - Technical non-negotiables

3. **Architecture:** Modular design
   - Frontend (Next.js? Vue?)
   - Backend (FastAPI? Django?)
   - Database (PostgreSQL? MongoDB?)
   - Auth (Supabase? Auth0?)

4. **Spec Generation:** Create `SPEC.md`
   - 15 sections (Problem, Solution, Architecture, etc.)
   - 27+ success criteria
   - Dependency graph

5. **Task Breakdown:** Create `tasks/plan.md` + `tasks/todo.md`
   - Horizontal slicing (Phase A, B, C, D...)
   - Each task = complete deliverable

**Output:**
- `SPEC.md` — Complete specification
- `tasks/plan.md` — Implementation plan
- `tasks/todo.md` — Detailed checklist
- `README.md` — Project overview
- `CLAUDE.md` — Instructions for Claude Code

→ Ready for `/mm:complete-task`

---

### Mode B: Existing Project (`--existing`)

**Process:**
1. **Audit:** Read all context
   - `README.md`, `CLAUDE.md`
   - `tasks/plan.md`, `tasks/todo.md`
   - `.planning/` (ROADMAP, etc.)
   - Code (via Serena)
   - Git history

2. **Rediscovery:** Brain #1 + #7 analyze
   - What was promised? (original specs)
   - What is done? (git log, tests)
   - **What is missing?** (gaps detected)

3. **Health Check:**
   - Test coverage (%)
   - Tech debt (cyclomatic complexity)
   - Dependencies (security outdated)

4. **Gap Analysis:**
   - Missing features for MVP
   - Known bugs (GitHub issues?)
   - Pending tech debt

5. **Re-plan:**
   - Update `tasks/plan.md` (ONLY WHAT'S MISSING)
   - Update `tasks/todo.md`
   - Prioritization (MoSCoW)
   - Estimates (optimistic/realistic/pessimistic)

**Output:**
- `SPEC.md` — UPDATED (or created if missing)
- `tasks/plan.md` — REGENERATED (only gaps)
- `tasks/todo.md` — REGENERATED
- `.planning/HEALTH-CHECK.md` — Health report (new)
- `.planning/GAPS.md` — Identified gaps (new)

→ Ready for `/mm:complete-task`

---

## Protocol (For Assistant)

When user executes `/mm:discover [options]`:

### Step 1: Execute Python Handler

```bash
python3 .claude/commands/mm/discover-handler.py [options]
```

Run from `/home/rpadron/proy/mastermind`

### Step 2: Parse Handler Output

Capture stdout and look for:
- `MODE: new|existing` → Which mode to run
- `TASK: agent-type` → Which agent to launch
- `PAYLOAD: {...}` → JSON payload for agent
- `ERROR: ...` → Handler error, show to user

### Step 3: Launch Agent (if payload present)

```
Agent(
  subagent_type="{agent_type_from_payload}",
  prompt=f"""
## Discovery Payload
{parsed_payload_json}

Working directory: /home/rpadron/proy/mastermind

Execute the discovery process following the agent protocol.
""",
  run_in_background=true
)
```

### Step 4: Notify User

```
✅ Discovery agent launched in background
📊 Results will be saved to: SPEC.md, tasks/plan.md, tasks/todo.md
🔔 You'll be notified when complete
```

---

## Flags

| Flag | Description |
|------|-------------|
| `--existing` | Audit existing project instead of new idea |
| `--mode=fast` | Quick discovery (15 min) |
| `--mode=deep` | Deep analysis (60 min) |
| `--health` | Health check only (existing mode) |
| `--gaps` | Gap analysis only (existing mode) |
| `--replan` | Re-plan with current gaps (existing mode) |

---

## Examples

### New Project

```bash
# Quick discovery
/mm:discover "SaaS de task management para equipos remotos"
# → SPEC.md + plan.md + todo.md in ~15 min

# Deep discovery
/mm:discover "E-commerce de café especial" --mode=deep
# → SPEC.md + plan.md + todo.md in ~60 min (more detailed)
```

### Existing Project

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

## Architecture

```
/mm:discover "idea..." o --existing
    ↓
Python Handler (discover-handler.py)
    ↓
Lee contexto (si --existing)
    ↓
Ejecuta Brains en paralelo:
  - Brain #1: Clarification/Rediscovery
  - Brain #4: Backend analysis
  - Brain #5: Frontend analysis
  - Brain #7: Validation
    ↓
Genera SPEC.md + plan.md + todo.md
    ↓
Listo para /mm:complete-task
```

---

## Files

- `.claude/commands/mm/discover-handler.py` — Python handler
- `.claude/agents/mm/discover-planner/discover-planner.md` — New project agent
- `.claude/agents/mm/rediscovery-auditor/rediscovery-auditor.md` — Existing project agent
- `.claude/skills/mm/discover/SKILL.md` — Reactive skill
- `SPEC.md` — Generated specification
- `tasks/plan.md` — Generated plan
- `tasks/todo.md` — Generated checklist

---

## Integration with agent-skills

**Complete flow:**

```
/mm:discover (nuevo)
    ↓
SPEC.md + plan.md + todo.md
    ↓
/mm:complete-task (existente)
    ↓
/build → /test → /review → /ship
```

---

## Brain Integration

**Brain #1 (Product Strategy):**
- What problem are we solving?
- For whom? (User Personas)
- MVP vs v1? (MoSCoW)
- Non-negotiables?

**Brain #4 (Backend):**
- Backend tech stack
- API design
- Database choice

**Brain #5 (Frontend):**
- Frontend tech stack
- UI/UX considerations
- Component architecture

**Brain #7 (Growth/Data):**
- Validation of plan
- Success criteria quality
- Risk assessment
