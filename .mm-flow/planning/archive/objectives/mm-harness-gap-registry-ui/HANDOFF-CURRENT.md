# Handoff — mm-harness-gap-registry-ui

## Current objective
- `mm-harness-gap-registry-ui`

## Decisions already made
- The first coherent slice is a read-only gap registry panel.
- Phase 1 should reuse `/project-state` instead of creating a separate route.
- UI write-side controls for gaps remain out of scope.
- The implementation reads the gap registry server-side and renders lifecycle fields in the existing right-rail dashboard panel.
- Empty-state rendering is explicit when the registry file is absent or has no entries.

## Blockers / risks
- The existing project-state data path may need a small server-side extension to expose the gap registry cleanly.
- Keeping the UI artifact-authoritative means not overcomputing browser-only gap semantics.
- This slice does not yet expose duplicate suspects or the `next` recommendation; it only shows raw registry entries.

## Exact next recommended task
- Archive `mm-harness-gap-registry-ui`.

## Validation commands
- `/mm:discover-contract-check --objective mm-harness-gap-registry-ui`
- `pnpm --dir apps/web test:run src/components/project-state/__tests__/ProjectStateDashboard.test.tsx`
