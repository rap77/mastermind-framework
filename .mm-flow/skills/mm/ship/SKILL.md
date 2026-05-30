---
name: mm-ship
description: >
  Legacy compatibility note for the old shipping flow. The active lifecycle now
  closes work with `/mm:archive-objective` and continues with
  `/mm:activate-next-objective`.
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "2.0.0"
---

# mm-ship — Legacy Compatibility Note

`/mm:ship` is no longer the primary lifecycle for this repository.

## Use This Instead

### Close a completed objective

```bash
/mm:archive-objective
```

### Materialize the roadmap and activate the next objective

```bash
/mm:discover --roadmap --existing
/mm:activate-next-objective
```

### Validate and execute the next task

```bash
/mm:discover-contract-check --objective <slug>
/mm:complete-task <TASK_ID> --brief
```

## Why `/mm:ship` is Legacy Here

The old flow assumed root-level planning artifacts and version-tag shipping as
the main closure mechanism.

The active flow uses:

- `.planning/changes/<objective>/...`
- `.planning/archive/objectives/<objective>/...`
- `execution-state.json`
- objective archive instead of milestone-style shipping

## Rule

If another model reaches for `/mm:ship`, redirect it to the objective lifecycle
above.
