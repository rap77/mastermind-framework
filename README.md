# MasterMind Framework

[![Version](https://img.shields.io/badge/version-0.1.0-blue)](https://github.com/rap77/mastermind-framework)
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

| # | Cerebro | Rol | Expertos |
|---|---------|-----|----------|
| 1 | Product Strategy | Define QUÉ y POR QUÉ | Cagan, Torres, Perri, Ries, Doerr, Meadows |
| 2 | UX Research | Define la EXPERIENCIA | TBD |
| 3 | UI Design | Define lo VISUAL | TBD |
| 4 | Frontend | CONSTRUYE la interfaz | TBD |
| 5 | Backend | CONSTRUYE la lógica | TBD |
| 6 | QA/DevOps | GARANTIZA estabilidad | TBD |
| 7 | Growth/Data | EVOLUCIONA todo (meta-cerebro) | TBD |

## Quick Start

### Prerequisitos

```bash
# Python 3.14+ (advertencia: actualmente el proyecto usa 3.12 en entorno de desarrollo)
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

# Verificar instalación
uv run python -c "import mastermind_cli; print('OK')"
```

### Uso Básico

```bash
# CLI (futuro - PRP-001)
mastermind init my-project
mastermind ask --brain product-strategy "¿Deberíamos construir X?"

# Consulta directa vía Claude Code
# Los cerebros se cargan como skills de Claude Code
```

## Estructura del Proyecto

```
mastermind-framework/
├── docs/
│   └── software-development/          # Nicho inicial
│       ├── 01-product-strategy-brain/ # ← Primer cerebro implementado
│       ├── 02-ux-research-brain/
│       └── ...
├── agents/                            # System prompts
│   ├── orchestrator/
│   ├── evaluator/
│   └── brains/
├── skills/reusable/                   # Skills compartidas
├── templates/brain-template/          # Para crear nuevos cerebros
├── config/                            # Configuraciones
├── logs/                              # No en Git (operativo)
└── projects/                          # No en Git (operativo)
```

## Documentación

- [PRD Principal](docs/design/00-PRD-MasterMind-Framework.md)
- [Filesystem Structure](docs/design/09-Filesystem-Structure.md)
- [Plan de Implementación](docs/design/10-Plan-Implementacion-Claude-Code.md)
- [Cerebro #1: Product Strategy](docs/design/05-Cerebro-01-Product-Strategy.md)

## Roadmap

| Fase | PRP | Descripción | Estado |
|------|-----|-------------|--------|
| 0 | PRP-000 | Initial Setup & Project Structure | ✅ En progreso |
| 1 | PRP-001 | mastermind-cli Implementation | ⏳ Pendiente |
| 2 | PRP-002 | YAML Versioning en Fichas | ⏳ Pending |
| 3 | PRP-003 | System Prompts de Agentes | ⏳ Pending |
| 4 | PRP-004 | NotebookLM Integration | ⏳ Pending |
| 5 | PRP-005 | PRP del Cerebro #1 | ⏳ Pending |

## License

Copyright © 2026 MasterMind Framework. All rights reserved.

## Contributing

Este proyecto es actualmente **privado y cerrado**. No se aceptan contribuciones externas.

---

**Versión:** 0.1.0 | **Estado:** Alpha
