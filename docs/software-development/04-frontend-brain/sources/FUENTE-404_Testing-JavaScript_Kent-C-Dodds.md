---
source_id: "FUENTE-404"
brain: "brain-software-04-frontend-architecture"
niche: "software-development"
title: "Testing JavaScript & Epic React — Testing Library Philosophy and Patterns"
author: "Kent C. Dodds"
expert_id: "EXP-404"
type: "course"
language: "en"
year: 2021
isbn: "N/A"
url: "https://testingjavascript.com / https://epicreact.dev"
skills_covered: ["H5", "H6", "H7"]
distillation_date: "2026-02-26"
distillation_quality: "complete"
loaded_in_notebook: true
version: "1.0.0"
last_updated: "2026-02-26"
changelog:
  - version: "1.0.0"
    date: "2026-02-26"
    changes:
      - "Ficha creada con destilación completa"
      - "Formato estándar del MasterMind Framework v2"
status: "active"

habilidad_primaria: "Testing de Frontend — Unit, Integration, E2E con la filosofía correcta"
habilidad_secundaria: "React Testing Patterns & Confidence en Deployments"
capa: 2
capa_nombre: "Frameworks Operativos"
relevancia: "CRÍTICA — El testing no es opcional; es lo que permite refactorizar sin miedo y deployar con confianza. El testing mal hecho (tests que testean implementación, no comportamiento) da falsa seguridad y se rompe con cada refactor."
---

# FUENTE-404: Testing JavaScript & Epic React
## Kent C. Dodds | Testing de Frontend con Propósito

---

## Tesis Central

> "Cuanto más tus tests se parecen a cómo los usuarios usan tu software, más confianza te dan." — KCD
>
> Los tests mal escritos testean la implementación, no el comportamiento. Se rompen con cada refactor aunque el producto funcione perfectamente. Los tests bien escritos testean lo que el usuario hace y ven, y solo se rompen cuando realmente algo deja de funcionar.

La pregunta de cada test: "¿Estaría roto esto si el usuario lo usara?" Si la respuesta es no, el test no aporta confianza real.

---

## 1. Principios Fundamentales

> **P1: Testea comportamiento, no implementación**
> Los tests deben verificar qué hace el componente desde la perspectiva del usuario, no cómo lo hace internamente. Si testeas que un método se llama con ciertos argumentos, el test se rompe cuando refactorizas el internals aunque el resultado sea idéntico para el usuario.
> *Aplicación: en Testing Library, interactúa con el DOM como lo haría el usuario (click, type, find by role/text) en lugar de llamar métodos de instancia directamente.*

> **P2: El Trofeo de Testing — Integration tests son los más valiosos**
> El "Testing Trophy" (Kent) vs la "Pirámide de Testing" (Google): Los tests de integración dan el mejor ROI. Los unit tests son rápidos pero no verifican que las piezas funcionan juntas. Los E2E son lentos y frágiles pero verifican el flujo completo. La integración equilibra velocidad y confianza.
> *Aplicación: la mayoría del tiempo de testing debe ir en integration tests (componentes con sus hooks, context, y dependencias reales o mocked).*

> **P3: Evita implementación details como text de queries**
> Testear buscando por clase CSS, por data-testid genéricos, o por estructura HTML específica acopla el test a detalles de implementación. Cuando el HTML refactoriza, el test se rompe aunque la funcionalidad sea igual.
> *Aplicación: preferir queries por role (`getByRole`), texto visible (`getByText`), label (`getByLabelText`). Estas queries fallan solo si la accesibilidad o el texto cambia, lo cual es correcto.*

> **P4: Los mocks deben ser simples y estar cerca de la realidad**
> Mocks complejos que replican comportamiento interno son otro tipo de implementation detail. Un mock de un servidor HTTP con MSW es más real y más mantenible que moquear módulos individuales de fetch.
> *Aplicación: usar Mock Service Worker (MSW) para moquear la capa de red, no cada función de fetch. El componente no sabe que está testeándose.*

