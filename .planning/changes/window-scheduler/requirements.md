# Requirements — window-scheduler

## Goal

Define and implement the reusable core planning slice for Window Scheduler so MasterMind can track backend availability windows, checkpoint before switching, and resume safely without coupling the design to a specific project adapter.

## In Scope

- Define the initial Window Scheduler planning slice for the reusable core
- Establish the minimal entities for backend sessions, availability state, run policy, scheduler events, and scheduler checkpoints
- Preserve auditable switching rules, especially mandatory checkpoint-before-switch behavior
- Create a task breakdown that can be implemented incrementally

## Out of Scope

- Provider-specific quota detection heuristics
- Full UI or reporting implementation
- Cost accounting exactness per provider
- Domain-specific adapter logic
- Full transcript persistence

## Non-Negotiables

- No backend switch without a checkpoint
- Reset estimations must capture source and confidence
- Run policy must be explicit or inherited
- Keep the schema reusable at the core layer, not project-adapter specific

## Acceptance Criteria

- A planning package exists for `window-scheduler`
- The package reflects the canonical architecture and schema docs
- The first implementation steps are broken into deterministic tasks
- The next session can start from `tasks.md` without needing chat history
