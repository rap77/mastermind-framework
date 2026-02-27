---
source_id: "FUENTE-505"
brain: "brain-software-05-backend"
niche: "software-development"
title: "Test Driven Development: By Example"
author: "Kent Beck"
expert_id: "EXP-005"
type: "book"
language: "en"
year: 2002
isbn: "978-0321146533"
url: "https://www.pearson.com/en-us/subject-catalog/p/test-driven-development-by-example/P200000009570"
skills_covered: ["H1", "H2", "H6"]
distillation_date: "2026-02-27"
distillation_quality: "complete"
loaded_in_notebook: true
version: "1.0.0"
last_updated: "2026-02-27"
changelog:
  - version: "1.0.0"
    date: "2026-02-27"
    changes:
      - "Ficha creada con destilación completa"
      - "Formato estándar del MasterMind Framework"
status: "active"

habilidad_primaria: "Test Driven Development — diseñar software guiado por tests"
habilidad_secundaria: "Refactoring y deuda técnica controlada"
capa: 2
capa_nombre: "Frameworks"
relevancia: "ALTA — TDD es la práctica que garantiza que el código sea testeable por diseño, no como una idea de último momento."
gap_que_cubre: "Metodología de desarrollo que produce código testeable, mantenible y con menos bugs en producción"
---

# FUENTE-505: Test Driven Development: By Example

## Tesis Central

> El código que se escribe sin tests primero está diseñado para ser escrito, no para ser cambiado. TDD invierte este orden: el test define el comportamiento deseado antes de que el código exista. El resultado es código que se puede refactorizar sin miedo y que está diseñado para ser usado (testeable = buena API).
> TDD no es sobre tests — es sobre el diseño emergente del software.

---

## 1. Principios Fundamentales

> **P1: Red → Green → Refactor es el Ritmo del TDD**
> Escribir un test que falla (Red). Escribir el mínimo código para que pase (Green). Mejorar el código sin cambiar el comportamiento (Refactor). Repetir. Este ritmo de 2-5 minutos mantiene el feedback loop corto y el diseño limpio.
> *Contexto de aplicación: En cada nueva función o caso de uso. No escribir código de producción sin un test rojo primero.*

> **P2: Un Test, Una Razón para Fallar**
> Un test debe verificar una sola cosa. Si falla, debe ser obvio por qué. Un test que verifica 10 cosas a la vez da información ambigua cuando falla.
> *Contexto de aplicación: Al escribir tests. Si el nombre del test tiene "and" en él, probablemente debería dividirse.*

> **P3: Tests como Documentación Ejecutable**
> Los tests bien nombrados son la mejor documentación del sistema porque nunca están desactualizados — si el test pasa, el comportamiento descrito es correcto. "should_reject_order_when_stock_is_insufficient" es más útil que un comentario.
> *Contexto de aplicación: Nombrar los tests con el comportamiento esperado, no con el método que se llama.*

> **P4: Fake It Till You Make It**
> Para pasar un test rojo rápido, está permitido hacer el mínimo posible: retornar un valor hardcodeado. La presión de más tests futuros fuerza la generalización. No es trampa — es el proceso de emergencia.
> *Contexto de aplicación: Cuando estás atascado y no sabes cómo implementar. Hazlo pasar primero, luego generaliza.*

> **P5: Tests Confiables No Tienen Dependencias Externas**
> Un test que depende de la base de datos, de la red, o del reloj del sistema no es determinista. Puede pasar hoy y fallar mañana sin que el código cambie. Los unit tests deben ser rápidos, aislados, repetibles.
> *Contexto de aplicación: Si un test tarda más de 100ms, probablemente tenga dependencias externas no mockeadas.*

---

## 2. Frameworks y Metodologías

### Framework 1: El Ciclo TDD Completo

**Propósito:** Proceso iterativo para agregar funcionalidad de forma segura y con diseño emergente.
**Cuándo usar:** Al implementar cualquier nueva funcionalidad en el backend.

**Pasos:**
1. **Escribir el test (Red):**
   - Pensar en el comportamiento deseado desde el punto de vista del usuario/llamador
   - Escribir el test ANTES de que la función exista
   - El test debe fallar por la razón correcta (el comportamiento no existe, no porque el test esté mal)
   - Ejemplo: `it('should return 404 when user not found', async () => { ... })`

