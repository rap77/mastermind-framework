# PRP-001: mastermind-cli Implementation

**Status:** Ready to Implement (after PRP-000)
**Priority:** Critical (core functionality)
**Estimated Time:** 2-3 hours
**Dependencies:** PRP-000

---

## Executive Summary

Implementar el CLI `mastermind` con todos los comandos para gestión de fuentes, cerebros y framework. El CLI es la interfaz principal del framework y debe permitir: crear/validar/actualizar fuentes, consultar estado de cerebros, y preparar export para NotebookLM.

---

## Context from Clarification Session

### Decisiones Críticas

1. **Comando:** `mastermind` con alias `mm`
2. **Stack:** Python con `uv` (consistente con el repo)
3. **Librerías CLI:** `click` (framework), `rich` (output bonito), `pyyaml` (parsing), `gitpython` (commits)

### Comandos del CLI

```
mastermind source new       → Crear nueva fuente desde plantilla
mastermind source update    → Actualizar fuente (auto-incrementa versión)
mastermind source validate  → Validar calidad de fuentes
mastermind source status    → Ver estado de fuentes de un cerebro
mastermind source list      → Listar todas las fuentes con metadata
mastermind source export    → Exportar para NotebookLM (sin YAML)

mastermind brain status     → Ver estado completo de un cerebro
mastermind brain validate   → Validar cerebro sin gaps
mastermind brain package    → Empaquetar cerebro para distribución

mastermind framework status → Estado global del framework
mastermind framework release→ Crear release con tag + changelog

mastermind brief            → Crear brief interactivo (FEATURE FUTURA)
mastermind config           → Configuración (FEATURE FUTURA)
```

---

## External Resources

### Click Documentation
- https://click.palletsprojects.com/ - Python CLI framework
- https://click.palletsprojects.com/en/8.1.x/arguments/ - Opciones y argumentos
- https://click.palletsprojects.com/en/8.1.x/commands/ - Múltiples comandos

### Rich Documentation
- https://rich.readthedocs.io/ - Terminal output bonito
- https://rich.readthedocs.io/en/stable/progress.html - Progress bars
- https://rich.readthedocs.io/en/stable/table.html - Tablas

### PyYAML
- https://pyyaml.org/wiki/PyYAMLDocumentation - Parsing YAML

### GitPython
- https://gitpython.readthedocs.io/ - Git operations desde Python

---

## Implementation Blueprint

### Pseudocode - Main CLI Structure

```python
# mastermind_cli/main.py
import click
from rich.console import Console
from rich.table import Table

console = Console()

@click.group()
@click.version_option(version="0.1.0")
def cli():
    """MasterMind Framework - AI-powered expert brains."""
    pass

# Group: source
@cli.group()
def source():
    """Manage source files for brains."""
    pass

@source.command('new')
@click.argument('source_id')
@click.option('--brain', required=True, help='Brain ID (e.g., 01-product-strategy)')
def source_new(source_id, brain):
    """Create new source from template."""
    # 1. Read template from templates/brain-template/sources/FUENTE-000-plantilla.md
    # 2. Generate new source with YAML front matter
    # 3. Save to docs/software-development/{brain}/sources/

@source.command('update')
@click.argument('source_id')
@click.option('--change', required=True, help='Description of changes')
def source_update(source_id, change):
    """Update source with version bump."""
    # 1. Find source file by ID
    # 2. Parse YAML front matter
    # 3. Increment version (1.0.0 -> 1.0.1)
    # 4. Add to changelog
    # 5. Update last_updated
    # 6. Git commit automático

@source.command('validate')
@click.option('--brain', required=True)
def source_validate(brain):
    """Validate all sources in a brain."""
    # Check YAML required fields
    # Check content sections (5 sections)
    # Check principles count (min 3)
    # Print errors if any

# Group: brain
@cli.group()
def brain():
    """Manage brain configuration."""
    pass

@brain.command('status')
@click.argument('brain_id')
def brain_status(brain_id):
    """Show complete brain status."""
    # Show sources count
    # Show skills covered
    # Show gaps
    # Show experts

# Group: framework
@cli.group()
def framework():
    """Framework-level operations."""
    pass

@framework.command('status')
def framework_status():
    """Global framework status."""
    # Show all brains
    # Show total sources
    # Show framework health
```

---

## Tasks (in Order)

### Task 1: Estructura del Proyecto CLI (15 min)
- [ ] Crear `tools/mastermind-cli/` con estructura uv
- [ ] `uv init` en subdirectorio
- [ ] Crear módulos: `__init__.py`, `main.py`, `commands/`
- [ ] Configurar `pyproject.toml` con scripts entry point

