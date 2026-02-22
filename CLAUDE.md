# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Mente Maestra** (MasterMind Framework) es una arquitectura cognitiva modular para crear cerebros especializados alimentados con conocimiento destilado de expertos mundiales.

**Nicho inicial:** Software Development
**Arquitectura:** 7 cerebros especializados + Orquestador Central + Evaluador Crítico
**Stack Tecnológico:** Python 3.14 (uv), Node.js (nvm), Claude Code, MCP (NotebookLM, Context7)

### Los 7 Cerebros (Flujo de Desarrollo)

| # | Cerebro | Rol | Expertos |
|---|---------|-----|----------|
| 1 | Product Strategy | Define QUÉ y POR QUÉ | Cagan, Torres, Perri, Ries, Doerr, Meadows |
| 2 | UX Research | Define la EXPERIENCIA | (pendiente) |
| 3 | UI Design | Define lo VISUAL | (pendiente) |
| 4 | Frontend | CONSTRUYE la interfaz | (pendiente) |
| 5 | Backend | CONSTRUYE la lógica | (pendiente) |
| 6 | QA/DevOps | GARANTIZA estabilidad | (pendiente) |
| 7 | Growth/Data | EVOLUCIONA todo (meta-cerebro en tiempo real) | (pendiente) |

## Development Commands

```bash
# Python runtime (uv)
uv run python main.py           # Ejecutar el script principal
uv sync                          # Sincronizar dependencias
uv add <package>                 # Agregar dependencia

# Git (versionamiento semántico)
git tag v0.1.0 -m "descripción"  # Marcar versión del framework
```

## Architecture

### Flujo de Ejecución Estándar

```
Brief del Usuario
    ↓
Orquestador (clasifica y asigna cerebro(s))
    ↓
Cerebro(s) consulta NotebookLM vía MCP
    ↓
Cerebro #7 evalúa cada output en TIEMPO REAL
    ↓
Si aprobado → siguiente cerebro o entrega
Si rechazado → iteración (máx 3) → escalar a humano
```

### Las 5 Capas de Cada Cerebro

1. **Base Conceptual:** Principios fundamentales (el "por qué")
2. **Frameworks Operativos:** Métodos y herramientas (el "cómo")
3. **Modelos Mentales:** Lente de análisis del mundo
4. **Criterios de Decisión:** Trade-offs profesionales (lo que separa experto de asistente)
5. **Mecanismo de Retroalimentación:** Medición y mejora continua

### Protocolo de Comunicación entre Cerebros

Todo intercambio usa formato YAML estándar con:
- `from`, `to`, `type` (output/request/rejection/approval)
- `task_id`, `version`, `content` (summary, detail, assumptions, dependencies, confidence)

## Project Structure

```
docs/
├── PRD/                           # Documentos de diseño (00-09)
│   ├── 00-PRD-MasterMind-Framework.md      ← PRD principal (leer primero)
│   ├── 01-Plantilla-Cerebro.md
│   ├── 02-Metodo-Seleccion-Expertos.md
│   ├── 03-Proceso-Destilacion-Fuentes.md
│   ├── 04-Plantilla-Ficha-Fuente-Maestra.md
│   ├── 05-Cerebro-01-Product-Strategy.md
│   ├── 06-Cerebros-02-a-07-Specs.md
│   ├── 07-Orquestador-y-Evaluador.md
│   ├── 08-Casos-de-Uso-e-Historias.md
│   ├── 09-Filesystem-Structure.md
│   └── 10-Plan-Implementacion-Claude-Code.md
│
└── software-development/          # Nicho: Desarrollo de Software
    └── sources/                   # Fuentes maestras del Cerebro #1
        ├── FUENTE-001-inspired-cagan.md
        ├── FUENTE-002-continuous-discovery-torres.md
        └── ... (10 fuentes)

.claude/
└── commands/                     # Slash commands de Claude Code
    ├── explore-first.md
    ├── improve-prompt.md
    ├── lite-prd-generator.md
    └── prd-clarifier.md
```

## Source Files Format (Fichas de Fuentes Maestras)

Cada fuente usa YAML front matter + Markdown:

```yaml
---
source_id: "FUENTE-001"
brain: "brain-software-01-product-strategy"
title: "Inspired: How to Create Tech Products Customers Love"
author: "Marty Cagan"
expert_id: "EXP-001"
type: "book"
isbn: "978-1119387503"
skills_covered: ["H1", "H3", "H5", "H7"]
distillation_quality: "complete"
loaded_in_notebook: false
---

# Contenido destilado en secciones:
## 1. Principios Fundamentales
## 2. Frameworks y Metodologías
## 3. Modelos Mentales
## 4. Criterios de Decisión
## 5. Anti-patrones
```

## Implementation Phases (Plan)

| Fase | Descripción | Estado |
|------|-------------|--------|
| 0 | Verificación del entorno | Pendiente |
| 1 | Estructura del proyecto (carpetas) | Pendiente |
| 2 | mastermind-cli (gestión de fuentes) | Pendiente |
| 3 | YAML versionado en fichas existentes | Pendiente |
| 4 | System prompts de agentes | Pendiente |
| 5 | Flujo de carga NotebookLM | Pendiente |
| 6 | PRP del Cerebro #1 | Pendiente |

## Key Design Decisions

**Por qué NotebookLM (no RAG propio desde el inicio):**
- Ya funciona en WSL vía MCP
- Cero configuración de embeddings/chunking
- Permite generar audios, videos, infografías
- Suficiente para Fase 1 con pocos cerebros
- **Ruta de migración:** Fichas portables (Markdown + YAML) → RAG propio futuro (ChromaDB/Qdrant + LangChain)

**Por qué 7 cerebros y no 1 mega-cerebro:**
- Especialización permite conocimiento profundo por dominio
- Cada cerebro puede cuestionar outputs de otros (checks & balances)
- Cerebro #7 como meta-evaluador previene auto-engaño del sistema
- Escalabilidad: agregar nichos = nuevos conjuntos de 7 cerebros

**Por qué YAML front matter en las fuentes:**
- Parseable por CLI futuro para validación automática
- Portable entre NotebookLM (hoy) y RAG propio (futuro)
- Versionado semántico con changelog automático
- Metadata filtering para consultas multi-cerebro

## Documentation Priority Order

Cuando trabajes en este proyecto, lee en este orden:
1. `docs/PRD/00-PRD-MasterMind-Framework.md` - Arquitectura completa
2. `docs/PRD/10-Plan-Implementacion-Claude-Code.md` - Fases de implementación
3. `docs/PRD/09-Filesystem-Structure.md` - Estructura de carpetas
4. Cerebro específico en `docs/PRD/05-*.md` o `06-*.md`

## Language

Todo el contenido y documentación está en **español**. El código y comandos usan inglés (convención estándar).
