---
source_id: "FUENTE-M10-007"
brain: "brain-marketing-10-retention"
niche: "marketing-digital"
title: "SMS Marketing Mastery: Retention, Winback, and Lifecycle Automation"
author: "Klaviyo Team"
expert_id: "EXP-M10-007"
type: "guide"
language: "en"
year: 2023
isbn: null
url: "https://www.klaviyo.com/marketing-resources/sms-marketing-guide"
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

habilidad_primaria: "SMS marketing para retención y lifecycle automation"
habilidad_secundaria: "Flows de SMS, compliance, integración email+SMS"
capa: 2
capa_nombre: "Frameworks Operativos"
relevancia: "ALTA — Klaviyo es el estándar de la industria en email+SMS para e-commerce. Sus datos de performance de SMS (98% open rate, 45% CTR promedio) definen la oportunidad del canal."
---

# FUENTE-M10-007: SMS Marketing Mastery (Klaviyo)

## Tesis Central

> **"El SMS tiene 98% de tasa de apertura y se lee en los primeros 3 minutos. No hay otro canal con esa combinación de alcance inmediato y atención garantizada. El error no es usar SMS — es usarlo sin estrategia."**

---

## 1. Principios Fundamentales

### Por qué SMS para retención (no solo adquisición)

Las métricas promedio de SMS en e-commerce (Klaviyo data, 2023):

| Métrica | Email | SMS |
|---------|-------|-----|
| **Open rate** | 20-25% | 95-98% |
| **CTR** | 2-5% | 20-45% |
| **Time to open** | Horas | < 3 minutos |
| **Opt-in rate** | Alta (email estándar) | 40-60% de suscriptores email |
| **Opt-out rate** | 0.3% | 1-3% (más fácil darse de baja) |

**Insight:** SMS no reemplaza al email — lo complementa en momentos de urgencia y alta personalización.

*Fuente: Klaviyo, "SMS Benchmarks Report" (2023)*

### Consent y Compliance: el non-negotiable

SMS tiene regulaciones más estrictas que email (TCPA en EEUU, GDPR en Europa):

- **Doble opt-in obligatorio** (en muchos países)
- **Opt-out inmediato:** Responder STOP debe cancelar instantáneamente
- **Identificación del remitente:** Siempre incluir nombre de marca
- **Horario:** Solo entre 8am-9pm hora local del destinatario

**Consecuencia de incumplimiento:** Multas de hasta $1,500 por mensaje en EEUU.

*Fuente: Klaviyo, "SMS Compliance Guide" (2023)*

---

## 2. Frameworks y Metodologías

### Framework: Los 5 Flows de SMS para Retención

```
1. WELCOME SERIES (nuevos suscriptores)
   └── SMS 1: Bienvenida + oferta exclusiva
   └── SMS 2 (48h): Beneficios del programa/producto
   └── SMS 3 (7d): Primer contenido de valor

2. CART ABANDONMENT (carritos abandonados)
   └── SMS 1 (1h): "Dejaste algo atrás"
   └── SMS 2 (24h): Social proof + urgencia
   └── SMS 3 (72h): Descuento de recuperación

3. WINBACK (clientes inactivos)
   └── SMS 1 (30d sin compra): "Te extrañamos"
   └── SMS 2 (45d): Oferta especial
   └── SMS 3 (60d): Última oportunidad

4. POST-PURCHASE (post-compra)
   └── SMS 1 (confirmación): Track tu pedido
   └── SMS 2 (entrega): Pedido recibido + CTA review
   └── SMS 3 (14d): Cross-sell basado en compra

5. LOYALTY/VIP (clientes frecuentes)
   └── SMS mensual: Acceso anticipado, ofertas exclusivas
```

*Fuente: Klaviyo, "SMS Flow Templates" (2023)*

### Framework: Email + SMS Orchestration

No usar ambos canales en el mismo momento para el mismo mensaje. Reglas de coordinación:

| Evento | Canal primario | Canal secundario |
|--------|---------------|-----------------|
| **Carrito abandonado (1h)** | SMS | — |
| **Carrito abandonado (24h)** | Email | — |
| **Carrito abandonado (72h)** | Email | SMS (si no abrió email) |
| **Promoción importante** | Email | SMS (urgencia final) |
| **Transaccional (pedido)** | SMS | Email (detalle) |
| **Newsletter** | Email | — (SMS no es newsletter) |

*Fuente: Klaviyo, "Email vs SMS Strategy" (2023)*

### Métricas de SMS que hay que trackear

1. **Revenue per SMS:** El número que justifica el canal
2. **Opt-out rate por flow:** Para identificar mensajes que irritan
3. **CTR por copy:** Para optimizar contenido
4. **Conversion rate:** % de clics que compran
5. **Unsubscribe spike:** Alertas cuando opt-out > 2x el promedio

*Fuente: Klaviyo, "SMS Analytics Guide" (2023)*

---

## 3. Modelos Mentales

### "SMS es íntimo, no intrusivo"

El SMS llega al espacio personal del usuario. El estándar de calidad debe ser más alto que el email: cada SMS debe justificar la interrupción con valor real.

**Test:** Antes de enviar, preguntar "¿yo abriría este SMS?" Si la respuesta no es un sí claro, no enviarlo.

*Fuente: Klaviyo, "SMS Strategy Guide" (2023)*

### "Frecuencia menor, impacto mayor"

E-mail: 2-4 veces por semana puede ser aceptable.
SMS: 2-4 veces por MES es el máximo para retener opt-in rate saludable.

*Fuente: Klaviyo, "SMS Frequency Data" (2023)*

---

## 4. Criterios de Decisión

### Cuándo SMS supera al email

- Urgencia temporal (oferta de 24h, evento hoy)
- Confirmaciones transaccionales
- Clientes VIP/alta frecuencia
- Re-engagement de clientes que no abren emails

### Cuándo email supera al SMS

- Contenido largo (newsletter, educacional)
- B2B y audiencias profesionales
- Primeros mensajes de una relación nueva
- Contenido con imágenes/video importante

*Fuente: Klaviyo, "Channel Selection Guide" (2023)*

---

## 5. Anti-patrones

### Anti-patrón: Usar SMS como email

Enviar newsletters largas, contenido educativo extenso, o mensajes sin CTA claro por SMS es el error más común. SMS = máx 160 caracteres, un solo mensaje, una sola acción.

*Fuente: Klaviyo, "SMS Best Practices" (2023)*

### Anti-patrón: Comprar listas de SMS

Incluso más grave que comprar listas de email. Sin consentimiento explícito, cada SMS es una violación regulatoria con consecuencias legales.

*Fuente: Klaviyo, "SMS Compliance" (2023)*

### Anti-patrón: No respetar las opt-outs

No procesar los STOP de forma inmediata es ilegal en la mayoría de jurisdicciones y destruye la confianza de marca de forma irreversible.

*Fuente: Klaviyo, "SMS Compliance Guide" (2023)*
