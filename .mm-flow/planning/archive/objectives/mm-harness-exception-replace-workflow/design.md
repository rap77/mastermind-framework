# Design — mm-harness-exception-replace-workflow

## Architecture / Boundaries

This objective is workflow-focused. It builds on the existing exception
authoring chain:

1. scaffold a new entry, or render an existing entry by `id`
2. edit the JSON object
3. validate the artifact explicitly

Primary touchpoints:

- `.mm-flow/planning/active-objective-exceptions.json`
- `.mm-flow/commands/mm/render-active-objective-exception.py`
- `.mm-flow/commands/mm/validate-active-objective-exceptions.py`
- a potential replace-oriented helper under `.mm-flow/commands/mm/`

## Technical Approach

### 1. Start from the current gap

Current behavior:

- rendering an existing entry by `id` is now safe and normalized
- validation is explicit
- the final paste/replace step is still manual and easy to botch

### 2. Candidate replace workflows

1. helper replaces one entry by `id` from a provided JSON object and then asks
   for explicit validation
2. helper writes a staged candidate artifact to a temp file for manual review
3. docs-only workflow over render + manual replace

Phase 1 should choose the smallest approach that reduces replace errors without
hiding the artifact transition too much.

### 3. Chosen phase-1 workflow: narrow direct-write replace helper

Phase 1 chooses a **narrow direct-write helper**.

The helper should:

1. accept `--id <exception-id>`
2. accept one explicit JSON object input from a file path
3. replace exactly one matching entry inside
   `.mm-flow/planning/active-objective-exceptions.json`
4. fail closed if:
   - the artifact is missing or invalid
   - the target `id` does not exist
   - duplicate ids exist in the artifact
   - the replacement object's `id` does not match `--id`
   - the replacement object is invalid after normalization
5. print a clear instruction to run `validate-active-objective-exceptions.py`

This is the smallest useful step beyond render + manual paste/replace because
it removes the most fragile manual operation while still keeping the
replacement payload explicit and inspectable as a standalone JSON object.

### 4. Rejected phase-1 alternative: staged candidate artifact

Phase 1 does **not** generate a second staged artifact file.

Reasons:

- it adds one more file surface to manage
- it still leaves the final replacement step unresolved
- it gives less practical risk reduction than a narrow replace-by-id write

### 5. Input contract for T2

Proposed helper shape:

- command under `.mm-flow/commands/mm/`
- required input:
  - `--id <exception-id>`
  - `--entry-file <path-to-json-object>`
- behavior:
  - read one JSON object from `--entry-file`
  - normalize and validate it with the existing shared helper logic
  - replace only the matching entry by `id`
  - rewrite the artifact deterministically
- non-goals:
  - no batch replacement
  - no generic JSON patch syntax
  - no implicit editing from stdin/chat text

### 6. Explicit operator workflow

Phase-1 replace flow should be:

1. render the current exception entry by `id`
2. save the edited JSON object to a temporary file
3. run the replace helper with `--id` and `--entry-file`
4. run `validate-active-objective-exceptions.py`

This keeps the changed entry visible as an explicit file artifact while
removing the error-prone manual in-file replacement step.

### 7. Implemented phase-1 behavior

The helper now:

- fails clearly when the exception artifact is missing
- fails clearly when the replacement JSON file is missing or invalid
- fails closed for unknown target ids
- fails closed for duplicate target ids
- fails closed when the replacement object's `id` does not match `--id`
- normalizes the replacement object before writing
- rewrites exactly one matching entry and preserves the rest of the artifact

The helper still requires explicit post-write validation.

## Dependencies

- archived objective `mm-harness-exception-update-workflow`
- `render-active-objective-exception.py`
- `validate-active-objective-exceptions.py`

## Validation Strategy

```bash
python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-exception-replace-workflow
```

T1 should make explicit:

- replace behavior is narrow direct-write, not staged-write
- input is one explicit JSON object file plus `--id`
- validation remains mandatory after replacement
- the helper must fail closed on id mismatch, duplicate ids, missing artifact,
  or invalid replacement objects

## Important Tradeoffs

- **Ergonomics vs auditability:** direct writes reduce manual editing but can
  obscure the artifact delta
- **Narrow replacement vs generic editing:** replace-by-id is safer than
  exposing generic JSON patch behavior
