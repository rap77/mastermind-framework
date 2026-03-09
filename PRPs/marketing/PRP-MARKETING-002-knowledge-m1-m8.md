# PRP-MARKETING-002: Nicho Marketing Digital - Knowledge Base M1-M8

**Status:** Ready to Implement (after PRP-MARKETING-001)
**Priority:** High
**Estimated Time:** 30-40 hours
**Dependencies:** PRP-MARKETING-001 (Foundation)

---

## Executive Summary

Crear la base de conocimiento (fuentes maestras) para los primeros 8 cerebros del nicho Marketing Digital: Strategy, Brand, Content, Social Organic, Social Paid, Search PPC, SEO Technical, y SEO Content. Esto incluye investigación, destilación, y carga en NotebookLM de ~80 fuentes.

---

## Context from Requirements

### Decisiones Críticas

1. **~10 fuentes por cerebro:** Balance entre cobertura y esfuerzo
2. **Expertos sin preferencia:** Mezcla de hispanos e internacionales según conocimiento necesario (no hay cuota)
3. **Destilación de 5 capas:** Principios, Frameworks, Modelos Mentales, Criterios de Decisión, Anti-patrones
4. **YAML front matter:** Formato estándar para portabilidad
5. **NotebookLM por cerebro:** 8 notebooks (uno por cerebro M1-M8)

### Expertos a Cubrir (M1-M8)

| Cerebro | Expertos Clave (~10 cada uno) |
|---------|------------------------------|
| **M1: Strategy** | April Dunford, Andy Cunningham, Marty Neumeier, Elena Verna, Kyle Poyar, Christopher Lochhead, Seth Godin, Geoffrey Moore, Margarita Pasos (México), Sergi Silva (España) |
| **M2: Brand** | Sagi Haviv, Debbie Millman, Alina Wheeler, Brian Collins, David Aaker, Marty Neumeier, Fernando Del Vecchio (Argentina), Nuria Vilanova (España), Mario García (España), Rubén Fontana (Argentina) |
| **M3: Content** | Joanna Wiebe, Joe Pulizzi, Donald Miller, Andy Crestodina, Amy Posner, Neville Medhora, Patricia Soto (México), Luis M. Villar (México), Christian Rennella (Argentina), Germán Rondón (Venezuela) |
| **M4: Social Organic** | Jasmine Star, Rachel Pedersen, Justin Welsh, Katelyn Bourgoin, Brianne Fleming, Codie Sanchez, Margarita Pasos (México), Lidia García (España), Natalia 'TuTia' (Colombia), César Sandoval (México) |
| **M5: Social Paid** | Dennis Yu, Nicholas Kusmich, Molly Pittman, Ernie San, AJ Wilcox, Tom Breeze, Sergio Rama (España), Emi Gallego (México), Lidia García (España), Sebastián Gómez (Colombia) |
| **M6: Search PPC** | Perry Marshall, Mike Rhodes, Frederick Vallaeys, Larry Kim, Oli Gardner, Jesús Tronchoni (España), Alejandro Magallanes (México), Hanapin experts, Unbounce team, AdRoll experts |
| **M7: SEO Technical** | Aleyda Solís (España), Brian Dean, Barry Schwartz, Cyrus Shepard, Annie Cushing, Marie Haynes, Fernando Muñoz (España), Jesús Tronchoni (España), Rand Fishkin, Google Search Central |
| **M8: SEO Content** | Andy Crestodina, Jon Cooper, Lily Ray, Ross Hudgens, Neil Patel, Germán Rondón (Venezuela), Jesús Tronchoni (España), Stuart Davidson, Joy Hawkins, Marie Haynes |

**Total: ~80 expertos a investigar y destilar**

---

## External Resources

### Fuentes Maestras de Expertos

