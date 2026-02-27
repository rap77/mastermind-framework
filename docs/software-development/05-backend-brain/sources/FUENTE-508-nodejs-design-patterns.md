---
source_id: "FUENTE-508"
brain: "brain-software-05-backend"
niche: "software-development"
title: "Node.js Design Patterns: Design and Implement Production-Grade Node.js Applications"
author: "Mario Casciaro & Luciano Mammino"
expert_id: "EXP-005"
type: "book"
language: "en"
year: 2020
isbn: "978-1839214110"
url: "https://www.nodejsdesignpatterns.com"
skills_covered: ["H2", "H3", "H5"]
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

habilidad_primaria: "Patrones de diseño en Node.js — asincronía, streams, y arquitectura"
habilidad_secundaria: "Performance, escalabilidad, y patrones de concurrencia en Node.js"
capa: 2
capa_nombre: "Frameworks"
relevancia: "ALTA — Node.js es el runtime predominante en el stack del proyecto. Sus particularidades (event loop, non-blocking I/O) requieren patrones específicos."
gap_que_cubre: "Patrones específicos de Node.js que no cubren los libros agnósticos de lenguaje"
---

# FUENTE-508: Node.js Design Patterns

## Tesis Central

> Node.js no es un servidor web — es una plataforma para I/O asíncrono no bloqueante. Sus superpoderes (alto throughput, bajo footprint) vienen de entender cómo funciona el event loop y cómo escribir código que nunca lo bloquea. Los patrones de Node.js no son los patrones de Java — son específicos al paradigma de programación asíncrona y reactiva.
> Cubre el gap del stack tecnológico específico que Clean Architecture y DDIA no abordan.

---

## 1. Principios Fundamentales

> **P1: No Bloquear el Event Loop — Nunca**
> Node.js usa un solo thread. Si el event loop se bloquea (operación CPU-intensiva, sync I/O, while infinito), TODOS los requests esperan. Un loop que tarda 100ms bloquea el servidor completo durante ese tiempo.
> *Contexto de aplicación: Siempre. CPU-intensive tasks van en Worker Threads o en un servicio separado. Todo I/O es async.*

> **P2: Callbacks → Promises → Async/Await es una Evolución**
> El "callback hell" fue el primer patrón de Node.js. Las Promises lo mejoraron. Async/Await es la forma actual de escribir código asíncrono legible. Mezclar los tres en un mismo proyecto crea deuda técnica.
> *Contexto de aplicación: En proyectos nuevos, usar async/await exclusivamente. Al trabajar con APIs que retornan callbacks, promisificarlas con `util.promisify`.*

> **P3: Fail Fast — Manejar Errores en Cada Nivel**
> En Node.js, los errores no manejados en Promises crashean el proceso (en versiones modernas). El patrón `try/catch` en async/await es obligatorio. Los errores deben manejarse en el nivel correcto, no propagarse silenciosamente.
> *Contexto de aplicación: Todo `await` dentro de `try/catch` o con manejo de error explícito. Nunca `.catch(console.error)` sin más — eso silencia el error.*

> **P4: Streams para Datos Grandes**
> Cargar un archivo de 1GB en memoria con `fs.readFile` mata el servidor. Los Streams procesan datos en chunks sin cargarlos completos. Son el patrón correcto para archivos, responses HTTP grandes, o procesamiento de datos.
> *Contexto de aplicación: Al procesar archivos, al hacer pipe de datos entre fuentes, al enviar respuestas grandes. `fs.createReadStream().pipe(response)` en lugar de `fs.readFile()`.*

> **P5: The Module System como Herramienta de Diseño**
> Los módulos de Node.js son singletons (se cachean). Un módulo de base de datos importado en múltiples lugares retorna la misma instancia. Esto puede ser una feature (compartir conexión) o un bug (estado global inesperado).
> *Contexto de aplicación: Al diseñar módulos que deben ser singletons (DB connection, logger, config). Y al diseñar módulos que NO deben serlo (factories que crean nuevas instancias).*

---

## 2. Frameworks y Metodologías

### Framework 1: Patrones de Asincronía

**Propósito:** Elegir el patrón correcto para cada tipo de operación asíncrona.
**Cuándo usar:** Al escribir cualquier operación asíncrona en Node.js.

