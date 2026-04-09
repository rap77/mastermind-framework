# BRAIN-FEED-03 — UI Design Domain Feed

> Written by Brain #3 (UI Design). Read-only for other agents.
> Orchestrator reads this after all domain feeds to write BRAIN-FEED.md (global synthesis).
> Last updated: 2026-04-08

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

## 2026-04-05 — Onboarding Visual Proposal Evaluation

### Context
Proposal: Replace Paperclip's CLI onboarding (`npx paperclipai onboard`) with visual step-by-step browser wizard for MasterMind v3.0
Target: Non-technical LATAM enterprise users
Stack: Next.js 16 + React 19 + Tailwind 4 + shadcn/ui + Framer Motion

### Verified Insights

#### Critical Design Decision: APPROVED with Conditions

From NotebookLM consultation (Brain #3: Cooper, Wroblewski, Saffer):

**Priority Assessment:**
- CLI-only onboarding = BLOCKER for enterprise LATAM adoption (fricción técnica = principal motivo de abandono)
- Must be executed in parallel with Phase 15 (Rust Control Plane) — NOT deferred
- Risk: GUI becomes empty shell if Rust endpoints not ready

**4-Step MVP Structure (Anti-feature-creep):**
1. **Identity:** Agent Name + Namespace (simple Input)
2. **Connectivity:** LLM Provider selection + Credentials (Cards)
3. **Knowledge Distillation:** Base source upload (File/URL)
4. **Confirm & Deploy:** Visual summary before writing to Control Plane

**Concrete Implementation Specs:**

Components shadcn/ui available:
- `Card`, `Input`, `Button`, `Dialog`, `Sheet` already exist in `/apps/web/src/components/ui/`
- Missing: `Tabs`, `Progress` (need `pnpm dlx shadcn add tabs progress` before implementation)

Tailwind Classes (Dark Theme Only):
```tsx
// Container
<Card className="max-w-2xl mx-auto mt-20 bg-[var(--color-surface)] border-[var(--color-outline)] shadow-xl" />

// Inputs with Label
<Input className="focus-visible:ring-2 focus-visible:ring-[var(--color-primary)]" />
<Label /> // ALWAYS above input, never use placeholder-only (AC-09 violation)

// Focus ring (WCAG 2.1 AA 3:1 contrast)
focus-visible:ring-2 focus-visible:ring-[var(--color-primary)]
```

Framer Motion Decisions (UX Purpose Required):
| Action | Purpose | Implementation |
|--------|---------|----------------|
| Step transition | **Orientation** | `initial={{ x: 20, opacity: 0 }} animate={{ x: 0, opacity: 1 }}` (slide-in, <300ms) |
| API validation | **Feedback** | Shake on error OR scale-up (1.05) on check icon |
| Rust Plane loading | **Narrative** | Progress bar with `ease: "easeInOut"` |

**Color Tokens (globals.css - CSS-only config):**
```css
--color-background: #121212; /* Never #000000 (smearing) */
--color-surface: #1e1e1e;
--color-primary: #d0bcff; /* Desaturated for dark mode */
--color-error: #f2b8b5;
```

**Accessibility Hard Requirements:**
- Color alone = BLOCKER (8% daltonism). Always pair color + icon + label
- Icon examples: `AlertCircle` (error), `Check` (success), `Loader` (loading)
- Label examples: "Configuración" (not just gear icon), "Validando" (not just spinner)

**Power User Preservation:**
- Keyboard shortcuts (Tab/Enter navigation) benefit ALL users (Curb Cut Effect)
- Focus-visible ring with 3:1 contrast minimum
- Advanced mode toggle (collapse wizard sections)

### Anti-patterns to Avoid (Dan Saffer / Val Head)

- ❌ **AM-301:** Decorative spinners without background task → Use only for orientation/feedback
- ❌ **AM-302:** Transitions >300ms → Platform feels "heavy"
- ❌ **AC-09:** Validation only at final step → Use on-blur inline validation
- ❌ **Placeholder-only labels** → WCAG violation, use `<Label>` above input
- ❌ **Color-only states** → Always add icon or text secondary indicator

### Deferred Items

- Mobile-responsive layout (out of scope for v3.0 — desktop-first 1440px canvas)
- Template gallery integration (requires marketplace infrastructure — conditional on 3 LATAM SME interviews)
- Multi-tenant company switcher (requires CompanyRail pattern — Phase 16+)


### Final Verdict: CONDITIONAL APPROVAL

**Rationale from Brain #3 (Cooper, Wroblewski, Saffer):**

Technical foundation is solid, but missing critical design systems before implementation:

**Blockers to Resolve:**
1. **5-State System Required:** Every interactive component needs Default, Hover, Active, Disabled, Error/Loading. Proposal only addresses happy path.
2. **Tonal Elevation Missing:** Dark mode cannot use shadows (invisible on #000000). Must define white overlay levels for depth perception.
3. **Grid System Undefined:** 1440px canvas requires 12-column grid + 4/8px spacing scale. Without this, frontend improvises margins → inconsistent.
4. **Typography Scale Missing:** Need math-based ratio (e.g., 1.25) for heading/body flow. Prevents aggressive visual jumps.

**Critical Implementation Constraints:**
- Background color: `#121212` (NEVER `#000000` → causes OLED smearing)
- Validation: on-blur inline (never at final step → abandonment spike)
- Tokens: Semantic naming (`--color-on-background` not `--blue-500`)
- Motion max duration: 300ms for transitions (>300ms = "heavy" feel)

**Required Before Phase 15 Implementation:**
1. Add missing shadcn components: `pnpm dlx shadcn add tabs progress`
2. Define elevation tonal levels in globals.css (e.g., `--elevation-1: rgba(255,255,255,0.05)`)
3. Document 5-state system for all onboarding inputs
4. Apply "Squint Test" — if primary action not visible in 3 seconds, fix hierarchy

**Post-Approval Path:**
Execute in parallel with Phase 15 (Rust Control Plane). GUI becomes empty shell if Rust endpoints not ready.

---

## 2026-04-08 — Phase 17 UI Evolution (Plans 02-03)

### Context

Phase 17-01 COMPLETE: Three-Column Layout Foundation shipped
- ThreeColumnLayout.tsx (60 lines) — Desktop 3-column, mobile single-column
- CompanyRail.tsx (62 lines) — Left column placeholder, 180px expanded / 60px collapsed
- AppSidebar.tsx (107 lines) — Center column nav, 240px expanded / 60px collapsed
- layoutStore.ts (93 lines) — Zustand + Immer + persist, 4 state properties (includes `densityMode: 'compact' | 'normal' | 'detailed'`)
- CSS variables: --company-rail-width, --sidebar-width, --layout-transition-duration
- 439/439 tests passing (+32 new)

**Phase 17-02 (Multi-tenant Company Rail) and 17-03 (Active Agents Panel) require visual design guidance.**

### Verified Insights

From NotebookLM consultation (Brain #3: Cooper, Wroblewski, Saffer, Cairo, Pickering):

#### 1. CompanyRail Visual Design — Multi-tenant Switcher

**Branding in 60px Collapsed State:**
- Pattern: Use **image atoms** circular or with `rounded-xl` (12px) to avoid "sharp borders" effect on dark backgrounds
- Visual: Logo must have 8px internal padding inside container with `bg-white/5` to separate brand from `bg-[#121212]`
- Tailwind classes: `w-10 h-10 rounded-xl bg-[var(--surface-variant)] flex items-center justify-center overflow-hidden`
- Accessibility: Logo MUST have `alt` text describing company name (8% colorblind users rely on text labels)

**Drag Handle (Fitts's Law):**
- Interaction: Following Fitts's Law, target must be wide. Do NOT use small "knob"; use **vertical interaction zone** on right edge of rail
- Visual: Subtle 2px wide line that illuminates on `hover` (`bg-primary/50`)
- Tailwind classes: `absolute right-0 top-0 h-full w-1 cursor-col-resize hover:bg-[var(--color-primary)] transition-colors`
- **✅ ALREADY EXISTS** in CompanyRail.tsx line 48: `<GripVertical className="w-4 h-4 text-muted-foreground" />` — Current implementation is centered icon, NOT edge zone. VIOLATES Fitts's Law for 60px collapsed state.
- **Correction needed:** Move drag handle to right edge, expand hit area to full height, use hover illumination

**Status Indicators (Inclusivity):**
- Principle: Color **must never be the only indicator**
- Pattern: Floating `Badge` in top-right corner of logo
  - **Live Agents:** Color dot + number (e.g., `Green Dot` + "4")
  - **Notifications:** Circle with high-contrast border + number
- Tailwind classes: `absolute -top-1 -right-1 min-w-4 h-4 rounded-full bg-[var(--color-error)] text-[10px] flex items-center justify-center px-1 border-2 border-[#121212]`
- WCAG: Triple redundancy (color + icon + number) = passes AA

**Visual Hierarchy (Multi-company):**
- Active company must use **"Active" status indicator** (3px vertical bar on left of logo)
- Inactive companies must have **reduced opacity** (60%) so "squint test" highlights current selection
- Transition: `transition-opacity duration-200 ease-in-out` (matches existing layout transition duration)

#### 2. ActiveAgentsPanel Layout — Real-time Monitoring

**Density Modes:**
- **Compact:** Only **essential atoms**: Brain icon + Status badge + Mini sparkline
- **Normal:** Add agent name + current CPU percentage
- **Detailed:** Expose **complete molecule**: name, uptime, memory, current tasks list
- Interaction: Use **Framer Motion** to animate height change between modes, providing **spatial continuity**
  - Purpose: **Orientation** (user understands where data went/come from)
  - Implementation: `<motion.div layout="position" transition={{ duration: 0.2, ease: "easeInOut" }}>`
  - **✅ layoutStore.ts ALREADY HAS** `densityMode: 'compact' | 'normal' | 'detailed'` (line 9) — No store changes needed

**Status Badges Hierarchy:**
- **Error:** High emphasis (`bg-error/20 text-error` + Warning icon)
  - Tailwind: `bg-[var(--color-error)]/20 text-[var(--color-error)] border border-[var(--color-error)]/30`
- **Running:** Medium emphasis (`text-primary` + Subtle pulse on icon)
  - Tailwind: `text-[var(--color-primary)]` + `animate-pulse` on icon (ALREADY EXISTS in BrainTile.tsx line 65)
  - **CAUTION:** `animate-pulse` is shared between `active` and `running` states — consider `animate-ping` for running to differentiate
- **Idle:** Low emphasis (Desaturated neutrals, no animations)
  - Tailwind: `opacity-60` (ALREADY EXISTS in BrainTile.tsx line 63)

**Agent Metrics Without Clutter:**
- Principle: "Fewer elements than you think". Remove unnecessary borders; use **white space (breathing room)** to separate CPU from Memory
- Visual: Use **monospaced typography** for numeric values to avoid visual jump when data changes rapidly
- Tailwind classes: `font-mono text-xs tracking-tighter text-[var(--color-on-surface-variant)]`
- **✅ ALREADY EXISTS** in globals.css: `--font-mono: var(--font-geist-mono)` (line 18) — No new font loading needed

**Wroblewski's Principles Applied:**
- **Prioritization:** Agent with **highest CPU consumption or error state** must automatically rise to top of list (dynamic ordering)
- Implementation: Sort agents by `(status === 'error' ? 100 : cpu_percent)` before rendering
- **Anti-pattern:** Static alphabetical ordering hides critical issues

#### 3. Cost Dashboard Visuals (Future — Phase 17+)

**MetricCard Pattern:**
- Structure: Title (12px, neutral) → Main Value (24px, bold, white) → Delta change (% vs previous period)
- Visual: Delta must use **color + icon** (e.g., up arrow red for cost increase)
- Example: `+15%` with `TrendingUp` icon in `text-[var(--color-error)]`

**Progress Bar (Budget Enforcement):**
- Design: Background bar `bg-white/10` with progress in primary color
- Limit Indicator: Vertical line at 80% mark that changes progress color to `warning` (orange) if crossed
- Tailwind: `bg-white/10` parent, `bg-[var(--color-primary)]` progress, `absolute left-[80%] w-0.5 h-full bg-warning` limit line
- Accessibility: Do NOT use green→red gradient alone; use clear percentage labels

**Data Visualization Best Practices:**
- Chart Type: For cost tracking over time, use **Line Charts** with subtle shaded area
- Axes: In dark theme, grid lines must be nearly invisible (`opacity-5`) so data is protagonist
- Interaction: Tooltips that show not just number but **question they answer** (e.g., "You spent $20 more than yesterday at this time")

### Anti-patterns to Avoid

- ❌ **AM-303:** Using pure black (#000000) background → Causes OLED smearing, use #121212
- ❌ **AM-304:** Decorative animations without purpose → Every animation must serve Orientation/Feedback/Continuity/Narrative
- ❌ **AM-305:** Color-only status indicators → Always pair color + icon + label (8% colorblind users)
- ❌ **AM-306:** Transitions >300ms → Platform feels "heavy" (brain already validated 200ms in layoutStore)
- ❌ **AM-307:** Small drag handles → Violates Fitts's Law, use full-height edge zones

### Implementation Handoff Specs

**Color System (globals.css - CSS-only):**
```css
/* Dark theme background */
--background: oklch(0.145 0 0); /* #121212 equivalent */
--muted: oklch(0.269 0 0); /* Surface variant for company logos */
--primary: oklch(0.922 0 0); /* Desaturated for dark mode */
--destructive: oklch(0.704 0.191 22.216); /* Error state */
```

**Animation Durations (all in ms):**
- Micro-interactions (hover, focus): 100-200ms
- Layout transitions (CompanyRail, density mode): 200ms (✅ ALREADY DEFINED in `--layout-transition-duration`)
- Modal/panel open/close: 300ms max

**Easing Functions:**
- Entrance: `ease-out` (fast start, slow finish)
- Exit: `ease-in` (slow start, fast finish)
- Layout: `cubic-bezier(0.4, 0, 0.2, 1)` (✅ ALREADY DEFINED in `--layout-transition-easing`)

**Typography Scale (math-based ratio 1.25):**
```css
/* If base is 16px */
text-xs: 0.75rem;   /* 12px */
text-sm: 0.875rem;  /* 14px */
text-base: 1rem;    /* 16px */
text-lg: 1.125rem;  /* 18px */
text-xl: 1.25rem;   /* 20px */
text-2xl: 1.563rem; /* 25px (heading) */
```

**Accessibility Checklist:**
- [ ] All status changes include icon + text label (not just color)
- [ ] Focus-visible ring has 3:1 contrast minimum
- [ ] Drag handle has 44px minimum hit area (Fitts's Law)
- [ ] prefers-reduced-motion disables all animations (✅ ALREADY EXISTS in globals.css line 159-164)
- [ ] Company logos have descriptive alt text
- [ ] Numeric data uses monospaced font to prevent jumping

### Deferred Items

- **Cost Dashboard:** Deferred to Phase 17+ (requires MetricCard and QuotaBar components not yet defined)
- **Mobile bottom navigation:** Out of scope for v3.0 (desktop-first 1440px canvas)
- **Swipe gestures:** Requires touch event handling library (Phase 17+ consideration)
- **Company branding API integration:** Requires Rust Control Plane multi-tenant schema (Phase 15+ dependency)

### Verified Existing Patterns

After grep verification, these patterns already exist and should be reused:

✅ **RAF Batching:** brainStore.ts uses `requestAnimationFrame` batching for 60fps at 24-brain burst
✅ **Zustand + Immer + Persist:** layoutStore.ts follows this pattern (93 lines, 93 tests)
✅ **Dark Mode Colors:** globals.css defines OKLCH tokens for dark theme (lines 92-124)
✅ **Animation Primitives:** `animate-pulse`, `animate-shake`, `animate-spin` exist (globals.css lines 142-164)
✅ **Reduced Motion Support:** `@media (prefers-reduced-motion: reduce)` disables animations (globals.css line 159)
✅ **shadcn/ui Components:** button, card, dialog, input, sheet exist (need to add: tabs, progress)