> **P5: Un test que nunca puede fallar no tiene valor**
> Si un test siempre pasa independientemente de si la funcionalidad está rota, es peor que no tener el test (da falsa confianza). Antes de mergear un test, verificar que falla cuando el comportamiento que testea está roto.
> *Aplicación: "TDD": escribir el test primero, ver que falla, implementar hasta que pase. Esto garantiza que el test es significativo.*

---

## 2. Frameworks y Metodologías

### Framework 1: El Testing Trophy — Distribución de Tests

**Propósito:** Distribuir el esfuerzo de testing para máxima confianza con mínimo costo de mantenimiento.

```
          /‾‾‾‾‾‾‾‾‾‾‾‾\
         /  E2E (pocos)  \         → Cypress, Playwright
        /‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\
       / Integration (mayoría) \   → React Testing Library + MSW
      /‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\
     /    Unit (funciones puras)  \ → Jest / Vitest
    /‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\
   /    Static (TypeScript, ESLint)  \  → Sin ejecutar

DISTRIBUCIÓN RECOMENDADA:
  Static:      No cuentan como "tests" — son gratuitos con TS/ESLint
  Unit:        ~20% — Solo para funciones puras y utils complejos
  Integration: ~60% — La mayoría; componentes con dependencias reales
  E2E:         ~20% — Solo flujos críticos (checkout, login, onboarding)
```

---

### Framework 2: Queries de Testing Library — Jerarquía de Preferencia

**Propósito:** Elegir la query más accesible y resistente al refactor para cada caso.

```
JERARQUÍA (de más a menos recomendada):

1. getByRole — el más accesible y semántico
   → getByRole('button', { name: /enviar/i })
   → getByRole('textbox', { name: /nombre/i })
   → getByRole('heading', { level: 2 })

2. getByLabelText — para inputs con labels
   → getByLabelText(/correo electrónico/i)

3. getByPlaceholderText — solo si no hay label (mal diseño)
   → getByPlaceholderText(/buscar/i)

4. getByText — para texto visible que no es interactive
   → getByText(/bienvenido/i)

5. getByDisplayValue — para inputs con valor actual

6. getByAltText — para imágenes

7. getByTitle — último recurso

8. getByTestId — SOLO si ninguna otra aplica
   → Acopla a data-testid; cambiar el DOM rompe el test
```

**Por qué `getByRole` es la mejor opción:**
- Si el elemento no tiene el rol correcto, el test falla → incentiva la accesibilidad
- No se rompe si el HTML estructura cambia, solo si la semántica cambia
- Los accesibilidad names son legibles por humanos

---

### Framework 3: Anatomía de un Test de Integración con RTL

**Propósito:** Estructura estándar para tests de componentes React con todas las dependencias.

```javascript
// Setup — una sola vez por archivo
import { render, screen, userEvent } from '@testing-library/react'
import { server } from '../mocks/server' // MSW server
import { LoginForm } from './LoginForm'

// Wrapper que provee contextos necesarios (theme, router, query client)
function renderWithProviders(ui) {
  return render(
    <QueryClientProvider client={new QueryClient()}>
      <MemoryRouter>
        {ui}
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe('LoginForm', () => {
  // Arrange — estado inicial
  test('muestra error cuando las credenciales son incorrectas', async () => {
    // Arrange — Mock del servidor para este test
    server.use(
      rest.post('/api/login', (req, res, ctx) => {
        return res(ctx.status(401), ctx.json({ error: 'Credenciales inválidas' }));
      })
    );

    renderWithProviders(<LoginForm />);

    // Act — interactuar como lo haría el usuario
    await userEvent.type(
      screen.getByLabelText(/correo/i),
      'user@example.com'
    );
    await userEvent.type(
      screen.getByLabelText(/contraseña/i),
      'wrongpassword'
    );
    await userEvent.click(
      screen.getByRole('button', { name: /iniciar sesión/i })
    );

    // Assert — verificar lo que el usuario vería
    expect(
      await screen.findByText(/credenciales inválidas/i)
    ).toBeInTheDocument();

    // Verificar que NO navega al dashboard
    expect(screen.queryByText(/dashboard/i)).not.toBeInTheDocument();
  });
});
```

