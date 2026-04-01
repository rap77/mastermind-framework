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

---

## 2026-03-31 — Phase 12 (Parallel Dispatch + Command Update)

### Verified Insights

#### Question 1: brain_routing Edge Animation in The Nexus
**Decision: DEFERRED — surface in Engine Room log only**

Brain #3 query returned Option B (animate coordinator edges as relay). REJECTED after grep verification.

Reason for rejection:
- Current graph is star topology: coordinator → all brains. NO brain-to-brain edges exist (`buildBlueprintEdges` generates only coordinator→brain pairs).
- Option B (relay via coordinator) would require TWO sequential edge pulses — the relay is a lie; the actual routing is Brain #1 → Brain #4, not coordinator-mediated.
- Adding temporary `brain_routing` edges to the DAG violates the "nodes array is layout-only — never mutated by WS events" invariant in NexusCanvas.tsx (comment line 158).
- ICE re-scored: Impact 6 × Confidence 4 (implementation risk: graph mutation) / Effort 5 (edge lifecycle management + test coverage) = ICE 4.8 — BELOW the 15 threshold.

Correct minimal action: Add `brain_routing` as a loggable event in LiveLogPanel (Engine Room). The log message already has brain isolation (LogBadge) — zero new components needed. The Nexus already illuminates BrainNode status for both source and target brains via brainStore → that is sufficient orientation.

**Component: LiveLogPanel — subscribe to `brain_routing` WS events identically to `log:line`. Zero new components.**

#### Question 2: Brain Memory Panel (NodeDetailPanel Tab)
**Decision: APPROVED — NodeDetailPanel tab addition**

NodeDetailPanel is a shadcn Sheet. It currently has: Status, LastUpdated, Configuration section, "View YAML Config" button. No tabs exist yet.

Correct implementation path:
- Add `Tabs` from `@/components/ui/` (shadcn/ui — already used throughout; verify it exists before adding the import)
- Two tabs: "Details" (current content) | "Memory" (GET /api/experiences/{brain_id} list)
- Memory tab content: simple ordered list, newest first, text-xs font-mono text-muted-foreground — NO new component needed, inline in NodeDetailPanel
- The `Tabs` component is NOT in the current `components/ui/` directory (only button, card, dialog, input, sheet exist) — must be added via `pnpm dlx shadcn add tabs` before implementation
- ICE: structural decision, no animation — accessibility: memory entries are text-only, no color dependency

**Component to modify: NodeDetailPanel.tsx — add shadcn Tabs (must add primitive first)**

#### Question 3: BrainTile `routing_to` 5th State
**Decision: APPROVED WITH CORRECTION**

Brain's ICE score (24) accepted. However, corrected the animation class choice:
- Brain recommended `animate-pulse` for `routing_to` — REJECTED. `animate-pulse` is already used for `active` (BrainTile line 65). Two different states sharing the same animation = ambiguous feedback.
- Correct: `routing_to` = brief directional state (brain done, dispatching). Animation: NONE. Use border-only distinction.
- Classes: `opacity-100 border-amber-500/60 shadow-sm` — amber differentiates from blue (active) and green (complete). No animation = low cognitive noise.
- Secondary indicator: `ArrowRight` icon from lucide-react (already a dep — Check icon used at line 128 of BrainTile.tsx)
- Label text: "routing" — not "routing_to" (user-facing label, keep short)
- `NodeStatusIndicator` must also receive the new state — currently typed as `'blueprint' | BrainStatus`. `BrainStatus` is in brainStore.ts — that type must be extended.
- WCAG: amber border + ArrowRight icon + "routing" text label = triple redundancy — passes AA

**Components to modify: BrainTile.tsx + NodeStatusIndicator.tsx + brainStore.ts (BrainStatus type)**

### Deferred Items

- Brain-to-brain directed edges in The Nexus DAG (visualizing routing chains): deferred until graph is rebuilt as a general DAG (not star topology). At that point, brain_routing edges can be pre-built and state-toggled without graph mutation.
- Tabs primitive (`@/components/ui/tabs.tsx`) must be scaffolded before NodeDetailPanel Memory tab work begins. Track in Phase 12 task list.