### Task 2: Command `source new` (30 min)
- [ ] Leer plantilla desde `templates/brain-template/sources/FUENTE-000-plantilla.md`
- [ ] Generar YAML front matter con campos obligatorios
- [ ] Crear archivo con nombre correcto: `FUENTE-NNN-{titulo}.md`
- [ ] Validar que source_id no exista
- [ ] Output: Rich confirmation con ruta creada

### Task 3: Command `source update` (45 min)
- [ ] Buscar fuente por ID en todo el repo
- [ ] Parsear YAML front matter con `pyyaml`
- [ ] Auto-incrementar versión (semver patch)
- [ ] Actualizar `last_updated` con fecha actual
- [ ] Agregar al `changelog` array
- [ ] Escribir YAML de vuelta al archivo
- [ ] Git commit automático con `gitpython`
- [ ] Output: Rich diff de versiones

### Task 4: Command `source validate` (30 min)
- [ ] Validar campos YAML obligatorios
- [ ] Validar secciones de contenido (5 secciones)
- [ ] Validar count de principios (>= 3)
- [ ] Output: Tabla con errores o ✅ success

### Task 5: Commands `source status/list` (20 min)
- [ ] `source list`: Tabla con todas las fuentes y metadata
- [ ] `source status --brain`: Resumen de cerebro específico
- [ ] Output: Rich tables con colores

### Task 6: Command `source export` (30 min)
- [ ] Leer archivos con YAML front matter
- [ ] Remover YAML (entre `---` y `---`)
- [ ] Guardar en `dist/notebooklm/{brain}/`
- [ ] Output: Count de archivos exportados

### Task 7: Commands `brain status/validate` (20 min)
- [ ] Leer `brain-spec.yaml` del cerebro
- [ ] Comparar skills requeridas vs fuentes cubiertas
- [ ] Identificar gaps
- [ ] Output: Rich panel con estado del cerebro

### Task 8: Commands `framework status/release` (15 min)
- [ ] `framework status`: Dashboard global
- [ ] `framework release`: Git tag + changelog

### Task 9: Testing de Comandos (20 min)
- [ ] Probar cada comando con casos de prueba
- [ ] Validar outputs con Rich
- [ ] Verificar git commits

### Task 10: Documentación CLI (15 min)
- [ ] Agregar `--help` a todos los comandos
- [ ] Crear `docs/CLI-REFERENCE.md`
- [ ] Documentar ejemplos de uso

---

## File Structure Created

```
tools/mastermind-cli/
├── pyproject.toml           # CLI dependencies
├── mastermind_cli/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── cli.py               # Click commands
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── source.py        # source commands
│   │   ├── brain.py         # brain commands
│   │   └── framework.py     # framework commands
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── yaml.py          # YAML front matter parser
│   │   ├── git.py           # Git operations
│   │   └── validation.py    # Validation logic
│   └── config/
│       ├── __init__.py
│       └── templates.yaml   # File templates
└── tests/
    ├── test_source.py
    └── test_brain.py
```

---

## Key Code Patterns

### YAML Front Matter Parser

```python
# utils/yaml.py
import re
import yaml

def read_yaml_frontmatter(filepath):
    """Parse YAML front matter from markdown file."""
    with open(filepath) as f:
        content = f.read()

    # Extract YAML between --- markers
    match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if not match:
        return None, content

    yaml_str, markdown = match.groups()
    metadata = yaml.safe_load(yaml_str)
    return metadata, markdown

def write_yaml_frontmatter(filepath, metadata, content):
    """Write file with YAML front matter."""
    yaml_str = yaml.dump(metadata, default_flow_style=False)
    with open(filepath, 'w') as f:
        f.write(f'---\n{yaml_str}---\n\n{content}')
```

### Version Increment

```python
# utils/git.py
from semver import VersionInfo

def increment_patch(version_string):
    """Increment patch version (1.0.0 -> 1.0.1)."""
    version = VersionInfo.parse(version_string)
    return str(version.bump_patch())
```

### Git Auto-commit

```python
# utils/git.py
import git
from git import Repo

def git_commit(filepath, message):
    """Create git commit for file change."""
    repo = Repo('.')
    repo.index.add([filepath])
    repo.index.commit(message)
```

---

## Validation Gates