| Patrón | Caso de Uso | Ejemplo |
|--------|-------------|---------|
| **Async/Await** | Mayoría de casos. Código secuencial asíncrono. | `const user = await userRepo.findById(id)` |
| **Promise.all()** | Operaciones independientes en paralelo. | `const [user, orders] = await Promise.all([getUser(), getOrders()])` |
| **Promise.allSettled()** | Operaciones paralelas donde algunas pueden fallar. | Múltiples llamadas a APIs externas donde algunas pueden estar caídas. |
| **Streams** | Datos de tamaño desconocido o muy grande. | Procesar un CSV de 10GB, servir un video, upload de archivos. |
| **EventEmitter** | Comunicación desacoplada dentro de un proceso. | Notificar a múltiples partes del sistema cuando algo ocurre. |
| **Worker Threads** | CPU-intensive tasks que no pueden bloquearse. | Procesamiento de imágenes, criptografía pesada, parsing complejo. |

---

### Framework 2: Arquitectura de una Aplicación Node.js

**Propósito:** Organizar una aplicación Node.js/Express/Fastify con separación de responsabilidades.
**Cuándo usar:** Al iniciar un proyecto o al refactorizar uno sin estructura.

**Estructura recomendada:**
```
src/
  domain/           # Entidades, Value Objects, Domain Services (cero deps de Node.js)
  application/      # Use Cases, Application Services
  infrastructure/   # DB, cache, queues, external APIs
    database/       # Repositorios con ORM
    cache/          # Redis adapter
    messaging/      # Kafka/RabbitMQ adapters
  interfaces/       # HTTP controllers, GraphQL resolvers, CLI commands
    http/
      routes/
      middlewares/
      controllers/
  shared/           # Utils, errors, logger
index.ts            # Bootstrap y DI container
```

**Reglas:**
- `domain/` no importa nada de `infrastructure/` o `interfaces/`
- `application/` solo importa de `domain/`
- `infrastructure/` e `interfaces/` implementan las interfaces definidas en `domain/` y `application/`
- El `index.ts` ensambla todo: instancia los repositorios concretos e inyecta en los use cases

---

## 3. Modelos Mentales

| Modelo | Descripción | Aplicación Práctica |
|--------|-------------|---------------------|
| **Event Loop como Concierge** | El event loop es como un concierge en un hotel. No hace el trabajo (limpiar habitaciones, cocinar) — delega. Él solo organiza: "cuando termines de limpiar, avísame". Si el concierge se pone a limpiar él mismo, todo el hotel se detiene. | Nunca poner trabajo CPU-intensivo en el thread principal. El event loop delega todo a I/O asíncrono y Worker Threads. |
| **Backpressure en Streams** | Cuando el consumer de un Stream no puede procesar tan rápido como el producer produce, el buffer se llena. Sin backpressure, la memoria explota. `pipe()` maneja backpressure automáticamente. | Siempre usar `pipe()` o el pipe operator de streams en lugar de manejar manualmente los eventos `data`. |
| **Error-First Callbacks (legacy)** | El primer argumento de un callback es siempre el error. `callback(err, data)`. Si `err` es truthy, algo falló. Patrón de Node.js original que sigue en muchas APIs del core. | Al trabajar con APIs legacy de callbacks, siempre verificar el primer argumento antes de usar el segundo. |
| **Graceful Shutdown** | Al recibir SIGTERM, el proceso debe terminar las operaciones pendientes, cerrar conexiones de DB, y luego cerrarse. Sin graceful shutdown, requests en vuelo fallan y la DB puede tener operaciones incompletas. | Implementar handlers para SIGTERM y SIGINT. Usar `server.close()` y `db.disconnect()` antes de `process.exit()`. |
| **Connection Pooling** | Abrir una conexión a la DB por request es costoso (handshake, autenticación). Un pool de conexiones mantiene un conjunto abierto y las reutiliza. | Configurar el pool según el número de conexiones que la DB puede manejar. Default de `pg` es 10. |

---

## 4. Criterios de Decisión

| Situación | Prioriza | Sobre | Por qué |
|-----------|----------|-------|---------|
| Múltiples queries independientes | `Promise.all()` | `await` secuencial | `Promise.all()` ejecuta en paralelo. Si cada query tarda 100ms, 3 en secuencia = 300ms. En paralelo = 100ms. |
| Procesamiento de archivos grandes | Streams | Leer completo en memoria | Un archivo de 1GB leído completo ocupa 1GB en RAM. Un Stream lo procesa en chunks de 64KB. |
| Operación CPU-intensiva | Worker Thread | Main thread | Bloquear el main thread afecta todos los requests simultáneos. Workers usan cores separados. |
| Estado compartido entre módulos | Module singleton | Variables globales | Los módulos de Node se cachean — son singletons naturales. Las variables globales son menos predecibles. |
| Framework HTTP | Fastify | Express (para proyectos nuevos) | Fastify es 2-3x más rápido que Express, tiene schema validation integrado, y mejor TypeScript support. |

