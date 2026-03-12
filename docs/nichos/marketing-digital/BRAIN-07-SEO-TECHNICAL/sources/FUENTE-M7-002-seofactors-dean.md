---
source_id: "FUENTE-M7-002"
brain: "brain-marketing-07-seo-technical"
niche: "marketing-digital"
title: "SEO Factors That Matter: The Complete Guide to Ranking in Google"
author: "Brian Dean"
expert_id: "EXP-M7-002"
type: "online-course"
language: "en"
year: 2023
url: "https://backlinko.com/seo-factors"
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
      - "Ficha creada con destilación completa - SEO Factors & Structured Data"
status: "active"

habilidad_primaria: "SEO Technical Factors: sistema completo para entender y priorizar los factores de ranking técnico que realmente importan en Google, desde core web vitals hasta structured data y on-page optimization"
habilidad_secundaria: "SEO ranking factors, Core Web Vitals, structured data, schema markup, on-page SEO, technical SEO, link building, content optimization, featured snippets"
capa: 2
capa_nombre: "Framework Operativo"
relevancia: "CRÍTICA — Brian Dean es el fundador de Backlinko, una de las authorities más respetadas en SEO. Sus estudios sobre factores de ranking son citados por MOZ, Search Engine Journal y Neil Patel. Es especialmente relevante para M7 porque destila la complejidad de los 200+ factores de ranking de Google en un framework prioritario y accionable, enfocándose en lo que MUEVE la aguja en rankings."
---

# FUENTE-M7-002: SEO Factors That Matter — Brian Dean

## Tesis Central

> Google tiene 200+ factores de ranking, pero SOLO 15-20 realmente importan. El 80/20 de SEO está en: (1) Core Web Vitals + (2) Content que satisfice search intent + (3) Backlinks de autoridad + (4) On-page optimization. El error #1 de los SEOs es perseguir factores micro (keyword density, exact match domains) mientras ignoran los macro factores que Google realmente valora. Los rankings son un juego de suma cero: tu competencia está optimizando los macro factores, si vos no, perdés. La clave es priorizar por impacto, no por dificultad: empezá con Core Web Vitals (fácil de medir, impacto directo) y terminá con link building (difícil, pero el factor más fuerte).

## 1. Principios Fundamentales

> **P1: Core Web Vitals son ranking factors, no nice-to-have**
- LCP (Largest Contentful Paint) < 2.5s es HARD requirement para top 10
- FID (First Input Delay) < 100ms afecta experiencia y rankings
- CLS (Cumulative Layout Shift) < 0.1 es crítico para móviles
> *Fuente: "Google's Page Experience Update" (Dean, 2021)*

> **P2: Content sin backlinks es invisible, backlinks sin content es frágil**
- Content de calidad + backlinks de autoridad = rankings sostenibles
- Content sin backlinks = indexado pero no rankeado
- Backlinks sin content = rankings temporales (Google eventualmente lo penaliza)
> *Fuente: "Content + Links Equation" (Dean, 2023)*

> **P3: Search intent es el #1 factor de on-page SEO**
- Si tu contenido no matchea search intent, no importa cuán bueno sea
- Google mide satisfaction con pogo-sticking (volver a SERP y hacer click en otro resultado)
- La palabra clave exacta importa MENOS que satisfacer la intención detrás de ella
> *Fuente: "Search Intent Over Keywords" (Dean, 2022)*

> **P4: Structured data no te da rankings directos, pero te da visibilidad**
- Schema markup no es un ranking factor directo (según Google)
- PERO: structured data → rich snippets → CTR más alto → rankings indirectos
- Featured snippets vienen de structured data + content que directly answer la pregunta
> *Fuente: "Schema Markup Reality" (Dean, 2023)*

> **P5: La calidad de backlinks > cantidad (hoy más que nunca)**
- 1 backlink de NY Times vale más que 1000 de sitios spam
- Google's Penguin update mató la estrategia de cantidad
- Domain Authority (DA) es un proxy, pero la verdadera métrica es PageRank
> *Fuente: "Link Quality Revolution" (Dean, 2023)*

## 2. Frameworks y Metodologías

### Framework 1: Los 5 Macro Factores de Ranking

