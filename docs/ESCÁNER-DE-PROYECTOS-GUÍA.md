# Guía: Escanear y Evaluar Proyectos Externos

## 3 Niveles de Análisis Disponibles

| Nivel | Scanner | Profundidad | Mejor Para |
|-------|---------|-------------|------------|
| **Rápido** | `escanear_proyecto.py` | Docs + config | Quick overview |
| **Profundo** | `escanear_proyecto_serena.py` | Docs + código | Análisis técnico |
| **Manual** | Tu propio brief | Completo | Mejor evaluación |

---

## Nivel 1: Scanner Rápido

Analiza documentación y archivos de configuración.

```bash
# Escanear un proyecto externo
cd /home/rpadron/proy/mastermind

uv run python scripts/escanear_proyecto.py /path/to/proyecto

# Con NotebookLM real
uv run python scripts/escanear_proyecto.py /path/to/proyecto --mcp

# Guardar brief generado
uv run python scripts/escanear_proyecto.py /path/to/proyecto --output brief_generado.md
```

**Qué detecta:**
- ✅ Nombre del proyecto
- ✅ Stack técnico (del package.json, requirements.txt, etc.)
- ✅ Features listadas en README
- ✅ Documentación disponible
- ❌ No detecta: Problema, usuario target, evidencia, métricas

---

## Nivel 2: Scanner Profundo (Con Serena)

Analiza código, arquitectura, modelos, APIs.

```bash
# Escanear con análisis de código
uv run python scripts/escanear_proyecto_serena.py /path/to/proyecto

# Guardar brief para completar manualmente
uv run python scripts/escanear_proyecto_serena.py /path/to/proyecto --output brief.md
```

**Qué detecta:**
- ✅ Todo lo del Nivel 1
- ✅ Estructura de código (frontend/backend dirs)
- ✅ APIs encontradas
- ✅ Modelos de datos
- ✅ Tests presentes
- ❌ No detecta: Información de negocio (requiere input manual)

---

## Nivel 3: Brief Manual + Evaluación (Recomendado)

Para la mejor evaluación, completa el brief manualmente.

### Template de Brief Completo

```markdown
# [Nombre de tu Proyecto]

## Descripción (1-2 párrafos)
[¿Qué hace tu producto? ¿Para quién?]

## Problema que Resuelve
[¿Qué dolor específico tienes identificado?]
- ¿Quién tiene el problema?
- ¿Con qué frecuencia ocurre?
- ¿Qué soluciones usan actualmente?

## Solución Propuesta
[¿Cómo tu producto resuelve este problema?]
- Features clave (3-5)
- Diferenciadores vs competencia

## Usuario Objetivo
[Describe específicamente a tu usuario]
- Rol/demografía
- Contexto de uso
- Pain points actuales

## Evidencia de Validación
[¿Cómo sabes que este problema es real?]
- Entrevistas: ___ personas
- Observaciones: qué viste
- Datos de mercado
- Comportamiento actual de usuarios

## Stack Técnico
- Frontend: ___
- Backend: ___
- Database: ___
- Infrastructure: ___

## Métricas Objetivo (Realistas)
- D7 retention: >___%
- D30 retention: >___%
- Activation rate: >___%
- NPS: >___
- Paid conversion: >___% (si aplica)

## Modelo de Monetización
- [ ] Freemium
- [ ] Pago mensual/anual
- [ ] Enterprise
- [ ] Usage-based
- Pricing: $___/mes

## Competencia
- [Competidor 1]: cómo eres diferente
- [Competidor 2]: qué haces mejor

## Arquitectura (Opcional)
[Breve descripción de la arquitectura técnica]
```

---

## Flujo Completo Recomendado

```
1. ESCANEAR PROYECTO EXTERNO
   ↓
2. COMPLETAR BRIEF MANUALMENTE
   ↓
3. EVALUAR CON MENTE MAESTRA
   ↓
4. RECIBIR RECOMENDACIONES
   ↓
5. ITERAR (si es CONDITIONAL/REJECT)
```

### Ejemplo Completo