**Positioning & Strategy (M1):**
- April Dunford: https://www.aprildunford.com/blog/ - Obviously Awesome book
- Andy Cunningham: "Positioning" book
- Marty Neumeier: "Zag" and "The Brand Gap" books
- Elena Verna: https://elenaverna.com/ - PLG and growth content
- Kyle Poyar: https://kylepoyar.substack.com/ - PLG content
- Christopher Lochhead: "Play Bigger" book and podcast
- Seth Godin: https://seths.blog/ - Daily blog
- Geoffrey Moore: "Crossing the Chasm" book
- Margarita Pasos: https://www.margaritapasos.com/ - Contenido en español
- Sergi Silva: https://www.sergisilva.com/ - Positioning en español

**Brand Identity (M2):**
- Sagi Haviv: https://www.chermayeff.com/ - Case studies
- Debbie Millman: https://debbiemillman.com/ - Design matters podcast
- Alina Wheeler: "Designing Brand Identity" book
- Brian Collins: https://collins1.com/ - Work and methodology
- David Aaker: Brand books and articles
- Marty Neumeier: Brand strategy books
- Fernando Del Vecchio: https://www.fdvd.com.ar/ - Branding en español
- Nuria Vilanova: https://www.vilanovastrings.com/ - Branding estratégico en español
- Mario García: https://www.garcia-media.com/ - Identidad visual en español
- Rubén Fontana: http://www.rubenfontana.com.ar/ - Diseño de marca en español

**Copywriting & Content (M3):**
- Joanna Wiebe: https://copyhackers.com/blog/ - Copywriting resources
- Joe Pulizzi: https://contentmarketinginstitute.com/blog/ - Content Marketing Institute
- Donald Miller: "StoryBrand" book and framework
- Andy Crestodina: https://www.orbitmedia.com/blog/ - Content marketing
- Amy Posner: Copywriting resources
- Neville Medhora: https://nevillemedhurst.com/ - Copywriting
- Patricia Soto: https://www.patriciasoto.com/ - Copywriting en español
- Luis M. Villar: https://www.luis-m-villar.com/ - Content marketing en español
- Christian Rennella: https://www.christianrennella.com/ - Storytelling en español
- Germán Rondón: https://www.germanrondon.com/ - SEO content en español

**Social Media Organic (M4):**
- Jasmine Star: https://jasminestar.com/ - Social media strategy
- Rachel Pedersen: https://rachelpedersen.com/ - Social media marketing
- Justin Welsh: https://www.justinwelsh.me/ - LinkedIn and social selling
- Katelyn Bourgoin: https://katelynbourgoin.com/ - Customer research
- Brianne Fleming: https://briennefleming.com/ - Social media and community
- Codie Sanchez: https://www.codie-sanchez.com/ - Social media and business
- Margarita Pasos: https://www.margaritapasos.com/ - Social media en español
- Lidia García: https://www.linkedin.com/in/lidigarcia/ - LinkedIn en español
- Natalia Restrepo (TuTia): TikTok strategies en español
- César Sandoval: Twitter/X strategies en español

**Social Media Paid (M5):**
- Dennis Yu: https://www.blitzmetrics.com/ - Facebook Ads strategies
- Nicholas Kusmich: https://hussle.media/ - Facebook Ads
- Molly Pittman: https://www.mollypittman.com/ - Paid advertising
- Ernie San: Creative strategy for ads
- AJ Wilcox: https://www.b2linked.com/ - LinkedIn Ads
- Tom Breeze: https://www.viewability.com/ - YouTube Ads
- Sergio Rama: https://www.sergiorama.com/ - Meta Ads en español
- Emi Gallego: TikTok Ads en español
- Lidia García: LinkedIn Ads en español
- Sebastián Gómez: YouTube Ads en español

**Search PPC (M6):**
- Perry Marshall: https://www.perrymarshall.com/ - Google Ads definitive guide
- Mike Rhodes: https://www.mikeworks.com.au/ - Google Ads
- Frederick Vallaeys: https://www.optmyzr.com/blog/ - Google Ads strategies
- Larry Kim: https://www.wordstream.com/blog - SEM strategies
- Oli Gardner: https://unbounce.com/blog/ - Landing page optimization
- Jesús Tronchoni: https://www.jestrong.com/ - Google Ads en español
- Alejandro Magallanes: https://www.alejandro-magallanes.com/ - SEM en español
- Hanapin Marketing: https://www.hanapinmarketing.com/blog/ - PPC resources
- AdRoll: https://www.adroll.com/resources - Retargeting
- Microsoft Ads: https://about.ads.microsoft.com/en-us/resources/blog - Bing Ads

