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
- persisted gate verdict at `docs/canonical/objective-specs/<slug>.gate.json`
  (written by this command)

## Statuses

- `STATUS: PASSED`
  - the canonical/report pair is structurally ready for discover
  - writes a gate artifact that allows discover to continue
- `STATUS: FAILED`
  - required files, markers, or report keys are missing/invalid
  - writes a failing gate artifact when the canonical markdown exists
- `STATUS: NEEDS_INPUT`
  - structured interview questions remain unanswered
  - writes a gate artifact that tells another operator/model not to continue yet

## Lifecycle enforcement

If `docs/canonical/objective-specs/<slug>.md` exists, then
`/mm:discover --existing --objective <slug>` now checks the gate artifact:

- missing/stale artifact → stop and rerun the gate
- `NEEDS_INPUT` → stop and answer the open questions
- `FAILED` → stop and repair the canonical/report pair
- `PASSED` → discover may materialize the objective package

## Role in the harness flow

```text
context-to-canonical
→ objective-context-check
→ discover
→ discover-contract-check
→ complete-task
→ archive-objective
```