```bash
# 1. Escanear proyecto externo
cd /home/rpadron/proy/mastermind
uv run python scripts/escanear_proyecto_serena.py /path/to/super-app --output super-app-brief.md

# 2. Editar el brief generado
vim super-app-brief.md
# Agregar: Problema, Usuario, Evidencia, Métricas

# 3. Evaluar con MasterMind Framework
uv run python scripts/evaluar_proyecto.py --file super-app-brief.md --mcp --flow full_product

# 4. Recibir resultados
# - Si APPROVE: ¡Buen trabajo!
# - Si CONDITIONAL: Completar lo faltante y re-evaluar
# - Si REJECT: Revisar desde cero
```

---

## Modos de Evaluación

| Modo | Cerebros Usados | Duración | Mejor Para |
|------|-----------------|----------|------------|
| `validation_only` | #1, #7 | Rápido | ¿Vale la pena? |
| `full_product` | Todos | Completo | Producto completo |
| `optimization` | #7 | Rápido | Mejorar producto existente |
| `technical_review` | #4, #5, #6 | Técnico | Revisión arquitectura |

```bash
# Ejemplos de uso por modo

# Modo 1: Validación rápida (¿vale la pena?)
uv run python scripts/evaluar_proyecto.py --file brief.md --flow validation_only

# Modo 2: Producto completo (análisis exhaustivo)
uv run python scripts/evaluar_proyecto.py --file brief.md --flow full_product

# Modo 3: Optimización (mejorar algo existente)
uv run python scripts/evaluar_proyecto.py --file brief.md --flow optimization

# Modo 4: Revisión técnica (arquitectura, código)
uv run python scripts/evaluar_proyecto.py --file brief.md --flow technical_review
```

---

## Interpretación de Resultados

### Veredicto APPROVE (Score 100-156)

```
✅ APPROVE - Producto sólido

El brief está bien construido:
- Problema claro y específico
- Evidencia de validación suficiente
- Métricas realistas basadas en benchmarks
- Usuario target bien definido

ACCION: Avanzar con desarrollo
```

### Veredicto CONDITIONAL (Score 60-99)

```
⚠️  CONDITIONAL - Bueno pero incompleto

Falta mejorar:
- Más evidencia de validación
- Métricas más específicas
- Clarificar el diferencial
- Definir mejor el usuario target

ACCION: Completar lo faltante y re-evaluar
```

### Veredicto REJECT (Score 0-59)

```
❌ REJECT - Problemas serios

Issues críticos:
- Problema no claro o demasiado genérico
- Sin evidencia de validación real
- Métricas irreales (ej: "90% retention")
- Usuario target indefinido ("todo el mundo")

ACCION: Revisar desde cero, entrevistar usuarios
```

---

## Tips para Buenos Briefs

### 1. Evidencia Cuantitativa > Cualitativa

```markdown
❌ MAL: "La gente quiere esto"
✅ BIEN: "15/20 entrevistados dicen que pagarían $10/mes"

❌ MAL: "Es un mercado grande"
✅ BIEN: "TAM de $2B, SAM de $200M (Source: Gartner 2024)"
```

### 2. Métricas Basadas en Benchmarks

```markdown
❌ MAL: "D30 retention 90%" (irreal para apps B2C)
✅ BIEN: "D30 retention >20% (benchmark: apps B2C promedio 15-25%)"

❌ MAL: "Activation 100%"
✅ BIEN: "Activation rate >40% (benchmark: SaaS B2B promedio 35-45%)"
```

### 3. Problema Específico > Genérico

```markdown
❌ MAL: "App para ser más productivo"
✅ BIEN: "App de time tracking para freelancers con 3-10 clientes activos"

❌ MAL: "Plataforma de educación"
✅ BIEN: "Plataforma de aprendizaje de programación para devs junior (0-2 años experiencia)"
```

### 4. Evidencia de Validación > Suposiciones

```markdown
❌ MAL: "Mi amigo dice que es buena idea"
✅ BIEN: "12 freelancers entrevistados, 10 dicen que tracking time es 'dolor #1'"

❌ MAL: "La gente va a amar esto"
✅ BIEN: "8/12 entrevistados ya usan spreadsheets para tracking, todos están frustrados"
```

