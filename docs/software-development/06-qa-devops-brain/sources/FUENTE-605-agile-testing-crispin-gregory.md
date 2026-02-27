---
source_id: "FUENTE-605"
brain: "brain-software-06-qa-devops"
niche: "software-development"
title: "Agile Testing: A Practical Guide for Testers and Agile Teams"
author: "Lisa Crispin, Janet Gregory"
expert_id: "EXP-605"
type: "book"
language: "en"
year: 2009
isbn: "978-0321534460"
url: "https://lisacrispin.com/agile-testing-book/"
skills_covered: ["H3"]
distillation_date: "2026-02-27"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-02-27"
changelog:
  - version: "1.0.0"
    date: "2026-02-27"
    changes:
      - "Ficha creada con destilación completa"
      - "Formato estándar del MasterMind Framework"
status: "active"

habilidad_primaria: "QA integrado en procesos ágiles: testing como actividad del equipo completo"
habilidad_secundaria: "Estrategia de testing con los 4 cuadrantes y diseño de tests basados en historias de usuario"
capa: 2
capa_nombre: "Frameworks"
relevancia: "ALTA — Define cómo integrar QA de forma orgánica en equipos ágiles. El cuadrante de testing es el framework más usado en la industria para clasificar y planificar la estrategia de testing. Esencial para equipos que quieren ir más allá del testing reactivo."
---

# FUENTE-605: Agile Testing

## Tesis Central

> En equipos ágiles, el testing no es una fase separada al final del desarrollo: es una actividad continua que todo el equipo realiza. El QA no es el "guardián de la calidad" sino el facilitador que ayuda al equipo a construir calidad desde el inicio. La calidad es responsabilidad de todos, y el testing comienza cuando se define la historia de usuario, no cuando el código está terminado.

---

## 1. Principios Fundamentales

> **P1: "Testing is not a phase, it's a mindset"**
> En Waterfall, testing es la última fase. En Agile, testing es una actividad continua que comienza con la definición del requisito. Si el equipo espera a que el desarrollador "termine" para que el QA "empiece", están haciendo Waterfall con sprint boundaries.
> *Contexto: Aplica a la definición de qué hace el QA durante el sprint: participar en el refinamiento, escribir criterios de aceptación, testear features en paralelo con el desarrollo.*

> **P2: Whole-team approach: la calidad es responsabilidad de todo el equipo**
> El QA no es el único responsable de la calidad. El desarrollador es responsable de construir código testeable con unit tests. El product owner es responsable de criterios de aceptación claros. El QA facilita y colabora, pero no puede asegurar calidad solo.
> *Contexto: Aplica al hacer retrospectivas sobre bugs en producción. Si el QA es el único responsable de los bugs que se escapan, el modelo está roto.*

> **P3: Testing confirma entendimiento compartido, no solo detecta bugs**
> Antes de que se escriba el código, los criterios de aceptación de una historia de usuario son hipótesis sobre qué debe hacer el sistema. El testing no es buscar bugs: es verificar que el equipo entendió el problema de la misma forma que el negocio.
> *Contexto: Aplicar en las sesiones de "Three Amigos" (BA, developer, QA): revisar las historias juntos antes de que empiece el sprint para asegurar entendimiento compartido.*

> **P4: Automatizar el testing de regresión, explorar manualmente lo nuevo**
> Los tests de regresión (lo que ya funcionaba debe seguir funcionando) deben ser automáticos: son lentos y aburridos de hacer manualmente, y se necesitan en cada sprint. El testing exploratorio (descubrir comportamientos inesperados en features nuevas) debe ser manual: requiere creatividad y contexto humano.
> *Contexto: Al decidir qué automatizar, preguntar: ¿este test necesitará correr en cada sprint? Si sí → automatizar. ¿Este test requiere intuición y exploración? → manual.*

> **P5: El ambiente de testing debe estar listo antes de que comience el sprint**
> Si el ambiente de QA no está disponible al inicio del sprint, los developers completan features pero el QA no puede testear. Esto crea un cuello de botella al final del sprint. La disponibilidad del ambiente es parte de la Definition of Ready del sprint.
> *Contexto: Incluir la preparación del ambiente de test como tarea en el sprint de planificación. Los developers también son responsables de preparar datos y configuraciones de test.*

---

## 2. Frameworks y Metodologías

