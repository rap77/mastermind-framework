# PRP-014: Brain #8 Slash Command

**Status:** Ready to Implement (after PRP-013)
**Priority:** High (user-facing interface)
**Estimated Time:** 4 hours
**Dependencies:** PRP-011, PRP-012, PRP-013
**Branch:** `feature/prp-014-brain-08-slash-command`

---

## Executive Summary

Crear el comando slash `/mm:discovery` que permite a los usuarios ejecutar entrevistas de discovery desde cualquier contexto de Claude Code. Este comando es la interfaz principal para interactuar con el Cerebro #8.

**Activities:**
1. Crear archivo `.claude/commands/mm/discovery.md`
2. Documentar uso y ejemplos
3. Testear con varios inputs
4. Actualizar CLI-REFERENCE.md

---

## Context from Brain #8 Spec

**Referencia:** `docs/software-development/08-master-interviewer-brain/spec-brain-08-master-interviewer.md` → Sección "Slash Command"

### Comandos Existentes (Patrón)

El proyecto ya tiene varios comandos `/mm:...`:
- `/mm:ask-product` — Consulta Product Strategy brain
- `/mm:ask-ux` — Consulta UX Research brain
- `/mm:ask-qa` — Consulta QA/DevOps brain
- `/mm:generate-prp` — Genera PRP para features

**Pattern a seguir:** Mismo formato YAML + Markdown

### El Comando /mm:discovery

**Uso principal:**
```bash
/mm:discovery "<problem or requirement>"
```

**Casos de uso:**
1. Cliente de agencia necesita onboarding → brief estructurado
2. Feature request vaga → requerimientos clarificados
3. Problema técnico complejo → especificación técnica
4. Idea de producto → validación de gaps

---

## External Resources

### Claude Code Slash Commands Documentation

**Referencia:** `.claude/commands/` structure

```yaml
---
name: command-name
description: One-line description
usage: /command-name "<argument>"
examples:
  - /command-name "example 1"
  - /command-name "example 2"
---

# Command Name

## Usage

Detailed usage instructions...

## Examples

### Example 1
...
```

---

## Codebase Patterns to Follow

### Pattern 1: Ask Product Command

**Archivo:** `.claude/commands/mm/ask-product.md`

```yaml
---
name: ask-product
description: Consult Product Strategy brain
usage: /mm:ask-product "<question>"
examples:
  - /mm:ask-product "What are the key features of a delivery app?"
---

# Ask Product Strategy

## Usage

Run this command to get product insights from Brain #1 (Product Strategy).

## Examples

### Feature Prioritization
/mm:ask-product "How do I prioritize features for an MVP?"
```

**✅ PATRÓN A SEGUIR:** Mismo formato YAML + ejemplos

### Pattern 2: Generate PRP Command

**Archivo:** `.claude/commands/mm/generate-prp.md`

```yaml
---
name: generate-prp
description: Create PRP
usage: /mm:generate-prp "<feature description>"
examples:
  - /mm:generate-prp "user authentication system"
---

# Create PRP

## Usage

Use this command when you need to create a comprehensive...

## What It Does

1. Analyzes the feature request
2. Searches codebase for similar patterns
3. Researches external resources
4. Generates complete PRP with validation gates
```

**✅ PATRÓN A SEGUIR:** Sección "What It Does" con pasos enumerados

### Pattern 3: Namespace /mm

**Location:** Todos los comandos están en `.claude/commands/mm/`

**Razón:** Namespace `mm` indica que son comandos específicos del proyecto MasterMind

**✅ PATRÓN A SEGUIR:** Crear `.claude/commands/mm/discovery.md`

---

## Implementation Blueprint

### Step 1: Create Slash Command File (2 hours)

**Crear:** `.claude/commands/mm/discovery.md`

