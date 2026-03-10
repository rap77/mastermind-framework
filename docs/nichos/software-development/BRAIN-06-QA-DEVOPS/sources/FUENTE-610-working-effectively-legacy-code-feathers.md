---
source_id: "FUENTE-610"
brain: "brain-software-06-qa-devops"
niche: "software-development"
title: "Working Effectively with Legacy Code"
author: "Michael Feathers"
expert_id: "EXP-610"
type: "book"
language: "en"
year: 2004
isbn: "978-0131177055"
url: "https://www.oreilly.com/library/view/working-effectively-with/0131177052/"
skills_covered: ["H11"]
distillation_date: "2026-02-27"
distillation_quality: "complete"
loaded_in_notebook: true
version: "1.1.0"
last_updated: "2026-02-27"
changelog:
  - version: "1.1.0"
    date: "2026-02-27"
    changes:
      - "Cargada en NotebookLM (notebook ID: 74cd3a81-1350-4927-af14-c0c4fca41a8e)"
  - version: "1.0.0"
    date: "2026-02-27"
    changes:
      - "Ficha creada para cubrir GAP de modernización incremental y brownfield DevOps"
      - "Formato estándar del MasterMind Framework"
status: "active"

habilidad_primaria: "Modernización incremental: introducir tests, CI/CD y automatización en sistemas sin ellos"
habilidad_secundaria: "Técnicas de seam y refactoring seguro para hacer código legacy testeable sin romper producción"
capa: 2
capa_nombre: "Frameworks"
relevancia: "ALTA — Cubre el GAP de transformación incremental. Las demás fuentes describen el estado ideal; esta describe cómo llegar desde el caos al ideal en sistemas brownfield. Sin esta fuente, el cerebro sabe a dónde ir pero no cómo empezar cuando el sistema ya tiene 5 años de deuda técnica."
gap_que_cubre: "Transformación incremental de sistemas sin tests ni CI/CD hacia DevOps moderno — no cubierto por ninguna fuente base"
---

# FUENTE-610: Working Effectively with Legacy Code

## Tesis Central

> El código legacy no es código viejo: es código sin tests. Y sin tests, cualquier cambio es una apuesta. La única forma de modernizar un sistema existente de forma segura es introducir tests de caracterización que documenten el comportamiento actual antes de cambiarlo, usando técnicas de seam para romper dependencias que hacen el código inestable. La transformación no ocurre de golpe: ocurre una clase, un método, un test a la vez.

---

## 1. Principios Fundamentales

> **P1: Legacy code = código sin tests — la edad no importa**
> La definición operativa de Feathers es precisa y útil: código legacy no es sinónimo de código viejo o código malo. Es código que no tiene tests automatizados. Un sistema escrito la semana pasada sin tests es legacy. Un sistema de 15 años con buena cobertura de tests no lo es. Esta definición cambia el enfoque: el problema no es la antigüedad sino la ausencia de red de seguridad.
> *Contexto: Al evaluar si un sistema es "legacy" para propósitos de DevOps, preguntar: ¿hay tests que fallen si introduzco un cambio incorrecto? Si la respuesta es no, es legacy independientemente de su edad.*

> **P2: Tests de caracterización — documentar el comportamiento actual antes de cambiarlo**
> Antes de refactorizar o agregar funcionalidad a código sin tests, se escribe un test que documenta lo que el código hace hoy, no lo que debería hacer. Si el test pasa con el comportamiento actual, cualquier cambio futuro que rompa ese test es una regresión. Los tests de caracterización son la red de seguridad mínima para trabajar en legacy.
> *Contexto: Al recibir un sistema sin tests para modernizar, el primer sprint no es agregar features ni refactorizar: es escribir tests de caracterización de los flujos más críticos. Solo después es seguro cambiar.*

> **P3: El cambio seguro requiere el algoritmo: test → cambio → test pasa**
> En código sin tests, el flujo natural es "cambio → cruzar los dedos → deploy → incidente." El flujo seguro es: identificar el área a cambiar → escribir test de caracterización que cubra esa área → hacer el cambio → verificar que el test pasa. Este algoritmo se repite para cada cambio, por pequeño que sea.
> *Contexto: Este principio es el argumento para introducir testing antes de cualquier sprint de modernización. Sin la fase de tests de caracterización, la modernización es tan arriesgada como el status quo.*

