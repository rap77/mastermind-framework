---
source_id: "FUENTE-501"
brain: "brain-software-05-backend"
niche: "software-development"
title: "Clean Architecture: A Craftsman's Guide to Software Structure and Design"
author: "Robert C. Martin (Uncle Bob)"
expert_id: "EXP-005"
type: "book"
language: "en"
year: 2017
isbn: "978-0134494166"
url: "https://www.informit.com/store/clean-architecture-a-craftsmans-guide-to-software-structure-9780134494166"
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

habilidad_primaria: "Diseño de arquitectura limpia y mantenible"
habilidad_secundaria: "Principios SOLID y separación de responsabilidades"
capa: 1
capa_nombre: "Base Conceptual"
relevancia: "CRÍTICA — Es la biblia de arquitectura backend. Sin estos principios el código colapsa al escalar."
gap_que_cubre: "Principios fundamentales de arquitectura y diseño que guían todas las decisiones del Cerebro #5"
---

# FUENTE-501: Clean Architecture

## Tesis Central

> La arquitectura de software es sobre trazar líneas — fronteras — que separan el código de alto nivel (reglas de negocio) del código de bajo nivel (detalles como frameworks, bases de datos e interfaces). Si el negocio no depende de los detalles, el sistema sobrevive a cualquier cambio tecnológico.
> Es la fuente más importante del Cerebro #5 porque establece los principios que hacen que todo lo demás funcione.

---

## 1. Principios Fundamentales

> **P1: La Regla de Dependencia**
> Las dependencias del código fuente deben apuntar ÚNICAMENTE hacia adentro — hacia las políticas de más alto nivel. Nada en un círculo interior puede saber nada sobre algo en un círculo exterior. Entidades → Casos de Uso → Adaptadores → Frameworks.
> *Contexto de aplicación: Siempre. Es la ley fundamental. Si una entidad de dominio importa un ORM, la arquitectura está rota.*

> **P2: Las Entidades son Independientes de Todo**
> Las entidades encapsulan las reglas de negocio más críticas y estables de la empresa. No deben depender de ningún framework, base de datos, ni interfaz. Una entidad `User` no debería saber que existe PostgreSQL.
> *Contexto de aplicación: Al diseñar el dominio. Si una entidad tiene un decorator de Sequelize o TypeORM, se violó este principio.*

> **P3: Los Detalles No Importan (al núcleo)**
> Las bases de datos, frameworks, y UIs son detalles. Las reglas de negocio no deberían saber ni importar qué base de datos usas. Hoy es PostgreSQL, mañana puede ser DynamoDB — el negocio no debería cambiar.
> *Contexto de aplicación: Al decidir dónde colocar lógica. Si cambiar de Express a Fastify requiere reescribir lógica de negocio, la arquitectura falló.*

> **P4: SOLID como Contrato de Diseño**
> — S (Single Responsibility): Un módulo tiene una sola razón para cambiar.
> — O (Open/Closed): Abierto para extensión, cerrado para modificación.
> — L (Liskov Substitution): Los subtipos deben ser sustituibles por sus tipos base.
> — I (Interface Segregation): No forzar a clases a depender de interfaces que no usan.
> — D (Dependency Inversion): Depender de abstracciones, no de concreciones.
> *Contexto de aplicación: Al diseñar cualquier clase, módulo o servicio. Violaciones de SOLID son deuda técnica garantizada.*

> **P5: Screaming Architecture**
> La estructura de carpetas de un sistema debe gritar su propósito de negocio, no su framework. Si ves una carpeta `controllers/` en la raíz, el framework ganó. Si ves `orders/`, `payments/`, `users/`, el negocio ganó.
> *Contexto de aplicación: Al iniciar un proyecto o refactorizar la estructura de carpetas.*

---

## 2. Frameworks y Metodologías

### Framework 1: Clean Architecture — Los 4 Círculos

**Propósito:** Organizar el código en capas concéntricas donde las políticas de negocio no dependen de los detalles de implementación.
**Cuándo usar:** En cualquier sistema que necesite vivir más de 6 meses o que escale en equipo.

**Estructura (de adentro hacia afuera):**

