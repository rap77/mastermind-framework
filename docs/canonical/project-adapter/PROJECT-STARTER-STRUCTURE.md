# Project Starter Structure

## 1. Objective

Define the minimum recommended structure for a new project using MasterMind through the Core + Project Adapter model.

## 2. Minimum Starter Kit

Every new project should begin with:

1. project context
2. selected brains
3. decision rights baseline
4. minimal memory boundary
5. first workflow target

## 3. Suggested Structure

```text
project/
├── docs/
│   ├── PROJECT-CONTEXT.md
│   ├── PROJECT-ADAPTER.md
│   ├── DECISION-RECORDS/
│   └── WORKFLOWS/
├── context/
│   ├── niche.md
│   ├── constraints.md
│   └── integrations.md
├── memory/
│   ├── local-observations.md
│   ├── local-patterns.md
│   └── promotion-candidates.md
└── mastermind/
    ├── selected-brains.md
    ├── rights-matrix.md
    └── starter-plan.md
```

## 4. Required Initial Files

### `PROJECT-CONTEXT.md`

What this project is trying to do.

### `PROJECT-ADAPTER.md`

How this project adapts MasterMind.

### `selected-brains.md`

Which brains are in scope.

### `rights-matrix.md`

Who owns which decisions.

### `starter-plan.md`

What first workflow or problem MasterMind will help solve.

## 5. Promotion Rule

No file or rule should move back to core automatically.

Promotion to core requires:

- reuse across projects
- explicit decision
- documented rationale

## 6. Anti-Patterns

- copying the entire MasterMind repo
- mixing local context directly into reusable doctrine
- starting with too many brains
- no memory boundary between project and core

## 7. Recommendation

Start small:

- one clear problem
- a small brain set
- one reusable workflow
- explicit learning capture