2. **Hacer pasar el test (Green):**
   - Escribir el MÍNIMO código posible para que el test pase
   - No importa si el código es "feo" — el refactor viene después
   - Si tienes que hacer trampa (hardcodear), hazlo — más tests te forzarán a generalizar

3. **Refactorizar (Refactor):**
   - Con todos los tests en verde, mejorar el código: nombres, estructura, duplicación
   - Si algún test se rompe, revertir el refactor — algo estuvo mal
   - No agregar funcionalidad nueva durante el refactor

4. **Repetir:**
   - El siguiente test empieza el ciclo de nuevo
   - Cada iteración es 2-5 minutos

**Output esperado:** Código funcionando con test coverage alto, diseño limpio y documentación ejecutable del comportamiento.

---

### Framework 2: Pirámide de Tests

**Propósito:** Estrategia de cuántos tests de cada tipo tener para el mejor balance entre confianza y velocidad.
**Cuándo usar:** Al definir la estrategia de testing de un proyecto.

**Niveles (de más a menos cantidad):**

| Nivel | Cantidad | Velocidad | Qué prueba |
|-------|---------|-----------|------------|
| **Unit Tests** | ~70% | <100ms c/u | Una función/clase aislada con mocks de dependencias |
| **Integration Tests** | ~20% | 1-5s c/u | La interacción entre componentes: use case + repository + DB real |
| **E2E Tests** | ~10% | 5-30s c/u | El flujo completo: HTTP request → response, como el usuario real |

**Regla:** Más tests en los niveles más bajos. Los E2E son los más confiables pero los más costosos de mantener.

---

## 3. Modelos Mentales

| Modelo | Descripción | Aplicación Práctica |
|--------|-------------|---------------------|
| **Test como Primer Usuario** | El test es el primer cliente de tu API. Si es difícil escribir el test, la API está mal diseñada. El dolor del test es feedback de diseño. | Si para testear una función necesitas instanciar 5 objetos, esa función tiene demasiadas dependencias. |
| **Given / When / Then** | Todo test tiene tres partes: el estado inicial (Given), la acción (When), y el resultado esperado (Then). Estructura AAA: Arrange, Act, Assert. | Usar esta estructura explícitamente hace los tests más legibles y mantenibles. |
| **Test Double Taxonomy** | Mock (verifica interacciones), Stub (retorna valores predefinidos), Fake (implementación simplificada real), Spy (wrapper que registra llamadas). No todo mock es lo mismo. | Usar Stub para dependencias de datos. Mock para verificar que se llamó a un servicio externo con los parámetros correctos. |
| **Coverage como Guía, No como Meta** | 80% de coverage no significa que el código esté bien testeado. Puede significar que el 80% se ejecutó pero sin assertions útiles. El coverage es un floor (mínimo), no un techo. | Medir coverage para encontrar código no testeado. No optimizar para llegar al 100% a cualquier costo. |
| **Triangulation** | Si un test pasa con un valor hardcodeado, agregar otro test con un valor diferente obliga a generalizar la implementación. Es la mecánica de emergencia del diseño. | Al estar atascado en cómo implementar algo, agregar múltiples tests con diferentes inputs revela el patrón correcto. |

---

## 4. Criterios de Decisión

| Situación | Prioriza | Sobre | Por qué |
|-----------|----------|-------|---------|
| Testear la lógica de negocio | Unit Tests con mocks | Integration tests con DB | Los unit tests son 100x más rápidos y dan feedback inmediato. La lógica de negocio no necesita la DB real. |
| Testear el Repository | Integration Test con DB real | Mocks del ORM | Testear el ORM con mocks es testear el mock, no el comportamiento real con la DB. |
| Bug en producción | Escribir el test que reproduce el bug primero | Corregir el bug directamente | El test garantiza que el bug no regrese. "Bug sin test = bug que volverá." |
| API pública nueva | TDD desde el inicio | Code first, tests después | El primer usuario de la API (el test) revela problemas de diseño antes de que sean costosos de cambiar. |
| Código legacy sin tests | Characterization Tests primero | Refactorizar sin red de seguridad | Los Characterization Tests documentan el comportamiento actual antes de refactorizar, creando la red de seguridad. |

---

## 5. Anti-patrones

