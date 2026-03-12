---
source_id: "FUENTE-M7-004"
brain: "brain-marketing-07-seo-technical"
niche: "marketing-digital"
title: "Site Architecture for SEO: How to Structure Your Website for Maximum Rankings"
author: "Cyrus Shepard"
expert_id: "EXP-M7-004"
type: "online-guide"
language: "en"
year: 2023
url: "https://www.zyppy.com/technical-seo/site-architecture/"
skills_covered: ["H1", "H2", "H3", "H4"]
distillation_date: "2026-03-11"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-11"
changelog:
  - version: "1.0.0"
    date: "2026-03-11"
    changes:
      - "Ficha creada con destilación completa - Site Architecture & Crawl Optimization"
status: "active"

habilidad_primaria: "Site Architecture: sistema para diseñar y optimizar la arquitectura de sitios web para maximizar la capacidad de crawl de Google, distribuir autoridad eficientemente y evitar páginas huérfanas"
habilidad_secundaria: "Site architecture, information architecture, internal linking, crawl depth, orphan pages, flat architecture, URL structure, XML sitemaps, crawl budget optimization"
capa: 2
capa_nombre: "Framework Operativo"
relevancia: "CRÍTICA — Cyrus Shepard es ex-Moz y fundador de Zyppy, reconocido authority en technical SEO. Su guía de site architecture es considerada la referencia más completa sobre el tema. Es especialmente relevante para M7 porque aporta un framework sistemático para diseñar arquitecturas de sitio que maximizan crawl budget, distribuyen autoridad eficientemente y evitan orphan pages — los tres problemas más comunes de SEO técnico."
---

# FUENTE-M7-004: Site Architecture for SEO — Cyrus Shepard

## Tesis Central

> La arquitectura de tu sitio es el CIMENTO de SEO técnico. Si tu arquitectura es mala (deep nesting, orphan pages, crawler traps), no importa cuán bueno sea tu content — Google nunca lo va a encontrar o indexar. La arquitectura óptima es FLAT: desde la homepage, cualquier página importante debería estar a máximo 3 clicks de distancia. El segundo principio crítico es INTERNAL LINKING: cada página debe tener al menos 3 internal links pointing to it. El tercero es CRAWL BUDGET: Google tiene tiempo limitado para crawlear tu sitio, no lo desperdicies en páginas low-value. La mayoría de los sitios tienen 30-40% de páginas huérfanas (sin internal links) — ese es el SEO más fácil que vas a hacer: add internal links.

## 1. Principios Fundamentales

> **P1: Flat architecture > Deep architecture**
- Páginas a 1 click de homepage: Máxima autoridad
- Páginas a 2 clicks: Alta autoridad
- Páginas a 3 clicks: Autoridad media
- Páginas a 4+ clicks: Baja autoridad (Google casi nunca las encuentra)
> *Fuente: "Flat Architecture Principle" (Shepard, 2023)*

> **P2: Orphan pages son páginas invisibles para Google**
- Una página sin internal links = orphan page
- Google solo la encuentra si hay external link pointing to it
- Orphan pages rara vez rank (no tienen authority passing)
> *Fuente: "Orphan Page Problem" (Shepard, 2023)*

> **P3: Internal linking es cómo distribuís authority**
- Homepage tiene máxima autoridad
- Internal links pasan autoridad de homepage → páginas internas
- Sin internal links, la autoridad se muere en homepage
> *Fuente: "Link Equity Distribution" (Shepard, 2023)*

> **P4: Crawl budget es limitado, gastalo bien**
- Google crawla tu sitio X veces por día (crawl budget)
- Si tu sitio tiene 1000 pages y crawl budget es 100, Google solo ve 10%
- Priorizá: páginas importantes > páginas low-value
> *Fuente: "Crawl Budget Optimization" (Shepard, 2023)*

> **P5: URL structure refleja arquitectura (y viceversa)**
- URLs cortos y descriptivos = mejor para UX y SEO
- /category/product > /cat3/subcat2/prod45
- URLs con keywords ayudan (pero no lo son todo)
> *Fuente: "URL Structure Best Practices" (Shepard, 2023)*