### Framework 1: Los 4 Cuadrantes de Testing Ágil

**Propósito:** Clasificar todos los tipos de tests en una matriz que ayuda a planificar qué necesita el equipo y en qué proporción.
**Cuándo usar:** Al planificar la estrategia de testing de un proyecto; al hacer una retrospectiva de QA ("¿qué tipos de testing estamos descuidando?")

**La Matriz (Business-Facing vs. Technology-Facing × Supporting the team vs. Critiquing the product):**

```
                    BUSINESS-FACING
                         │
         Q2              │              Q3
  ┌─────────────────────┼─────────────────────┐
  │  Functional tests   │  Exploratory testing│
  │  Examples           │  Usability testing  │
  │  Story tests        │  User acceptance    │
  │  Prototypes         │  Alpha/Beta tests   │
  │  Simulations        │                     │
  │ (Automated & manual)│ (Mostly manual)     │
  ├─────────────────────┼─────────────────────┤
         Q1              │              Q4
  │  Unit tests         │  Performance        │
  │  Component tests    │  Security tests     │
  │  (Automated)        │  "ility" tests      │
  │                     │  (Tools)            │
  └─────────────────────┴─────────────────────┘
       TECHNOLOGY-FACING
  ←─ Supporting the team ─── Critiquing the product ─→
```

**Cuadrante 1 — Technology-facing, Supporting the team:**
- Unit tests, component tests
- Escritos y ejecutados por developers
- Automáticos, rápidos, el pilar de la Test Pyramid
- Objetivo: asegurar que el código funciona a nivel técnico

**Cuadrante 2 — Business-facing, Supporting the team:**
- Functional tests basados en criterios de aceptación
- Escritos con el product owner, ejecutados automáticamente
- Objective: asegurar que el sistema hace lo que el negocio necesita
- Ejemplo: BDD tests con Gherkin/Cucumber

**Cuadrante 3 — Business-facing, Critiquing the product:**
- Testing exploratorio, usability, UAT
- Manual, requiere creatividad y contexto de usuario
- Objetivo: descubrir problemas que la automatización no puede anticipar
- Cuando hacer: en cada sprint para features nuevas

**Cuadrante 4 — Technology-facing, Critiquing the product:**
- Performance testing, security testing, tests de "-ilities"
- Con herramientas especializadas (JMeter, OWASP ZAP, etc.)
- Objetivo: validar que el sistema cumple requisitos no-funcionales
- Cuándo hacer: regularmente, más intensivo antes de releases mayores

**Output esperado:** Mapa de qué tipos de testing existen en el proyecto y cuáles están descuidados.

---

### Framework 2: Three Amigos y Acceptance Criteria como Tests

**Propósito:** Definir los criterios de aceptación de una historia de usuario de forma que sean directamente convertibles en tests automáticos.
**Cuándo usar:** En el refinamiento del backlog antes de cada sprint.

**Proceso Three Amigos:**

1. **Reunir a los tres:** Product Owner (o BA), Developer, QA. Sin más, sin menos.

2. **El PO presenta la historia:** "Como usuario quiero X para poder Y"

3. **Elicitar ejemplos concretos (no reglas abstractas):**
   - En lugar de: "El sistema debe validar el email"
   - Mejor: "Si ingreso 'juan@' el sistema muestra 'Email inválido'. Si ingreso 'juan@empresa.com' el registro procede."
   - Los ejemplos son los tests antes de que exista el código.

4. **Formato Given-When-Then (BDD):**
   ```
   Given: el usuario está en el formulario de registro
   When: ingresa 'juan@' en el campo email y hace click en Registrar
   Then: el sistema muestra el mensaje "Email inválido" debajo del campo
   And: el formulario no se envía
   ```

5. **El QA agrega los edge cases:** ¿Qué pasa si el email ya existe? ¿Si está vacío? ¿Si tiene espacios?

6. **El Developer confirma viabilidad técnica:** ¿Es esto posible con la arquitectura actual? ¿Hay limitaciones?

**Output esperado:** Lista de escenarios Given-When-Then listos para convertirse en tests automatizados o manuales. Cero ambigüedad sobre qué debe hacer la historia.

---

## 3. Modelos Mentales

