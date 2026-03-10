---
source_id: "FUENTE-611"
brain: "brain-software-06-qa-devops"
niche: "software-development"
title: "Trunk Based Development & Feature Flags: Branching Strategy and Release Decoupling"
author: "Paul Hammant (trunkbaseddevelopment.com) + Pete Hodgson (martinfowler.com/articles/feature-toggles)"
expert_id: "EXP-611"
type: "guide"
language: "en"
year: 2023
url: "https://trunkbaseddevelopment.com / https://martinfowler.com/articles/feature-toggles.html"
skills_covered: ["H12"]
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
      - "Ficha compuesta creada para cubrir GAP de branching strategy y feature flags"
      - "Formato estándar del MasterMind Framework"
status: "active"

habilidad_primaria: "Trunk-based development: estrategia de branching que habilita CI/CD real"
habilidad_secundaria: "Feature flags: desacoplamiento de deploy y release para gestión segura de features"
capa: 2
capa_nombre: "Frameworks"
relevancia: "ALTA — Cubre el GAP operativo de branching y releases. Continuous Delivery menciona trunk-based development pero no lo desarrolla. Sin esta fuente, el cerebro no puede responder preguntas concretas sobre cómo organizar el trabajo en Git ni cómo hacer releases seguras de features grandes."
gap_que_cubre: "Estrategia de branching en Git, trunk-based development, feature flags como herramienta de desacoplamiento deploy/release"
---

# FUENTE-611: Trunk Based Development & Feature Flags

## Tesis Central

> GitFlow y las ramas de larga vida son el mayor obstáculo oculto al CI/CD real: crean "integration hell" al final, retrasan el feedback, y hacen imposible el deployment continuo. La alternativa es trunk-based development: todos integran a main al menos una vez al día, y las features incompletas se ocultan con feature flags, no con ramas. Esto separa el acto técnico del deploy del acto de negocio del release, dando control total sobre cuándo y para quién se activa cada feature.

---

## 1. Principios Fundamentales

> **P1: Una rama que vive más de 2 días es un problema en formación**
> Cada día que una rama diverge de main acumula conflictos potenciales. Una rama de 2 semanas puede requerir días de trabajo para integrar. El "integration hell" al mergear ramas largas es un síntoma directo de esta acumulación. La solución no es ser más cuidadoso al mergear: es no acumular divergencia.
> *Contexto: La regla de las 2 días no es arbitraria: es el punto empírico donde el costo del merge empieza a superar el beneficio de tener la rama separada. Más allá de 2 días, el equipo debería replantearse si está usando feature flags o dividiendo el trabajo en partes más pequeñas.*

> **P2: Deploy y release son dos eventos diferentes que deben poderse separar**
> Deploy es poner código en producción. Release es hacerlo visible y activo para los usuarios. En el modelo tradicional son el mismo evento, lo que crea presión enorme en cada deploy. Con feature flags, se pueden deployar docenas de features incompletas a producción (inactivas) y activar cada una cuando el negocio decida, sin un nuevo deploy.
> *Contexto: Esta separación es el habilitador del deployment continuo. Si cada feature debe ser "completamente lista" antes de ir a producción, los deploys son infrecuentes y grandes. Si las features pueden ir a producción inactivas, los deploys son frecuentes y pequeños.*

> **P3: El trunk es la única fuente de verdad — todo lo demás es temporal**
> En trunk-based development, main/trunk es siempre deployable. Todo trabajo en ramas es temporal y de corta vida. Si el trunk no puede deployarse en cualquier momento, algo está roto en el proceso, no en el código.
> *Contexto: "El trunk siempre está verde" debe ser una invariante del equipo, no un objetivo aspiracional. Si el trunk frecuentemente está rojo (tests fallando, build roto), el equipo necesita reforzar la cultura de "arreglar el trunk es prioridad #1."*