## 2. Frameworks y Metodologías

### Framework 1: Flat Architecture Design

**Fuente:** "Site Architecture Guide" (Shepard, 2023)
**Propósito:** Diseñar una arquitectura plana para máximo SEO.
**Cuándo usar:** Al diseñar nuevo sitio o reestructurar existente.

**Estructura Óptima:**

```
Homepage (Máxima autoridad)
  ↓
1 click: Category pages (Alta autoridad)
  ↓
2 clicks: Subcategory pages (Autoridad media)
  ↓
3 clicks: Product/Content pages (Autoridad media-baja)
```

**Ejemplo de E-commerce:**

```
Homepage
  ├── Men's Clothing (1 click)
  │   ├── Shirts (2 clicks)
  │   │   ├── Casual Shirts (3 clicks)
  │   │   └── Dress Shirts (3 clicks)
  │   └── Pants (2 clicks)
  │       ├── Jeans (3 clicks)
  │       └── Chinos (3 clicks)
  └── Women's Clothing (1 click)
      ├── Dresses (2 clicks)
      └── Tops (2 clicks)
```

**Ejemplo de Blog:**

```
Homepage
  ├── Blog (1 click)
  │   ├── SEO (2 clicks)
  │   │   ├── Technical SEO (3 clicks)
  │   │   └── Content SEO (3 clicks)
  │   ├── Marketing (2 clicks)
  │   └── Analytics (2 clicks)
```

**Regla de Oro:** Ninguna página importante a más de 3 clicks de homepage.

### Framework 2: Orphan Page Audit

**Fuente:** "Orphan Page Detection" (Shepard, 2023)
**Propósito:** Encontrar y eliminar orphan pages.
**Cuándo usar:** Auditoría técnica trimestral o launch de nuevo sitio.

**Paso 1: Encontrar Orphan Pages**

```yaml
Herramientas:
  - Screaming Frog → Internal report → Orphan pages
  - Ahrefs → Site Audit → Orphan pages
  - Google Search Console → Coverage → Excluded (orphan pages)

Qué buscar:
  - Páginas sin internal links pointing to them
  - Páginas solo en XML sitemap (sin internal links)
  - Páginas con 0 internal links (Screaming Frog report)
```

**Paso 2: Clasificar Orphan Pages**

| Tipo | Action |
|------|--------|
| Páginas importantes (products, blog posts) | **Add internal links** ASAP |
| Páginas de archivo (old blog posts) | Consolidate o noindex |
| Páginas duplicadas | Canonical o delete |
| Páginas de test/development | Delete o noindex |

**Paso 3: Add Internal Links**

**Estrategias:**
- Links desde posts related: "Related articles"
- Links desde category pages: "Latest posts"
- Links desde homepage: "Featured content"
- Links en footer: "Popular content"
- In-content links: anchor text natural

**Target:** Cada página debe tener al menos 3 internal links pointing to it.

### Framework 3: Crawl Budget Optimization

**Fuente:** "Crawl Budget Guide" (Shepard, 2023)
**Propósito:** Maximizar crawl budget para páginas importantes.
**Cuándo usar:** Sitios con > 10K páginas o problemas de indexación.

**Paso 1: Estimar Crawl Budget**

```yaml
Herramientas:
  - Google Search Console → Crawl Stats
  - Log file analysis (Screaming Frog Log Analyzer)

Métricas clave:
  - Average crawl requests per day
  - Crawl success rate (debe ser > 95%)
  - Pages crawled per day
```

**Paso 2: Identificar Crawl Budget Wasters**

| Crawl Waster | Por qué desperdicia | Action |
|--------------|--------------------|--------|
| Parámetros de URL (?sort=, ?filter=) | Crawl mismo content múltiples veces | Canonical o noindex |
| Faceted navigation (/color/red, /size/l) | Miles de URL combinaciones | Noindex filters |
| Paginación (/page/2, /page/99) | Crawl páginas low-value | Consolidate o canonical |
| Duplicate content (HTTP vs HTTPS) | Crawl same content twice | Redirect HTTP → HTTPS |
| Old/abandoned pages | Crawl páginas sin valor | Delete o 404 |

