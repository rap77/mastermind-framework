# Phase 17 Brain Consultation — Execution Framework

> **Generated:** 2026-04-09
> **Process:** Option D (File-based cross-brain communication)
> **Status:** Framework ready — Manual execution required

---

## Overview

This document provides the complete framework for consulting all 6 domain brains on Phase 17 plans 02-06. Each brain should read the plans, apply expert knowledge, and append their analysis to `17-BRAIN-OUTPUTS.md`.

## Brain Dispatch Matrix

| Brain # | Domain | Expertise | Output File |
|---------|--------|-----------|-------------|
| #1 | Product Strategy | Cagan, Torres, Ries, Doerr | `17-BRAIN-OUTPUTS.md` |
| #2 | UX Research | Norman, Nielsen, Hall | `17-BRAIN-OUTPUTS.md` |
| #3 | UI Design | Cooper, Wroblewski, Saffer | `17-BRAIN-OUTPUTS.md` |
| #4 | Frontend | Abramov, Markbåge, Florence | `17-BRAIN-OUTPUTS.md` |
| #5 | Backend | Fowler, Evans, Hohpe | `17-BRAIN-OUTPUTS.md` |
| #6 | QA/DevOps | Humble, Forsgren, Feathers | `17-BRAIN-OUTPUTS.md` |

---

## Brain #1: Product Strategy

### Evaluation Criteria

**1. User Value**
- Does each plan deliver clear, measurable user value?
- Is the value proposition compelling for enterprise users?
- Are we solving real pain points or nice-to-haves?

**2. Prioritization**
- Are the 5 plans in the right order for time-to-value?
- Should we reorder based on user impact vs. effort?
- Are there any missing high-value features?

**3. Outcomes vs. Outputs**
- Do success criteria focus on outcomes (behavior change) or outputs (features shipped)?
- Are we measuring the right metrics (onboarding completion, cost reduction, etc.)?

**4. Risk Assessment**
- Are risks real or perceived?
- Do rollback plans make sense from product perspective?
- Are we over-investing in low-impact areas?

### Key Questions

- **17-02 (Company Switcher):** Is multi-tenancy a must-have or nice-to-have for MVP?
- **17-03 (ActiveAgentsPanel):** 24-brain display = information overload? Hick's Law violation?
- **17-04 (Cost Dashboard):** Is cost tracking a core job-to-be-done or secondary feature?
- **17-05 (Command Palette):** Cmd+K discoverable or requires training?
- **17-06 (Onboarding):** 4-step wizard too long? Expect >20% drop-off?

### Output Format

```markdown
## Brain #1 (Product Strategy) Output

### Executive Summary
[2-3 sentences on overall product health]

### Plan-by-Plan Analysis

#### Plan 17-02: Multi-tenant Company Switcher
**User Value:** [Clear/Weak/Missing — explain why]
**Prioritization:** [Right order/Should be earlier/Should be later]
**Success Criteria:** [Outcome-focused/Output-focused — suggest fixes]
**Recommendations:** [Specific changes to PLAN.md]

[Repeat for 17-03, 17-04, 17-05, 17-06]

### Cross-Plan Concerns
- **Missing:** [What's missing from product perspective?]
- **Over-investment:** [Are we over-building anything?]
- **Sequence Issues:** [Should plans be reordered?]

### Product Score: [X/100]
**Rationale:** [Why this score?]

### Must-Fix Changes (Before Brain #7)
1. [Specific change to specific PLAN.md]
2. [Another must-fix]
3. [Third must-fix]
```

---

## Brain #2: UX Research

### Evaluation Criteria

**1. Cognitive Load**
- 24-brain display = information overload? Hick's Law violation?
- Progressive disclosure applied correctly?
- Density modes address different user expertise levels?

**2. Usability**
- Mobile gestures (swipe, pull-to-refresh) — discoverable or hidden?
- Keyboard shortcuts — learnable or require training?
- Command palette categories — match mental models?

