# PRP-012: Brain #8 NotebookLM Setup

**Status:** Ready to Implement (after PRP-011)
**Priority:** Critical (enables brain #8 functionality)
**Estimated Time:** 5 hours
**Dependencies:** PRP-011
**Branch:** `feature/prp-012-brain-08-notebooklm-setup`

---

## Executive Summary

Crear y configurar el NotebookLM notebook para el Cerebro #8 con 10 fuentes expertas en metodología de entrevista, discovery y facilitación. Esta fase hace que el Cerebro #8 sea funcionalmente activo (status cambia de `pending` a `active`).

**Activities:**
1. Crear directorio de fuentes para Brain #8
2. Destilar 10 fuentes expertas (libros compilations)
3. Crear notebook en NotebookLM
4. Upload y procesamiento de fuentes
5. Obtener notebook ID
6. Actualizar registry con ID
7. Validar conexión MCP

---

## Context from Brain #8 Spec

**Referencia:** `docs/software-development/08-master-interviewer-brain/spec-brain-08-master-interviewer.md` → Sección "Expert Sources"

### Las 10 Fuentes a Crear

| ID | Título | Autor | ISBN | Prioridad |
|----|--------|-------|------|-----------|
| FUENTE-801 | The Mom Test | Rob Fitzpatrick | 978-0993181515 | 🔴 Alta |
| FUENTE-802 | Never Split the Difference | Chris Voss | 978-0062407803 | 🔴 Alta |
| FUENTE-803 | The Coaching Habit | Michael Bungay Stanier | 978-0978440749 | 🟡 Media |
| FUENTE-804 | Continuous Discovery Habits | Teresa Torres | 978-1734313504 | 🔴 Alta |
| FUENTE-805 | User Interviews | Erika Hall | - | 🟡 Media |
| FUENTE-806 | Thinking, Fast and Slow | Daniel Kahneman | 978-0374533557 | 🟡 Media |
| FUENTE-807 | Crucial Conversations | Patterson et al. | 978-1469266824 | 🟢 Baja |
| FUENTE-808 | Improve Your Retrospectives | Judith Andres | - | 🟢 Baja |
| FUENTE-809 | Ask Method | Ryan Levesque | - | 🟢 Baja |
| FUENTE-810 | Socratic Questioning | Various | - | 🟢 Baja |

---

## External Resources

### NotebookLM Documentation
- **Create Notebook:** https://notebooklm.google.com/ — Click "New notebook"
- **Add Sources:** https://support.google.com/notebooklm/answer/13141548 — Upload files
- **Get Notebook ID:** From URL: `https://notebooklm.google.com/notebook/{UUID}`
- **Source Status:** Verify sources are "Processing" → "Ready"

### Book Information Sources
- **Google Books:** https://books.google.com/ — Get ISBNs, metadata
- **Goodreads:** https://www.goodreads.com/ — Book summaries, key concepts
- **Amazon:** https://www.amazon.com/ — Book details, page counts

### Interview Methodology References
- **The Mom Test Guide:** https://momtestbook.com/ — Key principles, examples
- **Chris Voss Method:** https://blackswanltd.com/ — Negotiation techniques
- **Teresa Torres Continuous Discovery:** https://www.techatlas.com/continuous-discovery-habits/

---

## Codebase Patterns to Follow

### Pattern 1: Source File Format (FUENTE-XXX.md)

**Referencia:** `docs/software-development/01-product-strategy-brain/sources/FUENTE-001-inspired-cagan.md`

**Template a usar:**

```yaml
---
source_id: "FUENTE-XXX"
brain: "brain-software-08-master-interviewer"
niche: "software-development"
title: "Book Title"
author: "Author Name"
expert_id: "EXP-80X"
type: "book"
year: YYYY
isbn: "978-XXXXXXXX"
publisher: "Publisher"
pages: XXX
language: "en"
skills_covered: ["interview", "discovery", "facilitation"]
distillation_date: "2026-03-07"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
changelog:
  - version: "1.0.0"
    date: "2026-03-07"
    changes:
      - "Destilación inicial para Brain #8"
status: "active"

---

# FUENTE-XXX: Book Title

## Datos de la Fuente

| Campo | Valor |
|-------|-------|
| **Autor** | Author Name |
| **Tipo** | Libro |
| **Título** | Book Title |
| **Año** | YYYY |
| **ISBN** | 978-XXXXXXXX |
| **Editorial** | Publisher |
| **Páginas** | XXX |

## Contenido Destilado

### 1. Principios Fundamentales

[Extraer 3-5 principios clave]

### 2. Frameworks y Metodologías

[Extraer frameworks aplicables a entrevistas]

### 3. Modelos Mentales

[Extraer modelos mentales para el cerebro]

### 4. Criterios de Decisión

[Extraer criterios para decidir cómo/de qué preguntar]

### 5. Anti-patrones

[Extraer qué NO hacer al entrevistar]
```

### Pattern 2: Directory Structure

**Referencia:** `docs/software-development/01-product-strategy-brain/sources/`

**Estructura a crear:**
```
docs/software-development/08-master-interviewer-brain/
└── sources/
    ├── FUENTE-801_the-mom-test_fitzpatrick.md
    ├── FUENTE-802_never-split-the-difference_voss.md
    ├── FUENTE-803_the-coaching-habit_stanier.md
    ├── FUENTE-804_continuous-discovery-habits_torres.md
    ├── FUENTE-805_user-interviews_hall.md
    ├── FUENTE-806_thinking-fast-and-slow_kahneman.md
    ├── FUENTE-807_crucial-conversations_patterson.md
    ├── FUENTE-808_improve-retrospectives_andres.md
    ├── FUENTE-809_ask-method_levesque.md
    └── FUENTE-810_socratic-questioning_compilation.md
```

### Pattern 3: Source Status Tracking

**Referencia:** `mastermind_cli/brain_registry.py`

**Actualizar después de NotebookLM:**
```yaml
# mastermind_cli/config/brains.yaml

  - id: 8
    name: Master Interviewer / Discovery
    notebook_id: "d8de74d6-7028-44ed-b4d4-784d6a9256e6"  # Actual ID
    status: active  # Cambiar de 'pending' a 'active'
```

---

## Implementation Blueprint

### Step 1: Create Sources Directory (15 min)

```bash
# Create directory
mkdir -p docs/software-development/08-master-interviewer-brain/sources

# Verify
ls -la docs/software-development/08-master-interviewer-brain/
```

### Step 2: Create 10 Source Files (3 hours)

**Para cada fuente, seguir este proceso:**

#### 2.1: Research Book Content (10-15 min por libro)

1. **Buscar en Goodreads/Amazon:**
   - Title, Author, Year, ISBN, Publisher, Pages
   - Key concepts (de descriptions y reviews)

2. **Buscar resúmenes/cliffs:**
   - Google Books preview
   - Goodreads reviews
   - Author website

3. **Extraer contenido clave:**
   - 3-5 principios fundamentales
   - 2-3 frameworks o metodologías
   - 2-3 modelos mentales
   - 3-5 criterios de decisión
   - 3-5 anti-patrones

#### 2.2: Write Source File (30 min por fuente)

**Ejemplo: FUENTE-801 (The Mom Test)**

```markdown
---
source_id: "FUENTE-801"
brain: "brain-software-08-master-interviewer"
niche: "software-development"
title: "The Mom Test: How to Talk to Customers & Learn if Your Business is a Good Idea When Everyone is Lying to You"
author: "Rob Fitzpatrick"
expert_id: "EXP-801"
type: "book"
year: 2014
isbn: "978-0993181515"
isbn_10: "0993181510"
publisher: "Circuit Runner"
pages: 135
language: "en"
skills_covered: ["interview", "discovery", "customer-development", "validation"]
distillation_date: "2026-03-07"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-07"
changelog:
  - version: "1.0.0"
    date: "2026-03-07"
    changes:
      - "Destilación inicial completa"
status: "active"

---

# FUENTE-801: The Mom Test

## Datos de la Fuente

| Campo | Valor |
|-------|-------|
| **Autor** | Rob Fitzpatrick |
| **Tipo** | Libro |
| **Título** | The Mom Test: How to Talk to Customers & Learn if Your Business is a Good Idea When Everyone is Lying to You |
| **Año** | 2014 |
| **ISBN** | 978-0993181515 |
| **Editorial** | Circuit Runner |
| **Páginas** | 135 |
| **Idioma** | Inglés |

## Experto Asociado

**Rob Fitzpatrick** — Customer development, startup discovery, validation techniques
Experto en evitar sesgos en entrevistas con clientes y descubrir necesidades reales vs. respuestas educadas.

## Habilidades que Cubre

- **H1**: User Research & Discovery
- **H3**: Interview Techniques
- **H5**: Customer Development
- **H7**: Problem Validation

## Contenido Destilado

### 1. Principios Fundamentales

#### 1.1 The Mom Test Rules
1. **Never mention your idea** — La regla más importante. Si mencionás tu idea, la gente será educada y te dirá lo que querés escuchar, no lo que realmente piensa.
2. **Talk about the past, not the future** — La gente es mala prediciendo el futuro. En su lugar, preguntá sobre comportamientos pasados específicos.
3. **Talk less, listen more** — Ratio 80/20: escucha 80% del tiempo, habla 20%.

#### 1.2 The Three Lies
1. **"I'd definitely buy that"** — Mentira más común. Nadie paga nada hasta que existe.
2. **"It's a great idea"** — Opinión educada, no validación de mercado.
3. **"Our biggest problem is X"** - Lo que dicen suele no ser lo que realmente necesitan.

### 2. Frameworks y Metodologías

#### 2.1 The Mom Test Framework
**Propósito:** Descubrir necesidades reales sin sesgar las respuestas.

**Pasos:**
1. **Identify the goal** — ¿Qué querés aprender?
2. **Choose the right people** — ¿Quién tiene el problema?
3. **Prepare questions** — Preguntas sobre pasado, no futuro
4. **Conduct interview** — Escucha más de lo que hablas
5. **Look for patterns** — 3-5 conversaciones similares = patrón

#### 2.2 Good Question Examples
- ❌ "Would you use a app that does X?" (Future, hypothetical)
- ✅ "Tell me about the last time you did X." (Past, specific)
- ❌ "How much would you pay for this?" (Future, hypothetical)
- ✅ "How much do you currently spend to solve X?" (Past, real behavior)

### 3. Modelos Mentales

#### 3.1 The Compliment Sandwich
**Problema:** La gente es amable para no herir tus sentimientos.

**Patrón:** Compliment → Feedback educado → Compliment

**Solución:** Romper el sándwich buscando contradicciones en historias, no elogios.

#### 3.2 The Expert Trap
**Problema:** "Soy experto en X, sé lo que necesito."

**Realidad:** Los expertos son los peores para predecir lo que los novatos quieren.

**Principio:** Innovación es para clientes, no expertos.

### 4. Criterios de Decisión

#### 4.1 Cuándo Creer una Respuesta
| Creen si... | No creas si... |
|------------|----------------|
| Comportamiento pasado específico | Opinión sobre futuro |
| Paga dinero o tiempo ahora | "Compraría" |
| Historia con struggle | Historia idealizada |
| Mencionó 3+ veces | Mencionó 1 vez |
| Contradice otras respuestas | Alinea con todo lo demás |

#### 4.2 Learning Velocity
**Objetivo:** Maximizar aprendizaje por conversación.

**Señal de alta velocidad:**
- Te sorprenden (no confirman lo que ya sabías)
- Contradicen tus suposiciones
- Revelan problemas que no sabías que existían

**Señal de baja velocidad:**
- Confirman lo obvio
- Todo es "perfecto"
- No hay struggle stories

### 5. Anti-patrones

#### 5.1 Leading Questions
**Mal:** "¿No te parece que X sería útil?"
- Imprime tu opinión en la pregunta
- La gente será educada y dirá sí

**Bien:** "Contame sobre la última vez que X fue un problema"
- Abierto, específico, sobre pasado

#### 5.2 Solution Interviews
**Mal:** "¿Te gustaría nuestra solución de X?"
- Pregunta sobre tu solución, no el problema
- Respuestas sesgadas

**Bien:** "¿Cómo solucionás X hoy?"
- Pregunta sobre problema actual
- Respuestas honestas

#### 5.3 Feature Requests
**Mal:** Tomar requests de features al pie de la letra
- "Quiero dark mode" → Puede que sea el menor de tus problemas

**Bien:** Investigar el problema detrás del request
- "¿Por qué querés dark mode?" → "Trabajo de noche, me deslumbra"
- Problema real: Glare en night shifts

## Checklists para Brain #8

### Para Entrevistar Clientes
- [ ] No mencionar mi idea/solución
- [ ] Preguntar sobre pasado específico, no futuro
- [ ] Buscar struggles y problemas reales
- [ ] Escuchar 80%, hablar 20%
- [ ] Buscar contradicciones, no confirmaciones
- [ ] Identificar si pagan tiempo/dinero en el problema

### Para Detectar Mentiras "Educadas"
- [ ] "Definitely buy that" → Ignorar
- [ ] "Great idea" → Pedir ejemplo específico
- [ ] Opiniones unánimes → Buscar disidentes
- [ ] Historias sin struggle → Preguntar más profundo

### Para Validar Aprendizaje
- [ ] ¿Me sorprendió algo?
- [ ] ¿Contradijo mis suposiciones?
- [ ] ¿Reveló problema desconocido?
- [ ] Si NO a todas → Revisar preguntas
```

**Repetir estructura similar para las otras 9 fuentes...**

### Step 3: Create Notebook in NotebookLM (30 min)

**Instrucciones:**

1. Ir a https://notebooklm.google.com/
2. Click **"New notebook"**
3. Nombre: `Brain 08 - Master Interviewer`
4. Click **"Create"**
5. Copy notebook ID from URL
   - URL format: `https://notebooklm.google.com/notebook/{UUID}`
   - Copy UUID only

### Step 4: Upload Sources (1 hour)

**Para cada una de las 10 fuentes:**

1. En NotebookLM, click **"Add sources"**
2. Seleccionar **"Google Drive"**
3. Upload `FUENTE-XXX.md`
4. Esperar a "Processing" → "Ready"
5. Verificar que aparece en el panel izquierdo

**Tip:** Podés subir todas en lote si están en el mismo directorio.

### Step 5: Update Brain Registry (15 min)

**Editar:** `mastermind_cli/config/brains.yaml`

```yaml
  - id: 8
    name: Master Interviewer / Discovery
    notebook_id: "ACTUAL-NOTEBOOK-ID-HERE"  # Reemplazar con ID real
    system_prompt: agents/brains/master-interviewer.md
    expertise:
      - Interview methodology
      - Information extraction
      - Question structuring
      - Gap detection
      - Facilitation techniques
    status: active  # Cambiar de 'pending' a 'active'
    sources_count: 10
    notebook_name: "Brain 08 - Master Interviewer"
```

### Step 6: Validate MCP Connection (30 min)

**Test 1: Status check**

```bash
mm brain status

# Expected output incluye:
# Brain #8: Master Interviewer / Discovery
#   Status: Active
#   Sources: 10
#   Notebook: [ID]
```

**Test 2: Query brain**

```bash
# Test que Brain #8 responde
python -c "
from mastermind_cli.orchestrator.brain_executor import BrainExecutor
executor = BrainExecutor()

result = executor.execute(
    brain_id=8,
    task={'context': {'brief': 'test', 'instruction': 'generate interview strategy'}},
    use_mcp=True
)

print('Brain #8 test result:')
print(result)
"

# Expected: status should NOT be 'mock', should be 'completed' or 'active'
```

---

## Validation Gates

```bash
# ========== Step 1: Directory Created ==========
ls -la docs/software-development/08-master-interviewer-brain/sources/
echo "✅ Sources directory exists"

# ========== Step 2: All Source Files Created ==========
python -c "
import yaml
from pathlib import Path

sources_dir = Path('docs/software-development/08-master-interviewer-brain/sources')
source_files = list(sources_dir.glob('FUENTE-*.md'))

print(f'Found {len(source_files)} source files')

# Verify all 10 exist
expected = [801, 802, 803, 804, 805, 806, 807, 808, 809, 810]
for i in expected:
    file = sources_dir / f'FUENTE-{i}_*.md'
    if not file.exists():
        print(f'❌ Missing FUENTE-{i}')
        exit(1)

print('✅ All 10 source files created')

# Verify YAML frontmatter in each file
for source_file in source_files:
    with open(source_file) as f:
        content = yaml.safe_load_all(f)
        if not content[0].get('source_id'):
            print(f'❌ {source_file.name}: missing source_id')
            exit(1)

print('✅ All source files have valid YAML frontmatter')
"

# ========== Step 3: NotebookLM Notebook Created ==========
# Manual verification required
echo "⚠️  MANUAL CHECK: Verify notebook exists in NotebookLM"
echo "   1. Go to https://notebooklm.google.com/"
echo "   2. Look for 'Brain 08 - Master Interviewer'"
echo "   3. Verify it has 10 sources uploaded"

# ========== Step 4: Sources Uploaded ==========
# Manual verification required
echo "⚠️  MANUAL CHECK: Verify all 10 sources show 'Ready' status"
echo "   In NotebookLM, each source should have a ✓ checkmark"

# ========== Step 5: Registry Updated ==========
python -c "
import yaml
from pathlib import Path

brains_path = Path('mastermind_cli/config/brains.yaml')
with open(brains_path) as f:
    config = yaml.safe_load(f)

brain_8 = [b for b in config['brains'] if b['id'] == 8][0]

assert brain_8['status'] == 'active', f\"Status is {brain_8['status']}, should be 'active'\"
assert brain_8['notebook_id'], 'notebook_id should be set'
assert brain_8['sources_count'] == 10, f'sources_count is {brain_8.get(\"sources_count\")}, should be 10'

print('✅ Brain #8 registry updated correctly')
print(f\"   Notebook ID: {brain_8['notebook_id']}\")
print(f\"   Status: {brain_8['status']}\")
"

# ========== Step 6: MCP Connection Works ==========
mm brain status

# Expected output includes Brain #8 as Active
if ! mm brain status | grep -q "Brain #8"; then
    echo "❌ Brain #8 not showing in status"
    exit 1
fi

echo "✅ Brain #8 visible in mm brain status"

# Test query (optional, requires MCP working)
echo "⚠️  OPTIONAL: Test Brain #8 query (requires MCP)"
echo "   If MCP is available, Brain #8 should respond (not mock)"

echo ""
echo "========== ALL VALIDATIONS PASSED (except manual checks) =========="
```

---

## Error Handling

### Error 1: Source File Invalid YAML

**When:** YAML frontmatter has syntax errors

**Validation:**
```python
import yaml
from pathlib import Path

sources_dir = Path('docs/software-development/08-master-interviewer-brain/sources')
for source_file in sources_dir.glob('FUENTE-*.md'):
    try:
        with open(source_file) as f:
            yaml.safe_load_all(f)
    except yaml.YAMLError as e:
        print(f"❌ {source_file.name}: {e}")
        # Fix common issues
        with open(source_file) as f:
            content = f.read()
        # Add quotes around status if needed
        content = re.sub(r'^status: (\w+)', r'status: "\1"', content, flags=re.MULTILINE)
```

### Error 2: Notebook Source Processing Failed

**When:** Source stuck in "Processing" status

**Troubleshooting:**
1. Check file size (<10MB recommended)
2. Check file encoding (UTF-8)
3. Try re-uploading the file
4. Check NotebookLM status page: https://www.google.com/status/

### Error 3: Notebook ID Not Found

**When:** MCP can't connect to notebook

**Diagnosis:**
```bash
# Test MCP connection
python -c "
from mastermind_cli.orchestrator.mcp_wrapper import MCPWrapper
mcp = MCPWrapper()
if not mcp.is_available():
    print('❌ MCP not available')
else:
    print('✅ MCP available')
    # Try to list notebooks
    mcp.list_all_brains()
"
```

---

## Gotchas & Pitfalls

### Gotcha 1: NotebookLM Source Limits

**Issue:** Max file size 10MB per source

**Fix:** Split large books into multiple files (FUENTE-801-part1.md, FUENTE-801-part2.md)

### Gotcha 2: ISBN Formatting

**Issue:** ISBN can be ISBN-10 or ISBN-13

**Fix:** Include both if available:
```yaml
isbn: "978-0993181515"
isbn_10: "0993181510"
```

### Gotcha 3: Source Status "Processing" Too Long

**Issue:** Source stuck processing > 10 minutes

**Fix:**
1. Refresh NotebookLM page
2. Check source file for encoding issues
3. Try uploading again
4. As fallback, create summary document instead of full book

### Gotcha 4: Notebook ID Format

**Issue:** Confusing notebook URL with ID

**Clarification:**
- Full URL: `https://notebooklm.google.com/notebook/abc123def456...`
- Notebook ID: `abc123def456...` (just the UUID part)

**Implementation:**
```python
# Extract ID from URL
url = "https://notebooklm.google.com/notebook/abc123def456"
notebook_id = url.split('/')[-1]
```

---

## Quality Checklist

- [x] All necessary context included (ISBNs, autores, referencias)
- [x] Validation gates ejecutables (excepto checks manuales NotebookLM)
- [x] References existing patterns (FUENTE-001 format)
- [x] Clear implementation path (6 steps, 5 horas)
- [x] Error handling documentado (3 categorías)
- [x] Source file template incluido con ejemplo completo
- [x] NotebookLM workflow documentado
- [x] MCP validation steps incluidos

---

## Branch Strategy

**Create branch:** `feature/prp-012-brain-08-notebooklm-setup`

```bash
git checkout -b feature/prp-012-brain-08-notebooklm-setup

# Work through implementation
# ... create 10 source files ...
# ... create notebook in NotebookLM ...
# ... upload sources ...

# Commit when done
git add docs/software-development/08-master-interviewer-brain/sources/
git add mastermind_cli/config/brains.yaml
git commit -m "feat(prp-012): setup notebooklm for brain #8

- Create 10 expert sources (FUENTE-801 to FUENTE-810)
- Create NotebookLM notebook: Brain 08 - Master Interviewer
- Upload and process all 10 sources
- Update brain registry with notebook ID
- Change brain #8 status from 'pending' to 'active'

Sources:
- FUENTE-801: The Mom Test (Fitzpatrick)
- FUENTE-802: Never Split the Difference (Voss)
- FUENTE-803: The Coaching Habit (Stanier)
- FUENTE-804: Continuous Discovery Habits (Torres)
- FUENTE-805: User Interviews (Hall)
- FUENTE-806: Thinking, Fast and Slow (Kahneman)
- FUENTE-807: Crucial Conversations (Patterson)
- FUENTE-808: Improve Your Retrospectives (Andres)
- FUENTE-809: Ask Method (Levesque)
- FUENTE-810: Socratic Questioning (Compilation)

Notebook ID: [ACTUAL-ID-FROM-NOTEBOOKLM]
Status: Active

Validations:
✅ All 10 source files created with valid YAML
✅ Notebook created with all sources uploaded
✅ Brain #8 status changed to 'active'
✅ mm brain status shows Brain #8 as Active

Refs: PRP-012, spec-brain-08"
```

---

## Success Criteria

- [ ] Directorio `docs/software-development/08-master-interviewer-brain/sources/` existe
- [ ] 10 archivos FUENTE-801 a FUENTE-810 creados con YAML válido
- [ ] Cada fuente tiene las 5 secciones requeridas (Principios, Frameworks, Modelos, Criterios, Anti-patrones)
- [ ] Notebook "Brain 08 - Master Interviewer" creado en NotebookLM
- [ ] Todas las 10 fuentes uploadeds y showing "Ready" status
- [ ] Notebook ID copiado y actualizado en `brains.yaml`
- [ ] Brain #8 status cambiado a `active`
- [ ] `mm brain status` muestra Brain #8 como Active
- [ ] MCP connection test pasa (opcional si MCP disponible)

---

## PRP Confidence Score

**Score: 9/10**

**Justification:**
- ✅ **Well-defined process** — Creación de fuentes es straightforward
- ✅ **Clear template** — FUENTE-001 como patrón
- ✅ **Manual checks** — NotebookLM requires manual steps (well documented)
- ✅ **Low code complexity** — Solo actualización de YAML registry
- ⚠️ **-1 punto** — Proceso manual (NotebookLM) puede tener errores humanos

**Riesgo identificado:** Crear 10 fuentes es trabajo intenso. Si la calidad de destilación es baja, el cerebro #8 no funcionará bien. **Mitigación:** Seguir template estrictamente y validar cada fuente con YAML check.

---

## Next Steps After Completion

Once PRP-012 is complete:

1. **Validate:** `mm brain status` shows Brain #8 as Active with 10 sources
2. **Test simple query:** Ejecutar un test básico de Brain #8 via MCP
3. **Start PRP-013:** Orchestrator Integration (implementa interview flow)

---

**END OF PRP-012**
