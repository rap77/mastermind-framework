# PRP-004: NotebookLM Integration

**Status:** Ready to Implement (after PRP-003)
**Priority:** High
**Estimated Time:** 1-1.5 hours
**Dependencies:** PRP-002 (fuentes con YAML), PRP-003 (system prompts)

---

## Executive Summary

Configurar NotebookLM para el Cerebro #1, crear el proceso de carga de fuentes, y verificar que el cerebro pueda responder correctamente a consultas. Esta fase completa el MVP del Cerebro #1.

---

## Context from Clarification Session

### Decisiones Críticas

1. **NotebookLM MCP:** Está configurado en otro proyecto - validar que funcione en este
2. **Nombre del cuaderno:** `[CEREBRO] Product Strategy - Software Development`
3. **Carga:** Híbrida - export manual (drag&drop) + opción auto-load vía MCP
4. **Verificación:** 3 consultas de prueba para validar la carga

### Estado NotebookLM

- Cuenta: Activa
- MCP tool: `notebooklm-mcp` disponible en otro proyecto
- Requiere validación en este proyecto

---

## External Resources

### NotebookLM Documentation
- https://notebooklm.google.com/ - NotebookLM main site
- https://support.google.com/notebooklm?hl=en - Official help

### NotebookLM MCP
- https://github.com/modelcontextprotocol/servers - MCP servers repository
- https://github.com/Anthropics/notebooklm-mcp - NotebookLM MCP server (si existe)

---

## Implementation Blueprint

### Pseudocode - Proceso de Carga

```python
# tools/notebooklm_setup.py
import subprocess
from pathlib import Path

def setup_notebooklm():
    # 1. Crear directorio de export
    Path("dist/notebooklm/01-product-strategy").mkdir(parents=True, exist_ok=True)

    # 2. Exportar fuentes sin YAML
    sources = glob("docs/software-development/01-product-strategy-brain/sources/*.md")
    for source in sources:
        metadata, content = read_yaml_frontmatter(source)
        output_path = f"dist/notebooklm/01-product-strategy/{Path(source).name}"
        write_file(output_path, content)  # Solo contenido, sin YAML

    # 3. Crear notebook-config.json
    config = {
        "notebook_name": "[CEREBRO] Product Strategy - Software Development",
        "brain_id": "01-product-strategy",
        "sources_count": 10,
        "sources_loaded": [],
        "last_sync": None,
        "verification_status": "pending",
        "test_queries": [
            "¿Cuáles son los 4 riesgos de product discovery según Marty Cagan?",
            "¿Qué es el Opportunity Solution Tree de Teresa Torres?",
            "¿Cuándo debería pivotar vs perseverar según Eric Ries?"
        ]
    }
    write_json("docs/software-development/01-product-strategy-brain/notebook-config.json", config)

def verify_with_mcp():
    # Si notebooklm-mcp está disponible:
    # 1. Crear notebook vía MCP
    # 2. Subir fuentes automáticamente
    # 3. Ejecutar consultas de prueba
    pass

def manual_verification_guide():
    print("""
    Manual Verification Steps:
    1. Go to https://notebooklm.google.com/
    2. Create notebook: [CEREBRO] Product Strategy - Software Development
    3. Upload all files from dist/notebooklm/01-product-strategy/
    4. Run test queries (see notebook-config.json)
    5. Update notebook-config.json with notebook_id and verification status
    """)
```

---

## Tasks (in Order)

### Task 1: Validar MCP Servers (10 min)
- [ ] Verificar ubicación de MCP servers en otros proyectos
- [ ] Validar que `notebooklm-mcp` funcione
- [ ] Si no funciona, documentar para configuración manual
- [ ] Output: `logs/mcp-validation.md`

### Task 2: Crear Directorio de Export (5 min)
- [ ] Crear `dist/notebooklm/01-product-strategy/`
- [ ] Actualizar .gitignore para excluir dist/

### Task 3: Exportar Fuentes sin YAML (15 min)
- [ ] Usar `mastermind source export --brain 01-product-strategy --format notebooklm`
- [ ] Verificar que archivos no tengan YAML front matter
- [ ] Verificar que contenido Markdown esté intacto
- [ ] Output: 10 archivos en `dist/notebooklm/01-product-strategy/`

### Task 4: Crear notebook-config.json (10 min)
- [ ] Crear config con metadatos del notebook
- [ ] Incluir consultas de prueba
- [ ] Guardar en `docs/software-development/01-product-strategy-brain/`

### Task 5: NotebookLM Setup (20 min)
- [ ] Ir a https://notebooklm.google.com/
- [ ] Crear notebook: `[CEREBRO] Product Strategy - Software Development`
- [ ] Subir 10 archivos desde `dist/notebooklm/01-product-strategy/`
- [ ] Esperar a que NotebookLM procese las fuentes
- [ ] Anotar notebook_id en config

