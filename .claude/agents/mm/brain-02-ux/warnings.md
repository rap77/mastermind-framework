# Brain #02-UX — Warnings & Anti-Patterns

These patterns trigger automatic rejection. When rejecting, cite the source using the Oracle Pattern:

```
Rejected: [specific pattern or recommendation] violates [constraint].
Source: global-protocol.md > [Section] | brain-02-ux/warnings.md > [pattern name]
```

Generic rejections without source citation = Rating 2 maximum.

---

## Universal BRAIN-FEED Poisoning Patterns

These 4 patterns apply across ALL brain domains. Source: Brain #6 consultation (2026-03-27).

### 1. Stack Hallucination

**Definition:** Brain suggests a library or tool not declared in the root `uv.lock` or `pnpm-lock.yaml`.

**Rule:** `PROHIBITED: Suggesting external dependencies not declared in the root lockfile.`

**UX-specific examples:** Suggesting FullStory, Hotjar, or UserTesting integrations that aren't in `pnpm-lock.yaml`. Recommending a CSS animation library not in the stack. Proposing Storybook without verifying it's installed.

**Rejection format:**
```
Rejected: [library name] is not declared in root pnpm-lock.yaml.
Source: global-protocol.md > Stack Hard-Lock | brain-02-ux/warnings.md > Stack Hallucination
```

---

### 2. Toil-Inducer

**Definition:** Brain suggests manual steps instead of code — manual content updates, direct DB edits, manual style overrides.

**Rule:** `ANTI-PATTERN: Any recommendation requiring manual production access is an architecture failure.`

**UX-specific examples:** "Manually update the copy in the database." "Edit the CSS file directly to change the theme." "Have a designer create new assets for each release."

**Rejection format:**
```
Rejected: [manual step] requires manual production access.
Source: global-protocol.md > Cross-Domain Anti-Patterns | brain-02-ux/warnings.md > Toil-Inducer
```

---

### 3. Security Bypass

**Definition:** Brain suggests hardcoded credentials, plain-text secrets, or disabled authentication — even in test examples or "temporary" configurations.

**Rule:** `BLOCKER: Never suggest hardcoded credentials, not even in test examples.`

**Rejection format:**
```
Rejected: hardcoded credentials violates Security Bypass rule.
Source: global-protocol.md > Cross-Domain Anti-Patterns | brain-02-ux/warnings.md > Security Bypass
```

---

### 4. Legacy Drift

**Definition:** Brain ignores existing tests or proposes changes that break existing contracts without a migration plan.

**Rule:** `PROHIBITED: Proposals that invalidate existing test contracts without explicit migration plan.`

**UX-specific examples:** Proposing a navigation redesign without addressing existing E2E tests that depend on current nav structure. Recommending component renaming without updating component test files.

**Rejection format:**
```
Rejected: [proposal] invalidates existing test contracts without migration plan.
Source: global-protocol.md > Cross-Domain Anti-Patterns | brain-02-ux/warnings.md > Legacy Drift
```

---

## Domain-Specific Anti-Patterns — UX Research

### Aesthetic Override

**Definition:** Recommending visual changes that reduce information density without cognitive load justification. Prioritizing appearance over function.

**Rule:** `ANTI-PATTERN: War Room is density-first. Beauty serves function, never the inverse.`

**Why:** The War Room is a developer tool with expert users who expect maximum information density. Whitespace and "clean" layouts are appropriate for consumer apps. Developers using the War Room need all relevant context visible without additional clicks. "It looks cleaner" is not a valid UX argument — "it reduces cognitive load by X" is.

**Detection:** Any recommendation justified by "it looks better," "it's cleaner," or "it feels more modern" without a cognitive load measurement = Aesthetic Override.

**Rejection format:**
```
Rejected: visual simplification without cognitive load justification = Aesthetic Override.
Source: brain-02-ux/warnings.md > Aesthetic Override
```

---

### Animation Inflation

**Definition:** Suggesting animation where the state change is already clear from other cues, or where animation delays user action without serving orientation.

**Rule:** `ANTI-PATTERN: Each animation must have a stated UX purpose (orientation, feedback, delight — in that priority order).`

**Why:** Animation in developer tools must earn its place. Orientation animations (helping users understand where content came from/went) are highest priority. Feedback animations (confirming action completed) are second. Delight animations (making the tool enjoyable) are acceptable only when the first two categories are fully satisfied and the animation adds no latency.

**Examples of animation that should be rejected:**
- Fade-in on page load when users already know they navigated there
- Slide transitions between panels that add 300ms to every navigation
- Hover animations on data tables where the data itself communicates state

**Valid animation (do not reject):**
- BrainNode pulse to indicate active processing (feedback — tells user something is happening)
- Graph edges drawing in sequence after dagre layout (orientation — shows the structure forming)

**Rejection format:**
```
Rejected: animation without stated orientation/feedback purpose = Animation Inflation.
Source: brain-02-ux/warnings.md > Animation Inflation
```

---

### Mobile-First Contamination

**Definition:** Applying mobile UX patterns to the War Room desktop tool. Any recommendation assuming touch input, small screen, or mobile-native conventions.

**Rule:** `PROHIBITED: Desktop-first always. Mobile patterns in the War Room are architectural contamination.`

**Prohibited patterns:**
- Bottom navigation bars (mobile-native, inverts desktop mental model)
- Hamburger menus (hides navigation — anathema on desktop where screen space is available)
- Swipe gestures (no touch input assumed — keyboard and mouse only)
- Card-based layouts designed for 390px width (War Room canvas is 1440px)
- "Responsive breakpoints" that change the War Room layout below 1024px (out of scope)

**Why this is PROHIBITED (not just anti-pattern):** Mobile-first patterns contaminate the information architecture. A developer tool with a hamburger menu communicates "I was built for mobile first" and immediately signals it wasn't designed for the actual use case.

**Rejection format:**
```
Rejected: [mobile pattern] violates desktop-first constraint.
Source: global-protocol.md > Stack Hard-Lock | brain-02-ux/warnings.md > Mobile-First Contamination
```

---

### Generic Persona Assumption

**Definition:** Treating War Room users as non-technical, casual, or first-time users. Applying consumer app UX patterns to an expert developer tool.

**Rule:** `BLOCKER for Rating >= 3. Users are developers who built this tool — assume expert mental models.`

**Why:** The primary user of the War Room is the developer/architect who built it. They have expert mental models for IDEs, terminals, dashboards, and developer tools. They do not need:
- Tooltips explaining what a button does (they'll figure it out or read the docs)
- Onboarding flows (they deployed the tool)
- Simplified "beginner mode" options
- Progressive disclosure of features they already know exist

What they DO need:
- Keyboard shortcuts for every frequent action
- Information density over whitespace
- State that persists between sessions
- Error messages that provide actionable context, not generic "something went wrong"

**Detection:** Any recommendation that starts with "users might not understand..." or "first-time users need..." = Generic Persona Assumption for the War Room.

**Rejection format:**
```
Rejected: generic persona assumption — War Room users are expert developers.
Source: brain-02-ux/warnings.md > Generic Persona Assumption
```
