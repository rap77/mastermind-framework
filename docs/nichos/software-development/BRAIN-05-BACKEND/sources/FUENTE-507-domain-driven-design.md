---
source_id: "FUENTE-507"
brain: "brain-software-05-backend"
niche: "software-development"
title: "Domain-Driven Design: Tackling Complexity in the Heart of Software"
author: "Eric Evans"
expert_id: "EXP-005"
type: "book"
language: "en"
year: 2003
isbn: "978-0321125217"
url: "https://www.domainlanguage.com/ddd"
skills_covered: ["H1", "H2", "H3"]
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

habilidad_primaria: "Modelado del dominio de negocio en código — DDD táctico y estratégico"
habilidad_secundaria: "Bounded Contexts, Aggregates, y Ubiquitous Language"
capa: 2
capa_nombre: "Frameworks"
relevancia: "ALTA — DDD es el framework para traducir complejidad de negocio a código. Sin él, los sistemas complejos colapsan en caos."
gap_que_cubre: "Metodología para modelar dominios complejos y diseñar la arquitectura de sistemas que reflejan el negocio"
---

# FUENTE-507: Domain-Driven Design (DDD)

## Tesis Central

> La complejidad del software no está en la tecnología — está en el dominio de negocio. Los mejores sistemas son aquellos donde el código habla el mismo idioma que los expertos del dominio. DDD proporciona el vocabulario y los patrones para que el modelo de código y el modelo de negocio converjan.
> Es el framework para diseñar sistemas que escalan en complejidad de negocio, no solo en usuarios.

---

## 1. Principios Fundamentales

> **P1: El Modelo es el Corazón del Diseño**
> El modelo de dominio no es un diagrama UML desactualizado — es el código mismo. Cada clase, método y nombre debe reflejar el lenguaje del negocio. Si el código dice `calculateTax()` y el experto de negocio dice "aplicar impuesto", hay un gap que produce bugs.
> *Contexto de aplicación: En todas las reuniones de diseño. Usar los términos exactos del negocio en el código, no términos técnicos inventados.*

> **P2: Ubiquitous Language — Un Solo Vocabulario**
> Desarrolladores y expertos del dominio deben hablar el mismo lenguaje. El glosario del negocio = el glosario del código. "Pedido" no es "Order" en un contexto y "Purchase" en otro. La ambigüedad en el lenguaje produce bugs invisibles.
> *Contexto de aplicación: Al iniciar un proyecto. Crear un glosario explícito de términos del dominio. Cuestionarlo cuando el código use términos distintos.*

> **P3: Bounded Context como Frontera del Modelo**
> Un mismo concepto (ej: "Cliente") significa cosas distintas en diferentes partes del negocio: para ventas, es quien compra; para soporte, es quien tiene incidentes; para contabilidad, es quien debe dinero. Cada significado vive en su propio Bounded Context con su propio modelo.
> *Contexto de aplicación: Al identificar que el mismo término tiene significados distintos en diferentes equipos. Es el momento de crear un Bounded Context separado.*

> **P4: Aggregates Protegen la Consistencia**
> Un Aggregate es un grupo de entidades que forman una unidad de consistencia. Solo la raíz del Aggregate (Aggregate Root) puede ser referenciada desde fuera. Las reglas de negocio del Aggregate se respetan siempre. Ejemplo: `Order` es el root. `OrderLine` solo existe dentro de `Order`.
> *Contexto de aplicación: Al identificar qué entidades siempre deben estar en un estado consistente juntas. Si `Order` sin `OrderLine` no tiene sentido, son un Aggregate.*

> **P5: Separar el Dominio del Resto**
> La lógica de negocio (dominio) debe estar completamente separada de la infraestructura (DB, API, colas). El dominio no sabe cómo se persiste, cómo se presenta, ni cómo se comunica. Esta separación permite que el dominio evolucione independientemente.
> *Contexto de aplicación: Si encuentras SQL, HTTP, o llamadas a librerías externas en tu modelo de dominio, hay violación de este principio.*

---

## 2. Frameworks y Metodologías

### Framework 1: Event Storming — Descubrir el Dominio

**Propósito:** Explorar el dominio de negocio con los expertos para identificar eventos, comandos, aggregates y bounded contexts.
**Cuándo usar:** Al iniciar un proyecto nuevo o al rediseñar un sistema existente.

**Pasos:**
1. **Eventos de Dominio (naranja):** Listar todo lo que "pasa" en el negocio. "Pedido creado", "Pago procesado", "Producto agotado". En tiempo pasado.
2. **Comandos (azul):** Identificar qué acciones desencadenan esos eventos. "Crear pedido" → "Pedido creado".
3. **Aggregates (amarillo):** Agrupar eventos y comandos alrededor del objeto de negocio que mantiene el estado.
4. **Bounded Contexts (líneas):** Dibujar fronteras alrededor de grupos coherentes de aggregates que hablan el mismo lenguaje.
5. **Context Map (relaciones):** Definir cómo se comunican los bounded contexts entre sí.

