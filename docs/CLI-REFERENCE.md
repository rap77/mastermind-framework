# MasterMind CLI - Referencia de Comandos

CLI del MasterMind Framework para gestión de cerebros especializados y fuentes de conocimiento.

## Instalación

```bash
cd tools/mastermind-cli
uv sync
```

## Comandos Disponibles

### Comandos Source

Gestión de archivos de fuentes (FUENTE-*.md).

#### `mastermind source new`

Crear nueva fuente desde plantilla.

```bash
mastermind source new FUENTE-011 \
  --brain 01-product-strategy \
  --title "The Mom Test" \
  --author "Rob Fitzpatrick" \
  --type book \
  --year 2013
```

#### `mastermind source update`

Actualizar fuente con auto-incremento de versión y git commit.

```bash
mastermind source update FUENTE-001 \
  --change "Agregado framework de discovery"
```

#### `mastermind source validate`

Validar todas las fuentes de un cerebro.

```bash
mastermind source validate --brain 01-product-strategy
```

#### `mastermind source list`

Listar todas las fuentes con metadata.

```bash
mastermind source list
```

#### `mastermind source status`

Ver estado de fuentes de un cerebro.

```bash
mastermind source status --brain 01-product-strategy
```

#### `mastermind source export`

Exportar fuentes para NotebookLM (sin YAML front matter).

```bash
mastermind source export --brain 01-product-strategy --output dist/notebooklm
```

### Comandos Brain

Gestión de configuración de cerebros.

#### `mastermind brain status`

Ver estado completo de un cerebro.

```bash
mastermind brain status 01-product-strategy
```

#### `mastermind brain validate`

Validar cerebro sin gaps.

```bash
mastermind brain validate 01-product-strategy
```

#### `mastermind brain package`

Empaquetar cerebro para distribución (próximamente).

```bash
mastermind brain package 01-product-strategy --output dist/packages
```

### Comandos Framework

Operaciones a nivel de framework.

#### `mastermind framework status`

Estado global del framework.

```bash
mastermind framework status
```

#### `mastermind framework release`

Crear release con tag + changelog.

```bash
mastermind framework release --version 0.2.0 --message "Add CLI support"
```

### Otros Comandos

#### `mastermind info`

Mostrar información del framework.

```bash
mastermind info
```

## Alias

El comando `mm` es un alias de `mastermind`:

```bash
mm source list
mm framework status
```

## Estructura de Archivos

```
mastermind-cli/
├── mastermind_cli/
│   ├── main.py              # Entry point
│   ├── commands/
│   │   ├── source.py        # Comandos de fuentes
│   │   ├── brain.py         # Comandos de cerebros
│   │   └── framework.py     # Comandos del framework
│   └── utils/
│       ├── yaml.py          # Parser de YAML front matter
│       ├── git.py           # Operaciones de Git
│       └── validation.py    # Lógica de validación
└── tests/
    ├── test_source.py
    └── test_brain.py
```

## Convenciones

### Formato de YAML Front Matter

```yaml
---
source_id: "FUENTE-001"
brain: "brain-software-01-product-strategy"
niche: "software-development"
title: "Título completo"
author: "Nombre del autor"
expert_id: "EXP-001"
type: "book|video|article|course|documentation"
language: "es|en"
year: 2020
skills_covered: ["H1", "H3"]
distillation_date: "2026-02-22"
distillation_quality: "complete|partial|pending"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-02-22"
changelog:
  - version: "1.0.1"
    date: "2026-02-22"
    changes:
      - "Descripción del cambio"
---
```

### Mensajes de Commit

El CLI usa conventional commits:

```
update(source): FUENTE-001: agregado framework de discovery
fix(source): FUENTE-002: corregido formato de YAML
```

## Desarrollo

### Ejecutar Tests

```bash
uv run pytest tests/ -v
```

### Formato con Ruff

```bash
uv run ruff check .
uv run ruff format .
```

## Troubleshooting

### Error: "Brain not found"

Verifica que el ID del cerebro sea correcto:
```bash
mastermind framework status  # Ver lista de cerebros disponibles
```

### Error: "No YAML front matter found"

Asegúrate de que el archivo tenga el formato correcto:
```markdown
---
yaml front matter aquí
---

Contenido markdown aquí
```

### Git commit falla

Verifica que el repo esté limpio:
```bash
git status
```

## Roadmap

- [ ] Comando `mastermind brief` - Crear brief interactivo
- [ ] Comando `mastermind config` - Configuración del framework
- [ ] Integración con NotebookLM MCP
- [ ] Export en otros formatos (JSON, PDF)
