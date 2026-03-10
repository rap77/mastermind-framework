---
source_id: "FUENTE-212"
brain: "brain-software-02-ux-research"
niche: "software-development"
title: "Information Architecture: For the Web and Beyond (4th Edition)"
author: "Louis Rosenfeld, Peter Morville, Jorge Arango"
expert_id: "EXP-212"
type: "book"
language: "en"
year: 2015
distillation_date: "2026-03-03"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-03"
changelog:
  - version: "1.0.0"
    date: "2026-03-03"
    changes:
      - "Initial distillation from IA 4th Edition"
status: "active"
---

# Information Architecture: For the Web and Beyond

**Louis Rosenfeld, Peter Morville, Jorge Arango**

## 1. Principios Fundamentales

> **P1 - La IA no es organización de archivos**: La Arquitectura de Información es el arte y la ciencia de organizar información para que sea findable, manejable, y valiosa. No es "hacer sitemap", es diseñar cómo las personas piensan sobre información.

> **P2 - Findability > Usability**: Si no pueden encontrarlo, no pueden usarlo. La findability es el prerrequisito de la usabilidad. Un contenido perfecto es inútil si está enterrado.

> **P3 - Contexto es Rey**: No existe una "mejor" estructura de información. Solo existe la mejor estructura PARA TU CONTEXTO específico: usuarios, contenido, y negocio.

> **P4 - Sistemas de Etiquetado son para Usuarios, no para Content Managers**: Las categorías internas del negocio raramente coinciden con modelos mentales de usuarios. Etiquetar es traducir, no transcribir.

> **P5 - La IA es Sistémica**: La IA no se hace en una fase. Se hace en el diseño inicial, se refina con analytics, y evoluciona con el producto. Es un organismo vivo, no un blueprint estático.

## 2. Frameworks y Metodologías

### The Three Circles of IA

```
         Context
       /     \
     /         \
   Users ----- Content
```

**Context** (Negocio, Política, Tecnología, Cultura):
- ¿Cuál es el modelo de negocio?
- ¿Qué restricciones técnicas existen?
- ¿Cuál es la cultura organizacional?
- ¿Quiénes son los stakeholders?

**Users** (Audiencia, Tareas, Necesidades, Experiencia):
- ¿Quiénes son los usuarios?
- ¿Qué tareas intentan completar?
- ¿Qué vocabulario usan?
- ¿Qué experiencia tienen con el dominio?

**Content** (Formato, Estructura, Metadatos, Volumen):
- ¿Qué contenido existe?
- ¿Qué formato tiene (texto, video, datos)?
- ¿Cómo se estructura?
- ¿Cuánto volumen hay?

### Systems of IA (los 5 sistemas)

#### 1. Organization Systems

**Exact Schemes** (Divisiones objetivas):
- Alphabetical: A-Z (glosarios, directorios)
- Chronological: Por fecha (noticias, archivos)
- Geographical: Por ubicación (tiendas, eventos)

**Ambiguous Schemes** (Divisiones subjetivas):
- Topic: Por tema (categorías de producto)
- Task: Por actividad (comprar, vender, aprender)
- Audience: Por tipo de usuario (estudiante, profesional)
- Metaphor: Por analogía (escritorio, biblioteca)
- Hybrid: Combinación de las anteriores

**Trade-off**:
- Exact schemes = fáciles de mantener, difíciles de diseñar
- Ambiguous schemes = difíciles de mantener, fáciles de usar

#### 2. Navigation Systems

| Tipo | Propósito | Ejemplo |
|------|-----------|---------|
| **Global nav** | Siempre visible, accesos principales | Home, Products, About |
| **Local nav** | Específico de sección | Subcategorías, filtros |
| **Site map** | Vista general, accesibilidad | Página de mapa completo |
| **Index** | Listado alfabético de contenido | Índice de términos |
| **Breadcrumbs** | Jerarquía visible, navegación hacia atrás | Home > Products > Shoes > Running |

#### 3. Labeling Systems

**Tipos de Labels:**
- Contextual: Links en el contexto de uso
- Iconic: Iconos (siempre + texto cuando sea posible)
- Headings: Títulos de secciones
- Index terms: Keywords para búsqueda

