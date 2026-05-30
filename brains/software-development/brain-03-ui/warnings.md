# Brain #03-UI — Warnings & Anti-Patterns

These patterns trigger automatic rejection. When rejecting, cite the source using the Oracle Pattern:

```
Rejected: [specific library or pattern] violates [constraint].
Source: global-protocol.md > [Section] | brain-03-ui/warnings.md > [pattern name]
```

Generic rejections without source citation = Rating 2 maximum.

---

## Universal BRAIN-FEED Poisoning Patterns

These 4 patterns apply across ALL brain domains. Source: Brain #6 consultation (2026-03-27).

### 1. Stack Hallucination

**Definition:** Brain suggests a library or tool not declared in the root `uv.lock` or `pnpm-lock.yaml`.

**Rule:** `PROHIBITED: Suggesting external dependencies not declared in the root lockfile.`

**UI Examples:** Suggesting a CSS-in-JS library (Emotion, styled-components), a new icon pack not in pnpm-lock.yaml, or a design token tool that requires `tailwind.config.js`.

**Rejection format:**
```
Rejected: [library name] is not declared in root pnpm-lock.yaml or uv.lock.
Source: global-protocol.md > Stack Hard-Lock | brain-03-ui/warnings.md > Stack Hallucination
```

---

### 2. Toil-Inducer

**Definition:** Brain suggests manual steps instead of code — direct DB access, SSH, manual file edits in production.

**Rule:** `ANTI-PATTERN: Any recommendation requiring manual production access is an architecture failure.`

**Rejection format:**
```
Rejected: [manual step] requires manual production access.
Source: global-protocol.md > Cross-Domain Anti-Patterns | brain-03-ui/warnings.md > Toil-Inducer
```

---

### 3. Security Bypass

**Definition:** Brain suggests hardcoded credentials, plain-text secrets, or disabled authentication — even in test examples or "temporary" configurations.

**Rule:** `BLOCKER: Never suggest hardcoded credentials, not even in test examples.`

**Rejection format:**
```
Rejected: hardcoded credentials violates Security Bypass rule.
Source: global-protocol.md > Cross-Domain Anti-Patterns | brain-03-ui/warnings.md > Security Bypass
```

---

### 4. Legacy Drift

**Definition:** Brain ignores existing visual patterns in `apps/web/src/components/` or proposes design changes that break the established War Room visual language without a migration plan.

**Rule:** `PROHIBITED: Proposals that invalidate existing visual contracts without explicit migration plan.`

**UI Examples:** Suggesting a new spacing scale that conflicts with existing components. Proposing a color system that requires re-theming all 4 panels. Ignoring the existing shadcn/ui component usage in favour of a new component library.

**Rejection format:**
```
Rejected: [proposal] breaks existing visual pattern without migration plan.
Source: global-protocol.md > Cross-Domain Anti-Patterns | brain-03-ui/warnings.md > Legacy Drift
```

---

## Domain-Specific Anti-Patterns — UI Design

### Animation Inflation

**Definition:** Adding animation where the state change is already communicated by other means, or adding animation "for feel," "to make it feel alive," or "to add polish" without a stated UX purpose.

**Rule:** `ANTI-PATTERN. Every Framer-Motion use requires stated UX purpose (orientation / feedback / delight).`

**Why:** Every animation adds cognitive overhead. If the animation doesn't serve the user's task, it is friction. Cite: Saffer — "A microinteraction should feel inevitable, not decorative."

**Examples:**
- "Add a fade-in to the card for a polished feel."
- "Animate the sidebar open/close so it feels smooth."
- Adding spring animations to list items that don't communicate order change.

**Rejection format:**
```
Rejected: animation without stated UX purpose = Animation Inflation.
Source: brain-03-ui/warnings.md > Animation Inflation | Saffer/microinteractions
```

---

### Color-Only State Communication

**Definition:** Relying on color alone to communicate interactive state (active, error, success, disabled, loading) without a secondary visual indicator.

**Rule:** `BLOCKER. Accessibility violation — 8% colorblind users in the War Room target audience.`

**Why:** Red/green color distinction fails for protanopia and deuteranopia users. State must always be communicated through a minimum of TWO signals: color + one of (icon, label, pattern, shape, position).

**Examples:**
- "Show active brain nodes in green, inactive in gray." (color-only)
- "Error state is red border." (color-only)
- Using only opacity changes to indicate disabled state without a label.

**Required fix:** Name the specific secondary indicator before submitting the recommendation. "Active node: green ring + `active` label badge" is acceptable. "Active node: green ring" is not.

---

### Tailwind Config Contamination

**Definition:** Suggesting changes that require `tailwind.config.js` to exist or be modified.

**Rule:** `PROHIBITED. Stack Hallucination — Tailwind 4 CSS-only. There is no tailwind.config.js in this project.`

**Why:** Tailwind 4 uses CSS-only configuration. All design tokens, custom colors, and theme values live in `globals.css` as CSS variables. Any recommendation assuming `tailwind.config.js` exists has hallucinated the stack.

**Examples:**
- "Add a custom color to your Tailwind config."
- "Extend the theme in tailwind.config.js to add a new spacing scale."
- "Configure your Tailwind safelist to include..."

**Rejection format:**
```
Rejected: tailwind.config.js does not exist in this project.
Source: global-protocol.md > Stack Hard-Lock | brain-03-ui/warnings.md > Tailwind Config Contamination
```

---

### Component Bloat

**Definition:** Adding a new custom component for a use case where a shadcn/ui primitive already exists and can serve the need via Tailwind class overrides.

**Rule:** `ANTI-PATTERN. Justify why the existing shadcn/ui primitive is insufficient before creating a new component.`

**Why:** Every new component is maintenance debt. shadcn/ui provides a comprehensive primitive set. Before proposing a new component, the brain must verify that no existing shadcn/ui primitive (Button, Card, Badge, Dialog, Sheet, etc.) can serve the need with class overrides.

**Examples:**
- Proposing a `StatusBadge` component when `Badge` with variant exists.
- Creating a `PanelHeader` component when `CardHeader` with class override works.
- Adding a custom `LoadingSpinner` when the existing one can be resized via className.

**Required before proposing new component:** Show the grep result that proves no shadcn/ui primitive covers this use case.

---

### Panel-Agnostic Recommendation

**Definition:** Providing a design recommendation without specifying which War Room panel (Command Center / The Nexus / Strategy Vault / Engine Room) is in scope.

**Rule:** `ANTI-PATTERN. Triggers automatic Rating 2 max — generic advice without context is not actionable.`

**Why:** Each panel has different information density requirements, interaction patterns, and user tasks. A recommendation valid for Strategy Vault (high density, scannable) may be harmful for Command Center (focus, minimal cognitive load). Without naming the panel, the recommendation is unverifiable.

**Fix:** Every design suggestion must begin with "In [Panel Name]:" and reference the panel's primary user task.

---

### Theme Scope Creep

**Definition:** Proposing light mode, theme switching, system-preference detection, or any multi-theme work.

**Rule:** `PROHIBITED. Out of scope for v2.2 — single dark theme only.`

**Why:** v2.2 ships with a single dark theme. Theme infrastructure is a significant undertaking and is explicitly deferred. Any recommendation touching `prefers-color-scheme`, theme toggles, or light-mode variants is out of scope and adds scope risk.

**Rejection format:**
```
Rejected: theme switching is out of scope for v2.2 — single dark theme only.
Source: brain-03-ui/warnings.md > Theme Scope Creep
```
