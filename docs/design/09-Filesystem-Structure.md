# Estructura del Filesystem — Lista para Implementar

Este documento define la estructura completa de carpetas y archivos del MasterMind Framework.

---

## Estructura Completa

```
mastermind-framework/
│
├── README.md                              ← Descripción general del framework
├── LICENSE                                ← Licencia (privada por ahora)
│
├── config/
│   ├── orchestrator.yaml                  ← Configuración del Orquestador Central
│   ├── evaluator.yaml                     ← Configuración del Evaluador Crítico
│   ├── mcp-servers.json                   ← Mapeo de servidores MCP
│   └── precedents.yaml                    ← Registro de precedentes (conflictos resueltos)
│
├── docs/
│   └── software-development/              ← Nicho: Desarrollo de Software
│       ├── index.md                       ← Índice del nicho, orden de cerebros, visión
│       │
│       ├── 01-product-strategy-brain/
│       │   ├── README.md
│       │   ├── brain-spec.yaml
│       │   ├── knowledge-map.md
│       │   ├── experts-directory.md
│       │   ├── master-sources.md
│       │   ├── sources/
│       │   │   ├── FUENTE-001-inspired-cagan.md
│       │   │   ├── FUENTE-002-continuous-discovery-torres.md
│       │   │   ├── FUENTE-003-escaping-build-trap-perri.md
│       │   │   ├── FUENTE-004-lean-startup-ries.md
│       │   │   ├── FUENTE-005-measure-what-matters-doerr.md
│       │   │   ├── FUENTE-006-thinking-in-systems-meadows.md
│       │   │   ├── FUENTE-007-empowered-cagan.md
│       │   │   ├── FUENTE-008-video-cagan-discovery.md
│       │   │   ├── FUENTE-009-video-torres-discovery.md
│       │   │   └── FUENTE-010-video-perri-build-trap.md
│       │   ├── use-cases.md
│       │   ├── evaluation-criteria.md
│       │   └── notebook-config.json
│       │
│       ├── 02-ux-research-brain/
│       │   ├── README.md
│       │   ├── brain-spec.yaml
│       │   ├── knowledge-map.md
│       │   ├── experts-directory.md
│       │   ├── master-sources.md
│       │   ├── sources/
│       │   ├── use-cases.md
│       │   ├── evaluation-criteria.md
│       │   └── notebook-config.json
│       │
│       ├── 03-ui-design-brain/
│       │   └── (misma estructura)
│       │
│       ├── 04-frontend-brain/
│       │   └── (misma estructura)
│       │
│       ├── 05-backend-brain/
│       │   └── (misma estructura)
│       │
│       ├── 06-qa-devops-brain/
│       │   └── (misma estructura)
│       │
│       └── 07-growth-data-brain/
│           └── (misma estructura)
│
├── agents/
│   ├── orchestrator/
│   │   ├── system-prompt.md               ← System prompt del Orquestador
│   │   └── flow-definitions.yaml          ← Flujos estándar (full_product, validation, etc.)
│   │
│   ├── evaluator/
│   │   ├── system-prompt.md               ← System prompt del Evaluador Crítico
│   │   └── evaluation-checklist.yaml      ← Checklist de evaluación
│   │
│   └── brains/
│       ├── product-strategy.md            ← System prompt Cerebro #1
│       ├── ux-research.md                 ← System prompt Cerebro #2
│       ├── ui-design.md                   ← System prompt Cerebro #3
│       ├── frontend.md                    ← System prompt Cerebro #4
│       ├── backend.md                     ← System prompt Cerebro #5
│       ├── qa-devops.md                   ← System prompt Cerebro #6
│       └── growth-data.md                 ← System prompt Cerebro #7
│
├── skills/
│   └── reusable/
│       ├── context-loader.md              ← Carga contexto de NotebookLM
│       ├── output-formatter.md            ← Formatea outputs en schema estándar
│       ├── quality-checker.md             ← Validación básica de completitud
│       ├── code-generator.md              ← Generación de código con estándares
│       ├── doc-writer.md                  ← Generación de documentación
│       └── research-synthesizer.md        ← Síntesis de investigación
│
├── templates/
│   └── brain-template/                    ← Plantilla vacía para crear nuevos cerebros
│       ├── README.md
│       ├── brain-spec.yaml
│       ├── knowledge-map.md
│       ├── experts-directory.md
│       ├── master-sources.md
│       ├── sources/
│       │   └── FUENTE-000-plantilla.md
│       ├── use-cases.md
│       ├── evaluation-criteria.md
│       └── notebook-config.json
│
├── logs/
│   ├── evaluations/                       ← Logs de evaluación del Cerebro #7
│   └── precedents/                        ← Historial de conflictos resueltos
│
└── projects/
    └── (carpeta por proyecto ejecutado)
        ├── brief.md
        ├── outputs/
        └── evaluation-report.md
```

---

## Comando para Crear la Estructura

```bash
#!/bin/bash
# Crear estructura del MasterMind Framework

BASE="mastermind-framework"

# Raíz
mkdir -p $BASE/{config,logs/{evaluations,precedents},projects}

# Templates
mkdir -p $BASE/templates/brain-template/sources

# Skills
mkdir -p $BASE/skills/reusable

# Agents
mkdir -p $BASE/agents/{orchestrator,evaluator,brains}

# Docs - Nicho Software Development
NICHO="$BASE/docs/software-development"
for brain in 01-product-strategy-brain 02-ux-research-brain 03-ui-design-brain 04-frontend-brain 05-backend-brain 06-qa-devops-brain 07-growth-data-brain; do
  mkdir -p "$NICHO/$brain/sources"
done

echo "Estructura creada exitosamente en ./$BASE"
```

---

## Convenciones de Nombres

| Tipo | Convención | Ejemplo |
|------|-----------|---------|
| Carpetas de nicho | kebab-case | `software-development` |
| Carpetas de cerebro | `{##}-{nombre}-brain` | `01-product-strategy-brain` |
| Archivos de fuente | `FUENTE-{NNN}-{titulo-corto}.md` | `FUENTE-001-inspired-cagan.md` |
| System prompts | `{nombre}.md` | `product-strategy.md` |
| Configs | `.yaml` o `.json` | `orchestrator.yaml` |
| Logs | `{fecha}-{tipo}.yaml` | `2026-02-21-evaluation.yaml` |

---

## Notas de Implementación

1. **Git:** Inicializar como repositorio Git desde el día 1. Cada cambio significativo = commit.
2. **`.gitignore`:** Excluir `logs/` y `projects/` del repo (son datos operativos, no diseño).
3. **Backup de NotebookLM:** Los cuadernos no viven en Git. Se documentan en `notebook-config.json` y se respaldan manualmente como PDF + `master-sources.md`.
4. **Versionado:** Usar tags de Git para marcar versiones del framework (v0.1, v0.2, etc.).
