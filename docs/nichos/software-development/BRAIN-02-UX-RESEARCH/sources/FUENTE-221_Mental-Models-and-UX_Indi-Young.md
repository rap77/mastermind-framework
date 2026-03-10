---
source_id: "FUENTE-221"
brain: "brain-software-02-ux-research"
niche: "software-development"
title: "Mental Models: Aligning Design Strategy with Human Behavior"
author: "Indi Young"
expert_id: "EXP-221"
type: "book"
language: "en"
year: 2017
distillation_date: "2026-03-03"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-03"
changelog:
  - version: "1.0.0"
    date: "2026-03-03"
    changes:
      - "Initial distillation from Mental Models"
status: "active"
---

# Mental Models: Aligning Design Strategy with Human Behavior

**Indi Young**

## 1. Principios Fundamentales

> **P1 - Los mental models son cómo la gente entiende el mundo, no cómo el mundo realmente es**: Un usuario tiene un modelo mental de cómo funciona tu producto que puede estar completamente equivocado. Diseñar para el modelo real sin entender el modelo mental es diseñar para fallos. Primero entiende cómo ellos creen que funciona.

> **P2 - La empatía cognitiva es la herramienta de investigación más importante**: No basta con observar behavior. Necesitas entender el reasoning detrás del behavior. ¿Qué creen los usuarios que está pasando? ¿Qué analogías usan? ¿Qué suposiciones hacen? Ese es el modelo mental.

> **P3 - Los modelos mentales son degradaciones deliberadas de la complejidad**: La gente no puede modelar toda la complejidad de un sistema. Crean simplificaciones que funcionan "bien suficiente". Diseñar es facilitar estas degradaciones, no exponer toda la complejidad.

> **P4 - Hay dos tipos de conocimiento: el que la gente puede articular y el que es tácito**: Las entrevistas típicas capturan knowledge explícito. Pero gran parte del conocimiento es tácito — cosas que la gente hace sin poder explicar por qué. La observación contextual revela conocimiento tácito.

> **P5 - Los modelos mentales evolucionan con la experiencia**: Los usuarios novatos tienen modelos mentales diferentes de los expertos. El diseño debe acomodar ambos, o facilitar la transición de novice a expert. No puedes diseñar solo para expertos si quieres crecimiento.

## 2. Frameworks y Metodologías

### Understanding Mental Models

**Definition**: Un modelo mental es una representación interna de cómo funciona algo.

**Example**: Email model
```
Novice model:
Email = Physical mail on computer
- Inbox = Desktop
- Archive = Filing cabinet

Expert model:
Email = Database with search + tags
- Inbox = Unprocessed items
- Archive = Everything is searchable
```

**Design implication**: Si diseñas para expert model (search-based), users con novice model se perderán.

### Researching Mental Models

**1. Diener Interview Method**
- "Walk me through the last time you X"
- "What were you expecting?"
- "How did you figure out what to do?"

**2. Concept Mapping**
- Dibuja cómo el usuario cree que funciona el sistema
- Identifica gaps entre user model y system model
- Revela analogías usadas

**3. Shadowing**
- Observa users en contexto real
- Nota qué hacen sin pensar (tácito)
- Nota dónde se confunden, se frustran

**4. Artifact Analysis**
- Pide a users que dibujen cómo funciona algo
- Revela modelos mentales visuales
- Mostran analogías inesperadas

### The Gap Analysis

```
System Model (cómo funciona realmente)
Mental Model (cómo el usuario cree que funciona)
    ↓
    Gap → Friction, confusion, errors
```

**Design goal**: Bridge the gap alinear diseño con modelo mental.

### Types of Mental Models

**1. Structural Models**
- Cómo está organizado el sistema
- "Settings are in the menu"

**2. Causal Models**
- Cómo A afecta B
- "If I click this, X happens"

**3. Process Models**
- El flujo para lograr un objetivo
- "To buy: search → select → pay"

**4. Conceptual Models**
- Qué es X, cómo se relaciona con Y
- "Tags are like folders but items can have multiple"

### Conceptual Models in Design

**Direct Manipulation** (Don Norman):
- La interfaz se siente como el objeto real
- El modelo mental coincide con la interfaz
- Ej: Delete file → arrastrar a papelera

**Conversation** (las interfaces conversan):
- Los bots chat son conversationales
- El modelo mental = talking to someone

### Model-Metaphor Mismatch

