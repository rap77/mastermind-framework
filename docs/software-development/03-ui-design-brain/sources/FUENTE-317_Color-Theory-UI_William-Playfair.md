---
source_id: "FUENTE-317"
brain: "brain-software-03-ui-design"
niche: "software-development"
title: "Interaction of Color"
author: "Josef Albers"
expert_id: "EXP-317"
type: "book"
language: "en"
year: 1963
distillation_date: "2026-03-02"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-02"
changelog:
  - version: "1.0.0"
    date: "2026-03-02"
    changes:
      - "Destilación inicial completa"
status: "active"
---

# Interaction of Color

## 1. Principios Fundamentales

> **P1: El color es relativo** - El color no existe de forma aislada; solo puede entenderse en relación con otros colores.

> **P2: La percepción del color es subjetiva y contextual** - El mismo color puede percibirse de manera diferente según el contexto y los colores circundantes.

> **P3: El contraste crea jerarquía** - El uso inteligente del contraste guía la atención del usuario y establece importancia visual.

> **P4: La armonía visual proviene de relaciones** - Las combinaciones de colores armónicas se basan en relaciones matemáticas y perceptuales entre tonos.

## 2. Frameworks y Metodologías

### Relaciones de Color Básicas
- **Análogos**: Colores adyacentes en el círculo cromático (armonía suave)
- **Complementarios**: Colores opuestos (contraste máximo)
- **Triádicos**: Tres colores equidistantos (equilibrio vibrante)
- **Divididos**: Variación de complementarios (menos tensión)

### Ejercicios de Albers
1. **Estudios de restitución** - Hacer que el mismo color se vea diferente
2. **Restitución de borde** - Hacer que dos colores parezcan tres
3. **Estudios de mezcla visual** - Crear ilusión de tercer color

## 3. Modelos Mentales

**Cualidad sobre cantidad** - Un pequeño número de relaciones de color bien ejecutadas es superior a muchas combinaciones arbitrarias.

**El color como sistema** - Los colores no se eligen individualmente; se crean como sistemas relacionales donde cada color afecta a los demás.

**La temperatura es relativa** - Un color puede verse "cálido" o "frío" según su contexto, independientemente de su posición teórica en el espectro.

**El valor define la estructura** - Las variaciones de luminosidad (valor) son más importantes para la estructura y legibilidad que el croma o el matiz.

## 4. Criterios de Decisión

### Paletas de Color para UI

| Tipo | Características | Casos de Uso |
|------|----------------|--------------|
| Monocromática | Un matiz, variaciones de valor/croma | Minimalismo, elegancia |
| Análoga | Colores adyacentes | Harmonía suave, natural |
| Complementaria | Opuestos en círculo | Alto contraste, CTAs |
| Triádica | Tres equidistantes | Vitalidad, balance |

### Contraste y Legibilidad
- **Mínimo WCAG AA**: Contraste 4.5:1 para texto normal
- **Mínimo WCAG AAA**: Contraste 7:1 para texto largo
- **El valor precede al croma**: Asegurar contraste de luminosidad primero

### Accesibilidad
- No depender solo del color para comunicar información
- Usar patrones, texturas o iconos como refuerzo
- Verificar con simuladores de daltonismo
- Testear en condiciones de luz variable

## 5. Anti-patrones

❌ **Elegir colores en aislamiento** - Siempre evaluar colores en contexto con otros colores del sistema.

❌ **Demasiados colores primarios** - Limitar colores saturados; usar variaciones de valor y croma para sofisticación.

❌ **Ignorar el contraste de valor** - El croma (saturación) no compensa falta de contraste de luminosidad.

❌ **Paletas aleatorias** - Las elecciones de color deben seguir principios sistemáticos, no preferencias personales.

❌ **Olvidar modo oscuro** - Diseñar ambos modos simultáneamente; las relaciones de color cambian drásticamente.

## Referencias de Aplicación a UI

**Sistemas de Design Tokens:**
```
color-primary: #0066CC (matiz base)
color-primary-light: lighten(color-primary, 20%)
color-primary-dark: darken(color-primary, 20%)
color-contrast: #FF6600 (complementario)
```

**Principios de Albers aplicados:**
- Usar estudios de "restitución" para refinar paletas
- Probar colores superpuestos en capas
- Verificar que los colores mantengan su intención contextual
- Documentar relaciones sistemáticas, no valores hex aislados