**Output esperado:** Mapa del dominio con eventos, commandos, aggregates y bounded contexts claramente identificados.

---

### Framework 2: DDD Táctico — Bloques de Construcción

**Propósito:** Implementar el modelo de dominio con los building blocks correctos.
**Cuándo usar:** Al escribir código de la capa de dominio.

| Building Block | Descripción | Ejemplo |
|----------------|-------------|---------|
| **Entity** | Tiene identidad única. Puede cambiar sus atributos. | `User`, `Order`, `Product` |
| **Value Object** | Sin identidad. Definido por sus atributos. Inmutable. | `Money`, `Address`, `Email` |
| **Aggregate** | Cluster de entidades con una raíz. Unidad de consistencia. | `Order` (root) + `OrderLine` |
| **Domain Event** | Algo que ocurrió en el dominio, expresado en tiempo pasado. | `OrderPlaced`, `PaymentFailed` |
| **Repository** | Abstracción de persistencia. Parece una colección en memoria. | `OrderRepository` |
| **Domain Service** | Lógica de negocio que no encaja en ninguna entidad. | `TaxCalculationService` |
| **Factory** | Encapsula la lógica de creación de objetos complejos. | `OrderFactory` |

---

## 3. Modelos Mentales

| Modelo | Descripción | Aplicación Práctica |
|--------|-------------|---------------------|
| **Anticorruption Layer (ACL)** | Al integrar con sistemas externos que tienen un modelo diferente, el ACL traduce entre los dos modelos sin contaminar el dominio interno. | Al integrar con una API de terceros (ej: Stripe), no dejar que los tipos de Stripe entren al dominio. El ACL los traduce a los tipos del dominio. |
| **Context Map** | Mapa de todos los Bounded Contexts y cómo se relacionan: Partnership, Customer-Supplier, Conformist, ACL, Open Host Service, Published Language. | Al diseñar la integración entre servicios, identificar qué tipo de relación existe para elegir el patrón correcto. |
| **Invariantes del Aggregate** | Reglas de negocio que SIEMPRE deben cumplirse dentro del Aggregate. El Aggregate Root las protege rechazando comandos inválidos. | `Order` nunca debe poder tener un `total < 0`. Si un comando lo haría, lanzar una excepción de dominio. |
| **Domain Events como Integración** | Los Bounded Contexts se comunican a través de Domain Events, no llamadas directas. `OrderPlaced` es publicado por el contexto de Orders. El contexto de Inventory lo consume. | Reduce el acoplamiento entre contextos. Si el contexto de Inventory cae, el de Orders no falla — el evento espera. |
| **Supple Design** | El código del dominio debe ser expresivo, fluido, y diseñado para ser leído por personas, no solo por máquinas. Los métodos tienen nombres de verbos del negocio. | `order.place()`, `payment.capture()`, `subscription.cancel()` — el código lee como el negocio habla. |

---

## 4. Criterios de Decisión

| Situación | Prioriza | Sobre | Por qué |
|-----------|----------|-------|---------|
| Dominio complejo con múltiples equipos | DDD con Bounded Contexts | Un modelo único compartido | Múltiples equipos con un modelo compartido produce conflictos de diseño constantes. Cada equipo necesita autonomía en su contexto. |
| CRUD simple sin lógica de negocio | Transaction Script o Active Record | Domain Model completo | DDD tiene costo. Para un CRUD, es sobre-ingeniería. |
| Integración con sistema legado | Anticorruption Layer | Conformist (adoptar el modelo del legado) | Sin ACL, el modelo del sistema legado contamina el nuevo sistema. Con el tiempo, ambos son inseparables. |
| Comunicación entre contextos | Domain Events (asíncrono) | Llamadas síncronas directas | Los eventos desacoplan. Si el contexto consumidor cae, el productor sigue funcionando. |
| Concepto que significa cosas distintas en diferentes partes | Bounded Contexts separados | Un modelo único con muchos if-else | Un modelo que sirve a todos no sirve bien a ninguno. Los if-else para manejar contextos diferentes son deuda técnica. |

---

## 5. Anti-patrones

