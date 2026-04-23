---
name: mm:review
description: Generate code review payload for changes detection and delegate to code-reviewer agent
argument-hint: "[--staged] [--branch <name>] [--files <paths>] [--last-commit]"
---

# /mm:review

Code review: generate structured diff payload and delegate to code-reviewer agent for 5-axis analysis.

## Usage

```bash
# Mode 1: Uncommitted changes (default)
/mm:review

# Mode 2: Staged changes
/mm:review --staged

# Mode 3: Branch comparison
/mm:review --branch main
/mm:review --branch develop

# Mode 4: Specific files
/mm:review --files apps/web/src/components/Button.tsx
/mm:review --files apps/api/routes/tasks.py .claude/commands/mm/init-handler.py

# Mode 5: Last commit
/mm:review --last-commit
```

## What It Does

### Input

**Git diff** (or file content) from multiple modes:
- Uncommitted changes: `git diff`
- Staged changes: `git diff --staged`
- Branch diff: `git diff <branch>...HEAD`
- Direct files: read file contents
- Last commit: `git diff HEAD~1..HEAD`

### Process

1. **Handler Execution:**
   ```bash
   python3 .claude/commands/mm/review-handler.py [options]
   ```

2. **Diff Generation:**
   - Extract changed files
   - Detect programming languages (25+ extensions)
   - Truncate to 500 lines (configurable via `--max-lines`)
   - Generate structured output

3. **Code-Reviewer Delegation:**
   ```
   Agent(subagent_type="code-reviewer")
   ```

4. **5-Axis Analysis:**
   - **Correctness** — Bugs, logic errors, edge cases
   - **Readability** — Code clarity, naming, structure
   - **Architecture** — Patterns, design, maintainability
   - **Security** — Vulnerabilities, input validation
   - **Performance** — Efficiency, resource usage

### Output

**Structured Payload:**
```
MODE: review
SCOPE: uncommitted|staged|branch|files|last-commit
FILES: 3 changed files
LINES: 247 total (truncated from 312)
LANGUAGES: TypeScript, Python, Rust
LAUNCH: code-reviewer
PAYLOAD: {...json...}
```

**Report Format:**
```
.planning/REVIEWS/<timestamp>-review.md
```

Sections:
- **Summary** — Overall verdict (APPROVE/NEEDS WORK/REJECT)
- **Critical Issues** — Must fix before merge
- **Important Issues** — Should fix
- **Suggestions** — Nice to have
- **What's Done Well** — Positive feedback

## Brain Integration

### Brain #6 (QA/DevOps)

**Role:** Testing strategy and quality standards

**Consults on:**
- Test coverage assessment
- QA standards verification
- Edge case identification
- Testing strategy review

**Example:**
```python
# Brain #6 validates:
- Are there tests for this change?
- Do tests cover edge cases?
- Is the testing strategy appropriate?
```

### Brain #7 (Growth/Data)

**Role:** Systems thinking and impact analysis

**Consults on:**
- Cross-component impact
- Performance implications
- User experience impact
- Systems thinking evaluation

**Example:**
```python
# Brain #7 evaluates:
- How does this change affect other components?
- What are the performance implications?
- Are there second-order effects?
```

## Architecture

```
/mm:review
    ↓
review-handler.py (Python script)
    ↓
Generates diff payload:
    - MODE, SCOPE, FILES, LINES
    - LANGUAGES detected
    - Structured PAYLOAD
    ↓
Code-Reviewer Agent (5-axis analysis)
    ↓
Brain #6 + Brain #7 consultation
    ↓
Report: .planning/REVIEWS/<timestamp>-review.md
    ↓
Critical/Important/Suggestions sections
```

## Report Format

### Severity Levels

**CRITICAL** — Must fix before merge
- Security vulnerabilities
- Data loss risks
- Breaking changes

**WARNING** — Should fix
- Performance issues
- Maintainability concerns
- Missing error handling

**SUGGESTION** — Nice to have
- Code style improvements
- Minor optimizations
- Documentation additions

### Example Report

```markdown
# Code Review — 2026-04-23-14-30

## Summary

**Verdict:** APPROVE with minor suggestions

**Files reviewed:** 3
**Total lines:** 247 (TypeScript: 180, Python: 67)

## Critical Issues

**None identified.**

## Important Issues

**Issue #1:** Missing error handling in `apps/web/src/components/Button.tsx:45`
- Description: onClick handler doesn't catch errors
- Recommendation: Wrap with try-catch or add error boundary
- Severity: WARNING

## Suggestions

**Suggestion #1:** Consider extracting Button variants to separate component
- File: `apps/web/src/components/Button.tsx:120-180`
- Reason: Reduces complexity, improves reusability
- Impact: Low effort, medium benefit

## What's Done Well

1. **Excellent type safety** — All functions have proper type hints
2. **Clean component structure** — Logical separation of concerns
3. **Good documentation** — Clear comments where needed

## Brain #6 Feedback

- Test coverage: Good (85% of new code paths)
- Edge cases: Consider adding test for error scenario

## Brain #7 Feedback

- Cross-component impact: Low (isolated change)
- Performance: No concerns (efficient implementation)

## Checklist

- [x] Correctness verified
- [x] Readability assessed
- [x] Architecture reviewed
- [x] Security checked
- [x] Performance evaluated
```

## Files

- `.claude/commands/mm/review.md` — This file
- `.claude/commands/mm/review-handler.py` — Python handler script
- `.claude/agents/mm/code-reviewer/code-reviewer.md` — Review agent definition
- `.planning/REVIEWS/` — Report output directory

## Related Commands

- `/mm:complete-task` — Execute tasks with automatic review
- `/mm:safe-commit` — Commit with pre-commit validation
- `/mm:discover` — Generate specs and plans
