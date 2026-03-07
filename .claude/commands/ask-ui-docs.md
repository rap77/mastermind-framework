---
description: Generate UI/UX design system documentation for precise implementation
argument-hint: [context about your project - tech stack, phase, scope]
---

<objective>
Generate complete UI/UX design system documentation based on UX Research and UI Design brain expertise.

This produces developer-ready specifications with exact values, not vague guidelines.
</objective>

<context>
Current project: ! `pwd`
Project name: ! `basename $(pwd)`

## Context to provide:

Before using this command, know your:
- Tech stack: (Next.js version, UI library, styling approach)
- Current phase: (what you're building)
- Scope: (what needs documentation)
</context>

<process>
1. Read project context from
2. Query UX Research brain (Brain #2) for documentation structure
3. Query UI Design brain (Brain #3) for technical specifications
4. Synthesize both perspectives into comprehensive documentation
5. Generate deliverables in structured format
</process>

<success_criteria>
- Design tokens specified with exact values (hex, pixels, spacing)
- Component library with all states (default, hover, active, disabled, error)
- Layout and grid system defined
- Redlining specifications for mockups
- Accessibility checklist included
- Dark mode mapping (if applicable)
</success_criteria>

## What This Generates

Based on your context, this will produce:

1. **Design Tokens** - Colors, typography, spacing (exact values)
2. **Component Library** - Atomic components with all states
3. **Layout System** - Grid, breakpoints, containers
4. **Mockup Specs** - Redlining guidelines
5. **Accessibility Guide** - WCAG compliance checklist
6. **Handoff Guide** - For AI tools and developers

## Example Usage

```bash
# General request
/ask-ui-docs Next.js 16, Tailwind 4, product catalog phase

# Specific scope
/ask-ui-docs Need component library for forms - Next.js 16, React 19, Tailwind 4
```

## Notes

- Generates precise specifications, not "guidelines"
- Includes exact values (no "choose what looks good")
- Focuses on implementable documentation
- Uses expert knowledge from 19 UX/UI sources
