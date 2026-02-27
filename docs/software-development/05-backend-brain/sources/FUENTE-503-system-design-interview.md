---
source_id: "FUENTE-503"
brain: "brain-software-05-backend"
niche: "software-development"
title: "System Design Interview: An Insider's Guide (Vol 1 & 2)"
author: "Alex Xu"
expert_id: "EXP-005"
type: "book"
language: "en"
year: 2020
isbn: "978-1736049211"
url: "https://www.systemdesigninterview.com"
skills_covered: ["H3", "H4", "H5"]
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

habilidad_primaria: "System design a escala — de 1 usuario a 100 millones"
habilidad_secundaria: "Patrones de diseño de sistemas: rate limiting, cache, CDN, load balancer"
capa: 1
capa_nombre: "Base Conceptual"
relevancia: "CRÍTICA — Provee el vocabulario, los patrones, y el proceso de pensamiento para diseñar cualquier sistema backend a escala."
gap_que_cubre: "Framework de pensamiento para escalar sistemas desde zero hasta cientos de millones de usuarios"
---

# FUENTE-503: System Design Interview (Vol 1 & 2)

## Tesis Central

> Diseñar un sistema es un proceso iterativo de hacer trade-offs explícitos. No hay respuestas correctas únicas — hay decisiones con ventajas y desventajas que deben ser entendidas y comunicadas claramente. El dominio de estos patrones convierte al backend engineer en alguien que diseña sistemas que escalan, no solo código que funciona.
> Es el manual de construcción de sistemas que duran y escalan.

---

## 1. Principios Fundamentales

> **P1: Escala en Fases — No Sobre-Ingeniería desde el Día 1**
> Un sistema para 1,000 usuarios no necesita la arquitectura de Twitter. Diseña para la escala actual +1 orden de magnitud. Luego itera. La complejidad prematura mata más startups que la falta de escalabilidad.
> *Contexto de aplicación: Al tomar decisiones arquitectónicas. Pregunta: ¿Cuántos usuarios tenemos hoy y en 6 meses? Diseña para eso.*

> **P2: Los Números Importan — Estima Antes de Decidir**
> Back-of-the-envelope calculations: estimar QPS (queries por segundo), almacenamiento necesario, y ancho de banda antes de diseñar. Un sistema con 1,000 QPS necesita decisiones distintas que uno con 1,000,000 QPS.
> *Contexto de aplicación: Al inicio de cualquier diseño de sistema. "¿Cuántos requests por segundo?" es la primera pregunta.*

> **P3: Stateless > Stateful para Escalabilidad Horizontal**
> Los servidores stateful (que guardan sesión en memoria) no pueden escalarse horizontalmente. Mueve el estado a Redis o una DB. Los servidores stateless son intercambiables — puedes agregar 10 más detrás de un load balancer sin fricción.
> *Contexto de aplicación: Al diseñar cualquier servidor web. Si la sesión está en memoria del servidor, no puedes escalar horizontalmente.*

> **P4: Cache Donde Puedas, Invalida con Cuidado**
> El cache es la diferencia entre una query de 200ms y una de 1ms. Pero el cache introduce problemas de invalidación. "There are only two hard problems in CS: cache invalidation and naming things." — Phil Karlton.
> *Contexto de aplicación: Identificar los datos más leídos y menos cambiados. Cachear agresivamente. Definir TTL y estrategia de invalidación explícita.*

> **P5: Diseña para el Fallo — Fault Tolerance**
> Todo falla en producción. Discos, redes, servicios externos. Un sistema resiliente asume que cualquier componente puede fallar y tiene un plan: retries con backoff exponencial, circuit breakers, fallbacks graceful.
> *Contexto de aplicación: Al diseñar integraciones con servicios externos. ¿Qué le pasa al usuario si Stripe cae? Si la respuesta es "el sistema también cae", hay trabajo por hacer.*

---

## 2. Frameworks y Metodologías

### Framework 1: El Proceso de Diseño de Sistemas (4 Pasos)

**Propósito:** Proceso estructurado para abordar cualquier problema de diseño de sistema de forma completa.
**Cuándo usar:** Al diseñar un sistema nuevo, al escalar uno existente, o al evaluar propuestas arquitectónicas.

**Pasos:**
1. **Entender el Problema y el Alcance (5-10 min):**
   - ¿Qué features necesitamos? ¿Cuáles no?
   - ¿Cuántos usuarios? ¿Cuál es el patrón de uso? (DAU, pico de tráfico)
   - ¿Qué importa más: consistencia o disponibilidad?
   - ¿Qué escala de datos? ¿Cuánto almacenamiento en 5 años?

