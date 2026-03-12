---
source_id: "FUENTE-M7-001"
brain: "brain-marketing-07-seo-technical"
niche: "marketing-digital"
title: "International SEO: Strategies for Global and Local Markets"
author: "Aleyda Solís"
expert_id: "EXP-M7-001"
type: "book"
language: "en"
year: 2022
isbn: "978-1735497523"
url: "https://www.aleydasolis.com/international-seo-book/"
skills_covered: ["H1", "H2", "H3", "H4", "H5"]
distillation_date: "2026-03-11"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-11"
changelog:
  - version: "1.0.0"
    date: "2026-03-11"
    changes:
      - "Ficha creada con destilación completa - International SEO"
status: "active"

habilidad_primaria: "International SEO: sistema completo para gestionar la visibilidad orgánica de sitios web en múltiples mercados y idiomas, desde la estrategia de geolocalización hasta la implementación técnica de hreflang y estructura de dominios"
habilidad_secundaria: "International SEO, multi-regional SEO, multi-lingual SEO, hreflang implementation, site migrations, ccTLDs vs subdomains vs subdirectories, geotargeting, international site architecture"
capa: 2
capa_nombre: "Framework Operativo"
relevancia: "CRÍTICA — Aleyda Solís es reconocida internacionalmente como una de las máximas autoridades en SEO técnico, especialmente en International SEO. Su libro es la referencia más completa sobre el tema. Es especialmente relevante para M7 porque aporta un framework estructurado para SEO técnico aplicado a mercados internacionales, cubriendo desde la estrategia hasta la implementación técnica de hreflang, estructura de dominios y migraciones."
---

# FUENTE-M7-001: International SEO — Aleyda Solís

## Tesis Central

> El International SEO no es solo traducir contenido, es gestionar la complejidad técnica de mostrar el contenido correcto al usuario correcto en el mercado correcto. Google usa señales específicas (hreflang, geolocalización, estructura de dominios) para entender la versión apropiada de tu sitio para cada usuario. El error más común es tratar el International SEO como una afterthought: cuando no planificás la arquitectura desde el inicio, terminás con problemas canónicos, contenido duplicado y confusión de Google. La clave es elegir la estructura correcta (ccTLD vs subdomain vs subdirectory) BASEADO EN tus recursos técnicos, tu equipo y tus objetivos de negocio — no por lo que hacen los competitors.

## 1. Principios Fundamentales

> **P1: Google no adivina, vos tenés que decirle explícitamente**
- Hreflang no es opcional para multi-idioma/multi-regional, es obligatorio
- Sin hreflang, Google elige la versión "mejor" (usualmente la wrong)
- Confusión de Google = Rankings perdidos + tráfico equivocado
> *Fuente: "Hreflang: Not Optional" (Solís, 2022)*

> **P2: Estructura de dominios es una decisión de 5-10 años, no algo que cambiás mañana**
- ccTLD (.es, .mx, .fr) = máximo señal geográfica pero máximo overhead técnico
- Subdirectories (/es/, /mx/, /fr/) = mejor balance señal vs overhead
- Subdomains (es.site.com, mx.site.com) = medio signal, medio overhead
> *Fuente: "Domain Structure Decision Framework" (Solís, 2022)*

> **P3: International SEO sin investigación de mercado es SEO a ciegas**
- No asumas que tu estrategia de US funciona en LATAM o Europa
- Cada mercado tiene diferente search behavior, competition, device usage
- Hacé keyword research POR MERCADO antes de decidir estructura
> *Fuente: "Market-Specific SEO Research" (Solís, 2022)*

> **P4: Las migraciones internacionales son donde más sitios se rompen**
- Migrar sin plan = pérdida del 40-60% de tráfico (temporal o permanente)
- Hreflang mal implementado en migración = desastre canónico
- Test en staging, migrate en fases, monitoreá como un loco las primeras 48h
> *Fuente: "Migration Pitfalls" (Solís, 2022)*

> **P5: Local no significa solo traducir, significa adaptar**
- Traducción literal vs transcreación (localización cultural)
- Fechas, monedas, formatos, imágenes, referencias culturales importan
- Usuario español nota cuando el contenido es "traducido por máquina"
> *Fuente: "Localization vs Translation" (Solís, 2022)*

## 2. Frameworks y Metodologías

### Framework 1: Elección de Estructura de Dominios

**Fuente:** "International SEO" (Solís, 2022)
**Propósito:** Decidir la estructura técnica para multi-regional/multi-lingual.
**Cuándo usar:** Al planificar expansión internacional o migración.

**Paso 1: Evaluación de Recursos**

| Recurso | Nivel Requerido |
|---------|-----------------|
| Equipo de desarrollo | Dedicado por mercado |
| Budget | Soportar N sitios |
| CMS | Multi-site capability |
| Autoridad de dominio | Suficiente para N sitios |
| Inversión link building | Por cada mercado |

