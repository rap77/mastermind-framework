---
source_id: "FUENTE-621"
brain: "brain-software-06-qa-devops"
niche: "software-development"
title: "Continuous Delivery: Reliable Software Releases through Build, Test, and Deployment Automation"
author: "Jez Humble, David Farley"
expert_id: "EXP-621"
type: "book"
language: "en"
year: 2010
distillation_date: "2026-03-03"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-03"
changelog:
  - version: "1.0.0"
    date: "2026-03-03"
    changes:
      - "Initial distillation from Continuous Delivery"
status: "active"
---

# Continuous Delivery

**Jez Humble, David Farley**

## 1. Principios Fundamentales

> **P1 - El deployment pipeline es el corazón**: Un deployment pipeline automatizado desde commit hasta producción es la base.

> **P2 - Si duele, hazlo más frecuentemente**: Deployment pain es inversamente proporcional a deployment frequency.

> **P3 - La build es el estado verificable**: Una build que pasó tests es reproducible. Deploy anterior build para rollback.

> **P4 - Tests automatizados son la red de seguridad**: Sin tests, cada deployment es gambling.

> **P5 - Feature toggles permiten branching en código**: Merge a master diariamente, deploy continuo, features via flags.

## 2. Frameworks y Metodologías

### Deployment Pipeline
```
Commit → Build → Acceptance Tests → Capacity Tests → Production
```

### Deployment Strategies
- **Blue-Green**: Zero downtime, instant rollback
- **Rolling**: Gradual rollout
- **Canary**: Test with real traffic

### Feature Toggles
```python
if feature_flag_enabled("new_feature"):
    new_feature()
else:
    old_feature()
```

## 3. Modelos Mentales

### Deployment Frequency vs Failure Rate
```
Failure Rate
    ↓
    │    ╲
    └───────→ Deployment Frequency
```
**More deployments = Lower failure rate.**

## 4. Criterios de Decisión

### Blue-Green vs Rolling vs Canary
| Blue-Green | Rolling | Canary |
|-----------|---------|--------|
| Zero downtime | Gradual | Real traffic test |
| Double cost | Partial downtime | Complex |

## 5. Anti-patrones

### Anti-patrón: "Deployment Fridays"
❌ Deploy Friday → Weekend debugging
✅ Deploy Monday-Thursday

### Anti-patrón: "No Rollback Plan"
❌ Deploy, break, panic
✅ Previous build ready