**Fuente:** "SEO Factors That Matter" (Dean, 2023)
**Propósito:** Priorizar esfuerzos SEO basado en impacto real.
**Cuándo usar:** Al planificar estrategia SEO o auditoría.

```
Macro Factor 1: Core Web Vitals (20% peso)
  ├─ LCP < 2.5s (loading)
  ├─ FID < 100ms (interactivity)
  └─ CLS < 0.1 (visual stability)

Macro Factor 2: Content Quality (25% peso)
  ├─ Search intent match
  ├─ Content depth (comprehensive coverage)
  ├─ Freshness (para queries freshness-sensitive)
  └─ Uniqueness (no duplicate/thin content)

Macro Factor 3: Backlinks Authority (30% peso)
  ├─ Quantity de domains únicos linking
  ├─ Quality de dominios (DA, traffic)
  ├─ Relevance del link context
  └─ Anchor text natural (no over-optimization)

Macro Factor 4: On-Page Optimization (15% peso)
  ├─ Title tag con keyword (pero no keyword stuffing)
  ├─ Meta description optimizada para CTR
  ├─ URL structure corta y descriptiva
  ├─ Header tags (H1, H2) con keywords semánticas
  └─ Internal linking a related content

Macro Factor 5: Technical SEO (10% peso)
  ├─ Mobile-friendliness
  ├─ HTTPS
  ├─ XML sitemap
  ├─ Robots.txt correcto
  └─ Canonical tags implementadas
```

**Priorización:**
1. Technical SEO → Core Web Vitals (fácil, alto impacto)
2. On-Page Optimization → Search intent (fácil, alto impacto)
3. Content Quality → Comprehensive coverage (medio, alto impacto)
4. Backlinks Authority → Link building (difícil, máximo impacto)

### Framework 2: Audit de Core Web Vitals

**Fuente:** "Core Web Vitals Guide" (Dean, 2021)
**Propósito:** Optimizar Core Web Vitals para Google rankings.
**Cuándo usar:** Siempre (Google lo mide continuamente).

**Paso 1: Medición**

```yaml
Herramientas:
  - PageSpeed Insights (Google official)
  - Search Console → Core Web Vitals report
  - Lighthouse (Chrome DevTools)
  - WebPageTest (deep analysis)

Datos que necesitás:
  - LCP (Largest Contentful Paint) - target: < 2.5s
  - FID (First Input Delay) - target: < 100ms
  - CLS (Cumulative Layout Shift) - target: < 0.1
```

**Paso 2: Diagnóstico por Métrica**

**LCP > 2.5s (Slow loading):**
- Causas comunes:
  - Imágenes no optimizadas (compress/resize/WebP)
  - JavaScript bloqueando render
  - Server response time lento
  - No usar CDN
- Soluciones rápidas:
  - Comprimir imágenes (TinyPNG, ImageOptim)
  - Lazy loading de imágenes below-the-fold
  - Minify CSS/JS
  - Usar CDN (Cloudflare, AWS CloudFront)

**FID > 100ms (Slow interactivity):**
- Causas comunes:
  - JavaScript excesivo en main thread
  - Third-party scripts (analytics, chat widgets)
  - Large JavaScript bundles
- Soluciones rápidas:
  - Defer non-critical JS
  - Remove unused third-party scripts
  - Code splitting (React.lazy, webpack)

**CLS > 0.1 (Layout shifts):**
- Causas comunes:
  - Imágenes sin dimensions width/height
  - Ads sin espacio reservado
  - Content inyectado dinámicamente sin espacio
- Soluciones rápidas:
  - Siempre especificar width/height en imágenes
  - Reservar espacio para ads
  - Usar `min-height` para contenido dinámico

**Paso 3: Validación**

| Métrica | Good | Needs Improvement | Poor |
|---------|------|-------------------|------|
| LCP | < 2.5s | 2.5s - 4s | > 4s |
| FID | < 100ms | 100ms - 300ms | > 300ms |
| CLS | < 0.1 | 0.1 - 0.25 | > 0.25 |

### Framework 3: Structured Data para Rich Snippets

**Fuente:** "Schema Markup Guide" (Dean, 2023)
**Propósito:** Implementar structured data para rich snippets.
**Cuándo usar:** Para contenido elegible para rich snippets (reviews, recipes, products, etc.).

**Schema Types con Mayor Impacto en CTR:**

