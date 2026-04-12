# Installer Update - 2026-03-07

## Fecha
2026-03-07

## Cambios Realizados

**Commit:** 00155b2

Actualización completa del instalador para soportar la estructura de namespace `mm:` y mejora del desinstalador.

## Instalador Actualizado

### Cambios en `mastermind install init`

**Antes (estructura plana):**
```
.claude/
├── commands/
│   ├── ask-product.md
│   ├── project-health-check.md
│   └── ...
├── hooks/
│   └── *.sh
└── skills/
    └── *.md
```

**Ahora (estructura con namespace):**
```
.claude/
├── commands/
│   └── mm/               # ← Namespace folder
│       ├── ask-product.md      # → /mm:ask-product
│       ├── project-health-check.md  # → /mm:project-health-check
│       └── ...
├── hooks/
│   └── mm/               # ← Namespace folder
└── agents/
    └── mm/               # ← Namespace folder
```

### Comandos Copiados

**19 slash commands** en `.claude/commands/mm/`:
- ask-product.md, ask-ux.md, ask-design.md
- ask-frontend.md, ask-backend.md, ask-qa.md, ask-growth.md
- ask-all.md, ask-ui-docs.md
- project-health-check.md, audit.md
- lite-prd-generator.md, prd-clarifier.md
- generate-prp.md, execute-prp.md
- improve-prompt.md, ux-spec-to-prompt.md
- explore-first.md

### Mensajes Actualizados

**Éxito de instalación:**
```
✓ MasterMind Framework installed successfully!

Project: my-project
Framework: /path/to/mastermind
Active brains: 7

Next steps:
  1. Restart Claude Code in this project
  2. Use /mm:ask-product to consult the Product brain
  3. Use /mm:project-audit for full 7-brain analysis
  4. Run mastermind install status to verify

Configuration: .mastermind/config.yaml
Commands: .claude/commands/mm/*.md
All commands use /mm: namespace
```

**README Appendix (agregado automáticamente):**
```markdown
## 🧠 MasterMind Framework

### Available Slash Commands

All commands use the `/mm:` namespace:

**Consult Brains:**
- `/mm:ask-product` - Product Strategy
- `/mm:ask-ux` - UX Research
- `/mm:ask-design` - UI Design
- `/mm:ask-frontend` - Frontend Architecture
- `/mm:ask-backend` - Backend Architecture
- `/mm:ask-qa` - QA/DevOps
- `/mm:ask-growth` - Growth/Data
- `/mm:ask-all` - All 7 brains as a team

**Project Management:**
- `/mm:project-audit` - Complete 7-brain analysis
- `/mm:audit` - Quick project audit

**PRDs & Specs:**
- `/mm:lite-prd-generator` - Generate PRD from rough idea
- `/mm:prd-clarifier` - Refine and clarify PRD
```

## Desinstalador Mejorado

### Nuevas Funcionalidades

**Opción `--remove-readme`:**
```bash
mastermind install uninstall --remove-readme
```
Elimina también la sección de MasterMind del README.md usando regex.

**Limpieza de carpetas vacías:**
- Si después de eliminar `commands/mm/` la carpeta `commands/` queda vacía, también se elimina
- Lo mismo para `hooks/` y `agents/`

**Mensajes detallados:**
```
Uninstalling MasterMind Framework...

✓ Removed .mastermind-active
✓ Removed .claude/commands/mm/
✓ Removed .claude/hooks/mm/
✓ Removed .claude/agents/mm/
✓ Removed .mastermind/ directory

═════════════════════════════════
✓ MasterMind Framework uninstalled

Removed: 3 namespace folder(s)
Config kept: False

Note: If you want to remove the MasterMind section from README.md, run:
  mastermind install uninstall --remove-readme
═════════════════════════════════
```

### Opciones del Desinstalador

| Opción | Descripción |
|--------|-------------|
| (sin flags) | Elimina todo (config, symlinks, activation file) |
| `--keep-config` | Mantiene `.mastermind/` con la config |
| `--remove-readme` | Elimina sección MasterMind del README |

## Compatibilidad con Versiones Anteriores

**Legacy Support:**
- Si existe `framework/.claude/skills/` (estructura vieja), los copia a `commands/mm/`
- Las instalaciones previas siguen funcionando
- No rompe proyectos existentes

## Uso

### Instalar en un proyecto

```bash
# En tu proyecto
cd /path/to/your-project

# Instalar con detección automática del framework
mastermind install init

# Instalar solo cerebros específicos
mastermind install init --brains #1,#4,#7

# Instalar con path explícito
mastermind install init --framework-path ~/proy/mastermind

# Reinstalar (forzar)
mastermind install init --force
```

### Ver estado

```bash
mastermind install status
```

Muestra:
- Versión del framework
- Path del framework
- Cerebros activos
- Archivos de integración
- Comandos slash disponibles

### Desinstalar

```bash
# Desinstalar completo
mastermind install uninstall

# Mantener config
mastermind install uninstall --keep-config

# Eliminar también sección del README
mastermind install uninstall --remove-readme
```

## Archivos Modificados

- `mastermind_cli/commands/install.py` (142 insertions, 65 deletions)

## Testing

Para probar el instalador:

```bash
# Crear proyecto de prueba
mkdir /tmp/test-project
cd /tmp/test-project

# Inicializar
mastermind install init

# Verificar estructura
ls -la .claude/commands/mm/

# Ver estado
mastermind install status

# Desinstalar
mastermind install uninstall --remove-readme

# Verificar limpieza
ls -la .claude/
```

## Beneficios

1. **Namespace limpio:** Todos los comandos usan `/mm:`
2. **Identificación fácil:** Las carpetas `mm/` identifican recursos de MasterMind
3. **Desinstalación completa:** Elimina todas las carpetas namespace
4. **No conflictos:** No colisiona con otros proyectos o habilidades
5. **Compatibilidad:** Soporta instalaciones viejas y nuevas
