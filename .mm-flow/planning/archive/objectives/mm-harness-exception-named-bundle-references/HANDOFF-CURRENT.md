# Handoff — mm-harness-exception-named-bundle-references

## Current objective
- `mm-harness-exception-named-bundle-references`

## Decisions already made
- Exception matching, bundle metadata, machine expiry, and authoring validation are implemented and archived.
- Named bundle refs are now supported through additive/alternative `command_bundle_refs`.
- Bundle entries now require stable `name` fields.
- Validation/runtime resolve effective command scopes deterministically and fail closed on unknown refs.

## Blockers / risks
- Named refs reduce duplication, but there is still no guided way to author a brand-new exception entry from scratch.
- Effective command scopes are surfaced by validation, but operators still edit raw artifacts manually.

## Deferred follow-up gaps
- Add a safer creation/update workflow for new exception entries.
- Consider whether exception entries should eventually prefer refs over raw commands by convention.
- Revisit roadmap exception awareness now that refs, bundles, and expiration are artifact-visible.

## Exact next recommended task
- All objective tasks are complete; run `/mm:archive-objective mm-harness-exception-named-bundle-references` and open the next exception-related follow-up objective.

## Validation commands
- `/mm:discover-contract-check --objective mm-harness-exception-named-bundle-references`
- `python3 .mm-flow/commands/mm/validate-active-objective-exceptions.py`
- `python3 -m unittest tests.unit.test_mm_discover_workflow`