```yaml
---
name: discovery
description: Conduct structured discovery interview using Brain #8 (Master Interviewer)
usage: /mm:discovery "<problem or vague requirement>"
examples:
  - /mm:discovery "Quiero crear una app de delivery"
  - /mm:discovery "Necesito un sistema de login moderno"
  - /mm:discovery "Cliente de agencia de marketing necesita onboarding"
  - /mm:discovery "¿Cómo implementar SEO en mi sitio?"
---

# MasterMind Discovery Interviewer

## Usage

Run this command when you need to:
- **Extract requirements** from vague or incomplete user input
- **Conduct onboarding interviews** for clients
- **Clarify technical specifications** before implementation
- **Discover user needs** before designing features
- **Identify knowledge gaps** that require new expertise

## What It Does

The `/mm:discovery` command conducts an **iterative interview** powered by Brain #8 (Master Interviewer):

1. **Analyzes your input** to understand context and detect ambiguity
2. **Consults Brain #8** to design an interview strategy
3. **Asks structured questions** one by one (interactive)
4. **Routes each question** to the appropriate domain brain (#1-7) for follow-up
5. **Generates a complete Q&A document** in JSON/YAML/Markdown formats
6. **Detects knowledge gaps** and recommends creating new brains if needed

## Examples

### Client Onboarding (Agency Use Case)

**Input:**
```bash
/mm:discovery "Cliente de agencia de marketing necesita una app para gestionar campañas"
```

**Process:**
1. Brain #8 asks about target users, platforms, key features
2. Each answer gets follow-up from relevant domain brains
3. After 10-15 questions, structured brief is generated

**Output:**
```markdown
# Discovery Interview Summary

**Session ID:** a1b2c3d4
**Date:** 2026-03-07
**Context:** client_onboarding

**Questions Asked:** 12