### Task 6: Verificación con Consultas (15 min)
- [ ] Ejecutar consulta 1: "¿Cuáles son los 4 riesgos de product discovery según Cagan?"
- [ ] Ejecutar consulta 2: "¿Qué es el Opportunity Solution Tree?"
- [ ] Ejecutar consulta 3: "¿Cuándo pivotar vs perseverar?"
- [ ] Verificar que respuestas sean correctas
- [ ] Documentar respuestas en `logs/notebooklm-verification.md`

### Task 7: Documentación y Git (10 min)
- [ ] Actualizar `notebook-config.json` con status "verified"
- [ ] Crear `docs/NOTEBOOKLM-GUIDE.md` con proceso de carga
- [ ] Git commit: `feat(notebooklm): integrate Cerebro #1 with NotebookLM`

### Task 8: Test End-to-End (10 min)
- [ ] Crear brief de prueba
- [ ] Simular consulta al cerebro usando NotebookLM
- [ ] Verificar que output use la información de las fuentes
- [ ] Documentar resultado

---

## notebook-config.json Structure

```json
{
  "notebook_name": "[CEREBRO] Product Strategy - Software Development",
  "notebook_id": "NB-ID-FROM-URL",
  "brain_id": "01-product-strategy",
  "version": "1.0.0",
  "created_at": "2026-02-22",
  "sources": [
    {
      "source_id": "FUENTE-001",
      "title": "Inspired: How to Create Tech Products Customers Love",
      "author": "Marty Cagan",
      "filename": "FUENTE-001-inspired-cagan.md",
      "loaded": true,
      "notebook_source_id": "SOURCE-ID-FROM-NOTEBOOKLM"
    }
  ],
  "sources_count": 10,
  "sources_loaded": 10,
  "last_sync": "2026-02-22T10:00:00Z",
  "verification_status": "verified",
  "test_queries": [
    {
      "query": "¿Cuáles son los 4 riesgos de product discovery según Marty Cagan?",
      "expected_answer": "Value, Usability, Feasibility, Viability",
      "actual_answer": "",
      "passed": false
    }
  ]
}
```

---

## Consultas de Verificación

### Query 1: 4 Riesgos de Discovery (Cagan)

**Pregunta:** "¿Cuáles son los 4 riesgos de product discovery según Marty Cagan?"

**Respuesta esperada:**
Los 4 riesgos son:
1. **Value risk** - ¿Alguien realmente va a comprar esto?
2. **Usability risk** - ¿El usuario puede figured out cómo usarlo?
3. **Feasibility risk** - ¿Podemos construirlo con las habilidades/tecnología que tenemos?
4. **Viability risk** - ¿Este producto funciona para nuestro negocio?

**Criterio de aprobación:** Menciona los 4 riesgos por nombre.

---

### Query 2: Opportunity Solution Tree (Torres)

**Pregunta:** "¿Qué es el Opportunity Solution Tree de Teresa Torres?"

**Respuesta esperada:**
El Opportunity Solution Tree es un método de continuous discovery que conecta:
- **Outcomes** (resultados deseados)
  → **Opportunities** (oportunidades de mejora)
    → **Solutions** (soluciones para aprovechar oportunidades)
      → **Experiments** (tests para validar soluciones)

**Criterio de aprobación:** Describe la estructura jerárquica del árbol.

---

### Query 3: Pivotar vs Perseverar (Ries)

**Pregunta:** "¿Cuándo debería pivotar vs perseverar según Eric Ries?"

**Respuesta esperada:**
Según el Build-Measure-Learn cycle:
- **Perseverar** si las métricas muestran progreso hacia Product-Market Fit
- **Pivotar** si los datos demuestran que las hipótesis centrales son falsas
- La decisión se basa en datos, no en opiniones

**Criterio de aprobación:** Menciona que la decisión se basa en datos del ciclo Build-Measure-Learn.

---

## Validation Gates

```bash
# 1. Verificar export
ls -la dist/notebooklm/01-product-strategy/
# Debe haber 10 archivos .md sin YAML front matter

# 2. Verificar que YAML fue removido
head -5 dist/notebooklm/01-product-strategy/FUENTE-001-*.md
# NO debe empezar con ---

# 3. Verificar notebook-config.json
cat docs/software-development/01-product-strategy-brain/notebook-config.json
python3 -c "import json; json.load(open('...'))"

# 4. Verificar documento de guía
ls docs/NOTEBOOKLM-GUIDE.md

# 5. Verificación manual (requiere navegador)
# Ir a NotebookLM y ejecutar consultas de prueba
```

---

## Definition of Done

- [ ] MCP servers validados (o documentación de configuración manual)
- [ ] 10 fuentes exportadas sin YAML front matter
- [ ] `notebook-config.json` creado con metadata completa
- [ ] Notebook creado en NotebookLM con nombre correcto
- [ ] Fuentes cargadas en NotebookLM
- [ ] 3 consultas de prueba ejecutadas y pasan
- [ ] `notebook-config.json` actualizado con notebook_id y status "verified"
- [ ] `docs/NOTEBOOKLM-GUIDE.md` creado
- [ ] Test end-to-end documentado
- [ ] Git commit con cambios

