# Stack Tecnológico Estándar

**Version:** 1.0.0
**Fecha:** 2026-03-07
**Status:** Activo

---

## Overview

Este documento define el stack tecnológico estándar para todos los proyectos de Python que utilizan la arquitectura del MasterMind Framework o siguen sus patrones.

## Principios Rectores

1. **Modern Python:** Última versión estable con features modernos
2. **UV First:** UV como package manager por defecto
3. **Type Safety:** Type hints + mypy siempre que sea posible
4. **Developer Experience:** Herramientas que mejoren la productividad
5. **Minimal Dependencies:** Solo lo necesario, sin sobrecarga

---

## Stack Definitivo

### Core

| Componente | Versión | Propósito |
|-------------|---------|-----------|
| **Python** | 3.14+ | Lenguaje principal (type hints nativos) |
| **uv** | Última | Package manager (reemplaza pip/poetry) |

### Dependencias Esenciales

```toml
dependencies = [
    # CLI Framework
    "click>=8.1.0",           # Comandos CLI
    "rich>=13.0.0",            # Output terminal bonito

    # Data & Validation
    "pydantic>=2.10.0",         # Validation type-safe
    "pyyaml>=6.0",             # Archivos YAML
    "pydantic-settings>=2.6.0", # Settings management

    # Git
    "gitpython>=3.1.0",        # Operaciones Git
]
```

### Dependencias de Desarrollo

```toml
[project.optional-dependencies]
dev = [
    # Testing
    "pytest>=9.0.0",
    "pytest-cov>=6.0.0",
    "pytest-asyncio>=0.24.0",

    # Code Quality
    "ruff>=0.15.0",            # Linter + formatter (todo en uno)
    "mypy>=1.14.0",             # Type checker
]
```

---

## Herramientas de CLI

### UV (Package Manager)

**Por qué UV:**
- 10-100x más rápido que pip
- Resuelve dependencias en paralelo
- Administra entornos virtuales automáticamente
- Reemplaza: pip, pip-tools, poetry, virtualenv, pipx

```bash
# Instalación
curl -LsSf https://astral.sh/uv/install.sh | sh

# Crear proyecto
uv init mi-proyecto
cd mi-proyecto

# Instalar dependencias
uv add click rich pydantic

# Instalar dev dependencies
uv add --dev pytest ruff mypy

# Ejecutar
uv run python main.py
uv run pytest
```

### Comandos UV Esenciales

| Comando | Propósito |
|---------|-----------|
| `uv init` | Crear nuevo proyecto |
| `uv add <pkg>` | Agregar dependencia |
| `uv add --dev <pkg>` | Agregar dependencia de desarrollo |
| `uv sync` | Sincronizar lockfile |
| `uv lock --upgrade` | Actualizar dependencias |
| `uv run <cmd>` | Ejecutar comando en el entorno |
| `uv pip install` | Instalar paquete (si uv no lo tiene) |
| `uv remove <pkg>` | Remover dependencia |

---

## Estructura de Proyecto Estándar

```
mi-proyecto/
├── pyproject.toml              # Config principal (PEP 621)
├── uv.lock                     # Lock file de dependencias
├── README.md                   # Documentación del proyecto
├── .gitignore                  # Archivos a ignorar en Git
│
├── src/                        # Código fuente (PEP 420)
│   └── mi_proyecto/
│       ├── __init__.py
│       ├── cli.py              # Comandos Click (entry point)
│       ├── models/             # Pydantic models
│       │   ├── __init__.py
│       │   └── domain.py
│       ├── services/           # Lógica de negocio
│       │   ├── __init__.py
│       │   └── core.py
│       ├── utils/              # Utilidades compartidas
│       │   ├── __init__.py
│       │   └── helpers.py
│       └── config/             # Configuración
│           ├── __init__.py
│           └── settings.py
│
├── tests/                      # Tests (PEP 8)
│   ├── __init__.py
│   ├── conftest.py            # Config pytest global
│   ├── test_cli.py            # Tests de CLI
│   ├── test_models.py         # Tests de models
│   └── fixtures/              # Datos de prueba
│
├── config/                     # Archivos de configuración
│   ├── settings.yaml          # Settings (opcional)
│   └── schema.yaml            # Schemas (opcional)
│
├── scripts/                    # Scripts de utilidad
│   ├── setup.sh
│   └── migrate.py
│
├── docs/                       # Documentación adicional
│   └── api.md
│
└── .github/                    # GitHub specific
    └── workflows/
        └── ci.yml
```