---

## 3. Modelos Mentales

| Modelo | Descripción | Aplicación Práctica |
|--------|-------------|---------------------|
| **"El usuario como perspectiva"** | El test simula lo que hace el usuario, no lo que hace el código | ¿Qué haría el usuario para llegar a este estado? Reproduce eso en el test |
| **"Testing Trophy vs Pirámide"** | La mayoría de tests deben ser de integración, no unitarios | Si tienes 100 unit tests y 5 integration tests, el ratio está invertido |
| **"Confidence Score"** | Cada test que añades debería aumentar tu confianza de deployar | Si un test pasa y aun así tienes miedo de deployar, ese test no aporta confianza real |
| **"Mocks como Seams"** | Los mocks son puntos de corte entre tu código y el mundo exterior (red, DB, tiempo) | Moquear la capa de red con MSW, no módulos internos de tu propio código |
| **"Tests como Documentación"** | Un test bien escrito describe el comportamiento esperado mejor que un README | `describe('cuando el usuario no está autenticado')` + `test('redirige al login')` |
| **"Falso Positivo vs Falso Negativo"** | Falso positivo: test pasa pero la feature está rota. Falso negativo: test falla pero la feature funciona. Ambos son problemas. | Verificar que el test falla cuando la implementación está rota (evita falsos positivos) |

---

## 4. Criterios de Decisión

| Situación | Prioriza | Sobre | Por qué |
|-----------|----------|-------|---------|
| Función pura con lógica compleja | Unit test | Integration test | Las funciones puras son simples de aislar y cubrir con múltiples casos rápidamente |
| Componente con fetch y estado | Integration test con MSW | Moquear fetch directamente | MSW intercepta a nivel de red; el componente no sabe que está siendo mockeado |
| Flujo crítico de negocio (checkout, auth) | E2E con Playwright/Cypress | Solo integration tests | Los E2E verifican el flujo completo incluyendo la integración real con el backend |
| Refactor de implementación sin cambiar UX | Ningún test debería romperse | Añadir tests acoplados a implementación | Si el test se rompe con un refactor, estaba testeando implementación, no comportamiento |
| Componente con animaciones CSS | `waitFor` + assertions de estado final | Testear estados intermedios | Las animaciones son implementation detail; importa el estado final |
| Queries de Testing Library | `getByRole` > `getByLabelText` > `getByText` > `getByTestId` | Cualquier orden | La jerarquía refleja la accesibilidad del componente |

---

## 5. Anti-patrones

| Anti-patrón | Por qué es malo | Qué hacer en su lugar |
|-------------|-----------------|----------------------|
| **Testear que una función se llamó con ciertos args** | Testa implementación, no comportamiento. Se rompe con refactors internos | Testear el efecto observable: "¿El usuario vio el mensaje de confirmación?" |
| **`data-testid` como query principal** | Acopla el test a detalles del DOM que no el usuario no ve | `getByRole`, `getByLabelText`, `getByText` — lo que el usuario usa |
| **Moquear módulos internos** | Crea tests frágiles que se rompen cuando refactorizas | Moquear solo la capa de red (MSW) o el storage. No moquear tus propios módulos. |
| **Tests que no pueden fallar** | No añaden confianza; dan falsa seguridad | "TDD": escribir el test antes de la implementación; verlo fallar primero |
| **Snapshot tests sin propósito** | Los snapshots se actualizan automáticamente y dejan de ser verificación real | Usar snapshots solo para estructuras que deben ser exactamente iguales y que el equipo revisará conscientemente |
| **`act()` manualmente en exceso** | Síntoma de no entender cuándo React actualiza. Oscurece el test | Usar `userEvent` en lugar de `fireEvent` — `userEvent` maneja los `act()` internamente |

---

## 6. Casos y Ejemplos Reales

