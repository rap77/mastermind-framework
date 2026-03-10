# Marketing Digital y Redes Sociales - MasterMind Framework Niche

**Status:** 🟡 Foundation Complete | Knowledge Base Pending

Este nicho proporciona 16 cerebros especializados para cubrir **full-stack marketing agency** con modelo de growth partnership.

---

## Overview

| Aspecto | Detalle |
|---------|---------|
| **Cerebros** | 16 especializados (M1-M16) |
| **Estado Foundation** | ✅ Completado (PRP-MARKETING-001) |
| **Estado Knowledge** | 🟡 Pendiente (PRP-MARKETING-002/003) |
| **System Prompts** | ✅ 16 creados en `agents/brains/marketing-*.md` |
| **Config** | ✅ `mastermind_cli/config/brains-marketing.yaml` |

---

## Los 16 Cerebros

### Strategy & Brand (M1-M3)

| # | Cerebro | System Prompt | Sources |
|---|---------|---------------|---------|
| M1 | Marketing Strategy & Positioning | [marketing-01-strategy.md](../../../agents/brains/marketing-01-strategy.md) | [BRAIN-01-STRATEGY](sources/BRAIN-01-STRATEGY/) |
| M2 | Brand Identity & Design | [marketing-02-brand.md](../../../agents/brains/marketing-02-brand.md) | [BRAIN-02-BRAND](sources/BRAIN-02-BRAND/) |
| M3 | Content Strategy & Copywriting | [marketing-03-content.md](../../../agents/brains/marketing-03-content.md) | [BRAIN-03-CONTENT](sources/BRAIN-03-CONTENT/) |

### Social Media (M4-M6)

| # | Cerebro | System Prompt | Sources |
|---|---------|---------------|---------|
| M4 | Social Media Organic | [marketing-04-social-organic.md](../../../agents/brains/marketing-04-social-organic.md) | [BRAIN-04-SOCIAL-ORGANIC](sources/BRAIN-04-SOCIAL-ORGANIC/) |
| M5 | Social Media Paid | [marketing-05-social-paid.md](../../../agents/brains/marketing-05-social-paid.md) | [BRAIN-05-SOCIAL-PAID](sources/BRAIN-05-SOCIAL-PAID/) |
| M6 | Search PPC (Google/Bing) | [marketing-06-search-ppc.md](../../../agents/brains/marketing-06-search-ppc.md) | [BRAIN-06-SEARCH-PPC](sources/BRAIN-06-SEARCH-PPC/) |

### SEO (M7-M8)

| # | Cerebro | System Prompt | Sources |
|---|---------|---------------|---------|
| M7 | SEO Technical | [marketing-07-seo-technical.md](../../../agents/brains/marketing-07-seo-technical.md) | [BRAIN-07-SEO-TECHNICAL](sources/BRAIN-07-SEO-TECHNICAL/) |
| M8 | SEO Content & Link Building | [marketing-08-seo-content.md](../../../agents/brains/marketing-08-seo-content.md) | [BRAIN-08-SEO-CONTENT](sources/BRAIN-08-SEO-CONTENT/) |

### Email & Retention (M9-M10)

| # | Cerebro | System Prompt | Sources |
|---|---------|---------------|---------|
| M9 | Email Marketing & Automation | [marketing-09-email.md](../../../agents/brains/marketing-09-email.md) | [BRAIN-09-EMAIL](sources/BRAIN-09-EMAIL/) |
| M10 | Push, SMS & Retention | [marketing-10-retention.md](../../../agents/brains/marketing-10-retention.md) | [BRAIN-10-RETENTION](sources/BRAIN-10-RETENTION/) |

### Analytics & Operations (M11-M13)

| # | Cerebro | System Prompt | Sources |
|---|---------|---------------|---------|
| M11 | Marketing Analytics & Data | [marketing-11-analytics.md](../../../agents/brains/marketing-11-analytics.md) | [BRAIN-11-ANALYTICS](sources/BRAIN-11-ANALYTICS/) |
| M12 | Conversion Rate Optimization (CRO) | [marketing-12-cro.md](../../../agents/brains/marketing-12-cro.md) | [BRAIN-12-CRO](sources/BRAIN-12-CRO/) |
| M13 | Marketing Automation & Operations | [marketing-13-ops.md](../../../agents/brains/marketing-13-ops.md) | [BRAIN-13-OPS](sources/BRAIN-13-OPS/) |

### Community & Growth (M14-M16)

