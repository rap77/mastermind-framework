# UOW-1 Implementation Plan — Project Manifest + Source-of-Truth Rules

## Goal
Create the minimum runtime and planning contract needed to identify the active
project, separate AI-DLC from `.planning`, and make the rest of the harness
architecture executable.

## Scope
### In scope
- project manifest structure
- active project detection
- source-of-truth rules
- planning vs design responsibility split
- first validation of the unified initiative context

### Out of scope
- harness loop execution
- memory persistence internals
- project adapter implementation
- rewriting existing planning/history artifacts

## Deliverables
- `ProjectManifest` schema
- project detection rules
- source-of-truth contract
- AI-DLC / `.planning` responsibility split
- validation notes for downstream UOWs
- functional spec with exact manifest fields and conflict rules

## Implementation Steps
- [ ] Define the manifest fields required to identify the active project.
- [ ] Define the explicit rule that AI-DLC is the design/source-of-truth layer.
- [ ] Define the explicit rule that `.planning` is the operational/intention layer.
- [ ] Define the validation condition that prevents cross-project confusion.
- [ ] Record the contract in AI-DLC planning artifacts.
- [ ] Verify the manifest can support downstream harness and memory slices.
- [ ] Add concrete examples and failure cases.

## Acceptance Criteria
- The active project can be named without ambiguity.
- The workflow split is documented and stable.
- The downstream UOWs can consume the manifest without reinterpretation.
- No existing historical artifacts need to be deleted or rewritten.
- The conflict behavior is explicit enough to implement without new questions.

## Notes
- This UOW is intentionally small.
- It exists to stop scope drift before harness code is written.