**Principios de Labeling:**
1. **Hablar el lenguaje del usuario** → No del negocio
2. **Ser específico pero conciso** → "Botines de running" no "Calzado deportivo"
3. **Ser consistente** → Mismo concepto = mismo label
4. **Testear con usuarios** → Los modelos mentales varían

#### 4. Searching Systems

**Cuando implementar búsqueda:**
- Volumen de contenido > 1000 items
- Usuarios conocen qué buscan
- Existe vocabulario específico del dominio
- El contenido cambia frecuentemente

**Componentes de Search:**
1. **Search box**: Ubicación, visibilidad, placeholder
2. **Autocomplete**: Sugerencias mientras escribe
3. **Advanced search**: Filtros, operadores booleanos
4. **Results display**: Relevancia, snippets, paging
5. **Search analytics**: Qué buscan, qué no encuentran

#### 5. Metadata & Controlled Vocabularies

**Metadata** (Datos sobre datos):
- Descriptive: Título, autor, fecha
- Structural: Capítulos, secciones
- Administrative: Copyright, permisos
- Technical: Formato, tamaño, URL

**Controlled Vocabularies:**
- Synonym rings: Términos equivalentes (laptop = notebook)
- Authority files: Términos preferidos (USA no U.S.A.)
- Classification schemes: Jerarquías de temas
- Thesaurus: Relaciones entre términos (BT, NT, RT)

### IA Research Methods

| Método | Para qué | Cuándo |
|--------|----------|--------|
| **Content inventory** | Auditar contenido existente | Inicio del proyecto |
| **Card sorting** | Entender modelos mentales | Diseño de categorías |
| **User interviews** | Entender vocabulario, tareas | Fase de investigación |
| **Search analytics** | Qué buscan, qué falla | Mejora continua |
| **Usability testing** | Validar estructuras propuestas | Prototipos, antes de dev |

### The "IA for the Web" Evolution

**Web 1.0**: IA = Sitemap + Taxonomy (estático)
**Web 2.0**: IA + Social (tags, ratings, user-generated)
**Web 3.0**: IA + Semantic (schema.org, linked data)
**Web 4.0**: IA + AI + Voice (chatbots, asistentes, VUI)

## 3. Modelos Mentales

### Modelo de "Information Seeking"

**Berry Picking Model**: La búsqueda no es lineal.
1. Usuario tiene una necesidad de información
2. Comienza con una query inicial
3. Navega los resultados
4. Refina la query (new query)
5. Recolecta información "bit by bit"
6. El proceso evoluciona conforme aprende

**Implicaciones de diseño:**
- Proveer múltiples puntos de entrada
- Permitir fácil refinación de búsqueda
- Mostrar información relacionada
- No asumir un camino lineal

### Modelo de "Ambiguity in Information Organization"

Todo sistema de organización tiene ambigüedad inherente:
- "iPhone" es ¿producto? ¿categoría? ¿marca?
- "Running" es ¿deporte? ¿actividad? ¿calzado?

**Decisiones:**
1. Aceptar ambigüedad → Permitir múltiples categorías
2. Resolver con contexto → El contexto aclara
3. Decisiones de negocio → Una categoría "oficial"

### Taxonomy vs Folksonomy

| Aspecto | Taxonomy | Folksonomy |
|---------|----------|------------|
| Quién crea | Expertos, controlado | Usuarios, emergente |
| Estructura | Jerárquica, rígida | Plana, flexible |
| Mantenimiento | Costoso | Automático |
| Escalabilidad | Difícil de escalar | Escala con usuarios |
| Uso ideal | E-commerce corporativo | Social, contenido masivo |

**Híbrido**: Taxonomy para estructura base + Folksonomy para tags de usuarios

### Memoria y Findability

| Tipo de memoria | Duración | Implicación de diseño |
|-----------------|----------|----------------------|
| **Sensory** | Milisegundos | Atención visual inmediata |
| **Short-term** | 15-30 segundos | Breadcrumbs, estado visible |
| **Long-term** | Días-años | Consistencia, modelos mentales |

