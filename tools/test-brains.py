#!/usr/bin/env python3
"""
MasterMind Framework - Brain Testing Script

Tests Product Strategy (#1) and UX Research (#2) brains with sample briefs.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add agents to path
agents_dir = Path(__file__).parent.parent / "agents"
sys.path.insert(0, str(agents_dir))

# Sample briefs for testing
SAMPLE_BRIEFS = {
    "product_strategy": {
        "title": "AI-Powered Code Review Assistant",
        "description": """
Quiero construir una herramienta que use IA para revisar código automáticamente.
La idea es que los desarrolladores puedan subir su código y recibir feedback
sobre bugs, smells de código, y oportunidades de mejora.

Contexto:
- Ya existen herramientas como SonarQube pero son muy pesadas
- Los desarrolladores quieren feedback rápido en el PR
- El target es equipos pequeños de 5-20 personas

¿Es esto una buena idea? ¿Qué debería construir primero?
        """.strip(),
        "constraints": [
            "Budget limitado (<$500/mes en APIs)",
            "Lanzamiento en 3 meses",
            "Equipo: 1 fullstack dev + 1 designer",
        ],
    },
    "ux_research": {
        "title": "Dashboard de Análisis para E-commerce",
        "description": """
Necesito diseñar el dashboard de análisis para dueños de tiendas e-commerce.

El problema actual:
- Los dueños de tienda no entienden sus métricas
- Hay demasiados números y gráficos
- No saben qué acciones tomar basados en los datos

Usuarios: Dueños de tiendas pequeñas (1-10 empleados)
Contexto: Usan el dashboard 1-2 veces por semana, principalmente desktop
        """.strip(),
        "current_experience": "Dashboard actual con 15+ métricas, filtros complejos, sin jerarquía visual",
        "goals": [
            "Que entiendan cómo va su negocio",
            "Que sepan qué acciones tomar",
            "Que no se sientan abrumados",
        ],
    },
}


def load_brain_prompt(brain_name: str) -> str:
    """Load brain system prompt from file."""
    brain_file = agents_dir / "brains" / f"{brain_name}.md"
    if not brain_file.exists():
        raise FileNotFoundError(f"Brain not found: {brain_file}")

    return brain_file.read_text()


def create_test_prompt(brain_name: str, brief: dict) -> str:
    """Create a test prompt combining brain system prompt and brief."""
    system_prompt = load_brain_prompt(brain_name)

    user_message = f"""## Brief: {brief['title']}

{brief['description']}

"""
    if "constraints" in brief:
        user_message += f"""### Constraints
{chr(10).join(f'- {c}' for c in brief['constraints'])}

"""
    if "current_experience" in brief:
        user_message += f"""### Current Experience
{brief['current_experience']}

"""
    if "goals" in brief:
        user_message += f"""### Goals
{chr(10).join(f'- {g}' for g in brief['goals'])}

"""

    user_message += """---
Please respond with your analysis following your output format.
Include both the JSON structure and a human-readable explanation.
"""

    return system_prompt, user_message


def print_test_header(test_name: str):
    """Print test header."""
    print("\n" + "=" * 80)
    print(f"  TEST: {test_name}")
    print("=" * 80 + "\n")


def print_section(title: str):
    """Print section header."""
    print(f"\n{'─' * 40}")
    print(f"  {title}")
    print(f"{'─' * 40}\n")


def main():
    """Run brain tests."""
    print("\n" + "🧠" * 20)
    print("  MasterMind Framework - Brain Testing")
    print("🧠" * 20 + "\n")

    tests = [
        (
            "product-strategy",
            "Brain #1: Product Strategy",
            SAMPLE_BRIEFS["product_strategy"],
        ),
        ("ux-research", "Brain #2: UX Research", SAMPLE_BRIEFS["ux_research"]),
    ]

    results = []

    for brain_name, brain_title, brief in tests:
        print_test_header(brain_title)

        # Load brain prompt
        try:
            system_prompt, user_message = create_test_prompt(brain_name, brief)
            print(f"✅ Brain loaded: {brain_name}.md")
        except FileNotFoundError as e:
            print(f"❌ {e}")
            results.append((brain_name, "FAIL", "Brain file not found"))
            continue

        # Display brief summary
        print(f"\n📋 Brief: {brief['title']}")
        print(f"   {brief['description'][:100]}...")

        # Show expected output format
        print_section("Expected Output Format")

        if brain_name == "product-strategy":
            print("""
{
  "brain": "product-strategy",
  "task_id": "UUID",
  "validated_problem": { ... },
  "target_persona": { ... },
  "value_proposition": "string",
  "success_metrics": [ ... ],
  "prioritized_features": [ ... ],
  "risks": [ ... ],
  "recommendation": "BUILD|DON'T BUILD|PIVOT",
  "confidence": 0.0-1.0,
  "content": "Markdown explanation"
}
""")
        elif brain_name == "ux-research":
            print("""
{
  "brain": "ux-research",
  "task_id": "UUID",
  "research_summary": { ... },
  "persona": { ... },
  "experience_design": { ... },
  "usability_recommendations": [ ... ],
  "further_research": [ ... ],
  "confidence": 0.0-1.0,
  "content": "Markdown explanation"
}
""")

        # Print instructions for manual testing
        print_section("Manual Testing Instructions")
        print(f"""
To test this brain with Claude:

1. Copy the system prompt from: agents/brains/{brain_name}.md

2. Use this user message:

{user_message}

3. Verify the response:
   - Contains all required fields
   - Follows the JSON format above
   - Includes content field with explanation
   - Confidence score is reasonable (0.5-1.0)
   - Recommendations are actionable
""")

        results.append((brain_name, "READY", "Instructions generated"))

    # Summary
    print("\n" + "=" * 80)
    print("  TEST SUMMARY")
    print("=" * 80 + "\n")

    for brain_name, status, note in results:
        symbol = "✅" if status == "READY" else "❌"
        print(f"{symbol} {brain_name}: {status} - {note}")

    print("\n" + "=" * 80 + "\n")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = Path(__file__).parent.parent / "logs" / f"brain-test-{timestamp}.txt"

    # Create logs directory if needed
    results_file.parent.mkdir(exist_ok=True)

    with open(results_file, "w") as f:
        f.write("MasterMind Framework - Brain Test Results\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")

        for brain_name, status, note in results:
            f.write(f"{brain_name}: {status} - {note}\n")

    print(f"📝 Results saved to: {results_file}\n")


if __name__ == "__main__":
    main()
