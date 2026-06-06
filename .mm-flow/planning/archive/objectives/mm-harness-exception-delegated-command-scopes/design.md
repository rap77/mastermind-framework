# Design — mm-harness-exception-delegated-command-scopes

## Architecture / Boundaries

This objective is policy-first. It should define how multi-active exception
command scopes behave when one harness command delegates to another.

Primary touchpoints:

- `.mm-flow/commands/mm/active-objective-state.py`
- `.mm-flow/commands/mm/activate-next-objective-handler.py`
- `.mm-flow/commands/mm/discover-handler.py`
- planning/handoff guidance for writing exception artifacts

## Technical Approach

### 1. Start from the new runtime behavior

Current behavior is safe but verbose:

- `activate-next-objective` checks its own command scope
- then delegated `discover --existing --objective` must also be listed
- otherwise activation fails closed

### 2. Evaluate explicit delegated-scope options

Candidate approaches:

1. keep explicit listing of every participating command
2. let certain parent commands imply a documented delegated child scope
3. add artifact-level aliases/bundles for related command scopes

Phase 1 chooses the smallest model that preserves explainability:

- only `activate-next-objective` may delegate exception scope
- only to `discover --existing --objective`
- only when `discover` receives an explicit delegation marker

### 3. Runtime interpretation rule

The delegated-scope rule should be:

- normal case: command must match one listed in `commands`
- delegated case: `discover --existing --objective` may also match when:
  - it was invoked by `activate-next-objective`
  - the invocation carries a dedicated delegation marker
  - the exception lists `activate-next-objective`

This keeps direct discover usage strict while reducing operator-facing need to
list both commands for the common activation path.

### 4. Smallest implementation surface

Phase-1 touchpoints should be:

- `activate-next-objective-handler.py`
  - pass an explicit delegation marker when it launches discover
- `discover-handler.py`
  - accept a hidden/internal `--delegated-from <command>` flag
- `active-objective-state.py`
  - centralize the parent->child delegated scope rule so both commands stay aligned

### 5. Test matrix for implementation

T2 should prove:

1. direct `discover --existing --objective` with only `activate-next-objective` in `commands`
   - remains blocked
2. delegated discover from `activate-next-objective` with only `activate-next-objective` in `commands`
   - succeeds
3. unsupported/unknown delegation markers
   - fail closed
4. invalid metadata
   - fail closed
5. normal explicit discover command entries
   - still work unchanged

## Dependencies

- archived objective `mm-harness-multi-active-exception-runtime-recognition`
- current active-objective exception artifact contract
- existing runtime tests for discover/activate exception recognition

## Validation Strategy

```bash
python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-exception-delegated-command-scopes
```

T1 should make explicit:

- what the delegated-scope rule is
- where it is interpreted
- how operators author artifacts safely
- how direct discover stays stricter than delegated discover

## Important Tradeoffs

- **Safety vs ergonomics:** explicit command lists are safer but expose orchestration details
- **Implicit inheritance vs explicit bundles:** inheritance is simpler to author, bundles may be clearer to audit
