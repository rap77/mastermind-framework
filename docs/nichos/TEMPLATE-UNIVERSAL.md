# Template Universal de Nicho - MasterMind Framework

Este template define la estructura estándar para todos los nichos en MasterMind Framework.

## Estructura de Directorios

```
docs/nichos/{nombre-nicho}/
├── README.md                          # Descripción del nicho
├── PRP-{NICHO}-XXX.md                # PRPs del nicho (si aplica)
├── BRAIN-01-{NOMBRE}/
│   ├── sources/
│   │   ├── FUENTE-XXX.md             # Fuentes maestras (10 por brain)
│   │   └── ...                       # Más fuentes
│   └── notebook-config.json          # Config de NotebookLM
├── BRAIN-02-{NOMBRE}/
│   ├── sources/
│   └── notebook-config.json
└── ...                                # Hasta BRAIN-XX
```

## Formato de Fuente Maestra

Todas las fuentes deben seguir este formato YAML + Markdown:

```yaml
---
source_id: "FUENTE-XXX"
brain: "brain-{niche}-{short-id}"
niche: "{nombre-nicho}"
title: "Título del libro/recurso"
author: "Nombre del autor"
expert_id: "EXP-XXX"
type: "book|course|blog|podcast|newsletter"
language: "en|es"
year: XXXX
isbn: "..." (si aplica)
url: "https://..."
skills_covered: ["H1", "H3", "H5"]
distillation_date: "YYYY-MM-DD"
distillation_quality: "complete|partial"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "YYYY-MM-DD"
changelog:
  - version: "1.0.0"
    date: "YYYY-MM-DD"
    changes:
      - "Ficha creada con destilación completa"
status: "active"

# Campos estándar obligatorios (desde v1.1)
habilidad_primaria: "Una frase describiendo la habilidad principal del experto"
habilidad_secundaria: "Habilidades secundarias separadas por comas"
capa: 1  # 1-5 según corresponda
capa_nombre: "Base Conceptual|Framework Operativo|Modelo Mental|Criterio de Decisión|Mecanismo de Retroalimentación"
relevancia: "[CRÍTICA|ALTA|MEDIA|BAJA] — Justificación de por qué este experto es relevante para este cerebro"
---

# FUENTE-XXX: {Título} — {Autor}

## Tesis Central

> Una frase que capture la idea central del experto.

---

## 1. Principios Fundamentales

> **P1: [Nombre del principio]**
> [Descripción detallada del principio]
> *Fuente: [Título, Capítulo X (Autor, Año)]*
> *Contexto: [Cuándo aplicar este principio]*

> **P2: [Nombre del principio]**
> [Descripción detallada del principio]
> *Fuente: [Título, Capítulo Y (Autor, Año)]*
> *Contexto: [Cuándo aplicar este principio]*

[... 3-5 principios]

---

## 2. Frameworks y Metodologías

### Framework 1: [Nombre del Framework]

**Fuente:** [Título, Capítulo/Página (Autor, Año)]
**Propósito:** [Cuál es el propósito de este framework]
**Cuándo usar:** [En qué situaciones aplicar]

**Pasos/Componentes:**
1. [Paso 1]
2. [Paso 2]
3. [Paso 3]

**Output esperado:** [Qué resultado se obtiene]

[... 2-4 frameworks]

---

## 3. Modelos Mentales

### Modelo Mental 1: [Nombre]

**Fuente:** [Título, Capítulo/Sección (Autor, Año)]
**El modelo:** [Descripción del modelo]
**Por qué funciona:** [Explicación]
**Cuándo usarlo:** [Situaciones donde aplica]
**Limitaciones:** [Cuándo NO usarlo]

[... 2-3 modelos mentales]

---

## 4. Criterios de Decisión

### Trade-off: [Nombre del trade-off]

**Fuente:** [Título, Capítulo/Sección (Autor, Año)]

**Opción A:** [Descripción]
- **Ventajas:** [Lista]
- **Desventajas:** [Lista]
- **Mejor para:** [Cuándo elegir esta opción]

**Opción B:** [Descripción]
- **Ventajas:** [Lista]
- **Desventajas:** [Lista]
- **Mejor para:** [Cuándo elegir esta opción]

**Recomendación del experto:** [Qué opina el experto]

[... 2-3 trade-offs]

---

## 5. Anti-patrones

### Anti-patrón 1: [Nombre]

**Fuente:** [Título, Capítulo/Sección (Autor, Año)]
**Qué es:** [Descripción del error]
**Por qué la gente lo hace:** [Causa común]
**Consecuencias:** [Qué pasa si lo haces]
**Cómo evitarlo:** [Mejor práctica]
**Qué hacer en su lugar:** [Alternativa correcta]

[... 2-3 anti-patrones]

---

## Referencias

- **Libro principal:** [Título, ISBN]
- **Blog:** [URL]
- **Curso:** [URL si aplica]
- **Podcast:** [URL si aplica]
- **Newsletter:** [URL si aplica]

---

## Notas Adicionales

[Espacio para notas específicas sobre este experto]
```

