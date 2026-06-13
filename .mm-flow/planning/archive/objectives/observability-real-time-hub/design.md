# Design — observability-real-time-hub

## Architecture / Boundaries
- Follow the existing monorepo split: Python/FastAPI product logic, Next.js UI, Rust control-plane where operationally justified.
- New behavior should enter through semantic services or explicit UI boundaries, not ad-hoc global state.

## Technical Approach
- Build the smallest coherent vertical slice that satisfies the acceptance criteria.
- Reuse the existing `project_state` incremental domain and MM command infrastructure where possible.
- Reuse the existing `BrainStatusFeed` + `useWebSocket` client path instead of
  inventing a new observability transport for Phase 1.
- Keep `/project-state` SSE refresh as-is for data refresh; the new read path is
  additive and read-only.

## Dependencies
- No explicit upstream dependency declared

## Validation Strategy
- Run targeted Python tests or validation commands for touched areas.
- Run relevant web lint/typecheck commands when frontend files change.
- Refresh handoff state after completing or partially completing the objective.
- For the first implementation slice, prefer targeted frontend tests around the
  new `/project-state` observability surface and the existing brain-event feed.

## Important Tradeoffs
- Prefer execution-ready specificity over speculative completeness.
- Prefer incremental compatibility over large migration bursts.
- Prefer exposing already-available brain lifecycle signals in the UI over
  broadening backend observability infrastructure again.

## Context Notes
- Historical phase evidence shows the repo already shipped:
  - Rust WebSocket event hub under `/ws/events`
  - reusable `BrainStatusFeed` and `useWebSocket` in the web app
  - `/project-state` live shell with SSE-triggered refresh
- The smallest coherent next gap is not “build observability from scratch” but
  “connect existing real-time brain-event visibility to a high-value operator
  surface.”

## Phase 1 Slice

### Goal
Add a read-only brain-event observability panel to `/project-state` so an
operator can see live brain lifecycle updates without leaving the project-state
surface.

### Likely Touchpoints
- `apps/web/src/components/project-state/ProjectStateDashboard.tsx`
- `apps/web/src/components/project-state/ProjectStateLiveShell.tsx`
- `apps/web/src/components/ws/BrainStatusFeed.tsx`
- new focused frontend tests if needed

### Explicit Non-Goals
- no replacement of SSE with WebSockets for project-state refresh
- no new backend event aggregation endpoint
- no alerting/metrics export integration in this slice
