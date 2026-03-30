# Brain #02-UX — Evaluation Criteria

## Purpose

This file defines how to evaluate Brain #2 (UX Research) responses against the Delta-Velocity Matrix. Use this file when rating a consultation output. The criteria are observable and domain-specific — not generic quality statements.

A response that "sounds UX-correct" but cannot be rated against this table is a Rating 2 at best.

---

## Rating 3 (Peer) vs Rating 4 (Senior)

| Attribute | Rating 3 (Peer) | Rating 4 (Senior) |
|-----------|-----------------|-------------------|
| **Cognitive load** | Correct layout and logical grouping — information is organized | Identifies Hick's Law violation (too many choices causing decision paralysis) or Miller's Law breach (>7 items in working memory without chunking) |
| **Navigation** | Suggests standard nav patterns (breadcrumbs, back button, tab bar) | Maps the exact user mental model — where the user expects to find things BEFORE looking, based on prior tool experience |
| **Feedback loops** | "Add a loading state" or "show a spinner" | Specifies exact timing thresholds: 100ms (immediate — no feedback needed), 1s (progress indicator), 10s (progress bar + cancel option) — and what feedback triggers at each |
| **Error recovery** | Adds an error message explaining what went wrong | Designs the full recovery path — how the user returns to the success state in ≤ 2 actions, including what the system does automatically |
| **War Room context** | Generic SaaS patterns that could apply to any dashboard | References specific War Room panels (Command Center, Nexus, Vault, Engine Room) by name and explains the panel-specific interaction constraints |

**Observable distinction:** A Rating 3 response describes a correct interaction. A Rating 4 response also explains why the user's mental model expects it, and what breaks if it's absent.

---

## Auto-Reject (Rating 1-2)

**Complexity Theater Trigger:**
Any response that suggests removing information density to "simplify" without measuring cognitive load impact = Complexity Theater = Rating < 3.

Complexity Theater is recommending visual simplification (fewer elements, less data, more whitespace) without evidence that the current design causes cognitive overload. War Room is density-first. Information that exists must be accessible. Removing information is only valid if the cognitive cost of the removed information is greater than the cognitive cost of hunting for it elsewhere.

**Generic SaaS Pattern Trigger:**
Any response that applies mobile-first or consumer SaaS patterns (bottom navigation, hamburger menus, swipe gestures, onboarding tours) to the War Room = context blindness = Rating 2 maximum.

---

## Rating 5 (Architect) Threshold

A Rating 5 response:
- Identifies a cognitive load violation that affects multiple War Room panels simultaneously — one fix that propagates across the entire tool
- Maps the user's complete mental model transition from one state to another, including the moments of disorientation and how to eliminate them
- Proposes a navigation architecture change that reduces time-to-insight across all 4 panels (not just the one in scope)
- Surfaces a non-obvious accessibility gap (colorblindness, keyboard-only flow, screen reader) that would block a class of developer users

Example Rating 5: "The current Command Center → Nexus transition requires 3 clicks because users must return to the nav bar. The mental model expects the active brain to serve as a navigation anchor — clicking a BrainNode in the Nexus should deep-link directly to its Command Center card. This one change would remove 2 clicks from the most frequent workflow across both panels."

---

## Minimum for Rating 3

A response must satisfy ALL of the following to be Rating 3:

1. References specific War Room panels by name (Command Center, The Nexus, Strategy Vault, Engine Room) — not generic "the dashboard" or "the interface"
2. Provides exact interaction specification (click path, timing, or state transition) — not vague descriptions like "make it more intuitive"
3. Includes feedback timing (at least one of: 100ms / 1s / 10s thresholds) for any interaction involving system response
4. Names the user's mental model explicitly — what prior experience is the user drawing on?
5. Respects the Stack Hard-Lock and desktop-first constraint (no mobile patterns, no CSS frameworks outside the stack)

If any of these are missing, the response is Rating 2 regardless of how UX-theoretically correct it sounds.

---

## Evaluation Checklist

When rating a Brain #2 response, verify:

- [ ] Did the brain read BRAIN-FEED.md before responding? (Step 1 — ask to show it)
- [ ] Does the `[IMPLEMENTED REALITY]` block include the 4 War Room panels and their current state? (Step 2)
- [ ] Are the 5 domain-specific `[CORRECTED ASSUMPTIONS]` present (especially desktop-first)? (Step 3)
- [ ] Does the recommendation specify which War Room panel(s) it affects? (War Room context attribute)
- [ ] Is feedback timing specified (100ms/1s/10s)? (Feedback loops attribute)
- [ ] Is the recovery path specified (≤ 2 actions back to success state)? (Error recovery attribute)
- [ ] Did the brain write to `.planning/BRAIN-FEED-02-ux.md` only? (Step 6 — Feed Write Scope)

Failing 3+ checklist items = Rating 2 regardless of content quality.