> **P4: Los feature flags tienen un ciclo de vida — nacen y mueren**
> Un feature flag que se crea para un lanzamiento y nunca se elimina después es deuda técnica. Los flags acumulados crean una combinatoria de estados posibles que hace el sistema impredecible y difícil de testear. Cada flag debe tener una fecha de expiración planeada desde que se crea.
> *Contexto: Al crear un feature flag, definir inmediatamente: ¿cuándo se elimina este flag? (después del lanzamiento + periodo de rollback, o cuando se elimine la feature old). Los flags huérfanos son tan problemáticos como el código muerto.*

> **P5: Feature flags no son solo para features — son para operaciones, experimentos y permisos**
> Hay 4 tipos de feature flags con propósitos distintos: Release flags (ocultar trabajo en progreso), Experiment flags (A/B testing), Ops flags (kill switches de operación), y Permission flags (acceso por rol o usuario). Cada tipo tiene un ciclo de vida y gestión diferente.
> *Contexto: Al decidir si usar un feature flag, primero identificar qué tipo es. Un Release flag debe eliminarse pronto. Un Permission flag puede vivir indefinidamente. Tratarlos igual es un error común.*

---

## 2. Frameworks y Metodologías

### Framework 1: Trunk-Based Development en la práctica

**Propósito:** Implementar trunk-based development de forma que habilite CI/CD real sin caos en el equipo.
**Cuándo usar:** Al definir la estrategia de branching de un proyecto nuevo, o al migrar desde GitFlow.

**El modelo de trabajo:**

```
main (trunk) ─────●─────●─────●─────●─────●──── (siempre deployable)
                  ↑     ↑     ↑     ↑     ↑
              dev-A  dev-B  dev-A  dev-C  dev-B
              (2h)   (4h)   (1h)   (8h)   (3h)
              ramas de vida muy corta (< 2 días)
```

**Reglas del modelo:**
1. Nadie trabaja directamente en main — siempre en una rama de corta vida
2. Las ramas se crean desde main actualizado (no desde otra rama)
3. El PR se abre tan pronto como haya algo que revisar (no al final)
4. La rama se integra a main en máximo 1-2 días
5. Si la feature no cabe en 1-2 días, se divide en partes más pequeñas o se usa un feature flag

**Migración desde GitFlow:**

| GitFlow | Trunk-Based equivalente |
|---------|------------------------|
| `feature/mi-feature` (semanas) | Rama de 1-2 días + feature flag |
| `develop` branch | Eliminado — main cumple esa función |
| `release/v2.3` branch | Eliminado — tags en main + feature flags |
| `hotfix/` branch | Rama urgente de horas desde main |

**Qué hacer con features grandes:**
Una feature que toma 3 semanas no puede ir en una rama de 2 días. Opciones:
1. **Dividir en sub-features deployables:** Cada parte es valiosa por sí sola y puede ir a producción independientemente
2. **Feature flag:** La feature va a producción en partes a lo largo de 3 semanas, oculta detrás de un flag. Cuando está completa, se activa.
3. **Branch by abstraction:** Crear una nueva abstracción al lado de la vieja, migrar gradualmente, eliminar la vieja al final.

**Output esperado:** Historial de Git lineal y limpio, sin ramas de larga vida, con integración continua real (no solo CI de nombre).

---

### Framework 2: Feature Flags — Tipos, Implementación y Ciclo de Vida

**Propósito:** Implementar feature flags de forma estructurada que separe deploy de release sin acumular deuda técnica.
**Cuándo usar:** Siempre que una feature requiera más de 2 días de desarrollo, o cuando se necesite control granular sobre quién ve una feature nueva.

**Los 4 tipos de feature flags:**

**Tipo 1 — Release Flags (temporales, días a semanas):**
- Propósito: Ocultar trabajo en progreso hasta que esté listo para el release
- Ejemplo: `if (flags.isEnabled("new-checkout-flow")) { ... } else { ... }`
- Ciclo de vida: Se elimina cuando el release es estable (típicamente 1-4 semanas después del lanzamiento)
- ⚠️ El tipo más común de deuda si no se elimina a tiempo

**Tipo 2 — Experiment Flags (temporales, días a semanas):**
- Propósito: A/B testing y experimentos de producto
- Ejemplo: `if (flags.getVariant("pricing-experiment") === "B") { showAltPricing() }`
- Ciclo de vida: Se elimina cuando el experimento concluye y se toma la decisión
- Gestionados por el equipo de producto, no solo ingeniería

