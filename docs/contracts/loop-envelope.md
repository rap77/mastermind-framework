# Loop Envelope Contract

The harness must emit a canonical envelope for every run.

## Fields

- `status`: current run status (`ok`, `blocked`, `needs_clarification`, `failed`)
- `summary`: short human-readable result
- `artifacts`: files, outputs, or references produced by the run
- `risks`: remaining risks or failure modes
- `next_actions`: next safe steps
- `verification`: how the result was or should be verified
- `recovery`: checkpoint or resume information
- `selected_loop`: loop name chosen by the selector
- `selected_roles`: roles/cerebros used in the run
- `selection_reason`: why this loop was selected

## Invariants

- The envelope must be stable across loops.
- The same input context should produce the same selected loop.
- Ambiguous objectives must not silently fall through to a random loop.
- Verification and recovery must be explicit, not implied.

## Notes

- This contract is for the runtime boundary, not for user-facing narrative.
- The envelope should be machine-readable first and human-readable second.