**Paso 2: Matriz de Decisión**

**Usá ccTLD cuando:**
- Tenés equipo local en cada país
- Tenés budget para link building local
- Tu marca tiene fuerte presencia local
- Competidores usan ccTLD en ese mercado
- Ejemplo: site.es, site.mx, site.fr

**Usá subdirectories cuando:**
- Tenés un CMS centralizado
- No tenés equipo local en cada país
- Tu autoridad de dominio es alta
- Querés concentrar link equity
- Ejemplo: site.com/es/, site.com/mx/, site.com/fr/

**Usá subdomains cuando:**
- Tu CMS NO soporta subdirectories multi-idioma
- Tenés diferentes equipos técnicos por mercado
- Necesités hosting geo-localizado
- Ejemplo: es.site.com, mx.site.com, fr.site.com

**Paso 3: Validación Técnica**

```yaml
Requisitos ccTLD:
  - Registración de dominios por país
  - Hosting geo-localizado (ideal)
  - Google Search Console separado
  - Link building separado por país

Requisitos subdirectories:
  - CMS con soporte multi-language (hreflang auto)
  - Google Search Console con versiones especificadas
  - Geotargeting en GSC por subdirectory

Requisitos subdomains:
  - Configuración DNS correcta
  - Google Search Console separado
  - Hreflang cross-subdomain
```

### Framework 2: Implementación de Hreflang

**Fuente:** "International SEO" (Solís, 2022)
**Propósito:** Implementar correctamente hreflang para evitar contenido duplicado.
**Cuándo usar:** Siempre que tengas contenido multi-idioma/multi-regional.

**Regla 1: Hreflang va en TODAS las versiones**

```html
<!-- En site.com/es/ -->
<link rel="alternate" hreflang="es" href="https://site.com/es/" />
<link rel="alternate" hreflang="es-ES" href="https://site.com/es-es/" />
<link rel="alternate" hreflang="es-MX" href="https://site.com/es-mx/" />
<link rel="alternate" hreflang="en" href="https://site.com/en/" />
<link rel="alternate" hreflang="x-default" href="https://site.com/" />
```

**Regla 2: Usá códigos de idioma ISO 639-1 + región ISO 3166-1**

| Formato | Cuándo usar | Ejemplo |
|---------|-------------|---------|
| `hreflang="es"` | Español genérico | `/es/` |
| `hreflang="es-ES"` | Español España | `/es-es/` |
| `hreflang="es-MX"` | Español México | `/es-mx/` |
| `hreflang="en"` | Inglés genérico | `/en/` |
| `hreflang="x-default"` | Versión por defecto | `/` |

**Regla 3: Hreflang en XML Sitemap**

```xml
<!-- Para sitios grandes (más de 1000 páginas) -->
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>https://site.com/es/producto</loc>
    <xhtml:link rel="alternate" hreflang="es"
                 href="https://site.com/es/producto" />
    <xhtml:link rel="alternate" hreflang="es-ES"
                 href="https://site.com/es-es/producto" />
    <xhtml:link rel="alternate" hreflang="es-MX"
                 href="https://site.com/es-mx/producto" />
  </url>
</urlset>
```

**Regla 4: Evitá errores comunes**

| Error | Problema | Solución |
|-------|----------|----------|
| Hreflang apunta a 404 | Google ignora toda la cadena | Verificá todos los URLs |
| Hreflang en solo una versión | Google no puede entender la relación | Poné hreflang en TODAS |
| Hreflang sin `x-default` | Confusión sobre versión default | Siempre especificá default |
| Hreflang no returna | Google ignora la relación | A↔B, no solo A→B |

### Framework 3: Auditoría Técnica Internacional

**Fuente:** "International SEO" (Solís, 2022)
**Propósito:** Auditar problemas técnicos específicos de International SEO.
**Cuándo usar:** Antes de lanzamiento, migración o cuando haya caídas de tráfico.

**Checklist 1: Estructura de Dominios**

- [ ] Dominios registrados correctamente (ccTLDs)
- [ ] DNS configurado (A records, CNAME)
- [ ] HTTPS implementado en TODAS las versiones
- [ ] Hosting geolocalizado (ideal)
- [ ] Google Search Console verificada para cada versión

**Checklist 2: Hreflang**

- [ ] Hreflang implementado en todas las páginas
- [ ] Códigos de idioma/región correctos (ISO)
- [ ] URLs de destino son 200 (no 404/redirect)
- [ ] Bidireccionalidad respetada (A↔B, no solo A→B)
- [ ] X-default especificado
- [ ] Validación con Google Search Console → International Targeting

**Checklist 3: Contenido**

