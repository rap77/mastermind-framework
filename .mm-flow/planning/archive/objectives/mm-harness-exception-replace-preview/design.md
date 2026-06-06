# Design — mm-harness-exception-replace-preview

## Architecture / Boundaries

This objective builds on the current exception authoring chain:

1. render one entry by `id`
2. edit the JSON object in a file
3. optionally preview the replacement impact
4. replace by `id`
5. validate explicitly

Primary touchpoints:

- `.mm-flow/commands/mm/render-active-objective-exception.py`
- `.mm-flow/commands/mm/replace-active-objective-exception.py`
- `.mm-flow/commands/mm/validate-active-objective-exceptions.py`
- a potential preview-oriented helper under `.mm-flow/commands/mm/`

## Technical Approach

### 1. Start from the current gap

Current behavior:

- replace-by-id is now narrow and fail-closed
- replacement input is explicit and inspectable
- there is still no first-class preview/dry-run before the artifact write

### 2. Candidate preview workflows

1. helper compares current entry vs replacement file and prints a narrow field diff
2. replace helper gains a `--dry-run` mode that prints the pending replacement
3. docs-only workflow using render output and manual comparison

Phase 1 should choose the smallest preview surface that improves confidence
without growing into a general diff tool.

### 3. Chosen phase-1 workflow: `--dry-run` on replace helper

Phase 1 chooses a **`--dry-run` mode on**
`.mm-flow/commands/mm/replace-active-objective-exception.py`.

The dry-run should:

1. accept the same required inputs as the write path:
   - `--id <exception-id>`
   - `--entry-file <path>`
2. load the current artifact and replacement object using the exact same
   fail-closed checks as the write path
3. print a narrow preview containing:
   - target `id`
   - normalized current entry
   - normalized replacement entry
   - a concise changed-fields summary
4. avoid mutating the artifact

This is the smallest useful preview slice because:

- it reuses the replace helper contract users already know
- it avoids creating another standalone command surface
- it gives pre-write confidence without becoming a general diff engine

### 4. Why this gap can be deferred if needed

This gap is useful, but **not critical** right now.

Reasons:

- the current replace-by-id workflow is already explicit and fail-closed
- validation remains mandatory after writes
- the remaining risk is operator confidence/visibility, not silent corruption

So the priority guidance is:

- **implement now** if we want smoother operator UX on exception maintenance
- **defer safely** if more urgent harness/runtime gaps appear

### 5. Helper contract for T2

Proposed behavior:

- keep `replace-active-objective-exception.py` as the single mutation surface
- add:
  - `--dry-run`
- rules:
  - `--dry-run` runs the same parsing/normalization path as the real write
  - `--dry-run` must never write the artifact
  - normal execution keeps current write semantics

### 6. Explicit operator workflow

Phase-1 preview flow should be:

1. render the current exception entry by `id` if needed
2. edit the replacement JSON file
3. run `replace-active-objective-exception.py --dry-run`
4. if the preview looks correct, run the write path
5. run `validate-active-objective-exceptions.py`

This keeps the workflow narrow and gives a clear decision point before writes.

### 7. Implemented phase-1 behavior

The preview now lives on `replace-active-objective-exception.py --dry-run`.

It:

- reuses the same fail-closed parsing path as the write mode
- prints:
  - target id
  - normalized current entry
  - normalized replacement entry
  - changed top-level fields
- never mutates the artifact in dry-run mode
- keeps the normal write path unchanged

## Dependencies

- archived objective `mm-harness-exception-replace-workflow`
- `render-active-objective-exception.py`
- `replace-active-objective-exception.py`

## Validation Strategy

```bash
python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-exception-replace-preview
```

## Important Tradeoffs

- **Confidence vs scope:** a narrow field diff is safer than a generic artifact diff
- **Separate helper vs helper flag:** `--dry-run` may be simpler, but must remain explicit and deterministic

## T1 decision

T1 now makes explicit:

- preview should be a `--dry-run` flag, not a new generic diff tool
- the preview should show normalized before/after entries plus changed fields
- this gap is valuable but deferrable because current write semantics are already
  explicit and fail-closed
