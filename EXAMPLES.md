# MasterMind Framework — Current Command Examples

These examples reflect the active objective-package workflow.

## 1. Regenerate the roadmap

```bash
python3 .claude/commands/mm/discover-handler.py --roadmap --existing
```

Expected outputs:

- `.planning/roadmap/objectives.md`
- `.planning/roadmap/objectives.json`
- `.planning/roadmap/dependency-graph.md`

## 2. Activate the next recommended objective

```bash
python3 .claude/commands/mm/activate-next-objective-handler.py
```

Expected output:

```text
STATUS: PASSED
- Activated recommended objective: `<slug>`
- Package created under: .planning/changes/<slug>
```

## 3. Validate the package

```bash
python3 .claude/commands/mm/discover-contract-check.py --objective <slug>
```

## 4. Start the first task

```bash
python3 .claude/commands/mm/complete-task-handler.py T1 --brief
```

The active package should contain:

```text
.planning/changes/<slug>/
  requirements.md
  design.md
  tasks.md
  todo.md
  HANDOFF-CURRENT.md
  execution-state.json
```

## 5. Resume an interrupted task

```bash
python3 .claude/commands/mm/complete-task-handler.py T1 --continue --brief
```

## 6. Check status

```bash
python3 .claude/commands/mm/complete-task-handler.py --status
```

## 7. Archive a completed objective

```bash
python3 .claude/commands/mm/archive-objective-handler.py
```

This command:

- infers the sole active objective when possible
- verifies required files exist
- verifies all root tasks are `completed`
- verifies there is no conflicting runtime state
- moves the package to `.planning/archive/objectives/<slug>/`

## Deprecated examples removed

This repository no longer uses examples based on the old root-level planning
surface, the retired manual criteria-verification command, or `/mm:ship` as the
primary workflow.
