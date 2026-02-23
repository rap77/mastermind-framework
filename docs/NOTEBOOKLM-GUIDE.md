# NotebookLM Integration Guide

Guía para integrar cerebros de MasterMind con Google NotebookLM.

---

## Overview

NotebookLM permite cargar documentos y consultarlos con IA. Esta guía explica cómo preparar las fuentes destiladas de los cerebros de MasterMind para cargarlas en NotebookLM.

---

## Process for Cerebro #1 (Product Strategy)

### Step 1: Export Sources

Exporta las fuentes sin YAML front matter (NotebookLM procesa mejor contenido limpio):

```bash
# Usar el script de exportación
python3 tools/export_sources_notebooklm.py

# O usar el CLI
mastermind source export --brain 01-product-strategy --format notebooklm
```

Esto crea archivos limpios en `dist/notebooklm/01-product-strategy/`.

**Verificación:**
```bash
ls -la dist/notebooklm/01-product-strategy/
# Debe haber 10 archivos .md

# Verificar que YAML fue removido
head -5 dist/notebooklm/01-product-strategy/FUENTE-001-*.md
# NO debe empezar con ---
```

---

### Step 2: Create Notebook

1. Ir a https://notebooklm.google.com/
2. Click "New notebook"
3. Nombre: `[CEREBRO] Product Strategy - Software Development`
4. Opcional: Agregar descripción

---

### Step 3: Upload Sources

1. Click "Add sources" → "Upload from computer"
2. Seleccionar todos los archivos de `dist/notebooklm/01-product-strategy/`
3. Esperar a que NotebookLM procese (puede tomar varios minutos)
4. Verificar que las 10 fuentes aparezcan en el panel lateral

**Tip:** Si una fuente no carga, verificar:
- Archivo esté en UTF-8
- No tenga caracteres especiales raros
- Tamaño < 50MB

---

### Step 4: Verify with Test Queries

Ejecuta estas consultas de prueba:

#### Query 1: 4 Riesgos de Discovery (Cagan)
```
¿Cuáles son los 4 riesgos de product discovery según Marty Cagan?
```
**Expected:** Value, Usability, Feasibility, Viability

#### Query 2: Opportunity Solution Tree (Torres)
```
¿Qué es el Opportunity Solution Tree de Teresa Torres?
```
**Expected:** Outcomes → Opportunities → Solutions → Experiments

#### Query 3: Pivotar vs Perseverar (Ries)
```
¿Cuándo debería pivotar vs perseverar según Eric Ries?
```
**Expected:** Decision based on Build-Measure-Learn data, not opinions

---

### Step 5: Update Config

Actualiza `docs/software-development/01-product-strategy-brain/notebook-config.json`:

```json
{
  "notebook_id": "ID-FROM-URL",
  "verification_status": "verified",
  "sources_loaded": 10,
  "last_sync": "2026-02-22T10:00:00Z"
}
```

**Cómo obtener notebook_id:**
- URL del notebook: `https://notebooklm.google.com/notebook/{NOTEBOOK_ID}/...`
- Copia el ID de la URL

---

## Updating Sources

Cuando una fuente se actualiza:

1. **Re-exportar:**
   ```bash
   python3 tools/export_sources_notebooklm.py
   ```

2. **En NotebookLM:**
   - Eliminar la fuente vieja del notebook
   - Subir la nueva versión

3. **Verificar:**
   - Ejecutar una consulta de prueba relacionada
   - Verificar que la respuesta use la información actualizada

4. **Update config:**
   - Actualizar `last_sync` en notebook-config.json

---

## Troubleshooting

| Problema | Solución |
|----------|----------|
| Fuente no carga | Verificar UTF-8 encoding, reducir tamaño |
| Respuestas incorrectas | Verificar que la fuente se cargó correctamente, re-exportar |
| NotebookLM no responde | Esperar a que termine de procesar (indicador de carga) |
| Caracteres raros | Verificar encoding, usar UTF-8 sin BOM |
| MCP errors | Ver `logs/mcp-validation.md` para documentación |

---

## Export Directory Structure

```
dist/notebooklm/
└── 01-product-strategy/
    ├── FUENTE-001-inspired-cagan.md
    ├── FUENTE-002-continuous-discovery-torres.md
    ├── FUENTE-003-escaping-build-trap-perri.md
    ├── FUENTE-004-lean-startup-ries.md
    ├── FUENTE-005-measure-what-matters-doerr.md
    ├── FUENTE-006-thinking-in-systems-meadows.md
    ├── FUENTE-007-empowered-cagan.md
    ├── FUENTE-008-video-cagan-discovery.md
    ├── FUENTE-009-video-torres-discovery.md
    └── FUENTE-010-video-perri-build-trap.md
```

---

## NotebookLM Tips

1. **Procesamiento:** Puede tomar 5-10 minutos procesar 10 fuentes
2. **Consultas específicas:** Mejor respuestas con preguntas específicas
3. **Citas:** NotebookLM incluye citas a las fuentes - verificarlas
4. **Idioma:** Funciona bien en español e inglés
5. **Límites:** 50 fuentes por notebook, 500k palabras por fuente

---

## Future Brains

El mismo proceso aplica para los demás cerebros:
- Brain #2: UX Research
- Brain #3: UI Design
- Brain #4: Frontend
- Brain #5: Backend
- Brain #6: QA/DevOps
- Brain #7: Growth & Data

Cada uno tendrá su propio notebook en NotebookLM.
