---
name: mm-discover
description: >
  Objective-package discovery skill for MasterMind. Use it to materialize the
  roadmap, activate the next objective, or scaffold/update a specific
  `.planning/changes/<objective>/` package.
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "2.0.0"
---

# mm-discover — Objective Discovery Skill

## Mission

Convert repository intent plus current implementation evidence into the active
objective workflow:

```text
.planning/roadmap/
.planning/changes/<objective>/
.planning/archive/objectives/<objective>/
```

This skill no longer uses the old root-level planning artifacts.

## When to Use

Use this skill when the user wants to:

- generate or refresh the roadmap
- activate the next recommended objective
- scaffold a specific objective package
- audit an existing project and tighten the active planning package

## Canonical Flow

### 1. Generate the roadmap

```bash
/mm:discover --roadmap --existing
```

Expected outputs:

- `.planning/roadmap/objectives.md`
- `.planning/roadmap/objectives.json`
- `.planning/roadmap/dependency-graph.md`

### 2. Activate the next recommended objective

```bash
/mm:activate-next-objective
```

If the user wants a specific objective instead:

```bash
/mm:discover --existing --objective <slug> "<Title>"
```

### 3. Validate the package

```bash
/mm:discover-contract-check --objective <slug>
```

Expected package shape:

```text
.planning/changes/<slug>/
  requirements.md
  design.md
  tasks.md
  todo.md
  HANDOFF-CURRENT.md
  execution-state.json
```

### 4. Hand off to execution

```bash
/mm:complete-task <TASK_ID> --brief
```

## Discovery Rules

1. Prefer canonical docs, roadmap state, active packages, and archive/objective
   history.
2. Treat `execution-state.json` as the durable source of task progress.
3. Do not reintroduce root-level planning files.
4. If the package is already scaffolded, tighten it instead of inventing a new
   parallel structure.
5. If there is one active objective in `.planning/changes/`, treat it as the
   current focus unless the user explicitly asks otherwise.

## Active Sources of Truth

- `docs/canonical/**`
- `.planning/roadmap/**`
- `.planning/changes/**`
- `.planning/archive/objectives/**`
- `.planning/HANDOFF-CURRENT.md`

## Do Not Use

- root-level planning artifacts from the retired flow
- manual progress edits in planning artifacts

## Handoff Reminder

Discovery ends when the package is structurally valid. Execution belongs to:

```bash
/mm:discover-contract-check --objective <slug>
/mm:complete-task <TASK_ID> --brief
```