**SEO Technical (M7):**
- Aleyda Solís: https://www.aleydasolis.com/en/blog/ - SEO técnico (hispana)
- Brian Dean: https://backlinko.com/ - SEO resources
- Barry Schwartz: https://www.seroundtable.com/ - SEO news
- Cyrus Shepard: https://www.cyrusshepard.com/ - SEO technical
- Annie Cushing: https://www.anniecushing.com/ - Technical SEO
- Marie Haynes: https://www.mariehaynes.com/ - SEO and quality
- Fernando Muñoz: https://www.fernandomunoz.es/ - SEO técnico en español
- Jesús Tronchoni: https://www.jestrong.com/ - SEO en español
- Rand Fishkin: https://sparktoro.com/blog/ - SEO insights
- Google Search Central: https://developers.google.com/search/blog - Official SEO docs

**SEO Content & Link Building (M8):**
- Andy Crestodina: https://www.orbitmedia.com/blog/ - Content SEO
- Jon Cooper: https://pointblankseo.com/ - Link building
- Lily Ray: https://www.lilyray.nyc/ - E-E-A-T and SEO
- Ross Hudgens: https://rosshudgens.com/ - SEO content
- Neil Patel: https://neilpatel.com/blog/ - SEO and marketing
- Germán Rondón: https://www.germanrondon.com/ - SEO content en español
- Jesús Tronchoni: https://www.jestrong.com/ - Link building en español
- Stuart Davidson: https://www.searchenginejournal.com/ - SEO news
- Joy Hawkins: https://www.sterlingsky.ca/ - Local SEO
- Marie Haynes: https://www.mariehaynes.com/ - Quality content

---

## Implementation Blueprint

### Proceso de Creación de Fuente Maestra

Para cada experto:
1. **Investigación** (30-45 min)
   - Buscar libros principales, blogs, cursos, podcasts
   - Identificar contenido más relevante (no todo)
   - Encontrar URLs de recursos clave

2. **Destilación** (1-2 hours)
   - Crear archivo FUENTE-XXX.md con YAML front matter
   - Escribir 5 secciones de destilación:
     1. Principios Fundamentales (3-5 principios clave)
     2. Frameworks y Metodologías (2-4 frameworks)
     3. Modelos Mentales (2-3 modelos)
     4. Criterios de Decisión (trade-offs profesionales)
     5. Anti-patrones (errores comunes a evitar)

3. **Validación** (15 min)
   - Revisar calidad de destilación
   - Verificar formato correcto
   - Validar YAML front matter

4. **Carga a NotebookLM** (15 min)
   - Agregar fuente al notebook del cerebro correspondiente
   - Marcar `loaded_in_notebook: true` en YAML

### Formato de Fuente Maestra (Template)

