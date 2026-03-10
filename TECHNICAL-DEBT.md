# Technical Debt - MasterMind Framework

## Pending Tasks

### 1. Estandarizar Fuentes de Software (122 fuentes)

**Prioridad:** Media
**Fecha de creación:** 2026-03-10
**Contexto:** Estandarización de nichos

**Descripción:**
Agregar campos extra a las 122 fuentes de `docs/nichos/software-development/` para que coincidan con el formato estándar de marketing.

**Campos a agregar:**
```yaml
habilidad_primaria: "Una frase describiendo la habilidad principal del experto"
habilidad_secundaria: "Habilidades secundarias separadas por comas"
capa: 1  # 1-5 según corresponda
capa_nombre: "Base Conceptual|Framework Operativo|Modelo Mental|Criterio de Decisión|Mecanismo de Retroalimentación"
relevancia: "[CRÍTICA|ALTA|MEDIA|BAJA] — Justificación"
```

**Fuentes afectadas:**
- BRAIN-01-PRODUCT-STRATEGY: 10 fuentes
- BRAIN-02-UX-RESEARCH: 19 fuentes
- BRAIN-03-UI-DESIGN: 20 fuentes
- BRAIN-04-FRONTEND: 18 fuentes
- BRAIN-05-BACKEND: 21 fuentes
- BRAIN-06-QA-DEVOPS: 20 fuentes
- BRAIN-07-GROWTH-DATA: 14 fuentes

**Total:** 122 fuentes

**Cómo hacerlo:**
1. Leer cada fuente
2. Analizar el contenido (título, autor, expertise)
3. Determinar valores apropiados para:
   - `habilidad_primaria`: Basarse en el título del libro/recurso
   - `habilidad_secundaria`: Del campo `expertise` o skills_covered
   - `capa`: Determinar por tipo de contenido (principios=1, frameworks=2, etc.)
   - `capa_nombre`: Mapear de número a nombre
   - `relevancia`: Determinar por autoridad del autor y citas
4. Actualizar YAML front matter
5. Validar syntax

**Script de ayuda:**
```bash
# Encontrar fuentes que aún no tienen los campos
grep -L "habilidad_primaria:" docs/nichos/software-development/BRAIN-*/sources/FUENTE-*.md
```

**Estado:** ⏳ Pending (hacer después de completar marketing PRP-002/003)

---

## Completed Tasks

### 1. Estandarización de Estructura de Nichos ✅ (2026-03-10)

- Movido `docs/software-development/` → `docs/nichos/software-development/`
- Renombrado brains a formato `BRAIN-XX-NAME/`
- Reorganizado marketing a estructura estándar
- Creado `docs/nichos/TEMPLATE-UNIVERSAL.md`

---

**Última actualización:** 2026-03-10
