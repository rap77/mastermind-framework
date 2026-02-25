# Test Prompt for Brain #1 - Product Strategy

## System Prompt (from agents/brains/product-strategy.md)

You are Brain #1 of the MasterMind Framework - Product Strategy. You define WHAT to build and WHY.

(Full system prompt content above...)

---

## User Brief

### AI-Powered Code Review Assistant

Quiero construir una herramienta que use IA para revisar código automáticamente. La idea es que los desarrolladores puedan subir su código y recibir feedback sobre bugs, smells de código, y oportunidades de mejora.

#### Contexto
- Ya existen herramientas como SonarQube pero son muy pesadas
- Los desarrolladores quieren feedback rápido en el PR
- El target es equipos pequeños de 5-20 personas

#### Constraints
- Budget limitado (<$500/mes en APIs)
- Lanzamiento en 3 meses
- Equipo: 1 fullstack dev + 1 designer

#### Questions
- ¿Es esto una buena idea?
- ¿Qué debería construir primero?
- ¿Cuáles son los riesgos?

---

## Expected Response Structure

```json
{
  "brain": "product-strategy",
  "task_id": "test-001",
  "validated_problem": {
    "statement": "...",
    "evidence": ["...", "..."]
  },
  "target_persona": {
    "name": "...",
    "needs": ["...", "..."],
    "pains": ["...", "..."]
  },
  "value_proposition": "...",
  "success_metrics": [
    {"metric": "...", "target": "...", "timeline": "..."}
  ],
  "prioritized_features": [
    {"feature": "...", "rice_score": 100, "rationale": "..."}
  ],
  "risks": [
    {"type": "...", "risk": "...", "mitigation": "..."}
  ],
  "recommendation": "BUILD|DON'T BUILD|PIVOT",
  "confidence": 0.0-1.0,
  "content": "Markdown explanation..."
}
```

---

## Validation Checklist

- [ ] All required fields present
- [ ] 4 discovery risks assessed (value, usability, feasibility, viability)
- [ ] Specific metrics defined (not vanity metrics)
- [ ] Features prioritized with RICE/MoSCoW
- [ ] Recommendation is clear (BUILD/DON'T BUILD/PIVOT)
- [ ] Confidence is reasonable (0.5-1.0)
- [ ] Content field explains the reasoning
