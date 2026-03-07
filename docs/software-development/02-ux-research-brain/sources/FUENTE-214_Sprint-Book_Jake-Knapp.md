---
source_id: "FUENTE-214"
brain: "brain-software-02-ux-research"
niche: "software-development"
title: "Sprint: How to Solve Big Problems and Test New Ideas in Just Five Days"
author: "Jake Knapp, John Zeratsky, Braden Kowitz"
expert_id: "EXP-214"
type: "book"
language: "en"
year: 2016
distillation_date: "2026-03-03"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-03"
changelog:
  - version: "1.0.0"
    date: "2026-03-03"
    changes:
      - "Initial distillation from Sprint Book"
status: "active"
---

# Sprint: How to Solve Big Problems and Test Ideas in Just Five Days

**Jake Knapp, John Zeratsky, Braden Kowitz (Google Ventures)**

## 1. Principios Fundamentales

> **P1 - La velocidad reduce el riesgo**: Pasar meses en una idea que nadie quiere es el mayor riesgo. Un sprint de 5 días reduce meses de debate a días de aprendizaje.

> **P2 - El proceso protege del ego**: Cuando todos tienen ideas, el "mejor orador" suele ganar. El sprint estructura el proceso para que la mejor idea gane, no la más ruidosa.

> **P3 - Construir para aprender, no para terminar**: El prototipo del sprint no es el producto. Es un vehículo para aprender si vale la pena construir el producto real.

> **P4 - La decisión se hace el viernes**: No se toma una decisión grande sin data. El sprint genera data real de usuarios reales para informar decisiones informadas.

> **P5 - Todo el mundo en la misma habitación**: Cuando stakeholders, designers, devs, y PMs trabajan juntos 5 días, se comprime meses de email y meetings en una semana de foco intenso.

## 2. Frameworks y Metodologías

### The 5-Day Sprint Schedule

#### Monday: Map and Sketch
**Mañana:**
- **Long-term goal** (10 años): ¿Qué tipo de mundo queremos crear?
- **Sprint questions** (This sprint): ¿Qué necesitamos responder?
- **Make a map**: El flujo del usuario de principio a fin
- **Ask the experts**: Cada experto comparte contexto (15 min cada uno)
- **Target**: Elegir un objetivo foco del sprint

**Tarde:**
- **Lightning demos**: 20 min sketching inspiración de productos existentes
- **Sketch**: 8-step process para crear soluciones
  1. Notes: 20 min — capturar ideas
  2. Ideas: 20 min — messy concepts
  3. Crazy 8s: 8 min — 8 sketches en 8 minutos
  4. Storyboard: 30-60 min — flujo detallado
  5. Silent review: Revisar todos los sketches

#### Tuesday: Decide and Storyboard
**Mañana:**
- **Review**: Todos los sketches colgados en la pared
- **Heat maps**: Team pone puntos en ideas que les gustan
- **Speed critique**: 3 min por sketch → explicación y feedback
- **Straw poll**: Cada persona vota por su favorito (supervotes x3)
- **Decide**: Decisor final elige la dirección (puede combinar)

**Tarde:**
- **Storyboard**: Crear storyboard detallado del prototype
- Frame-by-frame del flujo del usuario
- Incluir copy, botones, transiciones

#### Wednesday: Prototype
**Regla**: Fake it till you make it.
- **Tools**: Keynote, PowerPoint, Figma, paper & cardboard
- **Realista en apariencia, no en funcionalidad**
- **No-code**: El prototype es theater, no engineering

**Tipos de prototypes:**
- **Mockup**: Screens estáticas con navegación simulada
- **Wizard of Oz**: Parece real, humanos detrás del telón
- **Video**: Scenarios grabados con screencasts o sketches

#### Thursday: Test
**Mañana:**
- **Setup**: 5 entrevistas con usuarios reales
- **Script**: 5 preguntas clave a responder
- **Team**: 5 roles: interviewer, note taker, timer, greeter, observers

**Tarde:**
- **Debrief**: Equipo comparte insights
- **Patterns**: Qué aprendimos de los 5 usuarios
- **Data**: Frases literales, comportamientos observados

