# MasterMind Framework

[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://github.com/rap77/mastermind-framework)
[![Python](https://img.shields.io/badge/python-3.14+-blue)](https://python.org)

> **Arquitectura Cognitiva Modular para Cerebros Especializados**

MasterMind es una arquitectura para crear "cerebros" especializados alimentados con conocimiento destilado de expertos mundiales. Cada cerebro domina un dominio específico y colabora con otros mediante un orquestador central y un evaluador crítico.

## Arquitectura

```
Brief del Usuario
    ↓
Orquestador Central (clasifica y asigna)
    ↓
Cerebro(s) Especializado(s) + NotebookLM (MCP)
    ↓
Cerebro #7 (Evaluador Crítico - meta-cerebro)
    ↓
Aprobado → Entrega | Rechazado → Iteración
```

### Los 7 Cerebros (Nicho: Software Development)

| # | Cerebro | Rol | Expertos Clave |
|---|---------|-----|----------------|
| 1 | Product Strategy | Define QUÉ y POR QUÉ | Cagan, Torres, Perri, Ries, Doerr |
| 2 | UX Research | Define la EXPERIENCIA | Norman, Nielsen, Krug, Young, Hall |
| 3 | UI Design | Define lo VISUAL | Frost, Wathan, Wroblewski, Lupton |
| 4 | Frontend | CONSTRUYE la interfaz | Simpson, Comeau, Osmani, Dodds |
| 5 | Backend | CONSTRUYE la lógica | Jin, Martin, Kleppmann, Xu, Fowler |
| 6 | QA/DevOps | GARANTIZA estabilidad | Kim, Forsgren, Humble, Majors, Crispin |
| 7 | Growth/Data | EVOLUCIONA todo | Munger, Kahneman, Tetlock, Hormozi |

## Quick Start

### Instalación Universal (Recomendado)

**¡No necesitas Python instalado!** El instalador lo hace todo por vos.

#### Linux / macOS

```bash
curl -fsSL https://raw.githubusercontent.com/rap77/mastermind-framework/master/install.sh | bash
```

#### Windows (PowerShell)

```powershell
irm https://raw.githubusercontent.com/rap77/mastermind-framework/master/install.ps1 | iex
```

**Lo que hace el instalador:**
1. ✅ Verifica dependencias (git, curl)
2. ✅ Instala uv (package manager)
3. ✅ Descarga Python 3.14 automáticamente
4. ✅ Clona el repositorio
5. ✅ Instala MasterMind globalmente
6. ✅ Configura PATH para usar `mm` y `mastermind` desde cualquier lugar

---

### Instalación Manual (si ya tenés Python 3.14+)

```bash
# Clonar repositorio
git clone https://github.com/rap77/mastermind-framework.git
cd mastermind-framework

# Instalar dependencias
uv sync

# Instalar CLI globalmente
uv pip install -e .

# Verificar instalación
mastermind info
```

---

### Instalación en Otro Proyecto

```bash
# En cualquier proyecto existente
cd /path/to/your-project

# Inicializar MasterMind
mastermind install init

# El framework crea .mastermind/ con config local
```

## CLI Reference

```bash
# === Gestión de Fuentes de Conocimiento ===
mastermind source new              # Crear nueva fuente
mastermind source list             # Listar todas las fuentes
mastermind source validate         # Validar formato YAML
mastermind source export           # Exportar fuentes a NotebookLM

# === Estado de Cerebros ===
mastermind brain status            # Estado de todos los cerebros
mastermind brain status <id>       # Estado de cerebro específico
mastermind brain validate          # Validar system prompts
mastermind brain package           # Empaquetar cerebro para distribución

# === Orquestación ===
mastermind orchestrate run "brief"           # Ejecutar flujo completo
mastermind orchestrate run --dry-run "brief" # Ver plan sin ejecutar
mastermind orchestrate run --flow validation_only "brief"
mastermind orchestrate run --use-mcp "brief" # Usar NotebookLM real

# === Memory & Learning ===
mastermind eval list [--limit N]         # Listar evaluaciones recientes
mastermind eval show <EVAL-ID>           # Mostrar detalle de evaluación
mastermind eval find <project>           # Buscar por proyecto
mastermind eval search <keyword>         # Búsqueda por keyword
mastermind eval stats                    # Estadísticas de evaluaciones

# === Framework ===
mastermind framework status         # Estado del framework
mastermind framework release        # Preparar release

# === Instalación ===
mastermind install init             # Inicializar en proyecto
mastermind install status           # Ver estado de instalación
mastermind install uninstall        # Desinstalar de proyecto

# === Info ===
mastermind info                     # Mostrar información del framework
```

### Ejemplos de Uso

```bash
# Validar idea de producto
mastermind orchestrate run --flow validation_only \
  "Quiero crear una app para encontrar compañeros de viaje"

# Ver plan de ejecución sin ejecutar
mastermind orchestrate run --dry-run \
  "Necesito rediseñar el onboarding de mi SaaS"

# Usar cerebros específicos
mastermind orchestrate run --flow design_sprint \
  "Diseñar UI para dashboard de analytics"
```

## Claude Code Slash Commands

El framework incluye **slash commands** para usar directamente desde Claude Code con el namespace `mm:`:

### Consulta de Cerebros

```bash
/mm:ask-product    # Consulta cerebro Producto (qué y por qué)
/mm:ask-ux         # Consulta cerebro UX Research
/mm:ask-design     # Consulta cerebro UI Design
/mm:ask-frontend   # Consulta cerebro Frontend
/mm:ask-backend    # Consulta cerebro Backend
/mm:ask-qa         # Consulta cerebro QA/DevOps
/mm:ask-growth     # Consulta cerebro Growth/Data
/mm:ask-all        # Consulta TODOS los cerebros como equipo
```

### Gestión de Proyectos

```bash
/mm:project-audit      # Análisis completo de 7 cerebros
/mm:audit              # Alias rápido de project-audit
```

### PRDs y Especificaciones

```bash
/mm:lite-prd-generator  # Convierte idea en PRD demo-grade
/mm:prd-clarifier       # Refina y clarifica PRD existente
/mm:generate-prp        # Crea PRP (Project Requirements Plan)
/mm:execute-prp         # Ejecuta PRP existente
```

### Mejora de Prompts

```bash
/mm:improve-prompt       # Transforma prompts genéricos en detallados
/mm:ux-spec-to-prompt    # Convierte specs UX en prompts de construcción
```

### Instalación en Proyectos Externos

```bash
# Copiar todos los comandos mm:
cp -r /path/to/mastermind/.claude /path/to/your-project/

# O solo los comandos:
cp -r /path/to/mastermind/.claude/commands/mm /path/to/your-project/.claude/commands/
```

**Ver documentación completa:** `.claude/README.md`

## Sistema de Memoria y Aprendizaje

El framework **recuerda todas las evaluaciones** del cerebro y permite aprender de experiencias pasadas.

```bash
# Ver evaluaciones guardadas
mastermind eval list

# Buscar evaluaciones de un proyecto específico
mastermind eval find prosell-sass

# Buscar por keyword
mastermind eval search "cold-start"

# Ver detalle de una evaluación
mastermind eval show EVAL-2026-03-07-001
```

### Lo que el Framework Aprende

- **Evaluaciones:** Cada vez que el cerebro #7 evalúa, se guarda automáticamente
- **Patrones:** El framework detecta patrones (ej: "Cold Start en 60% de B2C mobile apps")
- **Contexto:** Evaluaciones futuras usan contexto histórico para mejorar decisiones
- **Mejora Continua:** Los cerebros se vuelven más inteligentes con cada proyecto

### Arquitectura de Memoria

```
mastermind-memory/
├── evaluations/
│   ├── hot/       # Últimos 30 días (completo)
│   ├── warm/      # 30-90 días (resumido)
│   ├── cold/      # +90 días (solo patrones)
│   └── archive/   # +1 año (comprimido)
│
└── vector-db/    # Fase 4: Búsqueda semántica (futuro)
```

Para más detalles ver [PRP-009: Memory & Learning System](PRPs/PRP-009-memory-learning-system.md).

- [Stack Tecnológico Estándar](docs/STACK-TECNOLOGICO.md) ⭐
- [PRD Principal](docs/design/00-PRD-MasterMind-Framework.md)
- [Guía de Instalación](tools/mastermind-cli/INSTALL.md)
- [CLI Reference](docs/CLI-REFERENCE.md)
- [Orchestrator Guide](docs/ORCHESTRATOR-GUIDE.md)

## Development Status

| Componente | Estado |
|------------|--------|
| CLI v1.0.0 | ✅ Completo |
| 7 Cerebros | ✅ Activos (122 fuentes) |
| Orquestador | ✅ Funcional |
| Testing Suite | ✅ 5/5 tests passing |
| Installation | ✅ Funcional |
| **Memory System** | ✅ **Fase 1: Evaluation Logger** |

## Roadmap

| PRP | Descripción | Estado |
|-----|-------------|--------|
| PRP-000 | Initial Setup & Project Structure | ✅ Completo |
| PRP-001 | mastermind-cli Implementation | ✅ Completo |
| PRP-002 | YAML Versioning en Fichas | ✅ Completo |
| PRP-003 | System Prompts de Agentes | ✅ Completo |
| PRP-004 | NotebookLM Integration | ✅ Completo |
| PRP-005 | Brain #7 Evaluator | ✅ Completo |
| PRP-006 | Orchestrator Core | ✅ Completo |
| PRP-008 | Orchestrate Command | ✅ Completo |
| PRP-009 | Memory & Learning System | ✅ **Fase 1: Evaluation Logger** |

**Próximas Fases (PRP-009):**
- Fase 2: Retention Policy (hot/warm/cold)
- Fase 3: SQLite Migration
- Fase 4: Vector Database + RAG

## License

Copyright © 2026 MasterMind Framework. All rights reserved.

---

**Versión:** 1.0.0 | **Estado:** Production Ready
