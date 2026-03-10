---
source_id: "FUENTE-410"
brain: "brain-software-04-frontend-architecture"
niche: "software-development"
title: "Accessibility in Practice: ARIA, HTML Semántico e Implementación en React — Guía Consolidada"
author: "W3C WAI (ARIA Authoring Practices Guide) + Deque Systems (axe-core) + Scott O'Hara"
expert_id: "EXP-410"
type: "guide"
language: "en"
year: 2024
isbn: "N/A"
url: "https://www.w3.org/WAI/ARIA/apg/ + https://dequeuniversity.com + https://www.scottohara.me"
skills_covered: ["H2", "H3", "H4", "H9"]
distillation_date: "2026-02-26"
distillation_quality: "complete"
loaded_in_notebook: true
version: "1.0.0"
last_updated: "2026-02-26"
changelog:
  - version: "1.0.0"
    date: "2026-02-26"
    changes:
      - "Ficha creada — complementa FUENTE-309 del Cerebro #3 (diseño accesible) con la implementación en código"
status: "active"

habilidad_primaria: "Implementación de Accesibilidad Web — HTML semántico, ARIA, keyboard navigation"
habilidad_secundaria: "Testing de accesibilidad con axe-core y herramientas de auditoría"
capa: 2
capa_nombre: "Frameworks Operativos"
relevancia: "ALTA — El Cerebro #3 diseña interfaces accesibles (FUENTE-309). El Cerebro #4 las implementa. Sin esta fuente, el diseño accesible queda solo en papel."
gap_que_cubre: "Implementación de accesibilidad en código — el Cerebro #3 cubre el diseño, el #4 necesita la implementación"
---

# FUENTE-410: Accessibility in Practice — ARIA, HTML Semántico e Implementación en React

## Tesis Central

> La accesibilidad correcta no es `aria-*` en todas partes; es HTML semántico correcto primero, ARIA solo cuando el HTML no alcanza. El orden importa: un elemento `<button>` correcto es infinitamente más accesible que un `<div role="button">` con 10 atributos ARIA. La regla es usar el elemento más semántico disponible antes de recurrir a ARIA.

La segunda regla: el código accesible es código de mejor calidad. Los componentes semánticos son más robustos, más fáciles de testear, y más fáciles de mantener.

---

## 1. Principios Fundamentales

> **P1: Las 5 Reglas de ARIA — En Orden de Prioridad**
> 1. Si puedes usar un elemento HTML nativo con la semántica correcta, úsalo. `<button>` > `<div role="button">`.
> 2. No cambies la semántica nativa de un elemento. `<h2 role="tab">` es confuso.
> 3. Todos los controles interactivos deben ser operables con teclado.
> 4. No usar `role="presentation"` o `aria-hidden="true"` en elementos que necesitan ser usables.
> 5. Todos los elementos interactivos deben tener un nombre accesible.
> *Aplica a: cada componente que construye el Cerebro #4.*

> **P2: El Árbol de Accesibilidad (Accessibility Tree)**
> El browser construye dos árboles del DOM: el visual y el de accesibilidad. Los lectores de pantalla leen el árbol de accesibilidad, no el visual. ARIA modifica el árbol de accesibilidad sin afectar el visual. Entender esto explica por qué `aria-hidden="true"` hace un elemento invisible para screen readers aunque sea visible en pantalla.
> *Aplica a: debugging de accesibilidad — usar Chrome DevTools > Accessibility panel.*

> **P3: Focus Management es Responsabilidad del Frontend**
> Cuándo y dónde se mueve el foco (keyboard focus) en respuesta a acciones del usuario es una decisión de implementación, no de diseño. El Cerebro #3 diseña el estado visual del foco; el Cerebro #4 decide cuándo moverlo y a dónde.
> *Aplica a: modals, drawers, menús, wizards, y cualquier UI que aparezca o desaparezca.*

> **P4: Live Regions para Contenido Dinámico**
> Cuando el contenido cambia sin que el usuario lo cause directamente (notificaciones, resultados de búsqueda en tiempo real, mensajes de éxito/error), los screen readers no lo anuncian automáticamente. `aria-live` le indica al lector de pantalla que anuncie estos cambios.
> *Aplica a: toasts, alerts, contadores, resultados de búsqueda dinámica.*

> **P5: Testing de Accesibilidad No Es Solo Auditoría Automática**
> Las herramientas automáticas (axe, Lighthouse) detectan ≈30-40% de los problemas de accesibilidad. El resto requiere navegación real con teclado y prueba con lector de pantalla (NVDA, JAWS, VoiceOver). Las herramientas automáticas son el piso, no el techo.
> *Aplica a: proceso de QA de cualquier feature.*