**Tipo 3 — Ops Flags (permanentes o semi-permanentes):**
- Propósito: Kill switches operativos para degradar o desactivar funcionalidad bajo presión
- Ejemplo: `if (flags.isEnabled("recommendations-service")) { fetchRecommendations() } else { showDefaultContent() }`
- Ciclo de vida: Puede ser permanente como mecanismo de resiliencia
- Se activan/desactivan en segundos durante un incidente sin necesidad de deploy

**Tipo 4 — Permission Flags (permanentes):**
- Propósito: Controlar acceso a features por plan, rol, o usuario específico
- Ejemplo: `if (flags.hasPermission(user, "advanced-analytics")) { ... }`
- Ciclo de vida: Permanente — es parte del sistema de permisos
- No son deuda técnica; son features del sistema

**Implementación técnica mínima viable:**

```javascript
// Implementación simple sin librería externa
// Para proyectos pequeños: basta con variables de entorno o config en DB

class FeatureFlags {
  constructor(config) {
    this.flags = config; // { "new-checkout": true, "beta-dashboard": false }
  }

  isEnabled(flagName, context = {}) {
    const flag = this.flags[flagName];
    if (flag === undefined) return false; // Desactivado por defecto si no existe
    if (typeof flag === 'boolean') return flag;
    if (typeof flag === 'function') return flag(context); // Para flags por usuario/porcentaje
    return false;
  }
}

// Uso:
const flags = new FeatureFlags(process.env.FEATURE_FLAGS_CONFIG);

if (flags.isEnabled('new-checkout-flow', { userId: user.id })) {
  return renderNewCheckout();
} else {
  return renderOldCheckout();
}
```

**Para proyectos que crecen:** Usar una plataforma de feature flags (LaunchDarkly, Unleash, Flagsmith) que provee UI de gestión, targeting por usuario/segmento, rollout gradual por porcentaje, y auditoría.

**Proceso de eliminación de flags (evitar deuda):**
1. Al crear el flag, crear el ticket de eliminación con fecha estimada
2. Después del release estable, hacer el cleanup: eliminar el código del flag inactivo y el flag mismo
3. Regla: nunca más de X flags activos simultáneamente (el número depende del equipo, típicamente 5-15)

**Output esperado:** Sistema de feature flags con tipos bien definidos, ciclo de vida documentado, y proceso de cleanup que previene acumulación de deuda.

---

## 3. Modelos Mentales

| Modelo | Descripción | Aplicación Práctica |
|--------|-------------|---------------------|
| **Integration hell como deuda compuesta** | Cada día que una rama diverge de main acumula "integration debt." Así como la deuda financiera tiene interés compuesto, la divergencia de ramas crece más que linealmente: 2 semanas de divergencia no cuesta 14x el precio de 1 día — cuesta 14² más. | Cuando un developer dice "necesito más tiempo para terminar esta rama antes de integrar," la respuesta correcta es "¿qué podemos deployar ya con un feature flag?" La integración tarde siempre es más costosa que la integración temprana. |
| **Deploy como evento técnico, release como decisión de negocio** | Separar mentalmente estos dos eventos libera al equipo de la presión de que cada deploy sea perfecto. El deploy puede ocurrir múltiples veces al día sin que el usuario vea nada nuevo. El release ocurre cuando el negocio decide que la feature está lista. | Cuando el equipo de producto dice "no podemos deployar hasta que la feature esté completa," la respuesta es: "deployamos con el flag desactivado hoy, activamos el flag cuando tú decidas." Esto elimina la acumulación de cambios. |
| **Dark launches** | Deployar código a producción en modo invisible para validar que funciona correctamente antes de exponerlo a usuarios. El código está en producción, recibe tráfico real (duplicado o sintético), pero los usuarios no ven el resultado. | Usar dark launches para features con alto riesgo de performance: la nueva query de búsqueda se ejecuta en paralelo con la actual, se comparan los resultados y el tiempo de respuesta, sin que el usuario vea el nuevo resultado hasta que está validado. |
| **Percentage rollouts como red de seguridad** | Activar una feature para el 1% de usuarios, observar métricas, expandir al 10%, 50%, 100%. Si algo falla, revertir el flag en segundos sin deploy. | Para cualquier feature con incertidumbre de impacto, el rollout gradual por porcentaje es la forma más segura de descubrir problemas antes de que afecten a todos los usuarios. |