| Modelo | Descripción | Aplicación Práctica |
|--------|-------------|---------------------|
| **Testing como red de seguridad, no como inspección** | Los tests no son para detectar que el código está mal (inspección reactiva). Son para dar confianza de que el sistema funciona (red de seguridad proactiva). Esta diferencia cambia cómo se piensa en el testing. | Al justificar inversión en testing, no usar el argumento "para encontrar bugs." Usar: "para poder desplegar con confianza y cambiar el código sin miedo a romper algo." |
| **Test-first como diseño, no solo como verificación** | Escribir el test antes del código (TDD o BDD) fuerza a pensar en el diseño de la API o función desde la perspectiva del usuario, no del implementador. Resulta en APIs más simples y código más testeable. | Al implementar una feature compleja, escribir primero el test de aceptación (Given-When-Then) para clarificar qué debe hacer antes de pensar en cómo implementarlo. |
| **El QA como explorador, no como ejecutor de scripts** | Los mejores QAs no ejecutan test cases de un script predefinido: exploran el sistema buscando comportamientos inesperados. Su valor está en la intuición y creatividad, no en la ejecución mecánica. | El testing exploratorio basado en charter (objetivo + tiempo) es más efectivo que los test cases escritos: "En 45 minutos, explorar el flujo de pago con tarjetas internacionales buscando problemas de validación de moneda." |
| **Definition of Done incluye tests** | Una historia no está done si no tiene tests automáticos del Q1 y Q2, y si no pasó por exploración del Q3. Los tests son parte del entregable, no un extra opcional. | Revisar el Definition of Done del equipo. Si no incluye "tests automáticos escritos y pasando" y "testing exploratorio realizado", están acumulando deuda de calidad. |

---

## 4. Criterios de Decisión

| Situación | Prioriza | Sobre | Por qué |
|-----------|----------|-------|---------|
| Feature con lógica de negocio compleja | Tests del Q2 (BDD con criterios de aceptación) | Tests del Q1 (unit tests técnicos) | La lógica de negocio compleja necesita validación de que el sistema hace lo correcto según el negocio, no solo que el código funciona técnicamente. |
| Regresión frecuente en el flujo de checkout | Automatizar tests de regresión del Q2 para ese flujo | Más testing exploratorio del Q3 | Si el mismo flujo se rompe repetidamente, necesitas una red de seguridad automática que detecte regresiones en cada commit. |
| Feature nueva de UX | Testing exploratorio del Q3 (usabilidad) | Automatización completa | Las features nuevas de UX se benefician de exploración manual antes de automatizar: hay mucha incertidumbre sobre qué debería funcionar de qué forma. |
| Servicio con requisitos de performance | Q4 (performance testing) obligatorio | Solo Q1 y Q2 | Los unit tests y acceptance tests no revelan problemas de performance bajo carga. Necesitas herramientas específicas del Q4. |

---

## 5. Anti-patrones

| Anti-patrón | Por qué es malo | Qué hacer en su lugar |
|-------------|-----------------|----------------------|
| **"QA testea al final del sprint"** | Crea un cuello de botella en los últimos días del sprint. Las features terminadas esperan en una cola. El QA no tiene tiempo suficiente y el sprint termina con cosas "en testing". | QA comienza a testear features en paralelo con el desarrollo, desde los primeros días del sprint. Cuando el developer termina una feature, el QA ya tiene el ambiente listo y los test cases escritos. |
| **Criterios de aceptación vagos ("el sistema debe funcionar correctamente")** | "Correctamente" no es testeable. Ni el developer ni el QA saben qué significa. Los bugs que escapan a producción a menudo se deben a entendimientos diferentes de "correcto". | Criterios de aceptación como ejemplos concretos en formato Given-When-Then. Si no puedes escribir un test para verificar el criterio, el criterio está mal definido. |
| **100% de cobertura de código como objetivo** | La cobertura de código mide qué líneas se ejecutaron en los tests, no si los tests son significativos. Un código puede tener 100% de cobertura y no tener ningún assertion útil (tests vacíos). | Enfocarse en coverage de comportamientos de negocio (historias de usuario cubiertas), no de líneas de código. Mejor 70% de cobertura de casos de negocio reales que 100% de líneas ejecutadas sin assertions. |
| **No tener testing exploratorio** | La automatización solo verifica lo que anticipaste. Los bugs más impactantes suelen ser los inesperados: combinaciones de estados, edge cases de usuario real, comportamientos emergentes. | Reservar tiempo en cada sprint para testing exploratorio con charter: un objetivo específico y un tiempo límite. El QA usa su intuición y creatividad para encontrar lo que los tests automáticos no pueden. |
| **El QA como único responsable de la calidad** | Crea un cuello de botella inevitable. El QA no puede probar todo si el equipo produce más código del que puede testear. Además, la calidad del código depende de los developers, no del QA. | Whole-team quality: developers hacen unit tests (Q1), trabajan con el QA en criterios de aceptación (Q2), y el QA facilita el proceso. El QA no puede asegurar calidad que el developer no construyó. |