> **P4: Avanzar en pasos tan pequeños que cada uno sea reversible**
> La tentación en sistemas legacy es "refactorizarlo todo de una vez." Invariablemente esto resulta en un refactor que dura meses, rompe algo en producción, y termina con el equipo haciendo rollback a la versión original. La alternativa es el cambio incremental: cada paso es tan pequeño que si falla, el rollback es trivial.
> *Contexto: Al planificar modernización, la unidad de trabajo es "una función testeable" o "un componente desacoplado", no "el módulo completo." El progreso es lento pero irreversible.*

> **P5: La deuda técnica tiene interés compuesto — cada día sin tests hace el siguiente cambio más costoso**
> El código sin tests se vuelve más difícil de cambiar con el tiempo, no igual. Cada feature nueva que se añade sin tests añade más superficie sin protección. El costo de añadir tests mañana es mayor que hoy porque el código habrá crecido. La ventana para modernizar de forma razonable se cierra con el tiempo.
> *Contexto: Usar este argumento con stakeholders que dicen "lo modernizamos cuando tengamos tiempo." Cada sprint que pasa sin modernización hace la modernización futura más cara, no igual.*

---

## 2. Frameworks y Metodologías

### Framework 1: El Algoritmo de Cambio Seguro en Legacy

**Propósito:** Proceso paso a paso para introducir cualquier cambio en un sistema sin tests de forma que minimice el riesgo de regresiones.
**Cuándo usar:** Siempre que se trabaje en código sin tests automatizados. Es el protocolo base de toda modernización.

**Paso 1 — Identificar los Change Points:**
- ¿Qué código necesita cambiar para implementar lo que se pide?
- ¿Qué otras partes del sistema dependen de ese código? (impacto potencial)
- Documentar las dependencias antes de tocar nada

**Paso 2 — Encontrar los Test Points:**
- ¿Dónde puedo escribir un test que detecte si el cambio rompe algo?
- Si el código tiene dependencias difíciles (base de datos real, sistema externo, singletons), necesita seams para poder testearse
- Si no hay Test Points → ir al Paso 3 antes de continuar

**Paso 3 — Romper dependencias con Seams:**
- Un seam es un lugar donde se puede alterar el comportamiento del código sin modificarlo
- Tipos de seam: constructor injection, extract interface, extract method, subclass and override
- Ejemplo: en lugar de `new DatabaseConnection()` hardcodeado, inyectar la conexión como parámetro → ahora se puede inyectar un fake en el test

**Paso 4 — Escribir tests de caracterización:**
```python
# Ejemplo: test de caracterización
def test_calcula_descuento_comportamiento_actual():
    # No sé si este cálculo es correcto, pero SÍ sé que esto es lo que hace hoy
    # Si cambia, el test me avisa
    resultado = calcular_descuento(precio=100, cliente_vip=True)
    assert resultado == 15  # Esto es lo que retorna HOY — puede ser un bug, no importa aún
```

**Paso 5 — Hacer el cambio:**
- Con los tests de caracterización en verde, hacer el cambio planificado
- Los tests deben seguir pasando
- Si alguno falla, el cambio introdujo una regresión inesperada → investigar antes de continuar

**Paso 6 — Agregar tests del comportamiento nuevo:**
- Ahora que el código es testeable y el cambio está hecho, agregar tests que verifiquen el comportamiento nuevo esperado
- Estos tests son los que quedan como parte del suite permanente

**Output esperado:** Código modificado con tests de caracterización del comportamiento previo + tests del comportamiento nuevo. El siguiente cambio en esa área es más seguro que el anterior.

---

### Framework 2: Introducción Incremental de CI/CD en un Sistema Brownfield

