# Rediscovery Auditor Agnóstico — Implementation Progress

**Started:** 2026-04-20
**Status:** IN PROGRESS (2/10 tasks complete)
**Approach:** Enfoque C - Híbrido Inteligente

## Design Spec

📄 `docs/superpowers/specs/2026-04-20-rediscovery-agnostic-design.md`

## Implementation Plan

📄 `docs/superpowers/plans/2026-04-20-rediscovery-agnostic.md`

## Completed Tasks

### ✅ Task 2: Create Core Module Structure
- **File:** `.claude/agents/mm/rediscovery-auditor/core/__init__.py`
- **Content:** Module docstring + `__version__ = "2.0.0"`
- **Commit:** `feat(rediscovery): create core module structure`

### ✅ Task 5: Implement Fingerprint Detector
- **Files:**
  - `core/detector.py` (263 lines) - ProjectDetector class
  - `core/tests/test_detector.py` (135 lines) - 9 tests
  - `core/tests/__init__.py`
  - `pyproject.toml` (for testing)
- **Tests:** 9/9 passing
- **Features:**
  - Detects Python, Node, Rust, Go stacks
  - Classifies monolito vs monorepo
  - Package manager detection (uv/pip/pnpm/yarn/npm/cargo)
  - Tool availability checking with timeout
- **Commit:** `e73cd2fd feat(rediscovery): implement fingerprint detector`

## Remaining Tasks (8 of 10)

### ⏳ Task 4: Base Strategy Interface
**Priority:** HIGH - Required by all strategies
- Create `core/strategies/__init__.py`
- Create `core/strategies/base.py` with ProjectStrategy ABC
- Methods: `validate()`, `run_tests()`, `analyze_deps()`, `analyze_code()`, `get_coverage()`
- Commit: `feat(rediscovery): add base strategy interface`

### ⏳ Task 1: Python Strategy
**Priority:** HIGH - Core functionality for this project
- Create `core/strategies/python.py`
- Validate uv/pip, run pytest, analyze deps, code, coverage
- Create `core/tests/test_python_strategy.py`
- Commit: `feat(rediscovery): implement Python strategy`

### ⏳ Task 6: Node Strategy
**Priority:** MEDIUM - For projects with Node.js
- Create `core/strategies/node.py`
- Validate pnpm/npm/yarn, run tests, analyze deps, code
- Commit: `feat(rediscovery): implement Node strategy`

### ⏳ Task 3: Rust Strategy
**Priority:** MEDIUM - For projects with Rust (rust_control_plane)
- Create `core/strategies/rust.py`
- Validate cargo, run cargo test, analyze deps, code
- Commit: `feat(rediscovery): implement Rust strategy`

### ⏳ Task 10: Orchestrator
**Priority:** HIGH - Coordinates all strategies
- Create `core/orchestrator.py`
- STRATEGY_MAP, load strategies, execute_all(), format_health_report()
- Commit: `feat(rediscovery): implement orchestrator`

### ⏳ Task 9: Update Agent Protocol
**Priority:** HIGH - Integrates new core into existing agent
- Modify `rediscovery-auditor.md`
- Replace hardcoded analysis with detector + orchestrator
- Commit: `feat(rediscovery): update agent protocol with agnostic core`

### ⏳ Task 7: Integration Tests
**Priority:** HIGH - Validates end-to-end flow
- Create `core/tests/test_integration.py`
- Test full flow: detector → orchestrator → health report
- Commit: `test(rediscovery): add integration tests`

### ⏳ Task 8: Verify Against Current Project
**Priority:** HIGH - Ensures it works on the actual project
- Test detector on `/home/rpadron/proy/mastermind`
- Expected: type=monolito, stacks=[python]
- Test orchestrator → health report generation
- Commit: `test(rediscovery): verify against current monolito project`

## How to Continue

### Option A: Single Agent in Background (Recommended)
```bash
# In a clean session, dispatch one agent to complete ALL remaining tasks
Agent(
  subagent_type="general-purpose",
  prompt="""
Implement the remaining 8 tasks for the rediscovery auditor agnostic project.

Plan: docs/superpowers/plans/2026-04-20-rediscovery-agnostic.md
Progress: .planning/REDISCOVERY-PROGRESS.md

Work through tasks 4,1,6,3,10,9,7,8 in order.
Follow TDD, commit each task separately.
Run: `cd .claude/agents/mm/rediscovery-auditor && uv run pytest core/tests/ -v` after each task.
""",
  run_in_background=true
)
```

### Option B: Continue Task-by-Task
```bash
# Use superpowers:subagent-driven-development skill
# Dispatch one agent per task with spec + code quality review
```

### Option C: Manual Implementation
```bash
# Follow the plan step by step
cd /claude/agents/mm/rediscovery-auditor
# Read: docs/superpowers/plans/2026-04-20-rediscovery-agnostic.md
# Implement each task following TDD
```

## Success Criteria

- [x] Detector identifies monolito Python
- [ ] Detector would identify monorepo (test needed)
- [ ] Python strategy runs tests (uv run pytest)
- [ ] Node strategy detects package manager
- [ ] Rust strategy runs cargo test
- [ ] Orchestrator merges results → HEALTH-CHECK.md
- [ ] Graceful degradation (missing tools = "skipped")
- [ ] Brain #1 receives fingerprint in context
- [ ] No hardcoded paths

## Notes

- Working directory for implementation: `.claude/agents/mm/rediscovery-auditor/`
- Tests run with: `uv run pytest core/tests/ -v`
- All commits use conventional commits format
- Follow TDD: test first, implementation, verify pass, commit
