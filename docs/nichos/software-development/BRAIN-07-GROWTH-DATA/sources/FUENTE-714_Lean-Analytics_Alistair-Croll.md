---
source_id: "FUENTE-714"
brain: "brain-software-07-growth-data"
niche: "software-development"
title: "Lean Analytics: Use Data to Build a Better Startup Faster"
author: "Alistair Croll, Benjamin Yoskovitz"
expert_id: "EXP-714"
type: "book"
language: "en"
year: 2013
distillation_date: "2026-03-03"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-03"
changelog:
  - version: "1.0.0"
    date: "2026-03-03"
    changes:
      - "Initial distillation from Lean Analytics"
status: "active"
---

# Lean Analytics

**Alistair Croll, Benjamin Yoskovitz**

## 1. Principios Fundamentales

> **P1 - No mides todo, mides lo que importa para TU stage**: Una startup pre-PMF que obsesiona sobre CAC/LTV está midiendo lo incorrecto. Different stages = different metrics. Mide lo que indica que avanzaste al siguiente stage.

> **P2 - El One Metric That Matters (OMTM) es el foco estratégico**: Tienes 100 métricas disponibles. Escoge UNA que, si mejora, guarantee progress. Todo lo demás es ruido. El OMTM cambia conforme avanza tu startup.

> **P3 - La vanidad metric mata startups**: "Total registered users" suena bien pero no significa nada. "Weekly active users" es mejor. "Paying users" es mejor aún. Si no puedes convertir en acción, es vanity.

> **P4 - El cohort analysis revela la verdad que aggregate metrics esconden**: Retention agregada del 80% puede ser 100% retention de usuarios viejos + 0% de nuevos. Cohort analysis muestra la health real de tu producto.

> **P5 - Solves meaningful problem es prerequisite, no feature**: Antes de optimizar funnel, asegúrate que el problema existe y que tu solución realmente lo resuelve. Lean Analytics empieza con problem validation, no optimization.

## 2. Frameworks y Metodologías

### The 5 Stages of Startup

```
Stage 1: Empathy → Problem validation
Stage 2: Stickiness → Product/market fit
Stage 3: Virality → Growth engine
Stage 4: Revenue → Monetization
Stage 5: Scale → Optimization
```

**Critical:** No saltes etapas. Si no tienes stickiness, virality es leaky bucket. Si no tienes revenue, scale es burning cash faster.

### The One Metric That Matters (OMTM)

| Stage | OMTM | Target |
|-------|------|--------|
| Empathy | Problem interviews completed | 100+ |
| Stickiness | Weekly active users / Weekly new users | > 40% |
| Virality | K-factor (viral coefficient) | > 1.0 |
| Revenue | MRR / ARPU | Positive unit economics |
| Scale | CAC < LTV (within 12 months) | 3:1 ratio |

### Lean Analytics Framework by Business Model

#### E-Commerce

```
Key Metrics:
- Conversion rate (visit → purchase)
- Average order value (AOV)
- Cart abandonment rate
- Repeat purchase rate

Baseline benchmarks:
- Conversion: 1-3%
- Cart abandonment: 65-75%
- Repeat purchase: 20-30% (annual)
```

#### SaaS (B2B)

```
Key Metrics:
- MRR (Monthly Recurring Revenue)
- Churn rate (logo + revenue)
- CAC (Customer Acquisition Cost)
- LTV (Lifetime Value)
- ARPU (Average Revenue Per User)
- MRR Churn / MRR New bookings

Baseline benchmarks:
- Logo churn: < 5% monthly (enterprise), < 10% (SMB)
- Revenue churn: < 2% monthly (enterprise)
- CAC payback: < 12 months
- LTV:CAC ratio: > 3:1
```

#### SaaS (B2C / Freemium)

```
Key Metrics:
- Free → paid conversion rate
- Daily/Monthly active users (DAU/MAU ratio)
- Viral coefficient (K-factor)
- Engagement retention (day 1, 7, 30)

Baseline benchmarks:
- Free → paid: 2-5%
- DAU/MAU: > 20% (healthy engagement)
- Day 30 retention: > 30% for consumer apps
```