| Anti-patrón | Por qué es malo | Qué hacer en su lugar |
|-------------|-----------------|----------------------|
| **Tests que prueban implementación, no comportamiento** | `expect(orderService.calculateTotal).toHaveBeenCalled()` — si refactorizas el método, el test falla aunque el comportamiento sea correcto. | Testear el output: `expect(order.total).toBe(150)`. Los tests deben sobrevivir al refactor interno. |
| **Test Suite lenta** | Si los tests tardan 10 minutos, los desarrolladores dejan de correrlos localmente. El feedback loop se rompe. | Mantener el suite de unit tests < 2 minutos. Separar integration/E2E tests en CI. |
| **Test que depende del orden de ejecución** | Un test modifica estado global que otro test necesita. Si corres el segundo primero, falla. No determinístico. | Cada test es independiente. Setup y teardown en cada test. No compartir estado mutable entre tests. |
| **Mocking excesivo** | Si mockeas todo, el test no prueba nada real. "Mock everything" es falsa confianza. | Mockear dependencias externas (DB, APIs, email). No mockear el código que estás escribiendo tú mismo. |
| **Code first, tests después (Test Last)** | Escribir los tests después del código es difícil porque el código no fue diseñado para ser testeable. Se termina con tests que encajan al código existente, no que lo verifican. | TDD: test primero. Si no es posible, al menos escribir tests antes de mergear. |

---

## 6. Casos y Ejemplos Reales

### Caso 1: Beck's Money Example (del libro)

- **Situación:** Implementar una clase `Money` que soporte múltiples monedas y operaciones de suma.
- **Proceso TDD:** Test 1: `5 USD == 5 USD`. Falla. Implementar `equals`. Verde. Refactorizar. Test 2: `5 USD + 10 EUR`. Falla. El diseño emerge de los tests: `Money` necesita `Currency`, y las sumas entre monedas diferentes necesitan un `Exchange`.
- **Resultado:** Un diseño emergente que nadie habría diseñado completamente desde el inicio. El sistema de múltiples monedas emergió de tests simples.
- **Lección:** TDD no es solo testing — es un método de diseño. El diseño correcto emerge de los tests.

### Caso 2: Equipo con Suite Lenta — Splitting Tests

- **Situación:** Suite de 3,000 tests que tarda 45 minutos. Los devs dejan de correrla localmente.
- **Decisión:** Identificar que el 90% del tiempo lo consumían 300 integration tests con DB real.
- **Resultado:** Separar en: unit tests (< 2 min, corren en cada save), integration tests (5 min, corren en pre-commit), E2E (30 min, solo en CI). Feedback inmediato restaurado.
- **Lección:** La velocidad del feedback loop determina si los tests se usan. Más rápido = más útil.

### Caso 3: Bug en Producción — Test First Fix

- **Situación:** Bug reportado: los pedidos con descuento del 100% fallaban silenciosamente.
- **Proceso:** Primero escribir el test que reproduce el bug: `expect(createOrder({ discount: 100 })).toSucceed()`. Falla. Ahora corregir el bug. Verde. El bug nunca volverá.
- **Resultado:** El bug fue corregido y documentado como test en < 30 minutos. El mismo bug nunca volvió a producción.
- **Lección:** Todo bug merece un test. Es la forma más eficiente de documentar "esto no debería pasar nunca más".

---

## Conexión con el Cerebro #5

| Habilidad del Cerebro | Aporte de esta fuente |
|-----------------------|----------------------|
| Testing de lógica de negocio | TDD como metodología de diseño que produce código testeable por default |
| Estrategia de tests | Pirámide de tests: cuántos unit vs integration vs E2E |
| Refactoring seguro | Red-Green-Refactor como ciclo que garantiza no romper el comportamiento |
| Diseño de APIs internas | El test como primer usuario revela APIs mal diseñadas temprano |
| Debugging eficiente | Test que reproduce el bug como primer paso antes de corregirlo |
| Documentación | Tests como documentación ejecutable del comportamiento esperado |

---

## Preguntas que el Cerebro puede responder

1. ¿Cómo empiezo a aplicar TDD en mi proyecto si nunca lo he hecho?
2. ¿Cuál es la diferencia entre un Mock, un Stub y un Fake?
3. ¿Cómo estructuro los tests de mi aplicación backend — qué testeo con unit tests y qué con integration tests?
4. ¿Por qué escribir los tests antes del código si al final tengo el mismo código?
5. ¿Cómo testeo código legacy sin tests existentes?
6. ¿Por qué mi test suite tarda tanto y cómo acelerarlo?