---

## 4. Criterios de Decisión

| Situación | Prioriza | Sobre | Por qué |
|-----------|----------|-------|---------|
| Feature que tarda 3 semanas: ¿rama larga o feature flag? | Feature flag + commits diarios a main | Rama larga de 3 semanas | Una rama de 3 semanas garantiza integration hell al final. El feature flag permite integración continua con la feature oculta hasta que esté lista. |
| Release de feature de alto riesgo: ¿big bang o rollout gradual? | Rollout gradual por porcentaje (1% → 10% → 50% → 100%) | Release a todos los usuarios simultáneamente | El rollout gradual limita el blast radius de un problema. Si el 1% de usuarios experimenta errores, el impacto es mínimo y el flag se revierte en segundos. |
| ¿Cuándo eliminar un feature flag de release? | Inmediatamente después de que el rollout sea estable (1-4 semanas post-lanzamiento) | Dejarlo "por si acaso" indefinidamente | Los flags acumulados crean complejidad exponencial. Cada flag activo es una dimensión adicional en la que el sistema puede comportarse diferente. |
| Equipo migrando de GitFlow a trunk-based: ¿migración total o gradual? | Gradual: empezar con los módulos más activos primero | Migración total de golpe | El cambio de workflow es cultural además de técnico. Empezar con un equipo o módulo, aprender, y expandir es más sostenible que cambiar todo de una vez. |

---

## 5. Anti-patrones

| Anti-patrón | Por qué es malo | Qué hacer en su lugar |
|-------------|-----------------|----------------------|
| **Feature flags como sustituto de tests** | "La feature está oculta con un flag, no importa si está bien testeada." La feature va a producción eventualmente; si no tiene tests, los bugs en producción son inevitables. | Los feature flags no eliminan la necesidad de tests. El código detrás de un flag debe testearse igual que cualquier otro código. Los tests deben cubrir ambos caminos (flag activo y flag inactivo). |
| **GitFlow con CI/CD de nombre** | Tener un pipeline de CI pero con ramas de features de 2-3 semanas no es CI: es automated testing de ramas que se integran tarde. La "I" de CI significa integración continua, no tests continuos en ramas separadas. | Trunk-based development. Si el equipo no puede integrar diariamente, investigar por qué (features demasiado grandes, falta de feature flags, miedo al trunk roto) y resolver esa causa raíz. |
| **Flag cemetery — flags que nunca se eliminan** | 50 flags activos en producción crean una combinatoria imposible de testear y de entender. Nadie sabe cuáles están activos, cuáles están obsoletos, y cuáles son críticos. | Política de equipo: cada nuevo flag tiene un ticket de cleanup asociado. Revisión mensual del inventario de flags activos. Si un flag lleva más de 3 meses activo sin plan de eliminación, es deuda activa. |
| **Feature flags para lógica de negocio compleja** | Un flag que controla 500 líneas de lógica de negocio completamente diferente no es un flag: es un switch entre dos versiones del sistema. El código se vuelve imposible de entender y mantener. | Los flags deben controlar comportamiento pequeño y bien definido. Si la diferencia entre flag activo e inactivo es demasiado grande, probablemente la feature necesita más tiempo de diseño antes de empezar a codificar. |
| **Ignorar el testing de ambos paths del flag** | Si el flag inactivo no se testea, cuando se elimine el flag (activando permanentemente el nuevo comportamiento), puede haber regresiones inesperadas en el código del path inactivo que nadie notó porque nadie lo testeó. | Los tests del pipeline deben correr con el flag activo Y con el flag inactivo hasta que el flag se elimine. Las herramientas modernas de feature flags permiten configurar esto en el environment de testing. |

---