---

## 5. Anti-patrones

| Anti-patrón | Por qué es malo | Qué hacer en su lugar |
|-------------|-----------------|----------------------|
| **Callback Hell** | Callbacks anidados 5+ niveles. Ilegible, imposible de debuggear, el manejo de errores es un caos. | Usar async/await. Promisificar callbacks legacy con `util.promisify`. |
| **Await en loop** | `for (const item of items) { await processItem(item) }` — procesa uno por uno, en secuencia. Si hay 100 items de 100ms cada uno = 10 segundos. | `await Promise.all(items.map(item => processItem(item)))` — todos en paralelo. Con control de concurrencia si es necesario: `p-limit`. |
| **Swallowing errors** | `.catch(err => console.log(err))` — el error se logea y la ejecución continúa como si nada. El estado del sistema puede ser inconsistente. | Manejar el error adecuadamente: retornar error al cliente, reintentar, o propagar arriba para que el handler global lo maneje. |
| **Sync operations en server** | `fs.readFileSync()` o `crypto.pbkdf2Sync()` en un request handler. Bloquea el event loop. | Usar siempre las versiones async: `fs.readFile()`, `crypto.pbkdf2()` o `bcrypt.hash()`. |
| **Conexiones sin pool** | Crear una nueva conexión de DB por request. El overhead de conexión es alto. La DB tiene un límite de conexiones concurrentes. | Usar connection pool del cliente de DB (pg-pool, mongoose connection pool, Prisma connection pool). |

---

## 6. Casos y Ejemplos Reales

### Caso 1: API que Procesaba Imágenes — Blocking Event Loop

- **Situación:** Un endpoint `/resize-image` usaba `sharp` (operación CPU-intensiva) directamente en el request handler. Con 10 requests concurrentes, los otros 9 esperaban en cola.
- **Decisión:** Mover el procesamiento de imágenes a Worker Threads con `workerpool`.
- **Resultado:** De 10 requests atascados a procesamiento verdaderamente concurrente usando los 4 cores del servidor.
- **Lección:** CPU-intensive en Node.js = Worker Threads. Sin excepción.

### Caso 2: Export CSV de 500,000 Rows — Memory Crash

- **Situación:** Endpoint que exportaba todos los registros como CSV. Funcionaba bien con 1,000 registros. Con 500,000 registros, el servidor tenía Out of Memory.
- **Decisión:** Reescribir usando Streams. La DB retorna un cursor. Se convierte a CSV stream. Se pipe al response HTTP.
- **Resultado:** Exportar 500,000 registros con 2MB de RAM en lugar de 500MB. El cliente recibe el CSV en streaming, sin esperar que termine todo.
- **Lección:** Streams son el patrón correcto siempre que el volumen de datos sea desconocido o grande.

### Caso 3: Await Secuencial en Hot Path

- **Situación:** Endpoint de checkout que hacía 5 queries en secuencia: usuario, carrito, inventario, precios, descuentos. Latencia: 400ms.
- **Decisión:** Identificar que las 5 queries eran independientes. Cambiar a `Promise.all()`.
- **Resultado:** Latencia de 400ms a 85ms. El backend no cambió ninguna lógica — solo el orden de ejecución.
- **Lección:** Queries independientes en paralelo es una de las optimizaciones de mayor impacto con menor riesgo.

---

## Conexión con el Cerebro #5

| Habilidad del Cerebro | Aporte de esta fuente |
|-----------------------|----------------------|
| Performance de APIs | Event loop, async/await, Promise.all — patrones para alta concurrencia |
| Procesamiento de datos | Streams para datos grandes sin consumo excesivo de memoria |
| Arquitectura de aplicación | Estructura de carpetas recomendada para Node.js con Clean Architecture |
| Concurrencia | Worker Threads para CPU-intensive, Promise.all para I/O paralelo |
| Error handling | Manejo correcto de errores en código async |
| Producción | Connection pooling, graceful shutdown, configuración para producción |

---

## Preguntas que el Cerebro puede responder

1. ¿Por qué mi servidor Node.js se torna lento bajo carga y cómo solucionarlo?
2. ¿Cuándo usar `Promise.all()` vs `await` secuencial?
3. ¿Cómo procesar un archivo CSV de 1GB sin que el servidor tenga Out of Memory?
4. ¿Cómo ejecutar código CPU-intensivo en Node.js sin bloquear el servidor?
5. ¿Cómo organizo las carpetas de mi proyecto Node.js para que escale en equipo?
6. ¿Cómo implemento un graceful shutdown correcto en producción?