| Anti-patrón | Por qué es malo | Qué hacer en su lugar |
|-------------|-----------------|----------------------|
| **God Aggregate** | Un Aggregate con 20 entidades y todas las reglas del sistema. Cada operación es una transacción masiva. Rendimiento y contención de locks destruidos. | Aggregates pequeños. Si necesitas consistencia entre dos aggregates, probablemente puedes usar eventual consistency con Domain Events. |
| **Anemic Domain Model** | Entidades sin comportamiento. Toda la lógica en Services. El dominio es solo un DTO. | Mover la lógica al aggregate. `order.addLine(product, quantity)` en lugar de `orderService.addLineToOrder(orderId, productId, qty)`. |
| **Shared Database entre Bounded Contexts** | Dos contextos comparten la misma tabla. Cambiar el schema para uno afecta al otro. El acoplamiento es invisible y peligroso. | Cada Bounded Context tiene su propia DB o schema. Se comunican via eventos o API, no por DB compartida. |
| **Model Pollution** | El dominio de `Ventas` usa directamente el modelo de `Facturación`. Cuando `Facturación` cambia su modelo, `Ventas` se rompe. | ACL o Domain Events. Los contextos no se conocen directamente — se comunican a través de interfaces definidas. |
| **Ubiquitous Language inconsistente** | El código dice `customer`, el dominio dice `client`, el CRM dice `account`. Tres palabras para el mismo concepto. Confusión perpetua. | Un glosario del dominio acordado por devs y expertos. Refactorizar el código para usar el término correcto en cada contexto. |

---

## 6. Casos y Ejemplos Reales

### Caso 1: Amazon — Bounded Contexts en E-commerce

- **Situación:** El catálogo de productos en Amazon es radicalmente diferente según el contexto: para el cliente es "lo que puedo comprar", para el vendedor es "lo que pongo a la venta", para el almacén es "lo que debo almacenar".
- **Decisión:** Bounded Contexts separados: `Catalog`, `Inventory`, `Fulfillment`, `Pricing`. Cada uno con su modelo del "producto".
- **Resultado:** Equipos autónomos, despliegues independientes, modelos optimizados para cada uso.
- **Lección:** El mismo concepto tiene representaciones diferentes en diferentes contextos. Forzar un modelo único produce un modelo que no sirve bien a ninguno.

### Caso 2: Sistema Bancario — Aggregates y Consistencia

- **Situación:** Una transferencia bancaria involucra dos cuentas: debitar una y acreditar la otra. ¿Son un solo Aggregate?
- **Decisión:** Si se hace en un solo Aggregate, el lock es sobre ambas cuentas — un bottleneck masivo.
- **Solución DDD:** Dos Aggregates separados (`AccountA`, `AccountB`). La transferencia usa eventual consistency via Domain Events: `MoneyDebited` de A dispara `CreditMoney` en B. Con Saga pattern para el fallo.
- **Lección:** La consistencia eventual bien diseñada escala mucho mejor que la consistencia fuerte en todos los casos.

### Caso 3: Startup — Lenguaje Ubicuo que Ahorró un Bug

- **Situación:** Los developers llamaban al proceso "confirm order". Los de negocio llamaban "place order". En el código, `confirm` hacía lo que el negocio llamaba "place", pero también había otro `confirm` que significaba "verificar pago".
- **Problema:** Un nuevo developer usó `confirmOrder()` creyendo que verificaba el pago. En realidad, completaba el pedido sin cobrar.
- **Solución:** Event storming con el equipo de negocio. Se estableció: `placeOrder()`, `capturePayment()`, `fulfillOrder()` como el lenguaje único.
- **Lección:** Un bug de negocio causado por lenguaje inconsistente. El Ubiquitous Language no es burocracia — es seguridad.

---

## Conexión con el Cerebro #5

| Habilidad del Cerebro | Aporte de esta fuente |
|-----------------------|----------------------|
| Modelado del dominio | Building blocks de DDD: Entity, Value Object, Aggregate, Domain Service |
| Arquitectura de microservicios | Bounded Contexts como fronteras naturales de microservicios |
| Comunicación entre servicios | Domain Events como mecanismo de integración desacoplado |
| Diseño de la capa de dominio | Ubiquitous Language y Supple Design para código expresivo |
| Integración con sistemas externos | Anticorruption Layer como patrón para proteger el dominio |
| Event-driven architecture | Domain Events como base de sistemas reactivos y desacoplados |

---

## Preguntas que el Cerebro puede responder

1. ¿Qué es un Bounded Context y cómo identifico las fronteras correctas en mi sistema?
2. ¿Cómo identifico los Aggregates de mi dominio y qué tamaño deben tener?
3. ¿Cómo me aseguro de que el código use el mismo lenguaje que el negocio?
4. ¿Cómo comunico dos microservicios sin acoplarlos?
5. ¿Cómo protejo mi dominio cuando integro con un sistema legado o una API externa?
6. ¿Cuándo tiene sentido aplicar DDD completo vs un enfoque más simple?