```yaml
---
source_id: "FUENTE-M{NÚMERO}-{SERIE}"
brain: "brain-marketing-0{N}-[short-id]"
niche: "marketing-digital"
title: "[Título del libro/recurso principal]"
author: "[Nombre del experto]"
expert_id: "EXP-M{NÚMERO}-{SERIE}"
type: "book|course|blog|podcast|newsletter"
language: "en|es"
year: [Año]
isbn: "[ISBN si es libro]"
url: "[URL principal del recurso]"
skills_covered: ["H1", "H3", "H5"]  # Skills cubiertas del cerebro
distillation_date: "[YYYY-MM-DD]"
distillation_quality: "complete|partial"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "[YYYY-MM-DD]"
changelog:
  - version: "1.0.0"
    date: "[YYYY-MM-DD]"
    changes:
      - "Ficha creada con destilación completa"
status: "active"

habilidad_primaria: "[Una frase describiendo la habilidad principal]"
habilidad_secundaria: "[Habilidades secundarias]"
capa: 1
capa_nombre: "Base Conceptual|Framework Operativo|Modelo Mental|Criterio de Decisión|Mecanismo de Retroalimentación"
relevancia: "[CRÍTICA|ALTA|MEDIA|BAJA — Justificación de por qué este experto es relevante]"
---

# FUENTE-M{NÚMERO}-{SERIE}: [Título]

## Tesis Central

> [Una frase que capture la idea central del experto]

---

## 1. Principios Fundamentales

> **P1: [Principio 1]**
> [Descripción detallada del principio]
> *Contexto: [Cuándo aplicar este principio]*

> **P2: [Principio 2]**
> [Descripción detallada del principio]
> *Contexto: [Cuándo aplicar este principio]*

[...]

---

## 2. Frameworks y Metodologías

### Framework 1: [Nombre del Framework]

**Propósito:** [Cuál es el propósito de este framework]
**Cuándo usar:** [En qué situaciones aplicar]

**Pasos/Componentes:**
1. [Paso 1]
2. [Paso 2]
3. [Paso 3]

**Output esperado:** [Qué resultado se obtiene]

---

## 3. Modelos Mentales

### Modelo Mental 1: [Nombre]

**El modelo:** [Descripción del modelo]
**Por qué funciona:** [Explicación]
**Cuándo usarlo:** [Situaciones donde aplica]
**Limitaciones:** [Cuándo NO usarlo]

---

## 4. Criterios de Decisión

### Trade-off: [Nombre del trade-off]

**Opción A:** [Descripción]
- **Ventajas:** [Lista]
- **Desventajas:** [Lista]
- **Mejor para:** [Cuándo elegir esta opción]

**Opción B:** [Descripción]
- **Ventajas:** [Lista]
- **Desventajas:** [Lista]
- **Mejor para:** [Cuándo elegir esta opción]

**Recomendación del experto:** [Qué opina el experto]

---

## 5. Anti-patrones

### Anti-patrón 1: [Nombre]

**Qué es:** [Descripción del error]
**Por qué la gente lo hace:** [Causa común]
**Consecuencias:** [Qué pasa si lo haces]
**Cómo evitarlo:** [Mejor práctica]
**Qué hacer en su lugar:** [Alternativa correcta]

---

## Referencias

- **Libro principal:** [Título, ISBN]
- **Blog:** [URL]
- **Curso:** [URL si aplica]
- **Podcast:** [URL si aplica]
- **Newsletter:** [URL si aplica]

---

## Notas Adicionales

[Espacio para notas específicas sobre este experto que no caben en las secciones anteriores]
```

---

## Tasks (in Order)

### Task 1: Crear Notebooks en NotebookLM (2 hours)
- [ ] Iniciar sesión en NotebookLM
- [ ] Crear 8 notebooks con formato: `[CEREBRO] {Nombre} - Marketing Digital`
  - [ ] Notebook M1: Marketing Strategy & Positioning
  - [ ] Notebook M2: Brand Identity & Design
  - [ ] Notebook M3: Content Strategy & Copywriting
  - [ ] Notebook M4: Social Media Organic
  - [ ] Notebook M5: Social Media Paid
  - [ ] Notebook M6: Search PPC (Google/Bing)
  - [ ] Notebook M7: SEO Technical
  - [ ] Notebook M8: SEO Content & Link Building
- [ ] Copiar notebook_id de cada uno a archivo temporal
- [ ] Output: 8 notebooks creados con IDs documentados

### Task 2: Investigar y Destilar - M1 Strategy (5 hours)
- [ ] **FUENTE-M1-001**: April Dunford - Obviously Awesome
  - [ ] Investigar libro y blog
  - [ ] Destilar 5 secciones
  - [ ] Cargar a NotebookLM M1
- [ ] **FUENTE-M1-002**: Andy Cunningham - Positioning
  - [ ] Investigar libro y recursos
  - [ ] Destilar 5 secciones
  - [ ] Cargar a NotebookLM M1