1. **Entities (Dominio)** — Reglas de negocio de la empresa. Las más estables. Objetos con métodos, no solo DTOs. Cero dependencias externas. Ejemplo: `class Order { calculate_total() {...} }`
2. **Use Cases (Aplicación)** — Reglas de negocio de la aplicación. Orquestan el flujo de datos hacia y desde entidades. Definen Interfaces (puertos) que los adaptadores implementarán. Ejemplo: `CreateOrderUseCase`
3. **Interface Adapters (Adaptadores)** — Convierten datos del formato más conveniente para casos de uso al formato más conveniente para el exterior. Controllers, Presenters, Gateways. Aquí vive Express/Fastify.
4. **Frameworks & Drivers (Infraestructura)** — La capa más exterior. Bases de datos, frameworks web, UI. Son detalles intercambiables. Aquí vive PostgreSQL, Redis, S3.

**Regla crítica:** Un módulo en la capa 3 puede importar de la capa 2 y 1. NUNCA al revés.

**Output esperado:** Sistema donde puedes cambiar la base de datos sin tocar los casos de uso, y cambiar el framework web sin tocar el dominio.

---

### Framework 2: SOLID en Práctica

**Propósito:** Guía de decisión para diseñar clases y módulos que sean mantenibles y extensibles.
**Cuándo usar:** Al diseñar nuevas clases o revisar código existente en code review.

**Pasos/Checklist:**
1. **SRP Check:** ¿Qué actores (roles del negocio) usarían esta clase? Si son más de uno, separar.
2. **OCP Check:** ¿Para agregar una nueva funcionalidad necesito modificar código existente? Si sí → usar Strategy Pattern o interfaces.
3. **LSP Check:** ¿Puedo reemplazar esta clase por cualquier subclase sin romper el comportamiento? Si no → rediseñar jerarquía.
4. **ISP Check:** ¿Esta interfaz tiene métodos que algún implementador necesita dejar vacíos? Si sí → dividir la interfaz.
5. **DIP Check:** ¿Esta clase de alto nivel importa directamente una clase de bajo nivel? Si sí → extraer interfaz y usar inyección de dependencias.

**Output esperado:** Código donde agregar features no rompe features existentes (OCP), y donde el testing es trivial porque las dependencias son interfaces.

---

## 3. Modelos Mentales

| Modelo | Descripción | Aplicación Práctica |
|--------|-------------|---------------------|
| **Policy vs Detail** | Las reglas de negocio (policy) son estables y valiosas. Los frameworks y DBs (details) cambian. El dinero está en la policy. | Preguntarse siempre: "¿Esto es negocio o infraestructura?" antes de decidir dónde va el código. |
| **Plugin Architecture** | Los detalles deben conectarse al núcleo como plugins, no al revés. La base de datos es un plugin de tu dominio. | Diseñar interfaces en los casos de uso que los repositorios implementan. Si el ORM desaparece, solo cambias los repositorios. |
| **Boundaries como Decisiones** | Cada frontera en la arquitectura representa una decisión que postergaste deliberadamente. Las buenas arquitecturas maximizan el número de decisiones NO tomadas. | No decidir SQL vs NoSQL en el día 1. Diseñar el repositorio como interfaz y decidir después con más información. |
| **Component Cohesion (REP/CCP/CRP)** | Agrupa en el mismo componente lo que cambia junto (CCP). No incluyas lo que no usan todos (CRP). Agrupa lo que se reutiliza junto (REP). | Al decidir si dos clases van en el mismo módulo o en módulos separados. |
| **Stable vs Volatile** | Los componentes de los que muchos dependen deben ser estables (difíciles de cambiar). Los componentes que cambian mucho deben ser independientes. | Poner las entidades de dominio en el centro porque son estables. Poner integraciones externas en la periferia porque cambian. |

---

## 4. Criterios de Decisión

| Situación | Prioriza | Sobre | Por qué |
|-----------|----------|-------|---------|
| ¿Dónde pongo la lógica de negocio? | Use Case / Entity | Controller / Repository | La lógica de negocio es el valor del sistema. Si está en el controller, no es portable ni testeable. |
| ¿Uso un ORM que acopla las entidades? | Repository Pattern con interfaces | Active Record / ORM directo en dominio | Active Record viola DIP: el dominio conoce la base de datos. |
| ¿Cuándo rompo una clase en dos? | Cuando tiene >1 razón para cambiar (SRP) | Mantenerla unida por conveniencia | Una clase con dos responsabilidades tiene dos fuentes de inestabilidad. |
| ¿Herencia o Composición? | Composición | Herencia profunda | La herencia acopla. La composición es extensible sin modificar. |
| ¿Framework en el dominio? | Nunca | Conveniencia del framework | Si el dominio conoce el framework, cambiar el framework rompe el negocio. |

