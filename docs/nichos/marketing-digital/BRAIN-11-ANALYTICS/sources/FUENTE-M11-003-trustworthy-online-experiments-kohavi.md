---
source_id: "FUENTE-M11-003"
brain: "brain-marketing-11-analytics"
niche: "marketing-digital"
title: "Trustworthy Online Controlled Experiments: A Practical Guide to A/B Testing"
author: "Ronny Kohavi, Diane Tang, Ya Xu"
expert_id: "EXP-M11-003"
type: "book"
language: "en"
year: 2020
isbn: "978-1108724264"
url: "https://www.cambridge.org/core/books/trustworthy-online-controlled-experiments/D97B26382EB0EB2DC2019A7A7B518F59"
skills_covered: ["H1", "H3", "H5", "H7"]
distillation_date: "2026-03-12"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-12"
changelog:
  - version: "1.0.0"
    date: "2026-03-12"
    changes:
      - "Ficha creada con destilación completa"
status: "active"

habilidad_primaria: "A/B testing riguroso y cultura de experimentación"
habilidad_secundaria: "Statistical significance, sample size, pitfalls de experimentación"
capa: 2
capa_nombre: "Frameworks Operativos"
relevancia: "CRÍTICA — Kohavi (ex-Microsoft, ex-Amazon, fundador de ExP) es el autor del libro más riguroso sobre A/B testing. Su trabajo en Microsoft (20,000+ experimentos/año) define los estándares de experimentación de la industria."
---

# FUENTE-M11-003: Trustworthy Online Controlled Experiments (Kohavi et al.)

## Tesis Central

> **"La mayoría de los test A/B que las empresas creen que son válidos, no lo son. El 60-70% de las 'mejoras' detectadas en experimentos mal diseñados son falsas. La experimentación rigurosa requiere disciplina estadística, no solo una herramienta."**

---

## 1. Principios Fundamentales

### El Twyman's Law

> "Cualquier número que parece interesante o inusual es probablemente un error."

Regla de Kohavi para analizar resultados de experimentos: si el resultado parece demasiado bueno (o demasiado malo), primero buscar el error en la implementación antes de celebrar.

*Fuente: Trustworthy Online Controlled Experiments, Cap. 3 (Kohavi et al., 2020)*

### Los tres requerimientos de un experimento válido

1. **Randomización correcta:** Los usuarios deben ser asignados aleatoriamente y de forma estable (el mismo usuario siempre ve la misma variante)
2. **Tamaño de muestra suficiente:** Calculado ANTES del experimento, no después
3. **Métrica primaria pre-definida:** La métrica de éxito debe definirse antes de ver los resultados

Si alguno de estos tres falla, el experimento no es confiable.

*Fuente: Trustworthy Online Controlled Experiments, Cap. 2 (Kohavi et al., 2020)*

---

## 2. Frameworks y Metodologías

### Framework: Overall Evaluation Criterion (OEC)

El OEC es la métrica única que define el éxito de un experimento. Debe:

1. Ser medible en el corto plazo
2. Ser predictiva del valor de largo plazo del negocio
3. Ser sensible (cambiar cuando hay efecto real)
4. No tener efectos secundarios no deseados

**Ejemplo de OEC para e-commerce:** Revenue per visitor (no conversion rate solo, porque ignora el valor del pedido)

*Fuente: Trustworthy Online Controlled Experiments, Cap. 6 (Kohavi et al., 2020)*

### Framework: Sample Size Calculator

Fórmula simplificada para calcular el tamaño de muestra necesario:

```
n = (16 × σ²) / δ²

Donde:
n = muestra por variante
σ² = varianza de la métrica (histórica)
δ = efecto mínimo detectable (MDE) que importa
16 = factor para 80% power y 5% significance
```

**Regla práctica:** Si no podés lograr el tamaño de muestra en 2-4 semanas, el experimento no vale la pena correrlo.

