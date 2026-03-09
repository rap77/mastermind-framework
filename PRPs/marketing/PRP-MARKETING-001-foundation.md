# PRP-MARKETING-001: Nicho Marketing Digital - Foundation

**Status:** Ready to Implement
**Priority:** High
**Estimated Time:** 8-10 hours
**Dependencies:** None

---

## Executive Summary

Crear la base del nicho **Marketing Digital y Redes Sociales** para el MasterMind Framework. Este PRP establece la estructura de archivos, configuración multi-nicho, y los 16 system prompts base para los cerebros especializados. NO incluye la creación de fuentes maestras (eso es PRP-MARKETING-002 y PRP-MARKETING-003).

---

## Context from Requirements

### Decisiones Críticas

1. **16 Cerebros vs 7:** Marketing Digital es más amplio y fragmentado que Software Development
2. **Expertos sin preferencia:** Mezcla de expertos hispanos e internacionales según conocimiento necesario (no hay cuota, solo calidad)
3. **System prompts en inglés:** Mejor performance con LLMs
4. **Output bilingüe:** Responder en el idioma del input
5. **Cerebro #16 como evaluador:** Growth Partner & Agency Operations (meta-cerebro similar al #7 de Software Dev)

### Estructura de Archivos a Crear

```
docs/
└── nichos/
    └── marketing-digital/
        ├── PROPUESTA-16-CEREBROS.md    ✅ (ya existe)
        ├── PRP-MARKETING-DIGITAL-NICHO.md ✅ (ya existe)
        └── sources/                     (a crear en PRP-002/003)
            ├── BRAIN-01-STRATEGY/
            ├── BRAIN-02-BRAND/
            └── ... (hasta BRAIN-16)

mastermind_cli/
└── config/
    └── brains-marketing.yaml           (a crear en este PRP)

agents/
└── brains/
    ├── marketing-01-strategy.md        (a crear en este PRP)
    ├── marketing-02-brand.md
    └── ... (hasta marketing-16-growth-partner.md)
```

---

## External Resources

### System Prompt Patterns
- `/home/rpadron/proy/mastermind/PRPs/PRP-003-system-prompts.md` - Reference para estructura de prompts
- `/home/rpadron/proy/mastermind/agents/brains/product-strategy.md` - Template de system prompt

### YAML Config Patterns
- `/home/rpadron/proy/mastermind/mastermind_cli/config/brains.yaml` - Estructura existente

### Marketing Expert Sources
- **April Dunford:** https://www.aprildunford.com/blog/ - Positioning experts
- **Andy Crestodina:** https://www.orbitmedia.com/blog/ - Content marketing
- **Brian Dean:** https://backlinko.com/blog/ - SEO content
- **Peep Laja:** https://conversionxl.com/blog/ - CRO
- **Aleyda Solís:** https://www.aleydasolis.com/en/blog/ - SEO técnico (hispana)

---

## Implementation Blueprint

### System Prompt Template para Marketing Brains

```markdown
# Role: [MARKETING_DOMAIN] Expert

You are Brain #[M-NUMBER] of the MasterMind Framework - Marketing Digital Niche. You are the [DOMAIN] expert.

## Your Identity

You are a [DOMAIN] expert with knowledge distilled from:
- **[Expert 1]** ([Affiliation/Background]): [Key contribution]
- **[Expert 2]** ([Affiliation/Background]): [Key contribution]
- **[Expert 3]** ([Affiliation/Background]): [Key contribution]
- **[Expert 4+]** ([Affiliation/Background]): [Key contribution]

## Your Purpose

You define:
- **[WHAT aspect of marketing you handle]**
- **[WHY this matters for the business]**
- **[HOW you measure success]**

## Your Frameworks

- **[Framework 1]** ([Expert]): [Brief description]
- **[Framework 2]** ([Expert]): [Brief description]
- **[Framework 3]** ([Expert]): [Brief description]

## Your Process

1. **[Step 1]**
2. **[Step 2]**
3. **[Step 3]**

## Your Rules

- [Rule 1]
- [Rule 2]
- [Rule 3]

## Your Output Format

```json
{
  "brain": "marketing-[domain]",
  "task_id": "UUID",
  "niche": "marketing-digital",
  "[key_outputs]": {},
  "recommendations": [],
  "confidence": 0.0-1.0
}
```

Add a `content` field with Markdown explanation for humans.

## Language

Respond in the same language as the user's input. If they write in Spanish, respond in Spanish. If English, respond in English.
```

### brains-marketing.yaml Structure

