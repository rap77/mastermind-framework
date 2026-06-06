# Design — mm-harness-exception-authoring-workflow

## Architecture / Boundaries

This objective is policy-first. It defines how to help operators create/update
exception artifacts more safely than raw manual JSON editing.

Primary touchpoints:

- `.mm-flow/planning/active-objective-exceptions.json`
- `.mm-flow/planning/active-objective-command-bundles.json`
- `.mm-flow/commands/mm/validate-active-objective-exceptions.py`
- a new scaffold helper command for authoring

## Technical Approach

### 1. Start from the current gap

Current behavior:

- validation and named bundle refs exist
- runtime semantics are strong and artifact-visible
- operators still author exceptions by editing JSON directly

### 2. Choose scaffold-to-stdout, not mutation

Phase 1 chooses:

- a helper that prints a single exception entry JSON object
- no direct mutation of the exceptions file
- validation remains a separate explicit step

Why this wins:

- reduces syntax mistakes and field omission
- keeps the final artifact transparent and manually inspectable
- avoids hidden merges/upserts in phase 1

### 3. Helper inputs

The scaffold helper should accept explicit fields such as:

- `--id`
- repeated `--objective-slug`
- `--reason`
- repeated `--command`
- repeated `--command-bundle-ref`
- `--expires-at-utc`
- `--expires-context`

It should emit canonical fields including:

- `expires_at_utc`
- `expires_when` formatted as `Expires at <expires_at_utc> — <context>`

### 4. Update workflow stays simple

For updating an existing entry:

- operator reruns the helper with corrected values
- replaces the old entry manually
- reruns the validator

This is less convenient than mutation, but safer and easier to audit.

## Dependencies

- archived objective `mm-harness-exception-named-bundle-references`
- current exception artifact, bundle artifact, and validator
- current runtime fail-closed matching behavior

## Validation Strategy

```bash
python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-exception-authoring-workflow
python3 .mm-flow/commands/mm/scaffold-active-objective-exception.py --help
python3 .mm-flow/commands/mm/scaffold-active-objective-exception.py ...
python3 .mm-flow/commands/mm/validate-active-objective-exceptions.py
```

T1 should make explicit:

- helper-driven scaffold vs mutation
- how the helper integrates with validation
- why scaffold-to-stdout is the smallest safe step beyond manual JSON editing

## Important Tradeoffs

- **Ergonomics vs transparency:** scaffold output is less magical than mutation and keeps artifacts visible, but still requires manual paste/replace
- **Scaffold vs mutate:** generating a skeleton is safer than in-place mutation, but less convenient for repeated updates
