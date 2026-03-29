# BRAIN-FEED-03 — UI Design Domain Feed

> Written by Brain #3 (UI Design). Read-only for other agents.
> Orchestrator reads this after all domain feeds to write BRAIN-FEED.md (global synthesis).
> Last updated: 2026-03-28

---

## Design System (OKLCH + Nova Preset)

- Perceptual Uniformity: All color tokens via OKLCH → WCAG 2.1 AA auto-compliance (confirmed in globals.css)
- 3-Tier Token Architecture: Global → Semantic → Component (e.g., color-action-primary → brain-tile-border)
- Dark Mode Desaturation: Brand colors desaturated in dark mode, background #121212 (never #000000)
- Anti-pattern: Hardcoded hex values → use tokens only

---

## Component Patterns (Atomic Design)

- BrainTile = Molecule, BentoGrid = Organism/Template
- Rule of 5 States: Every component MUST define Default, Hover, Active, Disabled, Error/Loading
- Layout Grid: Command Center aligns to 8px baseline + 12-column system (breaking grid = functional narrative choice, not whim)
- Touch Targets: Mobile Nexus = 44x44px minimum hit area

---

## Animation (Beyond ICE ≥ 15)

- Functional Purpose: Every animation serves Orientation, Feedback, Continuity, or Narrative — no "noise"
- Duration Standards: Micro-interactions 100-300ms, Modal/Canvas 300-600ms
- Easing Invariant: Never linear — use physically-inspired easing (ease-out entrance, ease-in exit)
- Accessibility: prefers-reduced-motion support mandatory (high-risk = >25% screen coverage)

---

## WCAG 2.1 AA Hard Floor

- No Color Only: ICE scores and errors MUST include icon or text (8% daltonism users)
- Focus Ring Invariant: outline: none forbidden unless replaced by custom 3:1 focus-visible ring
- Prohibited: Using placeholders as labels, truncating Y-axis in charts

---

## SYNC Cross-References

Sync: ICE Scoring animation threshold — [SYNC: BF-02-001] → BRAIN-FEED-02-ux.md > Strategic Anchors. ICE ≥ 15 required before recommending any animation. Brain #2 UX owns the decision. Owner: Brain #2 UX.
