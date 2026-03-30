# BRAIN-FEED-02 — UX Research Domain Feed

> Written by Brain #2 (UX Research). Read-only for other agents.
> Orchestrator reads this after all domain feeds to write BRAIN-FEED.md (global synthesis).
> Last updated: 2026-03-28

---

## Strategic Anchors — v2.2 Foundation Facts

- War Room = IDE, not SaaS dashboard. Interaction model: developer-as-composer orchestrating agents, not consumer browsing a product.
- 4-panel layout locked (Command Center, The Nexus, Strategy Vault, Engine Room) — no panel additions without Phase N+1 PRD.
- ICE Scoring ≥ 15 for animations — proven in Phase 06. Below threshold = over-engineering.
- Efficiency > Learnability: Expert speed (Time-on-task) > new user success. No "onboarding tours" — those are SaaS patterns, not IDE patterns.
- High Information Density: Use Chunking (Miller's Law) to organize data, NOT "minimalism" that removes necessary context.
- Engine Status Feedback (H1): Every uv/pnpm action needs immediate visual feedback (loading states, mini-consolas) — close the Gulf of Evaluation.

---

## Migrated Patterns — from BRAIN-FEED.md Phase 00-09

- ICE Scoring prevents over-engineering — only implement animations with ICE ≥ 15 [Phase 06 — UX decision framework owner]

---

## SYNC Cross-References

[none — Brain #2 UX is the owner of ICE Scoring, not a consumer]

---

## 2026-03-29 — Brain Navigation Request (15-tab system rejected)

### Verified Insights

- **15-tab brain navigation = Hick's Law violation.** 15 equal-weight choices create scanning mode on every context switch. Decision time grows logarithmically — directly contradicts the keyboard-first, expert-speed mandate.
- **Tabs are the wrong affordance for brain context.** Tabs signify equivalent pages in horizontal relationship. In War Room, a brain is a DATA CONTEXT flowing into the 4 existing panels — not a destination. Using tabs misrepresents the affordance (Norman: Conceptual Model mismatch).
- **Command Center BentoGrid already IS the brain navigator.** Jakob's Law: users expect a central hub for selection (BentoGrid) + specialized views for execution (4 panels). Adding 15 tabs duplicates the BentoGrid role, creates H4 Consistency violation, and breaks the conceptual model.
- **Mapping conflict: 15 tabs vs. 24 brains.** If the BentoGrid shows 24, why are only 15 tab-worthy? This creates a Gulf of Execution — user doesn't know how to reach the other 9. This is a direct Norman signifier failure.
- **Correct pattern for expert brain-switching: Command Palette (Cmd+K).** Fuzzy search over brain name/niche. Zero scanning, keyboard-first, instantaneous. This is VS Code's Cmd+P pattern applied to the War Room context.
- **Secondary pattern if persistent nav is genuinely needed: MRU working set (<5 items).** Show only recently-used brains in a pinned strip — not all 15/24. Respects Miller's 4±1 working memory constraint.

### Deferred Items

- 📅 Command Palette (Cmd+K) for brain/niche search — Phase 12 candidate. Requires: fuzzy search over brains API response already in TanStack Query cache, no new API needed.
- 📅 MRU pinned-brain strip (<5 items) in global header — Phase 12 candidate, only if observational data shows users repeatedly switching between same 2-3 brains mid-session.
