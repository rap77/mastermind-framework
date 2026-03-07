---
source_id: "FUENTE-513"
brain: "brain-software-05-backend"
niche: "software-development"
title: "Refactoring: Improving the Design of Existing Code (2nd Edition)"
author: "Martin Fowler, Kent Beck"
expert_id: "EXP-513"
type: "book"
language: "en"
year: 2018
distillation_date: "2026-03-03"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-03"
changelog:
  - version: "1.0.0"
    date: "2026-03-03"
    changes:
      - "Initial distillation from Refactoring 2nd Edition"
status: "active"
---

# Refactoring: Improving the Design of Existing Code

**Martin Fowler, Kent Beck**

## 1. Principios Fundamentales

> **P1 - Refactoring NO es rewriting**: Refactoring es cambiar la estructura del código sin cambiar su comportamiento externo. Es reorganizar, no reconstruir. Si cambias lo que el código hace, no es refactoring.

> **P2 - Tests First, Always**: Nunca refactorices sin una red de seguridad de tests. Si no tienes tests, el refactoring es gambling, no engineering. Los tests son lo que te permite cambiar con confianza.

> **P3 - Two Hats Principle**: Cuando programas, usas dos sombreros: adding new functionality o refactoring. Nunca uses ambos sombreros al mismo tiempo. Cambia de sombrero explícitamente.

> **P4 - Small Steps, Frequent Commits**: Refactoring en pasos pequeños. Cada paso deja el código en un estado working. Commits frecuentes = rollback fácil. El miedo al cambio viene de pasos grandes.

> **P5 - Code Smells son síntomas, no enfermedades**: Un long method no es el problema, es el síntoma de que la lógica no está bien distribuida. Refactoring ataca la causa raíz, no el síntoma superficial.

## 2. Frameworks y Metodologías

### The Refactoring Cycle

```
1. Tests verdes (starting point)
2. Identify code smell
3. Choose refactoring
4. Apply refactoring (small step)
5. Run tests
6. Tests green? → Commit, repeat
   Tests red? → Revert, understand, retry
```

### The Two Hats (Adding vs Refactoring)

| Hat Adding | Hat Refactoring |
|------------|----------------|
| Goal: Add new feature | Goal: Improve structure |
| Tests fail initially | Tests never fail |
| Write code to pass tests | Restructure existing code |
| Commits add functionality | Commits keep behavior |
| Change behavior | Preserve behavior |

**Regla**: One hat at a time, explicitly.

### Refactoring Catalog (Fowler's)

**Category 1: Composing Methods**
- **Extract Method**: Bloque de código → método con nombre descriptivo
- **Inline Method**: Método trivial → eliminar, llamar directamente
- **Extract Variable**: Expression compleja → variable con nombre
- **Inline Temp**: Temp usada una vez → eliminar
- **Replace Temp with Query**: Temp calculada → método que calcula
- **Split Temporary Variable**: Temp usada para múltiples cosas → separar
- **Remove Assignments to Parameters**: Reasignar parámetro → temp variable
- **Replace Method with Method Object**: Método largo con muchas temps → objeto
- **Substitute Algorithm**: Algoritmo complejo → algoritmo más claro

**Category 2: Moving Features Between Objects**
- **Move Method**: Método en clase A → debería estar en clase B
- **Move Field**: Field en clase A → debería estar en clase B
- **Extract Class**: Clase hace demasiado → extraer clase nueva
- **Inline Class**: Clase no hace nada interesante → mover a otra
- **Hide Delegate**: A llama B.method() → A delega a B
- **Remove Middle Man**: Delegación trivial → eliminar中间man
- **Introduce Foreign Method**: Necesitas método en clase que no controlas
- **Introduce Local Extension**: Subclase local para agregar métodos

**Category 3: Organizing Data**
- **Self Encapsulate Field**: Acceso directo → accessor methods
- **Replace Data Value with Object**: Data primitivo → objeto
- **Change Value to Reference**: Objeto duplicado → instancia única
- **Change Reference to Value**: Instancia única → copia inmutable
- **Replace Array with Object**: Array con estructura → objeto con campos
- **Duplicate Observed Data**: Data en GUI → copiar en domain

**Category 4: Simplifying Conditional Expressions**
- **Decompose Conditional**: If/else complejo → métodos
- **Consolidate Conditional Expression**: Mismos conditionals → uno
- **Consolidate Duplicate Conditional Fragments**: Código duplicado en branches
- **Replace Nested Conditional with Guard Clauses**: Anidación → guards
- **Replace Conditional with Polymorphism**: Type codes → subclases
- **Introduce Null Object**: null checks → Null Object
- **Introduce Assertion**: Assumptions → assertions

