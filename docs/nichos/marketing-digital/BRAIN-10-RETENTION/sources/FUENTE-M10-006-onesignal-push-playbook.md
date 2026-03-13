---
source_id: "FUENTE-M10-006"
brain: "brain-marketing-10-retention"
niche: "marketing-digital"
title: "The Complete Push Notification Playbook: Engagement, Retention & Re-engagement"
author: "OneSignal Team"
expert_id: "EXP-M10-006"
type: "guide"
language: "en"
year: 2022
isbn: null
url: "https://onesignal.com/blog/push-notification-best-practices/"
skills_covered: ["H3", "H5", "H7"]
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

habilidad_primaria: "Push notification strategy para retención y re-engagement"
habilidad_secundaria: "Segmentación, timing, opt-in optimization, métricas push"
capa: 2
capa_nombre: "Frameworks Operativos"
relevancia: "ALTA — OneSignal es el líder del mercado en push notifications (1M+ apps). Sus datos de benchmarks y best practices están basados en análisis de millones de notificaciones reales."
---

# FUENTE-M10-006: The Complete Push Notification Playbook (OneSignal)

## Tesis Central

> **"Las push notifications son el canal de retención más directo y personal que existe. Usadas correctamente, aumentan el retention rate hasta un 190%. Usadas incorrectamente, son la forma más rápida de que un usuario desinstale tu app."**

---

## 1. Principios Fundamentales

### Las 3 métricas de push que importan

1. **Opt-in rate:** % de usuarios que aceptan recibir notificaciones
   - Benchmark: 60-70% (iOS), 80-90% (Android)
   - Impacto directo en alcance potencial

2. **Click-through rate (CTR):** % de usuarios que hacen click
   - Benchmark: 3-10% (móvil), 0.5-3% (web push)
   - Depende de relevancia y segmentación

3. **Churn por notificaciones:** % de usuarios que se desuscriben
   - Benchmark acceptable: <0.5% por push
   - Señal de alarma: >1% por push

*Fuente: OneSignal, "Push Notification Benchmarks" (2022)*

### Permission Priming: el opt-in es lo primero

El error más costoso es mostrar el prompt nativo de iOS/Android de inmediato. El usuario no tiene contexto para decir sí.

**Estrategia de Permission Priming:**
1. Mostrar primero un "soft ask" in-app con contexto del valor
2. Solo si el usuario acepta el soft ask, mostrar el prompt nativo
3. Si rechaza el soft ask, no pedir de nuevo hasta que haya obtenido más valor

*Fuente: OneSignal, "Opt-in Best Practices" (2022)*

---

## 2. Frameworks y Metodologías

### Framework: Push Notification Segmentation Matrix

```
              Alto Engagement          Bajo Engagement
             ┌─────────────────┬──────────────────────┐
 Recientes   │   POWER USERS   │   PASSIVE USERS      │
             │  (últimos 7d)   │  (últimos 7d, poco)  │
             ├─────────────────┼──────────────────────┤
 Inactivos   │  AT-RISK USERS  │   DORMANT USERS      │
             │  (7-30d sin uso)│  (>30d sin uso)      │
             └─────────────────┴──────────────────────┘
```

- **Power Users:** Notificaciones de valor agregado, nuevas features, contenido exclusivo
- **Passive Users:** Educación, highlights de features no usadas
- **At-Risk:** Re-engagement urgente, recordatorio de valor, win-back
- **Dormant:** Campaña de resurrección fuerte o limpiar lista

*Fuente: OneSignal, "Segmentation Guide" (2022)*

### Framework: The Push Notification Calendar

Tipos de push y frecuencia recomendada:

| Tipo | Frecuencia | Ejemplo |
|------|-----------|---------|
| **Transaccional** | Según evento | "Tu pedido fue enviado" |
| **Behavioral trigger** | Según comportamiento | "Tenés 3 artículos en el carrito" |
| **Re-engagement** | 1 vez/semana máx | "¡Te extrañamos! 20% off" |
| **Educacional** | 2 veces/semana máx | "Tip: usá X feature para Y resultado" |
| **Promocional** | 1-2 veces/semana | "Oferta 24 horas" |

*Fuente: OneSignal, "Push Frequency Best Practices" (2022)*

### Framework: A/B Testing de Push

Variables a testear en orden de impacto:

1. **Timing:** ¿Cuándo enviar? (mayor impacto: 10-12am hora local)
2. **Copy del título:** Primera línea visible en la notificación
3. **Segmentación:** ¿A quién enviar?
4. **CTA:** Deep link vs. homepage
5. **Imagen/icono:** Solo si hay diferencia de CTR >20%

*Fuente: OneSignal, "A/B Testing Push" (2022)*

---

## 3. Modelos Mentales

### "Una push relevante vale 10 pushes genéricas"

Los datos de OneSignal muestran que las notificaciones personalizadas tienen CTR 3-5x mayor que las genéricas. La segmentación no es opcional — es el factor de mayor impacto.

*Fuente: OneSignal, "Personalization Data" (2022)*

### "El timing correcto es más importante que el copy perfecto"

Análisis de 7B+ notificaciones: el factor de mayor impacto en el open rate no es el copy sino el timing. Notificaciones enviadas entre 10am-12pm local tienen CTR 20-30% mayor.

*Fuente: OneSignal, "Timing Analysis" (2022)*

---

## 4. Criterios de Decisión

### Web push vs. mobile push

| Factor | Web Push | Mobile Push |
|--------|---------|-------------|
| **Alcance** | Usuarios de desktop/mobile web | Usuarios de app instalada |
| **CTR típico** | 0.5-3% | 3-10% |
| **Opt-out fácil** | Sí (fácil desuscribirse) | Más difícil |
| **Mejor para** | E-commerce, noticias, SaaS | Apps de consumo, retención |

*Fuente: OneSignal, "Web vs Mobile Push" (2022)*

### Frecuencia óptima por vertical

| Vertical | Push/semana recomendado |
|----------|------------------------|
| **E-commerce** | 2-4 (no promocional todos) |
| **Medios/noticias** | 3-7 (contenido, no spam) |
| **SaaS/productividad** | 1-2 (triggers + educacional) |
| **Fintech** | 1-3 (transaccional + insight) |
| **Entretenimiento** | 3-5 (novedad + social) |

*Fuente: OneSignal, "Frequency Benchmarks" (2022)*

---

## 5. Anti-patrones

### Anti-patrón: Push sin deep link

Enviar una notificación que lleva al usuario a la homepage (en lugar de al contenido relevante) destruye la experiencia. La tasa de conversión cae hasta 60%.

*Fuente: OneSignal, "Deep Linking Guide" (2022)*

### Anti-patrón: Broadcast masivo sin segmentación

Enviar la misma notificación a toda la base de usuarios garantiza alta tasa de opt-out. La regla: si no podés justificar por qué este segmento específico necesita este mensaje, no lo envíes.

*Fuente: OneSignal, "Segmentation Data" (2022)*

### Anti-patrón: Ignorar métricas de opt-out

Muchos equipos miden CTR y olvidan opt-out rate. Una campaña con CTR=8% y opt-out=2% es un desastre a mediano plazo: estás quemando tu audiencia para resultados de corto plazo.

*Fuente: OneSignal, "Metrics to Track" (2022)*