*Fuente: Trustworthy Online Controlled Experiments, Cap. 8 (Kohavi et al., 2020)*

### Framework: The Experiment Trustworthiness Checklist

Antes de declarar un resultado como válido:

- [ ] ¿El SRM (Sample Ratio Mismatch) es < 0.1%? (si no, la randomización falló)
- [ ] ¿El experimento corrió el tiempo planificado sin interrupciones?
- [ ] ¿La métrica primaria tiene significancia estadística? (p < 0.05)
- [ ] ¿Las métricas secundarias son coherentes con la primaria?
- [ ] ¿Hay novelty effect posible? (los usuarios se comportan diferente porque es nuevo)

*Fuente: Trustworthy Online Controlled Experiments, Cap. 12 (Kohavi et al., 2020)*

---

## 3. Modelos Mentales

### "Un tercio de los experimentos mejoran, un tercio empeoran, un tercio son neutros"

Kohavi documenta que en empresas maduras de experimentación (Microsoft, Google, Booking.com), solo ~33% de los experimentos muestran mejora real. Esto no es fracaso — es el proceso correcto. Las ideas de los mejores equipos también fallan.

**Implicación:** No medir el éxito de un equipo de CRO por cuántos tests "ganan", sino por cuántos tests válidos corren.

*Fuente: Trustworthy Online Controlled Experiments, Cap. 1 (Kohavi et al., 2020)*

### "Correlation ≠ Causation, especialmente en datos observacionales"

Los experimentos controlados son la única forma de establecer causalidad. Cualquier análisis observacional (incluso con ML) tiene sesgo de confound que puede llevar a conclusiones incorrectas.

*Fuente: Trustworthy Online Controlled Experiments, Cap. 4 (Kohavi et al., 2020)*

---

## 4. Criterios de Decisión

### Cuándo hacer A/B test vs. análisis observacional

| Escenario | Método |
|-----------|--------|
| Suficiente tráfico, cambio testeable | A/B test |
| Bajo tráfico o cambio difícil de randomizar | Quasi-experiment o análisis pre/post |
| Pregunta de "por qué" | Cualitativo (surveys, interviews) |
| Decisión urgente (< 1 semana) | Datos históricos + juicio experto |

*Fuente: Trustworthy Online Controlled Experiments, Cap. 5 (Kohavi et al., 2020)*

### Cuándo parar un experimento antes de tiempo

Solo parar early si:
1. El experimento está causando daño claro al negocio (caída de revenue >10%)
2. Hay un bug crítico en la implementación

NUNCA parar porque "el test va bien y quiero implementar rápido" (esto es p-hacking).

*Fuente: Trustworthy Online Controlled Experiments, Cap. 9 (Kohavi et al., 2020)*

---

## 5. Anti-patrones

### Anti-patrón: Peeking (mirar resultados antes de terminar el test)

Revisar los resultados del test mientras corre y decidir terminarlo cuando los resultados "se ven bien" infla dramáticamente la tasa de falsos positivos. Se llama p-hacking y es el error estadístico más común en A/B testing.

*Fuente: Trustworthy Online Controlled Experiments, Cap. 9 (Kohavi et al., 2020)*

### Anti-patrón: Múltiples comparaciones sin corrección

Si testeas 20 variantes o 20 métricas, estadísticamente 1 de ellas "ganará" por azar al 5% de significancia. Usar corrección de Bonferroni o False Discovery Rate cuando hay múltiples comparaciones.

*Fuente: Trustworthy Online Controlled Experiments, Cap. 10 (Kohavi et al., 2020)*

### Anti-patrón: Ignorar el novelty effect

Cuando se lanza una variante nueva, los usuarios la usan más por curiosidad. Este efecto desaparece en 1-2 semanas. Correr el experimento menos de 2 semanas puede mostrar mejoras falsas.

*Fuente: Trustworthy Online Controlled Experiments, Cap. 11 (Kohavi et al., 2020)*
