---
source_id: "FUENTE-620"
brain: "brain-software-06-qa-devops"
niche: "software-development"
title: "Site Reliability Engineering: How Google Runs Production Systems"
author: "Google SRE Team"
expert_id: "EXP-620"
type: "book"
language: "en"
year: 2016
distillation_date: "2026-03-03"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-03"
changelog:
  - version: "1.0.0"
    date: "2026-03-03"
    changes:
      - "Initial distillation from SRE book"
status: "active"
---

# Site Reliability Engineering

**Google SRE Team**

## 1. Principios Fundamentales

> **P1 - SRE es lo que sucede cuando le pides a un operations engineer que diseñe automation**: SRE es la evolución de sysadmin work. En vez de responder manualmente, SRE automatiza respuestas y crea tools.

> **P2 - El error budget debe gastarse sabiamente, no evitarse**: Un error budget del 5% significa 43 horas al mes de downtime aceptable. Úsalo para innovar, no guardarlo.

> **P3 - Toil es trabajo manual que debe eliminarse**: SREs deberían pasar < 50% del tiempo en engineering, no operations work.

> **P4 - La SLA es un contract, no aspiración**: Un Service Level Agreement define qué nivel de servicio prometes. Incumplirlo tiene consecuencias financieras.

> **P5 - Los postmortems son blameless**: Si buscas culpables, las personas esconderán mistakes. Blameless focusing en process mejora learning.

## 2. Frameworks y Metodologías

### SLI, SLO, SLA

**SLI**: Service Level Indicator (métrica específica)
- Request latency (p95 < 200ms)
- Error rate (0.1%)
- Availability (99.9%)

**SLO**: Service Level Objective (target para SLI)
- SLO: 99.9% availability monthly

**SLA**: Service Level Agreement (contract con customer)
- SLA: We guarantee 99.9% or refund

### Error Budget

```
Error Budget = 100% - SLO
SLO = 99.9% → Error Budget = 0.1% = 43 min/month
```

## 3. Modelos Mentales

### Change Velocity vs Stability
```
Change Velocity ←→ Stability
    ↓                  ↓
  Features            Uptime
    ↑                  ↑
    └──── Error Budget ────┘
```

## 4. Criterios de Decisión

### When to Use SRE
✅ Large-scale production systems
❌ Small, low-traffic apps

## 5. Anti-patrones

### Anti-patrón: "Hero Culture"
❌ Dependiendo de individuals heroics
✅ Systems over heroes