**Category 5: Simplifying Method Calls**
- **Rename Method**: Nombre no descriptivo → nombre claro
- **Add Parameter**: Método necesita más contexto
- **Remove Parameter**: Parámetro no usado
- **Separate Query from Modifier**: Método que query y modifica → separar
- **Parameterize Method**: Métodos similares que solo difieren en valor
- **Replace Parameter with Explicit Methods**: Parámetro que controla flujo
- **Preserve Whole Object**: Varios parámetros del mismo objeto
- **Replace Parameter with Methods**: Objeto pide dato que puede calcular
- **Introduce Parameter Object**: Grupo de parámetros relacionados → objeto

**Category 6: Dealing with Generalization**
- **Pull Up Method**: Método duplicado en subclases → superclase
- **Push Down Method**: Método en superclase solo usado por algunas subclases
- **Pull Up Field**: Campo duplicado → superclase
- **Push Down Field**: Campo no usado por todas las subclases
- **Extract Subclass**: Clase tiene casos de uso distintos
- **Extract Superclass**: Clases comparten comportamiento
- **Extract Interface**: Clientos solo usan subset de métodos
- **Collapse Hierarchy**: Superclase y subclase casi idénticas
- **Form Template Method**: Subclases tienen mismos pasos, diferente implementación

**Category 7: Big Refactorings**
- **Tease Apart Inheritance**: Clases con responsabilidades múltiples
- **Convert Procedural Design to Objects**: Código procedural → OO
- **Separate Domain from Presentation**: Business logic mezclada con UI
- **Extract Hierarchy**: Case statements con type codes → herencia
- **Simplify Conditional Expressions**: Polymorphism sobre conditionals

### The Key Refactorings (Top 5)

1. **Extract Method** (el más usado)
   - **Cuándo**: Método hace más de una cosa
   - **Cómo**: Bloque de código → nuevo método con nombre descriptivo
   - **Beneficio**: Readability, reusability, overriding

2. **Extract Class**
   - **Cuándo**: Clase tiene demasiadas responsabilidades
   - **Cómo**: Grupo de campos y métodos relacionados → nueva clase
   - **Beneficio**: SRP, testability, cohesion

3. **Replace Conditional with Polymorphism**
   - **Cuándo**: Type codes, switch statements
   - **Cómo**: Cada type → subclase con behavior override
   - **Beneficio**: Elimina conditionals, extensible

4. **Decompose Conditional**
   - **Cuándo**: If/else complejo
   - **Cómo**: Condition → methods con nombres descriptivos
   - **Beneficio**: Readability, testability

5. **Introduce Parameter Object / Preserve Whole Object**
   - **Cuándo**: Demasiados parámetros, grupos de parámetros relacionados
   - **Cómo**: Parámetros → objeto que los contiene
   - **Beneficio**: Evolutive, claro

## 3. Modelos Mentales

### Modelo de "Technical Debt"

**Metáfora financiera**:
- **Principal**: Código mal diseñado
- **Interest**: Cada cambio es más difícil
- **Refactoring**: Pagar deuda
- **No refactoring**: Interés compuesto → sistema inmanejable

**Cuándo pagar deuda**:
- **Strategic debt**: Correcto en su momento, el contexto cambió
- **Accidental debt**: Atajos por deadlines, corregir ASAP

### Modelo de "Entropy in Software"

**Second Law of Thermodynamics aplicada al código**:
- Los sistemas tienden al desorden
- Sin energía (refactoring), la entropía aumenta
- Refactoring = energía invertida para mantener orden

**Manifestación**:
- Código nuevo = limpio
- Sin refactor → enredado, duplicado, confuso
- Con refactor → código mantenible por años

### Modelo de "Refactoring as Risk Mitigation"

**Paradoja**:
- Refactoring cambia código → podría introducir bugs
- NO refactorizar → bugs son más difíciles de encontrar

**Solución**:
- Tests de regresión = red de seguridad
- Cambios pequeños = rollback fácil
- Commits frecuentes = time travel

### Modelo de "Code as Communication"

**Dos audiencias**:
1. **Máquina**: Compilador, runtime
2. **Humanos**: Future you, teammates

**Refactoring optimiza para humanos**:
- La máquina no le importa si el código es bonito
- Los humanos SÍ les importa
- Código bien refactorizado → comunicación clara

## 4. Criterios de Decisión

### When to Refactor

| ✅ Refactor cuando | ❌ No refactorices cuando |
|---------------------|---------------------------|
| Regla de tres (tercera vez) | deadline inminiente sin tests |
| Adds new feature (opportunistic) | Código legacy sin tests (escribe tests primero) |
| Fixing bug (understand context) | Performance hotspot (premature optimization) |
| Code review (continuous improvement) | API pública (breaking changes) |
| Before/after adding feature | Código a ser reemplazado pronto |

### Rule of Three