**Paso 3: Priorizar Crawl Budget**

```yaml
Alta prioridad (deben ser crawleadas):
  - Homepage
  - Category pages
  - Important product/content pages
  - Páginas con backlinks
  - Páginas que generan revenue

Media prioridad:
  - Blog posts recientes
  - Páginas de archivo
  - Páginas con tráfico moderado

Baja prioridad (pueden ser noindex):
  - Páginas de filtros
  - Páginas de búsqueda interna
  - Páginas old sin tráfico
  - Páginas de test
```

**Paso 4: Implementar Crawl Budget Controls**

```yaml
Robots.txt:
  - Disallow: /search
  - Disallow: /filter
  - Disallow: /admin

Noindex tags:
  - Páginas de filtros
  - Páginas de búsqueda
  - Páginas de paginación (> page/3)

Canonical tags:
  - Parámetros de URL
  - Duplicate content
  - HTTP → HTTPS redirect

XML Sitemap:
  - Solo incluir páginas importantes
  - No incluir páginas noindex/filters
```

### Framework 4: Internal Linking Strategy

**Fuente:** "Internal Linking Guide" (Shepard, 2023)
**Propósito:** Distribuir autoridad a través de internal linking.
**Cuándo usar:** Continuamente (cada vez que publicás content).

**Principios de Internal Linking:**

**Principio 1: Anchor Text Descriptivo**
- ❌ Bad: "Click here", "Read more"
- ✅ Good: "SEO guide for beginners", "Best running shoes 2024"

**Principio 2: Link a Contextually Relevant Pages**
- ❌ Bad: Link from post about SEO to page about cooking recipes
- ✅ Good: Link from post about SEO to page about technical SEO

**Principio 3: Distribuir Links Uniformemente**
- ❌ Bad: Homepage tiene 100 links, page X tiene 0 links
- ✅ Good: Homepage tiene 50 links, page X tiene 3-5 links

**Principio 4: Link Deep, No Solo a Top-Level**
- ❌ Bad: Solo link a category pages
- ✅ Good: Link a specific content/product pages

**Tipos de Internal Links:**

| Tipo | Dónde | Impacto |
|------|-------|--------|
| Navigation links | Menú, footer | Alto (sitewide) |
| Contextual links | In-content body | Alto (contextual) |
| Related links | "Related posts" sidebar | Medio |
| Breadcrumb links | Top of page | Medio |
| Pagination links | Bottom of category pages | Bajo |

**Implementación:**

```html
<!-- Example: Contextual Internal Link -->
<p>Para aprender más sobre
<a href="/technical-seo/site-architecture">site architecture</a>,
leé nuestra guía completa.</p>

<!-- Example: Related Posts -->
<h3>Related Articles</h3>
<ul>
  <li><a href="/technical-seo/crawl-budget">Crawl Budget Optimization</a></li>
  <li><a href="/technical-seo/internal-linking">Internal Linking Strategy</a></li>
  <li><a href="/technical-seo/orphan-pages">How to Fix Orphan Pages</a></li>
</ul>
```

## 3. Modelos Mentales

### Modelo 1: La Distribución de Autoridad

```
Homepage Authority (100%)
      ↓
Internal Links Distribution
      ↓
┌─────────┬─────────┬─────────┐
│   A     │    B    │    C    │
│ (50%)   │  (30%)  │  (20%)  │
└─────────┴─────────┴─────────┘
```

**Key insight:** Homepage tiene máxima autoridad. Internal links distribuyen esa autoridad. Sin internal links, la autoridad no fluye.

### Modelo 2: La Métrica de Crawl Depth

```
Crawl Depth = Clicks desde Homepage

Depth 1: 100% authority, 90% crawl rate
Depth 2: 70% authority, 70% crawl rate
Depth 3: 40% authority, 40% crawl rate
Depth 4+: 10% authority, 10% crawl rate
```

**Key insight:** Cada click adicional reduce authority y crawl rate dramáticamente.

