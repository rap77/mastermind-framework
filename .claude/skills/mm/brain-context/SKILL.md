---
name: mm-brain-context
description: Use when about to create a GSD roadmap, plan a GSD phase, or validate a PLAN.md in a project with mm CLI — injects expert brain knowledge at 3 critical moments before generic planning decisions are made
---

# mm Brain Context — GSD Integration

## Overview

Injects NotebookLM brain knowledge into GSD workflow at 3 critical moments. Without this, GSD plans are informed only by web research. With this, they're informed by distilled knowledge from 86+ expert books.

**Core principle:** Brains answer WHAT and WHY. GSD answers HOW and WHEN.

---

## The 3 Moments

### Moment 1 — Before ROADMAP.md
**Trigger:** About to run `/gsd:new-milestone` or `gsd-roadmapper`
**Goal:** Brains inform phase structure and priorities before phases are defined

```bash
cd apps/api
uv run mm orchestrate run \
  "[milestone brief — scope, screens, tech stack, constraints]" \
  --brains brain-02-ux-research,brain-03-ui-design,brain-04-frontend \
  --use-mcp
```

**Save output to:** `.planning/research/BRAIN-0X-CONTEXT.md` per brain
**Tell roadmapper:** "Read `.planning/research/BRAIN-*-CONTEXT.md` files when defining phases"

---

### Moment 2 — Before `/gsd:plan-phase N`
**Trigger:** About to plan a specific phase
**Goal:** Domain brain informs CONTEXT.md so gsd-planner has expert context

Select brain by phase domain (table below), run with the phase goal as brief.

```bash
uv run mm orchestrate run \
  "[phase goal + key questions + tech constraints]" \
  --brains [domain-brain] \
  --use-mcp
```

**Save output to:** `.planning/phases/XX-phase-name/CONTEXT.md`
**Then:** Run `/gsd:plan-phase N` — planner reads CONTEXT.md automatically

---

### Moment 3 — After PLAN.md, Before Execute
**Trigger:** `gsd-planner` produced PLAN.md, waiting for user approval
**Goal:** Brain-07 (evaluator) validates the plan before execution

Query brain-07 **directly via MCP** (no context chaining needed):

```python
mcp__notebooklm-mcp__notebook_query(
    notebook_id="d8de74d6-7028-44ed-b4d5-784d6a9256e6",  # brain-07
    query=f"""
    Project: [project name + tech stack]
    Phase: [phase name]
    Plan to validate:
    {plan_md_contents}

    Evaluate: Is this plan complete, well-sequenced, and likely to succeed?
    Provide: approval_conditions or rejection_reasons.
    """
)
```

**If brain-07 approves:** Run `/gsd:execute-phase N`
**If brain-07 rejects:** Iterate PLAN.md on rejection_reasons, re-validate

---

## Brain Selection by Phase Domain

| Phase domain | Brains to run | Context chains |
|---|---|---|
| UX / user flows / info architecture | `brain-02-ux-research` | — |
| Visual design / UI / components | `brain-03-ui-design` | ← brain-02 |
| Frontend / React / state / performance | `brain-04-frontend` | ← brain-03 |
| Backend / API / DB / architecture | `brain-05-backend` | ← brain-01 |
| Testing / CI/CD / DevOps / infra | `brain-06-qa-devops` | ← brain-04 + brain-05 |
| Metrics / growth / post-launch eval | `brain-07-growth-data` | — |
| Strategy / requirements / product | `brain-01-product-strategy` | — |
| Plan validation (always) | `brain-07-growth-data` | — |

**Multiple domains:** Run brains in chain order — context chaining activates automatically.
Example: UI + Frontend phase → `--brains brain-03-ui-design,brain-04-frontend`

---

## Notebook IDs (Software Dev niche)

| Brain | Notebook ID |
|---|---|
| brain-01 Product Strategy | `f276ccb3-0bce-4069-8b55-eae8693dbe75` |
| brain-02 UX Research | `ea006ece-00a9-4d5c-91f5-012b8b712936` |
| brain-03 UI Design | `8d544475-6860-4cd7-9037-8549325493dd` |
| brain-04 Frontend | `85e47142-0a65-41d9-9848-49b8b5d2db33` |
| brain-05 Backend | `c6befbbc-b7dd-4ad0-a677-314750684208` |
| brain-06 QA/DevOps | `74cd3a81-1350-4927-af14-c0c4fca41a8e` |
| brain-07 Growth/Data | `d8de74d6-7028-44ed-b4d5-784d6a9256e6` |
| brain-08 Master Interviewer | `5330e845-29dc-4219-9d7e-c1ccb4851bb3` |

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| Running without `--use-mcp` | Returns stub data. Always `--use-mcp` for real NotebookLM |
| Wrong working dir | `mm` CLI lives in `apps/api/` — always `cd apps/api` first |
| Skipping brain-07 at Moment 3 | Brain-07 is the evaluator — Moment 3 is non-negotiable |
| Running after `/gsd:plan-phase` | Too late — brain context must exist BEFORE the planner runs |
| Generic brief | Include tech stack, constraints, phase goal — vague = vague answer |

---

## Setup (first time in a new project)

Run these checks before using the skill in any repo:

### 1. Detect mm CLI location

```bash
# Option A: global install
which mm

# Option B: local uv project
find . -name "pyproject.toml" | xargs grep -l "mastermind" 2>/dev/null

# Option C: monorepo (apps/api/ or similar)
find . -path "*/mastermind_cli/__init__.py" 2>/dev/null
```

Use the detected path in all commands. Examples:
- Global: `mm orchestrate run ...`
- Local uv: `cd <mm-dir> && uv run mm orchestrate run ...`

### 2. Detect brain config and notebook IDs

```bash
# Option A: .mastermind/config.yaml (standard install)
cat .mastermind/config.yaml 2>/dev/null

# Option B: brain registry (monorepo)
find . -name "brain_registry.py" | xargs grep "notebook_id" 2>/dev/null

# Option C: list brains via CLI
mm brain list 2>/dev/null
```

**Use the notebook IDs from the project config — never from this skill.**
The IDs in the Notebook IDs table above are Software Dev niche only.

### 3. Verify prerequisites

```bash
# NotebookLM MCP running?
# (check mcp__notebooklm-mcp tools are available in session)

# GSD installed?
ls ~/.claude/commands/gsd/ 2>/dev/null | head -3

# Skill installed in project?
grep -l "mm:brain-context\|mm-brain-context" CLAUDE.md 2>/dev/null
```

### 4. Update project CLAUDE.md if missing

Add under a `## mm Brain Context` section:

```markdown
## mm Brain Context (GSD Integration)
Before any GSD operation, check if mm:brain-context skill applies:
- Before ROADMAP.md creation → Moment 1 (pre-roadmap brains)
- Before /gsd:plan-phase N → Moment 2 (domain brain → CONTEXT.md)
- After PLAN.md created → Moment 3 (brain-07 validation)
Skill: `.claude/skills/mm/brain-context/SKILL.md`
mm CLI: [path detected in step 1]
Brain config: [path detected in step 2]
```