---

## pyproject.toml Plantilla

```toml
[project]
name = "mi-proyecto"
version = "0.1.0"
description = "Descripción del proyecto"
readme = "README.md"
requires-python = ">=3.14"
dependencies = [
    "click>=8.1.0",
    "rich>=13.0.0",
    "pydantic>=2.10.0",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=9.0.0",
    "pytest-cov>=6.0.0",
    "ruff>=0.15.0",
    "mypy>=1.14.0",
]

[project.scripts]
mi-proyecto = "mi_proyecto.cli:cli"
mp = "mi_proyecto.cli:cli"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/mi_proyecto"]

# ====================
# Ruff (Linter + Formatter)
# ====================
[tool.ruff]
target-version = "py314"
line-length = 100

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # Pyflakes
    "I",      # isort
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

# ====================
# MyPy (Type Checker)
# ====================
[tool.mypy]
python_version = "3.14"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false  # Habilitar gradualmente

# ====================
# Pytest (Testing)
# ====================
[tool.pytest.ini_options]
minversion = "9.0"
testpaths = ["tests"]
addopts = [
    "--cov=src/mi_proyecto",
    "--cov-report=term-missing",
]
```

---

## Ruff (Linter + Formatter)

**Por qué Ruff:**
- Escrito en Rust (ultra rápido)
- Reemplaza: flake8, isort, black, pyupgrade
- Configuración simple en `pyproject.toml`

```bash
# Verificar código
uv tool run ruff check .

# Formatear código
uv tool run ruff format .

# Verificar + formatear
uv tool run ruff check --fix .
```

### Reglas Activadas

| Código | Propósito |
|--------|-----------|
| E, W | pycodestyle (errores y warnings) |
| F | Pyflakes (detecta errores lógicos) |
| I | isort (ordena imports) |
| B | flake8-bugbear (detecta bugs comunes) |
| UP | pyupgrade (actualiza syntax) |
| ARG | argumentos no usados |
| SIM | simplifica código |

---

## MyPy (Type Checking)

**Por qué Type Hints:**
- Detecta errores en tiempo de desarrollo
- Mejora autocompletado en IDEs
- Documenta interfaces implícitamente
- Pydantic lo requiere

```bash
# Type check
uv run mypy src/

# Type check con reporte detallado
uv run mypy src/ --show-error-codes
```

### Estrategia de Adopción

1. **Fase 1 (Inicio):** `disallow_untyped_defs = false`
2. **Fase 2 (Crecimiento):** Activar en módulos nuevos
3. **Fase 3 (Madurez):** `disallow_untyped_defs = true`

---

## Pytest (Testing)

**Por qué Pytest:**
- Fixture system potente
- Plugins ecosistema amplio
- Paralelización incluida
- Discovery automático

```bash
# Correr todos los tests
uv run pytest

# Con coverage
uv run pytest --cov=src/mi_proyecto

# Test específico
uv run pytest tests/test_cli.py

# Verbose
uv run pytest -v

# Stop en primer failure
uv run pytest -x
```

### Estructura de Tests

```python
# tests/conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def sample_data():
    """Fixture con datos de prueba."""
    return {"key": "value"}

# tests/test_cli.py
def test_command_list(cli_runner, sample_data):
    """Test command list."""
    result = cli_runner.invoke(["list"])
    assert result.exit_code == 0
    assert "key" in result.output
```

---

## Pydantic (Data Validation)

**Por qué Pydantic:**
- Validación automática
- Type coercion
- JSON Schema export
- Settings management
- Performance (Rust core)

```python
from pydantic import BaseModel, Field, field_validator

class User(BaseModel):
    name: str = Field(..., min_length=1)
    email: str
    age: int = Field(..., ge=0, le=120)

    @field_validator('email')
    @classmethod
    def email_must_contain_at(cls, v: str) -> str:
        if '@' not in v:
            raise ValueError('must contain @')
        return v

# Uso
user = User(name="Juan", email="juan@example.com", age=30)
```