- [ ] **FUENTE-M1-003**: Marty Neumeier - Zag & Brand Gap
  - [ ] Investigar libros
  - [ ] Destilar 5 secciones
  - [ ] Cargar a NotebookLM M1
- [ ] **FUENTE-M1-004**: Elena Verna - PLG content
  - [ ] Investigar blog y talks
  - [ ] Destilar 5 secciones
  - [ ] Cargar a NotebookLM M1
- [ ] **FUENTE-M1-005**: Kyle Poyar - PLG content
  - [ ] Investigar substack y recursos
  - [ ] Destilar 5 secciones
  - [ ] Cargar a NotebookLM M1
- [ ] **FUENTE-M1-006**: Christopher Lochhead - Play Bigger
  - [ ] Investigar libro y podcast
  - [ ] Destilar 5 secciones
  - [ ] Cargar a NotebookLM M1
- [ ] **FUENTE-M1-007**: Seth Godin - Blog and books
  - [ ] Investigar blog y libros principales
  - [ ] Destilar 5 secciones
  - [ ] Cargar a NotebookLM M1
- [ ] **FUENTE-M1-008**: Geoffrey Moore - Crossing the Chasm
  - [ ] Investigar libro
  - [ ] Destilar 5 secciones
  - [ ] Cargar a NotebookLM M1
- [ ] **FUENTE-M1-009**: Margarita Pasos - Estrategia digital
  - [ ] Investigar recursos en español
  - [ ] Destilar 5 secciones
  - [ ] Cargar a NotebookLM M1
- [ ] **FUENTE-M1-010**: Sergi Silva - Positioning en español
  - [ ] Investigar recursos
  - [ ] Destilar 5 secciones
  - [ ] Cargar a NotebookLM M1
- [ ] Output: 10 fuentes creadas en `docs/nichos/marketing-digital/sources/BRAIN-01-STRATEGY/`

### Task 3: Investigar y Destilar - M2 Brand (4 hours)
- [ ] Crear 10 fuentes para Brand Identity & Design (lista de expertos arriba)
- [ ] Cada fuente: investigar → destilar → cargar a NotebookLM M2
- [ ] Output: 10 fuentes en `docs/nichos/marketing-digital/sources/BRAIN-02-BRAND/`

### Task 4: Investigar y Destilar - M3 Content (4 hours)
- [ ] Crear 10 fuentes para Content Strategy & Copywriting
- [ ] Cada fuente: investigar → destilar → cargar a NotebookLM M3
- [ ] Output: 10 fuentes en `docs/nichos/marketing-digital/sources/BRAIN-03-CONTENT/`

### Task 5: Investigar y Destilar - M4 Social Organic (4 hours)
- [ ] Crear 10 fuentes para Social Media Organic
- [ ] Cada fuente: investigar → destilar → cargar a NotebookLM M4
- [ ] Output: 10 fuentes en `docs/nichos/marketing-digital/sources/BRAIN-04-SOCIAL-ORGANIC/`

### Task 6: Investigar y Destilar - M5 Social Paid (4 hours)
- [ ] Crear 10 fuentes para Social Media Paid
- [ ] Cada fuente: investigar → destilar → cargar a NotebookLM M5
- [ ] Output: 10 fuentes en `docs/nichos/marketing-digital/sources/BRAIN-05-SOCIAL-PAID/`

### Task 7: Investigar y Destilar - M6 Search PPC (4 hours)
- [ ] Crear 10 fuentes para Search PPC (Google/Bing)
- [ ] Cada fuente: investigar → destilar → cargar a NotebookLM M6
- [ ] Output: 10 fuentes en `docs/nichos/marketing-digital/sources/BRAIN-06-SEARCH-PPC/`

### Task 8: Investigar y Destilar - M7 SEO Technical (4 hours)
- [ ] Crear 10 fuentes para SEO Technical
- [ ] Cada fuente: investigar → destilar → cargar a NotebookLM M7
- [ ] Output: 10 fuentes en `docs/nichos/marketing-digital/sources/BRAIN-07-SEO-TECHNICAL/`