---

## Troubleshooting

### "El scanner no detectó nada"

**Problema:** El proyecto no tiene README o documentación.

**Solución:**
```bash
# Usa --serena-prompt para generar un prompt de análisis manual
uv run python scripts/escanear_proyecto_serena.py /path/to/proyecto --serena-prompt > analysis_prompt.txt

# Copia el prompt y pégalo en Claude Code con Serena MCP activado
# Claude analizará el proyecto profundamente
```

### "Score es 0 sin MCP"

**Problema:** Sin `--mcp`, el modo mock puede dar resultados inconsistentes.

**Solución:**
```bash
# Usa --mcp para evaluations reales
uv run python scripts/evaluar_proyecto.py --file brief.md --mcp

# Primero asegúrate de tener nlm CLI instalado y autenticado
nlm login
```

### "Quiero análisis más profundo del código"

**Solución:** Usa el prompt de Serena MCP:
```bash
# Genera el prompt
uv run python scripts/escanear_proyecto_serena.py /path/to/proyecto --serena-prompt

# Pégalo en Claude Code y deja que Serena analice:
# - Estructura de código
# - Arquitectura
# - Patrones usados
# - Debt técnico
```

---

## Ejemplo Real

### Proyecto: App de Delivery de Comida Saludable

```bash
# 1. Escanear
uv run python scripts/escanear_proyecto_serena.py ~/projects/healthy-food --output brief.md

# 2. Completar brief (agregando info manual)
vim brief.md
```

**Brief completado:**
```markdown
# GreenEats - Delivery de Comida Saludable

## Problema
Las personas que quieren comer saludable no tienen tiempo de cocinar
y las opciones de delivery son predominantemente chatarra.

Target: Profesionales 25-40 años, ingresos medios-altos, sin tiempo.

## Solución
App que conecta con restaurantes saludables, filtrando por:
- Dietas (keto, vegana, paleo, etc.)
- Macros (proteína, calorías)
- Tiempo de entrega (<30 min)

Diferencial: Algoritmo de recomendación basado en goals de salud del usuario.

## Evidencia
- 30 personas entrevistadas (edad 25-40)
- 25/30 dicen "comida chatarra" es única opción en delivery
- 20/30 cocinan pero "no tienen tiempo" durante semana
- Competidores no filtrían por salud/macros

## Métricas Objetivo
- D7 retention: >25% (benchmark: delivery apps 15-25%)
- D30 retention: >15% (benchmark: food delivery 10-20%)
- Order frequency: >2 orders/semana
- NPS: >30

## Monetización
- Comisión por orden: 15%
- Subscription premium: $9.99/mes (delivery gratis + 10% dto)
```

```bash
# 3. Evaluar
uv run python scripts/evaluar_proyecto.py --file brief.md --mcp --flow full_product
```

**Resultado:**
```
Veredict: CONDITIONAL 72/156 (46%)

Critical Issues:
- Falta validar willingness-to-pay real (solo intención declarada)
- No hay análisis de unit economics (costo de delivery vs margen)
- Competidores no mencionados (Rappi, UberEats ya tienen filtros saludables)

What's Good:
- Problema específico y real
- Evidencia cuantitativa (30 entrevistadas)
- Métricas realistas basadas en benchmarks

Recommendations:
- Validar precio con test A/B ($9.99 vs $14.99 vs $19.99)
- Calcular unit economics antes de escalar
- Analizar feature parity con competidores
```

---

## Resumen

| Paso | Comando | Output |
|------|---------|--------|
| 1. Escanear | `uv run python scripts/escanear_proyecto_serena.py /path/to/proyecto -o brief.md` | Brief generado |
| 2. Completar | Editar `brief.md` con info manual | Brief completo |
| 3. Evaluar | `uv run python scripts/evaluar_proyecto.py --file brief.md --mcp` | Evaluación |
| 4. Iterar | Basado en recommendations | Brief mejorado |

---

¿Quieres que te ayude a escanear y evaluar un proyecto específico?
Dame el path y lo hacemos juntos.