**3. Accessibility**
- WCAG 2.1 AA compliance realistic for MVP?
- Screen reader announcements — too noisy vs. informative?
- Touch targets ≥ 44x44px — sufficient for mobile gestures?

**4. Mobile-First**
- Bottom nav vs. hamburger menu — right choice for enterprise app?
- Swipe gestures — conflict with browser navigation?
- Responsive breakpoints — tested on real devices?

### Key Questions

- **17-02 (Company Switcher):** Drag-and-drop discoverable? Visual affordances clear?
- **17-03 (ActiveAgentsPanel):** 24 status badges scannable? Group by domain (Strategy, UX, UI, etc.)?
- **17-04 (Cost Dashboard):** QuotaBar color coding universal? Green/Yellow/Red culturally dependent?
- **17-05 (Command Palette):** 4 categories match mental models? Fuzzy search handles typos gracefully?
- **17-06 (Onboarding):** 4 steps too many? Reduce to 3? Skip button prominent?

### Output Format

```markdown
## Brain #2 (UX Research) Output

### Executive Summary
[2-3 sentences on overall UX health]

### Plan-by-Plan Analysis

#### Plan 17-02: Multi-tenant Company Switcher
**Cognitive Load:** [Acceptable/Overwhelming — why?]
**Discoverability:** [Drag-and-drop discoverable?]
**Mobile Concerns:** [Status badges readable on mobile?]
**Recommendations:** [Specific UX improvements]

[Repeat for 17-03, 17-04, 17-05, 17-06]

### Critical UX Issues
1. **[Issue Title]** — [Why critical, how to fix]
2. **[Issue Title]** — [Why critical, how to fix]
3. **[Issue Title]** — [Why critical, how to fix]

### UX Score: [X/100]
**Rationale:** [Why this score?]

### Must-Fix Changes (Before Brain #7)
1. [Specific UX improvement to specific PLAN.md]
2. [Another must-fix]
3. [Third must-fix]
```

---

## Brain #3: UI Design

### Evaluation Criteria

**1. Component Architecture**
- Atomic design applied? (atoms → molecules → organisms)
- 5-state system defined for all interactive components?
- Component reuse across plans or duplicate work?

**2. Visual Design**
- OKLCH color system applied consistently?
- Typography hierarchy defined?
- Spacing system (4px grid) followed?

**3. Accessibility (Visual)**
- WCAG 2.1 AA compliance realistic?
- Focus visible states defined for all interactive elements?
- Color contrast ratios met (4.5:1 for text, 3:1 for large)?

**4. Responsive Design**
- Mobile-first approach or desktop-first?
- Breakpoints defined (320px, 768px, 1920px)?
- Component variants per breakpoint (compact/normal/detailed)?

### Key Questions

- **17-02 (Company Switcher):** Drag states defined? Visual feedback during drag?
- **17-03 (ActiveAgentsPanel):** Ping animation performance impact? Respect `prefers-reduced-motion`?
- **17-04 (Cost Dashboard):** MetricCard/QuotaBar reusable? Color + icons (not color alone)?
- **17-05 (Command Palette):** shadcn/ui Dialog sufficient? Focus trap defined?
- **17-06 (Onboarding):** Progress indicator clear? Validation errors visible?

### Output Format

```markdown
## Brain #3 (UI Design) Output

### Executive Summary
[2-3 sentences on overall UI design health]

### Plan-by-Plan Analysis

#### Plan 17-02: Multi-tenant Company Switcher
**Component Hierarchy:** [Atomic design applied?]
**Visual Feedback:** [Drag states defined?]
**Accessibility:** [Focus states on drag handles?]
**Recommendations:** [Component improvements]

[Repeat for 17-03, 17-04, 17-05, 17-06]

### Component Architecture Concerns
1. **[Concern]** — [Why concerning, how to fix]
2. **[Concern]** — [Why concerning, how to fix]
3. **[Concern]** — [Why concerning, how to fix]

### Design System Gaps
- **Missing Components:** [What needs to be built?]
- **Inconsistent Patterns:** [Where do plans conflict?]
- **Reusable Opportunities:** [What should be shared across plans?]

### UI Design Score: [X/100]
**Rationale:** [Why this score?]

### Must-Fix Changes (Before Brain #7)
1. [Specific UI improvement to specific PLAN.md]
2. [Another must-fix]
3. [Third must-fix]
```

