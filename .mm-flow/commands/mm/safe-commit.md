---
description: Pre-commit cognitive barrier that enforces GGA validation and Brain #6 testing standards. Blocks --no-verify, validates tests pass, checks conventional commits, integrates with Brain #6 QA/DevOps. Auto-corrects errors before committing.
argument-hint: "[--check | --fix | --message <msg>]"
---

# /mm:safe-commit

**Barrera cognitiva programática que NUNCA permite `--no-verify`.**

Handler Python que valida ANTES de commitear: tests pasando (0 fallas), GGA hook configurado, formato convencional correcto, sin "Co-Authored-By". Si detecta `--no-verify`, REVIERTE el commit automáticamente.

## Usage

```bash
/mm:safe-commit                    # Valida TODO y commitea cambios staged
/mm:safe-commit --check            # Solo checkea (dry-run), no commitea
/mm:safe-commit --fix              # Auto-corrige issues de GGA y commitea
/mm:safe-commit --message "feat(x): message"  # Commit con mensaje específico
```

## Handler Execution

Este comando ejecuta `safe_commit_handler.py` (también compatible con el alias
`safe-commit-handler.py`) que implementa:

1. **Detección de `--no-verify`** → Revierte commit + explicación detallada
2. **Tests backend** → `cd apps/api && uv run pytest` (0 fallas toleradas)
3. **Tests frontend** → `pnpm --prefix apps/web test run` (0 fallas toleradas)
4. **GGA hook** → Verifica `.pre-commit-config.yaml` en ROOT
5. **GGA validación** → `pre-commit run --all-files`
6. **Formato convencional** → `type(scope): description`
7. **Sin AI attribution** → Remueve "Co-Authored-By:"

## What Happens

### 1. Detección Reactiva

**IMPORTANTE: Los hooks NO pueden bloquear comandos en Claude Code.**

El hook `~/.claude/hooks/mm-safe-commit-pre-guard.js` detecta `git commit --no-verify` y muestra una ADVERTENCIA, pero **NO puede bloquear el comando** (Claude Code ignora los exit codes de los hooks).

**Cómo funciona:**
1. **Hook (automático):** PreToolUse detecta `git commit --no-verify` → Muestra advertencia (NO bloquea)
2. **Slash command (manual):** Usás `/mm:safe-commit` → Commitea con validación completa

**⚠️ LIMITACIÓN:** Claude Code NO respeta exit codes de hooks PreToolUse. La única forma real de bloquear es:
- Usar `/mm:safe-commit` manualmente (RECOMENDADO)
- Crear alias: `alias git='~/.claude/bin/git-safe'` en tu shell

### 2. Bloqueo de `--no-verify`

**IMPORTANTE: Si usás `--no-verify`, el commit se REVERTIRÁ automáticamente.**

Si detecto `--no-verify`:

```
❌ COMMIT REVERTIDO: Usaste --no-verify

El commit se deshizo automáticamente.
💡 Usá: /mm:safe-commit

🔍 ¿POR QUÉ ESTÁ PROHIBIDO?

--no-verify saltea GGA que valida:

Security:
• Hardcoded credentials (API keys, tokens, passwords)
• Private IPs (192.168.x.x, 10.x.x.x)
• Secrets antes de llegar al repo

Code Quality:
• TypeScript/React standards
• Conventions del proyecto
• Anti-patrones comunes

Accessibility:
• ARIA labels y roles
• WCAG 2.1 AA compliance
• Keyboard navigation

Performance:
• Bundle size optimización
• Lighthouse scores
• Image optimization

🚨 INVOCANDO: /systematic-debugging

Investigación: ¿Por qué se usó --no-verify?
Raíz: ¿Qué error de GGA causó esto?
Resolución: ¿Cómo arreglar el error raíz?
```

**El sistema automáticamente:**
1. Revierte el commit (`git reset --soft HEAD~1`)
2. Mantiene tus cambios staged (no los perdés)
3. Invoca `/systematic-debugging` para investigar la raíz
4. Te guía para resolver el problema que causó el uso de `--no-verify`

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
