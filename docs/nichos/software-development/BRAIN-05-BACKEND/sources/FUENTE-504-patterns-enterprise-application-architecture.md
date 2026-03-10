---
source_id: "FUENTE-504"
brain: "brain-software-05-backend"
niche: "software-development"
title: "Patterns of Enterprise Application Architecture"
author: "Martin Fowler"
expert_id: "EXP-005"
type: "book"
language: "en"
year: 2002
isbn: "978-0321127426"
url: "https://www.martinfowler.com/books/eaa.html"
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

habilidad_primaria: "Patrones de arquitectura enterprise: Domain Model, Repository, Unit of Work"
habilidad_secundaria: "Patrones de capa de datos y organización de lógica de negocio"
capa: 2
capa_nombre: "Frameworks"
relevancia: "ALTA — El vocabulario universal de patrones backend. Cada patrón tiene nombre, propósito y cuándo usarlo."
gap_que_cubre: "Catálogo de patrones para organizar la lógica de negocio y la capa de acceso a datos"
---

# FUENTE-504: Patterns of Enterprise Application Architecture (PoEAA)

## Tesis Central

> Los problemas de las aplicaciones enterprise no son únicos — se repiten una y otra vez. Los patrones son soluciones probadas a problemas recurrentes. Conocer su nombre, propósito y trade-offs evita reinventar la rueda y permite comunicar decisiones de diseño con precisión.
> Es el diccionario de patrones que el Cerebro #5 necesita para tener vocabulario preciso.

---

## 1. Principios Fundamentales

> **P1: Los Patrones Son Opciones, No Reglas**
> Un patrón describe una solución a un problema en un contexto. No todos los patrones aplican a todos los problemas. Usar Transaction Script es correcto para lógica simple. Usar Domain Model es correcto cuando la lógica de negocio es compleja y evoluciona.
> *Contexto de aplicación: Al elegir cómo organizar la lógica de negocio. La complejidad del dominio determina el patrón.*

> **P2: Separar Lógica de Negocio de Infraestructura**
> El patrón más importante del libro: la lógica de negocio no debe saber cómo se persisten los datos, ni cómo se presentan. Las tres capas (Presentación, Dominio, Datos) tienen responsabilidades distintas e incompatibles.
> *Contexto de aplicación: Siempre. Si una función de negocio tiene SQL embebido, está violando este principio.*

> **P3: La Complejidad Justifica el Patrón**
> Un CRUD simple no necesita Domain Model. Un sistema de facturación con reglas fiscales complejas sí lo necesita. Aplicar el patrón equivocado (Domain Model para un CRUD) es sobre-ingeniería. Aplicar Transaction Script para lógica compleja es un callejón sin salida.
> *Contexto de aplicación: Al iniciar un módulo. Evaluar la complejidad de la lógica de negocio antes de elegir el patrón.*

---

## 2. Frameworks y Metodologías

### Framework 1: Selección de Patrón de Lógica de Negocio

**Propósito:** Elegir cómo organizar la lógica de negocio según la complejidad del dominio.
**Cuándo usar:** Al iniciar un módulo o aplicación nueva.

**Opciones y cuándo usar cada una:**

| Patrón | Descripción | Cuándo usar | Cuándo NO usar |
|--------|-------------|-------------|----------------|
| **Transaction Script** | Una función por operación de negocio. El script orquesta todo: validación, DB, lógica. | CRUD simple, pocas reglas de negocio, equipo junior. | Cuando la lógica crece: se duplica entre scripts y se vuelve inmanejable. |
| **Table Module** | Una clase por tabla de DB. Métodos estáticos para operaciones. | Sistemas con mucho SQL, lógica acoplada a la DB. | Cuando las reglas de negocio son complejas e independientes de la DB. |
| **Domain Model** | Objetos de negocio ricos con comportamiento. Entidades con métodos que encapsulan reglas. | Lógica de negocio compleja, DDD, proyectos de largo plazo. | CRUD simple — es sobre-ingeniería innecesaria. |
| **Service Layer** | Capa de servicios que define las operaciones disponibles para el cliente. Delega al Domain Model. | Siempre que haya Domain Model. Coordina múltiples entidades y transacciones. | No hay Domain Model — es un anti-patrón si el servicio tiene toda la lógica. |

---

### Framework 2: Patrones de Capa de Datos

**Propósito:** Catálogo de cómo persistir y recuperar objetos de dominio.
**Cuándo usar:** Al diseñar la capa de acceso a datos.