---

## Brain #4: Frontend

### Evaluation Criteria

**1. State Management**
- 3 new stores (layoutStore, companyStore, costStore) sufficient?
- Store design follows Zustand best practices?
- Immer middleware needed or overkill?

**2. Performance**
- RAF batching plan realistic for 24-brain burst?
- React.memo, useDeferredValue applied correctly?
- WebSocket integration scalable (1000s of updates)?

**3. React Patterns**
- Client Components marked with 'use client'?
- Server Components opportunities missed?
- Component composition over prop drilling?

**4. Testing Strategy**
- Unit + Integration + E2E sufficient?
- Performance testing (RAF) realistic?
- Visual regression baseline process defined?

### Key Questions

- **17-02 (Company Switcher):** @dnd-kit vs React Flow DnD? Cross-tab sync race conditions?
- **17-03 (ActiveAgentsPanel):** P99 < 16.67ms realistic? 24-brain burst flood wsDispatcher?
- **17-04 (Cost Dashboard):** startTransition sufficient for cost burst? WebSocket → Store → Component efficient?
- **17-05 (Command Palette):** Custom fuzzy search vs fuse.js? Global listener cleanup risk?
- **17-06 (Onboarding):** onboardingStore needed or URL params suffice? Form validation client-only or server?

### Output Format

```markdown
## Brain #4 (Frontend) Output

### Executive Summary
[2-3 sentences on overall frontend architecture health]

### Plan-by-Plan Analysis

#### Plan 17-02: Multi-tenant Company Switcher
**State Management:** [companyStore design sound?]
**Drag-and-Drop:** [@dnd-kit vs React Flow DnD?]
**Cross-Tab Sync:** [localStorage events race condition risk?]
**Recommendations:** [Frontend architecture improvements]

[Repeat for 17-03, 17-04, 17-05, 17-06]

### Frontend Architecture Concerns
1. **[Concern]** — [Why concerning, how to fix]
2. **[Concern]** — [Why concerning, how to fix]
3. **[Concern]** — [Why concerning, how to fix]

### Performance Risks
- **RAF Batching:** [Will P99 < 16.67ms hold? Suggest monitoring]
- **WebSocket Flood:** [24-brain burst flood backend? Suggest throttling]
- **Bundle Size:** [New components increase bundle? Suggest code splitting]

### Frontend Score: [X/100]
**Rationale:** [Why this score?]

### Must-Fix Changes (Before Brain #7)
1. [Specific frontend improvement to specific PLAN.md]
2. [Another must-fix]
3. [Third must-fix]
```

---

## Brain #5: Backend

### Evaluation Criteria

**1. API Design**
- X-Tenant-ID header sufficient for multi-tenancy?
- REST + WebSocket hybrid approach sound?
- Event sourcing (Rust) integration plan realistic?

**2. Scalability**
- WebSocket Hub (Rust) handle 24-brain burst?
- Cost dashboard queries (activity_log) performant?
- Tenant isolation enforced at API layer?

**3. Data Consistency**
- Company state sync (localStorage) vs server truth?
- Cost metrics (Rust event sourcing) vs client cache?
- Cross-tab sync race conditions?

**4. Security**
- Tenant isolation (X-Tenant-ID) spoofable?
- JWT validation (tenant_id claim) sufficient?
- API key storage (onboarding) secure?

### Key Questions

- **17-02 (Company Switcher):** Server validates tenant_id belongs to user? X-Tenant-ID spoofable?
- **17-03 (ActiveAgentsPanel):** Rust Hub handle 24-brain burst? Push vs polling tradeoff?
- **17-04 (Cost Dashboard):** activity_log aggregation performant? WebSocket push flood risk?
- **17-05 (Command Palette):** New endpoints needed? Brain trigger idempotent?
- **17-06 (Onboarding):** API key storage secure? Company creation idempotent?

