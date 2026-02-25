# PRP-002: YAML Front Matter en Fichas Existentes

**Status:** ✅ COMPLETED
**Completed Date:** 2026-02-24
**Priority:** High
**Estimated Time:** 30-45 minutes (Actual: ~20 min)
**Dependencies:** PRP-001 (usa el CLI para validar)

---

## Executive Summary

Validar las 10 fuentes existentes del Cerebro #1 y agregar los campos de versionado (version, last_updated, changelog, status) al YAML front matter. Esta tarea puede ser manual o automatizada con un script one-time.

---

## Context from Clarification Session

### Decisiones Críticas

1. **Validación necesaria:** Las fuentes existen pero requieren validación contra estándares
2. **Campos a agregar:** `version`, `last_updated`, `changelog`, `status`
3. **Calidad:** Mínimo 3 principios, 5 secciones, YAML completo

### Fuentes Existentes

| ID | Título | Ubicación |
|----|--------|-----------|
| FUENTE-001 | Inspired: How to Create Tech Products Customers Love | `docs/software-development/sources/` |
| FUENTE-002 | Continuous Discovery Habits | `docs/software-development/sources/` |
| FUENTE-003 | Escaping the Build Trap | `docs/software-development/sources/` |
| FUENTE-004 | The Lean Startup | `docs/software-development/sources/` |
| FUENTE-005 | Measure What Matters | `docs/software-development/sources/` |
| FUENTE-006 | Thinking in Systems | `docs/software-development/sources/` |
| FUENTE-007 | Empowered | `docs/software-development/sources/` |
| FUENTE-008 | Marty Cagan - Product Discovery (video) | `docs/software-development/sources/` |
| FUENTE-009 | Teresa Torres - Continuous Discovery (video) | `docs/software-development/sources/` |
| FUENTE-010 | Melissa Perri - Escaping the Build Trap (video) | `docs/software-development/sources/` |

---

## External Resources

### YAML Documentation
- https://yaml.org/spec/1.2/spec.html - YAML specification
- https://learnxinyminutes.com/docs/yaml/ - YAML quick reference

### PyYAML
- https://pyyaml.org/wiki/PyYAMLDocumentation - Python YAML library

---

## Implementation Blueprint

### Pseudocode - Script de Actualización

```python
# tools/update_sources_yaml.py
import yaml
from datetime import date

# Campos a agregar a cada fuente
VERSIONING_FIELDS = {
    "version": "1.0.0",
    "last_updated": str(date.today()),
    "changelog": ["v1.0.0: Destilación inicial completa"],
    "status": "active"
}

REQUIRED_YAML_FIELDS = [
    "source_id", "brain", "title", "author", "type",
    "skills_covered", "distillation_quality", "loaded_in_notebook"
]

REQUIRED_CONTENT_SECTIONS = [
    "### 1. Principios Fundamentales",
    "### 2. Frameworks y Metodologías",
    "### 3. Modelos Mentales",
    "### 4. Criterios de Decisión",
    "### 5. Anti-patrones"
]

def update_source_file(filepath):
    # 1. Leer archivo actual
    metadata, content = read_yaml_frontmatter(filepath)

    # 2. Validar campos obligatorios
    missing = [f for f in REQUIRED_YAML_FIELDS if f not in metadata]
    if missing:
        print(f"❌ {filepath}: Missing fields: {missing}")
        return False

    # 3. Validar secciones de contenido
    missing_sections = []
    for section in REQUIRED_CONTENT_SECTIONS:
        if section not in content:
            missing_sections.append(section)

    if missing_sections:
        print(f"⚠️  {filepath}: Missing sections: {missing_sections}")

    # 4. Contar principios (> **P)
    principles_count = content.count("> **P")
    if principles_count < 3:
        print(f"⚠️  {filepath}: Only {principles_count} principles (min 3)")

    # 5. Agregar campos de versionado si no existen
    metadata.update(VERSIONING_FIELDS)

    # 6. Escribir archivo actualizado
    write_yaml_frontmatter(filepath, metadata, content)
    return True

# Procesar las 10 fuentes
sources = glob("docs/software-development/01-product-strategy-brain/sources/FUENTE-*.md")
for source in sources:
    update_source_file(source)
```