### Modelo 3: La Matriz de Internal Linking

```
           │ Links │ No Links │
──────────────────────────────────
Important │  ✅   │   ❌     │
           │ Rank  │ Orphan   │
──────────────────────────────────
Unimportant│  ⚠️  │   ✅     │
           │ Waste │ Noindex  │
──────────────────────────────────
```

**Key insight:** Páginas importantes =必须有 internal links. Páginas unimportantes = noindex (no crawler wasters).

## 4. Criterios de Decisión

### Decisión 1: ¿Flat o Deep Architecture?

**Usá Flat (≤3 clicks) si:**
- Tu sitio tiene < 10K páginas
- Tu content es evergreen
- Tu modelo de negocio permite categorías simples
- Tu authority de dominio es media

**Usá Deep (4-5 clicks) si:**
- Tu sitio tiene > 100K páginas
- Tu content es time-sensitive (news)
- Tu industria requiere categorías complejas
- Tu authority de dominio es alta

### Decisión 2: ¿Noindex o Delete Orphan Pages?

**Noindex si:**
- La página tiene value pero no es SEO-relevant
- La página tiene backlinks
- La página genera tráfico (directo o referral)

**Delete si:**
- La página no tiene valor
- La página no tiene backlinks
- La página no genera tráfico
- La página es duplicate/thin content

## 5. Anti-patrones

### Anti-patrón 1: "Todo en Homepage (Link Stuffing)"

**Problema:** Homepage con 200+ links.

**Consecuencias:**
- Link equity diluido (cada link tiene menos valor)
- User experience horrible
- Google puede verlo como spam

**Solución:** Homepage con 50-100 links maximum, a páginas más importantes.

### Anti-patrón 2: "Deep Navigation (7 levels de categorías)"

**Problema:** Páginas a 7 clicks de homepage.

**Consecuencias:**
- Google casi nunca las encuentra
- Authority casi cero
- Rankings imposibles

**Solución:** Reestructura a ≤3 clicks.

### Anti-patrón 3: "Orphan Pages Intentionales"

**Problema:** Crear páginas sin internal links (solo en sitemap).

**Consecuencias:**
- Google no las crawlea
- No rankean nunca
- Tráfico cero

**Solución:** Add internal links a todas las páginas importantes.

## 6. Checklists de Implementación

### Checklist de Site Architecture

**Diseño de Arquitectura:**
- [ ] Flat architecture (≤3 clicks desde homepage)
- [ ] Category pages a 1 click
- [ ] Content/Product pages a 2-3 clicks
- [ ] URLs cortos y descriptivos
- [ ] Breadcrumb navigation

**Internal Linking:**
- [ ] Cada página tiene ≥3 internal links
- [ ] Anchor text descriptivo (no "click here")
- [ ] Links contextuales (relevantes)
- [ ] Links distributed uniformemente
- [ ] No orphan pages importantes

**Crawl Budget:**
- [ ] Identificá crawl wasters (filters, parameters)
- [ ] Robots.txt configurado
- [ ] Noindex en páginas low-value
- [ ] Canonical en duplicate content
- [ ] XML sitemap con páginas importantes

**Monitoreo:**
- [ ] Orphan page audit trimestral
- [ ] Crawl stats review mensual
- [ ] Internal link analysis semestral
- [ ] URL structure review anual

## 7. Métricas de Éxito

| Métrica | Benchmark | Cómo medir |
|---------|-----------|------------|
| Orphan pages | < 5% de páginas | Screaming Frog |
| Crawl depth (avg) | < 3 clicks | Screaming Frog |
| Internal links per page | ≥ 3 | Screaming Frog |
| Crawl success rate | > 95% | Google Search Console |
| Pages indexed / pages total | > 90% | Google Search Console |

## 8. Referencias Externas

**Herramientas:**
- Screaming Frog (site architecture audit)
- Ahrefs Site Audit (orphan pages)
- Google Search Console (crawl stats)

**Lecturas complementarias:**
- Moz: "The Complete Guide to Site Architecture"
- Ahrefs: "Internal Linking for SEO"