1. **First time**: Just do it
2. **Second time**: Wince, but do it anyway
3. **Third time**: Refactor

**Aplica a**:
- Duplicated code
- Similar logic in multiple places
- Patterns that repeat

### Refactoring vs Rewriting

| Aspecto | Refactoring | Rewriting |
|---------|-------------|-----------|
| Approach | Cambio incremental | Cambio radical |
| Risk | Bajo (tests protegen) | Alto (nuevo código) |
| Time | Pequeños steps | Large upfront |
| Learning | Continuo | Todo al final |
| Cuándo usar | Siempre es la primera opción | Cuando refactoring es imposible |

**Rewriting cuando:**
- Arquitectura fundamentalmente incorrecta
- Technology stack deprecated
- Refactoring cost > rewrite cost (raro)

### Refactoring Depth

| Superficial | Medium | Deep |
|-------------|--------|------|
| Rename variables, extract methods | Extract classes, introduce abstractions | Change architecture, extract subsystems |
| Minutos | Horas | Días-semanas |
| Bajo riesgo | Riesgo medio | Riesgo alto (más tests) |

**Regla**: Start shallow, go deep as needed.

### Code Smells (When to Act)

| Smell | Severity | Action |
|-------|----------|--------|
| **Duplicated code** | Alta | Extract method/class immediately |
| **Long method** | Media | Extract method opportunistically |
| **Large class** | Alta | Extract class soon |
| **Long parameter list** | Media | Introduce parameter object |
| **Divergent change** | Alta | Extract class |
| **Shotgun surgery** | Alta | Move method/field, inline class |
| **Feature envy** | Media | Move method |
| **Data clumps** | Baja | Extract class/value object |
| **Primitive obsession** | Media | Replace with object |
| **Switch statements** | Media | Replace with polymorphism |
| **Temporary field** | Media | Extract class |
| **Message chains** | Baja | Hide delegate |
| **Middle man** | Baja | Inline class or remove delegation |
| **Inappropriate intimacy** | Media | Move methods, extract class |
| **Alternate classes** | Media | Extract superclass |
| **Lazy class** | Baja | Inline class |
| **Speculative generality** | Baja | Remove abstraction |
| **Mysterious name** | Alta | Rename immediately |

## 5. Anti-patrones

### Anti-patrón: "Refactoring without Tests"

**Problema**: Cambiar código sin tests = gambling.

**Solución:**
- Si el código no tiene tests, escribirlos primero
- "Characterization tests": Tests que describen comportamiento actual
- Luego refactorizar

### Anti-patrón: "Big Bang Refactoring"

**Problema**: Intentar refactorizar todo en un giant commit.

**Solución:**
- Refactor en pasos pequeños
- Cada paso es commit reversible
- Strangler pattern:新旧并存, gradual migration

### Anti-patrón: "Premature Refactoring"

**Problema**: Refactorizar código que todavía está evolucionando rápidamente.

**Solución:**
- Make it work, then make it right, then make it fast
- No over-refactor early code
- Refactor cuando el patrón es claro

### Anti-patrón: "Refactoring for Performance"

**Problema**: Cambiar estructura por optimización prematura.

**Solución:**
- First make it right, then make it fast
- Profile before optimizing
- Most readable code is fast enough

### Anti-patrón: "Refactoring Public API"

**Problema**: Cambiar interfaces públicas afecta consumers.

**Solución:**
- Refactor internamente, mantener API estable
- Si API debe cambiar: deprecate first, remove later
- Semantic versioning: Breaking changes = major version bump

### Anti-patrón: "Refactoring by Committee"

**Problema**: Team no está de acuerdo en direction.

**Solución:**
- Refactor es trabajo técnico, no philosophical
- Pair programming para agreement
- Si no hay acuerdo: spike both approaches, compare

### Anti-patrón: "Golden Master (Hate Testing)"

**Problema**: "No puedo escribir tests, es legacy code."

**Solución:**
- Characterization tests primero
- Hacen el comportamiento actual explícito
- Luego refactorizar con confianza

### Anti-patrón: "YAGNI Refactoring"

**Problema**: Crear abstracciones para un "future que nunca llega".

**Solución:**
- Refactor cuando hay un need actual
- No por "best practices" abstractas
- Three times rule apply

### Anti-patrón: "Refactoring Tools Do It For Me"

**Problema**: IDE auto-refactor sin entender.

**Solución:**
- Tools assist, don't replace understanding
- Lee el code diff
- Understand what the refactor did

### Anti-patrón: "Refactoring as Excuse for Rework"

**Problema**: "I'm refactoring" pero realmente estás changing functionality.

**Solución:**
- Two hats: Adding vs Refactoring
- Refactor NO cambia behavior
- Add feature AND refactor → dos commits separados