---

## Click (CLI Framework)

**Por qué Click:**
- Composición de comandos
- Argument parsing robusto
- Auto-genera help
- Colors y tabulación incluida

```python
import click
from rich.console import Console
from rich.table import Table

console = Console()

@click.group()
def cli():
    """Mi proyecto CLI."""
    pass

@cli.command()
@click.option("--verbose", "-v", is_flag=True)
def list(verbose: bool):
    """Listar recursos."""
    if verbose:
        console.print("[yellow]Modo verbose[/yellow]")

    table = Table(title="Recursos")
    table.add_column("ID", style="cyan")
    table.add_column("Nombre")
    table.add_row("1", "Recurso 1")
    console.print(table)

if __name__ == "__main__":
    cli()
```

---

## Rich (Terminal Output)

**Por qué Rich:**
- Tablas bonitas
- Progress bars
- Syntax highlighting
- Tracebacks amigables

```python
from rich.console import Console
from rich.progress import track
from rich.table import Table

console = Console()

# Tabla
table = Table(title="Users")
table.add_column("ID")
table.add_column("Name")
table.add_row("1", "Alice")
table.add_row("2", "Bob")
console.print(table)

# Progress bar
items = list(range(100))
for item in track(items, description="Procesando..."):
    process(item)

# Panel con texto
from rich.panel import Panel
console.print(Panel("Hola Mundo", title="Mensaje"))
```

---

## Gitignore Estándar

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg

# UV
.uv/
uv.lock

# Virtual environments
.venv/
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# MyPy
.mypy_cache/
.dmypy.json
dmypy.json

# Ruff
.ruff_cache/

# Logs
*.log

# OS
.DS_Store
Thumbs.db
```

---

## Workflow de Desarrollo

### 1. Iniciar Proyecto

```bash
# Crear proyecto
uv init --name mi-proyecto --app
cd mi-proyecto

# Crear estructura
mkdir -p src/mi_proyecto/{models,services,utils,config}
mkdir -p tests/{fixtures}
touch src/mi_proyecto/__init__.py
touch tests/__init__.py

# Instalar dependencias
uv add click rich pydantic pyyaml
uv add --dev pytest pytest-cov ruff mypy

# Crear scripts
uv run ruff format .
```

### 2. Desarrollo Iterativo

```bash
# Escribir código
vim src/mi_proyecto/cli.py

# Type check
uv run mypy src/

# Formatear
uv run ruff format .

# Lint
uv run ruff check .

# Tests
uv run pytest

# Coverage
uv run pytest --cov
```

### 3. Commit Changes

```bash
git add .
git commit -m "feat: add new feature"
```

---

## Checklist de Nuevo Proyecto

- [ ] UV instalado
- [ ] `uv init` ejecutado
- [ ] `pyproject.toml` configurado
- [ ] Estructura de carpetas creada
- [ ] Dependencias instaladas (click, rich, pydantic, pyyaml)
- [ ] Dev dependencies instaladas (pytest, ruff, mypy)
- [ ] `.gitignore` configurado
- [ ] Tests básicos escritos
- [ ] CI/CD configurado (opcional)
- [ ] README.md creado

---

## Recursos de Aprendizaje

| Herramienta | Documentación |
|-------------|---------------|
| **UV** | https://docs.astral.sh/uv/ |
| **Ruff** | https://docs.astral.sh/ruff/ |
| **MyPy** | https://mypy.readthedocs.io/ |
| **Pytest** | https://docs.pytest.org/ |
| **Pydantic** | https://docs.pydantic.dev/ |
| **Click** | https://click.palletsprojects.com/ |
| **Rich** | https://rich.readthedocs.io/ |
| **Python 3.14** | https://docs.python.org/3.14/whatsnew/ |

---

## Changelog

| Fecha | Cambio |
|-------|--------|
| 2026-03-07 | Versión inicial 1.0.0 |

---

**Maintainer:** MasterMind Framework Team
**Last Updated:** 2026-03-07
