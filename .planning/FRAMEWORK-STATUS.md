# MasterMind Framework — Current Active Flow

**Updated:** 2026-05-25

This file replaces the earlier v3.0-era command inventory.

## Active lifecycle

```text
/mm:discover --roadmap --existing
→ /mm:activate-next-objective
→ /mm:discover-contract-check --objective <slug>
→ /mm:complete-task <TASK_ID> --brief
→ /mm:archive-objective
```

## Active sources of truth

- `.planning/roadmap/**`
- `.planning/changes/<objective>/**`
- `.planning/archive/objectives/**`
- `.planning/HANDOFF-CURRENT.md`
- `execution-state.json` inside each active objective package

## Commands that define the active flow

| Command | Role |
|---|---|
| `/mm:discover --roadmap --existing` | Materialize the ranked roadmap |
| `/mm:activate-next-objective` | Create the next recommended objective package |
| `/mm:discover-contract-check` | Validate the package contract |
| `/mm:complete-task` | Execute a task from `tasks.md` |
| `/mm:continue-task` | Resume an interrupted task |
| `/mm:archive-objective` | Archive a completed objective package |

## Deprecated concepts

These are not part of the active workflow anymore:

- root-level planning artifacts from the retired flow
- the retired manual criteria-verification command
- the retired task-verification command
- milestone-style `/mm:ship` as the main closure path

Historical material may still exist under `.planning/archive/legacy/`, but it
must not guide day-to-day execution.