```yaml
version: "1.0"
niche: "marketing-digital"
niche_name: "Marketing Digital y Redes Sociales"
brains:
  - id: M1
    name: Marketing Strategy & Positioning
    short_id: marketing-strategy
    notebook_id: null  # To be filled in PRP-002
    system_prompt: agents/brains/marketing-01-strategy.md
    expertise:
      - Positioning strategy
      - Brand strategy
      - GTM strategy
      - Pricing strategy
      - Marketing frameworks
    status: active
    sources_count: 0  # To be filled in PRP-002

  # ... M2 to M16
```

---

## Tasks (in Order)

### Task 1: Crear Estructura de Directorios (15 min)
- [ ] Crear `docs/nichos/marketing-digital/sources/`
- [ ] Crear subdirectorios `BRAIN-01-STRATEGY/` a `BRAIN-16-GROWTH-PARTNER/`
- [ ] Verificar estructura con `tree docs/nichos/marketing-digital/`
- [ ] Output: 16 directorios vacíos listos para fuentes

### Task 2: Actualizar brains.yaml para Multi-Nicho (30 min)
- [ ] Leer `/home/rpadron/proy/mastermind/mastermind_cli/config/brains.yaml`
- [ ] Agregar campo `niche: "software-development"` a cerebros existentes (#1-8)
- [ ] Mantener compatibilidad backward compatible
- [ ] Documentar nuevo formato en comentario al inicio del YAML
- [ ] Validar YAML syntax
- [ ] Output: `brains.yaml` actualizado con soporte multi-nicho

### Task 3: Crear brains-marketing.yaml (1 hour)
- [ ] Crear archivo con 16 cerebros siguiendo estructura de brains.yaml
- [ ] Para cada cerebro M1-M16:
  - [ ] ID, nombre, short_id
  - [ ] notebook_id: null (placeholder)
  - [ ] system_prompt: path correspondiente
  - [ ] expertise: lista de 4-6 áreas
  - [ ] status: active
  - [ ] sources_count: 0
- [ ] Validar YAML syntax
- [ ] Output: `mastermind_cli/config/brains-marketing.yaml`

### Task 4: Crear System Prompts - Grupo 1: Estrategia (1.5 hours)
- [ ] **marketing-01-strategy.md** (30 min)
  - Expertos: April Dunford, Andy Cunningham, Marty Neumeier, Elena Verna, Kyle Poyar
  - Frameworks: Positioning, Brand Strategy, GTM, Pricing
- [ ] **marketing-02-brand.md** (30 min)
  - Expertos: Sagi Haviv, Debbie Millman, Alina Wheeler, Brian Collins, David Aaker
  - Frameworks: Brand Identity, Logo Design, Brand Voice, Design Systems
- [ ] **marketing-03-content.md** (30 min)
  - Expertos: Joanna Wiebe, Joe Pulizzi, Donald Miller, Andy Crestodina, Amy Posner
  - Frameworks: Copywriting, Content Strategy, Storytelling, Video Scripting
- [ ] Output: 3 system prompts en `agents/brains/`

### Task 5: Crear System Prompts - Grupo 2: Social Media (1.5 hours)
- [ ] **marketing-04-social-organic.md** (30 min)
  - Expertos: Jasmine Star, Rachel Pedersen, Justin Welsh, Katelyn Bourgoin, Brianne Fleming
  - Frameworks: Instagram/TikTok, LinkedIn, Twitter, Community Building, UGC
- [ ] **marketing-05-social-paid.md** (30 min)
  - Expertos: Dennis Yu, Nicholas Kusmich, Molly Pittman, AJ Wilcox, Tom Breeze
  - Frameworks: Meta Ads, TikTok Ads, LinkedIn Ads, YouTube Ads, Creative Strategy
- [ ] **marketing-06-search-ppc.md** (30 min)
  - Expertos: Perry Marshall, Mike Rhodes, Frederick Vallaeys, Larry Kim, Oli Gardner
  - Frameworks: Google Ads, Microsoft Ads, SEM Strategy, Landing Page CRO
- [ ] Output: 3 system prompts en `agents/brains/`

### Task 6: Crear System Prompts - Grupo 3: SEO (1 hour)
- [ ] **marketing-07-seo-technical.md** (30 min)
  - Expertos: Aleyda Solís, Brian Dean, Barry Schwartz, Cyrus Shepard, Annie Cushing
  - Frameworks: Technical SEO, On-Page Optimization, Site Architecture, Core Web Vitals
- [ ] **marketing-08-seo-content.md** (30 min)
  - Expertos: Andy Crestodina, Jon Cooper, Lily Ray, Ross Hudgens, Neil Patel
  - Frameworks: Content SEO, Link Building, Digital PR, E-E-A-T, Local SEO
- [ ] Output: 2 system prompts en `agents/brains/`

### Task 7: Crear System Prompts - Grupo 4: Email & Retention (1 hour)
- [ ] **marketing-09-email.md** (30 min)
  - Expertos: Ann Handley, Ryan Deiss, Val Geisler, Jepsen Crame, Joanna Wiebe
  - Frameworks: Email Copywriting, Email Strategy, Marketing Automation, Deliverability
- [ ] **marketing-10-retention.md** (30 min)
  - Expertos: Postscript team, ProfitWell (Patrick Campbell), Casey Accurso, Baremetrics, Lincoln Murphy
  - Frameworks: SMS Marketing, Push Notifications, Retention Strategy, LTV Optimization
- [ ] Output: 2 system prompts en `agents/brains/`

### Task 8: Crear System Prompts - Grupo 5: Analytics & Ops (1.5 hours)
- [ ] **marketing-11-analytics.md** (30 min)
  - Expertos: Avinash Kaushik, Simo Ahava, Peep Laja, Ronny Kohavi, Neil Patel
  - Frameworks: Web Analytics, Marketing Attribution, Data Visualization, A/B Testing
- [ ] **marketing-12-cro.md** (30 min)
  - Expertos: Peep Laja, Oli Gardner, Brian Bui, Russell Brunson, Huyen Tue
  - Frameworks: CRO Strategy, Landing Page Optimization, User Research, Funnel Optimization
- [ ] **marketing-13-ops.md** (30 min)
  - Expertos: Scott Brinker, Carlos Hidalgo, Zapier experts, Marketo team, HubSpot experts
  - Frameworks: Marketing Ops, Tech Stack Architecture, Workflow Automation, Lead Scoring
- [ ] Output: 3 system prompts en `agents/brains/`

### Task 9: Crear System Prompts - Grupo 6: Community & Growth (1 hour)
- [ ] **marketing-14-influencer.md** (30 min)
  - Expertos: Neal Schaffer, Joe Gagliese, Shawn Collins, Li Jin, Pat Flynn
  - Frameworks: Influencer Strategy, Creator Economy, Affiliate Marketing, Strategic Partnerships
- [ ] **marketing-15-community.md** (30 min)
  - Expertos: CMX team, David Spinks, Brianne Fleming, Reddit/Discord experts, GoPro team
  - Frameworks: Community Strategy, Community Management, UGC, Events, Advocacy
- [ ] Output: 2 system prompts en `agents/brains/`

### Task 10: Crear System Prompt - Evaluador (1 hour)
- [ ] **marketing-16-growth-partner.md** (60 min)
  - Expertos: Blair Enns, Carl Goulds, Marcel Petitpas, Gainsight experts, Patrick Campbell
  - Frameworks: Agency Growth, Client Success, Pricing Agency Services, Partnership Models
  - Rol: Meta-cerebro evaluador (similar al Brain #7 de Software Dev)
  - Debe tener capacidad de APPROVE/REJECT outputs de otros cerebros
- [ ] Output: 1 system prompt en `agents/brains/`

### Task 11: Validación y Testing (30 min)
- [ ] Validar que los 16 prompts tengan:
  - [ ] Sección "Your Identity" con expertos
  - [ ] Sección "Your Purpose" clara
  - [ ] Sección "Your Frameworks" con 3+ frameworks
  - [ ] Sección "Your Process" con pasos
  - [ ] Sección "Your Rules" con 3+ reglas
  - [ ] Sección "Output Format" con JSON structure
  - [ ] Sección "Language" con instrucción bilingüe
- [ ] Verificar YAML syntax de ambos config files
- [ ] Output: Checklist completado

### Task 12: Documentación (15 min)
- [ ] Actualizar `docs/nichos/marketing-digital/PROPUESTA-16-CEREBROS.md` con status "Foundation Complete"
- [ ] Crear `docs/nichos/marketing-digital/README.md` con:
  - Descripción del nicho
  - Lista de 16 cerebros con links a system prompts
  - Instrucciones para contribuir fuentes
- [ ] Output: 2 archivos de documentación

### Task 13: Git Commit (5 min)
- [ ] Revisar cambios con `git status`
- [ ] Commit: `feat(marketing): add 16-brain foundation for marketing digital niche`

---

## Validation Gates

```bash
# 1. Verificar estructura de directorios
tree docs/nichos/marketing-digital/sources/
# Expected: 16 empty directories BRAIN-01 to BRAIN-16

# 2. Validar YAML syntax
python3 -c "import yaml; yaml.safe_load(open('mastermind_cli/config/brains.yaml'))"
python3 -c "import yaml; yaml.safe_load(open('mastermind_cli/config/brains-marketing.yaml'))"
# Expected: No errors

# 3. Verificar system prompts creados
ls agents/brains/marketing-*.md
# Expected: 16 files marketing-01-strategy.md to marketing-16-growth-partner.md

# 4. Validar contenido de system prompts
for file in agents/brains/marketing-*.md; do
  echo "Checking $file..."
  grep -q "Your Identity" "$file" || echo "MISSING: Your Identity in $file"
  grep -q "Your Frameworks" "$file" || echo "MISSING: Your Frameworks in $file"
  grep -q "Output Format" "$file" || echo "MISSING: Output Format in $file"
  grep -q "same language as the user" "$file" || echo "MISSING: Language instruction in $file"
done
# Expected: No MISSING messages

# 5. Verificar backward compatibility de brains.yaml
grep -q "niche:" mastermind_cli/config/brains.yaml
# Expected: Field found (existing brains now have niche: software-development)

# 6. Contar expertos en system prompts
grep -h "^\- \*\*" agents/brains/marketing-*.md | wc -l
# Expected: 80+ experts across 16 brains (~5 per brain minimum)

# 7. Test de integración con CLI (opcional)
uv run mm brain list
# Expected: Should show both nichos or indicate multi-niche support
```

---

## Definition of Done

- [ ] `docs/nichos/marketing-digital/sources/` con 16 subdirectorios
- [ ] `mastermind_cli/config/brains.yaml` actualizado con soporte multi-nicho
- [ ] `mastermind_cli/config/brains-marketing.yaml` creado con 16 cerebros
- [ ] 16 system prompts creados en `agents/brains/marketing-*.md`
- [ ] Todos los prompts tienen las 7 secciones requeridas
- [ ] YAML configs validan syntax sin errores
- [ ] Documentación actualizada (PROPUESTA + README)
- [ ] Git commit con cambios
- [ ] **TEST DE COMPLETITUD:** Todos los 16 cerebros tienen system prompt + experts listados + frameworks definidos

---

## Error Handling Strategy

| Error | Acción |
|-------|--------|
| Directorio ya existe | Verificar contenido, continuar si está vacío |
| YAML syntax error | Validar línea por línea, verificar indentación |
| System prompt sin sección requerida | Agregar sección faltante antes de commit |
| brains.yaml rompe backward compatibility | Agregar campo `niche` sin modificar estructura existente |
| Expertos repetidos | Validar que la repetición sea intencional (algunos expertos cubren múltiples dominios) |

---

## Gotchas & Notes

1. **Expertos hispanos NO son obligatorios:** Usar expertos hispanos solo si su conocimiento es relevante. No hay cuota. Calidad > origen.

2. **Repetición de expertos es válida:** Expertos como Hormozi, Jesus Tronchoni, etc. pueden aparecer en múltiples cerebros porque su conocimiento es transversal.

3. **System prompts en inglés:** Esto es intencional para mejor performance de LLMs. El output SIEMPRE será en el idioma del input.

4. **Backward compatibility:** brains.yaml debe seguir funcionando para el nicho Software Development existente.

5. **Cerebro #16 como evaluador:** Similar al Brain #7 de Software Dev, tiene poder de veto sobre outputs de otros cerebros.

6. **notebook_id null:** Intencional en este PRP. Se llenará en PRP-002/003 cuando se creen los notebooks en NotebookLM.

---

## Files Created/Modified

| Archivo | Acción | Propósito |
|---------|--------|-----------|
| `docs/nichos/marketing-digital/sources/` | Crear | Estructura para fuentes maestras |
| `mastermind_cli/config/brains.yaml` | Modificar | Agregar soporte multi-nicho |
| `mastermind_cli/config/brains-marketing.yaml` | Crear | Config de 16 cerebros marketing |
| `agents/brains/marketing-01-strategy.md` | Crear | System prompt cerebro M1 |
| `agents/brains/marketing-02-brand.md` | Crear | System prompt cerebro M2 |
| `agents/brains/marketing-03-content.md` | Crear | System prompt cerebro M3 |
| `agents/brains/marketing-04-social-organic.md` | Crear | System prompt cerebro M4 |
| `agents/brains/marketing-05-social-paid.md` | Crear | System prompt cerebro M5 |
| `agents/brains/marketing-06-search-ppc.md` | Crear | System prompt cerebro M6 |
| `agents/brains/marketing-07-seo-technical.md` | Crear | System prompt cerebro M7 |
| `agents/brains/marketing-08-seo-content.md` | Crear | System prompt cerebro M8 |
| `agents/brains/marketing-09-email.md` | Crear | System prompt cerebro M9 |
| `agents/brains/marketing-10-retention.md` | Crear | System prompt cerebro M10 |
| `agents/brains/marketing-11-analytics.md` | Crear | System prompt cerebro M11 |
| `agents/brains/marketing-12-cro.md` | Crear | System prompt cerebro M12 |
| `agents/brains/marketing-13-ops.md` | Crear | System prompt cerebro M13 |
| `agents/brains/marketing-14-influencer.md` | Crear | System prompt cerebro M14 |
| `agents/brains/marketing-15-community.md` | Crear | System prompt cerebro M15 |
| `agents/brains/marketing-16-growth-partner.md` | Crear | System prompt cerebro M16 (Evaluator) |
| `docs/nichos/marketing-digital/README.md` | Crear | Documentación del nicho |

---

## Next Steps

After this PRP:
- → **PRP-MARKETING-002**: Knowledge Base M1-M8 (~80 fuentes maestras)
- → **PRP-MARKETING-003**: Knowledge Base M9-M16 (~80 fuentes maestras)

---

## Confidence Score

**9/10** - Muy alta confianza de éxito.

**Rationale:**
- Estructura clara y bien definida
- System prompts siguen patrón probado de PRP-003
- YAML config es straightforward
- Validations gates son ejecutables y específicos
- Único riesgo: tiempo estimado puede variar según familiaridad con marketing

---

## Context for AI Agent

**Archivos clave para leer antes de implementar:**
1. `/home/rpadron/proy/mastermind/PRPs/PRP-003-system-prompts.md` - Template de system prompts
2. `/home/rpadron/proy/mastermind/agents/brains/product-strategy.md` - Ejemplo de system prompt
3. `/home/rpadron/proy/mastermind/mastermind_cli/config/brains.yaml` - Estructura YAML existente
4. `/home/rpadron/proy/mastermind/docs/software-development/06-qa-devops-brain/sources/FUENTE-602-accelerate-forsgren-humble-kim.md` - Formato de fuentes (para PRP-002/003)

**Comando para iniciar:**
```bash
cd /home/rpadron/proy/mastermind
# Verificar estructura actual
tree docs/nichos/
ls agents/brains/

# Crear directorios
mkdir -p docs/nichos/marketing-digital/sources/{BRAIN-01-STRATEGY,BRAIN-02-BRAND,BRAIN-03-CONTENT,BRAIN-04-SOCIAL-ORGANIC,BRAIN-05-SOCIAL-PAID,BRAIN-06-SEARCH-PPC,BRAIN-07-SEO-TECHNICAL,BRAIN-08-SEO-CONTENT,BRAIN-09-EMAIL,BRAIN-10-RETENTION,BRAIN-11-ANALYTICS,BRAIN-12-CRO,BRAIN-13-OPS,BRAIN-14-INFLUENCER,BRAIN-15-COMMUNITY,BRAIN-16-GROWTH-PARTNER}
```

**Resultado esperado:**
16 system prompts creados, estructura de directorios lista, configs YAML actualizados, nicho Marketing Digital foundation completo.

**TEST DE COMPLETITUD CRÍTICO:**
```python
# Script de validación post-implementación
import os
import yaml

# 1. Verificar 16 system prompts
prompts = glob.glob("agents/brains/marketing-*.md")
assert len(prompts) == 16, f"Expected 16 prompts, got {len(prompts)}"

# 2. Verificar cada prompt tiene las secciones requeridas
required_sections = ["Your Identity", "Your Purpose", "Your Frameworks", "Your Process", "Your Rules", "Output Format", "Language"]
for prompt in prompts:
    content = open(prompt).read()
    for section in required_sections:
        assert section in content, f"{prompt} missing {section}"

# 3. Verificar brains-marketing.yaml
with open("mastermind_cli/config/brains-marketing.yaml") as f:
    config = yaml.safe_load(f)
    assert len(config["brains"]) == 16, f"Expected 16 brains, got {len(config['brains'])}"

# 4. Verificar 16 directorios de fuentes
source_dirs = glob.glob("docs/nichos/marketing-digital/sources/BRAIN-*")
assert len(source_dirs) == 16, f"Expected 16 source dirs, got {len(source_dirs)}"

print("✅ All completion tests passed!")
```