---

## Tasks (in Order)

### Task 1: Validar Estado Actual (10 min)
- [ ] Leer las 10 fuentes existentes
- [ ] Documentar estado actual de cada una
- [ ] Identificar qué fuentes ya tienen YAML front matter
- [ ] Crear reporte en `logs/sources-validation-before.md`

### Task 2: Crear Script de Actualización (15 min)
- [ ] Crear `tools/update_sources_yaml.py`
- [ ] Implementar lectura de YAML front matter
- [ ] Implementar validación de campos
- [ ] Implementar actualización con campos de versionado

### Task 3: Ejecutar Script (5 min)
- [ ] Hacer backup de fuentes: `cp -r sources/ sources.backup/`
- [ ] Ejecutar script de actualización
- [ ] Verificar que no haya errores

### Task 4: Validar Post-Update (10 min)
- [ ] Usar `mastermind source validate --brain 01-product-strategy`
- [ ] Verificar que todas las fuentes pasen validación
- [ ] Revisar YAML de cada fuente manualmente
- [ ] Crear reporte en `logs/sources-validation-after.md`

### Task 5: Git Commit (5 min)
- [ ] Revisar cambios con `git diff`
- [ ] Commit si todo está correcto
- [ ] Message: `feat(sources): add versioning fields to existing sources`

---

## Validation Criteria

### Campos YAML Obligatorios

```yaml
---
source_id: "FUENTE-001"
brain: "01-product-strategy"
title: "Inspired: How to Create Tech Products Customers Love"
author: "Marty Cagan"
expert_id: "EXP-001"
type: "book"
isbn: "978-1119387503"
skills_covered: ["H1", "H3", "H5", "H7"]
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-02-22"
changelog:
  - "v1.0.0: Destilación inicial completa"
status: "active"
---
```

### Secciones de Contenido Requeridas

1. `### 1. Principios Fundamentales` - Con mínimo 3 principios
2. `### 2. Frameworks y Metodologías`
3. `### 3. Modelos Mentales`
4. `### 4. Criterios de Decisión`
5. `### 5. Anti-patrones`

### Reglas de Calidad

- Mínimo 3 principios por fuente
- Cada principio marcado con `> **P`
- YAML front matter completo
- Sin errores de sintaxis YAML

---

## Validation Gates

```bash
# 1. Validar con CLI
mastermind source validate --brain 01-product-strategy

# 2. Verificar YAML de cada fuente
for f in docs/software-development/01-product-strategy-brain/sources/FUENTE-*.md; do
    echo "Checking $f"
    python3 -c "import yaml; yaml.safe_load(open('$f'))"
done

# 3. Verificar campos de versionado
grep -r "version:" docs/software-development/01-product-strategy-brain/sources/

# 4. Verificar secciones de contenido
grep -r "### 1. Principios" docs/software-development/01-product-strategy-brain/sources/

# 5. Contar principios
grep -r "> **P" docs/software-development/01-product-strategy-brain/sources/ | wc -l
```

---

## Definition of Done

- [x] Las 10 fuentes tienen YAML front matter completo
- [x] Todas tienen campos de versionado (version, last_updated, changelog, status)
- [x] Validación YAML sintáctica correcta
- [x] Mínimo 3 principios por fuente
- [x] Las 5 secciones de contenido están presentes
- [x] Reporte de validación creado (`logs/sources-validation-prp002-after.md`)
- [x] PRP actualizado a estado COMPLETED

---

## Implementation Result (2026-02-24)

### Estado de las Fuentes

