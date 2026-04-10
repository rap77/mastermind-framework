---
description: Pre-commit cognitive barrier that enforces GGA validation and Brain #6 testing standards. Blocks --no-verify, validates tests pass, checks conventional commits, integrates with Brain #6 QA/DevOps. Auto-corrects errors before committing.
argument-hint: "[--check | --fix | --help]"
---

# /mm:safe-commit

**Barrera cognitiva reactiva que nunca permite `--no-verify`.**

Valida ANTES de commitear: tests pasando (0 fallas), GGA hook configurado, formato convencional correcto, sin "Co-Authored-By". Se integra con Brain #6 QA/DevOps para estrategia de testing.

## Usage

```bash
/mm:safe-commit              # Valida TODO y commitea cambios staged
/mm:safe-commit --check      # Solo checkea (dry-run), no commitea
/mm:safe-commit --fix        # Auto-corrige issues y commitea
/mm:safe-commit --help       # Muestra esta ayuda
```

## What Happens

### 1. Detección Reactiva

La skill se activa automáticamente cuando:
- Vas a ejecutar `git commit`
- El usuario dice "commit this", "commiteá esto", "make commit"
- Veo `--no-verify` en cualquier comando git

**No espera a que lo pidas explícitamente. Es una barrera cognitiva.**

### 2. Bloqueo de `--no-verify`

Si detecto `--no-verify`:

```
❌ BLOQUEADO: --no-verify es PELIGROSO

Por qué:
- GGA valida security (hardcoded credentials, tokens, private IPs)
- GGA valida TypeScript/React standards
- GGA validates accessibility (ARIA, WCAG 2.1 AA)
- GGA valida performance (bundle size, Lighthouse scores)

Si GGA falla → Arreglá el error, NO lo salteés

Regla documentada en 4 lugares:
- memory/MEMORY.md
- .planning/codebase/CONVENTIONS.md
- .planning/codebase/CONCERNS.md
- docs/handoffs/HANDOFF.md
```

### 3. Pre-Commit Checklist

Antes de permitir cualquier commit:

```bash
# ✅ Tests pasando (570/570 backend + 407/407 frontend)
cd apps/api && uv run pytest
pnpm --prefix apps/web test run

# ✅ GGA hook configurado
test -f .pre-commit-config.yaml || echo "GGA hook missing"

# ✅ Formato convencional
echo "type(scope): message" | grep -E "^(feat|fix|chore|docs|style|refactor|perf|test|build|ci|revert)\(.+\): .+"

# ✅ Sin AI attribution
git log -1 --pretty=%B | grep -q "Co-Authored-By:" && echo "Remove AI attribution"
```

### 4. Brain #6 Integration

Consultamos a Brain #6 (QA/DevOps) para:

- Validar estrategia de testing
- Aplicar sus correcciones conocidas:
  - ❌ "npm test" → ✅ `pnpm --prefix apps/web test run`
  - ❌ "pytest from root" → ✅ `cd apps/api && uv run pytest`
  - ❌ "docker from apps/api/" → ✅ `docker compose up` desde ROOT
- Cero tolerancia a fallas pre-existentes

### 5. Auto-Correction Flow

Si algo falla:

| Error | Auto-corrección |
|-------|-----------------|
| Tests fallan | Mostrar qué tests fallaron, cómo fixearlos |
| GGA falla | Mostrar errores de validación, cómo corregir |
| Format wrong | Sugerir formato correcto: `feat(scope): message` |
| AI attribution | Remover "Co-Authored-By:" del mensaje |

## Examples

```bash
# Commit normal con validación completa
/mm:safe-commit

# Solo checkear si todo está OK (dry-run)
/mm:safe-commit --check

# Auto-corriger issues y commitear
/mm:safe-commit --fix
```

## Test Baseline

**Suite actual:** 977/977 tests (570 backend + 407 frontend)

Cualquier cambio que rompa este baseline = commit bloqueado hasta arreglar.

## Error Messages

**Si tests fallan:**
```
⚠️ Tests failing BEFORE commit

Backend: 568/570 passing (2 failures)
Frontend: 405/407 passing (2 failures)

Fix these BEFORE committing. Brain #6 demands ZERO failures.
```

**Si GGA hook falta:**
```
⚠️ GGA hook not configured

Expected: .pre-commit-config.yaml at ROOT
Current: [missing]

Gentleman Guardian Angel validates:
- Security (secrets, tokens, private IPs)
- TypeScript/React standards
- Accessibility (ARIA, WCAG 2.1 AA)
- Performance (bundle size, Lighthouse)

Configure GGA before committing.
```

## Related Commands

- `/mm:ask-qa` — Consult Brain #6 directly on testing/CI/CD strategy
- `/mm:execute-phase N` — Execute phase with Brain #7 validation
- `/mm:complete-phase N` — Execute + auto BRAIN-FEED update

## Saved to Memory

This skill saved to Engram with `topic_key: pattern/safe-commit-cognitive-barrier` after first use.