**Los 4 patrones principales:**

1. **Active Record:** El objeto de dominio tiene métodos `.save()`, `.find()`, `.delete()`. El objeto conoce la DB. Simple y rápido para CRUDs. Acoplado. Rails lo usa. Viola Clean Architecture.

2. **Data Mapper:** Un mapper separado mueve datos entre la DB y los objetos de dominio. Los objetos de dominio son puros (sin lógica de DB). TypeORM y Hibernate en modo DataMapper. Preferible para sistemas complejos.

3. **Repository Pattern:** Una abstracción que parece una colección en memoria. `userRepository.findById(id)` — el caller no sabe si hay DB, cache, o API detrás. El patrón más compatible con Clean Architecture.

4. **Unit of Work:** Rastrea todos los cambios a objetos durante una transacción y los persiste al final como una sola operación. Evita múltiples roundtrips a la DB y mantiene consistencia. ORM como Hibernate/TypeORM lo implementan internamente.

---

## 3. Modelos Mentales

| Modelo | Descripción | Aplicación Práctica |
|--------|-------------|---------------------|
| **Anemic vs Rich Domain Model** | Anemic: entidades solo con getters/setters, lógica en servicios. Rich: entidades con comportamiento real. Fowler considera el Anemic Model un anti-patrón. | Si `Order` solo tiene campos y toda la lógica está en `OrderService`, tienes un Anemic Model. |
| **Identity Map** | Garantiza que por cada DB row, solo existe un objeto en memoria. Si `user_id=5` se carga dos veces, es el mismo objeto. Evita problemas de consistencia en memoria. | Los ORMs implementan esto automáticamente. Sin Identity Map, podrías modificar dos copias del mismo usuario en la misma request. |
| **Lazy vs Eager Loading** | Lazy: las relaciones se cargan cuando se acceden. Eager: se cargan junto con el objeto principal. Lazy puede causar N+1. Eager puede sobrecargar si la relación es grande. | Siempre saber qué estrategia usa el ORM por default. Activar eager loading explícitamente para relaciones que siempre se usan. |
| **Optimistic vs Pessimistic Locking** | Pesimista: bloquea el row al leerlo. Nadie más puede modificarlo hasta que se libere. Optimista: agrega un campo `version`, si al guardar la versión cambió, hay conflicto. | Pesimista para operaciones cortas con alta contención. Optimista para la mayoría de casos — mejor rendimiento pero requiere manejo de conflictos. |
| **Value Object vs Entity** | Entity: tiene identidad única (ID). Puede cambiar sus atributos, sigue siendo la misma entidad. Value Object: sin identidad, definido por sus atributos. Dos `Money(100, "USD")` son iguales. | `User` es una Entity. `Money`, `Address`, `DateRange` son Value Objects. Identificarlos correctamente simplifica el código. |

---

## 4. Criterios de Decisión

| Situación | Prioriza | Sobre | Por qué |
|-----------|----------|-------|---------|
| Dominio con pocas reglas de negocio | Transaction Script | Domain Model | El Domain Model tiene costo de diseño que no se amortiza en dominios simples. |
| Dominio complejo con reglas que evolucionan | Domain Model + Repository | Active Record | La separación entre dominio y persistencia permite cambiar ambos independientemente. |
| Relaciones que siempre se usan juntas | Eager Loading | Lazy Loading | Evitar N+1. Si siempre muestras el usuario con sus órdenes, cargarlas juntas es más eficiente. |
| Operaciones de escritura concurrente | Optimistic Locking | Sin locking | Sin locking, dos usuarios pueden sobreescribirse mutuamente silenciosamente. |
| Sistema con múltiples fuentes de datos | Repository Pattern | DAO directo | El Repository abstrae la fuente. Hoy es PostgreSQL, mañana puede ser una API externa. |

---

## 5. Anti-patrones

