# Casos de Uso e Historias de Usuario — MasterMind Framework

---

## Casos de Uso

### CU-001: Crear un Producto desde Cero

**Actor:** CEO / Usuario  
**Precondición:** Tiene una idea o problema identificado  
**Flujo:**

1. Usuario da un brief al Orquestador: "Quiero crear una app de citas para barberos"
2. Orquestador clasifica como `full_product` → activa flujo completo
3. Cerebro #1 (Product Strategy) valida el problema, define persona, propuesta de valor
4. Cerebro #7 evalúa output de #1 → aprueba
5. Cerebro #2 (UX Research) diseña journey map y wireframes
6. Cerebro #7 evalúa → pide iteración (falta flujo de cancelación)
7. #2 itera y agrega flujo de cancelación → #7 aprueba
8. Cerebro #3 (UI Design) crea design system y componentes
9. Cerebro #4 (Frontend) implementa interfaz
10. Cerebro #5 (Backend) diseña API y base de datos
11. Cerebro #6 (QA/DevOps) configura CI/CD y testing
12. Cerebro #7 evalúa todo el flujo → genera reporte de métricas a monitorear

**Postcondición:** Producto diseñado, construido, y listo para despliegue con métricas definidas.

---

### CU-002: Validar una Idea antes de Construir

**Actor:** CEO / Emprendedor  
**Precondición:** Tiene una idea pero no sabe si vale la pena  
**Flujo:**

1. Usuario: "Quiero saber si tiene sentido crear un CRM para coaches de fitness"
2. Orquestador clasifica como `validation_only` → activa Cerebros #1 y #7
3. Cerebro #1 analiza: mercado, competencia, persona, problema real
4. Cerebro #7 evalúa y agrega: métricas de mercado, riesgos, potencial
5. Resultado: Reporte de validación con recomendación clara (SÍ/NO/PIVOTAR)

**Postcondición:** Decisión informada sin haber escrito una línea de código.

---

### CU-003: Diseñar una Feature Nueva para Producto Existente

**Actor:** Product Manager (o CEO)  
**Precondición:** Producto existente necesita nueva funcionalidad  
**Flujo:**

1. Usuario: "Necesito agregar sistema de notificaciones push a mi app"
2. Orquestador clasifica como `build_feature` → activa Cerebros #4, #5, #6, #7
3. Cerebro #4 (Frontend): diseña componentes de UI para notificaciones
4. Cerebro #5 (Backend): diseña API de notificaciones, integración con servicio push
5. Cerebro #6 (QA/DevOps): define tests y plan de despliegue
6. Cerebro #7 evalúa coherencia del flujo completo

**Postcondición:** Feature diseñada e implementada con testing y plan de deploy.

---

### CU-004: Optimizar un Producto que No Crece

**Actor:** CEO  
**Precondición:** Producto lanzado pero métricas estancadas  
**Flujo:**

1. Usuario: "Mi app tiene 500 usuarios pero nadie paga. ¿Qué hago?"
2. Orquestador clasifica como `optimization` → activa Cerebros #7 y #1
3. Cerebro #7 analiza: funnel, retención, activación, monetización
4. Cerebro #7 identifica: el momento "aha" no está claro, el onboarding es confuso
5. Cerebro #1 re-evalúa: propuesta de valor vs lo que el usuario realmente necesita
6. Resultado: Plan de optimización priorizado con experimentos concretos

**Postcondición:** Plan de acción basado en datos, no en suposiciones.

---

### CU-005: Resolver Conflicto entre Cerebros

**Actor:** Orquestador (automático)  
**Precondición:** Dos cerebros producen outputs contradictorios  
**Flujo:**

1. Cerebro #3 (UI) diseña una animación compleja de transición
2. Cerebro #4 (Frontend) dice que no es implementable con buen performance
3. Orquestador detecta conflicto → invoca Cerebro #7
4. #7 analiza: ¿hay precedente? → No
5. #7 evalúa trade-off: experiencia visual vs performance
6. #7 recomienda: simplificar animación a CSS transitions
7. Orquestador presenta opciones al usuario si #7 no puede resolver solo
8. Decisión se documenta como precedente PREC-XXX

**Postcondición:** Conflicto resuelto, precedente creado para el futuro.

---

### CU-006: Auditoría de Landing Page para Cliente de la Agencia

**Actor:** Hija (Agencia) / Cliente  
**Precondición:** Cliente tiene landing page que no convierte  
**Flujo:**

1. Usuario: "Este cliente tiene una landing de nutrición pero nadie se registra"
2. Orquestador activa: Cerebro #2 (UX), #3 (UI), #7 (Growth)
3. #2 evalúa: flujo de usuario, fricción, claridad del CTA
4. #3 evalúa: jerarquía visual, legibilidad, consistencia
5. #7 evalúa: funnel, copy, oferta, posicionamiento
6. Resultado: Reporte de auditoría con recomendaciones priorizadas