```
System Metaphor      User Mental Model    Result
━━━━━━━━━━━━━━━━━━    ━━━━━━━━━━━━━━━━━   ━━━━━━━
Desktop metaphor     Documents live in     Confusion
(Folders, files)     "The Cloud"

Database metaphor     Spreadsheet model      Frustration
(Sheets, queries)    "Just like Excel"
```

**Design implication**: Alinéate metaphor con user expectations.

## 3. Modelos Mentales

### Modelo de "Schemas" (Cognitive Psychology)

```
Schema = Mental structure que organiza conocimiento
```

**Examples**:
- Restaurant schema: menú, mesero, comida, cuenta
- Email schema: bandeja de entrada, enviar, recibir

**Activation**: Los schemas se activan con context cues.
**Design implication**: Usa metáforas familiares que activen schemas existentes.

### Modelo de "Analogical Reasoning"

```
Source → Target
    ↓
Transfer relationships
    ↓
Understanding target via source
```

**Example**: "Email is like postal mail"
- Enviar email → enviar carta
- Buzón de entrada → casilla física
- Archivo → archivo muerto

**Design implication**: Usa analogías familiares para explicar conceptos complejos.

### Modelo de "Progressive Disclosure of Complexity"

```
Novice user → Simple model
    ↓ (learning)
Advanced user → More complex model
    ↓ (learning)
Expert user → Complete model (may still have gaps)
```

**Design implication**: Don't expose everything at once.

### Modelo de "Mental Model Evolution"

```
Initial Mental Model (formed before using product)
    ↓ (usage)
Revised Mental Model (based on experience)
    ↓ (more usage)
Refined Mental Model (more accurate)
```

**Design implication**: Onboarding should shape initial mental model intentionally.

## 4. Criterios de Decisión

### When to Research Mental Models

| ✅ Research mental models when | ❌ May not need when |
|-----------------------------------|----------------------|
| Complex, multi-step workflows | Simple, one-click actions |
| New product category | Established patterns (email, file system) |
- High user confusion/complaints | Low friction, intuitive behavior |

### Conceptual Model Alignment

| Aligned | Misaligned |
|----------|------------|
| User expectations match system | Surprise/confusion |
| Familiar metaphors | Novel metaphors |
| Consistent with prior experience | Inconsistent, breaks mental models |

### Metaphor Selection

| Good Metaphor | Bad Metaphor |
|---------------|-------------|
| Shopping cart (e-commerce) | Shopping cart (file management) |
| Folders (file system) | Layers (file system) |
| Friends/Connections (social network) | Circles (confusing) |

### Progressive Disclosure Strategy

| Novice | Intermediate | Expert |
|---------|------------|--------|
| Simple interface | Advanced options available | Full control |
| Guided flows | Shortcuts | Customization |
| Defaults | Choice | Power tools |

## 5. Anti-patrones

### Anti-patrón: "Designing for the Ideal User"

**Problema**: Asumiendo que todos los usuarios piensan igual.

**Solution**:
- Research diversity of mental models
- Accommodate multiple models if possible
- At least understand the dominant model

### Anti-patrón: "Modeling the System Instead of the User"

**Problema**: Exponiendo la arquitectura interna en la UI.

**Solution**:
- User mental model > System architecture
- Abstract complexity
- Model user's conceptual model, not system internals

### Anti-patrón: "Ignoring Mental Model Evolution"

**Problema**: Diseñando como si el usuario siempre será novato.

**Solution**:
- Support novice → expert journey
- Progressive disclosure of features
- Learning opportunities

### Anti-patrón: "Changing Mental Models Without Warning"

**Problema**: Rediseño que rompe modelo mental existente.

**Solution**:
- Understand current mental model first
- If changing, guide users carefully
- Use migration paths, onboarding

### Anti-patrón: "Over-Reliance on Analogies"

**Problema**: Analogías que se rompen en edge cases.

**Solution**:
- Use analogies as scaffolding, not permanent
- Be clear about where analogy breaks down
- Eventually, users form direct models

### Anti-patrón: "Single Mental Model Assumption"

**Problema**: Asumiendo un único modelo mental.

**Solution**:
- Recognize multiple user segments may have different models
- Test with diverse users
- Consider personas and their varied experiences

### Anti-patrón: "Mental Model Without User Testing"

**Problema**: Asumiendo modelo mental sin research.

**Solution**:
- Research to discover actual mental models
- Test designs with real users
- Iterate based on feedback

### Anti-patrón: "Ignoring Tacit Knowledge"

**Problema**: Solo capturando explícito "what users say".

**Solution**:
- Observe behavior (tacit knowledge)
- Contextual inquiry reveals what users do without thinking
- Watch for workarounds that reveal mental models