**Propósito:** Roadmap de cómo llevar un sistema de "deploy manual + sin tests" a "CI/CD automatizado" sin interrumpir la operación actual.
**Cuándo usar:** Al recibir un sistema sin automatización y necesitar modernizarlo mientras sigue en producción.

**Fase 1 — Visibilidad (Semana 1-2): hacer el build repetible**
- Objetivo: que el build funcione desde cero en cualquier máquina, no solo en "la máquina del deploy"
- Acciones: documentar todos los pasos manuales del deploy actual, crear un script que los ejecute, ejecutarlo en una máquina limpia y verificar que funciona
- Criterio de éxito: cualquier miembro del equipo puede hacer el deploy siguiendo el script

**Fase 2 — Primera automatización (Semana 2-4): CI básico**
- Objetivo: que cada commit dispare un build automático
- Acciones: crear el primer pipeline de CI (GitHub Actions, GitLab CI) que solo compile/buildea el proyecto y corra los tests existentes (aunque sean 0)
- No agregar tests todavía — solo automatizar lo que existe
- Criterio de éxito: el pipeline corre en cada commit y da feedback en minutos

**Fase 3 — Red de seguridad mínima (Mes 1-2): tests de caracterización en los flujos críticos**
- Objetivo: proteger los 3-5 flujos más críticos del negocio con tests antes de cualquier refactor
- Acciones: identificar los flujos de negocio más importantes (checkout, autenticación, proceso core), escribir tests de caracterización end-to-end que cubran el happy path de cada uno
- No refactorizar nada todavía — solo documentar el comportamiento actual
- Criterio de éxito: si alguien rompe accidentalmente el checkout, el pipeline falla

**Fase 4 — Automatización del deploy (Mes 2-3): CD a staging**
- Objetivo: que el pipeline también haga deploy automático a staging en cada merge a main
- Acciones: containerizar la aplicación (si no lo está), crear el environment de staging, agregar el step de deploy al pipeline
- Criterio de éxito: cada merge a main resulta en un deploy automático a staging

**Fase 5 — Expansión de tests (ongoing): pagar la deuda de tests**
- Objetivo: aumentar la cobertura de tests progresivamente, priorizando el código que cambia con más frecuencia
- Regla: cada vez que se toca un área del código, se dejan más tests de los que había
- No hay sprint "de solo tests" — los tests se agregan como parte del trabajo normal

**Output esperado:** Sistema brownfield con CI/CD funcional, cobertura básica de los flujos críticos, y un proceso sostenible de expansión incremental de la automatización.

---

## 3. Modelos Mentales

| Modelo | Descripción | Aplicación Práctica |
|--------|-------------|---------------------|
| **El Boy Scout Rule** | "Deja el código un poco mejor de lo que lo encontraste." No refactorizar todo de una vez, pero sí dejar cada área tocada con mejor cobertura de tests que antes. El progreso es inevitable si se aplica consistentemente. | Política de equipo: cada PR que modifica código legacy debe incluir al menos un test de caracterización del área modificada. En 6 meses, las áreas más activas del código tienen cobertura decente sin un sprint dedicado. |
| **Seam como palanca de testabilidad** | Un seam es cualquier punto donde se puede cambiar el comportamiento del código para testing sin modificar el código de producción. La inyección de dependencias es el seam más común. | Al encontrar código "imposible de testear" (God class, singletons, dependencias hardcodeadas), la solución no es reescribirlo: es identificar el seam mínimo que permita inyectar un test double. |
| **Sprinkle, don't flood** | La modernización incremental es como agua que entra por las grietas: entra poco a poco pero llega a todos lados. El flood (reescribir todo) genera caos. El sprinkle (pequeños cambios consistentes) genera progreso sostenible. | Al planificar la modernización, rechazar la propuesta "reescribamos el módulo X completo en el próximo sprint." En su lugar: "cada feature nueva en ese módulo se hace con tests, cada bug se arregla dejando un test que lo cubre." |
| **El costo del primer test** | El primer test en un área de código legacy es el más costoso: requiere crear los seams, entender el comportamiento actual, escribir el test de caracterización. El segundo test en esa misma área es 5x más barato porque la infraestructura ya existe. | Concentrar el esfuerzo inicial de modernización en las áreas más activas del código. El alto costo inicial se amortiza rápido en áreas con alta frecuencia de cambio. |

