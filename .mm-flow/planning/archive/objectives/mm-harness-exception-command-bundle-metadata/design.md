# Design — mm-harness-exception-command-bundle-metadata

## Architecture / Boundaries

This objective is policy-first. It defines whether command-scope relationships
should remain purely hardcoded or become visible in artifacts that operators and
future models can inspect.

Primary touchpoints:

- `.mm-flow/commands/mm/active-objective-state.py`
- `.mm-flow/planning/active-objective-exceptions.json`
- `.mm-flow/planning/active-objective-command-bundles.json`
- planning/handoff guidance for exception authoring

## Technical Approach

### 1. Start from the current runtime model

Current behavior:

- delegated `discover --existing --objective` may inherit `activate-next-objective` scope
- the relationship is hardcoded in runtime helpers
- direct discover remains strict

### 2. Choose a separate bundle artifact

Phase 1 chooses a separate root artifact:

- `.mm-flow/planning/active-objective-command-bundles.json`

Why this option wins:

- keeps `active-objective-exceptions.json` focused on objective slug exceptions
- lets another model inspect command-bundle relationships directly
- avoids a schema break in the existing exception artifact

### 3. Runtime interpretation rule

Shared helpers should evaluate command scope in this order:

1. exact command match in the exception entry
2. delegated match only when:
   - `delegated_from` is present on the child command invocation
   - the bundle artifact explicitly contains `parent_command -> delegated_command`
   - the exception entry authorizes the `parent_command`
3. otherwise fail closed

### 4. Smallest implementation surface

- `active-objective-state.py`
  - load and validate the bundle artifact
  - replace the hardcoded map with artifact-driven bundle lookup
- `activate-next-objective-handler.py`
  - keep passing the hidden delegation marker
- `discover-handler.py`
  - keep consuming the hidden delegation marker
- tests
  - write both the exception artifact and the bundle artifact when delegated inheritance should succeed

### 5. Test matrix for implementation

T2 should prove:

1. delegated activation without bundle artifact
   - fails closed
2. delegated activation with invalid bundle artifact
   - fails closed
3. delegated activation with valid bundle artifact and parent command in exception entry
   - succeeds
4. direct discover with only parent command in exception entry
   - remains blocked
5. direct discover with explicit child command in exception entry
   - still succeeds

## Dependencies

- archived objective `mm-harness-exception-delegated-command-scopes`
- current runtime delegated-scope implementation
- current exception artifact contract

## Validation Strategy

```bash
python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-exception-command-bundle-metadata
python3 -m unittest tests.unit.test_mm_discover_workflow
```

T1 should make explicit:

- the bundle artifact path and schema
- how runtime matches delegated scopes
- how operators author both artifacts safely

## Important Tradeoffs

- **Runtime simplicity vs artifact explainability:** a separate artifact is more explicit, but adds one more file to maintain
- **Bundle artifact vs inline bundle names:** a registry is clearer to inspect and safer to validate centrally
