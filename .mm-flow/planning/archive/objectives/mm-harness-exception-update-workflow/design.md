# Design — mm-harness-exception-update-workflow

## Architecture / Boundaries

This objective is policy-first. It defines how to help operators update existing
exception entries more safely than manual copy/replace in raw JSON.

Primary touchpoints:

- `.mm-flow/planning/active-objective-exceptions.json`
- `.mm-flow/commands/mm/scaffold-active-objective-exception.py`
- `.mm-flow/commands/mm/validate-active-objective-exceptions.py`
- a potential update-oriented helper command

## Technical Approach

### 1. Start from the current gap

Current behavior:

- new entry creation is safer through scaffold-to-stdout
- validation catches mistakes after edits
- updates still require manual locate/copy/replace work

### 2. Chosen phase-1 workflow: print-first update helper

Phase 1 chooses a **print-first** workflow, not a mutate-first workflow.

The helper should:

1. read one existing exception entry by `id`
2. print a normalized editable JSON object to stdout
3. optionally apply narrow field overrides before printing
4. keep paste/replace + validation explicit in the operator workflow

This is the smallest useful improvement over manual copy/replace:

- the operator no longer has to locate and manually extract the original entry
- the artifact still changes only through an explicit visible edit
- validation remains a required separate step

### 3. Rejected phase-1 alternative: direct in-place mutation

Phase 1 does **not** perform in-place writes.

Reasons:

- in-place mutation hides too much of the artifact transition for a first slice
- it raises more edge cases around preserving file structure and partial edits
- the current gap is primarily safe extraction + safe editing, not write automation

### 4. Helper contract for T2

Proposed helper shape:

- command:
  - `.mm-flow/commands/mm/render-active-objective-exception.py`
- input:
  - `--id <exception-id>` required
  - narrow optional overrides for fields already supported by the scaffold flow
- output:
  - `STATUS: PASSED|FAILED`
  - one normalized JSON object to stdout when the entry exists
- non-goals:
  - no direct artifact mutation
  - no multi-entry editing
  - no generic JSON patch semantics

### 5. Explicit operator workflow

Phase-1 update flow should be:

1. render the current exception entry by `id`
2. apply narrow overrides in the helper call or edit the printed JSON
3. paste/replace the entry manually inside `active-objective-exceptions.json`
4. run `validate-active-objective-exceptions.py`

This preserves inspectability while reducing the most fragile manual step:
extracting the current entry correctly before editing it.

### 6. Implemented phase-1 behavior

The helper now:

- fails clearly when the exception artifact is missing
- fails clearly for unknown or duplicate ids
- renders one normalized entry by `id`
- supports narrow overrides for:
  - `objective_slugs`
  - `reason`
  - `commands`
  - `command_bundle_refs`
  - `expires_at_utc` + `expires_context`

The helper still does **not** mutate the artifact directly.

## Dependencies

- archived objective `mm-harness-exception-authoring-workflow`
- current scaffold helper and validator
- current exception artifact structure

## Validation Strategy

```bash
python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-exception-update-workflow
```

T1 should make explicit:

- the update flow is print-first
- it complements the scaffold helper rather than replacing it
- validation stays mandatory after paste/replace
- this is the smallest safe step beyond manual copy/replace because it removes
  manual extraction without hiding artifact writes

## Important Tradeoffs

- **Convenience vs auditability:** mutate-first is faster, but print-first keeps changes more inspectable
- **Single-entry tooling vs generic editor:** narrow entry-by-id tooling is safer than broad JSON mutation