**Postcondición:** Plan de mejora concreto basado en criterio experto.

---

## Historias de Usuario

### Formato

> **Como** {rol}, **quiero** {acción}, **para** {beneficio}.  
> **Criterios de aceptación:** {lista de condiciones que deben cumplirse}

---

### HU-001: Crear un cerebro nuevo

> **Como** CEO del framework, **quiero** poder crear un nuevo cerebro especializado siguiendo la plantilla estándar, **para** expandir las capacidades del sistema a nuevos dominios.

**Criterios de aceptación:**
- [ ] La plantilla genera todos los archivos necesarios (README, brain-spec, knowledge-map, etc.)
- [ ] El proceso de selección de expertos está documentado y se sigue paso a paso
- [ ] Cada fuente maestra tiene su ficha completa con YAML front matter
- [ ] El knowledge-map muestra 0 gaps al completar
- [ ] El cerebro se conecta a NotebookLM y responde consultas de prueba

---

### HU-002: Dar un brief y recibir un plan de producto

> **Como** emprendedor, **quiero** describir mi idea en lenguaje natural y recibir un plan de producto validado, **para** saber si vale la pena invertir tiempo y dinero.

**Criterios de aceptación:**
- [ ] El Orquestador descompone el brief sin pedir más de 2 clarificaciones
- [ ] El Cerebro #1 produce: problema validado, persona, propuesta de valor, métricas, riesgos
- [ ] El Cerebro #7 evalúa y aprueba el output
- [ ] El resultado incluye una recomendación clara: CONSTRUIR / PIVOTAR / NO PROCEDER
- [ ] Todo el proceso toma menos de 1 hora (no días)

---

### HU-003: Recibir feedback de calidad sobre un output

> **Como** cerebro especializado, **quiero** recibir feedback específico cuando mi output es rechazado, **para** saber exactamente qué corregir.

**Criterios de aceptación:**
- [ ] El feedback incluye: qué falló, por qué, y qué se espera
- [ ] Se referencia el criterio de evaluación específico que no se cumplió
- [ ] Se da un ejemplo o sugerencia de mejora cuando es posible
- [ ] El cerebro tiene máximo 3 iteraciones antes de escalamiento

---

### HU-004: Agregar un nuevo nicho al framework

> **Como** CEO del framework, **quiero** poder agregar un nicho completamente nuevo (ej: Marketing Digital), **para** expandir el sistema a nuevos mercados.

**Criterios de aceptación:**
- [ ] El proceso sigue la misma plantilla que Desarrollo de Software
- [ ] Se pueden definir cerebros específicos del nicho
- [ ] Los meta-cerebros (Orquestador, #7, Evaluador) funcionan sin modificación
- [ ] El nuevo nicho se integra al filesystem sin romper los existentes

---

### HU-005: Destinar una fuente nueva a un cerebro existente

> **Como** CEO del framework, **quiero** poder agregar un nuevo libro o video a un cerebro existente, **para** fortalecer su conocimiento sin reconstruirlo.

**Criterios de aceptación:**
- [ ] La nueva fuente se destila usando el proceso documentado
- [ ] Se genera una Ficha de Fuente Maestra con YAML front matter
- [ ] Se carga en NotebookLM y se verifica con consultas de prueba
- [ ] El knowledge-map se actualiza reflejando las nuevas habilidades cubiertas
- [ ] No se rompe nada del cerebro existente

---

### HU-006: Usar la agencia como laboratorio

> **Como** CEO, **quiero** que cada proyecto de la agencia de mi hija genere datos y aprendizajes para el framework, **para** mejorar los cerebros con experiencia real.

**Criterios de aceptación:**
- [ ] Cada proyecto de la agencia se ejecuta usando el framework
- [ ] Los resultados se documentan (qué funcionó, qué no)
- [ ] Los errores detectados se convierten en mejoras al knowledge base
- [ ] Los conflictos resueltos se registran como precedentes
- [ ] Cada 10 proyectos se hace una revisión de mejoras acumuladas

---

### HU-007: Migrar de NotebookLM a RAG propio

> **Como** CEO técnico, **quiero** poder migrar de NotebookLM a un sistema RAG propio sin perder conocimiento, **para** tener control total del sistema.

**Criterios de aceptación:**
- [ ] Todas las Fichas de Fuente Maestra tienen YAML front matter portable
- [ ] El proceso de ingestión en RAG está documentado
- [ ] Los notebooks de NotebookLM tienen backup exportable
- [ ] La migración se puede hacer cerebro por cerebro (no todo de golpe)
- [ ] Los system prompts no cambian (solo cambia la fuente de datos)
