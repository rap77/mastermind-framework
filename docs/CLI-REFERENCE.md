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

### Comandos Orchestrate

Orquestación de cerebros para procesar briefs de usuarios.

#### `mastermind orchestrate run`

Ejecutar flujo de orquestación completo.

```bash
# Validación simple (modo mock)
mm orchestrate run "validar idea de app de viajes"

# Con flow específico
mm orchestrate run --flow validation_only "es buena idea esta app?"

# Dry run para ver el plan
mm orchestrate run --dry-run "mi idea de startup"

# Guardar output en archivo
mm orchestrate run -o output.yaml "mi idea"

# Leer brief desde archivo
mm orchestrate run --file brief.md

# Usar MCP real (requiere nlm CLI)
mm orchestrate run --use-mcp "validar mi idea con NotebookLM real"
```

**Opciones:**
- `--file, -f`: Leer brief desde archivo
- `--flow`: Forzar flow específico (full_product, validation_only, design_sprint, build_feature, optimization, technical_review)
- `--dry-run`: Generar plan sin ejecutar
- `--use-mcp`: Usar MCP para llamadas reales a NotebookLM (requiere CLI `nlm`)
- `--output, -o`: Guardar output en archivo
- `--verbose, -v`: Output detallado

#### `mastermind orchestrate go`

Alias corto del comando `run`.

```bash
mm orchestrate go "mi idea"
```

#### Flujos Disponibles

| Flow | Cerebros | Descripción |
|------|----------|-------------|
| `validation_only` | 1 → 7 | Validar idea con Product Strategy + Evaluador |
| `full_product` | 1→2→3→4→5→6→7 | Producto completo |
| `design_sprint` | 1→2→3→7 | Diseño sin construcción |
| `build_feature` | 4→5→6→7 | Implementar feature |
| `optimization` | 7→1 | Optimizar existente |
| `technical_review` | 5→6→7 | Revisión técnica |
| `discovery` | 8 → 1-7 | Entrevista de discovery para briefs ambiguos |

### Comandos Slash (Claude Code)

Comandos disponibles desde Claude Code usando `/mm:`.

#### `/mm:discovery`

Conduct structured discovery interview using Brain #8 (Master Interviewer).

```
/mm:discovery "<problem or vague requirement>"
```

**Ejemplos:**
- `/mm:discovery "Quiero crear una app de delivery"` — Client onboarding
- `/mm:discovery "Necesito un sistema de login moderno"` — Feature clarification
- `/mm:discovery "Implementar OAuth con Google"` — Technical specification
- `/mm:discovery "SEO y content marketing para mi sitio"` — Gap detection

**Qué hace:**
1. Analiza el input para detectar ambigüedad
2. Consulta Brain #8 para diseñar estrategia de entrevista
3. Pregunta preguntas estructuradas interactivamente
4. Rutea cada respuesta a cerebros de dominio (#1-7) para follow-ups
5. Genera documento Q&A completo (JSON/YAML/Markdown)
6. Detecta gaps de conocimiento

**Tipos de output:**
- **Markdown:** Mostrado en la respuesta (human-readable)
- **YAML:** `logs/interviews/hot/YYYY-MM/INTERVIEW-*.yaml` (logging)
- **JSON:** `logs/interviews/json/YYYY-MM/INTERVIEW-*.json` (machine-readable)

**Duración:** 5-15 minutos (10-20 preguntas típico)

**Ver también:** [Documentación del comando](../.claude/commands/mm/discovery.md)

#### Otros comandos `/mm:`

- `/mm:ask-product` — Consult Product Strategy brain sin entrevista
- `/mm:ask-ux` — Consult UX Research brain
- `/mm:ask-frontend` — Consult Frontend Development brain
- `/mm:ask-backend` — Consult Backend Development brain
- `/mm:ask-qa` — Consult QA/DevOps brain
- `/mm:ask-growth` — Consult Growth/Data brain
- `/mm:ask-design` — Consult UI Design brain
- `/mm:ask-all` — Consult ALL 7 brains as a team
- `/mm:project-health-check` — Full 7-brain project analysis
- `/mm:generate-prp` — Create implementation plan from requirements
- `/mm:improve-prompt` — Transform generic feature requests into detailed requirements
- `/mm:lite-prd-generator` — Convert rough MVP idea into demo-grade PRD

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

- [x] Integración con NotebookLM MCP (--use-mcp flag)
- [x] Iteration loop para aprobación condicional
- [ ] Comando `mastermind brief` - Crear brief interactivo
- [ ] Comando `mastermind config` - Configuración del framework
- [ ] Export en otros formatos (JSON, PDF)
- [ ] Completar sources faltantes (17/100)