#### Mobile App

```
Key Metrics:
- Downloads (vanity, beware)
- Daily/Monthly active users
- Session length
- Retention (day 1, 7, 30)
- Screen flow analysis

Baseline benchmarks:
- Day 1 retention: > 40%
- Day 7 retention: > 20%
- Day 30 retention: > 10%
- DAU/MAU: > 20%
```

#### Two-Sided Marketplace

```
Key Metrics:
- Supply-side: Listings, active providers, response time
- Demand-side: Buyers, search-to-transaction rate
- Liquidity: Time to match (supply → demand)
- Marketplace health (dead listings, ghost accounts)

Baseline benchmarks:
- Search-to-purchase: > 5%
- Time to first transaction: < 7 days (for new listings)
- Supply/demand ratio: Balanced (excess supply = provider churn)
```

#### User-Generated Content

```
Key Metrics:
- Content consumption (views, reads)
- Content creation (posts, uploads)
- Content ratio (creators / consumers) → typically 1:9:90 (1% creators, 9% contributors, 90% consumers)
- Moderation queue time

Baseline benchmarks:
- Creator participation: > 5% of MAU create content monthly
- Comment-to-post ratio: > 2:1
- Flagged content: < 1% of total content
```

### Cohort Analysis

```
Week     Cohort 0  Cohort 1  Cohort 2  Cohort 3
─────────────────────────────────────────────────
Week 0    1000       1200       900        1100
Week 1     600        720        540        660   (60%)
Week 2     400        480        360        440   (40%)
Week 3     300        360        270        330   (30%)
Week 4     250        300        225        275   (25%)
```

**What to look for:**
- Cohorts getting worse? → Product is degrading or onboarding issues
- Cohorts improving? → Product-market fit
- Flat retention curves? → Healthy product

### Pirate Metrics (AARRR)

```
Acquisition: Users finding the product
Activation: Users having a great first experience
Retention: Users coming back
Revenue: Users paying
Referral: Users telling others

But wait: This framework assumes viral growth. Not all businesses should optimize for virality.
Better: Lean Analytics stage-based approach.
```

### Funnel Analysis

```
Visit → Signup → Activation → Retention → Revenue → Referral
  10k    1k       500       200       50       10
 (100%)  (10%)    (50%)    (40%)     (25%)    (20%)

Focus on WEAKEST link, not strongest.
Fixing signup (10% → 15%) = +1500 users total
Optimizing referral (20% → 25%) = +0 users (funnel already broken earlier)
```

## 3. Modelos Mentales

### Modelo de "Metric Momentum"

```
Current Metric = Previous Metric + (Change × Effort)
```

**Implication:** Changing metrics takes time. Don't expect overnight transformation.

**Strategy:** Pick OMTM, focus effort for 1-2 sprints, measure delta.

### Modelo de "Goodhart's Law"

```
When a measure becomes a target, it ceases to be a good measure.
```

**Example:**
- Target: "Maximize registered users"
- Result: Spam accounts, low-quality signups, gaming the system

**Solution:** Use guardrail metrics (quality, engagement, complaints).

### Modelo de "The One Data Point Fallacy"

```
Single data point = Noise
Trend (3+ points) = Signal
```

**Example:**
- Week 1: 5% conversion → Is this good?
- Week 1-4: 4%, 5%, 5.2%, 4.8% → Stable ~5%
- Week 5-8: 5%, 6%, 7%, 8% → Upward trend (investigate what changed)

### Modelo de "Lagged Leading Metrics"

```
Leading metric (today) → Lagging metric (future)

Example:
Leading: Weekly active users (today)
Lagging: 12-month retention (future)

If leading drops today, lagging drops in 12 months.
```

**Implication:** Fix leading metrics before lagging metrics become problems.

### Modelo de "Unit Economics"