```bash
# 1. Instalar CLI
cd tools/mastermind-cli
uv sync
uv run mastermind --help

# 2. Probar comandos básicos
uv run mastermind source list
uv run mastermind framework status

# 3. Probar validación
uv run mastermind source validate --brain 01-product-strategy

# 4. Probar export
uv run mastermind source export --brain 01-product-strategy --format notebooklm

# 5. Verificar archivos creados
ls -la dist/notebooklm/

# 6. Verificar git commits
git log --oneline | head -5
```

---

## Definition of Done

- [ ] CLI instalado y funcional (`mastermind --help` funciona)
- [ ] Comando `source new` crea fuente con YAML correcto
- [ ] Comando `source update` incrementa versión y hace git commit
- [ ] Comando `source validate` detecta errores de calidad
- [ ] Comando `source export` genera archivos sin YAML
- [ ] Comando `brain status` muestra gaps de cerebro
- [ ] Comando `framework status` muestra dashboard global
- [ ] Alias `mm` funciona
- [ ] Todos los comandos tienen `--help`
- [ ] Tests básicos pasan
- [ ] Documentación CLI creada

---

## Error Handling Strategy

| Error | Acción |
|-------|--------|
| Fuente no encontrada | Error con sugerencia de fuentes similares |
| YAML inválido | Error con línea específica del error |
| Source ID duplicado | Error con lista de IDs existentes |
| Git dirty state | Advertencia - offer stash o commit |
| Brain no existe | Error con lista de brains disponibles |
| Template no encontrado | Error con ruta esperada |

---

## Gotchas & Notes

1. **YAML Front Matter:** El formato es `---\nYAML\n---\n\nMarkdown`. Asegurarse de manejar correctamente los saltos de línea.

2. **Semver:** Usar `semver` library para version management. No hacer string manipulation manual.

3. **Git Commits:** Usar conventional commits format: `update(source): FUENTE-001: agregado framework de discovery`

4. **Rich Tables:** Configurar `max_width` para evitar problemas en terminales angostos.

5. **File Paths:** Todas las rutas deben ser relativas a la raíz del proyecto, no al subdirectorio `tools/mastermind-cli/`.

6. **Uso de `uv`:** El CLI se ejecuta con `uv run mastermind` que activa el venv temporal.

7. **Tests:** Mantener tests simples por ahora. PRP de testing vendrá más adelante.

---

## Dependencies (pyproject.toml)

```toml
[project]
name = "mastermind-cli"
version = "0.1.0"
requires-python = ">=3.14"
dependencies = [
    "click>=8.1.0",
    "rich>=13.0.0",
    "pyyaml>=6.0",
    "gitpython>=3.1.0",
    "semver>=3.0.0",
]

[project.scripts]
mastermind = "mastermind_cli.main:cli"
mm = "mastermind_cli.main:cli"

[tool.uv]
dev-dependencies = [
    "pytest>=8.0.0",
    "ruff>=0.8.0",
]
```

---

## Output Files Created

| Archivo | Propósito |
|---------|-----------|
| `tools/mastermind-cli/main.py` | Entry point del CLI |
| `tools/mastermind-cli/mastermind_cli/` | Módulos del CLI |
| `docs/CLI-REFERENCE.md` | Documentación de comandos |
| `tests/test_source.py` | Tests de comandos source |

---

## Next Steps

After this PRP:
- → PRP-002: YAML front matter en fichas existentes
- → PRP-003: System prompts de agentes
- → PRP-004: NotebookLM integration

---

## Confidence Score

**8.5/10** - Alta confianza de éxito.

**Rationale:** Click y Rich son librerías maduras y bien documentadas. Los patrones están claros. Riesgo principal es YAML front matter parsing que puede tener edge cases. El tiempo estimado de 2-3 horas es realista.

---

## Context for AI Agent

**Archivos clave para leer antes de implementar:**
1. `/home/rpadron/proy/mastermind/docs/design/10-Plan-Implementacion-Claude-Code.md` - Sección Fase 2
2. `/home/rpadron/proy/mastermind/docs/design/04-Plantilla-Ficha-Fuente-Maestra.md` - Plantilla de fuente
3. `/home/rpadron/proy/mastermind/docs/software-development/sources/FUENTE-001-inspired-cagan.md` - Ejemplo real

**Comando para iniciar:**
```bash
cd /home/rpadron/proy/mastermind/tools/mastermind-cli
uv init
uv add click rich pyyaml gitpython semver
```

**Resultado esperado:**
CLI funcional con comandos `source new/update/validate/export`, `brain status`, `framework status`. Alias `mm` funciona.