### Output Format

```markdown
## Brain #5 (Backend) Output

### Executive Summary
[2-3 sentences on overall backend architecture health]

### Plan-by-Plan Analysis

#### Plan 17-02: Multi-tenant Company Switcher
**Tenant Isolation:** [X-Tenant-ID header sufficient?]
**API Validation:** [Server validates tenant_id belongs to user?]
**Cross-Tab Sync:** [localStorage vs server truth conflict?]
**Recommendations:** [Improve tenant isolation]

[Repeat for 17-03, 17-04, 17-05, 17-06]

### Backend Architecture Concerns
1. **[Concern]** — [Why concerning, how to fix]
2. **[Concern]** — [Why concerning, how to fix]
3. **[Concern]** — [Why concerning, how to fix]

### Scalability Risks
- **WebSocket Flood:** [24-brain burst flood Rust Hub? Suggest throttling]
- **Cost Queries:** [activity_log aggregation slow? Suggest caching]
- **Tenant Isolation:** [X-Tenant-ID spoofable? Suggest validation]

### Backend Score: [X/100]
**Rationale:** [Why this score?]

### Must-Fix Changes (Before Brain #7)
1. [Specific backend improvement to specific PLAN.md]
2. [Another must-fix]
3. [Third must-fix]
```

---

## Brain #6: QA/DevOps

### Evaluation Criteria

**1. Testing Strategy**
- Unit + Integration + E2E sufficient coverage?
- Performance testing (RAF validation) realistic?
- Mobile testing (BrowserStack) plan executable?

**2. Quality Gates**
- axe-core CI/CD pipeline defined?
- Visual regression baseline capture process?
- RAF validation (P99 < 16.67ms) automated?

**3. Mobile Testing**
- BrowserStack ($39/month) commitment justified?
- Physical device testing included or emulators only?
- Touch response time (< 100ms) measurable?

**4. Accessibility Testing**
- WCAG 2.1 AA audit automated or manual?
- Keyboard navigation testable via Playwright?
- Screen reader testing (NVDA, VoiceOver) in CI?

### Key Questions

- **17-02 (Company Switcher):** Drag-and-drop testable via Playwright? Cross-tab sync testable?
- **17-03 (ActiveAgentsPanel):** RAF validation plan realistic? BrowserStack swipe gestures testable?
- **17-04 (Cost Dashboard):** WebSocket updates testable? 24-brain cost burst measurable?
- **17-05 (Command Palette):** Keyboard navigation testable? Visual regression baseline captured?
- **17-06 (Onboarding):** E2E test wizard completion? Mobile form inputs testable on real devices?

### Output Format

```markdown
## Brain #6 (QA/DevOps) Output

### Executive Summary
[2-3 sentences on overall testing strategy health]

### Plan-by-Plan Analysis

#### Plan 17-02: Multi-tenant Company Switcher
**Testing Coverage:** [Unit + Integration + E2E sufficient?]
**Drag-and-Drop:** [Testable via Playwright?]
**Cross-Tab Sync:** [Testable with 2 browser contexts?]
**Recommendations:** [Improve test coverage]

[Repeat for 17-03, 17-04, 17-05, 17-06]

### Testing Strategy Gaps
1. **[Gap]** — [What's missing, how to fix]
2. **[Gap]** — [What's missing, how to fix]
3. **[Gap]** — [What's missing, how to fix]

### Quality Gates Missing
- **Automated Tests:** [What's not automated?]
- **Performance Tests:** [RAF validation in CI?]
- **Accessibility Tests:** [axe-core in CI/CD?]
- **Mobile Tests:** [BrowserStack in CI?]

### QA Score: [X/100]
**Rationale:** [Why this score?]

### Must-Fix Changes (Before Brain #7)
1. [Specific QA improvement to specific PLAN.md]
2. [Another must-fix]
3. [Third must-fix]
```