**Diseño para optimizar:**
- Reconocimiento > Recuerdo (mostrar, no pedir recordar)
- Consistentes para consolidar memoria
- Progressive disclosure para no sobrecargar

## 4. Criterios de Decisión

### Cuando crear jerarquías profundas vs anchas

| Profundidad | Anchura | Cuándo usar |
|-------------|---------|-------------|
| **Profunda** (5+ niveles) | Estrecha | E-commerce con muchas categorías, usuarios expertos |
| **Ancha** (2-3 niveles) | Ancha | Sitios simples, audiencia amplia |
| **Híbrida** | Media | La mayoría de los casos |

**Regla empírica**: 3 clicks rule (debatido)
- Más importante: clicks significativos
- Usuario prefiere 5 clicks claros > 3 clicks confusos

### When to Use Card Sorting

**Open Card Sorting** (usuarios agrupan):
- Descubrir modelos mentales
- Fase exploratoria
- Sin categorías predefinidas

**Closed Card Sorting** (usuarios asignan a categorías):
- Validar estructura propuesta
- Fase de validación
- Con categorías existentes

**Tree Testing** (validar navegación):
- Después de tener estructura
- Probar findability sin UI
- Medir éxito, tiempo, dificultad

### Etiquetado: Technical vs Business vs User Language

| Tipo | Características | Uso apropiado |
|------|-----------------|---------------|
| **Technical** | Preciso, incomprensible para laypeople | Documentación técnica, developer tools |
| **Business** | Alineado con organización, buzzwords | Internos, reportes ejecutivos |
| **User** | Vocabulario natural, metafórico | Productos externos, consumer apps |

**Regla**: External products → User language. Internal tools → Business/Technical mix.

### Search vs Browse

| Situación | Preferir | Razón |
|-----------|----------|--------|
| Usuario sabe qué busca | Search | Más rápido |
| Usuario explorando | Browse | Descubrimiento |
| Contenido pequeño | Browse | No necesita search |
| Contenido masivo | Search + Browse | Complementarios |
| Dominio complejo | Browse + Facets | Estructura guía, search refina |

### Responsive IA

**Desktop**: Más espacio, menú horizontal, mega-menús
**Mobile**: Menú hamburguesa, tabs, bottom navigation

**No shrinking**: No es "adaptar desktop a mobile"
Es "diseñar IA para cada contexto"

## 5. Anti-patrones

### Anti-patrón: "Corporate Structure Mirror"

**Problema**: La estructura del sitio refleja el organigrama de la empresa.

**Solución:**
- El usuario no conoce ni le importa tu organigrama
- Estructurar según necesidades del usuario
- Silos organizacionales → Integrated user experience

### Anti-patrón: "Mega-menu Overload"

**Problema**: Menús con 50+ items, imposible de escanear.

**Solución:**
- Ley de Miller: 7±2 items por menú
- Agrupar lógicamente
- Progressive disclosure

### Anti-patrón: "Creative Labels"

**Problema**: Usar nombres creativos ("The Hub", "Exchange") en vez de descriptivos ("Community", "Forum").

**Solución:**
- Claridad > creatividad
- Testear comprensión con usuarios
- Creatividad en branding, no en navegación

### Anti-patrón: "Search as a Crutch"

**Problema**: "No sabemos cómo organizarlo, pongamos search."

**Solución:**
- Search es complemento, no excusa
- Buen search + mala IA = usuario frustrado
- Invertir en ambos

### Anti-patrón: "Flat UI = Flat IA"

**Problema**: Diseño plano no significa estructura plana de información.

**Solución:**
- Estilo visual ≠ profundidad de información
- Se puede tener diseño minimalista con IA profunda y rica

### Anti-patrón: "One-Time IA"

**Problema**: Diseñar IA al inicio y nunca revisar.

**Solución:**
- Analytics muestra qué no se encuentra
- A/B test de estructuras
- Evolución con producto y usuarios

### Anti-patrón: "Content Dump"

**Problema**: Volcar contenido sin estructura, pensando "la búsqueda lo resolverá".

**Solución:**
- Todo contenido necesita contexto
- Metadata, relacionamiento, estructura
- La búsqueda no reemplaza la organización