```
LTV = ARPU × (1 / Churn Rate)

CAC = Marketing Spend / New Customers

CAC Payback = CAC / (ARPU × Gross Margin)

Healthy business:
- LTV:CAC > 3:1
- CAC Payback < 12 months
- Churn < 5% monthly (B2B) or < 10% (B2C)
```

## 4. Criterios de Decisión

### When to Pivot vs. Persevere

| Metric | Pivot Signal | Persevere Signal |
|--------|--------------|------------------|
| Week 1 retention | < 20% | > 40% |
| Week 4 retention | < 10% | > 20% |
| Activation rate | < 30% | > 60% |
| Paid conversion | < 1% (after 1000 visits) | > 3% |
| NPS | < 20 | > 40 |

**Rule:** 2+ pivot signals = re-evaluate product-market fit.

### Data Sufficiency for Decisions

| Metric | Minimum sample size | Time period |
|--------|-------------------|-------------|
| Conversion rate | 1,000+ visits | 2-4 weeks |
| Churn rate | 500+ customers | 3-6 months |
| Viral coefficient | 1,000+ referrals | 2-4 weeks |
| A/B test lift | Power analysis | 2+ weeks |

**Before optimizing:** Ensure you have statistically significant baseline.

### Metric Selection by Question

| Question | Metric |
|----------|--------|
| Do users love it? | Retention (day 7, 30) |
| Is it growing? | Growth rate (new users/week) |
| Is it monetizing? | ARPU, MRR, LTV:CAC |
| Is it efficient? | CAC payback, burn rate |
| Is it viral? | K-factor, share rate |

### Segmentation Priority

1. **By acquisition channel** (SEO, ads, referral)
2. **By user type** (free vs. paid, B2B vs. B2C)
3. **By geography** (countries, cities)
4. **By behavior** (power users, casual, churned)

**Don't:** Segment by demographics unless relevant to your model.

## 5. Anti-patrones

### Anti-patrón: "Vanity Metrics"

**Problema:** Obsesionarse con métricas que sound good pero no indican health.

```
❌ Total registered users (ever)
❌ Total page views (without context)
❌ Number of features shipped

✅ Weekly active users
✅ Session length per active user
✅ Feature adoption rate (% of users using feature)
```

### Anti-patrón: "Data Paralysis"

**Problema:** Recolectando datos sin actuar. "We need more data" = procrastination disfrazada.

**Solution:**
- Set decision thresholds BEFORE collecting data
- Use "good enough" data for iteration
- A/B test with 80% confidence, not 99%

### Anti-patrón: "Optimizing Before Validating"

**Problema:** Tuning funnel when product-market fit doesn't exist.

**Example:**
- Week 1 retention: 5% (terrible)
- Focus: Optimizing signup flow

**Reality:** You're optimizing a leaky bucket. Fix retention first.

### Anti-patrón: "Blindly Copying Benchmarks"

**Problema:** "Facebook has 50% DAU/MAU, we should too."

**Reality:** Benchmarks vary by business model, stage, geography, audience.

**Solution:** Use benchmarks as reference points, not targets. Track YOUR trends.

### Anti-patrón: "Ignoring Qualitative Data"

**Problema:** "Retention is dropping" → "Send more push notifications" without understanding WHY.

**Solution:** Pair quantitative metrics with qualitative research:
- User interviews
- Usability testing
- Support ticket analysis
- NPS with open feedback

### Anti-patrón: "Measuring Without Hypothesis"

**Problema:** Tracking everything because "data is good."

**Solution:**
- Start with hypothesis: "We believe X will improve Y"
- Define metrics to test hypothesis
- Stop tracking metrics that don't inform decisions

### Anti-patrón: "Chasing Monthly Active Users (MAU) at All Costs"

**Problema:** MAU doesn't distinguish between:
- Power users (love your product)
- Casual users (meh)
- Accidental users (clicked wrong link)

**Better:** Track engagement quality:
- Active days per month
- Core feature usage
- Retention curves (not just monthly snapshots)
