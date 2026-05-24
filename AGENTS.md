# Mente Maestra - Code Review Rules

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

## Referencias

- Fuentes maestras: `docs/software-development/sources/FUENTE-*.md`
- Estructura filesystem: `docs/PRD/09-Filesystem-Structure.md`
- Plan implementación: `docs/PRD/10-Plan-Implementacion-Claude-Code.md`

---

## CRÍTICOS: Seguridad y Datos

REJECT if:

- Hardcoded API keys, tokens, passwords, o credenciales
- `ANTHROPIC_AUTH_TOKEN` o claves expuestas en commits
- IPs privadas, URLs de ambientes de producción
- Secrets en logs o print statements

---

## Python

REJECT if:

- Falta type hints en funciones públicas
- `print()` en lugar de `logger` para output de producción
- Bare `except:` sin excepción específica
- Imports no usados (`import` statements huérfanos)

REQUIRE:

- Docstring en todas las funciones públicas (formato Google o NumPy)
- Type hints en parámetros y return de funciones
- `raise ValueError()` con mensaje descriptivo para validaciones

PREFER:

- `pathlib.Path` sobre `os.path`
- `dataclasses` o `pydantic` para modelos de datos
- Context managers (`with` statement) para recursos

---

## Fichas de Fuentes Maestras (FUENTE-*.md)

REJECT if:

- Falta YAML front matter con campos requeridos
- Campos `source_id`, `brain`, `title`, `author` faltantes
- Sin sección `### 1. Principios Fundamentales`
- Sin sección `### 2. Frameworks y Metodologías`
- Sin sección `### 4. Criterios de Decisión`
- Sin sección `### 5. Anti-patrones`

REQUIRE:

- Formato estricto YAML front matter:
  ```yaml
  ---
  source_id: "FUENTE-NNN"
  brain: "brain-software-XX-nombre"
  title: "Título completo"
  author: "Nombre del autor"
  type: "book|article|video|podcast"
  year: YYYY
  isbn: "XXXXXXXXXX"  # para libros
  skills_covered: ["H1", "H3"]
  distillation_quality: "complete|partial|draft"
  ---
  ```

PREFER:

- Mínimo 3 principios (`> **P`)
- Mínimo 2 frameworks con sección `#### FM`
- Citar con `> ` para destacar principios clave

---

## Documentación PRD (docs/PRD/*.md)

REJECT if:

- Títulos rotos (sin `# ` al inicio de línea)
- Links rotos o sin formato `[texto](url)`
- Tablas con columnas desalineadas
- Listas numeradas desordenadas

REQUIRE:

- Headers jerárquicos (`#` → `##` → `###`)
- Índice al inicio de documentos largos (>100 líneas)
- Referencias cruzadas funcionales

---

## Scripts Bash (*.sh)

REJECT if:

- Falta shebang (`#!/usr/bin/env bash`)
- Sin `set -e` o `set -euo pipefail`
- Variables no citadas (`$var` en vez de `"$var"`)
- Comandos silenciosos sin comentarios

REQUIRE:

- Shebang al inicio
- Error handling con `set -e`
- Comentarios explicativos para comandos no triviales

---

## YAML (*.yaml, *.yml)

REJECT if:

- Tabulaciones en lugar de espacios
- Indentación inconsistente (2 vs 4 espacios)
- Keys duplicadas
- Strings sin comillas cuando tienen caracteres especiales

---

## Git Commits

REJECT if:

- Mensaje de commit sin formato conventional commits
- Falta descripción en commits de features/fixes

REQUIRE:

- Formato: `type(scope): description`
- Types permitidos: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- Ejemplo válido: `feat(product-strategy): add source distillation template`

---

## Response Format

FIRST LINE must be exactly:
STATUS: PASSED
or
STATUS: FAILED

If FAILED, list: `file:line - rule violated - issue`

---

## GLOSARIO

- **FUENTE**: Documento original (libro, artículo, video) de un experto
- **DESTILACIÓN**: Extracción y estructuración del conocimiento esencial
- **CEREBRO**: Repositorio especializado por dominio (Product Strategy, UX, etc.)
- **ORQUESTADOR**: Sistema que asigna tareas a cerebros y valida outputs
- **CEREBRO #7**: Growth/Data - evaluador en tiempo real de todos los outputs