---

## Cross-Brain Consolidation

After all 6 brains have appended their outputs to `17-BRAIN-OUTPUTS.md`, create a summary:

```markdown
# Phase 17 Brain Consultation Summary

> **Generated:** [Date]
> **Brains Consulted:** 6/6
> **Process:** Option D (File-based cross-brain communication)

---

## Brain-by-Brain Scores

| Brain # | Domain | Score | Key Concerns |
|---------|--------|-------|--------------|
| #1 | Product Strategy | [X/100] | [Top 3 concerns] |
| #2 | UX Research | [X/100] | [Top 3 concerns] |
| #3 | UI Design | [X/100] | [Top 3 concerns] |
| #4 | Frontend | [X/100] | [Top 3 concerns] |
| #5 | Backend | [X/100] | [Top 3 concerns] |
| #6 | QA/DevOps | [X/100] | [Top 3 concerns] |

**Overall Phase 17 Score:** [Average of all 6 scores]/100

---

## Cross-Brain Consensus

### Where Brains Agree
- **[Agreement 1]** — [Which brains agree? Why important?]
- **[Agreement 2]** — [Which brains agree? Why important?]
- **[Agreement 3]** — [Which brains agree? Why important?]

### Where Brains Disagree
- **[Disagreement 1]** — [Brain A says X, Brain B says Y. Resolution?]
- **[Disagreement 2]** — [Brain A says X, Brain B says Y. Resolution?]
- **[Disagreement 3]** — [Brain A says X, Brain B says Y. Resolution?]

---

## Plan Improvements Required

### Plan 17-02: Multi-tenant Company Switcher
**Product Changes:** [From Brain #1]
**UX Changes:** [From Brain #2]
**UI Changes:** [From Brain #3]
**Frontend Changes:** [From Brain #4]
**Backend Changes:** [From Brain #5]
**QA Changes:** [From Brain #6]

### Plan 17-03: ActiveAgentsPanel
[Same structure]

### Plan 17-04: Cost Dashboard
[Same structure]

### Plan 17-05: Command Palette
[Same structure]

### Plan 17-06: Onboarding Wizard + Mobile Polish
[Same structure]

---

## New Risks Identified

1. **[Risk Title]** — [Severity: High/Medium/Low] — [Which brain identified?]
2. **[Risk Title]** — [Severity: High/Medium/Low] — [Which brain identified?]
3. **[Risk Title]** — [Severity: High/Medium/Low] — [Which brain identified?]

---

## Next Steps

1. ✅ Review all brain outputs in `17-BRAIN-OUTPUTS.md`
2. ⏭️ Apply brain recommendations to each PLAN.md
3. ⏭️ Re-run Brain #7 validation on updated plans
4. ⏭️ Execute Phase 17 via `/mm:execute-phase 17`

---

**Status:** Ready for Brain #7 validation after plan improvements applied.
```

---

## Manual Execution Instructions

Since the brain agents are not directly invocable via the Agent tool, follow these steps:

1. **For Each Brain (#1-#6):**
   - Copy the brain's prompt from this document
   - Read all 6 Phase 17 plans (17-02 through 17-06)
   - Read 17-CONTEXT.md
   - Apply expert knowledge from referenced experts
   - Append analysis to `.planning/phases/17-ui-evolution/17-BRAIN-OUTPUTS.md`

2. **After All 6 Brains Complete:**
   - Read `17-BRAIN-OUTPUTS.md`
   - Create cross-brain summary (use template above)
   - Apply brain recommendations to each PLAN.md
   - Run Brain #7 validation

3. **Quality Checks:**
   - Each brain MUST append to `17-BRAIN-OUTPUTS.md` (don't overwrite)
   - Each brain MUST provide specific PLAN.md improvements (not generic advice)
   - Each brain MUST give a score (X/100) with rationale
   - Each brain MUST list 3 must-fix changes

---

**Created:** 2026-04-09
**Ready for:** Manual brain consultation or automated execution when brain agents are available