**Categories:**
- **Users & Personas** (Brain #2)
- **Platforms & Tech Stack** (Brain #4)
- **Key Features** (Brain #1)
- **Campaign Management** (Brain #1)

**Key Findings:**
- B2B SaaS for marketing agencies (5-50 employees)
- Web + Mobile (field staff needs tablets)
- Real-time collaboration is critical
- Must integrate with Facebook/Google Ads APIs

**Domain Recommendations:**
- Brain #1 suggests focusing on campaign approval workflows first
- Brain #4 recommends Progressive Web App for cross-platform support
```

### Feature Clarification (Internal Use)

**Input:**
```bash
/mm:discovery "Quiero una app moderna"
```

**Process:**
1. Brain #8 detects ambiguity ("moderna" is vague)
2. Asks clarifying questions about industry, users, platforms
3. Digs into what "modern" means (design? tech? features?)

**Output:**
```markdown
# Clarified Requirements

**Original:** "Quiero una app moderna"

**Clarified:**
- **Industry:** E-commerce (retail)
- **Users:** End customers (B2C)
- **Platform:** Mobile-first (iOS/Android)
- **"Modern" means:**
  - Clean UI with dark mode support
  - Gesture-based navigation
  - Real-time inventory updates
  - Social login (Google/Apple)

**Recommended Next Steps:**
1. Create wireframes with Brain #3 (UI Design)
2. Define tech stack with Brain #4 (Frontend)
3. Plan authentication with Brain #5 (Backend)
```

### Technical Specification (Dev Use)

**Input:**
```bash
/mm:discovery "Necesitamos integrar OAuth con Google y Microsoft para login"
```

**Process:**
1. Interview focuses on technical requirements
2. Brain #5 (Backend) provides deep follow-up on security
3. Generates technical spec

**Output:**
```markdown
# Technical Specification: OAuth Integration

**Requirements:**
- OAuth 2.0 flow for Google and Microsoft Identity
- JWT token handling with refresh mechanism
- Secure session management

**Security Considerations** (from Brain #5):
- PKCE extension for mobile apps
- Store tokens securely (Keychain/Keystore)
- Implement token revocation on logout
- Rate limiting to prevent abuse

**API Endpoints Needed:**
- POST /auth/google
- POST /auth/microsoft
- POST /auth/refresh
- POST /auth/revoke

**Recommended Libraries:**
- Python: authlib
- Node.js: passport.js
```

### Gap Detection (New Expertise)

**Input:**
```bash
/mm:discovery "Necesito implementar SEO y content marketing en mi sitio"
```

**Process:**
1. Interview proceeds normally
2. Brain #8 detects that current brains don't cover SEO/Marketing
3. Generates recommendation for new brain

**Output:**
```markdown
# Discovery Results

**Requirements Identified:**
- On-page SEO optimization
- Content management system
- Blog functionality
- Social media integration

**⚠️ Knowledge Gap Detected:**

Current MasterMind brains (#1-7) focus on software development.
SEO and Content Marketing require **domain expertise not currently available**.

**Recommendation:**

Consider creating **Brain #9: Growth Marketing** with expertise in:
- SEO (on-page, technical, off-page)
- Content strategy
- Social media marketing
- Analytics & attribution

**Suggested Experts:**
- Rand Fishkin (SEOmoz)
- Brian Dean (Backlinko)
- Ann Handley (Content Marketing Institute)

**Available Alternatives:**
- Brain #7 (Growth/Data) can help with analytics setup
- Brain #1 (Product Strategy) can help prioritize SEO features
```

## Output Formats

The discovery command generates **three formats** automatically:

### 1. JSON (Machine-readable)
```json
{
  "session_id": "a1b2c3d4",
  "timestamp": "2026-03-07T10:30:00Z",
  "document": {
    "qa": [...],
    "categories": [...],
    "gaps_detected": [...]
  }
}
```
**Location:** `logs/interviews/json/2026-03/INTERVIEW-2026-03-07-001.json`

### 2. YAML (Logging)
```yaml
interview_id: INTERVIEW-2026-03-07-001
timestamp: "2026-03-07T10:30:00Z"
brain: "brain-08"
context:
  brief_original: "..."
  context_type: "feature_spec"
interview:
  questions_asked: 12
  categories_covered: 4
```
**Location:** `logs/interviews/hot/2026-03/INTERVIEW-2026-03-07-001.yaml`

### 3. Markdown (Human-readable)
```markdown
# Discovery Interview Summary
...
```
**Displayed:** Directly in Claude Code response

## When to Use

| Scenario | Command | Expected Result |
|----------|---------|-----------------|
| **Client onboarding** | `/mm:discovery "cliente necesita X"` | Structured brief for team |
| **Feature request** | `/mm:discovery "agregar feature Y"` | Clarified requirements |
| **Vague idea** | `/mm:discovery "quiero una app"` | Specific direction |
| **Tech spec** | `/mm:discovery "integrar API Z"` | Technical specification |
| **Gap detection** | `/mm:discovery "necesito expertise X"` | New brain recommendation |

## Tips for Best Results

1. **Be honest about uncertainty** — Discovery works best with vague input
2. **Answer all questions** — Even "I don't know" helps the process
3. **Review the Q&A document** — It captures everything discussed
4. **Check gaps detected** — May reveal missing expertise
5. **Share with team** — Output formats designed for collaboration

## Related Commands

- `/mm:ask-product` — Get product insights without interview
- `/mm:generate-prp` — Create implementation plan from requirements
- `/mm:project-health-check` — Full 7-brain project analysis

## Technical Details

- **Brain Used:** #8 (Master Interviewer / Discovery)
- **Domain Brains Consulted:** #1-7 (as needed)
- **Interview Duration:** 5-15 minutes (10-20 questions typical)
- **Output Location:** `logs/interviews/`
- **Learning Enabled:** Yes (interviews improve future suggestions)
```

### Step 2: Update CLI Reference (1 hour)

**Editar:** `docs/CLI-REFERENCE.md`

**Agregar sección:**

```markdown
## Discovery Commands

### /mm:discovery

Conduct structured discovery interview using Brain #8.

**Usage:**
```
/mm:discovery "<problem or requirement>"
```

**Examples:**
- `/mm:discovery "Quiero crear una app de delivery"` — Client onboarding
- `/mm:discovery "Necesito un sistema de login"` — Feature clarification
- `/mm:discovery "Implementar OAuth con Google"` — Technical spec

**What it does:**
1. Analyzes input for ambiguity
2. Designs interview strategy via Brain #8
3. Asks structured questions interactively
4. Routes to domain brains (#1-7) for follow-ups
5. Generates Q&A document (JSON/YAML/Markdown)
6. Detects knowledge gaps

**Output:**
- JSON: `logs/interviews/json/YYYY-MM/INTERVIEW-*.json`
- YAML: `logs/interviews/hot/YYYY-MM/INTERVIEW-*.yaml`
- Markdown: Displayed in response

**Duration:** 5-15 minutes (10-20 questions typical)

**See also:** [Slash Command Documentation](.claude/commands/mm/discovery.md)
```

### Step 3: Manual Testing (1 hour)

**Test Cases:**

1. **Vague brief:**
   ```bash
   /mm:discovery "quiero una app"
   ```
   Expected: Detects ambiguity, asks clarifying questions

2. **Technical spec:**
   ```bash
   /mm:discovery "OAuth integration with Google"
   ```
   Expected: Focuses on technical requirements, routes to Brain #5

3. **Client onboarding:**
   ```bash
   /mm:discovery "Cliente de retail necesita inventory system"
   ```
   Expected: Covers users, platforms, features, business logic

4. **Gap detection:**
   ```bash
   /mm:discovery "SEO and content marketing system"
   ```
   Expected: Detects missing expertise, recommends new brain

### Step 4: Document Examples (Optional, 30 min)

**Crear:** `docs/examples/discovery-interviews.md`

```markdown
# Discovery Interview Examples

Collection of real discovery interview examples for reference.

## Example 1: E-commerce App

**Input:** `/mm:discovery "Quiero una app para vender productos online"`

**Summary:** [Include actual interview output]

---

## Example 2: B2B SaaS Dashboard

**Input:** `/mm:discovery "Dashboard para analytics de negocios"`

**Summary:** [Include actual interview output]

---

## Example 3: Social Network Features

**Input:** `/mm:discovery "Agregar social features a mi app existente"`

**Summary:** [Include actual interview output]
```

---

## Validation Gates

```bash
# ========== Step 1: Command File Created ==========
ls -la .claude/commands/mm/discovery.md
echo "✅ discovery.md command file exists"

# Verify YAML structure
python -c "
import yaml
with open('.claude/commands/mm/discovery.md') as f:
    content = f.read()
    # Check YAML frontmatter
    assert 'name: discovery' in content
    assert 'description:' in content
    assert 'usage:' in content
    print('✅ YAML frontmatter valid')
"

# ========== Step 2: CLI Reference Updated ==========
grep -q "/mm:discovery" docs/CLI-REFERENCE.md
echo "✅ CLI-REFERENCE.md updated"

# ========== Step 3: Command Discoverable ==========
# Verify command shows up in Claude Code
echo "⚠️  MANUAL CHECK: Run /mm: in Claude Code to verify discovery command appears"

# ========== Step 4: Test Command (Mock Mode) ==========
echo "⚠️  MANUAL CHECK: Test /mm:discovery 'test brief' in Claude Code"
echo "   Expected: Command executes without errors"

# ========== Step 5: Verify Output Files ==========
echo "⚠️  MANUAL CHECK: After running command, verify output files exist:"
echo "   ls -la logs/interviews/hot/\$(date +%Y-%m)/"
echo "   ls -la logs/interviews/json/\$(date +%Y-%m)/"

echo "========== ALL VALIDATIONS PASSED (except manual checks) =========="
```

---

## Error Handling

| Error | Handling |
|-------|----------|
| **Command not found** | Verify file is in `.claude/commands/mm/discovery.md` |
| **YAML parse error** | Check frontmatter indentation (use spaces, not tabs) |
| **Orchestrator not found** | Ensure PRP-013 is merged |
| **MCP unavailable** | Falls back to mock mode (documented in command) |

---

## Gotchas & Pitfalls

### Gotcha 1: YAML Frontmatter Indentation

**Issue:** YAML is sensitive to indentation

**Fix:** Use 2 spaces for indentation in frontmatter:
```yaml
---
name: discovery
description: Text here
usage: /mm:discovery "..."
examples:
  - /mm:discovery "example"
---
```

### Gotcha 2: Command Not Appearing

**Issue:** Command doesn't show up in Claude Code autocomplete

**Fix:**
1. Verify file is in correct location: `.claude/commands/mm/discovery.md`
2. Check file permissions (must be readable)
3. Restart Claude Code if needed

### Gotcha 3: Examples Too Long

**Issue:** Long examples make command documentation hard to read

**Fix:** Keep examples concise (3-5 lines max). Put detailed examples in separate file.

---

## Quality Checklist

- [x] All necessary context included (spec, comandos existentes)
- [x] Validation gates ejecutables (excepto checks manuales)
- [x] References existing patterns (ask-product, generate-prp)
- [x] Clear implementation path (4 steps, 4 horas)
- [x] Error handling documentado (4 categorías)
- [x] Complete command file incluido con todos los ejemplos
- [x] CLI reference update especificada
- [x] Test cases documentados

---

## Branch Strategy

**Create branch:** `feature/prp-014-brain-08-slash-command`

```bash
git checkout -b feature/prp-014-brain-08-slash-command

# Work through implementation
# ... create discovery.md ...
# ... update CLI-REFERENCE.md ...
# ... manual testing ...

# Commit when done
git add .claude/commands/mm/discovery.md
git add docs/CLI-REFERENCE.md
git add docs/examples/discovery-interviews.md
git commit -m "feat(prp-014): add /mm:discovery slash command

- Create .claude/commands/mm/discovery.md
- Document usage, examples, and output formats
- Update CLI-REFERENCE.md with discovery command
- Add example interviews for reference

Validations:
✅ Command file exists with valid YAML
✅ CLI-REFERENCE.md updated
✅ Command discoverable in Claude Code
✅ Manual tests passing (4 test cases)

Refs: PRP-014, spec-brain-08"
```

---

## Success Criteria

- [ ] `.claude/commands/mm/discovery.md` existe
- [ ] YAML frontmatter es válido
- [ ] Comando aparece en Claude Code autocomplete
- [ ] `/mm:discovery "test brief"` ejecuta sin errores
- [ ] Output files creados en `logs/interviews/`
- [ ] CLI-REFERENCE.md actualizado
- [ ] Ejemplo de entrevista documentado (opcional)

---

## PRP Confidence Score

**Score: 10/10**

**Justification:**
- ✅ **Well-defined pattern** — Varios comandos /mm: ya existen
- ✅ **Low complexity** — Solo creación de archivo de documentación
- ✅ **No code changes** — PRP-013 ya implementó toda la lógica
- ✅ **Clear validation** — Verificar que archivo existe y YAML es válido
- ✅ **Isolated** — No afecta otros componentes

**Riesgo mínimo:** Este PRP es puramente documentación. La lógica ya está implementada en PRP-013.

---

## Next Steps After Completion

Once PRP-014 is complete:

1. **Test manualmente** con `/mm:discovery "quiero una app"`
2. **Start PRP-015:** Learning System Integration (find_similar_interviews, metrics)
3. **Document** un ejemplo real de entrevista en `docs/examples/`

---

**END OF PRP-014**
