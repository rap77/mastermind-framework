---
source_id: "FUENTE-713"
brain: "brain-software-07-growth-data"
niche: "software-development"
title: "Trustworthy Online Controlled Experiments: A Practical Guide to A/B Testing"
author: "Ron Kohavi, Diane Tang, Ya Xu"
expert_id: "EXP-713"
type: "book"
language: "en"
year: 2020
distillation_date: "2026-03-03"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-03"
changelog:
  - version: "1.0.0"
    date: "2026-03-03"
    changes:
      - "Initial distillation from Trustworthy Online Controlled Experiments"
status: "active"
---

# Trustworthy Online Controlled Experiments

**Ron Kohavi, Diane Tang, Ya Xu**

## 1. Principios Fundamentales

> **P1 - El A/B testing es la única forma confiable de validar cambios en producción**: Las opiniones son baratas. Los datos son caros pero necesarios. Sin experimentos controlados, estás optimizando para lo que CREES que funciona, no para lo que REALMENTE funciona.

> **P2 - La statistical significance no es suficiente**: Un p-value < 0.05 NO significa que tu cambio es bueno. Significa que probablemente no es ruido. Necesitas statistical power, sample size adecuado, y métricas que realmente importen.

> **P3 - El Statistical leakage es enemigo silencioso**: Si users del treatment cuentan a friends del control sobre la nueva feature, tu experimento está contaminado. El control ya no es control. Necesitas isolation real.

> **P4 - El Novelty effect puede engañarte**: Un boost inicial en engagement tras un cambio NO es retained behavior. Users responden a novedad, no a valor real. Mide long-term retention, no solo week 1 metrics.

> **P5 - El OVR (Overall Evaluation Criteria) es más importante que cualquier métrica individual**: Puedes ganar en una métrica (CTR) y perder en otra (retention). El OVR fuerza trade-offs explícitos. ¿Prefieres +10% clicks o -2% retention? Decide ANTES del experimento.

## 2. Frameworks y Metodologías

### Experimentation Maturity Model

```
Level 1: Ad-hoc experiments
Level 2: Standardized platform
Level 3: Strong culture (30+ experiments/week)
Level 4: Embedded experimentation (features ship as experiments)
Level 5: Optimizing the optimization (automated experimentation)
```

**Google/Microsoft/Amazon están en Level 4-5.**
**Startups deben apuntar a Level 2-3.**

### The A/B Testing Workflow

```
1. Hypothesis: "Adding X will improve Y by Z%"
2. Power analysis: Sample size needed
3. Randomization: Users → buckets (50/50)
4. Exposure: Run for ≥ 2 weeks (seasonality)
5. Analysis: Statistical tests on OEC
6. Decision: Ship / Iterate / Kill
```

### Statistical Power Analysis

**Minimum Detectable Effect (MDE):**
```
Sample Size = f(α, β, MDE, σ²)

α = Type I error (false positive) → usually 0.05
β = Type II error (false negative) → usually 0.20
MDE = Minimum effect you care to detect
σ² = Variance of metric
```

**Rule of thumb:** Para detectar un 1% de mejora en retention con 80% power, necesitas ~400k users por bucket.

### The OEC (Overall Evaluation Criteria)

```
OEC = w₁·metric₁ + w₂·metric₂ + ... + wₙ·metricₙ

Example:
OEC = 0.4·(Revenue) + 0.3·(Active Days) + 0.2·(Retention) + 0.1·(NPS)
```

**Key:** Define weights BEFORE running experiment. No cheat.

### Guardrail Metrics

| Metric | Threshold | Action |
|--------|-----------|--------|
| Page load time | < +200ms | Alert if exceeded |
| Error rate | < +0.1% | Kill experiment |
| Uninstalls | < +0.5% | Kill experiment |
| Support tickets | < +10% | Review manually |

## 3. Modelos Mentales

### Modelo de "Experiment Velocity"

```
Learning Rate ∝ (Experiments × Quality) / Time
```

**Implication:** 1 experiment perfecto/mes < 10 experiments buenos/semana.

**Facebook (2012):** 1,000+ experiments running concurrently.
**LinkedIn (2016):** 100+ experiments/week.

### Modelo de "Statistical Power vs. Sample Size"

```
Power
  ↑
1 │─────────────────────────────
  │                        ╱────
  │                   ╱───
0.8│              ╱───  ← Target
  │         ╱───
  │    ╱───
0.5│ ───
  │
  └─────────────────────────────→ Sample Size
     1k   10k   100k   1M
```