### Task 9: Investigar y Destilar - M8 SEO Content (4 hours)
- [ ] Crear 10 fuentes para SEO Content & Link Building
- [ ] Cada fuente: investigar → destilar → cargar a NotebookLM M8
- [ ] Output: 10 fuentes en `docs/nichos/marketing-digital/sources/BRAIN-08-SEO-CONTENT/`

### Task 10: Actualizar brains-marketing.yaml (30 min)
- [ ] Para cada cerebro M1-M8:
  - [ ] Agregar notebook_id correspondiente
  - [ ] Actualizar sources_count a 10
  - [ ] Validar syntax
- [ ] Output: `mastermind_cli/config/brains-marketing.yaml` actualizado

### Task 11: Validación de Calidad (1 hour)
- [ ] Para cada fuente creada (80 total):
  - [ ] Verificar YAML front matter válido
  - [ ] Verificar 5 secciones completas
  - [ ] Verificar loaded_in_notebook: true
  - [ ] Verificar calidad de destilación (no solo copiar/pegar)
- [ ] Para cada notebook M1-M8:
  - [ ] Verificar que tenga 10 fuentes cargadas
  - [ ] Hacer 1 query de test en cada notebook
- [ ] Output: Checklist de validación completado

### Task 12: Documentación (30 min)
- [ ] Actualizar `docs/nichos/marketing-digital/README.md` con:
  - Status de M1-M8: "Knowledge Complete"
  - Links a notebooks
  - Count de fuentes por cerebro
- [ ] Crear `docs/nichos/marketing-digital/SOURCES-M1-M8.md` con:
  - Índice de todas las fuentes creadas
  - Mapeo experto → FUENTE-ID
- [ ] Output: 2 archivos de documentación

### Task 13: Git Commit (15 min)
- [ ] Revisar cambios con `git status`
- [ ] Commit: `feat(marketing): add knowledge base for brains M1-M8 (80 sources)`

---

## Validation Gates

```bash
# 1. Verificar 80 fuentes creadas
find docs/nichos/marketing-digital/sources/BRAIN-0{1..8} -name "FUENTE-*.md" | wc -l
# Expected: 80

# 2. Verificar YAML syntax de todas las fuentes
for file in docs/nichos/marketing-digital/sources/BRAIN-*/FUENTE-*.md; do
  python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>&1 | grep -q "error" && echo "ERROR: $file"
done
# Expected: No ERROR messages

# 3. Verificar cada fuente tiene las 5 secciones
for file in docs/nichos/marketing-digital/sources/BRAIN-0{1..8}/FUENTE-*.md; do
  grep -q "## 1. Principios Fundamentales" "$file" || echo "MISSING Section 1 in $file"
  grep -q "## 2. Frameworks y Metodologías" "$file" || echo "MISSING Section 2 in $file"
  grep -q "## 3. Modelos Mentales" "$file" || echo "MISSING Section 3 in $file"
  grep -q "## 4. Criterios de Decisión" "$file" || echo "MISSING Section 4 in $file"
  grep -q "## 5. Anti-patrones" "$file" || echo "MISSING Section 5 in $file"
done
# Expected: No MISSING messages

# 4. Verificar loaded_in_notebook: true en todas las fuentes
grep -r "loaded_in_notebook: false" docs/nichos/marketing-digital/sources/BRAIN-0{1..8}/
# Expected: No results (todas deben ser true)

# 5. Verificar brains-marketing.yaml actualizado
grep -A2 "id: M[1-8]" mastermind_cli/config/brains-marketing.yaml | grep "notebook_id"
# Expected: 8 notebook_ids (no null)
grep -A2 "id: M[1-8]" mastermind_cli/config/brains-marketing.yaml | grep "sources_count: 10"
# Expected: 8 occurrences

# 6. Verificar distribución de expertos hispanos (~20-30%)
grep -r "language: \"es\"" docs/nichos/marketing-digital/sources/BRAIN-0{1..8}/ | wc -l
# Expected: 16-24 (20-30% de 80)

# 7. Test de calidad: verificar que no sean copias literales
# Buscar patrones de copy/paste (mismo texto en múltiples fuentes)
for file in docs/nichos/marketing-digital/sources/BRAIN-0{1..8}/FUENTE-*.md; do
  # Verificar que tenga análisis original (no solo citas)
  wc -w "$file" | awk '{if ($1 < 500) print "TOO SHORT: " FILENAME}' FILENAME="$file"
done
# Expected: No TOO SHORT messages (mínimo 500 palabras por fuente)

# 8. Test de completitud por cerebro
for i in {1..8}; do
  count=$(find docs/nichos/marketing-digital/sources/BRAIN-0$i -name "FUENTE-*.md" | wc -l)
  echo "Brain M$i: $count sources"
  if [ "$count" -lt 10 ]; then
    echo "ERROR: Brain M$i has less than 10 sources"
  fi
done
# Expected: Each brain shows 10 sources
```