## Formato notebook-config.json

```json
{
  "notebook_id": "uuid-del-notebook-en-notebooklm",
  "notebook_name": "[CEREBRO] {Nombre} - {Nicho}",
  "brain_id": "M1 o 01",
  "brain_name": "Nombre completo del cerebro",
  "sources_count": 10,
  "created_date": "YYYY-MM-DD",
  "last_updated": "YYYY-MM-DD",
  "status": "complete|incomplete"
}
```

## Las 5 Capas de Cada Cerebro

| Capa | Nombre | Descripción |
|------|--------|-------------|
| 1 | Base Conceptual | Principios fundamentales y "por qué" |
| 2 | Framework Operativo | Métodos, herramientas y "cómo" |
| 3 | Modelo Mental | Lente de análisis del mundo |
| 4 | Criterio de Decisión | Trade-offs profesionales (lo que separa experto de asistente) |
| 5 | Mecanismo de Retroalimentación | Medición y mejora continua |

## Niveles de Relevancia

- **CRÍTICA:** Autoridad mundial, framework estándar de la industria, esencial para este cerebro
- **ALTA:** Experto reconocido, contribuciones significativas, altamente citado
- **MEDIA:** Experto con perspectivas útiles, complementa otros expertos
- **BAJA:** Referencia tangencial, contexto histórico o alternativo

## Requisito de Atribución

**OBLIGATORIO:** Cada sección (Principios, Frameworks, Modelos, Trade-offs, Anti-patrones) debe incluir la fuente específica:

- Principios: `*Fuente: [Título, Cap X (Autor, Año)]*`
- Frameworks: `**Fuente:** [Título, Cap X (Autor, Año)]`
- Modelos mentales: `**Fuente:** [Título, Sección (Autor, Año)]`
- Trade-offs: `**Fuente:** [Título, Cap X (Autor, Año)]`
- Anti-patrones: `**Fuente:** [Título, Cap X (Autor, Año)]`

Esto permite rastrear exactamente de dónde vino cada idea.

## Validations

Para validar que un nicho está bien estructurado:

```bash
# 1. Verificar estructura de directorios
ls -d docs/nichos/{nombre-nicho}/BRAIN-*/

# 2. Verificar notebook-config.json en cada brain
find docs/nichos/{nombre-nicho}/BRAIN-*/notebook-config.json | wc -l

# 3. Verificar YAML válido en fuentes
for file in docs/nichos/{nombre-nicho}/BRAIN-*/sources/FUENTE-*.md; do
  python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>&1 | grep -q "error" && echo "ERROR: $file"
done

# 4. Verificar campos obligatorios
grep -q "habilidad_primaria:" docs/nichos/{nombre-nicho}/BRAIN-*/sources/FUENTE-*.md
grep -q "capa:" docs/nichos/{nombre-nicho}/BRAIN-*/sources/FUENTE-*.md
grep -q "relevancia:" docs/nichos/{nombre-nicho}/BRAIN-*/sources/FUENTE-*.md
```

## Nichos Activos

| Nicho | Estado | Cerebros | Fuentes |
|-------|--------|----------|---------|
| Software Development | ✅ v1.1.0 | 7 (#1-7 + #8) | 122 |
| Marketing Digital | 🟡 In Progress | 16 (M1-M16) | 15 (M1 complete, M2 partial) |

---

**Template creado:** 2026-03-10
**Versión:** 1.0.0
**Aplica a:** Todos los nichos de MasterMind Framework
