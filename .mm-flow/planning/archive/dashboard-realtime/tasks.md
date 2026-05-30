# Tasks — dashboard-realtime

## Execution Rules
- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Each task must declare purpose, dependencies, likely file touchpoints, validation commands, and acceptance criteria.

## RT1: Event contract

### Purpose
Define the realtime contract before implementation diverges.

### Depends On
None

### Parallelizable
no

### Files / Areas Likely Touched
- docs/canonical/35-WEBSOCKET-EVENT-CONTRACT.md

### Validation Commands
- Review event contract for explicit payload fields and event names.

### Acceptance Criteria
- [ ] Event names, payloads, and source boundaries are documented.
- [ ] The backend has a clear authority boundary for publishing events.

## RT2: Backend publication path

### Purpose
Add a minimal publication path for the target objective.

### Depends On
RT1

### Parallelizable
no

### Files / Areas Likely Touched
- apps/api/mastermind_cli

### Validation Commands
- Run targeted backend tests for realtime publication.

### Acceptance Criteria
- [ ] A minimal backend publication path exists for the target objective.
- [ ] Tests or targeted validation cover the publication path.

## RT3: Frontend consumption

### Purpose
Consume the realtime signal safely in the UI.

### Depends On
RT2

### Parallelizable
no

### Files / Areas Likely Touched
- apps/web/src/components

### Validation Commands
- Run frontend lint/typecheck for the affected realtime components.

### Acceptance Criteria
- [ ] The frontend consumes the event signal safely.
- [ ] The UI degrades gracefully if no live events arrive.