- [ ] Contenido traducido/localizado (no duplicado)
- [ ] Etiquetas `lang` en `<html>` (ej: `<html lang="es-ES">`)
- [ ] Meta tags localizados (title, description)
- [ ] URLs localizados (/es/producto vs /en/producto)
- [ ] Fechas/monedas/formateos localizados

**Checklist 4: Geolocalización**

- [ ] Google Search Console → International Targeting configurado
- [ ] Google My Business por país (local SEO)
- [ ] Datos estructurados con dirección local
- [ ] NAP (Name, Address, Phone) consistente

### Framework 4: Migraciones Internacionales

**Fuente:** "International SEO" (Solís, 2022)
**Propósito:** Migrar estructura internacional sin perder tráfico.
**Cuándo usar:** Al cambiar de ccTLD a subdirectories, consolidar mercados, etc.

**Fase 1: Pre-Migración (4-6 semanas antes)**

1. **Auditoría completa:**
   - Auditoría técnica de todas las versiones
   - Mapeo completo de URLs (old → new)
   - Análisis de backlinks por país
   - Baseline de tráfico/orgánicos/posiciones

2. **Preparación de redirects:**
   - 301 redirects de old → new
   - Preservación de hreflang en destination URLs
   - Test en staging environment

3. **Preparación de hreflang:**
   - Hreflang actualizado en destination URLs
   - XML sitemaps actualizados
   - Google Search Console verificado para nuevos dominios/paths

**Fase 2: Migración (Día D)**

1. **Lanzamiento:**
   - Activar 301 redirects
   - Actualizar hreflang
   - Actualizar sitemaps
   - Enviar a Google: "Fetch as Google" para URLs clave

2. **Monitoreo (primeras 48h):**
   - Google Search Console → Coverage Report
   - Google Search Console → International Targeting errors
   - Posiciones de keywords clave
   - Tráfico orgánico por país

**Fase 3: Post-Migración (4-6 semanas)**

| Métrica | Qué mirar | Alerta |
|---------|-----------|--------|
| Tráfico orgánico | Caídas > 30% | Investigá inmediatamente |
| Posiciones | Pérdida de top 10 | Revisá indexación |
| Indexación | Páginas no indexadas | Verificá robots.txt/sitemap |
| Hreflang errors | Google Search Console | Corregí errores |
| Rankings por país | Caídas específicas por mercado | Revisá localización |

## 3. Modelos Mentales

### Modelo 1: La Cadena de Señales Internacionales

```
Usuario en España
        ↓
Google: "¿Qué versión mostrar?"
        ↓
Señales técnicas:
  - hreflang explícito (60% peso)
  - Estructura de dominio (20% peso)
  - Geolocalización de servidor (10% peso)
  - Contenido localizado (10% peso)
        ↓
Decisión: /es-es/ vs /es-mx/ vs /es/
```

**Key insight:** Hreflang es la señal más fuerte. Sin hreflang, Google adivina (y suele errar).

### Modelo 2: El Triángulo de Trade-offs de Estructura

```
       ccTLD
         ▲
  Señal ├──┐ Overhead técnico
  fuerte │  │ alto
         │  │
  Subdomains │ medio
         │  │
         │  ▼
  Subdirectories
  Señal media ├── Overhead bajo
```

**Key insight:** No existe la "mejor" estructura. Existe la mejor estructura PARA TUS RECURSOS.

### Modelo 3: La Complejidad de N Mercados

```
Complejidad = Mercados × Idiomas × Estructuras × Equipo

1 mercado, 1 idioma = Complejidad baja
5 mercados, 3 idiomas = Complejidad media
10 mercados, 5 idiomas = Complejidad alta (necesitás equipo dedicado)
```

**Key insight:** International SEO escala exponencialmente, no linealmente. Planificá en consecuencia.

## 4. Criterios de Decisión

### Decisión 1: ¿ccTLD, Subdomain o Subdirectory?

**Elegí ccTLD si:**
- Tu autoridad de dominio es alta (DA > 60)
- Tenés budget para link building en cada país
- Tu modelo de negocio requiere presencia local fuerte
- Competidores ya usan ccTLD en ese mercado
- Tenés equipo local/marketing local en cada país

**Elegí subdirectory si:**
- Tu autoridad de dominio es media-alta
- Tenés recursos limitados para gestionar múltiples sitios
- Tu CMS soporta multi-language
- Querés concentrar autoridad en un dominio
- Tu equipo es centralizado

**Elegí subdomain si:**
- Tu CMS NO soporta subdirectories multi-language
- Tenés diferentes equipos técnicos por mercado
- Necesités hosting geo-localizado específico
- Estás en una transición (migración futura a ccTLD o subdirectory)

### Decisión 2: ¿Hreflang en `<head>` o Sitemap?

**Usá `<head>` cuando:**
- Tu sitio tiene < 1000 páginas
- Tu CMS puede manejar hreflang dinámico
- Tenés control total del HTML
- Tu sitio cambia frecuentemente

