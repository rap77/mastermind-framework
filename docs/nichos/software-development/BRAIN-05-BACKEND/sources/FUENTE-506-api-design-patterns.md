---
source_id: "FUENTE-506"
brain: "brain-software-05-backend"
niche: "software-development"
title: "API Design Patterns"
author: "JJ Geewax"
expert_id: "EXP-005"
type: "book"
language: "en"
year: 2021
isbn: "978-1617295850"
url: "https://www.manning.com/books/api-design-patterns"
skills_covered: ["H3", "H4"]
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

habilidad_primaria: "Diseño de APIs REST escalables y mantenibles"
habilidad_secundaria: "Versionado, paginación, errores y contratos de API"
capa: 2
capa_nombre: "Frameworks"
relevancia: "ALTA — El Cerebro #5 es el responsable de las APIs que consume el Frontend (#4). Las APIs mal diseñadas son fuente de fricciones permanentes."
gap_que_cubre: "Principios y patrones concretos para diseñar APIs que escalen y sean fáciles de usar"
---

# FUENTE-506: API Design Patterns

## Tesis Central

> Las APIs son contratos públicos. Una vez que alguien las usa, cambiarlas es costoso o imposible. Las APIs bien diseñadas son intuitivas (el desarrollador adivina cómo funcionan), consistentes (los mismos patrones en toda la API), y evolucionables (pueden crecer sin romper clientes existentes).
> Es la guía para que el Cerebro #5 entregue APIs que el Cerebro #4 (Frontend) pueda usar sin fricción.

---

## 1. Principios Fundamentales

> **P1: Las APIs son Para Siempre — Diseña con Esa Mentalidad**
> Una API pública es un contrato que no puedes romper unilateralmente. Agregar campos es seguro (backwards compatible). Eliminar o renombrar campos rompe clientes existentes. El costo de un mal diseño de API es permanente.
> *Contexto de aplicación: Al diseñar cualquier campo o endpoint. "¿Qué pasa si necesito cambiar esto en 6 meses?" es la pregunta obligatoria.*

> **P2: Consistencia es Más Importante que Perfección**
> Una API que usa `user_id` en un endpoint y `userId` en otro es peor que una API que usa siempre `userId` aunque no sea el estilo que preferirías. La consistencia reduce la carga cognitiva del consumidor.
> *Contexto de aplicación: Al agregar un nuevo endpoint, revisar que siga los patrones existentes en nombres, estructura de errores, y respuestas.*

> **P3: Recursos, No Acciones**
> REST diseña sobre recursos (sustantivos), no acciones (verbos). `/users/123/activate` (acción) es peor que `PATCH /users/123 { status: "active" }` (recurso). La excepción son operaciones que genuinamente no encajan en CRUD.
> *Contexto de aplicación: Al definir endpoints. Si el endpoint tiene un verbo en la URL, probablemente puede rediseñarse como una operación sobre un recurso.*

> **P4: Fail Fast y con Mensajes Útiles**
> Un error `400 Bad Request` sin body es inútil. Un error con `{ "code": "INVALID_EMAIL", "message": "El campo email debe ser una dirección válida", "field": "email" }` permite al cliente corregirse sin leer documentación.
> *Contexto de aplicación: Al diseñar el manejo de errores. Cada error debe tener código de error legible por máquina, mensaje legible por humano, y campo afectado si aplica.*

> **P5: Paginación Siempre en Colecciones**
> Ninguna colección debería poder retornar todos sus elementos sin límite. Una tabla de 10 millones de rows sin paginación destruye el servidor y el cliente. Cursor-based pagination escala mejor que offset-based.
> *Contexto de aplicación: Todo endpoint que retorne una lista debe tener paginación. Por defecto, limitar a 20-100 elementos.*

---

## 2. Frameworks y Metodologías

### Framework 1: Estructura Estándar de Respuesta de API

**Propósito:** Asegurar que todas las respuestas de la API sean consistentes y predecibles.
**Cuándo usar:** Al definir los contratos de API de un proyecto nuevo o al estandarizar uno existente.

**Estructura de Respuesta Exitosa:**
```json
{
  "data": { ... },           // El recurso o colección solicitada
  "meta": {                  // Metadatos sobre la respuesta (paginación, etc.)
    "page": 1,
    "per_page": 20,
    "total": 450,
    "next_cursor": "abc123"
  }
}
```

