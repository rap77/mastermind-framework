# Design — mm-harness-exception-named-bundle-references

## Architecture / Boundaries

This objective is policy-first. It defines whether exception entries should be
able to reference reusable named command bundles instead of manually coordinating
with a separate artifact.

Primary touchpoints:

- `.mm-flow/planning/active-objective-exceptions.json`
- `.mm-flow/planning/active-objective-command-bundles.json`
- `.mm-flow/commands/mm/active-objective-state.py`
- authoring validation/helper flows

## Technical Approach

### 1. Start from the current drift source

Current behavior:

- command bundles are artifact-visible
- exception entries still list direct parent commands manually
- operators must mentally map from exception entry -> bundle registry -> delegated child commands

### 2. Choose additive/alternative named refs

Phase 1 chooses:

- bundle entries get a stable `name`
- exception entries may specify `command_bundle_refs`
- `commands` remains supported for direct explicit scopes
- effective allowed commands = explicit `commands` plus resolved parent commands from refs

Why this wins:

- bundle refs can reduce duplication immediately
- explicit `commands` still works for gradual rollout and transparency
- runtime can fail closed when refs are unknown without changing core matching semantics

### 3. Runtime interpretation rule

Shared helpers should:

1. load named bundle registry from artifact
2. resolve `command_bundle_refs` into parent commands
3. union those parent commands with explicit `commands`
4. apply current direct/delegated scope rules using the effective allowed command set

If any bundle ref is unknown or malformed, the exception entry must not match.

### 4. Validation behavior

The validator should:

- validate bundle names are unique and non-empty
- validate every `command_bundle_refs` entry resolves
- print effective command scopes for each exception entry on success

## Dependencies

- archived objective `mm-harness-exception-authoring-drift-reduction`
- current exception artifact, bundle artifact, and validator
- current runtime fail-closed matching behavior

## Validation Strategy

```bash
python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-exception-named-bundle-references
python3 .mm-flow/commands/mm/validate-active-objective-exceptions.py
python3 -m unittest tests.unit.test_mm_discover_workflow
```

T1 should make explicit:

- named bundle refs are additive/alternative to explicit commands
- runtime resolves refs to parent commands deterministically
- validation shows effective resolved command scopes

## Important Tradeoffs

- **Reuse vs transparency:** named refs reduce duplication, but need good validation output so effective scopes stay obvious
- **Alternative vs additive fields:** additive keeps rollout safer and backwards-compatible
