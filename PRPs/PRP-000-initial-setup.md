# PRP-000: Initial Setup & Project Structure

**Status:** Ready to Implement
**Priority:** Critical (blocker for all other PRPs)
**Estimated Time:** 45-60 minutes
**Dependencies:** None

---

## Executive Summary

Crear la estructura completa del proyecto MasterMind Framework, validar el entorno de desarrollo, y preparar el repositorio para las siguientes fases. Este PRP cubre las Fases 0 y 1 del plan de implementación.

---

## Context from Clarification Session

### Decisiones Críticas

1. **Modelo de Negocio:** CLI local ahora → SaaS en v2 (fases separadas, no refactor complejo)
2. **Alcance:** Multi-nicho desde el inicio - estructura modular por dominio
3. **Licencia:** Propietaria (todos los derechos reservados)
4. **Comando:** `mastermind` con alias `mm`
5. **Idioma System Prompts:** Inglés con output bilingüe (se adapta al usuario)

### Archivos de Referencia

- `/home/rpadron/proy/mastermind/docs/design/09-Filesystem-Structure.md` - Estructura completa
- `/home/rpadron/proy/mastermind/docs/design/10-Plan-Implementacion-Claude-Code.md` - Fases 0-5
- `/home/rpadron/proy/mastermind/docs/design/10-Plan-Implementacion-clarification-session.md` - 35 preguntas con decisiones

---

## External Resources

### Python/uv Documentation
- https://docs.astral.sh/uv/ - Package manager oficial
- https://docs.astral.sh/uv/cli/ - Comandos CLI

### Git Conventions
- https://www.conventionalcommits.org/ - Formato de commits
- https://semver.org/ - Versionado semántico

---

## Implementation Blueprint

### Pseudocode - Creación de Estructura

```python
# 1. Validar entorno
check_python_version()  # >= 3.14
check_uv_installed()
check_git_config()

# 2. Crear estructura de carpetas
create_directories([
    "config",
    "logs/evaluations",
    "logs/precedents",
    "projects",
    "templates/brain-template/sources",
    "skills/reusable",
    "agents/orchestrator",
    "agents/evaluator",
    "agents/brains",
    "docs/design",
    "docs/software-development/01-product-strategy-brain/sources",
    "docs/software-development/02-ux-research-brain/sources",
    "docs/software-development/03-ui-design-brain/sources",
    "docs/software-development/04-frontend-brain/sources",
    "docs/software-development/05-backend-brain/sources",
    "docs/software-development/06-qa-devops-brain/sources",
    "docs/software-development/07-growth-data-brain/sources",
])

# 3. Copiar archivos existentes a nuevas ubicaciones
move_design_docs_to_docs_design()
move_sources_to_brain_folder()

# 4. Crear archivos base
create_readme()
create_license()
create_gitignore()

# 5. Git inicial
git_init()
git_initial_commit()
git_tag_v0_1_0()
```

---

## Tasks (in Order)

### Task 1: Validación del Entorno (5 min)
- [ ] Verificar Python >= 3.14: `python3 --version`
- [ ] Verificar uv instalado: `uv --version`
- [ ] Verificar Node/nvm: `node --version`
- [ ] Verificar git config: `git config user.name && git config user.email`
- [ ] Verificar MCP servers (ubicación en otro proyecto)
- [ ] Documentar resultados en `logs/setup-env-validation.md`

### Task 2: Actualizar pyproject.toml (5 min)
- [ ] Actualizar nombre: `mastermind-framework`
- [ ] Agregar descripción: "AI-powered framework for specialized expert brains"
- [ ] Configurar scripts para `mastermind` y alias `mm`
- [ ] Agregar dependencias CLI: `click`, `rich`, `pyyaml`, `gitpython`

### Task 3: Crear Estructura de Carpetas (10 min)
- [ ] Crear carpetas config, logs, projects, templates, skills, agents
- [ ] Crear estructura docs/software-development/ con 7 cerebros
- [ ] Crear subcarpetas sources/ para cada cerebro
- [ ] Verificar estructura coincide con `docs/design/09-Filesystem-Structure.md`

### Task 4: Mover Documentación Existente (10 min)
- [ ] Mover archivos de `docs/design/` a su ubicación correcta
- [ ] Mover 10 fuentes a `docs/software-development/01-product-strategy-brain/sources/`
- [ ] Verificar que no queden archivos huérfanos

### Task 5: Crear Archivos Base (10 min)
- [ ] **README.md:** Descripción del framework con Quick Start
- [ ] **LICENSE:** Licencia propietaria con términos de uso
- [ ] **.gitignore:** Actualizar con reglas específicas (ver abajo)

