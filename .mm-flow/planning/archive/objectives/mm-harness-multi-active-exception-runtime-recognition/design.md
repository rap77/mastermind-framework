# Design — mm-harness-multi-active-exception-runtime-recognition

## Architecture / Boundaries

This objective turns the documented exception contract into narrow runtime
support.

Primary touchpoints:

- `.mm-flow/commands/mm/active-objective-state.py`
- `.mm-flow/commands/mm/discover-handler.py`
- `.mm-flow/commands/mm/activate-next-objective-handler.py`
- `tests/unit/test_mm_discover_workflow.py`

## Technical Approach

### 1. Add shared exception helpers in `active-objective-state.py`

The module should own:

- loading `active-objective-exceptions.json`
- validating the minimal schema defensively
- exact-set matching for objective slugs
- command-scoped matching
- returning matched metadata for operator output

Phase-1 helper surface should be explicit before implementation:

- `load_active_objective_exceptions(root_dir: Path) -> list[dict[str, object]]`
- `find_active_objective_exception(root_dir: Path, active_slugs: set[str], requested_slug: str, command_name: str) -> dict[str, object] | None`

Expected responsibilities:

- `load_active_objective_exceptions(...)`
  - read `.mm-flow/planning/active-objective-exceptions.json`
  - return `[]` when the file is missing, unreadable, invalid JSON, or not shaped like the phase-1 contract
  - discard malformed entries instead of raising
- `find_active_objective_exception(...)`
  - build the exact coexistence set from the currently active objective slug(s) plus the requested slug
  - compare against `objective_slugs` using exact-set equality
  - require `command_name` to appear in the entry `commands`
  - return the matched entry or `None`

### 2. Keep failure mode conservative

The helper should return no match when:

- the file is missing
- JSON is invalid
- entries are malformed
- the active/requested slug set does not match exactly
- the command is not listed

This means runtime behavior falls back to the current single-active blocking path.

### 3. Honor exceptions only at the current blocking points

- `discover --existing --objective <slug>`
  - after computing `conflicting_dirs`, ask `find_active_objective_exception(...)` before printing `STATUS: BLOCKED`
  - `command_name` should be `discover --existing --objective`
  - if matched, continue package materialization instead of blocking
- `activate-next-objective`
  - before failing on `active_objective_dirs(ROOT)`, ask the same helper using the currently active slug(s) plus the recommended slug
  - `command_name` should be `activate-next-objective`
  - if matched, continue activation instead of failing

### 4. Surface matched exception metadata to operators

When an exception is honored, commands should expose:

- `ACTIVE_OBJECTIVE_EXCEPTION: <id>`
- `ALLOWED_OBJECTIVES: <slugs>`
- one line with `reason`
- one line with `expires_when`

This should be additive guidance only; success/failure status remains owned by the command itself.

### 5. Explicit test matrix for implementation

T2/T3 should cover these exact cases:

1. `discover` with another active objective and **no exception artifact**
   - remains blocked
2. `discover` with invalid exception artifact
   - remains blocked
3. `discover` with matching slug set but missing `discover --existing --objective` in `commands`
   - remains blocked
4. `discover` with valid matching exception
   - proceeds and emits exception metadata
5. `activate-next-objective` with existing active objective and **no exception artifact**
   - remains failed/blocked under current policy
6. `activate-next-objective` with matching slug set but missing `activate-next-objective` in `commands`
   - remains failed/blocked
7. `activate-next-objective` with valid matching exception
   - proceeds and emits exception metadata

## Dependencies

- current single-active coordination behavior
- the documented exception contract in `.mm-flow/planning/active-objective-exceptions.json`
- existing discover/activate test harness in `tests/unit/test_mm_discover_workflow.py`

## Validation Strategy

```bash
python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-multi-active-exception-runtime-recognition
python3 -m unittest tests.unit.test_mm_discover_workflow
```

T1 is complete when:

- parser responsibilities are explicit
- blocking touchpoints are explicit
- command names for scope matching are explicit
- the T2/T3 test matrix is specific enough to implement without improvisation

## Important Tradeoffs

- **Safety vs convenience:** exact-set matching is restrictive, but safer for phase 1 runtime support
- **Shared helper vs inline parsing:** shared helper reduces drift between discover and activate
- **Runtime support vs roadmap support:** runtime support comes first; roadmap awareness stays deferred
