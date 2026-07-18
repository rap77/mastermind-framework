# ADR-001: Dynamic Loop Selector for Role Composition

## Status
Accepted

## Date
2026-07-11

## Context
MasterMind already has specialized brains and an orchestrator, but not every objective needs the same sequence or number of participants.
Hardcoding fixed councils or always running the same flow would waste tokens, add latency, and make the system brittle for simple tasks.

We need a reusable runtime decision layer that answers:
- which roles should participate
- how many participants are enough
- in what order they should run
- when to stop, retry, or escalate

## Decision
Add a deterministic `LoopSelector` that chooses the smallest safe loop for the current objective.

The selector will decide using objective type, ambiguity, risk, required capabilities, and available context.

The first version will be rule-based and explainable, not learned.

## Selection Rules
- Start with the smallest loop that can safely complete the objective.
- Add roles only when the objective requires their capability or risk coverage.
- Prefer existing brains as capability providers.
- Treat `contrarian`, `first_principles`, `outsider`, and `executor` as role overlays unless they need persistent memory or metrics.
- If the objective is ambiguous, stop and ask for clarification instead of guessing.
- If the objective is high-risk, add red-team and verification roles.
- If the task is a pure implementation step, do not spawn unnecessary deliberation roles.

## Loop Examples
- Low-risk fix: `executor -> verifier`
- Product decision: `product -> contrarian -> chairman`
- Design sprint: `product -> ux -> ui -> chairman`
- Build feature: `frontend -> backend -> qa -> chairman`
- High-risk objective: `domain role -> red-team -> verifier -> chairman`
- Ambiguous objective: `classifier -> clarification request`

## Alternatives Considered

### Fixed 5-advisor council
- Pros: simple to understand
- Cons: too rigid, always pays the same cost, ignores objective differences

### Learned policy first
- Pros: could optimize over time
- Cons: too hard to trust early, opaque decisions, no stable baseline

### Manual human selection
- Pros: accurate for edge cases
- Cons: defeats the point of an autonomous harness

## Consequences
- The runtime becomes cheaper and more adaptive.
- Roles become reusable adapters instead of permanent hardcoded citizens.
- The system needs a canonical objective classifier and loop contract.
- Future learning can improve selector heuristics without changing the loop contract.

## Related Files
- `docs/ORCHESTRATOR-GUIDE.md`
- `apps/api/mastermind_cli/orchestrator/brain_executor.py`
- `apps/api/mastermind_cli/orchestrator/brain_router.py`
- `apps/api/mastermind_cli/brain_registry.py`
- `.planning/archive/objectives/harness-memory-unification/harness-contract.md`
