# Code Generation Plan — UOW-1 Project Manifest + Source-of-Truth Rules

## Unit Context

- **Unit**: UOW-1 Project Manifest + Source-of-Truth Rules
- **Slice**: `manifest-contract-bridge-v1`
- **Stories / Requirements**:
  - UOW-1 manifest identity
  - source-of-truth split between AI-DLC and `.planning`
  - cross-project confusion prevention
  - manifest validation and conflict handling
- **Dependencies**:
  - AI-DLC application design for harness + memory architecture
  - AI-DLC functional spec for UOW-1
  - `.planning` operational state files used as input
- **Service Boundary**:
  - The slice should define and validate the manifest contract first.
  - It should not implement harness execution yet.
- **Database Ownership**:
  - No new persistent database entities.
  - The manifest is a lightweight contract artifact, not a schema migration.

## Exact Code / Artifact Paths

### AI-DLC artifacts
- `aidlc-docs/aidlc-state.md`
- `aidlc-docs/inception/plans/project-manifest.md`
- `aidlc-docs/inception/plans/harness-memory-roadmap.md`
- `aidlc-docs/inception/application-design/uow-1-project-manifest-spec.md`
- `aidlc-docs/construction/plans/UOW-1-project-manifest-code-generation-plan.md`

### Operational bridge inputs
- `.planning/HANDOFF-CURRENT.md`
- `.planning/FRAMEWORK-STATUS.md`

### Optional runtime seam for later slices
- `apps/api/mastermind_cli/orchestrator/project_manifest.py`
- `apps/api/tests/unit/test_project_manifest.py`

## Generation Strategy

- Keep the slice thin: define the manifest contract and validation rules.
- Do not mix in harness selection or memory persistence.
- Use explicit source-of-truth rules so the runtime can avoid project drift.
- If runtime parsing is added later, keep it isolated in a small helper module.

## Plan

- [ ] Step 1 — Confirm the canonical manifest location and the fields required
      to identify the active project, active objective, and source-of-truth
      split.
- [ ] Step 2 — Encode the manifest contract into AI-DLC artifacts so the
      project can be recognized without reading the entire repo.
- [ ] Step 3 — Define validation behavior for missing project identity,
      missing AI-DLC authority, missing `.planning` authority, and cross-project
      mismatch.
- [ ] Step 4 — Write the bridge rules that determine when AI-DLC wins, when
      `.planning` wins, and when execution must stop.
- [ ] Step 5 — Add a small, testable runtime seam later if needed to load and
      validate the manifest programmatically.
- [ ] Step 6 — Create a summary artifact for the slice with paths changed,
      rules added, and explicit non-goals.

## Traceability

- **Manifest identity** → Steps 1, 2
- **Source-of-truth rules** → Steps 2, 3, 4
- **Conflict handling** → Steps 3, 4
- **Future runtime seam** → Step 5

## Explicit Non-Goals For This Slice

- No harness loop execution
- No memory persistence implementation
- No adapter wiring
- No bridge runtime beyond contract definition
- No rewriting of historical planning artifacts

## Plan Status

This plan is the source of truth for Code Generation of
`manifest-contract-bridge-v1`.