2. **Propuesta de Alto Nivel (10-15 min):**
   - Diagrama simple: clients → API → services → DB
   - Identificar los componentes principales
   - Identificar si es read-heavy o write-heavy
   - Elegir el tipo de base de datos (SQL vs NoSQL)

3. **Deep Dive en Componentes Críticos (20-25 min):**
   - ¿Cómo funciona el servicio más crítico?
   - ¿Cómo se diseña el schema de datos?
   - ¿Cómo se maneja la consistencia?
   - ¿Dónde va el cache?

4. **Wrap Up — Optimizaciones y Edge Cases:**
   - ¿Qué cuellos de botella hay?
   - ¿Cómo monitorear el sistema?
   - ¿Qué pasa en el peor caso? (failure scenarios)

**Output esperado:** Diseño documentado con componentes, trade-offs, y justificaciones explícitas.

---

### Framework 2: Escala Progresiva — Evolución del Sistema

**Propósito:** Guía de cuándo y cómo agregar componentes de escalabilidad.
**Cuándo usar:** Al planificar la arquitectura de un sistema que va a crecer.

**Etapas:**

| Usuarios | Arquitectura | Componentes clave |
|----------|-------------|-------------------|
| 1 - 1K | Monolito simple | 1 servidor, 1 DB. No compliques. |
| 1K - 10K | Separar Web + DB | Web server y DB en servidores distintos. Agregar caché básico. |
| 10K - 100K | Load Balancer + Replicas | LB con múltiples web servers. Read replicas en DB. CDN para assets. |
| 100K - 1M | Caché distribuido + Sharding | Redis cluster. DB sharding por user_id. Separar servicios críticos. |
| 1M+ | Microservicios + Message Queue | Descomponer por dominio. Kafka para eventos. DB por servicio. |

---

## 3. Modelos Mentales

| Modelo | Descripción | Aplicación Práctica |
|--------|-------------|---------------------|
| **Read-heavy vs Write-heavy** | La mayoría de los sistemas son read-heavy (10:1 ratio). Esto determina dónde invertir en optimización. | Si el sistema es 90% lecturas, optimizar el camino de lectura: cache, read replicas, CDN. |
| **Hot Spot Problem** | Si se particiona por un atributo no distribuido uniformemente (ej: `celebrity_id`), un nodo recibe mucho más carga que otros. | Elegir sharding keys que distribuyan la carga uniformemente. Considerar hashing consistente. |
| **Long Tail of Requests** | La latencia del percentil 99 (p99) es más importante que la media. Los usuarios con peor experiencia definen la percepción del producto. | Monitorear latencia en p50, p95, p99. Optimizar los outliers, no solo el promedio. |
| **Circuit Breaker** | Cuando un servicio está fallando, en lugar de acumular requests fallidos (que consumen recursos), el circuit breaker "abre" y retorna un error rápido o un fallback. | Implementar con libraries como `hystrix` o `resilience4j`. Definir qué retornar cuando el circuit está abierto. |
| **Eventual Consistency como Contrato** | En sistemas distribuidos con replicación asíncrona, los datos eventualmente serán consistentes. El "eventual" puede ser milisegundos o segundos. | Comunicarlo explícitamente en la API: "Este dato puede tener hasta 30 segundos de lag". No sorprender al cliente. |

---

## 4. Criterios de Decisión

| Situación | Prioriza | Sobre | Por qué |
|-----------|----------|-------|---------|
| Reducir latencia de lectura | Cache (Redis) primero | Optimizar DB | El cache puede ser 100x más rápido que la DB. Es el cambio de mayor impacto. |
| Sistema con muchas lecturas de archivos/media | CDN | Servir desde el servidor | Una CDN sirve desde el edge cercano al usuario. El servidor central no escala para este caso. |
| Desacoplar servicios que procesan a diferente velocidad | Message Queue (Kafka/RabbitMQ) | Llamadas síncronas | La cola absorbe picos. El consumer procesa a su ritmo. Los servicios no se conocen. |
| Alta disponibilidad vs Consistencia | Depende del dominio | No hay default | Finanzas: consistencia. Redes sociales: disponibilidad. Definirlo explícitamente antes de diseñar. |
| Sessions y datos temporales | Redis / Memcached | Almacenar en DB | Redis en memoria es el lugar natural para sesiones. La DB no debe cargar con datos efímeros. |

---

## 5. Anti-patrones

