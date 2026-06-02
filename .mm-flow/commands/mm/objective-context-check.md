---
name: mm:objective-context-check
description: Validate whether a canonical objective is ready before discover materializes it.
argument-hint: "[--objective slug] [--path path/to/objective.md]"
---

# /mm:objective-context-check

Validate a canonical objective and its sidecar intake report before it flows
into `/mm:discover`.

## Usage

```bash
python3 .mm-flow/commands/mm/objective-context-check-handler.py --objective add-oauth-login
python3 .mm-flow/commands/mm/objective-context-check-handler.py --path docs/canonical/objective-specs/add-oauth-login.md
```

## Inputs

- canonical markdown at `docs/canonical/objective-specs/<slug>.md`
- sidecar intake report at `docs/canonical/objective-specs/<slug>.json`

## Statuses

- `STATUS: PASSED`
  - the canonical/report pair is structurally ready for discover
- `STATUS: FAILED`
  - required files, markers, or report keys are missing/invalid
- `STATUS: NEEDS_INPUT`
  - structured interview questions remain unanswered

## Role in the harness flow

```text
context-to-canonical
→ objective-context-check
→ discover
→ discover-contract-check
→ complete-task
→ archive-objective
```
