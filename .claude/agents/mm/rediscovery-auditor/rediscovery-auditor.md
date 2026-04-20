# Rediscovery Auditor Agent

**Purpose:** Audit existing projects and regenerate SPEC.md, plan.md, todo.md with current state and gaps

**Input:** Project context (files, git history, code)

**Output:**
- `SPEC.md` — UPDATED (or created if missing)
- `tasks/plan.md` — REGENERATED (only what's missing)
- `tasks/todo.md` — REGENERATED
- `.planning/HEALTH-CHECK.md` — Health report (new)
- `.planning/GAPS.md` — Identified gaps (new)

---

## Protocol

### Step 1: Fingerprint Project Structure

```python
# Detect project structure and available stacks using agnostic core
import subprocess
from pathlib import Path
import sys

# Add rediscovery core to path
sys.path.insert(0, str(Path(__file__).parent))

from core.detector import ProjectDetector
from core.orchestrator import Orchestrator

# Step 1: Detect project fingerprint
detector = ProjectDetector(Path.cwd())
fingerprint = detector.detect()

# Fingerprint contains:
# - type: "monolito" or "monorepo"
# - stacks: ["python", "node", "rust", "go"]
# - structure: per-stack analysis (package manager, src/tests dirs)

print(f"Project Type: {fingerprint['type']}")
print(f"Stacks Detected: {', '.join(fingerprint['stacks'])}")
```

---

### Step 2: Execute Multi-Stack Analysis

```python
# Step 2: Execute all strategies based on fingerprint
orchestrator = Orchestrator(Path.cwd(), fingerprint)
health_results = orchestrator.execute_all()

# Results contain per-stack analysis:
# - tests: passing/failing/skipped counts
# - deps: outdated/vulnerable packages
# - code: files, lines_of_code, modules
# - coverage: percentage (if available)
# - status: "success", "error", or "skipped"

for stack_name, results in health_results.items():
    if results.get("status") == "success":
        print(f"{stack_name.title()}: Tests {results['tests']['passing']} passing")
    else:
        print(f"{stack_name.title()}: {results.get('reason', 'Failed')}")
```

---

### Step 3: Generate Health Report

```python
# Step 3: Generate markdown health report
health_report = orchestrator.format_health_report()

# Save to planning directory
health_path = Path(".planning/HEALTH-CHECK.md")
health_path.parent.mkdir(exist_ok=True)
health_path.write_text(health_report)

print(f"Health report saved to {health_path}")
```

---

### Step 4: Collect Context Files

```python
# Step 4: Read key project files (simplified)
context_files = {}

files_to_read = [
    "README.md",
    "CLAUDE.md",
    "SPEC.md",
    "tasks/plan.md",
    "tasks/todo.md",
]

for file_path in files_to_read:
    full_path = Path(file_path)
    if full_path.exists():
        with open(full_path, 'r') as f:
            context_files[file_path] = f.read()

# Get git history
git_log = subprocess.run(
    ["git", "log", "--oneline", "--pretty=format:%h %s", "-20"],
    capture_output=True,
    text=True
).stdout.strip()

git_info = {
    "log": git_log,
    "status": subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True
    ).stdout.strip()
}
```

---

### Step 5: Brain #1 + #7 Rediscovery

```python
# Step 5: Query brains with fingerprint + health context
brain1_query = f"""
Project Fingerprint: {fingerprint['type']}
Stacks Detected: {', '.join(fingerprint['stacks'])}

Health Check Results:
{health_report}

Original Promise (from SPEC.md):
{context_files.get('SPEC.md', 'No SPEC.md found')}

Original Plan (from tasks/plan.md):
{context_files.get('tasks/plan.md', 'No plan.md found')}

Current State (git log - last 20 commits):
{git_info['log']}

Please analyze:
1. What features were promised vs delivered?
2. What's the gap per stack detected?
3. What are the critical blockers?
4. What should we prioritize next?

Consider the health check results for each stack.
"""

brain1_result = mcp__notebooklm_mcp__notebook_query(
    notebook_id="f276ccb3-0bce-4069-8b55-eae8693dbe75",
    query=brain1_query,
    timeout=180
)

# Brain #7: Quality assessment with health context
brain7_query = f"""
Project Context:
{brain1_result[:3000]}

Health Check Summary:
{health_report[:2000]}

Git Status:
{git_info['status']}

Please assess:
1. Project trajectory based on health check
2. Highest-impact gaps (consider test failures per stack)
3. Technical debt level (low/medium/high)
4. Risk assessment (Low/Medium/High)
5. Recommended priority order

Provide specific stack-level recommendations if issues found.
"""

brain7_result = mcp__notebooklm_mcp__notebook_query(
    notebook_id="d8de74d6-7028-44ed-b4d5-784d6a9256e6",
    query=brain7_query,
    timeout=180
)
```

**Parse brain outputs:**
```python
rediscovery = {
    "fingerprint": fingerprint,
    "health": health_results,
    "promised": [...],
    "delivered": [...],
    "gaps": [...],
    "blockers": [...],
    "bugs": [...],
    "priority": brain7_result['recommendations']
}
```

---

### Step 4: Health Check

```python
# Run tests
frontend_test_result = subprocess.run(
    "cd apps/web && pnpm test -- --run",
    capture_output=True,
    text=True,
    shell=True
)

backend_test_result = subprocess.run(
    "cd apps/api && uv run pytest",
    capture_output=True,
    text=True,
    shell=True
)

# Parse test results
import re

def parse_tests(output):
    passing = re.search(r'(\d+)\s+passing', output)
    failing = re.search(r'(\d+)\s+failing', output)
    return {
        "passing": int(passing.group(1)) if passing else 0,
        "failing": int(failing.group(1)) if failing else 0,
        "total": (int(passing.group(1)) if passing else 0) +
                (int(failing.group(1)) if failing else 0)
    }

frontend_health = parse_tests(frontend_test_result.stdout)
backend_health = parse_tests(backend_test_result.stdout)

# Check dependencies
frontend_deps = subprocess.run(
    "pnpm outdated",
    capture_output=True,
    text=True,
    shell=True
)

backend_deps = subprocess.run(
    "uv pip list --outdated",
    capture_output=True,
    text=True,
    shell=True
)

# Calculate coverage (if available)
frontend_coverage = re.search(r'Coverage:\s+(\d+\.?\d*)%', frontend_test_result.stdout)
backend_coverage = re.search(r'Coverage:\s+(\d+\.?\d*)%', backend_test_result.stdout)

health = {
    "frontend": {
        "tests": frontend_health,
        "coverage": float(frontend_coverage.group(1)) if frontend_coverage else None,
        "outdated_deps": len([l for l in frontend_deps.stdout.split('\n') if l.strip()])
    },
    "backend": {
        "tests": backend_health,
        "coverage": float(backend_coverage.group(1)) if backend_coverage else None,
        "outdated_deps": len([l for l in backend_deps.stdout.split('\n') if l.strip()])
    },
    "git": {
        "uncommitted": len(context['git']['status'].split('\n')) if context['git']['status'] else 0,
        "recent_activity": len(context['git']['log'].split('\n'))
    }
}
```

---

### Step 5: Generate `.planning/HEALTH-CHECK.md`

```markdown
# Project Health Check

**Date:** YYYY-MM-DD
**Branch:** [branch name]
**Commit:** [commit hash]

---

## Test Coverage

### Frontend
- **Passing:** [X]/[Y] tests ([Z]%)
- **Coverage:** [N]% (if available)
- **Status:** ✅ Healthy / ⚠️ Needs Attention / ❌ Critical

### Backend
- **Passing:** [X]/[Y] tests ([Z]%)
- **Coverage:** [N]% (if available)
- **Status:** ✅ Healthy / ⚠️ Needs Attention / ❌ Critical

### Overall
- **Total Tests:** [X] passing, [Y] failing
- **Status:** ✅ All tests passing / ⚠️ Some tests failing / ❌ Many tests failing

---

## Dependencies

### Frontend
- **Outdated Packages:** [N]
- **Security Vulnerabilities:** [N] (if available)
- **Deprecated APIs:** [N]

### Backend
- **Outdated Packages:** [N]
- **Security Vulnerabilities:** [N] (if available)
- **Deprecated APIs:** [N]

---

## Tech Debt Indicators

### Code Quality
- **Cyclomatic Complexity:** [High/Medium/Low] (if available)
- **Code Duplication:** [N]%
- **TODO Comments:** [N]
- **FIXME Comments:** [N]

### Architecture
- **Circular Dependencies:** [N] detected
- **God Classes:** [N] detected
- **Long Methods:** [N] detected

---

## Git Health

### Commit Activity
- **Recent Commits (last 7 days):** [N]
- **Uncommitted Changes:** [N] files
- **Branches:** [N] active

### Commit Quality
- **Conventional Commits:** [Yes/No]
- **Commit Message Quality:** [Good/Fair/Poor]

---

## Overall Health Score

| Category | Score | Status |
|----------|-------|--------|
| Tests | [X]/10 | [emoji] |
| Dependencies | [X]/10 | [emoji] |
| Code Quality | [X]/10 | [emoji] |
| Git Hygiene | [X]/10 | [emoji] |
| **Total** | **[X]/40** | [emoji] |

**Overall Status:** ✅ Healthy / ⚠️ Needs Work / ❌ Critical

---

## Recommendations

1. [Recommendation 1] — [Priority: High/Medium/Low]
2. [Recommendation 2] — [Priority: High/Medium/Low]
3. [Recommendation 3] — [Priority: High/Medium/Low]

---

**Generated by MasterMind /mm:discover --existing --health**
```

---

### Step 6: Generate `.planning/GAPS.md`

```markdown
# Gap Analysis

**Date:** YYYY-MM-DD
**Mode:** Existing Project Audit

---

## Executive Summary

**Original Promise:** [Summary from SPEC.md]
**Current Delivery:** [Summary of what's done]
**Gap:** [What's missing]

**Risk Level:** Low / Medium / High
**Estimated Time to Close Gaps:** [X] weeks

---

## Missing Features for MVP

| Feature | Status | Blocker | Priority | Est. Time |
|---------|--------|---------|----------|-----------|
| [Feature 1] | Not started / Partial / Complete | [Yes/No] | High / Medium / Low | [X]h |
| [Feature 2] | ... | ... | ... | ... |
| [Feature 3] | ... | ... | ... | ... |

**Total Missing Features:** [N]

---

## Known Bugs

| Bug | Impact | Status | Est. Time |
|-----|--------|--------|-----------|
| [Bug 1] | Critical / High / Medium / Low | Open / In Progress / Fixed | [X]h |
| [Bug 2] | ... | ... | ... |
| [Bug 3] | ... | ... | ... |

**Total Known Bugs:** [N]

---

## Tech Debt

| Item | Impact | Effort | Priority | Est. Time |
|------|--------|--------|----------|-----------|
| [Debt 1] | High / Medium / Low | High / Medium / Low | High / Medium / Low | [X]h |
| [Debt 2] | ... | ... | ... | ... |
| [Debt 3] | ... | ... | ... | ... |

**Total Tech Debt Items:** [N]

---

## Test Coverage Gaps

| Module | Current | Target | Gap | Priority |
|--------|---------|--------|-----|----------|
| [Module 1] | [X]% | [Y]% | [Y-X]% | High / Medium / Low |
| [Module 2] | ... | ... | ... | ... |
| [Module 3] | ... | ... | ... | ... |

**Total Coverage Gap:** [N] percentage points

---

## Documentation Gaps

| Document | Status | Missing | Priority |
|----------|--------|---------|----------|
| README.md | Complete / Incomplete / Missing | [What's missing] | High / Medium / Low |
| CLAUDE.md | ... | ... | ... |
| API Docs | ... | ... | ... |
| CONTRIBUTING.md | ... | ... | ... |

---

## Infrastructure Gaps

| Item | Status | Missing | Priority |
|------|--------|---------|----------|
| CI/CD | Complete / Partial / Missing | [What's missing] | High / Medium / Low |
| Monitoring | ... | ... | ... |
| Error Tracking | ... | ... | ... |
| Deployment | ... | ... | ... |

---

## Priority Order for Closing Gaps

Based on Brain #7 analysis:

1. **[Gap 1]** — [Reason for priority] — [Est. Time]
2. **[Gap 2]** — [Reason for priority] — [Est. Time]
3. **[Gap 3]** — [Reason for priority] — [Est. Time]
4. **[Gap 4]** — [Reason for priority] — [Est. Time]
5. **[Gap 5]** — [Reason for priority] — [Est. Time]

---

## Recommendations

### Immediate (This Week)
- [Action 1] — [Reason]
- [Action 2] — [Reason]

### Short-term (This Month)
- [Action 3] — [Reason]
- [Action 4] — [Reason]

### Long-term (This Quarter)
- [Action 5] — [Reason]
- [Action 6] — [Reason]

---

**Generated by MasterMind /mm:discover --existing --gaps**
```

---

### Step 7: Regenerate SPEC.md

If SPEC.md exists, UPDATE it with current state. If not, CREATE it.

```markdown
# [Project Name] — Specification (UPDATED)

**Generated:** YYYY-MM-DD (Original: YYYY-MM-DD)
**Mode:** Existing Project Re-discovery
**Status:** [In Progress / Complete]

---

## What Changed Since Original Spec

### Completed Features ✅
1. [Feature 1] — Completed on [Date] (commit [hash])
2. [Feature 2] — Completed on [Date] (commit [hash])
3. [Feature 3] — Completed on [Date] (commit [hash])

### Partially Implemented ⚠️
1. [Feature 4] — [What's done] — [What's missing]
2. [Feature 5] — [What's done] — [What's missing]

### Not Started ❌
1. [Feature 6] — [Reason for delay]
2. [Feature 7] — [Reason for delay]

---

[Include original SPEC.md sections, updated with current state]

---

## Updated Success Criteria

### Criteria Status

| Criterion | Status | Notes |
|-----------|--------|-------|
| F1: [Criterion] | ✅ Complete / ⚠️ Partial / ❌ Not Started | [Notes] |
| F2: [Criterion] | ... | ... |
| [...]
| F10: [Criterion] | ... | ... |
| B1: [Criterion] | ... | ... |
| [...]
| X7: [Criterion] | ... | ... |
| I5: [Criterion] | ... | ... |

**Overall Progress:** [X]/27 criteria complete ([Y]%)

---

## Updated Timeline

**Original Target Ship Date:** [Date]
**Current Estimated Ship Date:** [Date]
**Delay:** [X] weeks

**Reason for Delay:**
- [Reason 1]
- [Reason 2]

---

## Updated Risk Assessment

**Current Risk Level:** Low / Medium / High

**Top Risks:**
1. [Risk 1] — [Mitigation]
2. [Risk 2] — [Mitigation]
3. [Risk 3] — [Mitigation]

---

**Next:** Review updated plan and execute `/mm:complete-task` for highest-priority gap
```

---

### Step 8: Regenerate tasks/plan.md (ONLY WHAT'S MISSING)

```markdown
# [Project Name] — Implementation Plan (UPDATED)

**Generated:** YYYY-MM-DD
**Based on:** Current state audit
**Mode:** Existing project re-plan

---

## What's Done ✅

### A1: Project Setup — Complete
**Completed:** [Date] (commit [hash])
- [ ] All acceptance criteria met

### A2: Authentication System — Complete
**Completed:** [Date] (commit [hash])
- [ ] All acceptance criteria met

### B1: [Feature 1] — Partial
**Started:** [Date] (commit [hash])
**Status:** [What's done]
**Missing:**
- [ ] [Missing piece 1]
- [ ] [Missing piece 2]

---

## What's Missing 🔲

### B1-Complete: Finish [Feature 1] (HIGH)

**What:** Complete the remaining parts of [Feature 1]

**Why:** This is blocking [Feature 2] and is critical for MVP

**Files to modify:**
- `path/to/file1.ts` — [What to add]
- `path/to/file2.ts` — [What to add]

**Acceptance Criteria:**
- [ ] [Missing piece 1] implemented
- [ ] [Missing piece 2] implemented
- [ ] Tests pass for all scenarios
- [ ] Documentation updated

**Estimated:** [X] hours
**Priority:** HIGH

---

### B2: [Feature 2] (HIGH)

[Continue with ONLY missing tasks...]

---

### C1: Performance Optimization (MEDIUM)

[Continue with tasks...]

---

## Summary

**Completed Tasks:** [N]
**Remaining Tasks:** [M]
**Estimated Time to Complete:** [X] hours
**Target Ship Date:** [Date]

**Critical Path:** [Task 1] → [Task 2] → [Task 3]

---

**Next:** Run `/mm:complete-task B1-Complete` to close highest-priority gap
```

---

### Step 9: Regenerate tasks/todo.md

```markdown
# [Project Name] — Task List (UPDATED)

**Generated:** YYYY-MM-DD
**Based on:** tasks/plan.md (current state)

## Status Legend
- [ ] Pending
- [~] In Progress
- [x] Complete

---

## COMPLETED ✅

### A1: Project Setup
- [x] Initialize Git repository
- [x] Create package.json with dependencies
- [x] Configure TypeScript
- [x] Configure ESLint
- [x] Configure Jest
- [x] Create .gitignore
- [x] Write README.md
- [x] Verify TypeScript compiles
- [x] Verify linter runs
- [x] Verify tests can run

### A2: Authentication System
- [x] Create src/auth/types.ts
- [x] Create src/auth/jwt.ts
- [x] Create src/auth/middleware.ts
- [x] Create src/auth/routes.ts
- [x] Implement password hashing
- [x] Write tests for JWT logic
- [x] Write tests for middleware
- [x] Write tests for routes
- [x] Verify all tests pass

### B1: [Feature 1] (PARTIAL)
- [x] [Completed subtask 1]
- [x] [Completed subtask 2]
- [ ] [Missing subtask 1]
- [ ] [Missing subtask 2]

---

## PENDING 🔲

### B1-Finish: Complete [Feature 1]
- [ ] Implement [missing piece 1]
- [ ] Implement [missing piece 2]
- [ ] Write tests for [missing piece 1]
- [ ] Write tests for [missing piece 2]
- [ ] Update documentation
- [ ] Verify all tests pass

### B2: [Feature 2]
- [ ] [Subtask 1]
- [ ] [Subtask 2]
- [ ] [...]
- [ ] [Subtask N]

[Continue with ONLY missing tasks...]

---

## Summary

**Total Tasks:** [N]
**Completed:** [X] ([Y]%)
**Remaining:** [Z] ([W]%)
**Estimated Time:** [H] hours

**Next:** `/mm:complete-task B1-Finish`
```

---

### Step 10: Validate and Save

```python
# Validate files were updated/created
files_to_check = [
    ("SPEC.md", "updated" if Path("SPEC.md").exists() else "created"),
    ("tasks/plan.md", "updated"),
    ("tasks/todo.md", "updated"),
    (".planning/HEALTH-CHECK.md", "created"),
    (".planning/GAPS.md", "created"),
]

for file_path, action in files_to_check:
    if not Path(file_path).exists():
        raise Exception(f"Failed to {action} {file_path}")

# Save to memory
mcp__plugin_engram_engram__mem_save(
    title=f"Rediscovery complete: {project_name} - {len(gaps)} gaps identified",
    type="decision",
    content=f"""
**What:** Completed existing project rediscovery for {project_name}

**Findings:**
- Features delivered: {len(delivered)}/{len(promised)}
- Missing features: {len(gaps)}
- Known bugs: {len(bugs)}
- Tech debt items: {len(debt)}

**Health:**
- Frontend tests: {health['frontend']['tests']['passing']} passing
- Backend tests: {health['backend']['tests']['passing']} passing
- Overall health: {health_score}/40

**Priority Order:**
1. {priority[1]}
2. {priority[2]}
3. {priority[3]}

**Files updated/created:**
- SPEC.md (updated with current state)
- tasks/plan.md (regenerated with only missing tasks)
- tasks/todo.md (regenerated checklist)
- .planning/HEALTH-CHECK.md (new)
- .planning/GAPS.md (new)

**Estimated time to MVP:** {estimated_weeks} weeks

**Next:** /mm:complete-task {first_task_id}
""",
    project="mastermind"
)
```

---

## Output Format

When complete, report:

```markdown
✅ Rediscovery Complete: [Project Name]

📊 Project Health:
- Frontend: [X]/[Y] tests passing ([Z]%)
- Backend: [X]/[Y] tests passing ([Z]%)
- Health Score: [X]/40
- Overall Status: ✅ Healthy / ⚠️ Needs Work / ❌ Critical

🔍 Gaps Identified:
- Missing features: [N]
- Known bugs: [N]
- Tech debt items: [N]
- Test coverage gaps: [N] percentage points

📋 Files Updated/Created:
- ✅ SPEC.md (updated with current state)
- ✅ tasks/plan.md (regenerated - only missing tasks)
- ✅ tasks/todo.md (regenerated checklist)
- ✅ .planning/HEALTH-CHECK.md (new)
- ✅ .planning/GAPS.md (new)

⏱️  Estimated to MVP: [X] weeks
🎯 Top Priority: [Task 1] — [Reason]

🚀 Next Step: /mm:complete-task [Task ID]
```

---

## Notes

- **Working Directory:** Project root
- **Brain Integration:** Uses NotebookLM MCP server
- **Code Analysis:** Uses Serena for symbol-level analysis
- **Memory Integration:** Uses Engram MCP server
- **Background Mode:** Agent runs in background to not block main session
- **Context Budget:** Save checkpoints every 2-3 steps
- **Git Integration:** Reads git log, status, diff for state analysis