| Anti-patrón | Por qué es malo | Qué hacer en su lugar |
|-------------|-----------------|----------------------|
| **Anemic Domain Model** | Las entidades son bolsas de datos. Toda la lógica vive en Services. El Service Layer se convierte en un monolito procesal difícil de mantener. | Mover la lógica que pertenece a la entidad adentro de ella. `order.addItem()` en lugar de `orderService.addItemToOrder()`. |
| **Lazy Loading sin control** | Se accede a relaciones sin saber que disparan queries adicionales. En un loop de 100 objetos, puede disparar 100 queries adicionales. N+1 problem. | Usar eager loading explícito para relaciones que siempre se necesitan. Revisar queries generadas por el ORM en development. |
| **God Service** | Un `UserService` con 50 métodos que orquesta todo lo relacionado con usuarios. Viola SRP. Difícil de testear y mantener. | Dividir por caso de uso: `RegisterUserUseCase`, `UpdateProfileUseCase`, `DeactivateUserUseCase`. |
| **SQL en el Domain Model** | La entidad `Order` tiene un método `findByUser()` con SQL embebido. El dominio conoce la base de datos. | Repository Pattern. La entidad es puro dominio. El repositorio tiene el SQL o la lógica de ORM. |
| **Active Record para sistemas complejos** | Active Record acopla el dominio a la DB. Al crecer la lógica de negocio, el objeto se convierte en una mezcla de dominio e infraestructura imposible de separar. | Migrar a Data Mapper + Repository. Separar dominio de persistencia desde el inicio en proyectos de largo plazo. |

---

## 6. Casos y Ejemplos Reales

### Caso 1: Sistema de Facturación — Transaction Script vs Domain Model

- **Situación:** Una startup construye facturación con Transaction Scripts. Funciona para 5 tipos de facturas.
- **Decisión:** Al llegar a 20 tipos con reglas cruzadas (descuentos que dependen del cliente, del producto y del período), el código se duplicó en cada script.
- **Resultado:** Refactorización masiva a Domain Model con entidades `Invoice`, `LineItem`, `DiscountRule` con comportamiento. Los scripts se convirtieron en orquestadores simples.
- **Lección:** Transaction Script funciona hasta que la lógica se vuelve compleja. Reconocer el punto de inflexión antes de acumular deuda técnica masiva.

### Caso 2: E-commerce — Repository Pattern para Múltiples Fuentes

- **Situación:** El catálogo de productos venía de la DB interna, pero ciertos productos venían de una API de proveedor externo.
- **Decisión:** `ProductRepository` como interfaz. `DatabaseProductRepository` y `ApiProductRepository` como implementaciones. El use case no sabe de dónde viene el producto.
- **Resultado:** Agregar nuevas fuentes de productos no modificó ningún use case. Solo se agregó un nuevo Repository.
- **Lección:** Repository abstrae no solo bases de datos — abstrae cualquier fuente de datos. Open/Closed en acción.

### Caso 3: Sistema Bancario — Optimistic Locking

- **Situación:** Dos cajeros procesando la misma cuenta simultáneamente. Sin locking, ambos leen `balance=1000`, ambos descuentan 500, ambos guardan 500. El balance debería ser 0.
- **Decisión:** Campo `version` en la tabla `account`. Al guardar, verificar que la versión no cambió. Si cambió, uno de los dos recibe un conflicto y reintenta.
- **Resultado:** Sin locks a nivel DB, las transacciones concurrentes son correctas. El throughput es alto.
- **Lección:** El Optimistic Locking es el patrón correcto para sistemas con alta concurrencia donde los conflictos son raros pero deben manejarse.

---

## Conexión con el Cerebro #5

| Habilidad del Cerebro | Aporte de esta fuente |
|-----------------------|----------------------|
| Organización de lógica de negocio | Catálogo completo: Transaction Script, Domain Model, Service Layer |
| Capa de acceso a datos | Active Record vs Data Mapper vs Repository con criterios de elección |
| Modelado de dominio | Entity vs Value Object, Rich vs Anemic Domain Model |
| Concurrencia en escritura | Optimistic vs Pessimistic Locking con casos de uso |
| Vocabulario técnico | Nombres precisos para comunicar decisiones en code review |
| Performance de ORM | Lazy vs Eager Loading, Identity Map, Unit of Work |

---

## Preguntas que el Cerebro puede responder

1. ¿Cómo organizo la lógica de negocio — en la entidad, en el servicio, o en el controller?
2. ¿Cuál es la diferencia entre Active Record y Repository Pattern y cuándo usar cada uno?
3. ¿Qué es el Anemic Domain Model y por qué es un anti-patrón?
4. ¿Cómo evito que dos usuarios sobrescriban los datos del otro simultáneamente?
5. ¿Qué es lazy loading y por qué puede matar la performance de mi aplicación?
6. ¿Cuándo tiene sentido usar un Domain Model complejo vs Transaction Scripts simples?
