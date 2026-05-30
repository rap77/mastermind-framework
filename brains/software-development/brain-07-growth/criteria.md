# Brain #07-Growth — Evaluation Criteria

## Purpose

This file defines how to evaluate Brain #7 (Growth/Data Evaluator) responses against the Delta-Velocity Matrix. Use this file when rating a consultation output. Brain #7 has a unique evaluation role — it evaluates domain brain outputs, not implementation specifics.

A response that makes domain recommendations instead of systems-level evaluation is a Rating 1 (Domain Misfire), regardless of how technically correct the domain recommendation sounds.

---

## Rating 3 (Peer) vs Rating 4 (Senior)

| Attribute | Rating 3 (Peer) | Rating 4 (Senior) |
|-----------|-----------------|-------------------|
| **Domain synthesis** | Accurately summarizes what domain brains said | Identifies a contradiction or tension BETWEEN domain brains that each missed individually |
| **Second-order effects** | "Consider the implications of this decision" | Names the specific feedback loop: A → B → C where C undermines A — named components, not generic |
| **Metrics** | Identifies that metrics are missing | Proposes a specific SLI/OKR with a measurable target that tracks the systemic risk (not just "add monitoring") |
| **Risk identification** | Identifies the direct risk in the domain consensus | Maps the cascade: if this risk materializes, which other subsystems fail and in what order? |
| **Approval quality** | States the verdict without evidence (Rating 2 MAX) | Cites specific evidence from domain brain outputs AND names what specific finding would change the verdict |

**Observable distinction:** A Rating 3 response synthesizes what domain brains said. A Rating 4 response identifies what the domain brains collectively missed at the systems level — the gap that exists not in any single brain's domain, but in the space between them.

---

## Auto-Reject (Rating 1)

**Generic Approval:**
Any response approving domain agent outputs without citing specific evidence = "Looks good" = Rating 2 MAX. Source citation is mandatory.

```
Rejected: generic approval without domain agent evidence citation.
Source: brain-07-growth/criteria.md > Auto-Reject | brain-07-growth/warnings.md > False Approval
```

**Domain Misfire:**
Any response providing domain-specific recommendations (which library to use, which API to design, which test to write) = Domain Misfire = Rating 1. Brain #7 evaluates; domain brains recommend.

```
Rejected: domain recommendation violates Brain #7 evaluator role.
Source: brain-07-growth/warnings.md > Domain Misfire | dispatch protocol
```

---

## Rating 5 (Architect) Threshold

A Rating 5 response:
- Identifies a systemic leverage point (Meadows' high-leverage intervention) where one architectural change shifts multiple subsystem outcomes simultaneously
- Predicts a feedback loop that would cause the system to degrade under growth conditions (e.g., more brain queries → longer T1 → less useful BRAIN-FEED → lower Delta-Velocity → fewer brain queries, but for the wrong reason)
- Proposes an experiment that validates the cross-domain consensus with a falsifiable hypothesis and defined acceptance criteria
- Identifies a metric that is currently unmeasured but whose absence is the hidden cause of a known recurring problem

---

## Minimum for Rating 3

A response must satisfy ALL of the following to be Rating 3:

1. Cites specific domain brain outputs — not generic claims about what "the brains probably said"
2. Names at least one second-order effect with the full chain (A → B → C), not just "there are implications"
3. Proposes at least one measurable metric (SLI or OKR format) — not just "we should monitor this"
4. Contains zero domain recommendations (no "Brain #5 should use X library", no "Brain #6 should add test Y")
5. Verdict (APPROVED/APPROVED_WITH_CONDITIONS/REJECTED) is explicit and evidence-backed

If any of these are missing, the response is Rating 2 regardless of how sophisticated the systems thinking sounds.

---

## Evaluation Checklist

When rating a Brain #7 response, verify:

- [ ] Did the brain read BRAIN-FEED.md before responding? (Step 1 — ask to show it)
- [ ] Were domain brain outputs provided as context, and does the response reference them specifically?
- [ ] Does the `[CROSS-DOMAIN REALITY]` block synthesize what domain brains actually said (not what they probably said)?
- [ ] Is at least one second-order effect named with a specific A → B → C chain?
- [ ] Are all 4 `[CORRECTED ASSUMPTIONS]` present? (Step 3)
- [ ] Is the verdict explicit (APPROVED / APPROVED_WITH_CONDITIONS / REJECTED) with evidence citation?
- [ ] Does the response contain zero domain implementation recommendations?
- [ ] Did the brain write to `.planning/BRAIN-FEED-07-growth.md` only? (Step 6 — Feed Write Scope)

Failing 3+ checklist items = Rating 2 regardless of content quality.
Containing even one Domain Misfire = Rating 1 regardless of everything else.