| # | Cerebro | System Prompt | Sources |
|---|---------|---------------|---------|
| M14 | Influencer & Partnerships | [marketing-14-influencer.md](../../../agents/brains/marketing-14-influencer.md) | [BRAIN-14-INFLUENCER](sources/BRAIN-14-INFLUENCER/) |
| M15 | Community Building & Management | [marketing-15-community.md](../../../agents/brains/marketing-15-community.md) | [BRAIN-15-COMMUNITY](sources/BRAIN-15-COMMUNITY/) |
| M16 | Growth Partner & Agency Operations | [marketing-16-growth-partner.md](../../../agents/brains/marketing-16-growth-partner.md) | [BRAIN-16-GROWTH-PARTNER](sources/BRAIN-16-GROWTH-PARTNER/) |

> **Note:** M16 es el meta-cerebro evaluador del nicho Marketing Digital (similar al Brain #7 de Software Development).

---

## Estructura de Archivos

```
docs/nichos/marketing-digital/
├── PROPUESTA-16-CEREBROS.md        ← Propuesta original (status updated)
├── PRP-MARKETING-DIGITAL-NICHO.md  ← Plan de implementación
├── README.md                        ← Este archivo
└── sources/                         ← Fuentes maestras (para PRP-002/003)
    ├── BRAIN-01-STRATEGY/           ← Vacío (pendiente de PRP-002)
    ├── BRAIN-02-BRAND/
    ├── BRAIN-03-CONTENT/
    ├── BRAIN-04-SOCIAL-ORGANIC/
    ├── BRAIN-05-SOCIAL-PAID/
    ├── BRAIN-06-SEARCH-PPC/
    ├── BRAIN-07-SEO-TECHNICAL/
    ├── BRAIN-08-SEO-CONTENT/
    ├── BRAIN-09-EMAIL/
    ├── BRAIN-10-RETENTION/
    ├── BRAIN-11-ANALYTICS/
    ├── BRAIN-12-CRO/
    ├── BRAIN-13-OPS/
    ├── BRAIN-14-INFLUENCER/
    ├── BRAIN-15-COMMUNITY/
    └── BRAIN-16-GROWTH-PARTNER/

mastermind_cli/config/
└── brains-marketing.yaml            ← Config de 16 cerebros

agents/brains/
├── marketing-01-strategy.md         ← System prompts
├── marketing-02-brand.md
├── marketing-03-content.md
├── marketing-04-social-organic.md
├── marketing-05-social-paid.md
├── marketing-06-search-ppc.md
├── marketing-07-seo-technical.md
├── marketing-08-seo-content.md
├── marketing-09-email.md
├── marketing-10-retention.md
├── marketing-11-analytics.md
├── marketing-12-cro.md
├── marketing-13-ops.md
├── marketing-14-influencer.md
├── marketing-15-community.md
└── marketing-16-growth-partner.md
```

---

## Cómo Contribuir Fuentes Maestras

Las fuentes maestras (libros, artículos, videos) se agregarán en **PRP-MARKETING-002** y **PRP-MARKETING-003**.

### Formato de Fuentes

Cada fuente debe seguir el formato establecido en el framework:

```yaml
---
source_id: "FUENTE-XXX"
brain: "marketing-MX-YY"
title: "Título del libro/artículo"
author: "Nombre del autor"
type: "book|article|video|podcast|course"
year: YYYY
isbn: "XXXXXXXXXX"  # para libros
expert_id: "EXP-XXX"
skills_covered: ["H1", "H3"]
distillation_quality: "complete|partial|draft"
loaded_in_notebook: false
hispánico_expert: true|false
---

# [Título]

## 1. Principios Fundamentales

> **P1: [Principio]**
> *Fuente: [Título, Cap X (Autor, Año)]*

...

## 2. Frameworks y Metodologías

### Framework 1: [Nombre]
**Fuente:** [Título, Cap X (Autor, Año)]

...

## 3. Modelos Mentales
## 4. Criterios de Decisión
## 5. Anti-patrones
```

**IMPORTANTE:** Cada sección debe incluir atribución completa: `*Fuente: [Título, Cap X (Autor, Año)]*`

---

## Próximos Pasos

1. **PRP-MARKETING-002** (~30-40h): Knowledge base para M1-M8 (80 fuentes maestras)
2. **PRP-MARKETING-003** (~30-40h): Knowledge base para M9-M16 (80 fuentes maestras)
3. **Testing**: E2E tests con briefs reales de agencia de marketing
4. **Release v1.2.0**: Marketing Digital niche production ready

---

## Referencias

- [PROPUESTA-16-CEREBROS.md](PROPUESTA-16-CEREBROS.md) — Propuesta detallada
- [PRP-MARKETING-DIGITAL-NICHO.md](PRP-MARKETING-DIGITAL-NICHO.md) — Plan de implementación
- [PRPs/marketing/](../../../PRPs/marketing/) — PRPs del nicho