---

## 2. Frameworks y Metodologías

### Framework 1: Decisión HTML Semántico vs ARIA

**Propósito:** Elegir la implementación más accesible para cada componente UI.

**Árbol de decisión:**
```
¿Existe un elemento HTML nativo para este propósito?
│
├── SÍ → Usar el elemento HTML nativo
│         Ejemplos:
│           Botón de acción → <button>
│           Navegación → <nav>
│           Enlace de navegación → <a href>
│           Formulario → <form>
│           Campo de texto → <input type="text">
│           Checkbox → <input type="checkbox">
│           Select → <select>/<option>
│           Tabla de datos → <table><th><td>
│
└── NO → Usar el elemento más cercano + ARIA para añadir semántica
          Ejemplos:
            Modal → <div role="dialog" aria-modal="true" aria-labelledby="titulo-id">
            Tab panel → <div role="tabpanel" aria-labelledby="tab-id">
            Menu → <ul role="menu"> + <li role="menuitem">
            Combobox → <input role="combobox" aria-expanded aria-controls>
            Tooltip → <div role="tooltip" id="tooltip-id">
```

**Output esperado:** Cada componente usa el elemento semántico correcto, con ARIA solo donde HTML no llega.

---

### Framework 2: Implementación de Componentes Complejos

**Propósito:** Implementar los componentes de alta interactividad (modal, tabs, dropdown) con accesibilidad correcta de fábrica.

**Modal/Dialog:**
```typescript
// Patrón completo de modal accesible
function Modal({ isOpen, onClose, title, children }: ModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);
  const previousFocus = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (isOpen) {
      // Guardar el elemento que tenía foco antes de abrir
      previousFocus.current = document.activeElement as HTMLElement;
      // Mover el foco al modal
      modalRef.current?.focus();
    } else {
      // Restaurar el foco al cerrar
      previousFocus.current?.focus();
    }
  }, [isOpen]);

  // Trampa de foco: el tab solo cicla dentro del modal
  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Escape') { onClose(); return; }
    if (e.key === 'Tab') {
      const focusables = modalRef.current?.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      const first = focusables?.[0] as HTMLElement;
      const last = focusables?.[focusables.length - 1] as HTMLElement;

      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault(); last?.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault(); first?.focus();
      }
    }
  };

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      ref={modalRef}
      tabIndex={-1}
      onKeyDown={handleKeyDown}
    >
      <h2 id="modal-title">{title}</h2>
      {children}
      <button onClick={onClose} aria-label="Cerrar modal">×</button>
    </div>
  );
}
```

**Tabs:**
```typescript
function Tabs({ tabs }: { tabs: { id: string; label: string; content: ReactNode }[] }) {
  const [activeTab, setActiveTab] = useState(tabs[0].id);

  const handleKeyDown = (e: KeyboardEvent, idx: number) => {
    const tabCount = tabs.length;
    if (e.key === 'ArrowRight') { // Siguiente tab
      const next = (idx + 1) % tabCount;
      setActiveTab(tabs[next].id);
      document.getElementById(`tab-${tabs[next].id}`)?.focus();
    }
    if (e.key === 'ArrowLeft') { // Tab anterior
      const prev = (idx - 1 + tabCount) % tabCount;
      setActiveTab(tabs[prev].id);
      document.getElementById(`tab-${tabs[prev].id}`)?.focus();
    }
  };

  return (
    <div>
      <div role="tablist">
        {tabs.map((tab, idx) => (
          <button
            key={tab.id}
            id={`tab-${tab.id}`}
            role="tab"
            aria-selected={activeTab === tab.id}
            aria-controls={`panel-${tab.id}`}
            tabIndex={activeTab === tab.id ? 0 : -1}  // Solo el tab activo en el tab order
            onClick={() => setActiveTab(tab.id)}
            onKeyDown={(e) => handleKeyDown(e, idx)}
          >
            {tab.label}
          </button>
        ))}
      </div>
      {tabs.map(tab => (
        <div
          key={tab.id}
          id={`panel-${tab.id}`}
          role="tabpanel"
          aria-labelledby={`tab-${tab.id}`}
          hidden={activeTab !== tab.id}
        >
          {tab.content}
        </div>
      ))}
    </div>
  );
}
```