---

## Definition of Done

- [ ] 80 fuentes maestras creadas (10 por cerebro M1-M8)
- [ ] Todas las fuentes tienen YAML front matter válido
- [ ] Todas las fuentes tienen 5 secciones de destilación completas
- [ ] Todas las fuentes marcadas con `loaded_in_notebook: true`
- [ ] 8 notebooks creados en NotebookLM con IDs documentados
- [ ] `brains-marketing.yaml` actualizado con notebook_ids y sources_count
- [ ] 20-30% de fuentes en español (expertos hispanos)
- [ ] Validación de calidad pasada (no copy/paste, mínimo 500 palabras)
- [ ] Documentación actualizada (README + SOURCES-M1-M8.md)
- [ ] Git commit con cambios
- [ ] **TEST DE COMPLETITUD:** Cada cerebro M1-M8 tiene exactamente 10 fuentes cargadas en NotebookLM

---

## Error Handling Strategy

| Error | Acción |
|-------|--------|
| No se encuentra recurso del experto | Buscar alternativas (libros, cursos, podcasts) |
| YAML syntax error | Validar línea por línea, verificar indentación y quotes |
| Fuente muy corta (<500 palabras) | Expandir con más principios/frameworks |
| NotebookLM rechaza fuente | Verificar formato, intentar con texto plano |
| Distribución de expertos sesgada | No es error si la calidad está, solo tracking |
| No hay suficiente contenido hispano | No es obligatorio, solo preferencia |

---

## Gotchas & Notes

1. **Calidad > Cantidad:** Es mejor 8 fuentes bien destiladas que 10 superficiales. 500 palabras mínimo por fuente.

2. **Expertos hispanos NO son obligatorios:** Usarlos si su conocimiento es relevante. No hay cuota.

3. **Destilación NO es resumen:** No basta con copiar partes del libro. Hay que sintetizar en las 5 categorías del framework.

4. **NotebookLM tiene límites:** No cargar más de 10-15 fuentes por notebook para mantener calidad.

5. **Investigación toma tiempo:** 30-45 min por experto es normal. No shortcuttear esta parte.

6. **Repetición es válida:** Si dos expertos cubren lo mismo, está bien. Cada uno tiene su perspectiva.

7. **URLs pueden cambiar:** Guardar el contenido clave en la destilación, no solo links.

---

## Files Created/Modified

