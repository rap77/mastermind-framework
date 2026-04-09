# Brain #2 (UX Research) — Phase 17 Consultation

> **Phase:** 17 — UI Evolution
> **Date:** 2026-04-08
> **Expertise:** UX patterns, information architecture, interaction design, Miller's Law, Hick's Law, ICE Scoring

---

## Verified Insights

**From existing codebase + BRAIN-FEED-02:**
- 4 production screens already working (Command Center, Nexus, Vault, Engine Room)
- BrainTile ping animation exists (ICE Score ≥ 15 validated in Phase 06)
- ICE Scoring framework prevents over-engineering — only implement animations with ICE ≥ 15
- 15-tab brain navigation was REJECTED (Hick's Law violation) — Command Palette (Cmd+K) approved instead
- Miller's Law: 7±2 chunks maximum — 24 brains must be chunked to avoid cognitive overload
- CLI-based onboarding = REAL problem for non-technical users (validated via Paperclip research)
- Dual onboarding paths APPROVED (visual for business, CLI for technical)
- WebSocket infrastructure already exists (wsDispatcher.ts + brainStore RAF batching)

---

## Recommended Approach

### UIE-01 (Three-Column Layout)

**Information Architecture:**
```
┌─────────────┬─────────────────┬──────────────────────────┐
│ CompanyRail │    Sidebar      │       Content Area       │
│ (180px)     │    (240px)      │       (flex-fill)        │
│             │                 │                          │
│ PURPOSE:    │ PURPOSE:        │ PURPOSE:                 │
│ Multi-tenant │ Navigation      │ Page content +           │
│ context      │ (4 screens)     │ Properties panel         │
│             │                 │                          │
│ CHUNKS:     │ CHUNKS:         │ CHUNKS:                  │
│ - Company   │ - Command       │ - Dynamic (varies)       │
│   list      │   Center (1)    │ - Maximum 7 items visible │
│   (max 7)   │ - Nexus (1)     │   (Miller's Law)         │
│ - Add btn   │ - Vault (1)     │ - Progressive disclosure │
│             │ - Engine (1)    │   for complexity         │
└─────────────┴─────────────────┴──────────────────────────┘
```

**Progressive Disclosure Strategy:**
- **Desktop:** All 3 columns visible by default (expert users see everything)
- **Mobile:** Single column with bottom nav (4 items only — Hick's Law compliance)
- **Collapse behavior:** Each column collapses independently (user control, not forced)

**Multi-tenant Switcher UX:**
- CompanyRail shows max 7 companies (Miller's Law: 7±2)
- "Show all" button reveals remaining companies (progressive disclosure)
- Active company highlighted with visual indicator (border + icon)
- Company status badges: live agents count, unread notifications (contextual info)

**Mobile Responsive Strategy:**
- **Bottom nav:** 4 items only (Command Center, Nexus, Vault, Engine Room)
- **Swipe gestures:** Horizontal swipe to switch between screens (natural mobile pattern)
- **Full-screen content:** Back button for navigation depth (consistent with mobile OS patterns)
- **Company rail:** Hidden on mobile — move to settings or profile menu

**ICE Score for layout transitions:**
- Impact: 4 (user orientation — knowing which column is which)
- Confidence: 5 (well-established pattern)
- Effort: 3 (CSS transitions only)
- **ICE: 6.7** — BELOW 15 threshold → NO animation for collapse/expand
- **Decision:** Instant width change (200ms CSS transition max for usability, not "animation")

---

### UIE-02 (Real-time Agent Monitoring)

**The Problem:** 24 brains > Miller's Law (7±2 chunks) → cognitive overload guaranteed

**Solution: Density Modes + Progressive Disclosure**

**Density Modes (when to use each):**
1. **Compact Mode (default for 24 brains):**
   - Shows: Brain name + status badge only (2 data points)
   - Use case: Monitoring 24 brains simultaneously
   - Layout: Grid view (4-6 columns, responsive)

2. **Normal Mode (click to expand):**
   - Shows: Brain name + status + last result + duration (4 data points)
   - Use case: Focusing on subset of brains
   - Layout: Card view (2-3 columns)

3. **Detailed Mode (drill-down):**
   - Shows: All metrics + transcript + cost breakdown (8+ data points)
   - Use case: Investigating specific brain execution
   - Layout: Single brain full-screen or modal

**Status Badge System (visual hierarchy):**
| Status | Icon | Color | Meaning |
|--------|------|-------|---------|
| idle | Circle | Gray (muted) | Ready to run |
| running | Spinner | Blue (primary) | Currently executing |
| completed | Check | Green (success) | Finished successfully |
| failed | X | Red (error) | Error occurred |
| routing | Arrow | Amber (warning) | Dispatching to next brain |

**Ping Animation (ICE Score):**
- **Purpose:** Orientation (user sees which brains just received updates)
- **Impact:** 8 (critical for real-time monitoring — without it, users can't track changes)
- **Confidence:** 5 (proven in existing BrainTile component)
- **Effort:** 2 (reuse existing ping animation from BrainTile)
- **ICE: 20** — ABOVE 15 threshold → APPROVED
- **Implementation:** Reuse `animate-ping` from BrainTile.tsx line 65

**Chunking Strategy for 24 Brains:**
1. **Auto-group by niche:** 4-6 niches (e.g., "Product", "Frontend", "Backend", "Growth")
2. **Search/filter:** Command Palette for fuzzy search over brain names
3. **MRU (Most Recently Used):** Show top 5 brains first (temporal locality)
4. **Active group:** Only show brains running in current session (reduces 24 → ~3-5)

---

### UIE-03 (Cost Dashboard)

**Cognitive Load Prevention:**
- **Default view:** 3-5 key metrics only (Miller's Law: 7±2, aim for lower bound)
- **Progressive disclosure:** "Show details" button reveals full breakdown
- **Color semantics:** Green (within budget), Amber (warning > 80%), Red (over budget)

**QuotaBar Pattern (progress visualization):**
- **Primary metric:** % of budget consumed (e.g., "78% of monthly allocation")
- **Visual:** Horizontal bar with color gradient (green → amber → red)
- **Secondary text:** "$X of $Y spent" (absolute values for precision)
- **Tertiary text:** "Z days remaining" (temporal context)

**MetricCard Hierarchy (what matters most):**
1. **P0 (always visible):** Total cost this month, budget remaining
2. **P1 (default visible):** Cost per brain (top 5 by spend), projected overage
3. **P2 (on demand):** Cost per execution, cost per token provider, trends over time

**Cost Alert UX:**
- **Warning threshold:** 80% of budget (Amber color, non-dismissable notification)
- **Critical threshold:** 100% of budget (Red color, requires acknowledgement)
- **Enforcement:** Stop new executions when budget exceeded (hard stop with override option)

---

## Anti-patterns to Avoid

### UX Violations:
- ❌ **Show all 24 brains at once** — Miller's Law violation, guaranteed cognitive overload
- ❌ **15-tab navigation** — Hick's Law violation, rejected in Phase 12
- ❌ **Animated layout transitions** — ICE Score 6.7 < 15, over-engineering
- ❌ **Desktop-only design** — Mobile responsiveness is required, not optional
- ❌ **No progressive disclosure** — Information dumping creates Gulf of Execution
- ❌ **Color-only status indicators** — 8% daltonism users can't distinguish
- ❌ **No density modes** — One-size-fits-all fails for both novice and expert users

### Mobile Anti-patterns:
- ❌ **Hamburger menu** — Hidden affordance, extra tap required
- ❌ **More than 5 bottom nav items** — Touch targets too small (< 44x44px)
- ❌ **No swipe gestures** — Forces users to tap back button repeatedly

---

## ICE Scoring

**APPROVED Animations (ICE ≥ 15):**
1. **Ping animation for status updates** — ICE 20 (orientation for real-time monitoring)
2. **Status badge transitions** — ICE 16 (feedback for state changes)
   - Impact: 6 × Confidence: 4 / Effort: 1.5 = 16

**REJECTED Animations (ICE < 15):**
1. **Layout collapse/expand** — ICE 6.7 (below threshold, use instant CSS transition)
2. **Company rail reordering** — ICE 8 (below threshold, instant move is fine)

---

## Deferred Items

**Deferred to Phase 18+ (Multi-channel Gateway):**
- Mobile push notifications for brain completion
- Voice command integration
- Touch gestures beyond swipe (pinch-to-zoom, long-press context menus)

**Deferred to Phase 19+ (Future enhancements):**
- Advanced filtering (by brain type, by niche, by date range)
- Custom dashboard layouts (drag-and-drop widget arrangement)
- Cost anomaly detection (ML-based outlier alerts)

---

## Testing Recommendations

### Usability Testing:
1. **Paper prototype validation** — Test layout with 5 users before coding
   - Task: "Find the brain that just failed"
   - Success rate: > 80% required
   - Time-to-success: < 5 seconds required

2. **A/B test for density modes** — Compact vs Normal vs Detailed
   - Metric: Time-to-find-information
   - Target: Compact mode ≤ 3s, Normal mode ≤ 5s, Detailed mode ≤ 10s

3. **Mobile usability testing** — Swipe gestures + bottom nav
   - Task: "Navigate from Command Center to Engine Room"
   - Success rate: > 90% required (mobile users expect swipe)

4. **Cognitive load measurement** — 24 brains monitoring
   - Method: NASA-TLX questionnaire after 5-minute monitoring session
   - Target: < 60/100 (moderate load, not high)

### Performance Metrics:
- **Time-to-first-render:** Layout should render in < 100ms (60fps = 16.67ms per frame)
- **Layout state persistence:** localStorage read/write in < 10ms
- **Density mode switch:** < 50ms (instant perception)

---

## Open Questions Answered

### Q4: Onboarding skip flow — Can users skip? What's minimal setup?

**Answer:** YES, users can skip onboarding, BUT with trade-offs:

**Skip Path:**
- User clicks "Skip" → Go directly to Command Center
- Default company created: "My First Company" (placeholder name)
- Zero brains configured → User must manually configure each brain
- **Rationale:** Respect user autonomy (H7: Flexibility and efficiency)

**Minimal Setup (5 minutes):**
1. Company name (required)
2. Select 1-3 brains to enable (default: all disabled)
3. Set monthly budget (default: $10 free tier)
4. Skip optional steps (template gallery, advanced config)

**Full Setup (15 minutes):**
- All minimal steps PLUS
- Template gallery selection
- Knowledge base upload (PDF, URL, text)
- Advanced config (timeouts, retries)

**Progressive Disclosure:**
- Show "Setup incomplete" badge if user skipped
- Offer "Complete setup" action in Command Center
- Don't block functionality, but surface setup option proactively

### Q5: Mobile bottom nav — Which sections to include?

**Answer:** 4 items only (Hick's Law compliance):

1. **Command Center** (BentoGrid) — Home screen, brain execution
2. **The Nexus** (Orchestration canvas) — Visual DAG
3. **Strategy Vault** (Execution history) — Past runs
4. **Engine Room** (Settings/API keys) — Configuration

**Rationale:**
- 4 items = well below Hick's Law limit (log₂(4) = 2 bits of info, optimal)
- Matches desktop navigation exactly (consistency: H4)
- All 4 screens are high-value (none are "nice-to-have")

**Excluded from mobile:**
- CompanyRail (move to profile/settings menu)
- Properties panel (show as modal/sheet instead)
- Cost dashboard (integrate into Strategy Vault as tab)

**Mobile Nav Layout:**
```
┌─────────────────────────────────────┐
│         [Content Area]              │
│                                     │
│         (scrollable)                │
│                                     │
├─────────────────────────────────────┤
│ [🎯] [🕸️] [📜] [⚙️] │  ← Bottom nav
│ Center  Nexus  Vault  Engine       │
└─────────────────────────────────────┘
```

---

## Summary

**Key Decisions:**
1. **Three-column layout:** Instant transitions (no animation, ICE 6.7 < 15)
2. **24-brain monitoring:** Density modes (compact/normal/detailed) + chunking by niche
3. **Ping animation:** APPROVED (ICE 20 ≥ 15)
4. **Mobile bottom nav:** 4 items only (Hick's Law compliance)
5. **Onboarding skip:** YES, with trade-offs (minimal setup vs full setup)

**Next Steps:**
- Brain #3 (UI Design) — Component architecture + 5-state system
- Brain #4 (Frontend) — State management + WebSocket integration
- Brain #6 (QA) — Testing strategy + performance SLOs

---

*Brain #2 consultation complete — 2026-04-08*