**Team roles durante entrevista:**
- **Interviewer**: Facilita, pregunta "why", no explica
- **Note taker**: Captura quotes y observaciones
- **Timer**: Mantiene on track (45 min)
- **Greeter**: Welcome participant, paper work
- **Observers**: Toman notas silenciosas

#### Friday: Learn and Decide
**Mañana:**
- **Share insights**: Patterns de los 5 usuarios
- **Vote on themes**: ¿Qué emergió consistently?
- **Decision**: Go / No-Go / Pivot / Another Sprint

**Tarde:**
- **Next steps**: Si Go → planning de desarrollo real
- **If No-Go**: ¿Por qué? ¿Qué probamos después?

### The 8-Step Sketch Process (Monday PM)

1. **Notes** (20 min): Capturar ideas sin editar
2. **Mind map** (opcional): Organizar thoughts visualmente
3. **Crazy 8s** (8 min): 8 sketches, 1 min cada uno
4. **Sketch** (30-60 min): Storyboard detallado de una solución
5. **Silent review**: Todos revisan todos los sketches

**Reglas:**
- **No hablar**: Todos sketchean en paralelo
- **Timeboxed**: Constraints breed creativity
- **Quantity over quality initially**: Crazy 8s = ideas
- **Final sketch = quality**: Storyboard detallado

### Decision Framework

| Nivel | Quién decide | Cómo |
|-------|-------------|-----|
| **Team voting** | Todos (votes) | Straw poll identifica favoritos |
| **Decisor** | CEO / PM / Stakeholder | Elige final, puede combinar |

**Si no hay decisor claro**:
- Team vote determina dirección
- Pero esto es menos ideal

### Interview Script Template

**5 Questions:**
1. **Context**: ¿Qué problemas tienes con [domain]?
2. **Current**: ¿Cómo resuelves esto hoy?
3. **Reaction**: ¿Qué opinas de [solution]?
4. **Magic wand**: ¿Qué cambiarías?
5. **Value**: ¿Pagarias por esto? ¿Cuánto?

**No demos, no explanations**: Deja que el usuario descubra.

### The "Super Vote" Rule

- Cada persona tiene votos = team size - 1
- Un voto = un punto
- Un "super vote" = 3 puntos (tienes 1 super vote)
- Uso: Cuando estás realmente convencido

## 3. Modelos Mentales

### Modelo de "Team as Bottleneck"

**Problema típico:**
- PM: "Quiero specs"
- Design: "Quiero claridad"
- Dev: "Quiero tickets"
- Result: Gridlock, months de debate

**Sprint solution:**
- Todos en la misma habitación 5 días
- Comprimir months → weeks
- Shared understanding emerges

### Modelo de "Building the Wrong Thing Fast"

**Risk**: Construir rápido lo incorrecto = waste

**Sprint mitigación:**
- Antes de escribir una línea de código real, validamos
- Prototype = learning vehicle
- Friday decision = data-driven

### Modelo de "Hi-Res vs Lo-Res Thinking"

| Lo-Res (Early Sprint) | Hi-Res (Late Sprint) |
|-----------------------|----------------------|
| Broad strokes | Pixels perfect |
| Conceptual | Detailed |
| Sketches | Prototype |
| Brainstorming | Testing |

**Sprint empieza lo-res, termina hi-res.**

### Modelo de "Best Idea Wins"

**Problema**: En meetings, el orador más carismático / ruidoso suele persuadir.

**Sprint solution:**
- Silent sketching → todos tienen voz
- Anonimato de sketches → no bias por autor
- Voting system → best idea, not loudest

## 4. Criterios de Decisión

### When to Run a Sprint

| ✅ Good for | ❌ Not for |
|-------------|------------|
| New product idea | Incremental feature tweak |
| Big strategic shift | Technical refactoring |
| Solving a stuck problem | Adding a simple button |
| Testing risky hypothesis | Improving existing metrics |
| Team alignment needed | One-person decision |
| < 6 months horizon | > 2 years horizon |

### Team Size and Composition