**Live Regions (notificaciones):**
```typescript
// Componente de notificaciones accesible
function Announcer({ message }: { message: string }) {
  return (
    <>
      {/* Para mensajes urgentes (errores) */}
      <div
        role="alert"
        aria-live="assertive"
        aria-atomic="true"
        className="sr-only"  // Visualmente oculto, pero en el accessibility tree
      >
        {message}
      </div>

      {/* Para mensajes informativos (éxito, progreso) */}
      <div
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
      >
        {message}
      </div>
    </>
  );
}

// CSS para sr-only (visually hidden pero en accessibility tree)
// .sr-only {
//   position: absolute; width: 1px; height: 1px;
//   padding: 0; margin: -1px; overflow: hidden;
//   clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0;
// }
```

---

### Framework 3: Testing de Accesibilidad en el Pipeline

**Propósito:** Detectar problemas de accesibilidad automáticamente antes del merge.

**Paso 1 — Unit Tests con jest-axe:**
```typescript
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
expect.extend(toHaveNoViolations);

test('Modal no tiene violaciones de accesibilidad', async () => {
  const { container } = render(
    <Modal isOpen title="Confirmar" onClose={() => {}}>
      <p>¿Estás seguro?</p>
    </Modal>
  );
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

**Paso 2 — Testing manual con teclado:**
```
CHECKLIST de navegación por teclado:
☐ Tab: navega en orden lógico por todos los elementos interactivos
☐ Shift+Tab: navega en orden inverso
☐ Enter/Space: activa botones y enlaces
☐ Escape: cierra modals, menús, tooltips
☐ Flechas: navega dentro de tabs, menús, datepickers
☐ El foco siempre es visible (outline visible)
☐ El foco no se pierde al cerrar un modal (regresa al trigger)
☐ No hay "trampas de foco" fuera de modals
```

**Paso 3 — Lighthouse Accessibility Score:**
```
Target: Score ≥ 90 en Lighthouse Accessibility
Ejecutar en CI: lighthouse --only-categories=accessibility
```

---

## 3. Modelos Mentales

| Modelo | Descripción | Aplicación Práctica |
|--------|-------------|---------------------|
| **HTML Semántico First** | El HTML semántico correcto ya incluye accesibilidad por default | Antes de agregar `role=` o `aria-=`, preguntar "¿hay un elemento HTML nativo para esto?" |
| **Accessibility Tree** | El browser tiene dos árboles: visual y de accesibilidad. ARIA modifica el de accesibilidad | Para debuggear accesibilidad, usar Chrome DevTools > Accessibility panel para ver el árbol |
| **Focus Ring is a Feature** | El anillo de foco es la única guía visual para usuarios de teclado | Nunca hacer `outline: none` sin un reemplazo visual equivalente |
| **Live Regions as Notifications** | Los cambios de contenido que ocurren sin acción del usuario necesitan ser "anunciados" | Cualquier toast, alert, o actualización en tiempo real necesita `aria-live` |
| **Keyboard as First-Class Citizen** | Si un usuario no puede completar la acción con solo el teclado, hay un bug de accesibilidad | Testear cada nueva feature con el mouse desconectado |

---

## 4. Criterios de Decisión

| Situación | Prioriza | Sobre | Por qué |
|-----------|----------|-------|---------|
| ¿Botón o div clickeable? | `<button>` | `<div onClick>` | `<button>` tiene focus, keyboard activation, y role=button nativo |
| ¿Enlace a URL o acción? | `<a href>` para URL; `<button>` para acción | `<a onClick>` para acciones | `<a>` sin `href` no tiene semántica de enlace; `<a>` con `href` para acciones confunde el modelo mental |
| ¿Imagen informativa o decorativa? | `alt="descripción"` | `alt=""` | Las decorativas con `alt=""` son ignoradas por screen readers (correcto). Las informativas deben describir la información |
| ¿Cuándo usar `aria-label` vs texto visible? | Texto visible siempre que sea posible | `aria-label` oculto | El texto visible también ayuda a usuarios cognitivos y es más fácil de mantener |
| ¿`aria-live="assertive"` o `"polite"`? | `"assertive"` para errores urgentes | `"polite"` para updates informativos | `"assertive"` interrumpe al screen reader; usar solo cuando la info es crítica e inmediata |

---

## 5. Anti-patrones

| Anti-patrón | Por qué es malo | Qué hacer en su lugar |
|-------------|-----------------|----------------------|
| `<div onClick>` para botones | No tiene focus, no se activa con Enter/Space, no tiene role semántico | `<button type="button">` |
| `outline: none` sin reemplazo | El usuario de teclado no sabe dónde está el foco | `outline: 3px solid #0066CC` o diseñar `:focus-visible` alternativo |
| Ícono-botón sin texto accesible | El screen reader anuncia "botón" sin describir su función | `aria-label="Cerrar modal"` o `<span className="sr-only">Cerrar</span>` |
| Modal sin trampa de foco | El tab sale del modal hacia el contenido del fondo (que está oculto) | Implementar focus trap: tab cycla solo dentro del modal |
| `aria-hidden="true"` en elemento interactivo | El elemento es invisible para screen readers pero sigue en el tab order | Si es aria-hidden, también `tabIndex={-1}` |
| `role="button"` en `<a>` | Confunde la semántica: ¿es un enlace o un botón? Los usuarios esperan comportamientos distintos | `<button>` para acciones, `<a href>` para navegación. Nunca mezclar |
| Formulario sin labels | El screen reader no puede describir el campo cuando recibe el foco | `<label for="field-id">` visible asociado al `<input id="field-id">` |