---

## Error Handling Strategy

| Error | Acción |
|-------|--------|
| MCP no funciona | Usar proceso manual con documentación |
| NotebookLM no procesa fuente | Revisar formato del archivo (UTF-8, sin caracteres especiales) |
| Respuesta incorrecta | Verificar que la fuente se cargó correctamente, re-exportar si necesario |
| Notebook ID no disponible | Dejar en blanco hasta que se cree el notebook |

---

## Gotchas & Notes

1. **YAML en NotebookLM:** NotebookLM no procesa bien YAML front matter. Por eso exportamos solo el contenido Markdown.

2. **Codificación de caracteres:** Asegurarse de que los archivos estén en UTF-8. Los acentos en español pueden causar problemas.

3. **Nombre del notebook:** Usar el prefijo `[CEREBRO]` para distinguir los cuadernos de MasterMind de otros usos de NotebookLM.

4. **Procesamiento de NotebookLM:** Puede tomar varios minutos después de subir las fuentes. Esperar a que el indicador de "processing" desaparezca.

5. **Actualización de fuentes:** Cuando una fuente se actualiza, hay que:
   - Eliminar la fuente vieja del notebook
   - Subir la nueva
   - Verificar con consultas de prueba

6. **Backup de notebooks:** NotebookLM no tiene API de backup. Considerar exportar a PDF periódicamente.

---

## Files Created

| Archivo | Propósito |
|---------|-----------|
| `dist/notebooklm/01-product-strategy/*.md` | Fuentes limpias para carga |
| `docs/software-development/01-product-strategy-brain/notebook-config.json` | Config del notebook |
| `docs/NOTEBOOKLM-GUIDE.md` | Guía de proceso de carga |
| `logs/mcp-validation.md` | Validación de MCP servers |
| `logs/notebooklm-verification.md` | Resultados de consultas de prueba |

---

## NOTEBOOKLM-GUIDE.md Content

```markdown
# NotebookLM Integration Guide

## Overview
This guide explains how to integrate MasterMind brains with Google NotebookLM.

## Process for Cerebro #1 (Product Strategy)

### Step 1: Export Sources
```bash
mastermind source export --brain 01-product-strategy --format notebooklm
```

This creates clean Markdown files in `dist/notebooklm/01-product-strategy/`.

### Step 2: Create Notebook
1. Go to https://notebooklm.google.com/
2. Click "New notebook"
3. Name it: `[CEREBRO] Product Strategy - Software Development`

### Step 3: Upload Sources
1. Click "Add sources"
2. Upload all 10 files from `dist/notebooklm/01-product-strategy/`
3. Wait for processing (may take several minutes)

### Step 4: Verify
Run these test queries:
1. "¿Cuáles son los 4 riesgos de product discovery según Marty Cagan?"
2. "¿Qué es el Opportunity Solution Tree de Teresa Torres?"
3. "¿Cuándo debería pivotar vs perseverar según Eric Ries?"

Expected answers are in `notebook-config.json`.

### Step 5: Update Config
Update `notebook-config.json` with:
- `notebook_id`: From the notebook URL
- `verification_status`: "verified"
- Test query results

## Updating Sources
When a source is updated:
1. Re-export: `mastermind source export --brain 01 --only FUENTE-NNN`
2. In NotebookLM: Remove old source, upload new one
3. Verify with a test query
4. Update `last_sync` in config

## Troubleshooting
- **Source not loading:** Check file is UTF-8 encoded
- **Wrong answers:** Verify source uploaded correctly, re-export if needed
- **MCP errors:** See `logs/mcp-validation.md`
```

---

## Next Steps

After this PRP:
- **MVP del Cerebro #1 completo** ✅
- Testing con briefs reales
- Implementación de Cerebro #2 (UX Research)

---

## Confidence Score

**8/10** - Alta confianza de éxito.

**Rationale:** El proceso está bien definido. El riesgo principal depende de MCP servers que pueden requerir configuración adicional. El proceso manual es un fallback sólido.

---

## Context for AI Agent

**Archivos clave para leer antes de implementar:**
1. `/home/rpadron/proy/mastermind/docs/design/10-Plan-Implementacion-Claude-Code.md` - Sección Fase 5
2. `/home/rpadron/proy/mastermind/PRPs/PRP-001-mastermind-cli.md` - Comando `source export`
3. `/home/rpadron/proy/mastermind/docs/software-development/01-product-strategy-brain/notebook-config.json` - Config a crear

**Comando para iniciar:**
```bash
cd /home/rpadron/proy/mastermind
# Exportar fuentes
mastermind source export --brain 01-product-strategy --format notebooklm
# Verificar export
ls dist/notebooklm/01-product-strategy/
# Ir a NotebookLM en navegador para crear notebook y cargar fuentes
```

**Resultado esperado:**
NotebookLM configurado con 10 fuentes del Cerebro #1, 3 consultas de prueba pasan, config actualizado, guía creada.
