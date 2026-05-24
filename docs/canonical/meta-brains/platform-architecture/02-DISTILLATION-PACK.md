# Platform Architecture Brain — Distillation Pack

## 1. Context

- **Target brain:** Platform Architecture Brain
- **Brain ID:** MB-01
- **Expert pack:** `01-EXPERT-PACK.md`

## 2. Distillation Goals

This pack should produce doctrine that helps MasterMind answer:

1. what belongs in the core
2. what belongs in adapters
3. what stays project-local
4. how to evolve architecture without chaos
5. how to productize the framework for reuse

## 3. Core Principles to Extract

- boundaries are part of architecture, not documentation garnish
- reusable capability must justify promotion to core
- project-local logic should not pollute the platform
- architecture should evolve with explicit decisions
- ownership clarity reduces structural entropy

## 4. Frameworks / Methods

- core vs adapter separation
- bounded capability thinking
- architectural fitness-function mindset
- ownership/cognitive-load boundaries
- platform-as-product thinking

## 5. Decision Criteria

- does this generalize across multiple projects?
- is this capability structurally reusable?
- does this reduce or increase coupling?
- is this a platform concern or a project concern?
- does this improve long-term operability?

## 6. Anti-Patterns

- promoting convenience hacks into the core
- mixing project logic into reusable layers
- architecture by accumulation
- unclear ownership of structural decisions
- over-abstracting before repeated evidence exists

## 7. Operational Interpretation

For MasterMind, this distillation should directly inform:

- canonical repo structure
- Core + Project Adapter model
- promotion rules back into core
- meta-brain ownership boundaries
- MVP packaging strategy

## 8. Validation Checklist

- [x] Focuses on operational doctrine, not summary only
- [x] Directly usable by Platform Architecture Brain
- [x] Supports core/adoption decisions
- [x] Avoids project-specific contamination