---

## 6. Casos y Ejemplos Reales

### Caso 1: XP Team (Extreme Programming) — Testing como parte del desarrollo

- **Situación:** Los primeros equipos de XP (C3 payroll project, Kent Beck) integraron el testing como práctica central del desarrollo, no como actividad separada. TDD nació de esta práctica.
- **Decisión:** Los developers escribían los tests antes del código. Los tests definían el comportamiento esperado. El código existía para hacer pasar los tests.
- **Resultado:** El C3 project, aunque fue eventualmente cancelado por razones de negocio, demostró que el testing integrado en el desarrollo reducía drásticamente el tiempo de debugging y aumentaba la confianza para refactorizar.
- **Lección:** TDD no es sobre los tests: es sobre el diseño. Los tests son el artefacto secundario; el diseño claro es el objetivo principal.

### Caso 2: Implementación de los 4 Cuadrantes en una empresa de e-commerce

- **Situación:** Un equipo de e-commerce tenía 80% de su tiempo de QA en testing manual de regresión (Q2). Cada sprint, el QA pasaba 3 días haciendo click en los mismos flujos.
- **Decisión:** Mapearon su testing actual contra los 4 cuadrantes. Q1 (unit tests): 20% del ideal. Q2 (automatización de aceptación): 5% del ideal. Q3 (exploratorio): 0%. Q4 (performance/security): 0%.
- **Resultado:** En 3 meses, automatizaron el 70% de los tests de regresión del Q2. El tiempo del QA manual se redujo de 3 días a 4 horas por sprint. El tiempo liberado fue a Q3 (exploratorio) y Q4 (performance).
- **Lección:** Los 4 cuadrantes como diagnóstico revelan inmediatamente qué tipo de testing está descuidado. El testing manual de regresión casi siempre es el candidato #1 a automatizar.

### Caso 3: BDD con Cucumber — Criterios de aceptación ejecutables

- **Situación:** Un equipo de seguros tenía comunicación constante de "pero yo pensaba que funcionaba así" entre product owners y developers. Las historias de usuario eran ambiguas.
- **Decisión:** Adoptaron BDD con Cucumber. Cada historia requería Given-When-Then escritos en colaboración entre PO, QA y developer antes de que comenzara el desarrollo. Estos escenarios se convertían en tests ejecutables automáticamente.
- **Resultado:** Las discusiones de "¿qué significa esto?" ocurrían antes del desarrollo, no después. Los escenarios escritos en lenguaje de negocio servían como documentación viva del sistema. Los bugs de "malentendido de requisito" bajaron un 60%.
- **Lección:** Los criterios de aceptación en formato ejecutable (BDD) son la mejor forma de asegurar entendimiento compartido. Son a la vez documentación, especificación y test.

---

## Conexión con el Cerebro #6

| Habilidad del Cerebro | Aporte de esta fuente |
|------------------------|----------------------|
| H3 — Testing strategy y QA | Esta fuente es la referencia principal de estrategia de testing ágil: los 4 cuadrantes, el proceso Three Amigos, y cómo integrar QA en el flujo de trabajo del equipo sin crear cuellos de botella. |

---

## Preguntas que el Cerebro puede responder

1. ¿Cómo integramos el QA en el sprint sin crear un cuello de botella al final?
2. ¿Qué tipos de testing estamos descuidando con los 4 cuadrantes como diagnóstico?
3. ¿Cómo escribimos criterios de aceptación que sean directamente testables?
4. ¿Qué deberíamos automatizar vs. qué deberíamos testear manualmente?
5. ¿Por qué los bugs siguen escapando a producción aunque tengamos QA?
6. ¿Cómo convencemos al equipo de que la calidad es responsabilidad de todos, no solo del QA?
