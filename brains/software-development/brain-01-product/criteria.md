# Brain #01-Product — Evaluation Criteria

## Purpose

This file defines how to evaluate Brain #1 (Product Strategy) responses against the Delta-Velocity Matrix. Use this file when rating a consultation output. The criteria are observable and domain-specific — not generic quality statements.

A response that "sounds good" but cannot be rated against this table is a Rating 2 at best.

---

## Rating 3 (Peer) vs Rating 4 (Senior)

| Attribute | Rating 3 (Peer) | Rating 4 (Senior) |
|-----------|-----------------|-------------------|
| **Focus** | Solution space — suggests logical features based on the request | Opportunity space — frames the problem as user pain before touching solutions |
| **Risks** | "We should validate this" (generic, no specifics) | Explicitly names all 4 Risks: Value (will users want it?), Usability (can they use it?), Feasibility (can we build it?), Viability (should the business build it?) |
| **Metrics** | Vanity metrics or output metrics (ship X, ship by date Y) | Outcome KRs — measurable behavior changes (e.g., "agent executes protocol in <20% human T1 time") |
| **Systems** | Linear thinking — A causes B, single causal chain | Identifies Feedback Loops + second-order effects (e.g., faster T1 → more brain queries → more feed pollution → need for feed hygiene) |
| **Decision** | Waiter mode — takes the order, organizes it, asks "anything else?" | Synthesizer — questions "why now", surfaces alternatives, proposes the smallest useful experiment |

**Observable distinction:** A Rating 3 response answers the question asked. A Rating 4 response also points out what question SHOULD have been asked.

---

## Auto-Reject (Rating 1-2)

**Build Trap Trigger:**
Any response that proposes a date-fixed feature roadmap without demand validation = Build Trap = automatic Rating < 3.

The Build Trap is proposing outputs (features, deliverables, dates) without validating the underlying user pain. Cite: Torres/continuous-discovery — "Build Trap = optimizing for outputs, not outcomes."

**Feature-First Trigger:**
Any response that names solutions before framing the opportunity = solution space anchoring = Rating 2 maximum.

---

## Rating 5 (Architect) Threshold

A Rating 5 response:
- Identifies a systemic leverage point (Meadows) where one change shifts multiple outcomes simultaneously
- Predicts second-order effects with supporting logic (not just intuition)
- Proposes an experiment that validates multiple assumptions at once (Torres opportunity solution tree)
- Reframes the problem in a way that makes multiple current roadmap items obviously wrong or obviously right

Example Rating 5: "The real leverage point is not automating the 6-step protocol — it's the T1 measurement itself. If T1 > 5min consistently, we don't have an automation problem, we have a feed hygiene problem. One script that auto-prunes stale entries in BRAIN-FEED.md would unlock Phases 11-12 faster than any agent dispatch optimization."

---

## Minimum for Rating 3

A response must satisfy ALL of the following to be Rating 3:

1. References MasterMind Framework's actual milestone (v2.2 Brain Agents) — not a generic product advice response
2. Ties at least one recommendation to a measurable outcome metric (not "it would be nice")
3. Names the user pain explicitly (not implied, not assumed — stated)
4. Respects the Stack Hard-Lock (no suggestions outside `global-protocol.md > Stack Hard-Lock`)
5. Does not propose a feature roadmap without user demand validation

If any of these are missing, the response is Rating 2 regardless of how technically correct it sounds.

---

## Evaluation Checklist

When rating a Brain #1 response, verify:

- [ ] Did the brain read BRAIN-FEED.md before responding? (Step 1 — ask to show it)
- [ ] Does the `[IMPLEMENTED REALITY]` block contain only what's shipped, not roadmap? (Step 2)
- [ ] Are the 3 domain-specific `[CORRECTED ASSUMPTIONS]` present? (Step 3)
- [ ] Does the recommendation name user pain with evidence, not features with assumptions? (Focus attribute)
- [ ] Are all 4 Risks named (or explicitly excluded with reason)? (Risks attribute)
- [ ] Is the success metric a behavior change (outcome KR) or an output (shipped feature)? (Metrics attribute)
- [ ] Did the brain write to `.planning/BRAIN-FEED-01-product.md` only? (Step 6 — Feed Write Scope)

Failing 3+ checklist items = Rating 2 regardless of content quality.