### Task 6: Git Initial Commit (5 min)
- [ ] `git add .`
- [ ] Commit con conventional commits: `feat: initial project structure with documentation`
- [ ] Tag: `git tag v0.1.0 -m "v0.1.0: Initial structure"`

### Task 7: Documentación de Setup (5 min)
- [ ] Crear `docs/SETUP.md` con instrucciones de instalación
- [ ] Documentar ubicación de MCP servers para migración/configuración

---

## .gitignore Específico

```gitignore
# Python
__pycache__/
*.py[cod]
*.so
.Python
.venv/
uv.lock

# MasterMind Framework
logs/
projects/
dist/
*.db
*.sqlite

# IDE
.idea/
.vscode/
*.swp

# OS
.DS_Store
Thumbs.db

# Secrets
.env
secrets.yaml
```

---

## Validation Gates

```bash
# 1. Verificar estructura creada
find . -type d | wc -l  # Debe ser ~40 directorios

# 2. Verificar archivos base
ls -la | grep -E "(README|LICENSE|pyproject)"

# 3. Verificar git
git status
git log --oneline
git tag

# 4. Verificar Python imports (cuando exista código)
python3 -c "import sys; print(sys.version)"

# 5. Validar YAML syntax (para archivos de config)
python3 -c "import yaml; yaml.safe_load(open('pyproject.toml'))" 2>&1 || true
```

---

## Definition of Done

- [ ] Estructura de carpetas 100% completa según `09-Filesystem-Structure.md`
- [ ] Todos los archivos de diseño en `docs/design/`
- [ ] 10 fuentes del Cerebro #1 en `docs/software-development/01-product-strategy-brain/sources/`
- [ ] README.md funcional con instrucciones de Quick Start
- [ ] LICENSE propietaria creada
- [ ] .gitignore completo
- [ ] Git inicializado con commit v0.1.0
- [ ] pyproject.toml actualizado con dependencias CLI
- [ ] Validación de entorno documentada

---

## Error Handling Strategy

| Error | Acción |
|-------|--------|
| Python < 3.14 | Documentar en logs - continuar con advertencia |
| uv no instalado | Instalar con `curl -LsSf https://astral.sh/uv/install.sh | sh` |
| Git no configurado | Pedir al usuario que configure user.name y user.email |
| MCP servers no encontrados | Documentar - no es blocker para Fase 0-1 |

---

## Gotchas & Notes

1. **Ubicación de MCP servers:** Están en otro proyecto. No migrar en esta fase - solo documentar ubicación para Fase 5.

2. **Nombre del proyecto:** El repo es `mastermind-framework` pero el package Python puede ser `mastermind` o `mente_maestra`. Decisión: usar `mastermind` para simplicidad.

3. **Skills de Claude Code:** Las globales en `~/.claude/skills/` funcionarán automáticamente. No requieren acción en esta fase.

4. **Fuentes ya creadas:** Las 10 fuentes ya existen. Solo moverlas a la ubicación correcta según la estructura.

5. **Licencia propietaria:** NO usar plantilla MIT/Apache. Crear un archivo LICENSE simple que diga "All Rights Reserved" con términos de uso para clientes.

---

## Output Files Created

| Archivo | Propósito |
|---------|-----------|
| `README.md` | Documentación principal |
| `LICENSE` | Términos de licencia |
| `.gitignore` | Exclusiones de git |
| `pyproject.toml` | Configuración Python y dependencias |
| `docs/SETUP.md` | Guía de instalación |
| `logs/setup-env-validation.md` | Resultados de validación |

---

## Next Steps

After this PRP:
- → PRP-001: mastermind-cli implementation
- → PRP-002: YAML front matter en fichas existentes
- → PRP-003: System prompts de agentes
- → PRP-004: NotebookLM integration

---

## Confidence Score

**9/10** - Alta confianza de éxito en one-pass implementation.

**Rationale:** Estructura bien definida, archivos ya existen en gran parte, tareas son principalmente creación de carpetas y mover archivos. Riesgos mínimos - principal riesgo es ubicación de MCP servers que no es crítico para esta fase.

---

## Context for AI Agent

**Archivos clave para leer antes de implementar:**
1. `/home/rpadron/proy/mastermind/docs/design/09-Filesystem-Structure.md` - Estructura completa
2. `/home/rpadron/proy/mastermind/docs/design/10-Plan-Implementacion-Claude-Code.md` - Fase 0-1
3. `/home/rpadron/proy/mastermind/docs/design/10-Plan-Implementacion-clarification-session.md` - Decisiones de 35 preguntas

**Comando para iniciar:**
```bash
cd /home/rpadron/proy/mastermind
# Asegurarse de estar en la rama master
git status
```

**Resultado esperado:**
Estructura completa creada, git inicializado, tag v0.1.0 creado, README funcional.