| Archivo | Acción | Propósito |
|---------|--------|-----------|
| `docs/nichos/marketing-digital/sources/BRAIN-01-STRATEGY/FUENTE-M1-*.md` | Crear | 10 fuentes de estrategia |
| `docs/nichos/marketing-digital/sources/BRAIN-02-BRAND/FUENTE-M2-*.md` | Crear | 10 fuentes de branding |
| `docs/nichos/marketing-digital/sources/BRAIN-03-CONTENT/FUENTE-M3-*.md` | Crear | 10 fuentes de contenido |
| `docs/nichos/marketing-digital/sources/BRAIN-04-SOCIAL-ORGANIC/FUENTE-M4-*.md` | Crear | 10 fuentes de social orgánico |
| `docs/nichos/marketing-digital/sources/BRAIN-05-SOCIAL-PAID/FUENTE-M5-*.md` | Crear | 10 fuentes de social pago |
| `docs/nichos/marketing-digital/sources/BRAIN-06-SEARCH-PPC/FUENTE-M6-*.md` | Crear | 10 fuentes de search PPC |
| `docs/nichos/marketing-digital/sources/BRAIN-07-SEO-TECHNICAL/FUENTE-M7-*.md` | Crear | 10 fuentes de SEO técnico |
| `docs/nichos/marketing-digital/sources/BRAIN-08-SEO-CONTENT/FUENTE-M8-*.md` | Crear | 10 fuentes de SEO contenido |
| `mastermind_cli/config/brains-marketing.yaml` | Modificar | Agregar notebook_ids y sources_count |
| `docs/nichos/marketing-digital/SOURCES-M1-M8.md` | Crear | Índice de fuentes M1-M8 |

---

## Next Steps

After this PRP:
- → **PRP-MARKETING-003**: Knowledge Base M9-M16 (~80 fuentes para cerebros restantes)

---

## Confidence Score

**8/10** - Alta confianza de éxito.

**Rationale:**
- Proceso claro y bien definido
- Template de fuente maestra es específico
- Expertos están identificados
- Validation gates son ejecutables

**Riesgos:**
- Tiempo de investigación puede ser mayor al estimado
- Algunos expertos pueden tener menos recursos disponibles de lo esperado
- NotebookLM puede tener limitaciones de carga

---

## Context for AI Agent

**Archivos clave para leer antes de implementar:**
1. `/home/rpadron/proy/mastermind/docs/software-development/06-qa-devops-brain/sources/FUENTE-602-accelerate-forsgren-humble-kim.md` - Ejemplo completo de fuente maestra
2. `/home/rpadron/proy/mastermind/mastermind_cli/config/brains-marketing.yaml` - Config a actualizar
3. Este PRP completo - Para proceso y lista de expertos

**Comando para iniciar:**
```bash
cd /home/rpadron/proy/mastermind

# 1. Crear notebooks en NotebookLM (manual)
# Ir a https://notebooklm.google.com y crear 8 notebooks

# 2. Crear primera fuente como ejemplo
mkdir -p docs/nichos/marketing-digital/sources/BRAIN-01-STRATEGY/
# Usar el template de este PRP para crear FUENTE-M1-001-aprildunford.md

# 3. Continuar con las 79 fuentes restantes
```

**Resultado esperado:**
80 fuentes maestras creadas, cargadas en 8 notebooks de NotebookLM, configs actualizadas, validación de calidad pasada.

**TEST DE COMPLETITUD CRÍTICO:**
```python
# Script de validación post-implementación
import os
import yaml
import glob

# 1. Verificar 80 fuentes
sources = glob.glob("docs/nichos/marketing-digital/sources/BRAIN-0{1..8}/FUENTE-*.md")
assert len(sources) == 80, f"Expected 80 sources, got {len(sources)}"

# 2. Verificar cada cerebro tiene 10 fuentes
for brain_num in range(1, 9):
  brain_sources = glob.glob(f"docs/nichos/marketing-digital/sources/BRAIN-0{brain_num}/FUENTE-*.md")
  assert len(brain_sources) == 10, f"Brain M{brain_num}: Expected 10 sources, got {len(brain_sources)}"

# 3. Verificar YAML válido y loaded_in_notebook: true
for source in sources:
  with open(source) as f:
    data = yaml.safe_load(f)
    assert data['loaded_in_notebook'] == True, f"{source} not loaded in notebook"

# 4. Verificar brains-marketing.yaml actualizado
with open("mastermind_cli/config/brains-marketing.yaml") as f:
  config = yaml.safe_load(f)
  for brain in config['brains'][:8]:  # M1-M8
    assert brain['notebook_id'] is not None, f"{brain['id']} missing notebook_id"
    assert brain['sources_count'] == 10, f"{brain['id']} should have 10 sources"

print("✅ All completion tests passed! 80 sources loaded across M1-M8.")
```