| Schema Type | CTR Lift | Caso de uso |
|-------------|----------|-------------|
| Review / Rating | +25-30% | Product reviews, local business |
| FAQ | +15-20% | FAQ pages, how-to content |
| How-To | +20-25% | Step-by-step guides |
| Product | +30-35% | E-commerce product pages |
| Article | +10-15% | Blog posts, news |
| Video | +25-30% | Video content |
| Breadcrumb | +5-10% | E-commerce, large sites |

**Implementación:**

```html
<!-- Example: Product Schema -->
<script type="application/ld+json">
{
  "@context": "https://schema.org/",
  "@type": "Product",
  "name": "Nombre del Producto",
  "image": "https://example.com/product-image.jpg",
  "description": "Descripción del producto",
  "brand": {
    "@type": "Brand",
    "name": "Marca"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "reviewCount": "125"
  },
  "offers": {
    "@type": "Offer",
    "url": "https://example.com/product",
    "priceCurrency": "USD",
    "price": "99.99",
    "availability": "https://schema.org/InStock"
  }
}
</script>
```

**Validación:**
- Google Rich Results Test
- Schema.org Validator
- Search Console → Enhancements report

### Framework 4: Link Building Strategic

**Fuente:** "Link Building Strategies" (Dean, 2023)
**Propósito:** Construir backlinks de autoridad de forma sostenible.
**Cuándo usar:** Continuamente (link building es never-ending).

**Estrategia 1: Skyscraper Technique**

1. **Encontrá content con backlinks en tu niche**
   - Ahrefs → Backlinks → Competitor pages
   - Filtrá por páginas con +50 backlinks
   - Identificá contenido con alto link equity

2. **Creá algo MEJOR**
   - Más comprehensivo (2000+ words vs 500)
   - Más actualizado (2024 data vs 2020)
   - Mejor diseñado (visuals, charts)
   - Más action-oriented (checklists, templates)

3. **Outreach a sitios linking al content original**
   - Encontrá contactos (Hunter.io, LinkedIn)
   - Email personalizado: "Vi que linkeaste X, creamos una versión mejorada"
   - Tasa de success: 5-15%

**Estrategia 2: Broken Link Building**

1. **Encontrá broken links en tu niche**
   - Ahrefs → Broken backlinks → Competitor domains
   - Check HTTP status (404)

2. **Creá content que reemplace el broken link**
   - Similar topic, pero mejor/actualizado

3. **Outreach al site owner**
   - "Noté que tenés un broken link a [broken], tenemos content que lo reemplaza"
   - Tasa de success: 20-30%

**Estrategia 3: Digital PR**

1. **Creá data original**
   - Surveys, studies, original research
   - Industry reports, statistics

2. **Distribuí a journalists**
   - HARO (Help a Reporter Out)
   - Twitter lists of journalists in your niche
   - Direct email outreach

3. **Resultado:**
   - Links de high-authority news sites (NYT, Forbes, TechCrunch)
   - Tasa de success: 1-5% pero links de ALTÍSIMA calidad

**Quality > Quantity:**

| Metric | Good | Great |
|--------|------|-------|
| Domain Authority (DA) | 40+ | 60+ |
| Organic traffic | 5K+ | 50K+ |
| Relevance | Related niche | Exact niche |
| Link type | DoFollow | DoFollow + contextual |

## 3. Modelos Mentales

### Modelo 1: La Pirámide de Factores de Ranking

```
                    ▲
                   / \
                  / 1 \  Content Quality (25%)
                 /-----\
                /       \
               /    2    \  Backlinks Authority (30%)
              /-----------\
             /             \
            /      3        \  Core Web Vitals (20%)
           /-----------------\
          /                   \
         /          4          \  On-Page Optimization (15%)
        /-----------------------\
       /                           \
      /              5              \  Technical SEO (10%)
     /-------------------------------\
```

**Key insight:** Backlinks y Content son los cimientos. Sin ellos, lo demás es marginal.

### Modelo 2: El Ciclo de Rankings Sostenibles

```
Content Quality
      ↓
User Satisfaction (low pogo-sticking)
      ↓
Higher CTR from SERP
      ↓
More Dwell Time
      ↓
Google: "Este content es útil"
      ↓
Higher Rankings
      ↓
More Visibility
      ↓
More Backlinks (naturalmente)
      ↓
Higher Rankings (reforzado)
```

