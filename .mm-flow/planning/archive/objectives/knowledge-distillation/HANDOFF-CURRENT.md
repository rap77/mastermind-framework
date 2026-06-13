# Handoff — knowledge-distillation

## Current objective
- `knowledge-distillation`

## Decisions already made
- Use a per-objective planning package instead of relying on a single root planning surface forever.
- Another model should be able to resume from artifacts, not from chat memory alone.
- Historical Phase 14 backend work already exists for knowledge distillation;
  this objective should not restart that whole phase.
- The current Phase 1 slice is now narrowed to exposing existing
  knowledge-distillation signals in a current UI surface.
- The first implementation should reuse current analytics/template routes rather
  than creating a second backend observability path.
- `/project-state` now consumes the existing KD analytics/template routes and
  renders a read-only knowledge-distillation panel with record count, quality,
  latency, yield, and top reusable templates.
- The KD panel fails soft: the rest of `/project-state` still renders even if
  analytics endpoints are unavailable, because the page loader uses
  `Promise.allSettled(...)` for this additive surface.

## Blockers / risks
- This Phase 1 slice is intentionally read-only and global; it does not yet tie
  KD metrics/templates to a specific project or task.
- If deeper KD work continues later, the next gap should be a more specific
  operator workflow, not a broad restart of backend distillation logic.

## Exact next recommended task
- Run `/mm:archive-objective knowledge-distillation` if we want to close this
  Phase 1 visibility slice as complete.

## Validation commands
- `/mm:discover-contract-check --objective knowledge-distillation`
- `pnpm --dir apps/web test:run src/components/project-state/__tests__/ProjectStateDashboard.test.tsx`
- `pnpm --dir apps/web test:run src/components/ws/__tests__/BrainStatusFeed.test.tsx`
