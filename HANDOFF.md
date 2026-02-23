# MasterMind Framework - Handoff / Continue Session

> Última actualización: 2025-02-22
> PRPs completados: PRP-000 ✅, PRP-001 ✅

---

## Quick Start (Para continuar sesión)

```bash
# 1. Ir al proyecto
cd /home/rpadron/proy/mastermind

# 2. Verificar estado
git status
git log --oneline -3

# 3. Crear rama para siguiente PRP
git checkout -b feature/prp-002-yaml-versioning

# 4. Validar fuentes actuales
cd tools/mastermind-cli
uv run mastermind source validate --brain 01-product-strategy
```

---

## Estado Actual

### ✅ Completado

| PRP | Descripción | Commit |
|-----|-------------|--------|
| PRP-000 | Initial Setup & Project Structure | ac1696a |
| PRP-001 | mastermind-cli (11 comandos) | b050e22 |

### ⏳ Siguiente

| PRP | Descripción | Comando para empezar |
|-----|-------------|---------------------|
| PRP-002 | YAML Versioning en 10 fuentes | `git checkout -b feature/prp-002-yaml-versioning` |

---

## Comandos CLI Disponibles

```bash
# Desde tools/mastermind-cli/
uv run mastermind source list              # Listar todas las fuentes
uv run mastermind framework status        # Estado global del framework
uv run mastermind brain status 01-product-strategy  # Estado de un cerebro
uv run mastermind source validate --brain 01-product-strategy  # Validar
```

---

## Lo Que Necesita Arreglar (PRP-002)

### Fuentes con YAML faltante o incompleto:

| Fuente | Problema | Acción |
|--------|----------|--------|
| FUENTE-008 | Le falta YAML + secciones 3,4,5 | Agregar YAML front matter completo |
| FUENTE-009 | Sin YAML delimitadores | Agregar `---` delimitadores |
| FUENTE-010 | Sin YAML delimitadores | Agregar `---` delimitadores |

### Plantilla de YAML front matter:
```yaml
---
source_id: "FUENTE-XXX"
brain: "brain-software-01-product-strategy"
niche: "software-development"
title: "Título completo"
author: "Nombre del autor"
expert_id: "EXP-XXX"
type: "video"
language: "en"
year: YYYY
skills_covered: []
distillation_date: "2026-02-22"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
changelog: []
---
```

---

## Ubicaciones Clave

```
/home/rpadron/proy/mastermind/
├── docs/
│   ├── design/00-PRD-MasterMind-Framework.md  ← PRD principal
│   ├── design/10-Plan-Implementacion-Claude-Code.md  ← Plan
│   ├── CLI-REFERENCE.md  ← Guía del CLI
│   └── software-development/01-product-strategy-brain/sources/
│       ├── FUENTE-001 through FUENTE-010
├── tools/mastermind-cli/  ← CLI implementado
├── PRPs/  ← Todos los PRPs
└── CLAUDE.md  ← Reglas del proyecto
```

---

## Stack y Versiones

| Componente | Versión | Nota |
|------------|---------|------|
| Python | 3.12.3 | ⚠️ Proyecto requiere >=3.14 |
| uv | 0.9.28 | ✅ |
| Click | 8.3.1 | CLI framework |
| Rich | 14.3.3 | Terminal output |
| GitPython | 3.1.46 | Git operations |

---

## Git Rules

- **NUNCA** usar `--no-verify` (usuario lo prohibió)
- Esperar a que termine el hook GGA
- Conventional commits: `feat(scope): description`

---

## Problemas Conocidos

1. **Python 3.12 vs 3.14**: Funciona para dev, actualizar antes de producción
2. **3 fuentes con YAML inválido**: Resolver en PRP-002
3. **MCP servers**: Configurados pero no probados extensivamente

---

## Para Terminar Sesión

```bash
# 1. Commit si hay cambios
git add -A
git commit -m "feat: description"

# 2. Merge a master si está completo
git checkout master
git merge feature/prp-XXX

# 3. Crear checkpoint
/sc:save
```

---

## Comandos de Referencia Rápida

```bash
# Validar
uv run mastermind source validate --brain 01-product-strategy

# Listar fuentes
uv run mastermind source list

# Framework status
uv run mastermind framework status

# Tests
uv run pytest tests/ -v

# Git status
git status
git log --oneline -5
```

---

**Siguiente comando para continuar:**
```bash
git checkout -b feature/prp-002-yaml-versioning
```
