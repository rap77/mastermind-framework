---
source_id: "FUENTE-M10-004"
brain: "brain-marketing-10-retention"
niche: "marketing-digital"
title: "Retention Is the New Acquisition: The ProfitWell Framework for Reducing Churn"
author: "Patrick Campbell"
expert_id: "EXP-M10-004"
type: "blog_series"
language: "en"
year: 2019
isbn: null
url: "https://www.profitwell.com/recur/all/category/retention"
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

habilidad_primaria: "Retention analytics, churn prediction y pricing para retención"
habilidad_secundaria: "MRR recovery, dunning, involuntary churn reduction"
capa: 2
capa_nombre: "Frameworks Operativos"
relevancia: "CRÍTICA — Campbell (ProfitWell/Paddle) es la autoridad en datos de retención SaaS. Sus frameworks basados en análisis de 25,000+ empresas definen los benchmarks de la industria."
---

# FUENTE-M10-004: Retention Framework de Patrick Campbell / ProfitWell

## Tesis Central

> **"La retención es el canal de adquisición más barato que existe. Mejorar la retención en un 5% puede aumentar el revenue entre un 25% y un 95%. La mayoría de las empresas obsesionadas con adquisición están dejando dinero sobre la mesa."**

---

## 1. Principios Fundamentales

### Voluntary vs. Involuntary Churn

Campbell es el primero en hacer esta distinción de forma sistemática con datos:

- **Churn voluntario:** El cliente decide activamente cancelar (~60-70% del churn total)
- **Churn involuntario (delinquent):** Fallo en el pago, tarjeta vencida, problemas técnicos (~20-40% del churn)

**Insight clave:** El churn involuntario es el más fácil de reducir y el más ignorado. Un buen sistema de dunning (recuperación de pagos fallidos) puede reducir el churn total en 20-30%.

*Fuente: ProfitWell Recur, "The Complete Guide to Churn" (Campbell, 2019)*

### Retention Rate Benchmarks por segmento

Datos de 25,000+ empresas SaaS (ProfitWell database):

| Segmento | Logo Retention (anual) | Revenue Retention (neto anual) |
|----------|------------------------|-------------------------------|
| **Enterprise (>$1K ACV)** | 85-90% | 100-120% (expansion) |
| **Mid-Market ($500-$1K)** | 80-85% | 90-100% |
| **SMB ($100-$500)** | 70-80% | 80-90% |
| **Consumer (<$50/mes)** | 60-70% | 70-80% |

*Fuente: ProfitWell Recur, "SaaS Retention Benchmarks" (Campbell, 2020)*

---

## 2. Frameworks y Metodologías

### Framework: Churn Decomposition

Campbell descompone el churn en capas para atacar cada una:

```
Churn Total
├── Churn Involuntario (pago fallido)
│   ├── Tarjeta vencida → Dunning emails
│   ├── Insufficient funds → Retry lógica
│   └── Fraude → Actualización proactiva
└── Churn Voluntario
    ├── Product-fit → Feature gaps
    ├── Precio → Pricing optimization
    ├── Competencia → Diferenciación
    └── Business closure → No controlable
```

*Fuente: ProfitWell Recur, "Churn Decomposition" (Campbell, 2019)*

### Framework: The Dunning Playbook

Para reducir churn involuntario:

1. **Pre-dunning (30 días antes de expiración):** Email recordatorio de actualizar tarjeta
2. **Soft retry:** Reintentar el cobro a las 24h, 48h, 72h, 7 días
3. **Dunning emails:** Secuencia de 4-6 emails con urgencia progresiva
4. **Pause option:** Ofrecer pausa en lugar de cancelación (recupera 10-15% adicional)
5. **Win-back flow:** Para clientes que salen, secuencia de re-engagement a 30, 60, 90 días

*Fuente: ProfitWell, "The Complete Dunning Guide" (Campbell, 2020)*

### Framework: Net Revenue Retention (NRR)

La métrica más importante para el health de un negocio de suscripción:

```
NRR = (MRR inicio + Expansion - Contraction - Churn) / MRR inicio × 100
```

- **NRR > 100%:** El negocio crece aunque no adquiera nuevos clientes (best in class)
- **NRR 85-100%:** Saludable, depende de adquisición para crecer
- **NRR < 85%:** Alarm — el negocio se achica aunque adquiera

*Fuente: ProfitWell Recur, "Understanding NRR" (Campbell, 2021)*

---

## 3. Modelos Mentales

### "Retention como Unit Economics"

Campbell enmarca la retención como un problema financiero, no solo de producto:

```
CLTV = ARPU × Gross Margin / Churn Rate
```

Si el churn rate baja de 5% a 2.5%, el CLTV se DUPLICA sin cambiar precio ni márgenes.

*Fuente: ProfitWell, "The Economics of Churn" (Campbell, 2018)*

### "El precio correcto retiene más que el precio bajo"

Contra-intuitivo pero respaldado por datos: clientes con precio muy bajo tienen mayor churn que clientes con precio justo-alto. El cliente no percibe valor si el precio no comunica valor.

*Fuente: ProfitWell, "Pricing and Retention" (Campbell, 2020)*

---

## 4. Criterios de Decisión

### Qué atacar primero: churn voluntario o involuntario

**Regla de Campbell:**
1. Primero involuntario: ROI inmediato, solución técnica, 2-4 semanas de implementación
2. Luego voluntario: Requiere cambios de producto/proceso, 3-6 meses de impacto

Si el churn involuntario > 20% del churn total, es la primera prioridad absoluta.

*Fuente: ProfitWell, "Retention Prioritization" (Campbell, 2019)*

### Cuándo ofrecer pause vs. cancelación

- **Ofrecer pause:** Cuando el motivo de baja es temporal (presupuesto, proyecto parado, vacaciones)
- **No ofrecer pause:** Cuando es product-fit issue o el cliente ya encontró alternativa

*Fuente: ProfitWell, "The Pause Strategy" (Campbell, 2020)*

---

## 5. Anti-patrones

### Anti-patrón: Ignorar el churn involuntario

La mayoría de empresas analiza el churn voluntario y olvida que 20-40% se va por fallo técnico. Implementar dunning básico puede recuperar miles de dólares en MRR en semanas.

*Fuente: ProfitWell, "Churn Decomposition" (Campbell, 2019)*

### Anti-patrón: Medir logo churn en lugar de revenue churn

Una empresa puede tener 10% de logo churn pero -2% de revenue churn (si los clientes que se van son pequeños y los que quedan crecen). La métrica que importa es la que afecta el revenue.

*Fuente: ProfitWell, "Churn Metrics" (Campbell, 2020)*

### Anti-patrón: Win-back demasiado agresivo

Descuentos masivos en win-back campaigns atraen de vuelta a los clientes por precio, no por valor. Vuelven a irse cuando termina el descuento.

*Fuente: ProfitWell, "Win-back Strategies" (Campbell, 2021)*