---

## 5. Anti-patrones

| Anti-patrón | Por qué es malo | Qué hacer en su lugar |
|-------------|-----------------|----------------------|
| **Fat Controller** | El controller tiene lógica de negocio. Es intesteable, no reutilizable, y muere si cambias el framework. | Mover la lógica al Use Case. El controller solo traduce HTTP → Use Case → HTTP. |
| **God Class** | Una clase que sabe y hace todo. Viola SRP. Un cambio en cualquier parte rompe todo. | Dividir por responsabilidad. Si la clase se llama `UserManager` y tiene 30 métodos, está rota. |
| **Active Record en el Dominio** | La entidad `User` tiene métodos `.save()`, `.find()` del ORM. El dominio ahora depende de la base de datos. | Repository Pattern. La entidad es puro dominio. El repositorio implementa la persistencia. |
| **Directorio por Tipo** | Estructura `controllers/`, `models/`, `services/` en raíz. Grita el framework, no el negocio. | Estructura por feature/dominio: `orders/`, `payments/`, `users/`. |
| **Violation de Dependency Rule** | Un use case importa directamente un módulo de infraestructura (ej: `import { PgRepository } from '../infra'`). | Definir interfaz en la capa de use case. Inyectar la implementación concreta desde el exterior. |

---

## 6. Casos y Ejemplos Reales

### Caso 1: Sistema de Pagos — Cambio de Proveedor

- **Situación:** Una fintech usaba Stripe directamente en sus use cases. Stripe cambia precios y necesitan evaluar Braintree.
- **Decisión:** El use case `ProcessPaymentUseCase` tenía `import Stripe` directamente — no había interface.
- **Resultado:** Cambiar de proveedor requirió modificar 47 archivos y 3 semanas. Alta probabilidad de regresiones.
- **Lección:** Con Clean Architecture, el use case depende de `PaymentGatewayInterface`. Solo el adaptador de Stripe cambia. El negocio no se toca.

### Caso 2: Migración de Monolito a Microservicios

- **Situación:** Empresa con 5 años de codebase. Todo en `app.js`. Quieren migrar a microservicios.
- **Decisión:** El código no tenía boundaries. La lógica de `orders` llamaba directamente a `users` y `inventory` internamente.
- **Resultado:** La migración tomó 18 meses en lugar de 6 porque había que entender miles de dependencias implícitas.
- **Lección:** Si los boundaries de dominio están claros desde el inicio (screaming architecture), extraer un microservicio es cortar por la línea ya dibujada.

### Caso 3: Testing de Lógica de Negocio

- **Situación:** Un equipo de 8 devs. Sus tests tardan 45 minutos porque todo testea contra base de datos real.
- **Decisión:** Los use cases tenían dependencias directas de PostgreSQL via ORM.
- **Resultado:** Con repository pattern e inyección de dependencias, los tests de use cases corren con mocks en memoria. De 45 min a 3 min.
- **Lección:** Si puedes mockear los repositorios, puedes testear el 90% de tu lógica sin infraestructura. DIP hace esto posible.

---

## Conexión con el Cerebro #5

| Habilidad del Cerebro | Aporte de esta fuente |
|-----------------------|----------------------|
| Diseño de APIs limpias | La regla de dependencia determina qué sabe el controller vs el use case |
| Modelado de dominio | Entidades sin dependencias externas como base del DDD |
| Decisión SQL vs NoSQL | Repository pattern permite postergar la decisión sin costo |
| Testing | Dependency Inversion hace trivial el testing con mocks |
| Estructura de proyectos | Screaming Architecture como guía de organización de carpetas |
| Separación de responsabilidades | SOLID como contrato de revisión de código |

---

## Preguntas que el Cerebro puede responder

1. ¿Dónde debo poner la lógica de negocio — en el controller, en el service, o en la entidad?
2. ¿Cómo diseño el sistema para que cambiar de base de datos no requiera tocar el dominio?
3. ¿Cómo organizo las carpetas de un proyecto backend para que escale en equipo?
4. ¿Cuándo una clase tiene demasiadas responsabilidades y debo dividirla?
5. ¿Por qué mis tests tardan tanto y cómo hacer que corran sin necesitar la base de datos?
6. ¿Cómo sé si mi arquitectura está bien diseñada? ¿Qué señales busco?
