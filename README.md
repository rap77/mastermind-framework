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

### Prerequisitos

```bash
# Python 3.14+
python3 --version

# UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Node.js (para MCP servers)
nvm install 22
```

### Instalación

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

## Documentación

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

## License

Copyright © 2026 MasterMind Framework. All rights reserved.

---

**Versión:** 1.0.0 | **Estado:** Production Ready
