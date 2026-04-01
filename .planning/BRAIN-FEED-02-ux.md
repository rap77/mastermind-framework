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

---

## 2026-03-31 — Autonomous Agent Architecture Evaluation (v3.0 direction)

### Verified Insights

- **Mental Model Shift: "Invoke → Await" to "Trigger → Observe Chain".** This is a Norman conceptual model change, not just a feature addition. The War Room UI must expose the reasoning path — not just that Brain #4 is running, but *why* (Brain #1 detected frontend_implications). Without this, the Gulf of Evaluation widens: user sees motion but cannot close the feedback loop.

- **HybridFlowEdge already handles the brain_routing signal — no new component needed.** Edge state machine (idle/active/complete/error) reads from brainStore on every render. When brain_routing WebSocket event updates source brain status to 'active', edges in the Nexus animate automatically. ICE check: this is orientation (user understands which branch is executing live) — ICE >= 15 confirmed. NOT decoration.

- **brain_routing is a new WS event type — wsStore.subscribe() already supports arbitrary event types.** The routing signal surfaces in The Nexus only (DAG is the correct affordance for directional flow). Command Center BrainTiles show individual brain status (already works). No new subscriber architecture needed, only new event type registration.

- **Strategy Vault owns brain experiences (GET /api/experiences/{brain_id}).** It already owns execution history (GET /api/executions/history). Mental model: Vault = "what the system knows and has done." Adding experiences is additive, not a panel redesign. Progressive disclosure: BrainTile hover/click can surface a memory count badge, but the full experience log belongs in the Vault.

- **Focus Mode anxiety management for multi-minute chains.** Current isFocusMode activates on task start, deactivates on complete. With chained agents, "complete" may not arrive for 2-5 minutes. Missing feedback pattern: a Chain Progress indicator showing "Brain 2 of 4 — Frontend Analysis" uses the Zeigarnik Effect (incomplete task stays salient) and prevents anxiety from silence. This is NOT an animation — it is functional status text.

- **Routing transparency rule: label the WHY, not just the WHAT.** When brain_routing fires, the system must surface "Brain #4 dispatched — frontend_implications detected in Brain #1 output." This text belongs in the Engine Room LiveLogPanel (already has live log infrastructure). The Nexus shows it visually; the Engine Room shows it textually. Two-channel feedback = expert confidence.

### Deferred Items

- 📅 Chain Progress bar/breadcrumb (Zeigarnik pattern) in Command Center header — Phase 12/v3.0 candidate. Required state: orchestratorStore extended with chainSteps: Step[] where Step = {brainId, label, status}. No backend contract change needed if brain_routing events include step sequence.
- 📅 BrainTile memory count badge (progressive disclosure for experiences) — Phase 12/v3.0 candidate. Source: GET /api/experiences/{brain_id} count field. Max 1 API call per brain on hover (TanStack Query cache, staleTime 30s covers session).
- 📅 "Routing reason" label on Nexus edges — show the implication type (frontend/backend/ux) on the animated edge — Phase 12/v3.0 candidate. Requires: React Flow edge data prop + HybridFlowEdge extended to render an SVG foreignObject label.
