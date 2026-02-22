# Plantilla de Ficha de Fuente Maestra — MasterMind Framework

Esta plantilla define el formato estándar para documentar cada fuente de conocimiento. Cada ficha es un documento independiente que se carga como fuente en NotebookLM y en el futuro será ingestado por el sistema RAG propio.

**Convención de nombre:** `FUENTE-{NNN}-{titulo-corto}.md`
**Ubicación:** `docs/{nicho}/{cerebro}/sources/`

---

## Plantilla

```markdown
---
# YAML Front Matter (metadata portable para RAG futuro)
source_id: "FUENTE-{NNN}"
brain: "{brain_id}"
niche: "{nicho}"
title: "{Título completo de la fuente}"
author: "{Nombre del autor}"
expert_id: "EXP-{NNN}"
type: "book | video | article | course | documentation"
language: "es | en"
year: {año de publicación}

# Datos bibliográficos (según tipo)
isbn: "{ISBN-13}" # Solo para libros
isbn_10: "{ISBN-10}" # Solo para libros
publisher: "{Editorial}" # Solo para libros
pages: {número} # Solo para libros
url: "{URL}" # Para videos, artículos, cursos
duration_minutes: {minutos} # Para videos
platform: "{YouTube | Coursera | Udemy | etc.}" # Para cursos/videos

# Metadata del framework
skills_covered: ["H1", "H3", "H5"] # IDs del knowledge-map
distillation_date: "{fecha en que se destiló}"
distillation_quality: "complete | partial | pending"
loaded_in_notebook: true | false
---

# FUENTE-{NNN}: {Título Completo}

## Datos de la Fuente

| Campo | Valor |
|-------|-------|
| **Autor** | {Nombre completo} |
| **Tipo** | {Libro / Video / Artículo / Curso / Documentación} |
| **Título** | {Título completo} |
| **Año** | {Año} |
| **ISBN** | {ISBN-13} (solo libros) |
| **Editorial** | {Editorial} (solo libros) |
| **URL** | {URL} (solo videos/artículos) |
| **Duración** | {Minutos} (solo videos) |
| **Idioma** | {Idioma} |

## Experto Asociado

**{Nombre del experto}** — {Especialidad}
Ver ficha completa: `experts-directory.md → EXP-{NNN}`

## Habilidades que Cubre

| ID | Habilidad | Nivel de Cobertura |
|----|-----------|-------------------|
| H{n} | {Nombre} | Profundo / Parcial |
| H{n} | {Nombre} | Profundo / Parcial |

## Resumen Ejecutivo

{2-3 oraciones describiendo de qué trata la fuente y por qué es valiosa para este cerebro. No es una reseña, es una declaración de valor.}

---

## Conocimiento Destilado

### 1. Principios Fundamentales

> **P1: {Nombre del principio}**
> {Descripción clara y accionable del principio}
> *Contexto de aplicación: {cuándo aplica}*

> **P2: {Nombre del principio}**
> {Descripción}
> *Contexto: {cuándo aplica}*

> **P3: {Nombre del principio}**
> {Descripción}
> *Contexto: {cuándo aplica}*

### 2. Frameworks y Metodologías

#### FM1: {Nombre del Framework}

**Propósito:** {Qué problema resuelve}
**Cuándo usar:** {Situación específica}

**Pasos:**
1. {Paso 1}
2. {Paso 2}
3. {Paso 3}

**Output esperado:** {Qué produce}

#### FM2: {Nombre del Framework}

{Misma estructura...}

### 3. Modelos Mentales

| Modelo | Descripción | Aplicación Práctica |
|--------|-------------|-------------------|
| {Nombre} | {Cómo funciona} | {Cuándo y cómo usarlo} |
| {Nombre} | {Cómo funciona} | {Cuándo y cómo usarlo} |

### 4. Criterios de Decisión

| Cuando... | Prioriza... | Sobre... | Porque... |
|-----------|-------------|----------|-----------|
| {Situación} | {Opción A} | {Opción B} | {Razón} |
| {Situación} | {Opción A} | {Opción B} | {Razón} |

### 5. Anti-patrones (Qué NO Hacer)

| Anti-patrón | Por qué es malo | Qué hacer en su lugar |
|-------------|----------------|----------------------|
| {Práctica incorrecta} | {Consecuencia} | {Alternativa correcta} |
| {Práctica incorrecta} | {Consecuencia} | {Alternativa correcta} |

### 6. Casos y Ejemplos Reales

#### Caso 1: {Nombre/Empresa}

- **Situación:** {Contexto}
- **Decisión:** {Qué hicieron}
- **Resultado:** {Qué pasó}
- **Lección:** {Qué aprender}

---

## Notas de Destilación

- **Calidad de la fuente:** {Alta / Media}
- **Capítulos/secciones más valiosos:** {Lista}
- **Lo que NO se extrajo y por qué:** {Secciones ignoradas por ser irrelevantes o redundantes}
- **Complementa bien con:** FUENTE-{NNN} ({título}) — {por qué se complementan}
```

---

## Ejemplo Real: FUENTE-001-Inspired-Cagan

Ver archivo completo en `05-Cerebro-01-Product-Strategy.md`, sección de fuentes.

---

## Reglas para las Fichas

1. **Una ficha por fuente.** No combinar varios libros en una ficha.
2. **El YAML front matter es obligatorio.** Es lo que permite portabilidad al RAG futuro.
3. **Mínimo 3 principios, 1 framework, 2 criterios de decisión, 1 anti-patrón, 1 caso real.**
4. **Si la fuente no alcanza los mínimos, no es fuente maestra.** Es material de referencia secundario.
5. **Cada ficha se carga como documento independiente en NotebookLM.**
6. **El nombre del archivo en NotebookLM debe ser:** `[FUENTE-{NNN}] {Título} — {Autor}`