## 6. Casos y Ejemplos Reales

### Caso 1: Facebook — Trunk-based development a escala masiva

- **Situación:** Facebook tiene miles de ingenieros trabajando en el mismo codebase (monorepo). Con GitFlow, la integración sería un caos de conflictos. Necesitaban un modelo que permitiera a miles de personas integrar diariamente sin colisiones.
- **Decisión:** Adoptaron trunk-based development con un sistema de feature flags masivo (Gatekeeper). Cada feature, experiment y ops control pasa por Gatekeeper. Los deploys ocurren múltiples veces al día a producción. Los releases son decisiones de producto independientes del deploy.
- **Resultado:** Facebook puede deployar código de miles de ingenieros diariamente sin integration hell. Las features nuevas se activan para grupos específicos de usuarios (empleados primero, 1% de usuarios, rollout completo) con control total y rollback instantáneo si algo falla.
- **Lección:** A escala, trunk-based development + feature flags es la única arquitectura viable. GitFlow colapsa cuando el equipo supera cierto tamaño.

### Caso 2: Spotify — Feature flags como herramienta de resiliencia operativa (Ops flags)

- **Situación:** Spotify tiene un sistema de recomendaciones de música que requiere procesamiento intensivo. Durante incidentes de alta carga, el sistema de recomendaciones puede degradar el performance de funciones más críticas (reproducción de música).
- **Decisión:** Implementaron un Ops flag para el servicio de recomendaciones. Durante un incidente de carga, en lugar de esperar un deploy de emergencia, el equipo SRE activa el flag que desactiva las recomendaciones y muestra contenido estático. La música sigue sonando; las recomendaciones esperan.
- **Resultado:** El tiempo de respuesta ante incidentes de este tipo bajó de "deploy de emergencia en 15-30 minutos" a "toggle del flag en 30 segundos." El impacto al usuario se minimizó dramáticamente.
- **Lección:** Los Ops flags como kill switches son una de las herramientas de resiliencia más baratas y efectivas. Cuestan poco de implementar y valen muchísimo en el momento crítico.

### Caso 3: GitHub — Migración de GitFlow a GitHub Flow (trunk-based simplificado)

- **Situación:** El propio GitHub usaba internamente un proceso de branching complejo. A medida que el equipo creció, el proceso se volvió más lento, no más rápido. Los reviews tardaban días porque las ramas eran grandes y complejas.
- **Decisión:** Migraron a GitHub Flow: ramas de corta vida, PR abierto temprano para review incremental, merge a main cuando está listo, deploy automático. Sin ramas de release, sin ramas de develop.
- **Resultado:** El tiempo promedio de un PR pasó de días a horas. Los deploys se volvieron más frecuentes y menos arriesgados porque cada cambio era pequeño. El equipo reportó menor estrés en los días de deploy.
- **Lección:** La simplificación del proceso de branching no es una concesión a la calidad: es una mejora de la calidad. Menos complejidad en el proceso significa menos superficie para errores y más velocidad de feedback.

---

## Conexión con el Cerebro #6

| Habilidad del Cerebro | Aporte de esta fuente |
|------------------------|----------------------|
| H12 — Branching strategy y feature flags | Esta fuente cubre completamente el gap: trunk-based development como estrategia de branching que habilita CI/CD real, feature flags como mecanismo de desacoplamiento deploy/release, tipos de flags, ciclo de vida, y anti-patrones. |

---

## Preguntas que el Cerebro puede responder

1. ¿Por qué nuestros merges siempre causan conflictos enormes y cómo lo evitamos?
2. ¿Cómo deployamos una feature que tarda 3 semanas sin acumular una rama gigante?
3. ¿Cuál es la diferencia entre GitFlow, GitHub Flow y trunk-based development, y cuándo usar cada uno?
4. ¿Cómo hacemos un rollout gradual de una feature de alto riesgo para minimizar el impacto si algo falla?
5. ¿Cómo evitamos que los feature flags se acumulen y se conviertan en deuda técnica?
6. ¿Cuándo tiene sentido usar una plataforma de feature flags como LaunchDarkly vs. implementar algo propio?