| Anti-patrón | Por qué es malo | Qué hacer en su lugar |
|-------------|-----------------|----------------------|
| **Single Point of Failure (SPOF)** | Si un componente falla y no hay redundancia, el sistema completo cae. | Identificar todos los SPOFs y agregar redundancia. Load balancers, read replicas, múltiples availability zones. |
| **Sincronismo excesivo entre microservicios** | Si el servicio A llama síncronamente al B, que llama al C, la latencia se acumula y el fallo de C afecta a A. | Usar eventos asíncronos donde sea posible. Si A publica un evento y B lo consume, B puede caer sin afectar a A. |
| **Cache sin estrategia de invalidación** | Los datos del cache son inconsistentes con la DB. Los usuarios ven datos obsoletos indefinidamente. | Definir TTL explícito. Usar cache-aside pattern: invalidar el cache al escribir en DB. |
| **No estimar antes de elegir tecnología** | Elegir Kafka para un sistema de 100 QPS es sobredimensionamiento. Aumenta costo y complejidad sin beneficio. | Hacer back-of-the-envelope calculations primero. La tecnología correcta depende del volumen. |
| **Monolito como sinónimo de malo** | Muchos equipos rompen en microservicios prematuramente antes de entender las boundaries del dominio. El resultado son microservicios acoplados que son peores que el monolito. | Empezar con un monolito bien estructurado. Extraer microservicios cuando los boundaries estén claros y el volumen lo justifique. |

---

## 6. Casos y Ejemplos Reales

### Caso 1: URL Shortener (bit.ly style)

- **Situación:** Diseñar un sistema que acorte URLs y redireccione al destino. 100M URLs, 10B redirects/día.
- **Diseño:** Encodificar el ID numérico en base62 para generar el short code. DB para persistencia. Cache agresivo para lecturas (999:1 ratio read/write). CDN para distribución global.
- **Resultado:** La clave del diseño es que es extreme read-heavy. Cada short URL se crea una vez y se lee millones de veces.
- **Lección:** Identificar el ratio read/write es el primer paso. Determina toda la arquitectura de cache y replicación.

### Caso 2: Rate Limiter

- **Situación:** Proteger una API de abuso. Máximo 5 requests por segundo por usuario.
- **Diseño:** Token Bucket algorithm en Redis. Key: `rate_limit:{user_id}`. En cada request, decrementar el bucket. Si llega a 0, rechazar con 429.
- **Resultado:** Redis permite operaciones atómicas (INCR + EXPIRE) que hacen el rate limiting correcto incluso con múltiples instancias del servidor.
- **Lección:** Redis es el lugar natural para estado compartido entre instancias stateless. Sessions, rate limits, distributed locks.

### Caso 3: Feed de Noticias (Instagram/Facebook style)

- **Situación:** Mostrar el feed de posts de las personas que sigues. 1M DAU, usuarios con hasta 5,000 amigos.
- **Decisión A (Pull):** Al abrir el feed, calcular posts de todos los amigos. Muy costoso para usuarios con muchos contactos.
- **Decisión B (Push/Fanout):** Al publicar, escribir en el feed de cada seguidor. Costoso para influencers con millones de followers.
- **Solución híbrida:** Push para usuarios normales, pull para celebrities. Merge en el momento de lectura.
- **Lección:** Los sistemas complejos frecuentemente requieren soluciones híbridas. Los trade-offs no son binarios.

---

## Conexión con el Cerebro #5

| Habilidad del Cerebro | Aporte de esta fuente |
|-----------------------|----------------------|
| Diseño de sistemas escalables | Proceso de 4 pasos para diseñar cualquier sistema de forma estructurada |
| Selección de componentes | Cuándo agregar cache, CDN, message queue, sharding según el volumen |
| Estimaciones de capacidad | Back-of-the-envelope calculations para justificar decisiones técnicas |
| Fault tolerance | Circuit breaker, retries, fallbacks como patrones de diseño |
| Trade-offs explícitos | Lenguaje y framework para comunicar ventajas/desventajas de cada decisión |
| Arquitectura evolutiva | Escala progresiva: no sobre-ingenierizar el día 1 |

---

## Preguntas que el Cerebro puede responder

1. ¿Cómo diseño un sistema que soporte 1 millón de usuarios?
2. ¿Cuándo debo agregar un cache y de qué tipo?
3. ¿Cómo diseño el sistema para que no tenga un único punto de fallo?
4. ¿Cuándo descomponer en microservicios y cuándo mantener el monolito?
5. ¿Cómo estimo cuánto almacenamiento, ancho de banda, y QPS necesita mi sistema?
6. ¿Cómo diseño un rate limiter o un sistema de notificaciones a escala?