**Key insight:** Rankings sostenibles vienen de content que realmente satisface users, no de tricks.

### Modelo 3: La Matriz de Esfuerzo vs Impacto

```
Impacto Alto │  1  │  2  │
            │CWV  │Links│
            ├─────┼─────┤
Impacto Medio│OnPag│Cont │
            │ SEO │Qual │
            ├─────┼─────┤
Impacto Bajo│Tech │Micro│
            │SEO  │Factors│
            └─────┴─────┘
              Fácil  Difícil
            Esfuerzo
```

**Key insight:** Priorizá 1 y 2 (CWV + Links) antes de 3 y 4. Ignorá 5 (micro factors).

## 4. Criterios de Decisión

### Decisión 1: ¿Optimizar Core Web Vitals primero o Content primero?

**Optimizá CWV primero si:**
- Tu LCP/FID/CLS está en "Poor" (rojo en Search Console)
- Tu competencia ya tiene CWV optimizados
- Tu content es decente pero rankings no suben
- Tenés recursos técnicos (developer time)

**Optimizá Content primero si:**
- Tu CWV está en "Good" o "Needs Improvement"
- Tu content es thin/duplicado/baja calidad
- Tu pogo-sticking rate es alta
- No tenés recursos técnicos ahora

### Decisión 2: ¿Skyscraper, Broken Link o Digital PR?

**Usá Skyscraper si:**
- Tenés capacidad de crear content comprehensivo
- Tu competencia tiene content con muchos backlinks
- Tu niche tiene evergreen content

**Usá Broken Link Building si:**
- Encontraste broken links relevantes
- Podés crear content similar rápidamente
- Tu outreach email puede ser personalizado

**Usá Digital PR si:**
- Tenés budget para estudios/surveys
- Tu niche tiene news coverage
- Buscás links de MUY alta autoridad

## 5. Anti-patrones

### Anti-patrón 1: "Keyword Stuffing en Title Tag"

**Problema:** Poner la keyword 3 veces en el title tag NO ayuda, dueña.

**Consecuencias:**
- Google detecta over-optimization
- CTR más bajo (se ve spammy)
- Rankings penalizados

**Solución:** Usá la keyword UNA vez, naturalmente.

### Anti-patrón 2: "Comprar Backlinks"

**Problema:** Google's Penguin penaliza link schemes.

**Consecuencias:**
- Penalización manual o algorítmica
- Rankings perdidos permanentemente
- Recuperación toma meses (disavow file)

**Solución:** Construís links organically o outreach legítimo.

### Anti-patrón 3: "Ignorar Search Intent por Keyword Exact Match"

**Problema:** Tu contenido tiene la keyword exacta pero no responde la pregunta del usuario.

**Consecuencias:**
- Pogo-sticking alto (users vuelven a SERP)
- Google baja tus rankings
- Alta tasa de rebote

**Solución:** Entendé search intent PRIMERO, escribí content después.

### Anti-patrón 4: "Structured Data en Todo"

**Problema:** Poner schema markup en páginas que no lo necesitan.

**Consecuencias:**
- Google ignora tu markup
- Potential spam penalty
- Dilutes the impact of legitimate schema

**Solución:** Usá structured data SOLO cuando es relevante para el content type.

## 6. Métricas de Éxito

| Métrica | Benchmark | Cómo medir |
|---------|-----------|------------|
| Core Web Vitals | All "Good" | PageSpeed Insights |
| Keyword rankings | Top 10 para keywords clave | Ahrefs, SEMrush |
| Organic traffic | Baseline + 30% en 6 meses | Google Analytics |
| Backlinks | +10 domains únicos/mes | Ahrefs |
| CTR from SERP | 3-5% (posición 1-3) | Google Search Console |
| Pogo-sticking rate | < 20% | Google Analytics |

## 7. Referencias Externas

**Herramientas:**
- Ahrefs (backlink analysis, keyword research)
- SEMrush (keyword tracking, competitive analysis)
- PageSpeed Insights (Core Web Vitals)
- Google Search Console (performance, indexing)
- Schema.org Validator (structured data)

**Lecturas complementarias:**
- Google Search Central: "Core Web Vitals"
- Google Search Central: "Structured Data"
- Backlinko blog: SEO case studies