| Role | Ideal | Minimum | Maximum |
|------|-------|---------|----------|
| **Decisor** | 1 | 1 | 1 |
| **Facilitator** | 1 | 1 | 1 |
| **Designers** | 2 | 1 | 3 |
| **PMs** | 2 | 1 | 3 |
| **Devs** | 2 | 1 | 3 |
| **Total** | 7 | 4 | 8 |

**Too small** (< 4): Falta diversidad de perspectivas
**Too big** (> 8): Logística difícil, voices lost

### In-Person vs Remote Sprint

| In-Person | Remote |
|-----------|---------|
| Energy alta, colaboración orgánica | Logistics compleja, timezone hell |
| Whiteboards, post-its tangibles | Miro, Figma, Slack fatigue |
| Serendipitous conversations | Structured only |
| ✅ Best for complex problems | ⚠️ Possible but harder |

**Remote sprint adaptations:**
- Miro/FigJam for mapping
- Breakout rooms for sketching
- Strict timekeeping with shared timers

### Go / No-Go Decision Matrix

| Evidence | Go | Pivot | No-Go |
|----------|-----|-------|-------|
| **Users excited** | ✅ 4-5/5 | ⚠️ 2-3/5 | ❌ 0-1/5 |
| **Flows naturally** | ✅ Yes | ⚠️ Some friction | ❌ Confusing |
| **Value clear** | ✅ "When can I get it?" | ⚠️ "Maybe..." | ❌ "I wouldn't use it" |
| **Tech feasible** | ✅ Yes | ⚠️ Hard but doable | ❌ Impossible |

**Decision is binary but nuanced**:
- Go → Build real product
- Pivot → Another sprint with new direction
- No-Go → Kill idea, move to next

### Prototype Fidelity

| Prototype Type | When to Use | Tools |
|----------------|-------------|-------|
| **Paper sketches** | Monday-Tuesday exploration | Pen, paper, sticky notes |
| **Clickthrough mockup** | Most common | Keynote, Figma, Adobe XD |
| **Video prototype** | Hardware, physical product | Video editing, screen recording |
| **Wizard of Oz** | AI, complex backend | Humans behind interface |

**Rule**: Fake it until you learn it.

## 5. Anti-patrones

### Anti-patrón: "Waterfall Sprint"

**Problema**: Usar sprint para planificar, no para aprender.

**Solución:**
- Sprint = discovery, not planning
- Output = learning, not Gantt chart
- Decision on Friday is based on data, not speculation

### Anti-patrón: "Prototype as Product"

**Problema**: Teams fall in love with prototype, try to ship it.

**Solución:**
- Prototype is disposable
- It's a vehicle for learning, not the product
- Kill your darlings after Friday

### Anti-patrón: "Decisor by Committee"

**Problema**: Trying to decide by consensus = no decision.

**Solución:**
- One decisor has final say
- Team informs, decisor decides
- Democracy in ideas, autocracy in decision

### Anti-patrón: "Sprint for Everything"

**Problema**: Using sprints for trivial decisions or incremental work.

**Solución:**
- Not every problem needs a sprint
- Use for big bets, risky ideas, stuck problems
- For small improvements: just do it

### Anti-patrón: "Testing with Friends"

**Problema**: Testing with team members, friends, or colleagues.

**Solución:**
- Recruit real users from target audience
- Incentivize participation ($50-100 gift card)
- Stranger's feedback is honest, friends lie

### Anti-patrón: "Skipping Friday"

**Problema**: After building prototype, team skips testing.

**Solución:**
- No testing = no learning
- Why build prototype if you won't test it?
- Thursday without Friday = wasted Wednesday

### Anti-patrón: "Focusing on Solution, Not Problem"

**Problema**: Sprint starts with "let's build X feature" without understanding problem.

**Solución:**
- Monday AM = problem framing
- Start with long-term goal and sprint questions
- Problem first, solution second

### Anti-patrón: "Design by Committee"

**Problema**: Combining all ideas into Franken-feature.

**Solución:**
- Tuesday decide = pick ONE direction
- A clear, cohesive solution > muddled compromise
- Better to be wrong and clear than vague and safe
