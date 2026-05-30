---
name: mm:continue-task
description: Resume a MasterMind task from the last checkpoint. Alias for /mm:complete-task <task-id> --continue.
argument-hint: "<task-id> [--brief]"
---

# /mm:continue-task

Resume a previously started MasterMind task from its latest checkpoint.

## Usage

```bash
/mm:continue-task D2
/mm:continue-task D2 --brief
```

## Behavior

This command is equivalent to:

```bash
/mm:complete-task D2 --continue
```

To print the exact brief another model should use before resuming:

```bash
/mm:complete-task D2 --brief
```

## Required Inputs

- `.planning/task-progress.json` must exist for the task
- the objective package paths recorded in `task-progress.json` must still exist
- `.planning/changes/<objective>/execution-state.json` should exist to preserve durable task history across root tasks

## Continuation Contract

The resuming model/agent must:

1. read `.planning/task-progress.json`
2. read the plan path recorded in `.planning/task-progress.json`
3. read the todo path recorded in `.planning/task-progress.json`
4. continue from the last checkpoint instead of re-planning the task
5. preserve previously completed subtasks
6. re-run validation before marking new progress

If the package changed materially since the checkpoint was created, stop and regenerate the objective package with `/mm:discover --existing --objective <name>` before resuming.