---

## 4. Criterios de Decisión

| Situación | Prioriza | Sobre | Por qué |
|-----------|----------|-------|---------|
| Sistema legacy sin tests: ¿empezar con tests unitarios o E2E? | Tests E2E/integración de los flujos críticos primero | Tests unitarios granulares | Los tests unitarios requieren refactoring previo para desacoplar. Los E2E cubren los flujos críticos sin tocar el código interno. Son la red de seguridad más rápida de conseguir. |
| ¿Refactorizar o reescribir un módulo legacy problemático? | Refactorizar incrementalmente con tests de caracterización como guía | Reescribir desde cero | Las reescrituras desde cero tienen una tasa de fracaso muy alta: se subestima la complejidad, se pierden comportamientos implícitos, y el nuevo sistema tiene sus propios bugs. El refactor incremental es más lento pero más seguro. |
| ¿Agregar tests antes o después de arreglar un bug en legacy? | Escribir un test que reproduzca el bug → arreglarlo → verificar que el test pasa | Arreglar el bug directamente | El test que reproduce el bug es la prueba de que el bug existe y de que el fix funciona. Además, previene que el mismo bug regrese en el futuro (test de regresión). |
| CI pipeline falla porque el legacy tiene dependencias de ambiente imposibles de simular | Aislar esos tests en una suite separada de "integration" que no bloquea el pipeline | Bloquear todos los merges hasta resolver | No resolver este problema de golpe. Aislar los tests problemáticos, hacer que el pipeline principal corra los que sí funcionan, y resolver los complejos gradualmente. |

---

## 5. Anti-patrones

| Anti-patrón | Por qué es malo | Qué hacer en su lugar |
|-------------|-----------------|----------------------|
| **"Lo reescribimos desde cero"** | Las reescrituras totales subestiman invariablemente la complejidad del sistema original. El nuevo sistema hereda los mismos problemas de negocio más los bugs de la reescritura. Joel Spolsky lo llamó "the single worst strategic mistake." | Refactoring incremental con tests de caracterización como red de seguridad. Reescribir solo componentes aislados con interfaz clara, no sistemas completos. |
| **Modernizar sin tests de caracterización previos** | Refactorizar código sin tests es como hacer cirugía a ciegas. Se puede "mejorar" el código y romper un comportamiento implícito que nadie documentó y que el negocio depende. | Escribir tests de caracterización del comportamiento actual antes de cualquier refactor. No importa si el comportamiento actual es "incorrecto" — documentarlo primero, cambiarlo después. |
| **Sprint dedicado a "pagar la deuda técnica"** | Los sprints de deuda técnica raramente se aprueban, y cuando se aprueban, el progreso es menor del esperado porque el equipo no tiene contexto de todo el código. Además, la deuda sigue acumulándose. | Boy Scout Rule: cada PR deja el código mejor. La deuda técnica se paga de forma distribuida y continua, no en un sprint heroico. |
| **Introducir CI/CD sin cambiar el proceso de deploy** | Un pipeline de CI que automáticamente hace lo mismo que hacía el deploy manual solo automatiza el caos. Si el deploy manual requería 15 pasos manuales, el pipeline automatiza 15 pasos manuales. | Aprovechar la introducción del pipeline para rediseñar el proceso de deploy: eliminar pasos manuales, introducir idempotencia, separar configuración del artefacto. |
| **Ignorar los tests flaky heredados** | Los tests flaky en un sistema legacy son frecuentes (dependencias de estado, timeouts, orden de ejecución). Ignorarlos hace que el equipo pierda confianza en el pipeline completo. | Política de cuarentena: los tests flaky se mueven a una suite separada marcada como "pendiente de arreglar." No bloquean el pipeline pero son visibles como deuda activa. |

---

## 6. Casos y Ejemplos Reales

### Caso 1: J.B. Rainsberger — Rescate de sistema de facturación de 15 años