---

## 6. Casos y Ejemplos Reales

### Caso 1: GitHub — Accesibilidad como Cultura de Ingeniería

- **Situación:** GitHub necesitaba que su plataforma fuera usable por ingenieros con discapacidades visuales (un segmento significativo de su usuario base técnico).
- **Decisión:** Incorporar axe-core en el pipeline de CI. Todo PR que rompe accesibilidad no puede ser merged.
- **Resultado:** El equipo de accesibilidad reporta que la regresión de accesibilidad bajó un 90%. Los bugs de accesibilidad se detectan en code review, no en producción.
- **Lección:** La accesibilidad como gate en CI es más efectiva que como auditoría manual periódica.

### Caso 2: Stripe — Componentes de Formulario Plenamente Accesibles

- **Situación:** Stripe construye componentes de pago que son usados en millones de sitios. Los componentes deben ser accesibles en cualquier contexto.
- **Decisión:** Cada Stripe Element tiene gestión de foco correcta, labels correctos, y funciona con lectores de pantalla y teclado. Los iframes de Stripe también tienen focus management entre el host y el iframe.
- **Resultado:** Stripe es referenciado como gold standard de formularios de pago accesibles. Cumple con ADA en EEUU y EN 301 549 en Europa.
- **Lección:** La accesibilidad en componentes reutilizables multiplica su impacto. Un componente accesible bien construido sirve a miles de implementaciones.

### Caso 3: Implementación de Combobox (autocomplete) Accesible

- **Situación:** Una feature requería un campo de búsqueda con sugerencias en dropdown, similar a Google Search.
- **Implementación incorrecta inicial:** `<input>` + `<div>` con resultados sin ARIA → los screen readers no sabían que había sugerencias.
- **Implementación correcta final:**
  ```html
  <input
    role="combobox"
    aria-expanded="true/false"
    aria-controls="suggestions-list"
    aria-autocomplete="list"
    aria-activedescendant="option-3"  <!-- ID de la opción actualmente seleccionada -->
    aria-label="Buscar productos"
  />
  <ul id="suggestions-list" role="listbox">
    <li id="option-1" role="option" aria-selected="false">Opción 1</li>
    <li id="option-3" role="option" aria-selected="true">Opción activa</li>
  </ul>
  ```
- **Resultado:** El screen reader anuncia "3 sugerencias disponibles. Opción activa: Pantalón azul".
- **Lección:** Los componentes de búsqueda con autocomplete son de los más complejos en accesibilidad. La ARIA Authoring Practices Guide tiene el pattern completo.

---

## Conexión con el Cerebro #4

| Habilidad del Cerebro | Aporte de esta fuente |
|------------------------|----------------------|
| Implementar lo que Cerebro #3 diseñó | El diseño dice "este modal tiene foco gestionado"; esta fuente dice cómo implementarlo |
| Componentes React robustos | Los componentes accesibles son más robustos: tienen estado de foco, keyboard handlers, y ARIA que los hace testeable |
| Testing completo | jest-axe como capa adicional de testing automático de accesibilidad |
| Code reviews | Checklist de accesibilidad para revisar PRs |
| Handoff inverso a Cerebro #3 | Si el diseño no especifica comportamiento de foco o estado ARIA, el #4 debe pedirlo al #3 |

---

## Preguntas que el Cerebro puede responder

1. ¿Por qué este `<div onClick>` no funciona con el teclado y cómo lo corrijo?
2. ¿Cómo implemento la trampa de foco de este modal?
3. ¿Qué `aria-*` attributes necesita este dropdown de selección?
4. ¿Cómo hago que este toast de éxito sea anunciado por el screen reader?
5. ¿Qué `alt` text debe tener esta imagen en este contexto?
6. ¿Cómo configuro jest-axe para detectar problemas de accesibilidad automáticamente?
7. ¿Por qué este ícono-botón no tiene nombre accesible y cómo lo añado?