| Fuente | version | YAML | Secciones | Principios | Status |
|--------|---------|------|-----------|------------|--------|
| FUENTE-001 | 1.0.0 | ✅ | 5/5 | 5 | ✅ |
| FUENTE-002 | 1.0.0 | ✅ | 5/5 | 5 | ✅ |
| FUENTE-003 | 1.0.0 | ✅ | 5/5 | 4 | ✅ |
| FUENTE-004 | 1.0.0 | ✅ | 5/5 | 4 | ✅ |
| FUENTE-005 | 1.0.0 | ✅ | 5/5 | 4 | ✅ |
| FUENTE-006 | 1.0.0 | ✅ | 5/5 | 4 | ✅ |
| FUENTE-007 | 1.0.0 | ✅ | 5/5 | 4 | ✅ |
| FUENTE-008 | 1.0.0 | ✅ | 5/5 | 3 | ✅ |
| FUENTE-009 | 1.1.0 | ✅ | 5/5 | 3 | ✅ |
| FUENTE-010 | 1.1.0 | ✅ | 5/5 | 3 | ✅ |

### Cambios Aplicados

1. **FUENTE-009**: Agregado principio P3 "Compare & Contrast", actualizado a v1.1.0
2. **FUENTE-010**: Agregado principio P3 "Outcome > Output", actualizado a v1.1.0

### Archivos Creados

- `logs/sources-validation-prp002-after.md` - Reporte de validación final

### Próximos Pasos

- Commit con cambios si se desea
- PRP-002 marcado como COMPLETADO

---

## Error Handling Strategy

| Error | Acción |
|-------|--------|
| YAML inválido | Editar manualmente - reportar línea específica |
| Campo faltante | Agregar con valor por defecto o "" si desconocido |
| Sección faltante | Agregar placeholder con "PENDIENTE" |
| < 3 principios | Marcar como `status: draft` en YAML |

---

## Gotchas & Notes

1. **Caracteres especiales:** YAML es estricto con comillas, dos puntos, guiones. Validar con `yamllint` si es posible.

2. **Fechas:** Usar formato ISO `YYYY-MM-DD` para `last_updated`.

3. **Changelog:** Es un array, no un string. Usar sintaxis YAML correcta.

4. **Skills codes:** Validar que los códigos (H1, H2, etc.) correspondan a los definidos en el cerebro.

5. **Expert IDs:** Validar que cada `expert_id` exista en `experts-directory.md`.

6. **ISBNs:** Para videos y otros tipos, el campo puede estar vacío o usar URL.

7. **Backup:** Siempre hacer backup antes de modificar las fuentes.

---

## Files Modified

| Archivo | Cambio |
|---------|--------|
| `docs/software-development/01-product-strategy-brain/sources/FUENTE-*.md` | Agregar campos de versioning |
| `logs/sources-validation-before.md` | Reporte antes de cambios |
| `logs/sources-validation-after.md` | Reporte después de cambios |

---

## Output Files Created

| Archivo | Propósito |
|---------|-----------|
| `tools/update_sources_yaml.py` | Script de actualización one-time |
| `logs/sources-validation-before.md` | Estado inicial |
| `logs/sources-validation-after.md` | Estado final |

---

## Next Steps

After this PRP:
- → PRP-003: System prompts de agentes
- → PRP-004: NotebookLM integration

---

## Confidence Score

**9/10** - Muy alta confianza de éxito.

**Rationale:** Tarea mecánica y bien definida. Las fuentes ya existen, solo hay que agregar campos y validar. El riesgo principal es YAML syntax que se puede resolver con validación.

---

## Context for AI Agent

**Archivos clave para leer antes de implementar:**
1. `/home/rpadron/proy/mastermind/docs/design/04-Plantilla-Ficha-Fuente-Maestra.md` - Plantilla con campos
2. `/home/rpadron/proy/mastermind/docs/software-development/sources/FUENTE-001-inspired-cagan.md` - Ejemplo real
3. `/home/rpadron/proy/mastermind/PRPs/PRP-001-mastermind-cli.md` - Función `read_yaml_frontmatter`

**Comando para iniciar:**
```bash
cd /home/rpadron/proy/mastermind
# Hacer backup
cp -r docs/software-development/sources/ docs/software-development/sources.backup/
# Ejecutar script cuando esté listo
python3 tools/update_sources_yaml.py
```

**Resultado esperado:**
Las 10 fuentes tienen YAML front matter completo con campos de versioning. `mastermind source validate` pasa.