**Estructura de Error:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",           // Código legible por máquina
    "message": "La solicitud tiene errores de validación",  // Mensaje legible por humano
    "details": [                          // Lista de errores específicos
      {
        "field": "email",
        "code": "INVALID_FORMAT",
        "message": "El email debe tener formato válido"
      }
    ]
  }
}
```

**Pasos para definir el contrato:**
1. Listar todos los casos de éxito con sus status codes (200, 201, 204)
2. Listar todos los casos de error con sus status codes (400, 401, 403, 404, 409, 422, 500)
3. Para cada error, definir el código de error y mensaje
4. Documentar en OpenAPI/Swagger

**Output esperado:** Contrato de API documentado que el frontend puede consumir sin ambigüedad.

---

### Framework 2: Estrategia de Versionado de API

**Propósito:** Evolucionar la API sin romper clientes existentes.
**Cuándo usar:** Al diseñar cambios que podrían ser breaking changes.

**Tipos de cambios:**

| Tipo | Ejemplos | ¿Rompe clientes? | Acción |
|------|---------|-----------------|--------|
| **Non-breaking (additive)** | Agregar nuevo campo, nuevo endpoint, nuevo query param opcional | No | Deployar directamente |
| **Breaking** | Renombrar campo, eliminar campo, cambiar tipo de dato, cambiar estructura | Sí | Nueva versión de API |

**Estrategias de versionado:**

1. **URL versioning:** `/v1/users`, `/v2/users` — Más visible, más fácil de documentar. Recomendado para APIs públicas.
2. **Header versioning:** `Accept: application/vnd.api+json;version=2` — Más limpio en URLs pero oculto.
3. **Query param:** `/users?version=2` — Conveniente pero anti-patrón (la version no debería ser un filtro).

**Proceso de deprecación:**
1. Publicar la nueva versión
2. Documentar la deprecación de la versión anterior con fecha de fin de vida
3. Agregar header `Deprecation: true` y `Sunset: fecha` en las respuestas de la versión antigua
4. Desactivar la versión antigua en la fecha prometida

---

## 3. Modelos Mentales

| Modelo | Descripción | Aplicación Práctica |
|--------|-------------|---------------------|
| **API-First Design** | Diseñar el contrato de API (OpenAPI spec) antes de implementar. El frontend y el backend pueden trabajar en paralelo contra el mock. | Publicar el OpenAPI spec al inicio del sprint. Frontend usa Prism o similar para mockear. Backend implementa. |
| **Cursor-based vs Offset Pagination** | Offset (`?page=5&limit=20`) tiene problemas con inserciones/eliminaciones concurrentes. Cursor (`?after=cursor_token`) es estable: apunta a un registro específico. | Para APIs públicas o con alta concurrencia en escrituras, preferir cursor-based. Para dashboards internos simples, offset es aceptable. |
| **Idempotency Keys** | Las operaciones POST (crear) no son idempotentes por naturaleza. Un `Idempotency-Key` en el header permite retransmitir la misma request sin duplicar la operación. | En APIs de pagos o creación de recursos críticos, soportar idempotency keys. Si el cliente reenvía la misma key, retornar el resultado cacheado. |
| **HATEOAS (Hypermedia)** | Las respuestas incluyen links a las acciones disponibles sobre el recurso. El cliente no necesita saber URLs — las descubre en el runtime. Teóricamente ideal, prácticamente poco adoptado. | Conocer el concepto pero no implementarlo en la mayoría de casos. La complejidad raramente vale la pena fuera de APIs muy dinámicas. |
| **Rate Limiting Headers** | Las respuestas incluyen `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` para que los clientes se auto-regulen antes de ser bloqueados. | Siempre retornar estos headers en APIs públicas. El cliente puede implementar backoff automático. |

---

## 4. Criterios de Decisión

| Situación | Prioriza | Sobre | Por qué |
|-----------|----------|-------|---------|
| API para múltiples clientes (web, mobile, third-party) | REST con OpenAPI spec | GraphQL | REST es más cacheable, más simple de versionar, y más familiar. GraphQL agrega complejidad que se justifica solo con muchos clientes con necesidades diferentes. |
| Cliente único con necesidades muy específicas | GraphQL | REST | GraphQL elimina over-fetching y under-fetching cuando el único cliente puede definir exactamente qué necesita. |
| API de alta frecuencia entre servicios internos | gRPC | REST/JSON | gRPC con Protobuf es 5-10x más eficiente en serialización que JSON. Ideal para comunicación interna de alta velocidad. |
| Cambio que rompe backwards compatibility | Nueva versión de API | Modificar en lugar | Los breaking changes sin nueva versión rompen clientes en producción sin previo aviso. |
| Paginación en API pública | Cursor-based | Offset-based | El cursor es estable con datos que cambian. El offset tiene edge cases con inserciones concurrentes. |

---

## 5. Anti-patrones

| Anti-patrón | Por qué es malo | Qué hacer en su lugar |
|-------------|-----------------|----------------------|
| **Verbos en URLs** | `/getUserById`, `/createUser`, `/deleteUser` — no es REST. Los verbos son los HTTP methods. | Sustantivos en URLs: `GET /users/:id`, `POST /users`, `DELETE /users/:id`. |
| **Exponer la estructura interna de la DB** | Campos que son detalles de implementación: `user_table_id`, `created_at_timestamp`. Si cambias la DB, la API cambia. | Diseñar la API para el consumidor, no para el storage. El campo se llama `id` y `created_at` independientemente de cómo se llame en la DB. |
| **Errores genéricos sin información útil** | `{ "error": "Something went wrong" }` — el cliente no sabe qué falló ni cómo corregirlo. | Errores específicos con código, mensaje, y campo afectado. El 400 debe decir exactamente qué está mal. |
| **GET con side effects** | `GET /users/123/activate` — un GET que modifica estado viola HTTP semantics. Los GETs deben ser seguros (safe) e idempotentes. | `POST /users/123/activations` o `PATCH /users/123 { status: "active" }`. Las acciones van en POST o PATCH. |
| **No paginar colecciones** | `GET /transactions` retorna todas las transacciones. Con 10M registros, el servidor muere y la respuesta tarda minutos. | Siempre paginar. Default razonable (20-100). Máximo configurable pero acotado (ej: max 500). |

---

## 6. Casos y Ejemplos Reales

### Caso 1: Stripe API — El Estándar de Oro

- **Situación:** Stripe necesita una API que millones de desarrolladores usen sin fricción.
- **Decisión:** Consistencia absoluta: todos los errores tienen `type`, `code`, `message`. Idempotency keys en todos los POST. Versionado por fecha (`2023-08-16`). Paginación cursor-based en todas las listas.
- **Resultado:** La API de Stripe es frecuentemente citada como la mejor diseñada de la industria. Los developers la adoptan sin leer la documentación completa porque es predecible.
- **Lección:** La consistencia y la predecibilidad son el mayor valor de una API bien diseñada.

### Caso 2: API Breaking Change sin Versionado

- **Situación:** Una startup renombra el campo `name` a `full_name` en `/users`. "Es un cambio pequeño".
- **Decisión:** Deployaron el cambio directamente sin versionar. No tenían clients registrados.
- **Resultado:** Dos aplicaciones mobile en producción dejaron de mostrar nombres de usuario. Eran clientes que nunca se registraron en el portal. Rollback de emergencia.
- **Lección:** Nunca eliminar o renombrar campos en una API que tenga clientes. Deprecar con tiempo, agregar el nuevo campo, luego eliminar el viejo en la siguiente versión mayor.

### Caso 3: Diseño API-First en un Equipo

- **Situación:** Equipo de 4: 2 frontend, 2 backend. El frontend bloqueado esperando las APIs del backend.
- **Decisión:** Adoptar API-First: definir el OpenAPI spec en el día 1 del sprint. El frontend usa Prism para mockear. El backend implementa contra el spec.
- **Resultado:** Frontend y backend trabajaron en paralelo. Al final del sprint, la integración tomó 2 horas en lugar de 2 días. Cero "pero yo esperaba que retornara X".
- **Lección:** El contrato de API definido primero elimina la dependencia entre equipos y las sorpresas de integración.

---

## Conexión con el Cerebro #5

| Habilidad del Cerebro | Aporte de esta fuente |
|-----------------------|----------------------|
| Diseño de APIs REST | Estructura estándar de respuestas, errores, y paginación |
| Contratos entre Frontend y Backend | API-First design como proceso de colaboración |
| Versionado de APIs | Estrategia para evolucionar APIs sin romper clientes |
| Manejo de errores | Framework completo de error codes, mensajes, y HTTP status codes |
| Performance de APIs | Rate limiting, caching headers, paginación eficiente |
| Idempotencia | Idempotency keys para operaciones críticas |

---

## Preguntas que el Cerebro puede responder

1. ¿Cómo estructuro los errores de mi API para que sean útiles para el cliente?
2. ¿Cuándo debo versionar mi API y cómo lo hago correctamente?
3. ¿Cómo diseño la paginación de mis endpoints de colección?
4. ¿Cuándo usar REST vs GraphQL vs gRPC?
5. ¿Qué es el diseño API-First y cómo permite trabajar en paralelo con el equipo de frontend?
6. ¿Cómo hago que las operaciones de mi API sean seguras de reintentar?
