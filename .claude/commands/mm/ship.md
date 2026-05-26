---
name: mm:ship
description: Legacy compatibility command. Use objective archive/activation commands instead.
argument-hint: ""
---

# /mm:ship

`/mm:ship` is deprecated for this repository's active workflow.

## Use this lifecycle instead

```bash
/mm:archive-objective
/mm:discover --roadmap --existing
/mm:activate-next-objective
/mm:discover-contract-check --objective <slug>
/mm:complete-task <TASK_ID> --brief
```

## Why

The active workflow is objective-based and ledger-driven:

- `.planning/changes/<objective>/`
- `.planning/archive/objectives/<objective>/`
- `execution-state.json`

It no longer uses the old root-level planning surface.

## Compatibility behavior

If you run `/mm:ship`, the Python handler returns a deprecation error with the
replacement commands above.
