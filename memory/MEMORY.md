# Memory - MasterMind Framework

## Recent Sessions

| Session | Date | Outcome |
|---------|------|---------|
| 2026-03-13-simplification-cascade | 2026-03-13 | Simplification Cascade insight + PRP-03-00 Task 1 complete |
| 2026-03-13-phase2-complete | 2026-03-13 | Phase 2 execution complete (4 plans, 75 tests, 4.65x speedup) |
| 2026-03-13-phase2-planned | 2026-03-13 | Phase 2 planning complete (4 plans, 3 waves) |
| 2026-03-13-v1.3.0-merge | 2026-03-13 | v1.3.0 merged to master, codebase mapped |
| 2026-03-13-v2.0-planning | 2026-03-13 | v2.0 roadmap initialized with 4 phases |

---

## NotebookLM Naming Standards

| Tipo | Formato |
|------|---------|
| Cerebro permanente | `[CEREBRO] {Nombre} - {Nicho}` |
| Audit de proyecto | `[AUDIT] {Proyecto} - {Nicho} - {YYYY-MM-DD}` |

**Ejemplos:**
- `[CEREBRO] Product Strategy - Software Development`
- `[AUDIT] ProSell SaaS - Software Development - 2026-03-05`

---

## Git Rules

### CRITICAL: NUNCA usar `--no-verify`
- **El usuario lo prohibió explícitamente**
- Si GGA hook tarda mucho, esperar a que termine
- Si hay problemas con el hook, investigar y solucionar - NO saltearlo
- Esto es una regla fija, sin excepciones

---

## Project Notes

- Nombre del repo: **mastermind-framework**
- URL: https://github.com/rap77/mastermind-framework
- Branch principal: `master`
- Stack: Python 3.14 (uv), Node.js (nvm), Claude Code

## Framework Status: v2.0 In Progress 🚀

**Latest commit:** 4e4ee3e (2026-03-13)
**Current phase:** PRP-03-00 Pure Function Architecture (Task 1/5 complete)

### v2.0 Roadmap Progress

| Phase | Status | Plans |
|-------|--------|-------|
| 01 - Type Safety Foundation | ✅ Complete | 3/3 |
| 02 - Parallel Execution Core | ✅ Complete | 4/4 |
| 03 - Web UI Platform | ⏳ In Progress | PRP-03-00 (1/5 tasks) |
| 04 - Production Hardening | ⏳ Pending | 0/3 |

**Overall:** 7/10 plans complete (71%)

### PRP-03-00: Pure Function Architecture

**Insight:** "If every brain is a PURE FUNCTION (input → output), we DON'T need shared state."

**Progress:**
- ✅ Task 1: Pure function interfaces (Brief, BrainInput, ProductStrategy, etc.) - 27 tests passing
- ⏳ Task 2: Brain Functions Module (pending)
- ⏳ Task 3: Stateless Coordinator (pending)
- ⏳ Task 4: API Key Auth (pending)
- ⏳ Task 5: Legacy Brain Wrapper (pending)

**Complexity Reduction:** 80% (40+ files → 8 files, ~3000 LOC → ~600 LOC)

**See:** `.planning/phases/03-web-ui-platform/03-SIMPLIFICATION-PLAN.md`

---

## v1.3.0 Release (Previous)

**Fecha release:** 2026-03-12
**Merge confirmado:** 2026-03-13
**Estado:** 🟢 Production Ready

### Nicho Marketing Digital (COMPLETE ✅)
| Cerebro | Fuentes | Estado |
|---------|---------|--------|
| M1-M16 | 162 | v1.3.0 ✅ |

### Nicho Software Development (COMPLETE ✅)
17 PRPs completados - Framework v1.1.0 estable

---

## Stack Tecnológico Estándar

**Core:**
- Python 3.14+ (última estable)
- uv (package manager, reemplaza pip/poetry)

**Dependencias Principales:**
- click>=8.1.0 (CLI framework)
- rich>=13.0.0 (terminal output)
- pydantic>=2.10.0 (validation)
- pyyaml>=6.0 (config files)
- gitpython>=3.1.0 (git operations)

**Nuevas en v2.0:**
- aiosqlite>=0.20 (async SQLite)
- pytest-asyncio>=0.24 (async tests)
- faker>=34.0 (test data)

**Dev Dependencies:**
- pytest>=9.0.0 (testing)
- ruff>=0.15.0 (linter + formatter)
- mypy>=1.14.0 (type checking)

---

## CLI Comandos (v1.1.0)

```bash
# Source Management
mm source {new,update,validate,status,list,export}

# Brain Status
mm brain {status,validate,package}

# Orchestration
mm orchestrate {run,go,continue-plan} --parallel  # NEW in v2.0
```

---

## Referencias a Memorias Detalladas

### Sesiones más recientes
- `SESSION-2026-03-13-simplification-cascade` - Simplification Cascade insight + PRP-03-00
- `CHECKPOINT-PRP-03-00-TASK1-COMPLETE` - Task 1 complete checkpoint
- `SESSION-2026-03-13-phase2-complete` - Phase 2 execution details

### Arquitectura v2.0
- `V2.0-ARCHITECTURE-DECISIONS` - Core technical decisions
- `PHASE3-DECISIONS-2026-03-13` - Web UI platform decisions

### Progreso v2.0
- `PROJECT-v1.3.0-RELEASE-COMPLETE` - Release v1.3.0 baseline
- `HANDOFF-2026-03-13-PHASE2-COMPLETE` - Phase 2 completion handoff

### Estándares
- `NOTEBOOK-NAMING` - Naming convention for notebooks
- `CONVENTIONS` - Code conventions
- `COMMANDS` - CLI commands reference