- **Situación:** Consultor contratado para modernizar un sistema de facturación de 15 años en Java, sin tests, con 200,000 líneas de código. El cliente necesitaba agregar soporte para un nuevo tipo de factura, pero cualquier cambio rompía algo inesperado.
- **Decisión:** Aplicó el algoritmo de Feathers: identificó el área de cambio, encontró seams mediante extract interface en las dependencias de base de datos, escribió tests de caracterización de los cálculos de facturación más críticos, y luego hizo el cambio.
- **Resultado:** La feature tardó 3 semanas en lugar de los 3 días estimados originalmente, pero se entregó sin regresiones. Los tests de caracterización escritos durante el proceso quedan como activo permanente. Los siguientes cambios en el módulo de facturación son ahora 4x más rápidos porque la infraestructura de tests existe.
- **Lección:** La inversión inicial en tests de caracterización parece lenta. El ROI llega en los siguientes cambios al mismo módulo.

### Caso 2: Etsy — Modernización del monolito mientras seguía en producción

- **Situación:** Etsy tenía un monolito PHP de millones de líneas que necesitaba modernizarse sin poder detener el negocio. La solución de "lo reescribimos" no era viable para una empresa con millones de transacciones diarias.
- **Decisión:** Adoptaron el enfoque de "estrangulación incremental" (Strangler Fig pattern): los módulos nuevos se construyen con tests y arquitectura moderna, mientras el código legacy se va reemplazando incrementalmente módulo por módulo.
- **Resultado:** En 5 años, grandes porciones del monolito fueron reemplazadas sin downtime ni grandes releases de riesgo. El sistema nunca dejó de funcionar durante la transformación. Llegaron a 50+ deploys diarios mientras el monolito legacy aún existía.
- **Lección:** La modernización de sistemas críticos no requiere una "gran reescritura." El Strangler Fig pattern permite transformación continua sin riesgo catastrófico.

### Caso 3: Un equipo típico de agencia — De deploy manual a CI/CD en 3 meses

- **Situación:** Sistema de e-commerce en producción con 3 años de vida, sin tests, deploy manual via FTP, un solo desarrollador que "sabe cómo funciona todo." El desarrollador original se va y el equipo nuevo no puede tocar el sistema sin miedo.
- **Decisión:** Aplicaron el Framework 2 de esta ficha: primero documentaron el deploy en un script, luego crearon un pipeline de CI básico, luego escribieron tests E2E de los 3 flujos críticos (registro, checkout, administración de productos), luego automatizaron el deploy a staging.
- **Resultado:** En 3 meses tenían CI/CD funcional con cobertura básica de los flujos críticos. Los nuevos desarrolladores podían hacer cambios con confianza. El tiempo de onboarding bajó de "3 semanas de miedo" a "3 días con el pipeline como guía."
- **Lección:** La modernización incremental de un sistema brownfield es posible en meses, no años, si se sigue un proceso estructurado con prioridades claras.

---

## Conexión con el Cerebro #6

| Habilidad del Cerebro | Aporte de esta fuente |
|------------------------|----------------------|
| H11 — Modernización incremental y brownfield DevOps | Esta fuente es la referencia para la transformación de sistemas legacy: tests de caracterización, seams, el algoritmo de cambio seguro, y el roadmap de introducción incremental de CI/CD en sistemas brownfield. Cubre el gap que ninguna otra fuente toca. |

---

## Preguntas que el Cerebro puede responder

1. ¿Cómo introducimos tests en un sistema que nunca los tuvo sin dedicar un sprint completo a eso?
2. ¿Cómo hacemos el primer pipeline de CI para un sistema que lleva años con deploy manual?
3. ¿Cuál es la diferencia entre refactorizar y reescribir, y cuándo elegir cada opción?
4. ¿Cómo modificamos un módulo crítico en producción sin tests sin arriesgarnos a romper algo?
5. ¿Por qué el primer test en un área de código legacy es tan costoso y cómo reducir ese costo?
6. ¿Cómo convencemos al equipo de que la modernización incremental es más segura que la reescritura total?
