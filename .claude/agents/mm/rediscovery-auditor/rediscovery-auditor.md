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

### Step 1: Audit Context Collection

```python
# Read all project files
import subprocess
from pathlib import Path

# Files to read
context_files = {
    "README.md": None,
    "CLAUDE.md": None,
    "tasks/plan.md": None,
    "tasks/todo.md": None,
    "SPEC.md": None,
}

# Read existing files
for file_path in context_files:
    full_path = Path(file_path)
    if full_path.exists():
        with open(full_path, 'r') as f:
            context_files[file_path] = f.read()

# Read .planning directory
planning_dir = Path(".planning")
planning_files = {}
if planning_dir.exists():
    for file_path in planning_dir.glob("**/*.md"):
        with open(file_path, 'r') as f:
            planning_files[str(file_path)] = f.read()

# Get git history
git_log = subprocess.run(
    ["git", "log", "--oneline", "--pretty=format:%h %s", "-20"],
    capture_output=True,
    text=True
).stdout.strip()

git_status = subprocess.run(
    ["git", "status", "--porcelain"],
    capture_output=True,
    text=True
).stdout.strip()

# Get recent commits (detailed)
git_diff = subprocess.run(
    ["git", "diff", "--stat", "HEAD~5..HEAD"],
    capture_output=True,
    text=True
).stdout.strip()

context = {
    "files": context_files,
    "planning": planning_files,
    "git": {
        "log": git_log,
        "status": git_status,
        "diff": git_diff
    }
}
```

---

### Step 2: Code Analysis (using rg + fd)

```python
# Use ripgrep and fd for code analysis (no heavy Serena dependency)
code_files = {}
code_stats = {}

# Frontend analysis (TypeScript/TSX files)
frontend_dirs = ["apps/web/src", "apps/web/app"]
for dir_path in frontend_dirs:
    if Path(dir_path).exists():
        result = subprocess.run(
            ["fd", "-e", "ts", "-e", "tsx", ".", dir_path],
            capture_output=True,
            text=True
        )
        for line in result.stdout.strip().split('\n'):
            if line:
                file_path = Path(line)
                code_files[str(file_path)] = "frontend"

# Backend analysis (Python files)
backend_dirs = ["apps/api/src", "apps/api/app"]
for dir_path in backend_dirs:
    if Path(dir_path).exists():
        result = subprocess.run(
            ["fd", "-e", "py", ".", dir_path],
            capture_output=True,
            text=True
        )
        for line in result.stdout.strip().split('\n'):
            if line:
                file_path = Path(line)
                code_files[str(file_path)] = "backend"

# Count lines of code per module
for file_path in code_files.keys():
    result = subprocess.run(
        ["wc", "-l", file_path],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        lines = int(result.stdout.strip().split()[0])
        code_stats[file_path] = lines
```

---

### Step 3: Brain #1 + #7 Rediscovery

```python
# Brain #1: What was promised vs what's done?
brain1_query = f"""
Original Project Promise (from SPEC.md if exists):
{context['files'].get('SPEC.md', 'No SPEC.md found')}

Original Plan (from tasks/plan.md if exists):
{context['files'].get('tasks/plan.md', 'No plan.md found')}

Current State (from git log - last 20 commits):
{context['git']['log']}

Current Code Structure (from Serena analysis):
{str(code_analysis)[:5000]}  # First 5000 chars

Please analyze:
1. What features were promised in the original spec?
2. What features are actually implemented (from git log)?
3. What's the gap between promised and delivered?
4. What's blocking the completion of remaining features?
5. What are the critical bugs or issues?
6. What should we prioritize next?

Focus on:
- Features promised but not started
- Features partially implemented (what's missing?)
- Tests that are failing or missing
- Documentation that's outdated
"""

brain1_result = mcp__notebooklm_mcp__notebook_query(
    notebook_id="f276ccb3-0bce-4069-8b55-eae8693dbe75",
    query=brain1_query,
    timeout=180
)

# Brain #7: Quality and risk assessment
brain7_query = f"""
Project Context:
{brain1_result[:3000]}

Current Health Indicators:
- Git status: {context['git']['status']}
- Recent commits: {context['git']['log']}

Please assess:
1. Is this project on track for its stated goals?
2. What are the highest-impact gaps (features that block MVP)?
3. What's the technical debt level (low/medium/high)?
4. What's the risk assessment if we continue as-is?
5. What should we prioritize to reach a stable MVP?

Provide:
- Risk level (Low/Medium/High)
- Top 3 blockers for MVP
- Recommended priority order
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
    "promised": [...],  # Features from original spec
    "delivered": [...],  # Features actually done
    "gaps": [...],  # Missing features
    "blockers": [...],  # What's blocking progress
    "bugs": [...],  # Known issues
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