**Usá XML Sitemap cuando:**
- Tu sitio tiene > 1000 páginas
- Tu CMS tiene limitaciones con `<head>`
- Tu sitio es relativamente estático
- Tenéis procesos de deployment automatizados

### Decisión 3: ¿Traducir o Transcrear?

**Traducí (cuando:**
- Contenido técnico/informativo
- Documentación, especificaciones
- Contenido B2B donde la precisión importa
- Mercados con similar comportamiento

**Transcribí (cuando:**
- Contenido de marketing/branding
- Landing pages de conversión
- Contenido B2C donde la cultura importa
- Mercados con comportamiento muy diferente

## 5. Anti-patrones

### Anti-patrón 1: "Google me entiende, no necesito hreflang"

**Problema:** Google NO te entiende. Google elige la versión "mejor" según su algoritmo, que suele ser la wrong.

**Consecuencias:**
- Usuarios en México ven contenido de España
- Traficado filtrado a la versión incorrecta
- Rankings diluidos entre versiones

**Solución:** Implementá hreflang SIEMPRE para multi-idioma/multi-regional.

### Anti-patrón 2: "Traduzco todo con DeepL y listo"

**Problema:** Traducción automática sin revisión humana = contenido duplicado + mala experiencia.

**Consecuencias:**
- Google detecta contenido duplicado (o cercano a duplicado)
- Usuarios notan el contenido "robótico"
- Branding afectado negativamente

**Solución:** Usá traducción automática como base, pero siempre con revisión humana.

### Anti-patrón 3: "Migro primero y arreglo después"

**Problema:** Migrar sin testing = pérdida del 40-60% de tráfico.

**Consecuencias:**
- Rankings perdidos (temporal o permanentemente)
- Hreflang roto en la migración
- Experiencia de usuario degradada

**Solución:** Test en staging, migrate en fases, monitoreá intensivamente las primeras 48h.

### Anti-patrón 4: "Copio la estructura de mi competitor"

**Problema:** Lo que funciona para tu competitor puede NO funcionar para vos (diferentes recursos, equipo, autoridad).

**Consecuencias:**
- Elegís ccTLD sin tener budget para link building local
- Tu CMS no soporta la estructura elegida
- Tu equipo no puede gestionar N sitios

**Solución:** Elegí estructura basado en TUS recursos, no en lo que hacen otros.

### Anti-patrón 5: "Una vez implementado, me olvido"

**Problema:** International SEO requiere monitoreo constante. Los mercados cambian, Google cambia, tu negocio cambia.

**Consecuencias:**
- Hreflang roto sin que te des cuenta
- Mercados nuevos sin implementación correcta
- Competencia te adelanta

**Solución:** Auditoría trimestral de International SEO, monitoreo continuo en GSC.

## 6. Checklists de Implementación

### Checklist de Lanzamiento

**Pre-lanzamiento:**
- [ ] Estructura de dominios definida
- [ ] Hreflang implementado en todas las páginas
- [ ] XML sitemaps con hreflang
- [ ] Google Search Console verificado
- [ ] International Targeting configurado
- [ ] Contenido localizado (no solo traducido)
- [ ] Etiquetas `lang` en `<html>`
- [ ] HTTPS en todas las versiones
- [ ] Robots.txt y sitemaps correctos
- [ ] Test completo en staging

**Post-lanzamiento (semanas 1-4):**
- [ ] Monitoreo diario de tráfico orgánico
- [ ] Google Search Console → International Targeting errors
- [ ] Posiciones de keywords clave
- [ ] Indexación de nuevas páginas
- [ ] Backlinks apuntando a URLs correctas
- [ ] Velocidad de carga por mercado
- [ ] Experience de usuario móvil por país

## 7. Métricas de Éxito

| Métrica | Benchmark | Cómo medir |
|---------|-----------|------------|
| Tráfico orgánico por país | Baseline + 20% en 6 meses | Google Analytics |
| Posiciones internacionales | Top 10 para keywords clave | Google Search Console |
| Hreflang errors | < 1% de URLs | Google Search Console |
| Indexación | 95%+ de páginas indexadas | Google Search Console |
| Velocidad de carga | < 3s en todos los mercados | PageSpeed Insights |
| Conversion rate | Estable o + vs baseline | Google Analytics |

## 8. Referencias Externas

**Herramientas:**
- Google Search Console → International Targeting Report
- Aleyda's Hreflang Tags Generator Tool
- DeepCrawl → International SEO auditing
- SEMrush → Position tracking by country

**Lecturas complementarias:**
- Google Search Central: "Hreflang" (Official documentation)
- Aleyda Solís blog: "International SEO Case Studies"
- Moz: "The Complete Guide to International SEO"
