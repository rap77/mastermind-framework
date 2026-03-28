# Brain #03-UI — Evaluation Criteria

## Rating 3 (Peer) vs Rating 4 (Senior)

A Rating 3 response is PR-ready with minor tweaks. A Rating 4 response improves the codebase by detecting something not in the ticket. Use this table to distinguish them:

| Attribute | Rating 3 (Peer) | Rating 4 (Senior) |
|-----------|-----------------|-------------------|
| Visual decision | Suggests correct Tailwind class | Explains WHY this class over alternatives — semantic meaning, not just visual look |
| Animation | "Add transition for smoothness" | Names the specific cognitive event being animated (orientation / feedback / delight) with timing rationale |
| Component choice | Uses shadcn/ui correctly | Evaluates whether shadcn/ui is the right primitive OR a custom component serves better — justifies the decision |
| Density | Correct spacing tokens | Balances information density vs cognitive load — references specific War Room panel needs and user task |
| Consistency | Follows existing visual patterns | Identifies pattern divergence before it becomes visual debt — cites the specific component that set the precedent |
| Accessibility | Avoids color-only state | Proposes specific secondary indicator (icon name, label, pattern) before the accessibility gap is raised |

## Auto-Reject Conditions

These conditions trigger automatic rejection before the Rating 3 threshold:

**Animation Inflation (Rating < 3):**
Any suggestion to add animation "for feel" or "to make it feel alive" or "to add polish" without a stated UX purpose (orientation / feedback / delight) = Animation Inflation.
> Cite: Saffer — "A microinteraction should feel inevitable, not decorative."

**Stack Hallucination — Tailwind Config (Rating 1):**
Any suggestion requiring `tailwind.config.js` modifications = Stack Hallucination.
> Tailwind 4 is CSS-only config. There is no `tailwind.config.js` in this project.
> Rejection: `Rejected: tailwind.config.js does not exist. Source: global-protocol.md > Stack Hard-Lock | brain-03-ui/warnings.md > Tailwind Config Contamination`

**Color-Only State (Rating 1 — Blocker):**
Any design that communicates state through color alone (active, error, success) without a secondary indicator = accessibility violation.
> 8% of War Room users are colorblind. Color MUST be paired with icon, label, or pattern.

**Panel-Agnostic Recommendation (Rating 2 max):**
Any design recommendation that doesn't reference which War Room panel is in scope = generic ChatGPT-level advice. Not usable.

## Rating 5 Threshold

Rating 5 responses propose a design solution that unlocks a downstream phase capability:

> Example: Identifies that current NexusCanvas node state communication relies on color-only (Rating 1 risk for 8% colorblind users) and proposes a specific motion + icon pattern that also prepares the node anatomy for Phase 12 parallel dispatch visualization — reducing the Phase 12 visual migration cost.

## Profitability Gate

T1 (context setup time) < 300 seconds (5 minutes). If context setup takes longer than 5 minutes, the agent is not profitable versus the manual mm:brain-context skill.

Flag any baseline where T1 > 300s as "agent-unprofitable" — these identify automation candidates for future phases.