**Too small sample:** False negatives (miss real wins).
**Too large sample:** Detects micro-improvements not worth shipping.

### Modelo de "Novelty Effect Decay"

```
Metric Lift
  ↑
+20%│  ╱
    │ ╱  ← Novelty spike
+10%│╱────
    │     ╲
  0%│──────╲──────
    │        ╲─────── Long-term reality
    │          ╲
-10%│           ╲───
    └─────────────→ Time
    W1  W2  W3  W4  W5  W6+
```

**Recommendation:** Run experiments ≥ 2 weeks to wash out novelty.

### Modelo de "Experiment Interaction"

```
Experiment A: +5% CTR
Experiment B: +3% CTR
A + B (both): +2% CTR (not +8%!)
```

**Reason:** Overlapping audiences, cannibalization, or saturation.

**Solution:** Full factorial design (4 buckets: Control, A-only, B-only, A+B).

## 4. Criterios de Decisión

### When to A/B Test vs. Ship

| ✅ A/B Test when | ❌ Ship directly when |
|------------------|----------------------|
| High-risk change (homepage, checkout) | Low-risk (typos, bug fixes) |
| Ambiguous impact (new feature, UX change) | Clear wins (security fix, perf 2x) |
| Sufficient traffic (>100k DAU) | Insufficient traffic (use fake doors) |
| Time to validate (< 2 weeks) | Urgent (legal compliance) |

### Metric Selection Hierarchy

| Priority | Metric Type | Example |
|----------|-------------|---------|
| 1 (North Star) | Long-term value | 30-day retention |
| 2 (Guardrails) | System health | Page load, error rate |
| 3 (Leading) | Short-term signals | CTR, session length |
| 4 (Lagging) | Outcomes | Revenue, LTV |

### Statistical Significance vs. Practical Significance

```
p < 0.01 (highly significant)
BUT effect size = +0.1% (not practical)
→ DO NOT SHIP (not worth engineering cost)
```

**Rule:** MDE should be ≥ 1% for most metrics. Exceptions: massive scale (Google, Facebook).

### Multiple Testing Correction

**Problem:** Running 20 metrics → 1 false positive expected (by chance).

**Solution:** Bonferroni correction or False Discovery Rate (FDR).

```
α_corrected = α / number_of_metrics

α = 0.05, 10 metrics → α_corrected = 0.005
```

## 5. Anti-patrones

### Anti-patrón: "Stopping Early When Winning"

**Problema:** Ves +5% en día 3 y detienes el experimento.

**Reality:** Puedes estar viendo ruido temporal. Early stopping infla false positive rate.

**Solution:**
- Pre-commit to sample size
- Use sequential analysis (O'Brien-Fleming boundaries)
- Never stop before ≥ 1 week

### Anti-patrón: "P-Hacking"

**Problema:** Ejecutas experimento, no es significant, subdivides data ("maybe it works for mobile users in Brazil on Tuesdays").

**Solution:**
- Pre-register hypotheses
- Limit subgroup analysis
- Adjust for multiple comparisons

### Anti-patrón: "Ignoring Heterogeneous Treatment Effects"

**Problema:** Promedio dice 0% lift, pero hay subgrupos con +20% y otros con -20%.

**Solution:**
- Analyze by user segments (power users, new users, geo)
- Consider targeted rollouts instead of global

### Anti-patrón: "Sample Ratio Mismatch (SRM)"

**Problema:** Esperabas 50/50 split, pero obtienes 52/48. Tu randomization está roto.

**Detection:** Chi-square test on bucket sizes.

**Impact:** Invalidates ALL results. Trust nothing from this experiment.

### Anti-patrón: "Observing Without Interacting"

**Problema:** Users in treatment bucket no vieron el cambio (bug, slow rollout, low reach).

**Metric:** "Treatment exposure rate" debe ser > 80%.

**Solution:** Filter analysis to exposed users only.

### Anti-patrón: "Simpson's Paradox"

**Problema:**
- Mobile: +10% lift
- Desktop: +5% lift
- Overall: -2% lift

**Reason:** Composition shift (e.g., more desktop users in treatment).

**Solution:** Weighted averages or segment-specific analysis.

### Anti-patrón: "A/A Test Not Validating Platform"

**Problema:** Nunca corre A/A tests (control vs control) para validar la plataforma.

**What A/A should catch:**
- Sample ratio mismatch
- Randomization bugs
- Data pipeline errors

**Best practice:** Run A/A test weekly. 95% of A/A tests should show no significant difference.