### Caso 1: Migración de Tests Acoplados a Implementación

**Situación:** Un equipo tiene 200 tests de componentes React usando Enzyme. Al actualizar de React 16 a 18, el 80% de los tests se rompen aunque la UI funciona perfectamente.

**Causa:** Enzyme permite (y promovía) testear internal state, métodos de instancia, y estructura HTML específica — todos detalles de implementación. La actualización de React cambió los internals.

**Solución:** Migrar a React Testing Library usando `getByRole`, `userEvent`, y MSW. Los tests nuevos describen comportamiento del usuario.

**Resultado:** Al actualizar React de nuevo en el futuro, los tests no se rompen a menos que el comportamiento del usuario cambie.

**Lección:** Los tests acoplados a implementación son deuda técnica — dan falsa seguridad y se convierten en obstáculos para hacer upgrades.

---

### Caso 2: Integration Test de un Formulario con Validación Async

```javascript
test('no permite enviar mientras valida de forma asíncrona', async () => {
  // El servidor devuelve que el email ya existe
  server.use(
    rest.post('/api/check-email', (req, res, ctx) =>
      res(ctx.delay(500), ctx.json({ available: false }))
    )
  );

  render(<RegistrationForm />);

  // El usuario escribe un email
  await userEvent.type(
    screen.getByLabelText(/email/i),
    'existing@user.com'
  );

  // El botón debe estar deshabilitado mientras valida
  expect(screen.getByRole('button', { name: /registrar/i })).toBeDisabled();

  // Después de la validación, debe mostrar el error
  expect(
    await screen.findByText(/este email ya está registrado/i)
  ).toBeInTheDocument();

  // El botón sigue deshabilitado con el error
  expect(screen.getByRole('button', { name: /registrar/i })).toBeDisabled();
});
```

**Lección:** El test verifica el comportamiento completo del flujo (loading → error → disabled) sin saber nada del internals de la validación.

---

### Caso 3: Custom Render para Tests con Providers

**Situación:** Cada test necesita envolver el componente en QueryClient, Router, ThemeProvider. El boilerplate se repite 50 veces.

```javascript
// test-utils.jsx — configuración central
import { render } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'

function AllProviders({ children }) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } } // No reintentos en tests
  });

  return (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        {children}
      </MemoryRouter>
    </QueryClientProvider>
  );
}

// Re-export con providers automáticos
const customRender = (ui, options = {}) =>
  render(ui, { wrapper: AllProviders, ...options });

export * from '@testing-library/react'
export { customRender as render }

// En los tests — mismo API, providers automáticos
import { render, screen } from '../test-utils'
```

**Lección:** Centralizar los providers en un custom render elimina boilerplate y hace los tests más simples y mantenibles.

---

## Conexión con el Cerebro #4

| Habilidad del Cerebro | Aporte de esta fuente |
|------------------------|----------------------|
| Confidence en deployments | Testing Trophy distribuido correctamente da seguridad real para deployar |
| Code quality | Los tests revelan componentes con demasiadas responsabilidades (difíciles de testear = mal diseñados) |
| Refactoring sin miedo | Tests que testean comportamiento sobreviven refactors de implementación |
| Accesibilidad | `getByRole` como query principal incentiva componentes semánticamente correctos |
| Handoff con el Cerebro #6 (QA/DevOps) | Los tests de integración son la base del CI pipeline |

---

## Preguntas que el Cerebro puede responder

1. ¿Qué tipo de test (unit, integration, E2E) debo escribir para esta funcionalidad?
2. ¿Qué query de Testing Library debo usar para encontrar este elemento?
3. ¿Por qué este test se rompe cuando refactorizo aunque la UI funciona igual?
4. ¿Cómo mockear llamadas a la API en tests sin moquear módulos internos?
5. ¿Cómo testear un componente que usa Context sin montar el Provider en cada test?
6. ¿Cómo verificar que un componente muestra el estado de loading correctamente?
7. ¿Cuándo usar `findBy` (async) vs `getBy` (sync) en Testing Library?
