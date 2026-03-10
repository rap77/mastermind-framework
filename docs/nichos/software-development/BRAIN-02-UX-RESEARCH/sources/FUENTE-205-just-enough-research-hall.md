---
id: FUENTE-205
cerebro: 02-ux-research
titulo: Just Enough Research
autor: Erika Hall
tipo: libro
isbn: 978-1937557744
edicion: 2nd Edition
año: 2019
capa: frameworks
experto: Erika Hall
habilidad: Research estratégico y pragmático
tags:
- research-strategy
- mixed-methods
- competitive-research
- organizational-research
- survey-design
- research-planning
version_ficha: '1.0'
fecha_creacion: '2026-02-24'
source_id: FUENTE-205
brain: brain-software-02-ux-research
niche: software-development
title: Just Enough Research
author: Erika Hall
type: libro
year: 2019
expert_id: EXP-205
language: en
skills_covered:
- U6
- U9
distillation_date: '2026-02-24'
distillation_quality: complete
loaded_in_notebook: true
version: 1.0.1
last_updated: '2026-02-25'
changelog:
- version: 1.0.0
  date: '2026-02-24'
  changes:
  - Destilación inicial completa
  - Campos estándar de versioning agregados
- version: 1.0.1
  date: '2026-02-25'
  changes:
  - 'Cargada en NotebookLM (Cerebro #2 UX Research)'
  - 'Notebook ID: ea006ece-00a9-4d5c-91f5-012b8b712936'
status: active
---



# FUENTE-205 — Just Enough Research
**Erika Hall | A Book Apart, 2019 (2nd Ed.)**

---

## 1. Por qué esta fuente es indispensable para el Cerebro #2

Hall resuelve el problema opuesto al de Young: mientras Young profundiza en el "cómo investigar", Hall responde "cuándo, qué tipo, y cómo justificar el research". Es la fuente estratégica del Cerebro #2 — la que permite decidir qué método usar, cuánto research es suficiente, y cómo convertir el research en decisiones de diseño accionables. Además incluye el único tratamiento serio de research organizacional y competitivo en esta lista.

---

## 2. El Principio Central de Hall

> "Research is just another word for paying attention."

El research no requiere laboratorio, presupuesto enorme, o tiempo ilimitado. Requiere estructura, intención y el método correcto para la pregunta correcta.

**La trampa que Hall identifica:** Los equipos hacen research para validar lo que ya decidieron en lugar de para tomar mejores decisiones. Research defensivo vs research generativo.

---

## 3. Tipos de Research (Marco de Hall)

Hall clasifica el research en 4 tipos según el momento y el objetivo:

### 3.1 Research Organizacional
**Qué es:** Investigar el contexto interno — cómo funciona la organización, qué sabe ya, qué asume, qué está midiendo.

**Por qué importa:** Antes de investigar usuarios externos, hay que investigar qué sabe la organización. Muchos "insights de usuario" ya existen internamente pero no están consolidados.

**Métodos:**
- Entrevistas con stakeholders
- Revisión de documentación existente (analytics, soporte, ventas)
- Auditoría de conocimiento previo ("¿qué investigamos antes?")

**Output del #2:** Lista de supuestos organizacionales que el research debe confirmar o refutar.

### 3.2 Research de Usuario
**Qué es:** Investigar comportamientos, necesidades y contexto de las personas que van a usar el producto.

**Cuándo usarlo:** Siempre, pero con el método apropiado según la pregunta.

**Métodos cualitativos (para explorar):**
- Entrevistas contextuales (en el entorno real del usuario)
- Observación / shadowing
- Diary studies (usuarios documentan su propia experiencia)
- Listening sessions (FUENTE-204)

**Métodos cuantitativos (para medir):**
- Encuestas bien diseñadas
- Analytics de comportamiento
- A/B testing
- Usability testing con métricas

### 3.3 Research Competitivo
**Qué es:** Investigar sistemáticamente a los competidores — no para copiarlos sino para entender el espacio de soluciones y las expectativas del usuario.

**Framework de análisis competitivo de Hall:**

| Dimensión | Preguntas a responder |
|---|---|
| **Qué hacen** | ¿Qué funcionalidad ofrecen? ¿Cómo la presentan? |
| **Cómo lo hacen** | ¿Qué patrones de interacción usan? ¿Qué convenciones establecen? |
| **Por qué lo hacen así** | ¿Qué asunciones sobre el usuario revelan sus decisiones? |
| **Qué no hacen** | ¿Qué gaps deja el competidor? ¿Dónde falla? |

**Trampa del análisis competitivo:** Confundir "los competidores lo hacen" con "es la solución correcta". Los competidores también cometen errores.

**Regla del #2:** El research competitivo informa sobre convenciones del mercado y expectativas del usuario, no sobre qué feature construir.

### 3.4 Research de Evaluación
**Qué es:** Evaluar si un diseño existente (o prototipo) funciona para los usuarios.

**Métodos:** Usability testing (FUENTE-202 y FUENTE-203), heurísticas (FUENTE-202), analytics comparativo.

---

## 4. La Matriz de Decisión de Research (Hall)

Hall propone elegir el método según dos variables:

```
                    ACTITUDINAL (qué dicen)
                           ↑
            Encuestas |  Entrevistas
                      |
 CUANTITATIVO ────────┼──────── CUALITATIVO
                      |
     A/B Testing |  Usability testing
                           ↓
                  CONDUCTUAL (qué hacen)
```

**Regla de uso:**
- Preguntas de "¿cuántos?" → Cuantitativo
- Preguntas de "¿por qué?" → Cualitativo
- Preguntas de "¿qué dicen?" → Actitudinal
- Preguntas de "¿qué hacen?" → Conductual

**El error más común:** Usar métodos actitudinales (encuestas, entrevistas de opinión) para responder preguntas conductuales.

---

## 5. Diseño de Encuestas (Hall)

Hall dedica una sección importante al diseño de encuestas porque es el método más malutilizado en UX research.

### Errores comunes en encuestas:
1. **Preguntas leading:** "¿Cuánto te gusta nuestra nueva feature?" (asume que gusta)
2. **Escalas mal calibradas:** "¿Qué tan fácil fue?" sin anclar los extremos
3. **Preguntar por hipotéticos:** "¿Usarías X si existiera?" (las personas no saben lo que harían)
4. **Mezclar preguntas de comportamiento y de opinión** sin distinguir el tipo de respuesta
5. **Escalas impares sin punto neutro** cuando el punto neutro es relevante

### Reglas de Hall para encuestas:
- Empezar con preguntas de comportamiento antes de opinión
- Nunca preguntar por hipotéticos — preguntar por comportamiento pasado
- Incluir siempre una opción "No aplica / No tengo experiencia"
- Probar la encuesta con 3 personas antes de lanzar
- Definir qué decisión tomará el equipo según cada resultado posible ANTES de lanzar

### Cuándo NO usar encuestas (Hall):
- Para entender el razonamiento del usuario
- Para descubrir necesidades desconocidas
- Para justificar una decisión ya tomada
- Cuando el tamaño de muestra no permitirá significancia estadística

---

## 6. Preguntas de Research vs Preguntas de Diseño

Hall hace una distinción crítica que muchos equipos no hacen:

**Pregunta de diseño:** "¿Deberíamos usar un modal o una página nueva para el flujo de pago?"
→ Esta es una decisión de diseño, no una pregunta de research.

**Pregunta de research:** "¿El usuario entiende el costo total antes de comprometerse al pago?"
→ Esta sí requiere research.

**Proceso de Hall:**
1. Listar todas las decisiones de diseño pendientes
2. Para cada decisión: ¿qué necesitamos saber del usuario para tomarla bien?
3. Para cada cosa que necesitamos saber: ¿cuál es el método más eficiente para descubrirlo?
4. ¿Cuánto research es "suficiente" para tomar esta decisión con confianza razonable?

---

## 7. Research Guerrilla (Hall versión)

Hall introduce el concepto de "guerrilla research" — research rápido, barato, suficientemente bueno para decisiones iterativas:

**Formato mínimo viable:**
- Café + laptop + 1 hora con 3 usuarios = insights accionables
- Observar 3 usuarios intentar completar 1 tarea crítica
- Registrar dónde se detienen, dónde dudan, qué buscan
- Listar 3 cambios a implementar antes de la próxima iteración

**Regla de Hall:** "El research imperfecto hecho esta semana vale más que el research perfecto que nunca se hace."

---

## 8. Síntesis de Research en Decisiones

El output del research no es un informe — es una decisión mejor fundamentada.

**Framework de síntesis de Hall:**
1. ¿Qué observamos? (hechos, no interpretaciones)
2. ¿Qué significa esto? (interpretación fundamentada)
3. ¿Qué decidimos hacer diferente? (acción específica)
4. ¿Qué asunciones esto confirma o refuta?

**Regla del #2:** Todo research debe terminar con decisiones de diseño explícitas. Si el research no cambia nada, fue mal planeado.

---

## 9. Cuándo es "Suficiente" Research

Hall aborda directamente la pregunta que todos evitan: ¿cuánto research necesitamos?

**La respuesta:** Es suficiente cuando:
- El equipo puede tomar una decisión de diseño con confianza razonable
- Los hallazgos empiezan a repetirse (saturación)
- El costo de más research supera el riesgo de la decisión sin research

**No es suficiente cuando:**
- Hay una decisión de alto riesgo e irreversible pendiente
- Los hallazgos del equipo y el research divergen significativamente
- El product/market fit aún no está validado

---

## 10. Aplicación directa en el flujo del Mastermind

**Aplica FUENTE-205 para:**
- Decidir qué tipo de research hacer y cuándo (matriz de Hall)
- Diseñar encuestas de usuario sin los errores comunes
- Hacer análisis competitivo estructurado antes de definir features
- Convertir hallazgos de research en decisiones de diseño explícitas
- Responder "¿ya tenemos suficiente research para decidir?"

**Pregunta que activa esta fuente:** "¿Qué tipo de research necesitamos para tomar esta decisión de diseño?"

---

## 11. Conexiones con otras fuentes del Cerebro #2

- **FUENTE-204 (Young):** Young profundiza en el método cualitativo que Hall contextualiza en su marco
- **FUENTE-202 (Nielsen):** Hall y Nielsen se complementan en research de evaluación
- **FUENTE-207 (Fitzpatrick):** Fitzpatrick especializa la entrevista de usuario que Hall define como método
